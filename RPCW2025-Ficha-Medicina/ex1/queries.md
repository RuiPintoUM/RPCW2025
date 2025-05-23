1.
```sparql
  PREFIX owl: <http://www.w3.org/2002/07/owl#>
  PREFIX : <http://www.semanticweb.org/rui/ontologies/2025/ficha_afericao/>

  select ?class where{
      ?class a owl:Class .
      
      FILTER((STRSTARTS(STR(?class) , STR(:))))
  }
```
2.
```sparql
  PREFIX owl: <http://www.w3.org/2002/07/owl#>
  PREFIX : <http://www.semanticweb.org/rui/ontologies/2025/ficha_afericao/>

  select (COUNT(DISTINCT ?object) AS ?objectProperties ) where{
      ?object a owl:ObjectProperty .
  }
```
3.
```sparql
  PREFIX owl: <http://www.w3.org/2002/07/owl#>
  PREFIX : <http://www.semanticweb.org/rui/ontologies/2025/ficha_afericao/>

  select (COUNT(DISTINCT ?indiv) AS ?individuos ) where{
      ?indiv a owl:NamedIndividual .
  }
```
4.
```sparql
  PREFIX owl: <http://www.w3.org/2002/07/owl#>
  PREFIX : <http://www.semanticweb.org/rui/ontologies/2025/ficha_afericao/>


  SELECT ?agricultor
  WHERE {
    ?agricultor :cultiva :Tomate .
  }
```
5.
```sparql
  PREFIX owl: <http://www.w3.org/2002/07/owl#>
  PREFIX : <http://www.semanticweb.org/rui/ontologies/2025/ficha_afericao/>


  SELECT ?contratador
  WHERE {
    ?contratador a :Agricultor .
    ?contratador :contrata :Trabalhador .
  }
```