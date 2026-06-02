import pandas as pd
import numpy as np

# garante que os números aleatórios sejam sempre os mesmos em toda execução
np.random.seed(42)

def gerar_movimentacao_mensal(n_meses=24):
    # cria uma sequência de datas mensais começando em janeiro de 2024
    datas = pd.date_range(start="2024-01-01", periods=n_meses, freq="MS")
    
    # gera valores aleatórios de admissões e desligamentos por mês
    admissoes = np.random.randint(8, 25, size=n_meses)
    desligamentos = np.random.randint(4, 18, size=n_meses)

    # monta a tabela com as colunas geradas
    df = pd.DataFrame({
        "data": datas,
        "admissoes": admissoes,
        "desligamentos": desligamentos
    })

    # calcula a taxa de turnover do mês em percentual
    df["turnover_mensal"] = (df["desligamentos"] / (admissoes + desligamentos) * 100).round(2)
    return df


def gerar_absenteismo(n_funcionarios=1470):
    # cria uma linha por funcionário com dias ausentes aleatórios
    df = pd.DataFrame({
        "EmployeeNumber": range(1, n_funcionarios + 1),
        "dias_ausentes": np.random.randint(0, 20, size=n_funcionarios),
        "dias_uteis": 220  # total de dias úteis no ano
    })

    # calcula a taxa de absenteísmo em percentual
    df["taxa_absenteismo"] = (df["dias_ausentes"] / df["dias_uteis"] * 100).round(2)
    return df


# esse bloco só executa quando o arquivo é rodado diretamente
if __name__ == "__main__":
    mov = gerar_movimentacao_mensal()
    abs_ = gerar_absenteismo()

    # salva os dados gerados em arquivos CSV
    mov.to_csv("data/processed/movimentacao_mensal.csv", index=False)
    abs_.to_csv("data/processed/absenteismo.csv", index=False)

    print("Dados gerados com sucesso.")
    print(mov.head())
    print(abs_.head())