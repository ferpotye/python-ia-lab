import pandas as pd
from pathlib import Path
from datetime import datetime

from database import buscar_receitas, buscar_despesas


# ============================================================
# CONFIGURAÇÃO
# ============================================================

PASTA_RELATORIOS = (
    Path(__file__).resolve().parent
    / "relatorios_gerados"
)


# ============================================================
# FORMATAÇÃO
# ============================================================

def preparar_dados():

    receitas = buscar_receitas()
    despesas = buscar_despesas()

    df_receitas = pd.DataFrame(
        receitas,
        columns=[
            "id",
            "descricao",
            "categoria",
            "valor",
            "data",
        ]
    )

    df_despesas = pd.DataFrame(
        despesas,
        columns=[
            "id",
            "descricao",
            "categoria",
            "valor",
            "data",
        ]
    )

    if not df_receitas.empty:
        df_receitas["tipo"] = "Receita"

    if not df_despesas.empty:
        df_despesas["tipo"] = "Despesa"

    return df_receitas, df_despesas


# ============================================================
# RESUMO FINANCEIRO
# ============================================================

def gerar_resumo(df_receitas, df_despesas):

    total_receitas = (
        df_receitas["valor"].sum()
        if not df_receitas.empty
        else 0
    )

    total_despesas = (
        df_despesas["valor"].sum()
        if not df_despesas.empty
        else 0
    )

    saldo = total_receitas - total_despesas

    quantidade_receitas = len(df_receitas)
    quantidade_despesas = len(df_despesas)

    total_lancamentos = (
        quantidade_receitas
        + quantidade_despesas
    )

    return pd.DataFrame(
        [
            {
                "Indicador": "Total de receitas",
                "Valor": total_receitas,
            },
            {
                "Indicador": "Total de despesas",
                "Valor": total_despesas,
            },
            {
                "Indicador": "Saldo",
                "Valor": saldo,
            },
            {
                "Indicador": "Quantidade de receitas",
                "Valor": quantidade_receitas,
            },
            {
                "Indicador": "Quantidade de despesas",
                "Valor": quantidade_despesas,
            },
            {
                "Indicador": "Total de lançamentos",
                "Valor": total_lancamentos,
            },
        ]
    )


# ============================================================
# GASTOS POR CATEGORIA
# ============================================================

def gerar_gastos_por_categoria(df_despesas):

    if df_despesas.empty:

        return pd.DataFrame(
            columns=[
                "categoria",
                "total",
            ]
        )

    resultado = (
        df_despesas
        .groupby("categoria", as_index=False)["valor"]
        .sum()
        .sort_values(
            "valor",
            ascending=False
        )
    )

    resultado.columns = [
        "categoria",
        "total",
    ]

    return resultado


# ============================================================
# EVOLUÇÃO MENSAL
# ============================================================

def gerar_evolucao_mensal(
    df_receitas,
    df_despesas
):

    receitas = df_receitas.copy()
    despesas = df_despesas.copy()

    if not receitas.empty:

        receitas["data"] = pd.to_datetime(
            receitas["data"],
            errors="coerce"
        )

        receitas = receitas.dropna(
            subset=["data"]
        )

        receitas["mes"] = (
            receitas["data"]
            .dt.to_period("M")
            .astype(str)
        )

        receitas_mensais = (
            receitas
            .groupby("mes")["valor"]
            .sum()
            .rename("receitas")
        )

    else:

        receitas_mensais = pd.Series(
            dtype=float,
            name="receitas"
        )

    if not despesas.empty:

        despesas["data"] = pd.to_datetime(
            despesas["data"],
            errors="coerce"
        )

        despesas = despesas.dropna(
            subset=["data"]
        )

        despesas["mes"] = (
            despesas["data"]
            .dt.to_period("M")
            .astype(str)
        )

        despesas_mensais = (
            despesas
            .groupby("mes")["valor"]
            .sum()
            .rename("despesas")
        )

    else:

        despesas_mensais = pd.Series(
            dtype=float,
            name="despesas"
        )

    resultado = pd.concat(
        [
            receitas_mensais,
            despesas_mensais,
        ],
        axis=1
    ).fillna(0)

    resultado["saldo"] = (
        resultado["receitas"]
        - resultado["despesas"]
    )

    resultado = (
        resultado
        .reset_index()
        .rename(columns={"index": "mes"})
        .sort_values("mes")
    )

    return resultado


# ============================================================
# GERAR RELATÓRIO EXCEL
# ============================================================

def gerar_relatorio_excel():

    df_receitas, df_despesas = (
        preparar_dados()
    )

    resumo = gerar_resumo(
        df_receitas,
        df_despesas
    )

    categorias = gerar_gastos_por_categoria(
        df_despesas
    )

    evolucao = gerar_evolucao_mensal(
        df_receitas,
        df_despesas
    )

    PASTA_RELATORIOS.mkdir(
        parents=True,
        exist_ok=True
    )

    data_geracao = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    caminho = (
        PASTA_RELATORIOS
        / f"relatorio_finpilot_{data_geracao}.xlsx"
    )

    with pd.ExcelWriter(
        caminho,
        engine="openpyxl"
    ) as writer:

        resumo.to_excel(
            writer,
            sheet_name="Resumo",
            index=False
        )

        categorias.to_excel(
            writer,
            sheet_name="Categorias",
            index=False
        )

        evolucao.to_excel(
            writer,
            sheet_name="Evolucao Mensal",
            index=False
        )

        df_receitas.to_excel(
            writer,
            sheet_name="Receitas",
            index=False
        )

        df_despesas.to_excel(
            writer,
            sheet_name="Despesas",
            index=False
        )

    return caminho


# ============================================================
# GERAR RELATÓRIO CSV
# ============================================================

def gerar_relatorio_csv():

    df_receitas, df_despesas = (
        preparar_dados()
    )

    PASTA_RELATORIOS.mkdir(
        parents=True,
        exist_ok=True
    )

    data_geracao = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    caminho = (
        PASTA_RELATORIOS
        / f"lancamentos_finpilot_{data_geracao}.csv"
    )

    df_receitas_exportar = (
        df_receitas.copy()
    )

    df_despesas_exportar = (
        df_despesas.copy()
    )

    df_completo = pd.concat(
        [
            df_receitas_exportar,
            df_despesas_exportar,
        ],
        ignore_index=True
    )

    df_completo.to_csv(
        caminho,
        index=False,
        encoding="utf-8-sig"
    )

    return caminho


# ============================================================
# GERAÇÃO COMPLETA
# ============================================================

def gerar_relatorio_automatico():

    caminho_excel = (
        gerar_relatorio_excel()
    )

    caminho_csv = (
        gerar_relatorio_csv()
    )

    return {
        "excel": caminho_excel,
        "csv": caminho_csv,
    }


# ============================================================
# TESTE
# ============================================================

if __name__ == "__main__":

    print("\n🤖 FinPilot — Automação de Relatórios")
    print("=" * 50)

    resultado = (
        gerar_relatorio_automatico()
    )

    print("\n✅ Relatório gerado com sucesso!")

    print("\n📊 Arquivos criados:")

    print(
        f"📗 Excel: {resultado['excel']}"
    )

    print(
        f"📄 CSV: {resultado['csv']}"
    )

    print("\n🚀 Automação concluída!")