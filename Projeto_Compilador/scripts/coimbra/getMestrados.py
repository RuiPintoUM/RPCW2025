import requests
from bs4 import BeautifulSoup
import json
import time


def extrair_unidades_curriculares_uc(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Erro ao aceder ao plano de estudos {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    unidades = []
    tabela = soup.find("table", class_="uk-table")
    if not tabela:
        return []

    for row in tabela.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) >= 6:
            nome_tag = cols[0].find("a")
            nome = nome_tag.get_text(strip=True) if nome_tag else cols[0].get_text(strip=True)
            link = nome_tag["href"] if nome_tag and nome_tag.has_attr("href") else ""
            ano = cols[1].get_text(strip=True)
            regime = cols[2].get_text(strip=True)
            tipo = cols[3].get_text(strip=True)
            area_cientifica = cols[4].get_text(strip=True)
            ects = cols[5].get_text(strip=True)
            unidades.append({
                "nome": nome,
                "link": link,
                "ano": ano,
                "regime": regime,
                "tipo": tipo,
                "area_cientifica": area_cientifica,
                "ects": ects
            })
    return unidades

def extrair_detalhes_mestrado_uc(url, departamento):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Erro ao aceder {url}: {e}")
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

    # Nome
    nome = soup.find("h1")
    nome = nome.get_text(strip=True) if nome else "N/A"

    # Área científica (não aparece diretamente, podes tentar inferir do contexto ou deixar N/A)
    area_cientifica = "N/A"

    # Regime
    regime = "N/A"
    for h2 in soup.find_all("h2"):
        if "Regime de Estudo" in h2.get_text():
            regime = h2.find_next(string=True).strip()
            break

    # Descrição (Objetivos do Curso)
    descricao = "N/A"
    for h2 in soup.find_all("h2"):
        if "Objetivos do Curso" in h2.get_text():
            descricao = ""
            for sib in h2.next_siblings:
                if sib.name and sib.name.startswith("h"):
                    break
                if hasattr(sib, "get_text"):
                    descricao += sib.get_text(" ", strip=True) + " "
            descricao = descricao.strip()
            break

    # Saídas profissionais
    saidas_profissionais = "N/A"
    for h2 in soup.find_all("h2"):
        if "Saídas Profissionais" in h2.get_text():
            saidas_profissionais = ""
            for sib in h2.next_siblings:
                if sib.name and sib.name.startswith("h"):
                    break
                if hasattr(sib, "get_text"):
                    saidas_profissionais += sib.get_text(" ", strip=True) + " "
            saidas_profissionais = saidas_profissionais.strip()
            break

    # Unidades curriculares (Plano de Estudos)
    unidades_curriculares = []
    plano = soup.find("h2", string=lambda t: t and "Plano de Estudos" in t)
    if plano:
        for a in plano.find_all_next("a", href=True):
            if "programme" in a["href"]:
                unidades_curriculares = extrair_unidades_curriculares_uc(a["href"])
                break

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


urls = {
    "fluc": "Faculdade de Letras", "fduc": "Faculdade de Direito", "fctuc/dct": "Departamento de Ciências da Terra", "fmuc": "Faculdade de Medicina", 
    "ffuc": "Faculdade de Farmácia", "feuc": "Faculdade de Economia", "fpceuc": "Faculdade de Psicologia e de Ciências da Educação", 
    "fcdefuc": "Faculdade de Ciências do Desporto e Educação Física","cauc": "Colégio das Artes", "fctuc/dcv": "Departamento de Ciências da Vida",
    "fctuc/dec": "Departamento de Engenharia Civil", "fctuc/deec": "Departamento de Engenharia Eletrotécnica e de Computadores", 
    "fctuc/dei": "Departamento de Engenharia Informática", "fctuc/dem": "Departamento de Engenharia Mecânica", "fctuc/deq": "Departamento de Engenharia Química",
    "fctuc/df": "Departamento de Física","fctuc/dm": "Departamento de Matemática", "fctuc/dq": "Departamento de Química" 
    }

base_url = "https://www.uc.pt/candidaturas/mestrados/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

mestrados = []

for key, value in urls.items():
    print(f"🔍 A extrair mestrados da {value}...")
    
    url = f"{base_url}{key}/cursos/"
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Erro ao aceder ao site: {response.status_code}")
        exit()

    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")

    cursos_tabel = tables[1]

    if not cursos_tabel:
        print("❌ Bloco de mestrados não encontrado.")
        exit()

    # Extrair os links dos cursos
    for row in cursos_tabel.find_all("tr")[2:]:
        curso = row.find("a")
        if not curso:
            continue
        link = curso["href"]

        detalhes = extrair_detalhes_mestrado_uc(link, value)
        mestrados.append(detalhes)
        time.sleep(1)

# Guardar os dados em JSON
with open("ontologias/mestrados_uc.json", "w", encoding="utf-8") as f:
    json.dump(mestrados, f, ensure_ascii=False, indent=2)

print(f"✅ {len(mestrados)} mestrados extraídos com sucesso.")

