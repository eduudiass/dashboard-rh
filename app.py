import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# permite importar os módulos da pasta src
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from metrics import carregar_dados, calcular_turnover, calcular_diversidade, calcular_absenteismo

# configuração da página
st.set_page_config(page_title="Dashboard RH", layout="wide")

# carrega os dados
ibm, movimentacao = carregar_dados()

# título principal
st.title("Dashboard de Recursos Humanos")

# menu de navegação na barra lateral
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

    # exibe os três KPIs principais lado a lado
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Funcionários", total)
    col2.metric("Saídas", saidas)
    col3.metric("Turnover Geral", f"{taxa}%")

    st.divider()

    # rodapé com autor e links
    st.markdown("**Desenvolvido por Eduardo Dias**")
    st.markdown("[LinkedIn](https://linkedin.com/in/eduardodiasds) | [GitHub](https://github.com/eduudiass)")

# TURNOVER
elif aba == "Turnover":
    taxa, saidas, total, turnover_depto = calcular_turnover(ibm)

    st.subheader("Turnover por Departamento")

    # gráfico de barras com escala de cor iniciando em zero para evitar barras brancas
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

    # gráfico de linha com duas séries: admissões e desligamentos
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

    # KPI de taxa média geral
    st.metric("Taxa Média Geral", f"{media_abs}%")

    # gráfico de barras com escala de cor iniciando em zero
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
        # gráfico de pizza com cores definidas por gênero
        fig_genero = go.Figure(go.Pie(
            labels=genero.index,
            values=genero.values,
            marker=dict(colors=["#4A90D9", "#E8A0BF"])
        ))
        fig_genero.update_layout(
            title="Distribuição de Gênero",
            showlegend=True
        )
        st.plotly_chart(fig_genero, use_container_width=True)

    with col2:
        faixa_df = faixa.reset_index()
        faixa_df.columns = ["faixa_etaria", "quantidade"]

        # usando go.Figure para evitar herança de legenda do gráfico de pizza
        fig_faixa = go.Figure(go.Bar(
            x=faixa_df["faixa_etaria"],
            y=faixa_df["quantidade"],
            marker_color="#4A90D9",
            name=""
        ))
        fig_faixa.update_layout(
            title="Distribuição por Faixa Etária",
            xaxis_title="Faixa Etária",
            yaxis_title="Funcionários",
            showlegend=False
        )
        st.plotly_chart(fig_faixa, use_container_width=True)