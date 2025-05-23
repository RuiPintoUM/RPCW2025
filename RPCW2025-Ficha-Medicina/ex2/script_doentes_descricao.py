from rdflib import Graph, Namespace, Literal, RDF, OWL, URIRef, XSD
from rdflib.namespace import RDFS
import csv

csv_path = 'Disease_Description.csv'
ttl_path = 'med_doencas.ttl'

n = Namespace("http://www.example.org/disease-ontology#")
g = Graph()
g.parse(ttl_path)

g.add((n.hasDescription, RDF.type, OWL.DatatypeProperty))
g.add((n.hasDescription, RDFS.domain, n.Disease))
g.add((n.hasDescription, RDFS.range, XSD.string))


with open(csv_path, newline='',encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    
    for linha in reader:
        diseaseURI = URIRef(f"{n}{linha[0].strip().replace(' ', '_').replace('(', '').replace(')', '')}")
        
        description = linha[1].strip()
        g.add((diseaseURI, n.hasDescription, Literal(description, datatype=XSD.string)))

print(g.serialize())    
