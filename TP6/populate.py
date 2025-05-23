import json
from rdflib import Graph, Namespace, Literal, RDF, OWL, URIRef

g = Graph()
g.parse("cinema-base.ttl")

n = Namespace("http://www.semanticweb.org/afonsoabc36/2025/cinema#")

with open("data/movies.json","r",encoding="utf-8") as f:
    movies = json.load(f)

for id_,name in movies["people"].items():
    id_ = URIRef(n[id_])
    g.add((id_, RDF.type, OWL.NamedIndividual))
    g.add((id_, RDF.type, n.Pessoa))
    g.add((id_, n.name, Literal(name)))

for id_ in movies["countries"]:
    id_ = URIRef(n[id_])
    g.add((id_, RDF.type, OWL.NamedIndividual))
    g.add((id_, RDF.type, n.País))

for id_ in movies["languages"]:
    id_ = URIRef(n[id_])
    g.add((id_, RDF.type, OWL.NamedIndividual))
    g.add((id_, RDF.type, n.Língua))

for id_ in movies["genres"]:
    id_ = URIRef(n[id_])
    g.add((id_, RDF.type, OWL.NamedIndividual))
    g.add((id_, RDF.type, n.Género))

for movie in movies["movies"]:
    id_ = URIRef(n[movie["id"]])
    g.add((id_, RDF.type, OWL.NamedIndividual))
    g.add((id_, RDF.type, n.Filme))

    argumento_uri = URIRef(n[f"Argumento{movie['id']}"])
    g.add((argumento_uri, RDF.type, OWL.NamedIndividual))
    g.add((argumento_uri, RDF.type, n.Argumento))
    g.add((id_, n.temArgumento, argumento_uri))

    genres = movie["genres"]
    for genre in genres:
        g.add((id_, n.temGénero, n[genre]))

    if movie["originalLanguage"]:
        g.add((id_, n.temLíngua, n[movie["originalLanguage"]]))

    g.add((id_, n.temPaísOrigem, Literal(movie["originalCountry"])))
    g.add((id_, n.data, Literal(movie["releaseYear"])))
    g.add((id_, n.duração, Literal(movie["duration"])))

    for person in movie["peopleInvolved"]:
        person_uri = URIRef(n[person["nconst"]])
        category = person.get("category", "").lower()

        if category == "director":
            g.add((person_uri, n.realizou, id_))
        elif category == "writer":
            g.add((person_uri, n.escreveu, argumento_uri))
        elif category == "actor" or category == "actress":
            g.add((person_uri, n.atuou, id_))


print(g.serialize(format="turtle"))
