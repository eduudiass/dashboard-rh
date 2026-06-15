import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from metrics import carregar_dados, calcular_turnover, calcular_diversidade, calcular_absenteismo

st.set_page_config(
    page_title="Dashboard RH",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main .block-container {
    background-color: #F0F4F8;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D1B2A 0%, #1B3A5C 100%);
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: #CBD5E1 !important;
}

.kpi-card {
    background: white;
    border-radius: 12px;
    padding: 20px 22px 16px 22px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    border-top: 3px solid #2563EB;
    height: 100%;
}
.kpi-label {
    font-size: 11px;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 10px;
}
.kpi-value {
    font-size: 32px;
    font-weight: 700;
    color: #0F2944;
    line-height: 1;
}
.kpi-sub {
    font-size: 11px;
    color: #94A3B8;
    margin-top: 8px;
}

.page-title {
    font-size: 22px;
    font-weight: 700;
    color: #0F2944;
    margin-bottom: 2px;
}
.page-subtitle {
    font-size: 13px;
    color: #94A3B8;
    margin-bottom: 20px;
}
.section-divider {
    border: none;
    border-top: 1px solid #E2E8F0;
    margin: 20px 0;
}

#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


def kpi(label, value, sub="", accent="#2563EB"):
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    st.markdown(f"""
    <div class="kpi-card" style="border-top-color:{accent}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {sub_html}
    </div>""", unsafe_allow_html=True)


def estilo_chart(fig, title="", show_legend=False):
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color="#0F2944"), x=0, xanchor="left"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter, sans-serif", color="#374151", size=12),
        margin=dict(t=50, b=20, l=10, r=10),
        showlegend=show_legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False, linecolor="#E2E8F0", tickcolor="#E2E8F0"),
        yaxis=dict(gridcolor="#F1F5F9", linecolor="white"),
    )
    return fig


ibm, movimentacao = carregar_dados()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:24px 0 20px 0;text-align:center;">
        <div style="font-size:36px">👥</div>
        <div style="font-size:17px;font-weight:700;color:white;margin-top:8px">Dashboard RH</div>
        <div style="font-size:11px;color:#64748B;margin-top:4px;letter-spacing:0.5px">ANÁLISE DE PESSOAS</div>
    </div>
    <hr style="border-color:#1E4976;margin-bottom:12px">
    """, unsafe_allow_html=True)

    aba = st.radio(
        "nav",
        ["Visão Geral", "Turnover", "Admissões e Desligamentos", "Absenteísmo", "Diversidade"],
        label_visibility="collapsed"
    )

    st.markdown("""
    <div style="margin-top:40px;padding:0 8px;text-align:center;">
        <div style="font-size:11px;color:#475569;line-height:1.8">
            Desenvolvido por<br>
            <a href="https://linkedin.com/in/eduardodiasds" style="color:#93C5FD;text-decoration:none">Eduardo Dias</a>
            &nbsp;·&nbsp;
            <a href="https://github.com/eduudiass" style="color:#93C5FD;text-decoration:none">GitHub</a>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Visão Geral ──────────────────────────────────────────────────────────────
if aba == "Visão Geral":
    taxa, saidas, total, turnover_depto = calcular_turnover(ibm)
    media_abs, abs_depto = calcular_absenteismo(ibm)

    st.markdown('<div class="page-title">Visão Geral</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Resumo executivo dos principais indicadores de RH</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi("Total de Funcionários", f"{total:,}", accent="#2563EB")
    with col2:
        kpi("Desligamentos", saidas, accent="#DC2626")
    with col3:
        alerta = "acima do limite recomendado" if taxa > 10 else "dentro do esperado"
        cor_taxa = "#DC2626" if taxa > 10 else "#16A34A"
        kpi("Turnover Geral", f"{taxa}%", alerta, accent=cor_taxa)
    with col4:
        kpi("Absenteísmo Médio", f"{media_abs}%", "dias ausentes / dias úteis", accent="#F59E0B")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        cores = ["#DC2626" if v == turnover_depto["turnover_pct"].max() else "#2563EB"
                 for v in turnover_depto["turnover_pct"]]
        fig = go.Figure(go.Bar(
            x=turnover_depto["departamento"],
            y=turnover_depto["turnover_pct"],
            marker_color=cores,
            text=[f"{v}%" for v in turnover_depto["turnover_pct"]],
            textposition="outside",
            width=0.45
        ))
        estilo_chart(fig, "Turnover por Departamento (%)")
        fig.update_layout(yaxis_range=[0, turnover_depto["turnover_pct"].max() * 1.35])
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=movimentacao["data"], y=movimentacao["admissoes"],
            name="Admissões", line=dict(color="#16A34A", width=2.5),
            fill="tozeroy", fillcolor="rgba(22,163,74,0.07)"
        ))
        fig.add_trace(go.Scatter(
            x=movimentacao["data"], y=movimentacao["desligamentos"],
            name="Desligamentos", line=dict(color="#DC2626", width=2.5),
            fill="tozeroy", fillcolor="rgba(220,38,38,0.06)"
        ))
        estilo_chart(fig, "Movimentação Mensal", show_legend=True)
        st.plotly_chart(fig, use_container_width=True)


# ── Turnover ──────────────────────────────────────────────────────────────────
elif aba == "Turnover":
    taxa, saidas, total, turnover_depto = calcular_turnover(ibm)

    st.markdown('<div class="page-title">Análise de Turnover</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Taxa de rotatividade por departamento</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        cor = "#DC2626" if taxa > 10 else "#16A34A"
        kpi("Turnover Geral", f"{taxa}%", "acima de 10% é crítico" if taxa > 10 else "dentro do esperado", accent=cor)
    with col2:
        kpi("Total de Saídas", saidas, accent="#DC2626")
    with col3:
        kpi("Força de Trabalho", f"{total:,}", accent="#2563EB")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    max_val = turnover_depto["turnover_pct"].max()
    cores = ["#DC2626" if v == max_val else "#2563EB" for v in turnover_depto["turnover_pct"]]

    fig = go.Figure(go.Bar(
        x=turnover_depto["departamento"],
        y=turnover_depto["turnover_pct"],
        marker_color=cores,
        text=[f"{v}%" for v in turnover_depto["turnover_pct"]],
        textposition="outside",
        width=0.45
    ))
    estilo_chart(fig, "Taxa de Turnover por Departamento (%)")
    fig.update_layout(yaxis_range=[0, max_val * 1.35])
    st.plotly_chart(fig, use_container_width=True)


# ── Admissões e Desligamentos ─────────────────────────────────────────────────
elif aba == "Admissões e Desligamentos":
    total_adm = int(movimentacao["admissoes"].sum())
    total_des = int(movimentacao["desligamentos"].sum())
    saldo = total_adm - total_des

    st.markdown('<div class="page-title">Admissões e Desligamentos</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Movimentação de pessoal nos últimos 24 meses</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi("Total de Admissões", f"{total_adm:,}", accent="#16A34A")
    with col2:
        kpi("Total de Desligamentos", f"{total_des:,}", accent="#DC2626")
    with col3:
        cor_saldo = "#16A34A" if saldo >= 0 else "#DC2626"
        kpi("Saldo de Pessoal", f"+{saldo}" if saldo >= 0 else str(saldo), accent=cor_saldo)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=movimentacao["data"], y=movimentacao["admissoes"],
        name="Admissões", line=dict(color="#16A34A", width=2.5),
        fill="tozeroy", fillcolor="rgba(22,163,74,0.07)"
    ))
    fig.add_trace(go.Scatter(
        x=movimentacao["data"], y=movimentacao["desligamentos"],
        name="Desligamentos", line=dict(color="#DC2626", width=2.5),
        fill="tozeroy", fillcolor="rgba(220,38,38,0.06)"
    ))
    estilo_chart(fig, "Movimentação Mensal de Pessoal", show_legend=True)
    st.plotly_chart(fig, use_container_width=True)


# ── Absenteísmo ───────────────────────────────────────────────────────────────
elif aba == "Absenteísmo":
    media_abs, abs_depto = calcular_absenteismo(ibm)

    st.markdown('<div class="page-title">Absenteísmo</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Taxas de ausência por departamento</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        kpi("Taxa Média Geral", f"{media_abs}%", "ausências / dias úteis", accent="#F59E0B")
    with col2:
        depto_critico = abs_depto.loc[abs_depto["taxa_media"].idxmax(), "departamento"]
        kpi("Maior Absenteísmo", depto_critico, "departamento de atenção", accent="#DC2626")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    max_abs = abs_depto["taxa_media"].max()
    cores = ["#DC2626" if v == max_abs else "#F59E0B" for v in abs_depto["taxa_media"]]

    fig = go.Figure(go.Bar(
        x=abs_depto["departamento"],
        y=abs_depto["taxa_media"],
        marker_color=cores,
        text=[f"{v}%" for v in abs_depto["taxa_media"]],
        textposition="outside",
        width=0.45
    ))
    estilo_chart(fig, "Taxa Média de Absenteísmo por Departamento (%)")
    fig.update_layout(yaxis_range=[0, max_abs * 1.35])
    st.plotly_chart(fig, use_container_width=True)


# ── Diversidade ───────────────────────────────────────────────────────────────
elif aba == "Diversidade":
    genero, genero_nivel, faixa = calcular_diversidade(ibm)

    st.markdown('<div class="page-title">Diversidade</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Composição de gênero e faixa etária do quadro</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        fig_genero = go.Figure(go.Pie(
            labels=genero.index,
            values=genero.values,
            marker=dict(colors=["#2563EB", "#EC4899"]),
            hole=0.5,
            textinfo="label+percent",
            textfont_size=13,
            hovertemplate="%{label}: %{value}%<extra></extra>"
        ))
        fig_genero.update_layout(
            title=dict(text="Distribuição de Gênero", font=dict(size=15, color="#0F2944"), x=0),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Inter, sans-serif"),
            showlegend=False,
            margin=dict(t=50, b=20, l=20, r=20),
        )
        st.plotly_chart(fig_genero, use_container_width=True)

    with col2:
        faixa_df = faixa.reset_index()
        faixa_df.columns = ["faixa_etaria", "quantidade"]

        fig_faixa = go.Figure(go.Bar(
            x=faixa_df["faixa_etaria"].astype(str),
            y=faixa_df["quantidade"],
            marker_color="#2563EB",
            text=faixa_df["quantidade"],
            textposition="outside",
            width=0.5
        ))
        estilo_chart(fig_faixa, "Distribuição por Faixa Etária")
        fig_faixa.update_layout(
            yaxis_range=[0, faixa_df["quantidade"].max() * 1.2],
            xaxis_title="Faixa Etária",
            yaxis_title="Funcionários"
        )
        st.plotly_chart(fig_faixa, use_container_width=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    nivel_map = {1: "Júnior", 2: "Pleno", 3: "Sênior", 4: "Especialista", 5: "Gestão"}
    genero_nivel["nivel_label"] = genero_nivel["nivel"].map(nivel_map)

    fig_nivel = px.bar(
        genero_nivel,
        x="nivel_label",
        y="pct",
        color="genero",
        barmode="group",
        color_discrete_map={"Masculino": "#2563EB", "Feminino": "#EC4899"},
        text=genero_nivel["pct"].apply(lambda v: f"{v}%"),
        category_orders={"nivel_label": ["Júnior", "Pleno", "Sênior", "Especialista", "Gestão"]}
    )
    estilo_chart(fig_nivel, "Representatividade de Gênero por Nível Hierárquico (%)", show_legend=True)
    fig_nivel.update_layout(
        xaxis_title="Nível",
        yaxis_title="Percentual (%)",
        legend_title="Gênero"
    )
    fig_nivel.update_traces(textposition="outside")
    st.plotly_chart(fig_nivel, use_container_width=True)
