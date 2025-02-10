import json
from rdflib import Graph, URIRef, Literal, XSD, RDF

# Define Base URI
BASE_URI = "http://www.semanticweb.org/rui/ontologies/2025/TPC/"

graph = Graph()
graph.parse("exameMedico.ttl", format="ttl")

# Load JSON Dataset
with open('exames.json', 'r') as file:
    dataset = json.load(file)

# Define RDF Properties and Classes
pratica = URIRef(BASE_URI + "Pratica")

primeiroNome = URIRef(BASE_URI + "temPrimeiroNome")
ultimoNome = URIRef(BASE_URI + "temUltimoNome")
idade = URIRef(BASE_URI + "temIdade")
genero = URIRef(BASE_URI + "temGenero")
morada = URIRef(BASE_URI + "temMorada")
email = URIRef(BASE_URI + "temEmail")
clube = URIRef(BASE_URI + "temClube")
dataExame = URIRef(BASE_URI + "temData")
resultado = URIRef(BASE_URI + "temResultado")

# Function to Add Person
def add_pessoa(graph, pessoa_id, primeiro_nome, ultimo_nome, idade_value, genero_value, morada_value, email_value, clube_value, modalidade_uri, exame_uri):
    pessoa_uri = URIRef(BASE_URI + "Pessoa/" + pessoa_id)
    
    graph.add((pessoa_uri, RDF.type, URIRef(BASE_URI + "Pessoa")))
    graph.add((pessoa_uri, primeiroNome, Literal(primeiro_nome, datatype=XSD.string)))
    graph.add((pessoa_uri, ultimoNome, Literal(ultimo_nome, datatype=XSD.string)))
    graph.add((pessoa_uri, idade, Literal(idade_value, datatype=XSD.integer)))
    graph.add((pessoa_uri, genero, Literal(genero_value, datatype=XSD.string)))
    graph.add((pessoa_uri, morada, Literal(morada_value, datatype=XSD.string)))
    graph.add((pessoa_uri, email, Literal(email_value, datatype=XSD.string)))
    graph.add((pessoa_uri, clube, Literal(clube_value, datatype=XSD.string)))
    
    graph.add((pessoa_uri, pratica, modalidade_uri))

# Iterate Over Dataset
for entry in dataset:
    modalidade_uri = URIRef(BASE_URI + "Modalidade/" + entry["modalidade"])
    exame_uri = URIRef(BASE_URI + "Exame/" + entry["_id"])

    add_pessoa(graph, str(entry["_id"]), entry["nome"]["primeiro"], entry["nome"]["último"], 
               entry["idade"], entry["género"], entry["morada"], entry["email"], 
               entry["clube"], modalidade_uri, exame_uri)

    graph.add((exame_uri, RDF.type, URIRef(BASE_URI + "Exame")))
    graph.add((exame_uri, dataExame, Literal(entry["dataEMD"], datatype=XSD.string)))
    graph.add((exame_uri, resultado, Literal(entry["resultado"], datatype=XSD.boolean)))
    
    graph.add((modalidade_uri, RDF.type, URIRef(BASE_URI + "Modalidade")))

graph.serialize(destination="final.ttl", format="turtle")