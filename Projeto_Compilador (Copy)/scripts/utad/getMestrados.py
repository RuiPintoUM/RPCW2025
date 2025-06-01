import requests
from bs4 import BeautifulSoup
import time
import random
import json

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def extrair_detalhes_curso_utad(url):
    for tentativa in range(3):  # Tentar até 3 vezes
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            break
        except requests.exceptions.RequestException as e:
            print(f"Tentativa {tentativa + 1} falhou ao aceder {url} ➜ {e}")
            time.sleep(2)  # Esperar antes de tentar novamente
    else:
        print(f"Erro permanente ao aceder {url}")
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

    # Extrair o nome do curso
    nome_elem = soup.find("h1", class_="entry-title")
    nome = nome_elem.text.strip() if nome_elem else "N/A"

    # Extrair a área científica
    area_cientifica_elem = soup.find("span", string="Área de Educação e Formação")
    if area_cientifica_elem:
        area_cientifica = area_cientifica_elem.find_next("div", class_="font1").text.strip()
    else:
        area_cientifica = "N/A"

    # Extrair o regime
    regime_elem = soup.find("span", string="Regime de Estudo")
    if regime_elem:
        regime = regime_elem.find_next("div", class_="font1").text.strip()
    else:
        regime = "N/A"

    # Extrair a descrição do curso
    descricao_elem = soup.find("div", class_="post-content")
    descricao = ""
    if descricao_elem:
        paragrafos = descricao_elem.find_all(["p", "h2", "h3"])
        descricao = "\n".join(p.get_text(strip=True) for p in paragrafos if p.get_text(strip=True))

    # Extrair as saídas profissionais
    saidas_elem = soup.find("div", class_="col-xs-8 col-md-9")
    saidas_profissionais = saidas_elem.get_text(strip=True) if saidas_elem else "N/A"

    # Preencher outros campos com "N/A" (ajuste conforme necessário)
    return {
        "nome": nome,
        "area_cientifica": area_cientifica,
        "regime": regime,
        "departamento": "N/A",
        "descricao": descricao,
        "saidas_profissionais": saidas_profissionais,
        "pagina_url": url,
        "unidades_curriculares": []
    }

urls = [
    "https://www.utad.pt/estudar/inicio/mestrados/",
    "https://www.utad.pt/estudar/inicio/mestrados/page/2/",
    "https://www.utad.pt/estudar/inicio/mestrados/page/3/"
]

mestrados = []
for url in urls:
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    for a in soup.find_all("a", class_="linklist"):
        for span in a.find_all("span"):
            span.decompose()

        nome = a.text.strip()
        link = a.get("href")
        
        dados = extrair_detalhes_curso_utad(link)
        dados['nome'] = nome
        mestrados.append(dados)  # Adiciona o curso como um objeto na lista
        
with open("ontologias/mestrados_utad.json", "w", encoding="utf-8") as f:
    json.dump(mestrados, f, ensure_ascii=False, indent=2)
print("📁 Dados guardados em 'mestrados_utad.json'")

# Mostra os mestrados extraídos
for dados in mestrados:
    print(f"Nome: {dados['nome']}")
    print(f"Área Científica: {dados['area_cientifica']}")
    print(f"Regime: {dados['regime']}")
    print(f"Departamento: {dados['departamento']}")
    print(f"Descrição: {dados['descricao']}")
    print(f"Saídas Profissionais: {dados['saidas_profissionais']}")
    print(f"URL: {dados['pagina_url']}")
    print("-" * 40)