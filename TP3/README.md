# TPC 2

##a
```

```

## b
```
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

select ?classe where {
  ?classe rdf:type owl:Class.
}
```

## c
```
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

select distinct ?prop where {
  ?s a :Rei .
  ?s ?prop ?o .
} order by ?prop
```

## d
```
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

select (count (?s) as ?triples) where {
  ?s a :Rei .
} 
```

## e
```
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

select ?nome ?data ?cognome where {
	?s a :Rei .
	?s :nome ?nome .
   	?s :cognomes ?cognome .
    ?s :nascimento ?data .
} 
```

## f
```
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

select ?nome ?data ?cognome ?dinastia where {
	?s a :Rei .
	?s :nome ?nome .
   	?s :cognomes ?cognome .
    ?s :nascimento ?data .
    ?s :temReinado ?reinado.
    ?reinado :dinastia ?dinastia.
} 
```

## g
```
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

select ?dinastia ( count (?nome) as ?triples )  where {
	?s a :Rei .
	?s :nome ?nome .
   	?s :cognomes ?cognome .
    ?s :nascimento ?data .
    ?s :temReinado ?reinado.
    ?reinado :dinastia ?dinastia.
} GROUP BY ?dinastia
```

## h
```
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

select ?descricao where {
	?s a :Descobrimento .
    ?s :data ?data .
    ?s :notas ?descricao .
} order by ?data
```

## i

```
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

select ?nome ?data ?rei where {
	?s a :Conquista .
    ?s :data ?data .
    ?s :nome ?nome .
    ?s :temReinado ?reinado .
    ?reinado :temMonarca ?monarca .
    ?monarca :nome ?rei .
} 
```

## j
```
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

select (count (?mandatos) as ?triples ) ?nome ?data where {
	?s a :Presidente .
   	?s :nome ?nome .
    ?s :nascimento ?data.
    ?s :mandato ?mandatos .
} group by ?nome ?data 
```

## k
```

```

## l
```
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>

select ?nomepart (COUNT(?nummili) as ?triplets) where {
    ?p a :Partido .
    ?p :nome ?nomepart .
    ?p :temMilitante ?nummili .
}
Group by ?nomepart
```

## m 
```

```
```

```