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


# renderiza um card de indicador com label, valor principal e subtítulo opcional
def kpi(label, value, sub=""):
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {sub_html}
    </div>""", unsafe_allow_html=True)


# aplica a identidade visual padrão em qualquer figura Plotly
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


# verde floresta — mesma identidade do portfólio
COR_BASE   = "#2D5A3D"
COR_DEST   = "#1A3D2B"
COR_LINHA1 = "#2D5A3D"
COR_LINHA2 = "#7AAD8A"

# mapeamento PT→EN para labels retornados pelo metrics.py
PT_EN_DEPTOS = {
    "Recursos Humanos": "Human Resources",
    "Pesquisa e Desenvolvimento": "Research & Development",
    "Vendas": "Sales",
}
PT_EN_CARGOS = {
    "Rep. de Saúde": "Health Rep.",
    "Recursos Humanos": "Human Resources",
    "Téc. Laboratório": "Lab Technician",
    "Gerente": "Manager",
    "Dir. Manufatura": "Manufacturing Dir.",
    "Dir. Pesquisa": "Research Dir.",
    "Cientista": "Scientist",
    "Exec. Vendas": "Sales Executive",
    "Rep. Vendas": "Sales Rep.",
}
PT_EN_GENERO = {"Masculino": "Male", "Feminino": "Female"}

# textos da interface em português e inglês
TEXT = {
    "PT": {
        "nav": ["Visão Geral", "Turnover", "Admissões e Desligamentos", "Absenteísmo", "Diversidade", "Horas Extras"],
        "dept_label": "Departamento",
        "deptos": {"Todos": None, "Recursos Humanos": "Human Resources", "Pesquisa e Desenvolvimento": "Research & Development", "Vendas": "Sales"},
        "developed_by": "Desenvolvido por",
        # Visão Geral
        "overview_title": "Visão Geral",
        "overview_sub": "Resumo executivo dos principais indicadores de RH",
        "kpi_total_emp": "Total de Funcionários",
        "kpi_departures": "Desligamentos",
        "kpi_turnover": "Turnover Geral",
        "turnover_above": "acima do limite recomendado",
        "turnover_ok": "dentro do esperado",
        "kpi_absenteeism": "Absenteísmo Médio",
        "absenteeism_sub": "dias ausentes / dias úteis",
        "chart_turnover_dept": "Turnover por Departamento (%)",
        "chart_monthly": "Movimentação Mensal",
        "legend_hires": "Admissões",
        "legend_dep": "Desligamentos",
        # Turnover
        "turnover_title": "Análise de Turnover",
        "turnover_page_sub": "Taxa de rotatividade por departamento",
        "turnover_critical": "acima de 10% é crítico",
        "kpi_total_exits": "Total de Saídas",
        "kpi_workforce": "Força de Trabalho",
        "chart_turnover_dept_full": "Taxa de Turnover por Departamento (%)",
        # Admissões e Desligamentos
        "hires_title": "Admissões e Desligamentos",
        "hires_sub": "Movimentação de pessoal nos últimos 24 meses",
        "kpi_total_hires": "Total de Admissões",
        "kpi_total_departures": "Total de Desligamentos",
        "kpi_net": "Saldo de Pessoal",
        "chart_monthly_full": "Movimentação Mensal de Pessoal",
        # Absenteísmo
        "abs_title": "Absenteísmo",
        "abs_sub": "Taxas de ausência por departamento",
        "kpi_avg_rate": "Taxa Média Geral",
        "avg_rate_sub": "ausências / dias úteis",
        "kpi_highest_abs": "Maior Absenteísmo",
        "highest_abs_sub": "departamento de atenção",
        "chart_abs_dept": "Taxa Média de Absenteísmo por Departamento (%)",
        # Diversidade
        "div_title": "Diversidade",
        "div_sub": "Composição de gênero e faixa etária do quadro",
        "chart_gender": "Distribuição de Gênero",
        "chart_age": "Distribuição por Faixa Etária",
        "xaxis_age": "Faixa Etária",
        "yaxis_emp": "Funcionários",
        "chart_gender_level": "Representatividade de Gênero por Nível Hierárquico (%)",
        "xaxis_level": "Nível",
        "yaxis_pct": "Percentual (%)",
        "legend_gender": "Gênero",
        "nivel_map": {1: "Júnior", 2: "Pleno", 3: "Sênior", 4: "Especialista", 5: "Gestão"},
        "cat_levels": ["Júnior", "Pleno", "Sênior", "Especialista", "Gestão"],
        "gender_col_map": {"Masculino": COR_DEST, "Feminino": "#7AAD8A"},
        # Horas Extras
        "ot_title": "Horas Extras",
        "ot_sub": "Relação entre hora extra e saída de funcionários",
        "kpi_ot_with": "Turnover com hora extra",
        "ot_with_sub": "dos que fazem hora extra saíram",
        "kpi_ot_without": "Turnover sem hora extra",
        "ot_without_sub": "dos que não fazem hora extra saíram",
        "kpi_risk": "Risco relativo",
        "risk_sub": "mais chance de sair fazendo hora extra",
        "chart_ot_dept": "Média de Horas Extras por Departamento",
        "chart_ot_role": "% de Saídas que Faziam Hora Extra — por Cargo",
        "chart_composition": "Composição das Saídas — {}% dos que saíram faziam hora extra",
        "bar_ot_yes": "Faziam hora extra",
        "bar_ot_no": "Não faziam hora extra",
    },
    "EN": {
        "nav": ["Overview", "Turnover", "Hires & Departures", "Absenteeism", "Diversity", "Overtime"],
        "dept_label": "Department",
        "deptos": {"All": None, "Human Resources": "Human Resources", "Research & Development": "Research & Development", "Sales": "Sales"},
        "developed_by": "Developed by",
        # Overview
        "overview_title": "Overview",
        "overview_sub": "Executive summary of key HR indicators",
        "kpi_total_emp": "Total Employees",
        "kpi_departures": "Departures",
        "kpi_turnover": "Overall Turnover",
        "turnover_above": "above recommended limit",
        "turnover_ok": "within expected range",
        "kpi_absenteeism": "Average Absenteeism",
        "absenteeism_sub": "absent days / working days",
        "chart_turnover_dept": "Turnover by Department (%)",
        "chart_monthly": "Monthly Movement",
        "legend_hires": "Hires",
        "legend_dep": "Departures",
        # Turnover
        "turnover_title": "Turnover Analysis",
        "turnover_page_sub": "Turnover rate by department",
        "turnover_critical": "above 10% is critical",
        "kpi_total_exits": "Total Departures",
        "kpi_workforce": "Workforce",
        "chart_turnover_dept_full": "Turnover Rate by Department (%)",
        # Hires & Departures
        "hires_title": "Hires & Departures",
        "hires_sub": "Personnel movement over the last 24 months",
        "kpi_total_hires": "Total Hires",
        "kpi_total_departures": "Total Departures",
        "kpi_net": "Net Headcount",
        "chart_monthly_full": "Monthly Personnel Movement",
        # Absenteeism
        "abs_title": "Absenteeism",
        "abs_sub": "Absence rates by department",
        "kpi_avg_rate": "Overall Average Rate",
        "avg_rate_sub": "absences / working days",
        "kpi_highest_abs": "Highest Absenteeism",
        "highest_abs_sub": "department to watch",
        "chart_abs_dept": "Average Absenteeism Rate by Department (%)",
        # Diversity
        "div_title": "Diversity",
        "div_sub": "Gender and age composition of workforce",
        "chart_gender": "Gender Distribution",
        "chart_age": "Distribution by Age Group",
        "xaxis_age": "Age Group",
        "yaxis_emp": "Employees",
        "chart_gender_level": "Gender Representation by Hierarchical Level (%)",
        "xaxis_level": "Level",
        "yaxis_pct": "Percentage (%)",
        "legend_gender": "Gender",
        "nivel_map": {1: "Junior", 2: "Mid-level", 3: "Senior", 4: "Specialist", 5: "Management"},
        "cat_levels": ["Junior", "Mid-level", "Senior", "Specialist", "Management"],
        "gender_col_map": {"Male": COR_DEST, "Female": "#7AAD8A"},
        # Overtime
        "ot_title": "Overtime",
        "ot_sub": "Relationship between overtime and employee departure",
        "kpi_ot_with": "Turnover with overtime",
        "ot_with_sub": "of overtime workers left",
        "kpi_ot_without": "Turnover without overtime",
        "ot_without_sub": "of non-overtime workers left",
        "kpi_risk": "Relative risk",
        "risk_sub": "more likely to leave when working overtime",
        "chart_ot_dept": "Average Overtime Hours by Department",
        "chart_ot_role": "% of Departures Who Worked Overtime — by Role",
        "chart_composition": "Departure Composition — {}% of leavers worked overtime",
        "bar_ot_yes": "Worked overtime",
        "bar_ot_no": "Did not work overtime",
    }
}

# chaves fixas de navegação, independentes do idioma
NAV_KEYS = ["overview", "turnover", "hires", "absenteeism", "diversity", "overtime"]

# carrega os dados uma vez ao iniciar o app
ibm, movimentacao = carregar_dados()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    # seletor de idioma no topo da sidebar
    lang = st.radio("lang", ["PT", "EN"], horizontal=True, label_visibility="collapsed")
    T = TEXT[lang]

    st.markdown("""
    <div style="padding:20px 16px 20px 16px; border-bottom:1px solid rgba(214,204,186,0.15); margin-bottom:12px;">
        <div style="font-size:10px;font-weight:600;color:#6B9B7A;letter-spacing:2px;text-transform:uppercase;">Recursos Humanos</div>
        <div style="font-size:20px;font-weight:700;color:#EDE5D0;margin-top:4px;font-family:'Playfair Display',serif">Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    aba = st.radio("nav", T["nav"], label_visibility="collapsed")

    # índice da aba selecionada para comparação independente de idioma
    page = NAV_KEYS[T["nav"].index(aba)]

    st.markdown(f"""
    <div style="margin-top:24px;padding:0 16px 8px 16px;border-top:1px solid rgba(214,204,186,0.15);padding-top:20px;">
        <div style="font-size:10px;font-weight:600;color:#6B9B7A;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;">{T["dept_label"]}</div>
    </div>
    """, unsafe_allow_html=True)

    DEPTOS = T["deptos"]
    depto_sel = st.selectbox("depto", list(DEPTOS.keys()), label_visibility="collapsed")

    st.markdown(f"""
    <div style="margin-top:32px;padding:0 16px;">
        <div style="font-size:11px;color:#6B7D6E;line-height:1.8">
            {T["developed_by"]}<br>
            <a href="https://linkedin.com/in/eduardodiasds" style="color:#A8C4AF;text-decoration:none;font-weight:500">Eduardo Dias</a>
            &nbsp;·&nbsp;
            <a href="https://github.com/eduudiass" style="color:#A8C4AF;text-decoration:none;font-weight:500">GitHub</a>
        </div>
    </div>
    """, unsafe_allow_html=True)


# aplica filtro de departamento
if DEPTOS[depto_sel]:
    ibm = ibm[ibm["Department"] == DEPTOS[depto_sel]]


# ── Visão Geral / Overview ────────────────────────────────────────────────────
if page == "overview":
    taxa, saidas, total, turnover_depto = calcular_turnover(ibm)
    media_abs, abs_depto = calcular_absenteismo(ibm)

    if lang == "EN":
        turnover_depto["departamento"] = turnover_depto["departamento"].map(PT_EN_DEPTOS)

    st.markdown(f'<div class="page-title">{T["overview_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{T["overview_sub"]}</div>', unsafe_allow_html=True)

    # KPI cards do topo
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi(T["kpi_total_emp"], f"{total:,}")
    with col2:
        kpi(T["kpi_departures"], saidas)
    with col3:
        alerta = T["turnover_above"] if taxa > 10 else T["turnover_ok"]
        kpi(T["kpi_turnover"], f"{taxa}%", alerta)
    with col4:
        kpi(T["kpi_absenteeism"], f"{media_abs}%", T["absenteeism_sub"])

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # gráfico de barras de turnover e linha de movimentação mensal
    col_a, col_b = st.columns(2)

    with col_a:
        # destaca o departamento com maior turnover
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
        estilo_chart(fig, T["chart_turnover_dept"])
        fig.update_layout(yaxis_range=[0, turnover_depto["turnover_pct"].max() * 1.35])
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=movimentacao["data"], y=movimentacao["admissoes"],
            name=T["legend_hires"], line=dict(color=COR_LINHA1, width=2),
            fill="tozeroy", fillcolor="rgba(51,65,85,0.05)"
        ))
        fig.add_trace(go.Scatter(
            x=movimentacao["data"], y=movimentacao["desligamentos"],
            name=T["legend_dep"], line=dict(color=COR_LINHA2, width=2, dash="dot"),
            fill="tozeroy", fillcolor="rgba(148,163,184,0.04)"
        ))
        estilo_chart(fig, T["chart_monthly"], show_legend=True)
        st.plotly_chart(fig, use_container_width=True)


# ── Turnover ──────────────────────────────────────────────────────────────────
elif page == "turnover":
    taxa, saidas, total, turnover_depto = calcular_turnover(ibm)

    if lang == "EN":
        turnover_depto["departamento"] = turnover_depto["departamento"].map(PT_EN_DEPTOS)

    st.markdown(f'<div class="page-title">{T["turnover_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{T["turnover_page_sub"]}</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        alerta = T["turnover_critical"] if taxa > 10 else T["turnover_ok"]
        kpi(T["kpi_turnover"], f"{taxa}%", alerta)
    with col2:
        kpi(T["kpi_total_exits"], saidas)
    with col3:
        kpi(T["kpi_workforce"], f"{total:,}")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # destaca o departamento com maior turnover
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
    estilo_chart(fig, T["chart_turnover_dept_full"])
    fig.update_layout(yaxis_range=[0, max_val * 1.35])
    st.plotly_chart(fig, use_container_width=True)


# ── Admissões e Desligamentos / Hires & Departures ───────────────────────────
elif page == "hires":
    # soma os totais do período e calcula o saldo
    total_adm = int(movimentacao["admissoes"].sum())
    total_des = int(movimentacao["desligamentos"].sum())
    saldo = total_adm - total_des

    st.markdown(f'<div class="page-title">{T["hires_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{T["hires_sub"]}</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi(T["kpi_total_hires"], f"{total_adm:,}")
    with col2:
        kpi(T["kpi_total_departures"], f"{total_des:,}")
    with col3:
        kpi(T["kpi_net"], f"+{saldo}" if saldo >= 0 else str(saldo))

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=movimentacao["data"], y=movimentacao["admissoes"],
        name=T["legend_hires"], line=dict(color=COR_LINHA1, width=2),
        fill="tozeroy", fillcolor="rgba(51,65,85,0.05)"
    ))
    fig.add_trace(go.Scatter(
        x=movimentacao["data"], y=movimentacao["desligamentos"],
        name=T["legend_dep"], line=dict(color=COR_LINHA2, width=2, dash="dot"),
        fill="tozeroy", fillcolor="rgba(148,163,184,0.04)"
    ))
    estilo_chart(fig, T["chart_monthly_full"], show_legend=True)
    st.plotly_chart(fig, use_container_width=True)


# ── Absenteísmo / Absenteeism ─────────────────────────────────────────────────
elif page == "absenteeism":
    media_abs, abs_depto = calcular_absenteismo(ibm)

    if lang == "EN":
        abs_depto["departamento"] = abs_depto["departamento"].map(PT_EN_DEPTOS)

    st.markdown(f'<div class="page-title">{T["abs_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{T["abs_sub"]}</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        kpi(T["kpi_avg_rate"], f"{media_abs}%", T["avg_rate_sub"])
    with col2:
        # encontra o departamento com pior índice de absenteísmo
        depto_critico = abs_depto.loc[abs_depto["taxa_media"].idxmax(), "departamento"]
        kpi(T["kpi_highest_abs"], depto_critico, T["highest_abs_sub"])

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
    estilo_chart(fig, T["chart_abs_dept"])
    fig.update_layout(yaxis_range=[0, max_abs * 1.35])
    st.plotly_chart(fig, use_container_width=True)


# ── Diversidade / Diversity ───────────────────────────────────────────────────
elif page == "diversity":
    genero, genero_nivel, faixa = calcular_diversidade(ibm)

    if lang == "EN":
        genero.index = genero.index.map(PT_EN_GENERO)
        genero_nivel["genero"] = genero_nivel["genero"].map(PT_EN_GENERO)

    st.markdown(f'<div class="page-title">{T["div_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{T["div_sub"]}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # gráfico de rosca para distribuição de gênero
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
            title=dict(text=T["chart_gender"], font=dict(size=14, color="#1A1A1A", family="Playfair Display, serif"), x=0),
            plot_bgcolor="#FBF8F1",
            paper_bgcolor="#FBF8F1",
            font=dict(family="Inter, sans-serif", color="#8A7D65"),
            showlegend=False,
            margin=dict(t=48, b=16, l=20, r=20),
        )
        st.plotly_chart(fig_genero, use_container_width=True)

    with col2:
        # bar chart de quantidade por faixa etária
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
        estilo_chart(fig_faixa, T["chart_age"])
        fig_faixa.update_layout(
            yaxis_range=[0, faixa_df["quantidade"].max() * 1.2],
            xaxis_title=T["xaxis_age"],
            yaxis_title=T["yaxis_emp"]
        )
        st.plotly_chart(fig_faixa, use_container_width=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # traduz os níveis numéricos para labels legíveis
    nivel_map = T["nivel_map"]
    genero_nivel["nivel_label"] = genero_nivel["nivel"].map(nivel_map)

    fig_nivel = px.bar(
        genero_nivel,
        x="nivel_label",
        y="pct",
        color="genero",
        barmode="group",
        color_discrete_map=T["gender_col_map"],
        text=genero_nivel["pct"].apply(lambda v: f"{v}%"),
        category_orders={"nivel_label": T["cat_levels"]}
    )
    estilo_chart(fig_nivel, T["chart_gender_level"], show_legend=True)
    fig_nivel.update_layout(xaxis_title=T["xaxis_level"], yaxis_title=T["yaxis_pct"], legend_title=T["legend_gender"])
    fig_nivel.update_traces(textposition="outside")
    st.plotly_chart(fig_nivel, use_container_width=True)


# ── Horas Extras / Overtime ──────────────────────────────────────────────────
elif page == "overtime":
    taxa_ot, taxa_com, taxa_sem, multiplicador, pct_ot_saidas, em_risco, ot_depto, horas_depto = calcular_horas_extras(ibm)

    if lang == "EN":
        horas_depto["departamento"] = horas_depto["departamento"].map(PT_EN_DEPTOS)
        ot_depto["cargo"] = ot_depto["cargo"].map(PT_EN_CARGOS)

    st.markdown(f'<div class="page-title">{T["ot_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{T["ot_sub"]}</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi(T["kpi_ot_with"], f"{taxa_com}%", T["ot_with_sub"])
    with col2:
        kpi(T["kpi_ot_without"], f"{taxa_sem}%", T["ot_without_sub"])
    with col3:
        kpi(T["kpi_risk"], f"{multiplicador}×", T["risk_sub"])

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # gráficos de horas extras por departamento e por cargo
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
        estilo_chart(fig, T["chart_ot_dept"])
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
        estilo_chart(fig2, T["chart_ot_role"])
        fig2.update_layout(
            xaxis=dict(showgrid=True, gridcolor="#EDE5D0", range=[0, max_pct * 1.35]),
            yaxis=dict(showgrid=False),
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # composição das saídas: quanto dos demitidos faziam hora extra
    pct_ot_ficaram = round(100 - pct_ot_saidas, 1)
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        name=T["bar_ot_yes"], x=[T["bar_ot_yes"], T["bar_ot_no"]],
        y=[pct_ot_saidas, 100 - pct_ot_saidas],
        marker_color=COR_DEST, text=[f"{pct_ot_saidas}%", f"{100 - pct_ot_saidas}%"],
        textposition="outside", width=0.35
    ))
    estilo_chart(fig3, T["chart_composition"].format(pct_ot_saidas))
    fig3.update_layout(yaxis_range=[0, 100], showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)
