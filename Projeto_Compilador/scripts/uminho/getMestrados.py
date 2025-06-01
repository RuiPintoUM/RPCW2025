from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json

def extrair_unidades_curriculares(soup):
    unidades_curriculares = []

    tabelas = soup.find_all("table", class_="table")
    for tabela in tabelas:
        linhas = tabela.find_all("tr")
        for linha in linhas:
            colunas = linha.find_all("td")
            if len(colunas) >= 3:
                semestre = colunas[0].text.strip()
                nome = colunas[1].text.strip()
                areaCint = colunas[2].text.strip()
                ects = colunas[3].text.strip() 
                
                unidades_curriculares.append({
                    "nome": nome,
                    "ects": ects,
                    "semestre": semestre,
                    "area_cientifica": areaCint
                })

    return unidades_curriculares


def get_course_details(driver, course_name):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ctl00_PlaceHolderMain_ctlPlanosCurso_pnMain"))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        area_cientifica = soup.find('span', id='ctl00_PlaceHolderMain_rpAreas_ctl01_lblArea')
        regime = soup.find('span', id='ctl00_PlaceHolderMain_lblRegime')
        departamento = soup.find('span', id='ctl00_PlaceHolderMain_rpUnidades_ctl01_lblUnidade')
        descricao_elemento = soup.find('span', id='ctl00_PlaceHolderMain_lblDescricao')
        descricao = descricao_elemento.get_text(separator="\n").strip() if descricao_elemento else "N/A"
        saidas = soup.find('span', id='ctl00_PlaceHolderMain_lblSaidas')
        pagina = driver.current_url
        
        ucs = extrair_unidades_curriculares(soup)
        
        return {
            "nome": course_name,
            "area_cientifica": area_cientifica.text.strip() if area_cientifica else "N/A",
            "regime": regime.text.strip() if regime else "N/A",
            "departamento": departamento.text.strip() if departamento else "N/A",
            "descricao": descricao,
            "saidas_profissionais": saidas.get_text(separator="\n").strip() if saidas else "N/A",
            "pagina_url": pagina,
            "unidades_curriculares": ucs
        }
        
    except Exception as e:
        print(f"Erro ao obter detalhes do curso: {e}")
        return None
    
def ir_para_pagina(driver, pagina_destino):
    """
    Vai diretamente para a página indicada, apenas se o botão estiver visível.
    Não tenta clicar à toa na seta.
    """
    try:
        if pagina_destino > 3 and pagina_destino < 7:
            seta = driver.find_elements(By.XPATH, "//a[contains(@class, 'PageNumbers') and text()=' » ']")
            if seta:
                try:
                    seta[0].click()
                    time.sleep(2)
                except Exception as e:
                    print(f"⚠️ Erro ao clicar na seta: {e}")
                    return False
        
        if pagina_destino == 7:
            seta = driver.find_elements(By.XPATH, "//a[contains(@class, 'PageNumbers') and text()=' » ']")
            if seta:
                try:
                    seta[0].click()
                    time.sleep(2)
                except Exception as e:
                    print(f"⚠️ Erro ao clicar na seta: {e}")
                    return False
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "PageNumbers"))
            )
            seta = driver.find_elements(By.XPATH, "//a[contains(@class, 'PageNumbers') and text()=' » ']")
            if seta:
                try:
                    seta[0].click()
                    time.sleep(2)
                except Exception as e:
                    print(f"⚠️ Erro ao clicar na seta: {e}")
                    return False
            
        
        # Espera até os botões de página estarem visíveis
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "PageNumbers"))
        )

        botoes = driver.find_elements(By.XPATH, f"//a[contains(@class, 'PageNumbers') and text()='{pagina_destino}']")
        if botoes:
            botoes[0].click()
            time.sleep(2)
        else:
            print(f"⚠️ Página {pagina_destino} não visível no momento.")
    except Exception as e:
        print(f"❌ Erro ao tentar ir para a página {pagina_destino}: {e}")

def get_all_mestrados():
    options = EdgeOptions()
    options.use_chromium = True
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = EdgeService(executable_path="/usr/local/bin/msedgedriver")
    driver = webdriver.Edge(service=service, options=options)

    url = "https://www.uminho.pt/PT/ensino/oferta-educativa/Cursos-Conferentes-a-Grau/Paginas/Mestrados.aspx"
    driver.get(url)
    time.sleep(2)

    mestrados = []

    for pagina_num in range(1, 8):
        ir_para_pagina(driver, pagina_num)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('table', {'class': 'table table-condensed table-hover'})
        if not table:
            print(f"Nenhuma tabela encontrada na página {pagina_num}")
            continue

        cursos = []
        for row in table.find_all('tr'):
            td = row.find('td')
            if td:
                name_span = td.find('span', class_='setColor-Black')
                link = td.find('a')
                if name_span and link and link.has_attr("id"):
                    nome = name_span.text.strip()
                    link_id = link["id"]
                    cursos.append((nome, link_id))

        for nome, link_id in cursos:
            try:
                # Volta à página certa e encontra o botão de novo
                ir_para_pagina(driver, pagina_num)
                time.sleep(1)
                link_element = driver.find_element(By.ID, link_id)
                link_element.click()
                time.sleep(2)

                detalhes = get_course_details(driver, nome)
                if detalhes:
                    mestrados.append(detalhes)

                driver.get(url)
                time.sleep(2)
            except Exception as e:
                print(f"Erro ao processar curso '{nome}' (ID: {link_id}): {e}")

        print(f"✅ Página {pagina_num} processada")

    with open("ontologias/mestrados_uminho.json", "w", encoding="utf-8") as f:
        json.dump(mestrados, f, ensure_ascii=False, indent=2)
    print("📁 Dados guardados em 'mestrados_uminho.json'")

    # Print final
    for m in mestrados:
        print(f"Curso: {m['nome']}\nÁrea Científica: {m['area_cientifica']}\nRegime: {m['regime']}\nDepartamento: {m['departamento']}\nDescricao: {m['descricao']}\nSaidas_profissionais: {m['saidas_profissionais']}\nPagina_url: {m['pagina_url']}\n{'-'*40}")
    print(f"Total de mestrados encontrados: {len(mestrados)}")

if __name__ == "__main__":
    get_all_mestrados()
