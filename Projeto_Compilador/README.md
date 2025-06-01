# Portal de Mestrados em Portugal

Este projeto é uma aplicação web interativa que permite explorar, visualizar, adicionar e analisar cursos de mestrado oferecidos por várias universidades portuguesas. Foi desenvolvido no âmbito da unidade curricular de **Representação do Conhecimento e Raciocínio Web (RPCW)**, utilizando tecnologias semânticas e web scraping.

---

## Grupo de Trabalho

- **Jorge Teixeira** - PG55965 - [JorgeTeixeira20](https://github.com/JorgeTeixeira20) 
- **Rui Pinto** - PG56010 - [RuiPintoUM](https://github.com/RuiPintoUM)
- **Pedro Azevedo** - PG57897 - [Pexometro](https://github.com/Pexometro)

---

## Índice

1. [Objetivos e Motivação](#objetivos-e-motivação)
2. [Tecnologias Utilizadas](#tecnologias-utilizadas)
3. [Ontologia](#ontologia)
4. [Web Scraping e Povoamento](#web-scraping-e-povoamento)
5. [Funcionalidades](#funcionalidades)
6. [Estrutura do Projeto](#estrutura-do-projeto)
7. [Como Executar](#como-executar)
8. [Conclusão](#conclusão)

---

## Objetivos e Motivação

- Criar uma ontologia para representar cursos de mestrado, universidades, escolas e áreas científicas.
- Recolher dados reais a partir de websites oficiais e transformá-los em RDF com significado semântico.
- Desenvolver uma interface web que permita:
  - Navegar por universidades e escolas.
  - Filtrar e pesquisar mestrados.
  - Visualizar estatísticas por área científica.
  - Adicionar novos cursos via formulário.

---

## Tecnologias Utilizadas

- **Python 3.x** – Linguagem principal.
- **Flask** – Framework web para o back-end.
- **RDFlib** – Manipulação de grafos RDF e serialização `.ttl`.
- **SPARQL** – Consultas à ontologia.
- **HTML + CSS + Jinja2** – Front-end dinâmico.
- **BeautifulSoup + requests + selenium** – Web scraping.

---

## Ontologia

A ontologia do projeto foi concebida para representar de forma semântica e interligada toda a informação relativa aos cursos de mestrado em universidades portuguesas. Desenvolvida em formato RDF (Turtle), a ontologia define classes como `:Universidade`, `:Escola`, `:CursoMestrado`, `:UnidadeCurricular`, `:OfertaUnidadeCurricular` e `:AreaCientifica`, organizadas através de relações como `:temEscola`, `:ofereceCurso`, `:temAreaCient`, `:temOfertaUC`, `:incluiUnidadeCurricular` e `:semestre`.

A construção da ontologia foi feita de forma incremental: cada universidade teve um **script de scraping dedicado**, adaptado à sua estrutura web, responsável por extrair os dados relevantes. Os dados extraídos foram convertidos diretamente em RDF, gerando uma ontologia parcial por universidade. Estas ontologias foram depois **concatenadas sequencialmente** para formar uma ontologia única e povoada, que mantém coerência semântica entre diferentes fontes. A ontologia final tem o nome de `cursos_povoados_um_utad_fctnova_uc.ttl` e engloba a informação dos mestrados das universidades: UM, UTAD, Nova e UC.

Esta abordagem modular permitiu uma fácil expansão do conhecimento, garantindo que novas universidades pudessem ser integradas sem reformular a estrutura existente. A inclusão da entidade `:OfertaUnidadeCurricular` facilitou a representação detalhada das unidades curriculares, associando-lhes semestre e área científica, o que viabilizou consultas mais precisas e uma visualização enriquecida na aplicação.


---

## Web Scraping e Povoamento

Para adquirir os dados necessários ao povoamento da ontologia, foram desenvolvidos scripts de web scraping adaptados à estrutura de cada site universitário. Os scripts foram feitos maioritariamente com recurso a __BeautifulSoup__ e __requests__, sendo utilizado __Selenium__ quando necessário. Para cada mestrado, foram recolhidas as informações relevantes de forma a maximizar a correspondência com os conceitos definidos na ontologia. Todos os dados foram guardados num ficheiro __JSON__ estruturado.

No povoamento, foi feito o parse dos ficheiros __JSON__, e com o auxílio da biblioteca __rdflib__ foi construído um __grafo RDF__, respeitando a estrutura da ontologia previamente definida.

## Funcionalidades

-  Listagem de universidades.
-  Escolas e departamentos por universidade.
-  Visualização e detalhes dos cursos de mestrado.
-  Pesquisa por nome e filtro por área científica.
-  Estatísticas globais ou por universidade.
-  Adição de novos mestrados via formulário.
-  Ontologia em formato `.ttl`, representando todas as entidades semânticas.

---

## Estrutura do Projeto

```

├── app.py                   # Aplicação principal Flask
├── templates/               # Templates HTML Jinja2
├── static/                  # Ficheiros CSS e imagens
├── scripts/                 # Scripts de scraping/povoamento
│   ├── uminho/
│   ├── utad/
│   ├── coimbra/
│   └── fctnova/
├── ontologias/
│   ├── cursos.ttl           # Ontologia base
│   └── cursos_povoados_um_utad_fctnova_uc.ttl  # Ontologia com todos dados
```

---

## Como Executar

1. Instala dependências:
```bash
pip install flask rdflib beautifulsoup4
```

2. Executa a aplicação:
```bash
python app.py
```

3. Abrir o browser, neste link:
```
http://127.0.0.1:5000
```

---
## Conclusão

Este projeto demonstrou a aplicação de ontologias no desenvolvimento web, aliando scraping, processamento semântico e visualização. É uma plataforma escalável que poderá, futuramente, pretende-se alargar o processo de scraping a todos os mestrados de todas as universidades do país, de forma a criar uma ontologia abrangente e representativa da oferta formativa nacional.




