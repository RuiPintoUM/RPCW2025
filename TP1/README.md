# TPC 1

## Autor
### Rui Pinto

## Objectivo 

O objectivo deste TPC é a criação de uma ontologia apartir de um json tendoo como base um exemplo já fornecido. Para tal é utilizado um scipt em Python com a biblioteca RDFLib de forma a processar o JSON e fornecer um ficheiro em formato Turtle (.ttl) com a ontologia.

## Funcionamento 

1. **Criar a exemplo da ontologia**
    - É preciso criar um ficheiro `exameMedico.ttl` que contenha a um exmeplo da estrututa da ontologia 

2. **Executar o scrip**
    - Ao executar o script `convertor.py` os dados forncidos pelo ficheiro `exames.json` vão ser convertidos numa ontologia e vão ser escitos no ficheiro de output `final.ttl`
 
### Conclusão 

Este TPC mostra como, a partir de um exemplo, é possível automatizar a criação de uma ontologia em Turtle a partir de um JSON usando Python e RDFLib.
