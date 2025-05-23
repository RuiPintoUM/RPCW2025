from rdflib import Graph, Namespace, Literal, RDF, OWL, URIRef, XSD
from rdflib.namespace import RDFS
import csv

csv_path = 'Disease_Treatment.csv'
ttl_path = 'med_descrip.ttl'

n = Namespace("http://www.example.org/disease-ontology#")
g = Graph()
g.parse(ttl_path)

treatments = set()
disease_treatment = {}

with open(csv_path, newline='',encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    
    for linha in reader :
        diseaseURI = URIRef(f"{n}{linha[0].strip().replace(' ', '_').replace('(', '').replace(')', '')}")
        
        disease_treatment[diseaseURI] = set()
        for treatment in linha[1:]:
            if treatment not in treatments:
                if treatment.strip():
                    treatmentURI = URIRef(f"{n}{treatment.strip().replace(' ', '_')}")
                    treatments.add(treatmentURI)

                    disease_treatment[diseaseURI].add(treatmentURI)

    for treatmentURI in treatments:
        g.add((treatmentURI, RDF.type, n.Treatment))
        
    for diseaseURI in disease_treatment:
        for treatmentURI in disease_treatment[diseaseURI]:
            g.add((diseaseURI, n.hasTreatment, treatmentURI))
            
print(g.serialize())