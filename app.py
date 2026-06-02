import streamlit as st
import plotly.express as px
import sys
import os

# permite importar os módulos da pasta src
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from metrics import carregar_dados, calcular_turnover, calcular_diversidade, calcular_absenteismo

# configuração da página
st.set_page_config(page_title="Dashboard RH", layout="wide")

# carrega os dados
ibm, movimentacao = carregar_dados()

# título
st.title("Dashboard de Recursos Humanos")

# aba de navegação
aba = st.sidebar.radio("Navegação", [
    "Visão Geral",
    "Turnover",
    "Admissões e Desligamentos",
    "Absenteísmo",
    "Diversidade"
])

# VISÃO GERAL
if aba == "Visão Geral":
    taxa, saidas, total, turnover_depto = calcular_turnover(ibm)

    st.subheader("Visão Geral")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Funcionários", total)
    col2.metric("Saídas", saidas)
    col3.metric("Turnover Geral", f"{taxa}%")

    st.divider()

    st.markdown("**Desenvolvido por Eduardo Dias**")
    st.markdown("[LinkedIn](https://linkedin.com/in/eduardodiasds) | [GitHub](https://github.com/eduudiass)")

# TURNOVER
elif aba == "Turnover":
    taxa, saidas, total, turnover_depto = calcular_turnover(ibm)

    st.subheader("Turnover por Departamento")

    fig = px.bar(
        turnover_depto,
        x="departamento",
        y="turnover_pct",
        title="Taxa de Turnover por Departamento (%)",
        labels={"turnover_pct": "Turnover (%)", "departamento": "Departamento"},
        color="turnover_pct",
        color_continuous_scale="Reds",
        range_color=[0, turnover_depto["turnover_pct"].max() * 1.2]
    )
    st.plotly_chart(fig, use_container_width=True)

# ADMISSÕES E DESLIGAMENTOS
elif aba == "Admissões e Desligamentos":
    st.subheader("Movimentação Mensal")

    fig = px.line(
        movimentacao,
        x="data",
        y=["admissoes", "desligamentos"],
        title="Admissões e Desligamentos por Mês",
        labels={"value": "Quantidade", "data": "Mês", "variable": "Tipo"}
    )
    st.plotly_chart(fig, use_container_width=True)

# ABSENTEÍSMO
elif aba == "Absenteísmo":
    media_abs, abs_depto = calcular_absenteismo(ibm)

    st.subheader("Absenteísmo")
    st.metric("Taxa Média Geral", f"{media_abs}%")

    fig = px.bar(
        abs_depto,
        x="departamento",
        y="taxa_media",
        title="Taxa Média de Absenteísmo por Departamento (%)",
        labels={"taxa_media": "Absenteísmo (%)", "departamento": "Departamento"},
        color="taxa_media",
        color_continuous_scale="Blues",
        range_color=[0, abs_depto["taxa_media"].max() * 1.2]
    )
    st.plotly_chart(fig, use_container_width=True)

# DIVERSIDADE
elif aba == "Diversidade":
    genero, genero_nivel, faixa = calcular_diversidade(ibm)

    st.subheader("Diversidade")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.pie(
            values=genero.values,
            names=genero.index,
            title="Distribuição de Gênero"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        faixa_df = faixa.reset_index()
        faixa_df.columns = ["faixa_etaria", "quantidade"]
        fig = px.bar(
            faixa_df,
            x="faixa_etaria",
            y="quantidade",
            title="Distribuição por Faixa Etária",
            labels={"quantidade": "Funcionários", "faixa_etaria": "Faixa Etária"},
            color="quantidade",
            color_continuous_scale="Blues",
            range_color=[0, faixa_df["quantidade"].max() * 1.2]
        )
        st.plotly_chart(fig, use_container_width=True)