import pandas as pd


def formatar_moeda(valor):
    """Formata valores no padrão brasileiro."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def gerar_insights(df_receitas, df_despesas):
    """
    Analisa os dados financeiros e gera insights automáticos.

    V4.2
    - Analisa saldo
    - Analisa comprometimento da renda
    - Identifica maior categoria
    - Identifica concentração de gastos
    - Analisa média das despesas
    - Identifica maiores gastos
    - Detecta gastos recorrentes
    - Compara meses
    - Detecta aumento de despesas
    - Analisa evolução financeira
    """

    insights = []

    # ============================================================
    # PREPARAÇÃO DOS DADOS
    # ============================================================

    receitas = df_receitas.copy()
    despesas = df_despesas.copy()

    if not receitas.empty and "valor" in receitas.columns:
        receitas["valor"] = pd.to_numeric(
            receitas["valor"],
            errors="coerce"
        ).fillna(0)

    if not despesas.empty and "valor" in despesas.columns:
        despesas["valor"] = pd.to_numeric(
            despesas["valor"],
            errors="coerce"
        ).fillna(0)

    total_receitas = (
        receitas["valor"].sum()
        if not receitas.empty
        else 0
    )

    total_despesas = (
        despesas["valor"].sum()
        if not despesas.empty
        else 0
    )

    saldo = total_receitas - total_despesas

    # ============================================================
    # 1. SALDO
    # ============================================================

    if saldo > 0:

        insights.append(
            f"💰 Seu saldo atual é positivo em "
            f"{formatar_moeda(saldo)}."
        )

    elif saldo < 0:

        insights.append(
            f"🚨 Suas despesas estão "
            f"{formatar_moeda(abs(saldo))} acima das receitas."
        )

    else:

        insights.append(
            "ℹ️ Suas receitas e despesas estão equilibradas."
        )

    # ============================================================
    # 2. COMPROMETIMENTO DA RENDA
    # ============================================================

    if total_receitas > 0:

        percentual = (
            total_despesas / total_receitas
        ) * 100

        if percentual >= 100:

            insights.append(
                "🚨 Seus gastos ultrapassaram "
                "o total das suas receitas."
            )

        elif percentual >= 80:

            insights.append(
                f"⚠️ Você já comprometeu "
                f"{percentual:.1f}% da sua renda."
            )

        elif percentual >= 50:

            insights.append(
                f"📊 Suas despesas representam "
                f"{percentual:.1f}% da sua renda."
            )

        else:

            insights.append(
                f"✅ Suas despesas representam "
                f"{percentual:.1f}% da sua renda."
            )

    # ============================================================
    # 3. MAIOR CATEGORIA
    # ============================================================

    gastos_categoria = pd.Series(dtype=float)

    if not despesas.empty and "categoria" in despesas.columns:

        gastos_categoria = (
            despesas
            .groupby("categoria")["valor"]
            .sum()
            .sort_values(ascending=False)
        )

        if not gastos_categoria.empty:

            categoria = gastos_categoria.index[0]
            valor_categoria = gastos_categoria.iloc[0]

            percentual_categoria = (
                valor_categoria / total_despesas * 100
                if total_despesas > 0
                else 0
            )

            insights.append(
                f"🏷️ A categoria com maior gasto é "
                f"'{categoria}', com "
                f"{formatar_moeda(valor_categoria)}, "
                f"representando "
                f"{percentual_categoria:.1f}% "
                f"das suas despesas."
            )

    # ============================================================
    # 4. CONCENTRAÇÃO DE GASTOS
    # ============================================================

    if not gastos_categoria.empty and total_despesas > 0:

        duas_maiores = gastos_categoria.head(2).sum()

        percentual_duas_maiores = (
            duas_maiores / total_despesas
        ) * 100

        if percentual_duas_maiores >= 70:

            insights.append(
                f"🔎 Suas duas maiores categorias concentram "
                f"{percentual_duas_maiores:.1f}% "
                f"dos seus gastos."
            )

    # ============================================================
    # 5. MÉDIA DAS DESPESAS
    # ============================================================

    if not despesas.empty:

        media_despesa = despesas["valor"].mean()

        insights.append(
            f"📈 O valor médio dos seus lançamentos "
            f"de despesa é "
            f"{formatar_moeda(media_despesa)}."
        )

    # ============================================================
    # 6. MAIOR DESPESA INDIVIDUAL
    # ============================================================

    if not despesas.empty:

        maior_despesa = despesas.loc[
            despesas["valor"].idxmax()
        ]

        descricao = maior_despesa.get(
            "descricao",
            "Despesa"
        )

        valor = maior_despesa["valor"]

        insights.append(
            f"💳 Seu maior lançamento de despesa foi "
            f"'{descricao}', no valor de "
            f"{formatar_moeda(valor)}."
        )

    # ============================================================
    # 7. GASTOS RECORRENTES
    # ============================================================

    if (
        not despesas.empty
        and "descricao" in despesas.columns
    ):

        recorrentes = (
            despesas
            .groupby("descricao")
            .size()
            .sort_values(ascending=False)
        )

        recorrentes = recorrentes[
            recorrentes >= 2
        ]

        if not recorrentes.empty:

            descricao_recorrente = recorrentes.index[0]
            quantidade = recorrentes.iloc[0]

            valor_recorrente = despesas.loc[
                despesas["descricao"] == descricao_recorrente,
                "valor"
            ].sum()

            insights.append(
                f"🔁 O lançamento "
                f"'{descricao_recorrente}' "
                f"aparece {quantidade} vezes, "
                f"totalizando "
                f"{formatar_moeda(valor_recorrente)}."
            )

    # ============================================================
    # 8. ANÁLISE MENSAL
    # ============================================================

    despesas_com_data = pd.DataFrame()

    if (
        not despesas.empty
        and "data" in despesas.columns
    ):

        despesas_com_data = despesas.copy()

        despesas_com_data["data"] = pd.to_datetime(
            despesas_com_data["data"],
            errors="coerce",
            dayfirst=True
        )

        despesas_com_data = despesas_com_data.dropna(
            subset=["data"]
        )

    if not despesas_com_data.empty:

        despesas_com_data["mes"] = (
            despesas_com_data["data"]
            .dt.to_period("M")
        )

        gastos_mensais = (
            despesas_com_data
            .groupby("mes")["valor"]
            .sum()
            .sort_index()
        )

        # ========================================================
        # 9. COMPARAÇÃO ENTRE MESES
        # ========================================================

        if len(gastos_mensais) >= 2:

            mes_atual = gastos_mensais.iloc[-1]
            mes_anterior = gastos_mensais.iloc[-2]

            if mes_anterior > 0:

                variacao = (
                    (mes_atual - mes_anterior)
                    / mes_anterior
                ) * 100

                if variacao >= 20:

                    insights.append(
                        f"📈 Seus gastos aumentaram "
                        f"{variacao:.1f}% em relação "
                        f"ao mês anterior."
                    )

                elif variacao <= -20:

                    insights.append(
                        f"📉 Seus gastos diminuíram "
                        f"{abs(variacao):.1f}% em relação "
                        f"ao mês anterior."
                    )

                else:

                    insights.append(
                        f"📊 Seus gastos variaram "
                        f"{variacao:+.1f}% em relação "
                        f"ao mês anterior."
                    )

    # ============================================================
    # 10. MAIOR MÊS DE GASTOS
    # ============================================================

    if not despesas_com_data.empty:

        gastos_mensais = (
            despesas_com_data
            .groupby("mes")["valor"]
            .sum()
            .sort_values(ascending=False)
        )

        if not gastos_mensais.empty:

            maior_mes = gastos_mensais.index[0]
            maior_valor = gastos_mensais.iloc[0]

            insights.append(
                f"📅 O período com maior volume de "
                f"despesas foi {maior_mes.strftime('%m/%Y')}, "
                f"com {formatar_moeda(maior_valor)}."
            )

    # ============================================================
    # 11. EVOLUÇÃO DO SALDO MENSAL
    # ============================================================

    receitas_com_data = pd.DataFrame()

    if (
        not receitas.empty
        and "data" in receitas.columns
    ):

        receitas_com_data = receitas.copy()

        receitas_com_data["data"] = pd.to_datetime(
            receitas_com_data["data"],
            errors="coerce",
            dayfirst=True
        )

        receitas_com_data = receitas_com_data.dropna(
            subset=["data"]
        )

    if (
        not receitas_com_data.empty
        and not despesas_com_data.empty
    ):

        receitas_com_data["mes"] = (
            receitas_com_data["data"]
            .dt.to_period("M")
        )

        receitas_mensais = (
            receitas_com_data
            .groupby("mes")["valor"]
            .sum()
        )

        despesas_mensais = (
            despesas_com_data
            .groupby("mes")["valor"]
            .sum()
        )

        meses = sorted(
            set(receitas_mensais.index)
            | set(despesas_mensais.index)
        )

        if len(meses) >= 2:

            ultimo_mes = meses[-1]

            receita_ultimo = receitas_mensais.get(
                ultimo_mes,
                0
            )

            despesa_ultimo = despesas_mensais.get(
                ultimo_mes,
                0
            )

            saldo_mes = (
                receita_ultimo -
                despesa_ultimo
            )

            if saldo_mes > 0:

                insights.append(
                    f"💵 No último mês analisado, "
                    f"suas receitas superaram as despesas "
                    f"em {formatar_moeda(saldo_mes)}."
                )

            elif saldo_mes < 0:

                insights.append(
                    f"⚠️ No último mês analisado, "
                    f"suas despesas superaram as receitas "
                    f"em {formatar_moeda(abs(saldo_mes))}."
                )

    # ============================================================
    # 12. QUANTIDADE DE LANÇAMENTOS
    # ============================================================

    total_lancamentos = (
        len(receitas) +
        len(despesas)
    )

    insights.append(
        f"📋 O FinPilot analisou "
        f"{total_lancamentos} lançamentos financeiros."
    )

    return insights