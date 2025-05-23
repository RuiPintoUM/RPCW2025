
11.
    1. 
    ```spaqrl
      PREFIX owl: <http://www.w3.org/2002/07/owl#>
      PREFIX : <http://www.example.org/disease-ontology#>

      select (Count(distinct ?doencas) as ?nrdoencas) where{
          ?doencas a :Disease .
      }
    ```


    2.
    ```sparql 
      PREFIX owl: <http://www.w3.org/2002/07/owl#>
      PREFIX : <http://www.example.org/disease-ontology#>

      select ?doencas where{
          ?doencas a :Disease ;
                  :hasSymptom :yellowish_skin .
      }
    ```

    3.
    ```sparql
      PREFIX owl: <http://www.w3.org/2002/07/owl#>
      PREFIX : <http://www.example.org/disease-ontology#>

      select ?doencas where{
          ?doencas a :Disease ;
                  :hasTreatment :exercise .
      }
    ```

    4.
    ```sparql
      PREFIX owl: <http://www.w3.org/2002/07/owl#>
      PREFIX : <http://www.example.org/disease-ontology#>

      select ?doentesNome where{
          ?dontes a :Patient ;
              :name ?doentesNome .    	
      }
      Order by ?doentesNome
    ```

12.
```sparql
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
```
13.
```sparql
  PREFIX : <http://www.example.org/disease-ontology#>

  SELECT ?doenca (COUNT (?doenca) as ?doentes)
  where{
      ?s a :Patient;
        :hasDisease ?doenca.
  }

  Group by ?doenca
```

14.
```sparql
  PREFIX : <http://www.example.org/disease-ontology#>

  SELECT ?sintoma (COUNT(DISTINCT ?doenca) AS ?numDoencas)
  WHERE {
    ?doenca a :Disease ;
            :hasSymptom ?sintoma .
  }
  GROUP BY ?sintoma
  ORDER BY DESC(?numDoencas)
```

15.
```sparql
  PREFIX : <http://www.example.org/disease-ontology#>

  SELECT ?tratamento (COUNT(DISTINCT ?doenca) AS ?numDoencas)
  WHERE {
    ?doenca a :Disease ;
            :hasTreatment ?tratamento .
  }
  GROUP BY ?tratamento
  ORDER BY DESC(?numDoencas)
```
