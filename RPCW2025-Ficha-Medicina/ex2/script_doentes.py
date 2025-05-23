from rdflib import Graph, Namespace, Literal, RDF, OWL, URIRef, XSD
from rdflib.namespace import RDFS
import json

json_path = 'doentes.json'
ttl_path = 'med_tratamentos.ttl'

n = Namespace("http://www.example.org/disease-ontology#")
g = Graph()
g.parse(ttl_path)

with open(json_path, encoding='utf-8') as f:
    doentes = json.load(f)
    
for i, doente in enumerate(doentes):
    doente_id = f"{i+1}"
    paciente_uri = URIRef(f"{n}{doente_id}")

    g.add((paciente_uri, RDF.type, n.Patient))
    g.add((paciente_uri, n.name, Literal(doente["nome"], datatype=XSD.string)))

    for sintoma in doente["sintomas"]:
        sint_uri = URIRef(f"{n}{sintoma.strip().replace(' ', '_')}")
        g.add((paciente_uri, n.exhibitsSymptom, sint_uri))
        
print(g.serialize())