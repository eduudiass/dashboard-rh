import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from metrics import carregar_dados, calcular_turnover, calcular_diversidade, calcular_absenteismo, calcular_horas_extras

st.set_page_config(
    page_title="Dashboard RH",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Fundo creme com textura de grid — igual ao portfólio */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
    background-color: #F5F0E4 !important;
    background-image:
        linear-gradient(rgba(150,130,100,0.10) 1px, transparent 1px),
        linear-gradient(90deg, rgba(150,130,100,0.10) 1px, transparent 1px) !important;
    background-size: 28px 28px !important;
}
.block-container { padding-top: 2.5rem !important; padding-bottom: 2rem !important; }

/* Sidebar — verde escuro, mesma cor do botão do portfólio */
[data-testid="stSidebar"] {
    background: #1A3D2B !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * { color: #D6CCBA !important; }

[data-testid="stSidebar"] [data-baseweb="radio"] > div:first-child { display: none !important; }
[data-testid="stSidebar"] [role="radiogroup"] { gap: 2px; }
[data-testid="stSidebar"] label[data-baseweb="radio"] {
    padding: 9px 14px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
    transition: background 0.1s;
}
[data-testid="stSidebar"] label[data-baseweb="radio"]:hover {
    background: rgba(214,204,186,0.12) !important;
}

/* KPI Cards — creme claro sobre o fundo texturizado */
.kpi-card {
    background: #FBF8F1;
    border-radius: 6px;
    padding: 22px 24px 18px 24px;
    border: 1px solid #DDD4BC;
    height: 100%;
}
.kpi-label {
    font-size: 10px;
    font-weight: 600;
    color: #8A7D65;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 10px;
}
.kpi-value {
    font-size: 34px;
    font-weight: 700;
    color: #1A1A1A;
    line-height: 1;
    font-family: 'Playfair Display', serif;
}
.kpi-sub {
    font-size: 11px;
    color: #8A7D65;
    margin-top: 8px;
}

/* Títulos com fonte serifada — igual ao portfólio */
.page-title {
    font-size: 28px;
    font-weight: 700;
    color: #1A1A1A;
    margin-bottom: 2px;
    font-family: 'Playfair Display', serif;
}
.page-subtitle {
    font-size: 12px;
    color: #8A7D65;
    margin-bottom: 24px;
    letter-spacing: 0.3px;
}
.section-divider {
    border: none;
    border-top: 1px solid #DDD4BC;
    margin: 24px 0;
}

/* Selectbox do filtro na sidebar */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: rgba(214,204,186,0.08) !important;
    border-color: rgba(214,204,186,0.2) !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] svg { fill: #A8C4AF !important; }

#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


def kpi(label, value, sub=""):
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {sub_html}
    </div>""", unsafe_allow_html=True)


def estilo_chart(fig, title="", show_legend=False):
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#1A1A1A", family="Playfair Display, serif"), x=0, xanchor="left"),
        plot_bgcolor="#FBF8F1",
        paper_bgcolor="#FBF8F1",
        font=dict(family="Inter, sans-serif", color="#8A7D65", size=12),
        margin=dict(t=48, b=16, l=10, r=10),
        showlegend=show_legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=12, color="#8A7D65")),
        xaxis=dict(showgrid=False, linecolor="#DDD4BC", tickcolor="#DDD4BC", tickfont=dict(color="#8A7D65")),
        yaxis=dict(gridcolor="#EDE5D0", linecolor="rgba(0,0,0,0)", tickfont=dict(color="#8A7D65")),
    )
    return fig


ibm, movimentacao = carregar_dados()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:28px 16px 20px 16px; border-bottom:1px solid rgba(214,204,186,0.15); margin-bottom:12px;">
        <div style="font-size:10px;font-weight:600;color:#6B9B7A;letter-spacing:2px;text-transform:uppercase;">Recursos Humanos</div>
        <div style="font-size:20px;font-weight:700;color:#EDE5D0;margin-top:4px;font-family:'Playfair Display',serif">Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    aba = st.radio(
        "nav",
        ["Visão Geral", "Turnover", "Admissões e Desligamentos", "Absenteísmo", "Diversidade", "Horas Extras"],
        label_visibility="collapsed"
    )

    st.markdown("""
    <div style="margin-top:24px;padding:0 16px 8px 16px;border-top:1px solid rgba(214,204,186,0.15);padding-top:20px;">
        <div style="font-size:10px;font-weight:600;color:#6B9B7A;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;">Departamento</div>
    </div>
    """, unsafe_allow_html=True)

    DEPTOS = {
        "Todos": None,
        "Recursos Humanos": "Human Resources",
        "Pesquisa e Desenvolvimento": "Research & Development",
        "Vendas": "Sales",
    }
    depto_sel = st.selectbox("depto", list(DEPTOS.keys()), label_visibility="collapsed")

    st.markdown("""
    <div style="margin-top:32px;padding:0 16px;">
        <div style="font-size:11px;color:#6B7D6E;line-height:1.8">
            Desenvolvido por<br>
            <a href="https://linkedin.com/in/eduardodiasds" style="color:#A8C4AF;text-decoration:none;font-weight:500">Eduardo Dias</a>
            &nbsp;·&nbsp;
            <a href="https://github.com/eduudiass" style="color:#A8C4AF;text-decoration:none;font-weight:500">GitHub</a>
        </div>
    </div>
    """, unsafe_allow_html=True)


# aplica filtro de departamento
if DEPTOS[depto_sel]:
    ibm = ibm[ibm["Department"] == DEPTOS[depto_sel]]

# verde floresta — mesma identidade do portfólio
COR_BASE   = "#2D5A3D"
COR_DEST   = "#1A3D2B"
COR_LINHA1 = "#2D5A3D"
COR_LINHA2 = "#7AAD8A"


# ── Visão Geral ──────────────────────────────────────────────────────────────
if aba == "Visão Geral":
    taxa, saidas, total, turnover_depto = calcular_turnover(ibm)
    media_abs, abs_depto = calcular_absenteismo(ibm)

    st.markdown('<div class="page-title">Visão Geral</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Resumo executivo dos principais indicadores de RH</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi("Total de Funcionários", f"{total:,}")
    with col2:
        kpi("Desligamentos", saidas)
    with col3:
        alerta = "acima do limite recomendado" if taxa > 10 else "dentro do esperado"
        kpi("Turnover Geral", f"{taxa}%", alerta)
    with col4:
        kpi("Absenteísmo Médio", f"{media_abs}%", "dias ausentes / dias úteis")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        cores = [COR_DEST if v == turnover_depto["turnover_pct"].max() else COR_BASE
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
            name="Admissões", line=dict(color=COR_LINHA1, width=2),
            fill="tozeroy", fillcolor="rgba(51,65,85,0.05)"
        ))
        fig.add_trace(go.Scatter(
            x=movimentacao["data"], y=movimentacao["desligamentos"],
            name="Desligamentos", line=dict(color=COR_LINHA2, width=2, dash="dot"),
            fill="tozeroy", fillcolor="rgba(148,163,184,0.04)"
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
        alerta = "acima de 10% é crítico" if taxa > 10 else "dentro do esperado"
        kpi("Turnover Geral", f"{taxa}%", alerta)
    with col2:
        kpi("Total de Saídas", saidas)
    with col3:
        kpi("Força de Trabalho", f"{total:,}")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    max_val = turnover_depto["turnover_pct"].max()
    cores = [COR_DEST if v == max_val else COR_BASE for v in turnover_depto["turnover_pct"]]

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
        kpi("Total de Admissões", f"{total_adm:,}")
    with col2:
        kpi("Total de Desligamentos", f"{total_des:,}")
    with col3:
        kpi("Saldo de Pessoal", f"+{saldo}" if saldo >= 0 else str(saldo))

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=movimentacao["data"], y=movimentacao["admissoes"],
        name="Admissões", line=dict(color=COR_LINHA1, width=2),
        fill="tozeroy", fillcolor="rgba(51,65,85,0.05)"
    ))
    fig.add_trace(go.Scatter(
        x=movimentacao["data"], y=movimentacao["desligamentos"],
        name="Desligamentos", line=dict(color=COR_LINHA2, width=2, dash="dot"),
        fill="tozeroy", fillcolor="rgba(148,163,184,0.04)"
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
        kpi("Taxa Média Geral", f"{media_abs}%", "ausências / dias úteis")
    with col2:
        depto_critico = abs_depto.loc[abs_depto["taxa_media"].idxmax(), "departamento"]
        kpi("Maior Absenteísmo", depto_critico, "departamento de atenção")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    max_abs = abs_depto["taxa_media"].max()
    cores = [COR_DEST if v == max_abs else COR_BASE for v in abs_depto["taxa_media"]]

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
            marker=dict(colors=[COR_DEST, COR_BASE]),
            hole=0.5,
            textinfo="label+percent",
            textfont_size=13,
            hovertemplate="%{label}: %{value}%<extra></extra>"
        ))
        fig_genero.update_layout(
            title=dict(text="Distribuição de Gênero", font=dict(size=14, color="#1A1A1A", family="Playfair Display, serif"), x=0),
            plot_bgcolor="#FBF8F1",
            paper_bgcolor="#FBF8F1",
            font=dict(family="Inter, sans-serif", color="#8A7D65"),
            showlegend=False,
            margin=dict(t=48, b=16, l=20, r=20),
        )
        st.plotly_chart(fig_genero, use_container_width=True)

    with col2:
        faixa_df = faixa.reset_index()
        faixa_df.columns = ["faixa_etaria", "quantidade"]

        fig_faixa = go.Figure(go.Bar(
            x=faixa_df["faixa_etaria"].astype(str),
            y=faixa_df["quantidade"],
            marker_color=COR_BASE,
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
        color_discrete_map={"Masculino": COR_DEST, "Feminino": "#7AAD8A"},
        text=genero_nivel["pct"].apply(lambda v: f"{v}%"),
        category_orders={"nivel_label": ["Júnior", "Pleno", "Sênior", "Especialista", "Gestão"]}
    )
    estilo_chart(fig_nivel, "Representatividade de Gênero por Nível Hierárquico (%)", show_legend=True)
    fig_nivel.update_layout(xaxis_title="Nível", yaxis_title="Percentual (%)", legend_title="Gênero")
    fig_nivel.update_traces(textposition="outside")
    st.plotly_chart(fig_nivel, use_container_width=True)


# ── Horas Extras ──────────────────────────────────────────────────────────────
elif aba == "Horas Extras":
    taxa_ot, taxa_com, taxa_sem, multiplicador, pct_ot_saidas, em_risco, ot_depto, horas_depto = calcular_horas_extras(ibm)

    st.markdown('<div class="page-title">Horas Extras</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Relação entre hora extra e saída de funcionários</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi("Turnover com hora extra", f"{taxa_com}%", "dos que fazem hora extra saíram")
    with col2:
        kpi("Turnover sem hora extra", f"{taxa_sem}%", "dos que não fazem hora extra saíram")
    with col3:
        kpi("Risco relativo", f"{multiplicador}×", "mais chance de sair fazendo hora extra")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        max_horas = horas_depto["media_horas"].max()
        fig = go.Figure(go.Bar(
            y=horas_depto["departamento"],
            x=horas_depto["media_horas"],
            orientation="h",
            marker_color=[COR_DEST if v == max_horas else COR_BASE for v in horas_depto["media_horas"]],
            text=[f"{v}h" for v in horas_depto["media_horas"]],
            textposition="outside",
        ))
        estilo_chart(fig, "Média de Horas Extras por Departamento")
        fig.update_layout(
            xaxis=dict(showgrid=True, gridcolor="#EDE5D0", range=[0, max_horas * 1.35]),
            yaxis=dict(showgrid=False),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        max_pct = ot_depto["pct_ot"].max()
        fig2 = go.Figure(go.Bar(
            y=ot_depto["cargo"],
            x=ot_depto["pct_ot"],
            orientation="h",
            marker_color=[COR_DEST if v == max_pct else COR_BASE for v in ot_depto["pct_ot"]],
            text=[f"{v}%" for v in ot_depto["pct_ot"]],
            textposition="outside",
        ))
        estilo_chart(fig2, "% de Saídas que Faziam Hora Extra — por Cargo")
        fig2.update_layout(
            xaxis=dict(showgrid=True, gridcolor="#EDE5D0", range=[0, max_pct * 1.35]),
            yaxis=dict(showgrid=False),
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    pct_ot_ficaram = round(100 - pct_ot_saidas, 1)
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        name="Saíram", x=["Faziam hora extra", "Não faziam hora extra"],
        y=[pct_ot_saidas, 100 - pct_ot_saidas],
        marker_color=COR_DEST, text=[f"{pct_ot_saidas}%", f"{100 - pct_ot_saidas}%"],
        textposition="outside", width=0.35
    ))
    estilo_chart(fig3, f"Composição das Saídas — {pct_ot_saidas}% dos que saíram faziam hora extra")
    fig3.update_layout(yaxis_range=[0, 120], showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)
