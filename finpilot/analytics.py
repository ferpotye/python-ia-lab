import pandas as pd

from database import buscar_receitas, buscar_despesas
from charts import gerar_grafico_despesas, gerar_grafico_percentual


LARGURA = 64


# ============================================================
# FUNÇÕES VISUAIS
# ============================================================

def linha():
    print("═" * LARGURA)


def titulo(texto):

    print()
    linha()
    print(f"{texto:^{LARGURA}}")
    linha()


def formatar_moeda(valor):

    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

def carregar_dados():

    receitas = buscar_receitas()
    despesas = buscar_despesas()

    df_receitas = pd.DataFrame(
        receitas,
        columns=[
            "id",
            "descricao",
            "categoria",
            "valor",
            "data"
        ]
    )

    df_despesas = pd.DataFrame(
        despesas,
        columns=[
            "id",
            "descricao",
            "categoria",
            "valor",
            "data"
        ]
    )

    return df_receitas, df_despesas


# ============================================================
# ANÁLISE DE DESPESAS
# ============================================================

def analisar_despesas_por_categoria(
    df_despesas
):

    if df_despesas.empty:

        return pd.Series(
            dtype=float
        )

    return (
        df_despesas
        .groupby("categoria")["valor"]
        .sum()
        .sort_values(
            ascending=False
        )
    )


# ============================================================
# RESUMO FINANCEIRO
# ============================================================

def gerar_resumo_financeiro(
    df_receitas,
    df_despesas
):

    total_receitas = (
        df_receitas["valor"].sum()
    )

    total_despesas = (
        df_despesas["valor"].sum()
    )

    saldo = (
        total_receitas -
        total_despesas
    )

    if total_receitas > 0:

        percentual_despesas = (
            total_despesas /
            total_receitas *
            100
        )

    else:

        percentual_despesas = 0

    return {
        "total_receitas":
            total_receitas,

        "total_despesas":
            total_despesas,

        "saldo":
            saldo,

        "percentual_despesas":
            percentual_despesas
    }


# ============================================================
# MAIOR CATEGORIA
# ============================================================

def encontrar_maior_categoria(
    df_despesas
):

    despesas_por_categoria = (
        analisar_despesas_por_categoria(
            df_despesas
        )
    )

    if despesas_por_categoria.empty:

        return None

    return {
        "categoria":
            despesas_por_categoria.idxmax(),

        "valor":
            despesas_por_categoria.max()
    }


# ============================================================
# PERCENTUAL POR CATEGORIA
# ============================================================

def calcular_percentual_por_categoria(
    df_despesas
):

    despesas_por_categoria = (
        analisar_despesas_por_categoria(
            df_despesas
        )
    )

    if despesas_por_categoria.empty:

        return pd.Series(
            dtype=float
        )

    total_despesas = (
        despesas_por_categoria.sum()
    )

    if total_despesas == 0:

        return pd.Series(
            dtype=float
        )

    return (
        despesas_por_categoria
        .div(total_despesas)
        .mul(100)
    )


# ============================================================
# INSIGHTS
# ============================================================

def gerar_insights(
    resumo,
    maior_categoria
):

    insights = []

    receitas = resumo[
        "total_receitas"
    ]

    despesas = resumo[
        "total_despesas"
    ]

    saldo = resumo[
        "saldo"
    ]

    percentual = resumo[
        "percentual_despesas"
    ]

    if saldo > 0:

        insights.append(
            f"✅ Seu saldo está positivo "
            f"em {formatar_moeda(saldo)}."
        )

    elif saldo == 0:

        insights.append(
            "⚠️ Suas receitas e despesas "
            "estão equilibradas."
        )

    else:

        insights.append(
            f"🚨 Suas despesas superam "
            f"suas receitas em "
            f"{formatar_moeda(abs(saldo))}."
        )

    if percentual < 50:

        insights.append(
            f"🟢 Você está comprometendo "
            f"{percentual:.1f}% da sua renda "
            f"com despesas."
        )

    elif percentual <= 70:

        insights.append(
            f"🟡 Você está comprometendo "
            f"{percentual:.1f}% da sua renda "
            f"com despesas."
        )

    else:

        insights.append(
            f"🔴 Você está comprometendo "
            f"{percentual:.1f}% da sua renda "
            f"com despesas."
        )

    if maior_categoria:

        insights.append(
            f"🏆 Sua maior categoria de "
            f"despesa é "
            f"{maior_categoria['categoria']}, "
            f"com "
            f"{formatar_moeda(maior_categoria['valor'])}."
        )

    if receitas > 0:

        economia = (
            receitas -
            despesas
        )

        if economia > 0:

            insights.append(
                f"💡 Você terminou o período "
                f"com {formatar_moeda(economia)} "
                f"disponíveis."
            )

    return insights


# ============================================================
# DASHBOARD NO TERMINAL
# ============================================================

def mostrar_dashboard(
    df_receitas,
    df_despesas,
    resumo,
    despesas_por_categoria,
    maior_categoria
):

    print()

    linha()

    print(
        "💰 FINPILOT".center(LARGURA)
    )

    print(
        "Seu dinheiro. Seu controle."
        .center(LARGURA)
    )

    linha()

    print()

    print(
        "💰 RECEITAS        "
        "💳 DESPESAS        "
        "💵 SALDO"
    )

    print(
        f"{formatar_moeda(resumo['total_receitas']):<20}"
        f"{formatar_moeda(resumo['total_despesas']):<20}"
        f"{formatar_moeda(resumo['saldo'])}"
    )

    print()

    print(
        f"📊 RENDA COMPROMETIDA: "
        f"{resumo['percentual_despesas']:.1f}%"
    )

    print()

    linha()

    print(
        "📊 DESPESAS POR CATEGORIA"
        .center(LARGURA)
    )

    linha()

    if despesas_por_categoria.empty:

        print(
            "\n⚠️ Nenhuma despesa cadastrada."
        )

    else:

        for categoria, valor in (
            despesas_por_categoria.items()
        ):

            percentual = (
                valor /
                resumo["total_despesas"] *
                100
                if resumo["total_despesas"] > 0
                else 0
            )

            print(
                f"📂 {categoria:<20}"
                f"{formatar_moeda(valor):>15}   "
                f"{percentual:>5.1f}%"
            )

    print()

    linha()

    print(
        "🏆 DESTAQUES".center(LARGURA)
    )

    linha()

    if maior_categoria:

        print(
            f"🏆 Maior categoria: "
            f"{maior_categoria['categoria']}"
        )

        print(
            f"💳 Valor: "
            f"{formatar_moeda(maior_categoria['valor'])}"
        )

    else:

        print(
            "⚠️ Nenhuma categoria encontrada."
        )

    print()

    linha()

    print(
        "🤖 INSIGHTS FINANCEIROS"
        .center(LARGURA)
    )

    linha()

    insights = gerar_insights(
        resumo,
        maior_categoria
    )

    for insight in insights:

        print(
            f"\n{insight}"
        )

    print()

    linha()


# ============================================================
# GERAR RELATÓRIO
# ============================================================

def gerar_relatorio():

    (
        df_receitas,
        df_despesas
    ) = carregar_dados()

    despesas_por_categoria = (
        analisar_despesas_por_categoria(
            df_despesas
        )
    )

    resumo = gerar_resumo_financeiro(
        df_receitas,
        df_despesas
    )

    maior_categoria = (
        encontrar_maior_categoria(
            df_despesas
        )
    )

    mostrar_dashboard(
        df_receitas,
        df_despesas,
        resumo,
        despesas_por_categoria,
        maior_categoria
    )

    print(
        "\n📊 Gerando gráficos..."
    )

    gerar_grafico_despesas(
        despesas_por_categoria
    )

    gerar_grafico_percentual(
        despesas_por_categoria
    )


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    gerar_relatorio()