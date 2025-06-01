import requests
from bs4 import BeautifulSoup
import json

import time

def extrair_detalhes_mestrado(url, area_cientifica):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ Erro ao aceder à página do mestrado: {url}")
        return {
            "nome": "N/A",
            "area_cientifica": "N/A",
            "regime": "N/A",
            "departamento": "N/A",
            "descricao": "N/A",
            "saidas_profissionais": "N/A",
            "pagina_url": url,
            "unidades_curriculares": []
        }
    soup = BeautifulSoup(response.text, "html.parser")

    nome = soup.find("h1", class_="page-titles")
    nome = nome.text.strip() if nome else "N/A"

    # Regime (ex: Presencial / diurno)
    formato = soup.find("div", id="formato")
    regime = formato.get_text(strip=True).replace("Formato:", "").strip() if formato else "N/A"

    # Departamento
    departamento = "N/A"
    dep_div = soup.find("div", class_="curso-departamento")
    if dep_div:
        dep_title = dep_div.find("h2")
        if dep_title:
            departamento = dep_title.get_text(strip=True).replace("Sobre o ", "")

    # Descrição
    desc_div = soup.find("div", id="mestrado_descricao")
    descricao = desc_div.get_text(separator="\n", strip=True) if desc_div else "N/A"

    # Saídas profissionais
    saidas_div = soup.find("div", id="curso-mestrado-saidas")
    if saidas_div:
        saidas_list = saidas_div.find_all("li")
        saidas_profissionais = "; ".join(li.get_text(strip=True) for li in saidas_list)
    else:
        saidas_profissionais = "N/A"

    # Unidades curriculares (não está na página, pode tentar seguir o link do "Plano curricular")
    unidades_curriculares = []

    return {
        "nome": nome,
        "area_cientifica": area_cientifica,
        "regime": regime,
        "departamento": departamento,
        "descricao": descricao,
        "saidas_profissionais": saidas_profissionais,
        "pagina_url": url,
        "unidades_curriculares": unidades_curriculares
    }

def main():
    url = "https://www.fct.unl.pt/ensino/mestrados"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ Erro ao aceder ao site: {response.status_code}")
        exit()

    soup = BeautifulSoup(response.text, "html.parser")
    mestrados = []

    colunas = soup.find_all("div", class_="col-tn-12 col-sm-4")
    if not colunas:
        print("❌ Não foi possível encontrar os mestrados.")
        exit()

    areasCient = ['Ciências', 'Engenharia', 'Tecnologia']
    i = 0
    for coluna in colunas[1:]:
        for a in coluna.find_all("a", href=True):
            nome = a.get_text(strip=True)
            link = a["href"]


            detalhes = extrair_detalhes_mestrado(link, areasCient[i])
            mestrados.append(detalhes)
            
            i += 1
            time.sleep(1)
            

    output_file = "ontologias/mestrados_fctnova.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(mestrados, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(mestrados)} mestrados extraídos com sucesso.")

if __name__ == "__main__":
    print("🔍 A iniciar scraping dos mestrados da FCT NOVA...")

    main()
