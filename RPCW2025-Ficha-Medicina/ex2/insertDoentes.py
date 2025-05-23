from rdflib import Graph, Namespace, RDF, OWL, RDFS, Literal, XSD

g = Graph()
g.parse("med_doentes.ttl")

n = Namespace("http://www.example.org/disease-ontology#")

q="""
PREFIX : <http://www.example.org/disease-ontology#>

CONSTRUCT {
  ?patient :hasDisease ?disease .
}
WHERE {
  ?disease a :Disease ;
           :hasSymptom ?symptom .

  ?patient a :Patient ;
           :exhibitsSymptom ?symptom .

  # O paciente tem todos os sintomas da doença
  FILTER NOT EXISTS {
    ?disease :hasSymptom ?requiredSymptom .
    FILTER NOT EXISTS {
      ?patient :exhibitsSymptom ?requiredSymptom .
    }
  }

  # E o paciente não tem sintomas extra que não estão na doença
  FILTER NOT EXISTS {
    ?patient :exhibitsSymptom ?symptomExtra .
    FILTER NOT EXISTS {
      ?disease :hasSymptom ?symptomExtra .
    }
  }
}
"""

for r in g.query(q):
    print(r)
    g.add(r)

g.serialize(destination="med_doentes_diagonisticados.ttl", format="turtle")