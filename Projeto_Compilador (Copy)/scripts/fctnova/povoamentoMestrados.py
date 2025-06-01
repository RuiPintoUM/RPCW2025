from rdflib import Graph, Namespace, Literal, RDF
import json
import re
import unicodedata

# Função para criar URIs seguros
def criar_uri_valido(texto):
    # Remove acentos
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode()
    # Substitui espaços por underscore
    texto = texto.replace(" ", "_")
    # Remove parênteses, vírgulas, pontos e outros símbolos inválidos
    texto = re.sub(r"[^\w]", "_", texto)
    # Remove múltiplos underscores consecutivos
    texto = re.sub(r"_+", "_", texto)
    return texto.strip("_")

# Caminhos
json_path = "ontologias/mestrados_fctnova.json"
ttl_base_path = "ontologias/cursos_povoados_um_utad.ttl"
ttl_output_path = "ontologias/cursos_povoados_um_utad_fctnova.ttl"

# Carregar grafo base
g = Graph()
g.parse(ttl_base_path, format="turtle")

# Namespace
EX = Namespace("http://www.example.org/disease-ontology#")

cursos = {}
areaCientifica_set = set()
departamento_set = set()
unidades_curriculares_lista = []
uc_nomes_set = set()
regimes_set = set()


universidade = "Faculdade de Ciências e Tecnologia da Universidade NOVA de Lisboa"

# Ler JSON
with open(json_path, "r", encoding="utf-8") as f:
    cursos_data = json.load(f)

# Adicionar cursos ao grafo
for curso in cursos_data:
    nome_uri = criar_uri_valido(curso["nome"])
    
    areaCientifica = curso["area_cientifica"]
    departamento = curso["departamento"]
    regime = curso["regime"]
    descricao = curso.get("descricao", "N/A")
    saidas_profissionais = curso.get("saidas_profissionais", "N/A")
    pagina_url = curso["pagina_url"]
    unidades_curriculares = curso.get("unidades_curriculares", [])
    
    if regime not in regimes_set:
        regimes_set.add(regime)

    if areaCientifica not in areaCientifica_set:
        areaCientifica_set.add(areaCientifica)
    
    if departamento not in departamento_set:
        departamento_set.add(departamento)
    
    for uc in unidades_curriculares:
        nome_uc = uc["nome"]
        if nome_uc not in uc_nomes_set:
            uc_nomes_set.add(nome_uc)
            unidades_curriculares_lista.append(uc)
    
    curso = {
        "nome": curso["nome"],
        "area_cientifica": areaCientifica,
        "regime": regime,
        "departamento": departamento,
        "universidade": universidade,
        "descricao": descricao,
        "saidas_profissionais": saidas_profissionais,
        "pagina_url": pagina_url,
        "unidades_curriculares": unidades_curriculares
    }
    
    cursos[nome_uri] = curso
    
# Adicionar universidade ao grafo
universidade_uri = EX[criar_uri_valido(universidade)]
g.add((universidade_uri, RDF.type, EX.Universidade))
g.add((universidade_uri, EX.temNome, Literal(universidade)))


for regime in regimes_set:
    regime_uri = EX[criar_uri_valido(regime)]
    g.add((regime_uri, RDF.type, EX.Regime))


for area in areaCientifica_set:
    area_uri = EX[criar_uri_valido(area)]
    g.add((area_uri, RDF.type, EX.AreaCientifica))
    g.add((area_uri, EX.temNome, Literal(area)))

for departamento in departamento_set:
    departamento_uri = EX[criar_uri_valido(departamento)]
    g.add((departamento_uri, RDF.type, EX.Departamento))
    g.add((departamento_uri, EX.temNome, Literal(departamento)))
    g.add((departamento_uri, EX.pertenceA, universidade_uri))

    
for uc in unidades_curriculares_lista:
    uc_uri = EX[criar_uri_valido(uc['nome'])]
    g.add((uc_uri, RDF.type, EX.UnidadeCurricular))
    g.add((uc_uri, EX.temNome, Literal(uc['nome'])))
    g.add((uc_uri, EX.temAreaCient, Literal(uc['area_cientifica'])))
    
for curso_uri in cursos:
    curso_uri_ref = EX[curso_uri]  # Converte para rdflib.URIRef
    g.add((curso_uri_ref, RDF.type, EX.Mestrado))
    g.add((curso_uri_ref, EX.temNome, Literal(cursos[curso_uri]["nome"])))
    g.add((curso_uri_ref, EX.temAreaCientifica, EX[criar_uri_valido(cursos[curso_uri]["area_cientifica"])]))
    g.add((curso_uri_ref, EX.pertenceA, EX[criar_uri_valido(cursos[curso_uri]["departamento"])]))
    g.add((curso_uri_ref, EX.temRegime, EX[criar_uri_valido(cursos[curso_uri]["regime"])]))
    g.add((curso_uri_ref, EX.temDescricao, Literal(cursos[curso_uri]["descricao"])))
    g.add((curso_uri_ref, EX.temSaidasProfissionais, Literal(cursos[curso_uri]["saidas_profissionais"])))
    g.add((curso_uri_ref, EX.temLinkWebsite, Literal(cursos[curso_uri]["pagina_url"])))
    
    oferta_uri = EX[f"oferta_{criar_uri_valido(cursos[curso_uri]['nome'])}"]
    
    
    for i, uc in enumerate(cursos[curso_uri].get("unidades_curriculares", [])):
        uc_uri = EX[criar_uri_valido(uc["nome"])]

        # Criar instância de OfertaUnidadeCurricular única
        oferta_uri = EX[f"oferta_{criar_uri_valido(cursos[curso_uri]['nome'])}_{i}"]
        g.add((oferta_uri, RDF.type, EX.OfertaUnidadeCurricular))
        
        
        g.add((oferta_uri, EX.incluiUnidadeCurricular, uc_uri))
        g.add((oferta_uri, EX.semestre, Literal(uc.get("semestre", "N/A"))))
        g.add((oferta_uri, EX.temAreaCient, Literal(uc.get("area_cientifica", "N/A"))))

        # Ligar o mestrado à oferta
        g.add((curso_uri_ref, EX.temOfertaUC, oferta_uri))
    
    g.add((universidade_uri, EX.ofereceCurso, curso_uri_ref))


# Guardar o grafo resultante
g.serialize(destination=ttl_output_path, format="turtle")
print(f"Grafo salvo em: {ttl_output_path}")
