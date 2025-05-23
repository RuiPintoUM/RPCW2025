# TPC - Extração e Representação de Dados de Filmes da IMDb

## Objetivo
Este trabalho prático tem como objetivo extrair, transformar e representar dados de filmes provenientes da base de dados IMDb, estruturando-os em um grafo RDF conforme uma ontologia definida em `cinema-base.ttl`.

## Etapas Realizadas

1. **Download dos Dados IMDb**
   - O script `get_imdb_movie_files.txt` foi usado para baixar e descompactar os principais arquivos `.tsv` da base IMDb.

2. **Processamento dos Dados**
   - O script `concatenate_data.py` foi responsável por:
     - Selecionar 500 filmes válidos da IMDb.
     - Associar idiomas e países de origem.
     - Relacionar pessoas (atores, diretores, escritores) aos filmes.
     - Gerar um dataset final em JSON consolidando essas informações.

3. **População do Grafo RDF**
   - O script `populate.py` leu os dados JSON gerados e populou a ontologia `cinema-base.ttl` com indivíduos de:
     - Filmes, pessoas, géneros, países e línguas.
     - Relacionamentos como “atuou”, “realizou”, “escreveu”, “temGénero”, “temLíngua”, etc.

4. **Arquivo Final**
   - O grafo RDF resultante foi serializado no formato Turtle.


## Como Executar

1. **Baixar e preparar os dados IMDb:**
   ```bash
    ./get_imdb_movie_files.txt
   ```

2. **Processar os dados e gerar o dataset estruturado:**
   ```bash
   python3 concatenate_data.py
   ```

3. **Gerar o grafo RDF com base no dataset:**
   ```bash
   python populate.py > cinema.ttl
   ```