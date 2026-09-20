import matplotlib.pyplot as plt


def gerar_grafico_despesas(despesas_por_categoria):
    if despesas_por_categoria.empty:
        print("⚠️ Não há despesas para gerar o gráfico.")
        return

    despesas_por_categoria.plot(
        kind="bar",
        title="Despesas por Categoria"
    )

    plt.xlabel("Categoria")
    plt.ylabel("Valor (R$)")
    plt.tight_layout()
    plt.show()


def gerar_grafico_percentual(despesas_por_categoria):
    if despesas_por_categoria.empty:
        print("⚠️ Não há despesas para gerar o gráfico.")
        return

    despesas_por_categoria.plot(
        kind="pie",
        autopct="%1.1f%%",
        title="Distribuição das Despesas",
        ylabel=""
    )

    plt.tight_layout()
    plt.show()