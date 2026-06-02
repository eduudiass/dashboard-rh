# Dashboard de RH

[Acessar Dashboard](https://dashboard-rh-eduardo.streamlit.app/)

Dashboard para análise de dados de pessoas construído com Python e Streamlit. Cobre as principais métricas de RH: turnover, admissões, desligamentos, absenteísmo e diversidade em uma única aplicação interativa.

## Sobre

O projeto usa o dataset IBM HR Analytics como base. Como o dataset não possui série temporal nem dados de absenteísmo, gerei esses dados sinteticamente com NumPy para completar a análise. A lógica de cálculo das métricas fica separada da interface, o que facilita manutenção e expansão.

## Funcionalidades

- Visão geral com headcount, saídas e taxa de turnover
- Turnover por departamento
- Admissões e desligamentos mês a mês
- Absenteísmo médio e por departamento
- Distribuição de gênero e faixa etária

## Tecnologias

- Python 3
- Pandas
- NumPy
- Plotly
- Streamlit

## Estrutura do projeto

    dashboard-rh/
    ├── data/
    │   ├── raw/
    │   │   └── WA_Fn-UseC_-HR-Employee-Attrition.csv
    │   └── processed/
    │       ├── movimentacao_mensal.csv
    │       └── absenteismo.csv
    ├── notebook/
    │   └── eda.ipynb
    ├── src/
    │   ├── data_gen.py
    │   └── metrics.py
    ├── app.py
    ├── requirements.txt
    └── README.md

## Como executar

    pip install -r requirements.txt

    python src/data_gen.py

    streamlit run app.py

## Conceitos praticados

- Transformação e agregação de dados com Pandas
- Geração de dados sintéticos com NumPy
- Visualizações interativas com Plotly
- Aplicação web com Streamlit
- Separação de responsabilidades em módulos Python

## Autor

Eduardo Dias — Estudante de Data Science & AI na PUCRS

[LinkedIn](https://linkedin.com/in/eduardodiasds) | [GitHub](https://github.com/eduudiass)