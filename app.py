import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from metrics import carregar_dados, calcular_turnover, calcular_diversidade, calcular_absenteismo

st.set_page_config(
    page_title="Dashboard RH",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
    background-color: #F9FAFB !important;
}
.block-container { padding-top: 2.5rem !important; padding-bottom: 2rem !important; }

/* Sidebar clara */
[data-testid="stSidebar"] {
    background: #F1F5F9 !important;
    border-right: 1px solid #E2E8F0 !important;
}
[data-testid="stSidebar"] * { color: #0F172A !important; }

/* Remove círculo do radio e estiliza como menu */
[data-testid="stSidebar"] [data-baseweb="radio"] > div:first-child { display: none !important; }
[data-testid="stSidebar"] [role="radiogroup"] { gap: 2px; }
[data-testid="stSidebar"] label[data-baseweb="radio"] {
    padding: 9px 14px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
    transition: background 0.1s;
    cursor: pointer;
}
[data-testid="stSidebar"] label[data-baseweb="radio"]:hover {
    background: #E2E8F0 !important;
}

/* KPI Cards — sem borda colorida, só sombra limpa */
.kpi-card {
    background: #FFFFFF;
    border-radius: 8px;
    padding: 22px 24px 18px 24px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    height: 100%;
}
.kpi-label {
    font-size: 11px;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 10px;
}
.kpi-value {
    font-size: 34px;
    font-weight: 700;
    color: #0F172A;
    line-height: 1;
    font-variant-numeric: tabular-nums;
}
.kpi-sub {
    font-size: 11px;
    color: #94A3B8;
    margin-top: 8px;
}

.page-title {
    font-size: 20px;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 2px;
}
.page-subtitle {
    font-size: 12px;
    color: #94A3B8;
    margin-bottom: 24px;
    letter-spacing: 0.2px;
}
.section-divider {
    border: none;
    border-top: 1px solid #F1F5F9;
    margin: 24px 0;
}

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
        title=dict(text=title, font=dict(size=14, color="#0F172A", family="Inter, sans-serif"), x=0, xanchor="left"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(family="Inter, sans-serif", color="#64748B", size=12),
        margin=dict(t=48, b=16, l=10, r=10),
        showlegend=show_legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=12, color="#64748B")),
        xaxis=dict(showgrid=False, linecolor="#F1F5F9", tickcolor="#F1F5F9", tickfont=dict(color="#94A3B8")),
        yaxis=dict(gridcolor="#F8FAFC", linecolor="white", tickfont=dict(color="#94A3B8")),
    )
    return fig


ibm, movimentacao = carregar_dados()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:28px 16px 20px 16px; border-bottom:1px solid #E2E8F0; margin-bottom:12px;">
        <div style="font-size:11px;font-weight:700;color:#94A3B8;letter-spacing:2px;text-transform:uppercase;">Recursos Humanos</div>
        <div style="font-size:19px;font-weight:700;color:#0F172A;margin-top:4px;">Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    aba = st.radio(
        "nav",
        ["Visão Geral", "Turnover", "Admissões e Desligamentos", "Absenteísmo", "Diversidade"],
        label_visibility="collapsed"
    )

    st.markdown("""
    <div style="margin-top:40px;padding:0 16px;">
        <div style="font-size:11px;color:#94A3B8;line-height:1.8">
            Desenvolvido por<br>
            <a href="https://linkedin.com/in/eduardodiasds" style="color:#475569;text-decoration:none;font-weight:500">Eduardo Dias</a>
            &nbsp;·&nbsp;
            <a href="https://github.com/eduudiass" style="color:#475569;text-decoration:none;font-weight:500">GitHub</a>
        </div>
    </div>
    """, unsafe_allow_html=True)


# cores base: slate escuro para todos, slate-900 para o destaque
COR_BASE   = "#475569"
COR_DEST   = "#0F172A"
COR_LINHA1 = "#334155"
COR_LINHA2 = "#94A3B8"


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
            title=dict(text="Distribuição de Gênero", font=dict(size=14, color="#0F172A", family="Inter, sans-serif"), x=0),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Inter, sans-serif", color="#64748B"),
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
        color_discrete_map={"Masculino": COR_DEST, "Feminino": COR_BASE},
        text=genero_nivel["pct"].apply(lambda v: f"{v}%"),
        category_orders={"nivel_label": ["Júnior", "Pleno", "Sênior", "Especialista", "Gestão"]}
    )
    estilo_chart(fig_nivel, "Representatividade de Gênero por Nível Hierárquico (%)", show_legend=True)
    fig_nivel.update_layout(xaxis_title="Nível", yaxis_title="Percentual (%)", legend_title="Gênero")
    fig_nivel.update_traces(textposition="outside")
    st.plotly_chart(fig_nivel, use_container_width=True)
