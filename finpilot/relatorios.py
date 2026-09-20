import io

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def formatar_moeda(valor):
    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def nome_mes(numero):
    meses = {
        1: "Janeiro",
        2: "Fevereiro",
        3: "Março",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro"
    }

    return meses.get(numero, "")


# ============================================================
# PREPARAÇÃO DOS DADOS
# ============================================================

def preparar_dados(df_receitas, df_despesas):

    frames = []

    if not df_receitas.empty:

        receitas = df_receitas.copy()
        receitas["tipo"] = "Receita"
        frames.append(receitas)

    if not df_despesas.empty:

        despesas = df_despesas.copy()
        despesas["tipo"] = "Despesa"
        frames.append(despesas)

    if not frames:

        return pd.DataFrame(
            columns=[
                "id",
                "descricao",
                "categoria",
                "valor",
                "data",
                "tipo"
            ]
        )

    df = pd.concat(
        frames,
        ignore_index=True
    )

    df["data"] = pd.to_datetime(
        df["data"],
        errors="coerce"
    )

    return df


# ============================================================
# EXPORTAÇÃO CSV
# ============================================================

def gerar_csv(df):

    exportacao = df.copy()

    if "data" in exportacao.columns:

        exportacao["data"] = pd.to_datetime(
            exportacao["data"],
            errors="coerce"
        ).dt.strftime("%d/%m/%Y")

    return exportacao.to_csv(
        index=False,
        encoding="utf-8-sig"
    ).encode("utf-8-sig")


# ============================================================
# EXPORTAÇÃO EXCEL
# ============================================================

def gerar_excel(df):

    buffer = io.BytesIO()

    with pd.ExcelWriter(
        buffer,
        engine="openpyxl"
    ) as writer:

        exportacao = df.copy()

        if "data" in exportacao.columns:

            exportacao["data"] = pd.to_datetime(
                exportacao["data"],
                errors="coerce"
            )

        exportacao.to_excel(
            writer,
            index=False,
            sheet_name="Lancamentos"
        )

    buffer.seek(0)

    return buffer.getvalue()


# ============================================================
# RELATÓRIO PRINCIPAL
# ============================================================

def mostrar_relatorios(df_receitas, df_despesas):

    st.title("📊 Relatórios e Analytics")

    st.caption(
        "Transforme seus lançamentos em informações financeiras."
    )

    df = preparar_dados(
        df_receitas,
        df_despesas
    )

    if df.empty:

        st.info(
            "Ainda não existem lançamentos para analisar."
        )

        return

    registros_sem_data = df["data"].isna().sum()

    if registros_sem_data > 0:

        st.warning(
            f"ℹ️ {registros_sem_data} lançamento(s) "
            "não possuem data e não entram na análise por período."
        )

    df = df[
        df["data"].notna()
    ].copy()

    if df.empty:

        st.info(
            "Não existem lançamentos com data disponível."
        )

        return

    # ========================================================
    # CAMPOS TEMPORAIS
    # ========================================================

    df["ano"] = df["data"].dt.year
    df["mes_num"] = df["data"].dt.month

    anos = sorted(
        df["ano"].unique(),
        reverse=True
    )

    meses = {
        "Todos os meses": None,
        "Janeiro": 1,
        "Fevereiro": 2,
        "Março": 3,
        "Abril": 4,
        "Maio": 5,
        "Junho": 6,
        "Julho": 7,
        "Agosto": 8,
        "Setembro": 9,
        "Outubro": 10,
        "Novembro": 11,
        "Dezembro": 12
    }

    # ========================================================
    # FILTROS
    # ========================================================

    st.subheader("🔎 Filtros")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        ano_selecionado = st.selectbox(
            "Ano",
            anos
        )

    with col2:

        mes_selecionado_nome = st.selectbox(
            "Mês",
            list(meses.keys())
        )

    with col3:

        categorias = sorted(
            df["categoria"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        categoria_filtro = st.selectbox(
            "Categoria",
            ["Todas"] + categorias
        )

    with col4:

        tipo_filtro = st.selectbox(
            "Tipo",
            [
                "Todos",
                "Receita",
                "Despesa"
            ]
        )

    mes_selecionado = meses[
        mes_selecionado_nome
    ]

    # ========================================================
    # APLICAÇÃO DOS FILTROS
    # ========================================================

    df_filtrado = df[
        df["ano"] == ano_selecionado
    ].copy()

    if mes_selecionado is not None:

        df_filtrado = df_filtrado[
            df_filtrado["mes_num"] == mes_selecionado
        ]

    if categoria_filtro != "Todas":

        df_filtrado = df_filtrado[
            df_filtrado["categoria"].astype(str)
            == categoria_filtro
        ]

    if tipo_filtro != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["tipo"] == tipo_filtro
        ]

    # ========================================================
    # TÍTULO DO PERÍODO
    # ========================================================

    if mes_selecionado is None:

        periodo_nome = f"Ano de {ano_selecionado}"

    else:

        periodo_nome = (
            f"{mes_selecionado_nome} de "
            f"{ano_selecionado}"
        )

    st.divider()

    st.subheader(
        f"📌 Resumo — {periodo_nome}"
    )

    # ========================================================
    # TOTAIS
    # ========================================================

    receitas = df_filtrado[
        df_filtrado["tipo"] == "Receita"
    ]

    despesas = df_filtrado[
        df_filtrado["tipo"] == "Despesa"
    ]

    total_receitas = receitas["valor"].sum()
    total_despesas = despesas["valor"].sum()

    saldo = (
        total_receitas -
        total_despesas
    )

    comprometimento = (
        total_despesas /
        total_receitas *
        100
        if total_receitas > 0
        else 0
    )

    quantidade_lancamentos = len(
        df_filtrado
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "💰 Receitas",
            formatar_moeda(total_receitas)
        )

    with col2:

        st.metric(
            "💸 Despesas",
            formatar_moeda(total_despesas)
        )

    with col3:

        st.metric(
            "📊 Saldo",
            formatar_moeda(saldo)
        )

    with col4:

        st.metric(
            "📋 Lançamentos",
            quantidade_lancamentos
        )

    # ========================================================
    # KPIs AVANÇADOS
    # ========================================================

    st.subheader("📈 Indicadores")

    col1, col2, col3, col4 = st.columns(4)

    if not despesas.empty:

        despesa_media = despesas["valor"].mean()

    else:

        despesa_media = 0

    if not receitas.empty:

        receita_media = receitas["valor"].mean()

    else:

        receita_media = 0

    if not df_filtrado.empty:

        primeiro_dia = df_filtrado["data"].min()
        ultimo_dia = df_filtrado["data"].max()

        dias_periodo = (
            ultimo_dia - primeiro_dia
        ).days + 1

        gasto_diario = (
            total_despesas / dias_periodo
            if dias_periodo > 0
            else 0
        )

    else:

        gasto_diario = 0

    with col1:

        st.metric(
            "💰 Receita média",
            formatar_moeda(receita_media)
        )

    with col2:

        st.metric(
            "💸 Despesa média",
            formatar_moeda(despesa_media)
        )

    with col3:

        st.metric(
            "📅 Gasto diário médio",
            formatar_moeda(gasto_diario)
        )

    with col4:

        st.metric(
            "📉 Comprometimento",
            f"{comprometimento:.1f}%"
        )

    # ========================================================
    # EVOLUÇÃO ANUAL
    # ========================================================

    st.divider()

    st.subheader(
        f"📈 Evolução mensal — {ano_selecionado}"
    )

    df_ano = df[
        df["ano"] == ano_selecionado
    ].copy()

    resumo_mensal = (
        df_ano
        .groupby(
            ["mes_num", "tipo"]
        )["valor"]
        .sum()
        .reset_index()
    )

    meses_ano = pd.DataFrame({
        "mes_num": range(1, 13)
    })

    receitas_mensais = (
        resumo_mensal[
            resumo_mensal["tipo"] == "Receita"
        ][
            ["mes_num", "valor"]
        ]
        .rename(
            columns={
                "valor": "receitas"
            }
        )
    )

    despesas_mensais = (
        resumo_mensal[
            resumo_mensal["tipo"] == "Despesa"
        ][
            ["mes_num", "valor"]
        ]
        .rename(
            columns={
                "valor": "despesas"
            }
        )
    )

    evolucao = meses_ano.merge(
        receitas_mensais,
        on="mes_num",
        how="left"
    )

    evolucao = evolucao.merge(
        despesas_mensais,
        on="mes_num",
        how="left"
    )

    evolucao["receitas"] = (
        evolucao["receitas"]
        .fillna(0)
    )

    evolucao["despesas"] = (
        evolucao["despesas"]
        .fillna(0)
    )

    evolucao["saldo"] = (
        evolucao["receitas"] -
        evolucao["despesas"]
    )

    evolucao["mes"] = evolucao[
        "mes_num"
    ].apply(nome_mes)

    fig = px.bar(
        evolucao,
        x="mes",
        y=[
            "receitas",
            "despesas"
        ],
        barmode="group",
        labels={
            "mes": "Mês",
            "value": "Valor",
            "variable": "Tipo"
        }
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ========================================================
    # SALDO MENSAL
    # ========================================================

    fig_saldo = px.line(
        evolucao,
        x="mes",
        y="saldo",
        markers=True,
        labels={
            "mes": "Mês",
            "saldo": "Saldo"
        }
    )

    fig_saldo.update_layout(
        title="Evolução do saldo"
    )

    st.plotly_chart(
        fig_saldo,
        width="stretch"
    )

    # ========================================================
    # CATEGORIAS
    # ========================================================

    st.divider()

    st.subheader(
        f"🏷️ Categorias — {periodo_nome}"
    )

    if despesas.empty:

        st.info(
            "Nenhuma despesa encontrada no período."
        )

    else:

        categorias_df = (
            despesas
            .groupby("categoria")["valor"]
            .sum()
            .reset_index()
            .sort_values(
                "valor",
                ascending=False
            )
        )

        total_categorias = (
            categorias_df["valor"].sum()
        )

        categorias_df["percentual"] = (
            categorias_df["valor"]
            /
            total_categorias
            *
            100
        )

        col1, col2 = st.columns(2)

        with col1:

            fig_categoria = px.bar(
                categorias_df,
                x="categoria",
                y="valor",
                text_auto=".2f",
                labels={
                    "categoria": "Categoria",
                    "valor": "Valor"
                }
            )

            st.plotly_chart(
                fig_categoria,
                width="stretch"
            )

        with col2:

            maior_categoria = (
                categorias_df.iloc[0]
            )

            st.info(
                f"🏆 **Maior categoria**\n\n"
                f"**{maior_categoria['categoria']}**\n\n"
                f"{formatar_moeda(maior_categoria['valor'])}\n\n"
                f"{maior_categoria['percentual']:.1f}% "
                "das despesas."
            )

            tabela_categorias = categorias_df.copy()

            tabela_categorias["valor"] = (
                tabela_categorias["valor"]
                .apply(formatar_moeda)
            )

            tabela_categorias["percentual"] = (
                tabela_categorias["percentual"]
                .round(1)
                .astype(str)
                + "%"
            )

            tabela_categorias = (
                tabela_categorias
                .rename(
                    columns={
                        "categoria": "Categoria",
                        "valor": "Valor",
                        "percentual": "%"
                    }
                )
            )

            st.dataframe(
                tabela_categorias,
                width="stretch",
                hide_index=True
            )

    # ========================================================
    # COMPARAÇÃO COM MÊS ANTERIOR
    # ========================================================

    if mes_selecionado is not None:

        st.divider()

        st.subheader(
            "🔄 Comparação com o mês anterior"
        )

        data_mes = pd.Timestamp(
            year=ano_selecionado,
            month=mes_selecionado,
            day=1
        )

        mes_anterior = (
            data_mes -
            pd.DateOffset(months=1)
        )

        df_anterior = df[
            (
                df["data"].dt.year
                == mes_anterior.year
            )
            &
            (
                df["data"].dt.month
                == mes_anterior.month
            )
        ]

        if categoria_filtro != "Todas":

            df_anterior = df_anterior[
                df_anterior["categoria"].astype(str)
                == categoria_filtro
            ]

        if tipo_filtro != "Todos":

            df_anterior = df_anterior[
                df_anterior["tipo"]
                == tipo_filtro
            ]

        if df_anterior.empty:

            st.info(
                "Não existem dados do mês anterior "
                "para comparação."
            )

        else:

            receitas_anterior = df_anterior[
                df_anterior["tipo"] == "Receita"
            ]["valor"].sum()

            despesas_anterior = df_anterior[
                df_anterior["tipo"] == "Despesa"
            ]["valor"].sum()

            saldo_anterior = (
                receitas_anterior -
                despesas_anterior
            )

            def variacao(atual, anterior):

                if anterior == 0:

                    if atual == 0:
                        return 0

                    return 100

                return (
                    (atual - anterior)
                    /
                    abs(anterior)
                    *
                    100
                )

            var_receitas = variacao(
                total_receitas,
                receitas_anterior
            )

            var_despesas = variacao(
                total_despesas,
                despesas_anterior
            )

            var_saldo = variacao(
                saldo,
                saldo_anterior
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Receitas",
                    formatar_moeda(
                        total_receitas
                    ),
                    f"{var_receitas:+.1f}%"
                )

            with col2:

                st.metric(
                    "Despesas",
                    formatar_moeda(
                        total_despesas
                    ),
                    f"{var_despesas:+.1f}%"
                )

            with col3:

                st.metric(
                    "Saldo",
                    formatar_moeda(
                        saldo
                    ),
                    f"{var_saldo:+.1f}%"
                )

    # ========================================================
    # LANÇAMENTOS
    # ========================================================

    st.divider()

    st.subheader(
        f"📋 Lançamentos — {periodo_nome}"
    )

    if df_filtrado.empty:

        st.info(
            "Nenhum lançamento encontrado "
            "com os filtros selecionados."
        )

    else:

        tabela = df_filtrado[
            [
                "data",
                "tipo",
                "descricao",
                "categoria",
                "valor"
            ]
        ].copy()

        tabela["data"] = (
            tabela["data"]
            .dt.strftime("%d/%m/%Y")
        )

        tabela["valor"] = (
            tabela["valor"]
            .apply(formatar_moeda)
        )

        tabela = tabela.rename(
            columns={
                "data": "Data",
                "tipo": "Tipo",
                "descricao": "Descrição",
                "categoria": "Categoria",
                "valor": "Valor"
            }
        )

        st.dataframe(
            tabela,
            width="stretch",
            hide_index=True
        )

        # ====================================================
        # EXPORTAÇÃO
        # ====================================================

        st.subheader(
            "📥 Exportar relatório"
        )

        dados_exportacao = df_filtrado[
            [
                "data",
                "tipo",
                "descricao",
                "categoria",
                "valor"
            ]
        ].copy()

        dados_exportacao = dados_exportacao.rename(
            columns={
                "data": "Data",
                "tipo": "Tipo",
                "descricao": "Descrição",
                "categoria": "Categoria",
                "valor": "Valor"
            }
        )

        col1, col2 = st.columns(2)

        with col1:

            csv = gerar_csv(
                dados_exportacao
            )

            st.download_button(
                "📄 Baixar CSV",
                data=csv,
                file_name=(
                    f"finpilot_{ano_selecionado}"
                    f"_{mes_selecionado_nome.lower()}.csv"
                ),
                mime="text/csv",
                width="stretch"
            )

        with col2:

            try:

                excel = gerar_excel(
                    dados_exportacao
                )

                st.download_button(
                    "📊 Baixar Excel",
                    data=excel,
                    file_name=(
                        f"finpilot_{ano_selecionado}"
                        f"_{mes_selecionado_nome.lower()}.xlsx"
                    ),
                    mime=(
                        "application/vnd.openxmlformats-"
                        "officedocument.spreadsheetml.sheet"
                    ),
                    width="stretch"
                )

            except ImportError:

                st.warning(
                    "Para exportar Excel, instale o openpyxl."
                )