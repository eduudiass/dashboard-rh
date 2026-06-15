import pandas as pd

# mapeamento de departamentos para português
DEPARTAMENTOS = {
    "Human Resources": "Recursos Humanos",
    "Research & Development": "Pesquisa e Desenvolvimento",
    "Sales": "Vendas"
}

# mapeamento de gênero para português
GENERO = {
    "Male": "Masculino",
    "Female": "Feminino"
}

def carregar_dados():
    # carrega o dataset principal do IBM
    ibm = pd.read_csv("data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv")
    
    # carrega os dados sintéticos gerados
    movimentacao = pd.read_csv("data/processed/movimentacao_mensal.csv")
    absenteismo = pd.read_csv("data/processed/absenteismo.csv")
    
    # une o absenteismo com o dataset IBM pelo número do funcionário
    ibm = ibm.merge(absenteismo, on="EmployeeNumber", how="left")
    
    return ibm, movimentacao


def calcular_turnover(df):
    # total de funcionários
    total = len(df)
    
    # funcionários que saíram
    saidas = df[df["Attrition"] == "Yes"].shape[0]
    
    # taxa de turnover geral em percentual
    taxa = round(saidas / total * 100, 2)
    
    # turnover por departamento
    por_depto = (
        df.groupby("Department")["Attrition"]
        .apply(lambda x: (x == "Yes").sum() / len(x) * 100)
        .round(2)
        .reset_index()
    )
    por_depto.columns = ["departamento", "turnover_pct"]
    
    # traduz os nomes dos departamentos
    por_depto["departamento"] = por_depto["departamento"].map(DEPARTAMENTOS)
    
    return taxa, saidas, total, por_depto


def calcular_diversidade(df):
    # distribuição de gênero geral
    genero = df["Gender"].value_counts(normalize=True).mul(100).round(2)
    
    # traduz os valores de gênero
    genero.index = genero.index.map(GENERO)
    
    # distribuição de gênero por nível hierárquico
    genero_por_nivel = (
        df.groupby("JobLevel")["Gender"]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
        .reset_index()
    )
    genero_por_nivel.columns = ["nivel", "genero", "pct"]
    genero_por_nivel["genero"] = genero_por_nivel["genero"].map(GENERO)

    # faixa etária
    bins = [18, 25, 35, 45, 55, 65]
    labels = ["18-25", "26-35", "36-45", "46-55", "56-65"]
    df["faixa_etaria"] = pd.cut(df["Age"], bins=bins, labels=labels, right=True)
    faixa = df["faixa_etaria"].value_counts().sort_index()
    
    return genero, genero_por_nivel, faixa


def calcular_absenteismo(df):
    # taxa média geral
    media = df["taxa_absenteismo"].mean().round(2)
    
    # taxa por departamento
    por_depto = (
        df.groupby("Department")["taxa_absenteismo"]
        .mean()
        .round(2)
        .reset_index()
    )
    por_depto.columns = ["departamento", "taxa_media"]
    
    # traduz os nomes dos departamentos
    por_depto["departamento"] = por_depto["departamento"].map(DEPARTAMENTOS)
    
    return media, por_depto


def calcular_horas_extras(df):
    OT_MAP = {"Yes": "Com hora extra", "No": "Sem hora extra"}

    # taxa de turnover por grupo de hora extra
    taxa_ot = (
        df.groupby("OverTime")["Attrition"]
        .apply(lambda x: round((x == "Yes").sum() / len(x) * 100, 1))
        .reset_index()
    )
    taxa_ot.columns = ["overtime", "turnover_pct"]
    taxa_ot["overtime"] = taxa_ot["overtime"].map(OT_MAP)

    taxa_com = taxa_ot.loc[taxa_ot["overtime"] == "Com hora extra", "turnover_pct"].values[0]
    taxa_sem = taxa_ot.loc[taxa_ot["overtime"] == "Sem hora extra", "turnover_pct"].values[0]
    multiplicador = round(taxa_com / taxa_sem, 1) if taxa_sem > 0 else 0

    # entre os que saíram, quantos faziam hora extra
    saidas = df[df["Attrition"] == "Yes"]
    pct_ot_saidas = round((saidas["OverTime"] == "Yes").mean() * 100, 1)

    # funcionários ativos que ainda fazem hora extra
    em_risco = int(((df["OverTime"] == "Yes") & (df["Attrition"] == "No")).sum())

    # hora extra por departamento entre os que saíram
    ot_depto = (
        df[df["Attrition"] == "Yes"]
        .groupby("Department")["OverTime"]
        .apply(lambda x: round((x == "Yes").mean() * 100, 1))
        .reset_index()
    )
    ot_depto.columns = ["departamento", "pct_ot"]
    ot_depto["departamento"] = ot_depto["departamento"].map(DEPARTAMENTOS)

    return taxa_ot, taxa_com, taxa_sem, multiplicador, pct_ot_saidas, em_risco, ot_depto


if __name__ == "__main__":
    ibm, movimentacao = carregar_dados()
    
    taxa, saidas, total, turnover_depto = calcular_turnover(ibm)
    print(f"Turnover geral: {taxa}%")
    print(f"Total de funcionários: {total} | Saídas: {saidas}")
    print(turnover_depto)
    
    genero, genero_nivel, faixa = calcular_diversidade(ibm)
    print(genero)
    print(faixa)
    
    media_abs, abs_depto = calcular_absenteismo(ibm)
    print(f"Absenteísmo médio: {media_abs}%")
    print(abs_depto)