# Um jogo sobre a história de Portugal
# 2025-02-24 jcr
#
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
import random
import requests

app = Flask(__name__)
app.secret_key = 'História de Portugal'
CORS(app)

# Retrieve info from GraphDB
def query_graphdb(endpoint_url, sparql_query):
    headers = {
        'Accept': 'application/json', 
    }
    response = requests.get(endpoint_url, params={'query': sparql_query}, headers=headers)
    if response.status_code == 200:
        return response.json() 
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

endpoint = "http://localhost:7200/repositories/HistoriaPT"


sparql_query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
SELECT ?n ?o
    WHERE {
        ?s a :Rei.
        ?s :nome ?n .
        ?s :nascimento ?o.
    }
"""

result = query_graphdb(endpoint, sparql_query)
listaReis = []
for r in result['results']['bindings']:
    t = {
            'nome': r['n']['value'].split('#')[-1], 
            'dataNasc': r['o']['value'].split('#')[-1]
    }
    listaReis.append(t)



sparql_query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
SELECT ?b ?r
WHERE {
    ?s a :Batalha.
    ?s :nome ?b .
    ?s :resultado ?r.
    FILTER(?r != "Desconhecido")
}
"""

result = query_graphdb(endpoint, sparql_query)
listaWars = []
for r in result['results']['bindings']:
    t = {
            'nome': r['b']['value'].split('#')[-1], 
            'resultado': r['r']['value'].split('#')[-1]
    }
    listaWars.append(t)

sparql_query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
SELECT ?n ?dn
WHERE {
    ?s a :Rei.
    ?s :nome ?n .
    ?s :temReinado ?r .
    ?r :dinastia ?d.
    ?d :nome ?dn .
}
"""

result = query_graphdb(endpoint, sparql_query)
listaDinastias = []
for r in result['results']['bindings']:
    t = {
            'nome': r['n']['value'].split('#')[-1], 
            'dinastia': r['dn']['value'].split('#')[-1]
    }
    listaDinastias.append(t)

@app.route('/')
def home():
    session['score'] = 0
    return redirect(url_for('quiz'))

@app.route('/quiz', methods=['GET'])
def generate_question():
    
    question_type_list = ["king_birthday", "war_victory","dynasty_king"]
    #question_type_list = ["dynasty_king"]
    question_type = random.choice(question_type_list)

    print(question_type)
    
    if question_type == "king_birthday":
        reis = random.choices(listaReis, k=4)
        reiSel = reis[random.randrange(0,4)]
        question = {
            "question": f"Quando nasceu o rei {reiSel['nome']}?",
            "options": [reis[0]['dataNasc'], reis[1]['dataNasc'], reis[2]['dataNasc'], reis[3]['dataNasc']],
            "answer": reiSel['dataNasc']
        }
        html = 'quiz.html'
        
    elif question_type == "war_victory":
        opcoes = ["Vitória", "Derrota"]
        
        # Seleciona uma batalha aleatória da lista de batalhas
        wars = random.choices(listaWars, k=4)
        warSel = wars[random.randrange(0, 4)]

        print(f"war: {wars}")
        
        # Seleciona aleatoriamente o resultado esperado para a pergunta (Verdadeiro/Falso)
        resultado_pergunta = random.choice(opcoes)
        
        # Compara o resultado correto da batalha com o resultado gerado
        if resultado_pergunta == warSel["resultado"]:
            resposta = "Verdadeiro"
        else:
            resposta = "Falso"
        
        question = {
            "question": f"Portugal na batalha {warSel['nome']} obteve uma {resultado_pergunta}",
            "options": ["Verdadeiro", "Falso"],
            "answer": resposta,
        }
        html ='quiz.html'
        
    elif question_type == "dynasty_king":
        reis = random.choices(listaDinastias, k=4)
        
        dinastias_random = random.sample(reis, 4)
        
        question = {
            "question": f"Relaciona correctamente o rei com a sua dinastia",
            "kings": [reis[0]['nome'], reis[1]['nome'], reis[2]['nome'], reis[3]['nome']],
            "dynasties": [dinastias_random[0]['dinastia'], dinastias_random[1]['dinastia'], dinastias_random[2]['dinastia'], dinastias_random[3]['dinastia']],
            "answer": {king['nome']: king['dinastia'] for king in reis}
        }
        
        print(f"resposta certa {question['answer']}")
        html = 'quiz_associacao.html'
    
    return render_template(html, question=question)

#"options": [f"Portugal na batalha {wars[0]['nome']} obteve uma {wars[0]['resultado']}", f"Na Batalha {wars[1]['nome']} obteve uma {wars[1]['resultado']}", f"Na Batalha {wars[2]['nome']} obteve uma {wars[2]['resultado']}", f"Na Batalha {wars[3]['nome']} obteve uma {wars[3]['resultado']}"],


@app.route('/quiz', methods=['POST'])
def quiz():
    user_answer = request.form.get('answer')
    answer_correct = request.form.get('answerCorrect')
    correct = answer_correct == user_answer
    session['score'] = session.get('score', 0) + (1 if correct else 0)
    return render_template('result.html', correct=correct, correct_answer=answer_correct, score=session['score'])

@app.route('/score')
def score():
    return render_template('score.html', score=session.get('score', 0))

if __name__ == '__main__':
    app.run(debug=True)
