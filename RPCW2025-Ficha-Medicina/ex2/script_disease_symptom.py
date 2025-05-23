from rdflib import Graph, Namespace, Literal, RDF, OWL, URIRef, XSD
from rdflib.namespace import RDFS
import csv

csv_path = 'Disease_Syntoms.csv'
ttl_path = 'medical_base.ttl'
output_path = 'med_doencas.ttl'

n = Namespace("http://www.example.org/disease-ontology#")
g = Graph()
g.parse(ttl_path)

diseases = {}
syntoms = set()

with open(csv_path, newline='',encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    for linha in reader:
        
        disease = URIRef(f"{n}{linha[0].strip().replace(' ', '_').replace('(', '').replace(')', '')}")
        
        if disease not in diseases:
            diseases[disease] = set() 
        
        for synt in linha[1:]:
            if synt.strip():
                diseases[disease].add(synt.strip().replace(' ', '_'))
                
                if synt not in syntoms:
                    syntoms.add(synt.strip().replace(' ', '_'))
            
        
    for synt in syntoms:
        synt_uri = URIRef(f"{n}{synt}")
        g.add((synt_uri, RDF.type, n.Symptom))
        
    for disease_uri in diseases:
        g.add((disease_uri, RDF.type, n.Disease))
        
        for synt in diseases[disease_uri]:
            synt_uri = URIRef(f"{n}{synt}")
            g.add((disease_uri, n.hasSymptom, synt_uri))
            
print(g.serialize())
         
             
        