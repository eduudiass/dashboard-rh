# Dashboard de RH

[Acessar Dashboard](https://dashboard-rh-eduardo.streamlit.app/)

Dashboard para análise de dados de pessoas construído com Python e Streamlit. Cobre as principais métricas de RH, como turnover, movimentação, absenteísmo, diversidade e horas extras. Com filtro por departamento e visual inspirado no meu portfólio pessoal.

## Funcionalidades

O Dashboard de RH reúne os principais indicadores de pessoas em uma única visão. A Visão Geral traz um resumo executivo com headcount, saídas, turnover e absenteísmo. Na aba de Turnover, a rotatividade aparece por departamento, com destaque para o pior índice. Admissões e Desligamentos mostra a movimentação mensal ao longo de 24 meses, e Absenteísmo apresenta a taxa média geral e por departamento. A seção de Diversidade cobre distribuição de gênero, faixa etária e representatividade por nível hierárquico. Em Horas Extras, o painel evidencia a relação entre hora extra e desligamento: quem faz hora extra tem 2,9 vezes mais chance de sair. Todos os indicadores respondem ao filtro por departamento na barra lateral.

## Sobre os dados

O projeto usa o [IBM HR Analytics Dataset](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset) como base. Como o dataset não possui série temporal nem dados de absenteísmo, esses dados foram gerados sinteticamente com NumPy. A lógica de cálculo fica isolada em `src/metrics.py`, separada da interface.

## Tecnologias

Python,
Pandas,
NumPy,
Plotly,
Streamlit

## Estrutura

    dashboard-rh/
    ├── data/
    │   ├── raw/
    │   │   └── WA_Fn-UseC_-HR-Employee-Attrition.csv
    │   └── processed/
    │       ├── movimentacao_mensal.csv
    │       └── absenteismo.csv
    ├── src/
    │   ├── data_gen.py
    │   └── metrics.py
    ├── .streamlit/
    │   └── config.toml
    ├── app.py
    ├── requirements.txt
    └── README.md

## Como executar

    pip install -r requirements.txt
    python src/data_gen.py
    streamlit run app.py

## Conceitos praticados

Transformação e agregação de dados com Pandas
Geração de dados sintéticos com NumPy
Visualizações interativas com Plotly
Análise de correlação sem ML (horas extras × turnover)
Separação de responsabilidades em módulos Python
Deploy de aplicação web com Streamlit Cloud

## Autor

Eduardo Dias, Estudante de Data Science & AI na PUCRS

[LinkedIn](https://linkedin.com/in/eduardodiasds) | [GitHub](https://github.com/eduudiass)
