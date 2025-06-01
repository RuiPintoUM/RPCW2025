from flask import Flask, render_template, request, redirect, url_for
from rdflib import Graph, Namespace, Literal, RDF
import json
import uuid
import unicodedata
from collections import OrderedDict
import re

app = Flask(__name__)

# Carregar ontologia
g = Graph()
g.parse("ontologias/cursos_povoados_um_utad_fctnova_uc.ttl", format="ttl")

EX = Namespace("http://www.example.org/disease-ontology#")

def get_label(uri):
    query = f"""
    PREFIX : <http://www.example.org/disease-ontology#>
    SELECT ?nome WHERE {{ <{uri}> :temNome ?nome }}
    """
    results = g.query(query)
    for row in results:
        return str(row.nome)
    return uri.split("#")[-1]


@app.route("/")
@app.route("/universidades")
def listar_universidades():
    universidades = ["Minho", "UTAD", "Coimbra", "FCTNOVA"]
    return render_template("universidades.html", universidades=universidades)

@app.route("/universidade/<nome>")
def universidade_detalhes(nome):
    """
    Esta view mostra:
     - A lista de escolas/departamentos com o número de mestrados, quando não há pesquisa.
     - Se for passado o parâmetro `?q=...`, faz a pesquisa de mestrados por nome
       e popula a lista `cursos`. Caso haja EXACTAMENTE 1 resultado, redireciona
       directamente para a página de detalhes desse mestrado.
    """
    nome = nome.lower()

    # Redirecionamentos especiais (conforme o teu caso)
    if nome == "utad":
        return redirect(url_for("listar_mestrados_utad"))
    if nome == "lisboa":
        # no teu código original tu fazias este redirect para fctnova
        nome = "fctnova"

    # Dicionário que converte o “slug” para o nome completo da universidade
    nome_completo = {
        "minho": "Universidade do Minho",
        "coimbra": "Universidade de Coimbra",
        "fctnova": "Faculdade de Ciências e Tecnologia da Universidade NOVA de Lisboa",
        # acrescenta outras conforme for preciso
    }.get(nome)

    if not nome_completo:
        return "Universidade não reconhecida", 404

   
    query_escolas = f"""
    PREFIX : <http://www.example.org/disease-ontology#>
    SELECT ?escola ?escolaNome (COUNT(?curso) AS ?numCursos)
    WHERE {{
        ?curso a :Mestrado ;
               :pertenceA ?escola .
        ?escola :temNome ?escolaNome ;
                :pertenceA ?universidade .
        ?universidade :temNome ?nomeUniversidade .
        FILTER( LCASE(?nomeUniversidade) = LCASE("{nome_completo}") )
    }}
    GROUP BY ?escola ?escolaNome
    ORDER BY DESC(?numCursos)
    """
    results = g.query(query_escolas)
    escolas = []
    for row in results:
        escolas.append({
            "nome": str(row.escolaNome),
            "num": int(row.numCursos)
        })

    
    termo = request.args.get("q", "").strip()
    cursos = []

    if termo:
       
        sparql_busca = f"""
        PREFIX : <http://www.example.org/disease-ontology#>
        SELECT ?curso ?nome WHERE {{
            ?curso a :Mestrado ;
                   :temNome ?nome ;
                   :pertenceA ?escola .
            ?escola :pertenceA ?universidade .
            ?universidade :temNome ?nomeUniversidade .
            FILTER(
                LCASE(?nomeUniversidade) = LCASE("{nome_completo}") &&
                CONTAINS(LCASE(?nome), LCASE("{termo}"))
            )
        }}
        ORDER BY ?nome
        """
        resultados_busca = g.query(sparql_busca)

        for row in resultados_busca:
            cursos.append({
                "uri": str(row.curso),
                "nome": str(row.nome)
            })

        # 2.2) Se encontrou exatamente 1 mestrado, redireciona para página de detalhes
        if len(cursos) == 1:
            curso_uri = cursos[0]["uri"]                      
            curso_id = curso_uri.split("#")[-1]               
            return redirect(url_for("curso_detalhes", curso_id=curso_id))

  

    return render_template(
        "escolas.html",
        escolas=escolas,
        termo=termo,
        cursos=cursos,
        universidade=nome_completo,
        universidade_curto=nome,
        universidade_slug=nome  # esta linha é a nova!
    )


@app.route("/escola/<escola>")
def listar_mestrados_da_escola(escola):
    area_filtro = request.args.get("area")
    query = f"""
    PREFIX : <http://www.example.org/disease-ontology#>
    SELECT ?curso ?nome ?areaNome WHERE {{
        ?curso a :Mestrado ;
               :temNome ?nome ;
               :pertenceA ?escola ;
               :temAreaCientifica ?area .
        ?escola :temNome "{escola}" .
        ?area :temNome ?areaNome .
    }}
    """
    results = g.query(query)

    cursos = []
    areas = set()
    for row in results:
        areas.add(str(row.areaNome))
        if area_filtro is None or area_filtro == "" or area_filtro == str(row.areaNome):
            cursos.append({
                "uri": str(row.curso),
                "nome": str(row.nome)
            })

    return render_template("mestrados.html", escola=escola, cursos=cursos, areas=sorted(areas), area_atual=area_filtro)


@app.route("/universidade/utad")
def listar_mestrados_utad():
    area_filtro = request.args.get("area")

    query = """
    PREFIX : <http://www.example.org/disease-ontology#>
    SELECT ?curso ?nome ?areaNome WHERE {
        ?curso a :Mestrado ;
               :temNome ?nome ;
               :temAreaCientifica ?area ;
               :pertenceA :Universidade_de_Tras_os_Montes_e_Alto_Douro .
        ?area :temNome ?areaNome .
    }
    ORDER BY ?nome
    """
    resultados = g.query(query)

    cursos = []
    areas = set()
    for row in resultados:
        areas.add(str(row.areaNome))
        if area_filtro is None or area_filtro == "" or area_filtro == str(row.areaNome):
            cursos.append({
                "uri": str(row.curso),
                "nome": str(row.nome)
            })

    return render_template("mestrados.html", escola="UTAD", cursos=cursos, areas=sorted(areas), area_atual=area_filtro)


@app.route("/curso/<path:curso_id>")
def curso_detalhes(curso_id):
    uri = f"http://www.example.org/disease-ontology#{curso_id}"
    query = f"""
    PREFIX : <http://www.example.org/disease-ontology#>
    SELECT ?p ?o WHERE {{ <{uri}> ?p ?o }}
    """

    results = g.query(query)
    detalhes = {}
    ucs_por_opcao = {}
    opcao_atual = "UC's Obrigatórias"

    ns = Namespace("http://www.example.org/disease-ontology#")

    for row in results:
        pred = row.p.split("#")[-1]
        val_uri = str(row.o)

        labels_predicados = {
            "temNome": "Nome",
            "temDescricao": "Descrição",
            "temLinkWebsite": "Website",
            "temOfertaUC": "Oferta Curricular",
            "temRegime": "Regime",
            "temSaidasProfissionais": "Saídas Profissionais",
            "pertenceA": "Escola",
            "temAreaCientifica": "Área Científica",
            "decorreEm": "Localização",
            "type": "Tipo"
        }

        label = labels_predicados.get(pred, pred)

        if pred == "temOfertaUC":
            oferta_uri = row.o
            for uc_uri in g.objects(subject=oferta_uri, predicate=ns.incluiUnidadeCurricular):
                nome_uc = g.value(subject=uc_uri, predicate=ns.temNome)
                nome_uc = str(nome_uc) if nome_uc else "N/A"

                if nome_uc.startswith("Opção"):
                    opcao_atual = nome_uc.strip()
                    if opcao_atual not in ucs_por_opcao:
                        ucs_por_opcao[opcao_atual] = []
                    continue

                semestre_legivel = None
                q_semestre = f"""
                PREFIX : <http://www.example.org/disease-ontology#>
                SELECT ?s WHERE {{
                    <{oferta_uri}> :incluiUnidadeCurricular <{uc_uri}> ;
                                   :semestre ?s .
                }}
                """
                r_sem = list(g.query(q_semestre))
                if r_sem:
                    raw = str(r_sem[0][0])
                    if raw == "S1":
                        semestre_legivel = "1º semestre"
                    elif raw == "S2":
                        semestre_legivel = "2º semestre"

                if opcao_atual not in ucs_por_opcao:
                    ucs_por_opcao[opcao_atual] = []
                ucs_por_opcao[opcao_atual].append((nome_uc, semestre_legivel))
        else:
            val = get_label(val_uri) if val_uri.startswith("http://") else val_uri
            if val != "N/A":
                detalhes[label] = val

    def ordenar_opcoes(opcoes_dict):
        def chave_ordem(opcao):
            match = re.search(r"Opç[aã]o\s+([IVXLCDM]+)", opcao)
            if match:
                romanos = {
                    'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
                    'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10
                }
                return romanos.get(match.group(1), 1000)
            elif "Obrigat" in opcao:
                return 0
            return 9999

        return OrderedDict(sorted(opcoes_dict.items(), key=lambda x: chave_ordem(x[0])))

    ucs_por_opcao = ordenar_opcoes(ucs_por_opcao)

    return render_template("mestrado_detalhes.html", curso_id=curso_id, detalhes=detalhes, ucs_por_opcao=ucs_por_opcao)



@app.route("/estatisticas")
def estatisticas():
    query = """
    PREFIX : <http://www.example.org/disease-ontology#>
    SELECT ?areaNome (COUNT(?curso) AS ?numeroCursos)
    WHERE {
        ?curso a :Mestrado ;
               :temAreaCientifica ?area .
        ?area :temNome ?areaNome .
    }
    GROUP BY ?areaNome
    ORDER BY DESC(?numeroCursos)
    """
    resultados = g.query(query)
    combinados = [(str(row.areaNome), int(row.numeroCursos)) for row in resultados]
    return render_template("estatisticas.html", combinados=combinados)


@app.route("/mestrados")
def mostrar_mestrados():
    area_filtro = request.args.get("area")

    query = """
    PREFIX : <http://www.example.org/disease-ontology#>
    SELECT ?curso ?nome ?areaNome WHERE {
        ?curso a :Mestrado ;
               :temNome ?nome ;
               :temAreaCientifica ?area .
        ?area :temNome ?areaNome .
    }
    ORDER BY ?nome
    """
    resultados = g.query(query)

    cursos = []
    areas = set()

    for row in resultados:
        areas.add(str(row.areaNome))
        if area_filtro is None or area_filtro == "" or area_filtro == str(row.areaNome):
            cursos.append({
                "uri": str(row.curso),
                "nome": str(row.nome)
            })

    return render_template("mestrados.html", escola=None, cursos=cursos, areas=sorted(areas), area_atual=area_filtro)

@app.route("/universidade/minho/mestrados")
def listar_mestrados_uminho():
    area_filtro = request.args.get("area")
    query = """
    PREFIX : <http://www.example.org/disease-ontology#>
    SELECT ?curso ?nome ?areaNome WHERE {
        ?curso a :Mestrado ;
               :temNome ?nome ;
               :temAreaCientifica ?area ;
               :pertenceA ?escola .
        ?escola :temNome ?escolaNome .
        FILTER(CONTAINS(LCASE(?escolaNome), "universidade do minho") || CONTAINS(LCASE(?escolaNome), "escola"))
        ?area :temNome ?areaNome .
    }
    ORDER BY ?nome
    """
    resultados = g.query(query)
    cursos = []
    areas = set()
    for row in resultados:
        areas.add(str(row.areaNome))
        if not area_filtro or area_filtro == str(row.areaNome):
            cursos.append({
                "uri": str(row.curso),
                "nome": str(row.nome)
            })
    return render_template("mestrados.html", escola="Universidade do Minho", cursos=cursos, areas=sorted(areas), area_atual=area_filtro)

EX = Namespace("http://www.example.org/disease-ontology#")
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

@app.route("/adicionar-mestrado", methods=["GET", "POST"])
def adicionar_mestrado():
    if request.method == "GET":
        # Query para obter todas as universidades
        query = """
        PREFIX : <http://www.example.org/disease-ontology#>
        SELECT ?uniNome WHERE {
            ?uni a :Universidade ;
                 :temNome ?uniNome .
        }
        ORDER BY ?uniNome
        """
        results = g.query(query)
        universidades = [str(row.uniNome) for row in results]
        return render_template("adicionar_mestrado.html", universidades=universidades)

    if request.method == "POST":
        # Obter dados do formulário
        nome = request.form.get("nome")
        universidade = request.form.get("universidade")
        area_cientifica = request.form.get("area_cientifica")
        regime = request.form.get("regime")
        departamento = request.form.get("departamento")
        descricao = request.form.get("descricao")
        saidas_profissionais = request.form.get("saidas_profissionais")
        pagina_url = request.form.get("pagina_url")

        # Validar campos obrigatórios
        if not nome or not universidade or not pagina_url:
            erro = "Nome, universidade e página URL são campos obrigatórios."
            return render_template("adicionar_mestrado.html", erro=erro)

        # Criar URI base do mestrado
        mestrado_id = criar_uri_valido(nome)
        mestrado_uri = EX[mestrado_id]

        # Adicionar Mestrado
        g.add((mestrado_uri, RDF.type, EX.Mestrado))
        g.add((mestrado_uri, EX.temNome, Literal(nome)))
        g.add((mestrado_uri, EX.temDescricao, Literal(descricao)))
        g.add((mestrado_uri, EX.temLinkWebsite, Literal(pagina_url)))
        g.add((mestrado_uri, EX.temSaidasProfissionais, Literal(saidas_profissionais)))
        
        area_cientifica_uri = EX[criar_uri_valido(area_cientifica)]
        if (area_cientifica_uri, RDF.type, None) not in g:
            g.add((area_cientifica_uri, RDF.type, EX.AreaCientifica))
            g.add((area_cientifica_uri, EX.temNome, Literal(area_cientifica)))
        
        g.add((mestrado_uri, EX.temAreaCientifica, area_cientifica_uri))
            
        
        regime_uri = EX[criar_uri_valido(regime)]
        if (regime_uri, RDF.type, None) not in g:
            g.add((regime_uri, RDF.type, EX.Regime))
            g.add((regime_uri, EX.temNome, Literal(regime)))
            
        g.add((mestrado_uri, EX.temRegime, EX[criar_uri_valido(regime)]))
        
        departamento_uri = EX[criar_uri_valido(departamento)]
        if (departamento_uri, RDF.type, None) not in g:
            g.add((departamento_uri, RDF.type, EX.Departamento))
            g.add((departamento_uri, EX.temNome, Literal(departamento)))
            
        g.add((mestrado_uri, EX.pertenceA, departamento_uri))
        
        g.add((EX[criar_uri_valido(universidade)], EX.ofereceCurso, mestrado_uri))

        # Processar unidades curriculares
        uc_nomes = request.form.getlist("uc_nome[]")
        uc_ects = request.form.getlist("uc_ects[]")
        uc_semestres = request.form.getlist("uc_semestre[]")
        uc_areas = request.form.getlist("uc_area_cientifica[]")

        for i in range(len(uc_nomes)):
            if uc_nomes[i].strip():
                uc_nome = uc_nomes[i]
                uc_id = f"{mestrado_id}_UC_{i}"
                uc_uri = EX[uc_id]
                oferta_uri = EX[f"oferta_{mestrado_id}_{i}"]

                # Criar UC
                g.add((uc_uri, RDF.type, EX.UnidadeCurricular))
                g.add((uc_uri, EX.temNome, Literal(uc_nome)))
                g.add((uc_uri, EX.temAreaCient, Literal(uc_areas[i])))

                # Criar Oferta UC
                g.add((oferta_uri, RDF.type, EX.OfertaUnidadeCurricular))
                g.add((oferta_uri, EX.incluiUnidadeCurricular, uc_uri))
                g.add((oferta_uri, EX.temAreaCient, Literal(uc_areas[i])))
                g.add((oferta_uri, EX.semestre, Literal(uc_semestres[i])))

                # Ligar Mestrado à Oferta
                g.add((mestrado_uri, EX.temOfertaUC, oferta_uri))

        # Salvar ontologia
        g.serialize("ontologias/cursos_povoados_um_utad_fctnova_uc.ttl", format="ttl")

        return redirect(url_for("mostrar_mestrados"))

    return render_template("adicionar_mestrado.html")

@app.route("/universidade/<nome>/mestrados")
def listar_mestrados_da_universidade(nome):
    nome = nome.lower()

    nome_mapping = {
        "minho": "Universidade do Minho",
        "coimbra": "Universidade de Coimbra",
        "fctnova": "Faculdade de Ciências e Tecnologia da Universidade NOVA de Lisboa",
        "utad": "Universidade de Trás-os-Montes e Alto Douro"
    }

    nome_completo = nome_mapping.get(nome)
    if not nome_completo:
        return "Universidade não reconhecida", 404

    area_filtro = request.args.get("area", "")

    query = f"""
    PREFIX : <http://www.example.org/disease-ontology#>
    SELECT ?curso ?nome ?areaNome WHERE {{
        ?curso a :Mestrado ;
               :temNome ?nome ;
               :temAreaCientifica ?area ;
               :pertenceA ?escola .
        ?escola :pertenceA ?universidade .
        ?universidade :temNome ?nomeUniversidade .
        ?area :temNome ?areaNome .
        FILTER(LCASE(?nomeUniversidade) = LCASE("{nome_completo}"))
    }}
    ORDER BY ?nome
    """

    resultados = g.query(query)

    cursos = []
    areas = set()

    for row in resultados:
        areas.add(str(row.areaNome))
        if area_filtro == "" or area_filtro == str(row.areaNome):
            cursos.append({
                "uri": str(row.curso),
                "nome": str(row.nome)
            })

    return render_template("mestrados.html", escola=nome_completo, cursos=cursos, areas=sorted(areas), area_atual=area_filtro)

@app.route("/universidade/<nome>/estatisticas")
def estatisticas_universidade(nome):
    nome_mapping = {
        "minho": "Universidade do Minho",
        "coimbra": "Universidade de Coimbra",
        "fctnova": "Faculdade de Ciências e Tecnologia da Universidade NOVA de Lisboa",
        "utad": "Universidade de Trás-os-Montes e Alto Douro"
    }

    nome_completo = nome_mapping.get(nome.lower())
    if not nome_completo:
        return "Universidade não reconhecida", 404

    query = f"""
    PREFIX : <http://www.example.org/disease-ontology#>
    SELECT ?areaNome (COUNT(?curso) AS ?numeroCursos)
    WHERE {{
        ?curso a :Mestrado ;
               :temAreaCientifica ?area ;
               :pertenceA ?escola .
        ?escola :pertenceA ?universidade .
        ?universidade :temNome ?nomeUniversidade .
        ?area :temNome ?areaNome .
        FILTER(LCASE(?nomeUniversidade) = LCASE("{nome_completo}"))
    }}
    GROUP BY ?areaNome
    ORDER BY DESC(?numeroCursos)
    """

    resultados = g.query(query)
    combinados = [(str(row.areaNome), int(row.numeroCursos)) for row in resultados]

    return render_template("estatisticas.html", combinados=combinados, universidade=nome_completo)


if __name__ == "__main__":
    app.run(debug=True)
