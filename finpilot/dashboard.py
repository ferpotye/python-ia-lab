import streamlit as st
import pandas as pd
import plotly.express as px
import tempfile
from pathlib import Path

from database import (
    buscar_receitas,
    buscar_despesas,
    buscar_metas,
    salvar_meta,
    atualizar_meta,
    atualizar_receita,
    atualizar_despesa,
    excluir_receita,
    excluir_despesa,
    excluir_meta
)

from importador import (
    processar_csv,
    salvar_lancamentos
)

from relatorios import mostrar_relatorios


from automacao_relatorios import gerar_relatorio_automatico

# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="FinPilot",
    page_icon="💰",
    layout="wide"
)


# ============================================================
# ESTILO
# ============================================================

st.markdown("""
<style>

    .main {
        background-color: #0e1117;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 10px;
    }

    .metric-title {
        color: #8b949e;
        font-size: 14px;
        margin-bottom: 5px;
    }

    .metric-value {
        color: white;
        font-size: 28px;
        font-weight: bold;
    }

    .section-title {
        margin-top: 25px;
        margin-bottom: 15px;
    }

    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 12px;
    }

</style>
""", unsafe_allow_html=True)


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


def formatar_data(data):

    if pd.isna(data) or data is None or data == "":
        return "Sem data"

    try:

        data_convertida = pd.to_datetime(data)

        return data_convertida.strftime("%d/%m/%Y")

    except Exception:

        return "Sem data"


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

    if not df_receitas.empty:
        df_receitas["tipo"] = "Receita"

    if not df_despesas.empty:
        df_despesas["tipo"] = "Despesa"

    return df_receitas, df_despesas


def carregar_metas():

    metas = buscar_metas()

    return pd.DataFrame(
        metas,
        columns=[
            "id",
            "nome",
            "valor_objetivo",
            "valor_atual"
        ]
    )


def calcular_resumo(
    df_receitas,
    df_despesas
):

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

    saldo = (
        total_receitas -
        total_despesas
    )

    percentual = (
        total_despesas /
        total_receitas *
        100
        if total_receitas > 0
        else 0
    )

    return (
        total_receitas,
        total_despesas,
        saldo,
        percentual
    )


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

df_receitas, df_despesas = carregar_dados()

df_metas = carregar_metas()

(
    total_receitas,
    total_despesas,
    saldo,
    percentual
) = calcular_resumo(
    df_receitas,
    df_despesas
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("💰 FinPilot")

st.sidebar.caption(
    "Seu dinheiro. Seu controle."
)

st.sidebar.divider()

pagina = st.sidebar.radio(
    "Navegação",
    [
        "Dashboard",
        "Receitas",
        "Despesas",
        "Metas",
        "Relatórios",
        "📥 Importar Extrato",
        "Insights"
    ]
)

st.sidebar.divider()

if st.sidebar.button(
    "🔄 Atualizar dados",
    width="stretch"
):

    st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

if pagina == "Dashboard":

    st.title("💰 Dashboard")

    st.caption(
        "Visão geral da sua vida financeira."
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
            "📉 Comprometimento",
            f"{percentual:.1f}%"
        )

    st.divider()

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # DESPESAS POR CATEGORIA
    # --------------------------------------------------------

    with col1:

        st.subheader(
            "💸 Despesas por categoria"
        )

        if not df_despesas.empty:

            categorias = (
                df_despesas
                .groupby("categoria")["valor"]
                .sum()
                .reset_index()
                .sort_values(
                    "valor",
                    ascending=False
                )
            )

            fig = px.bar(
                categorias,
                x="categoria",
                y="valor",
                text_auto=".2f"
            )

            fig.update_layout(
                xaxis_title="Categoria",
                yaxis_title="Valor",
                showlegend=False
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info(
                "Nenhuma despesa cadastrada."
            )

    # --------------------------------------------------------
    # DISTRIBUIÇÃO
    # --------------------------------------------------------

    with col2:

        st.subheader(
            "🍩 Distribuição das despesas"
        )

        if not df_despesas.empty:

            categorias = (
                df_despesas
                .groupby("categoria")["valor"]
                .sum()
                .reset_index()
            )

            fig = px.pie(
                categorias,
                names="categoria",
                values="valor",
                hole=0.45
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info(
                "Nenhuma despesa cadastrada."
            )

    st.divider()

    st.subheader("📌 Resumo")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Lançamentos",
            len(df_receitas) +
            len(df_despesas)
        )

    with col2:

        maior_receita = (
            df_receitas["valor"].max()
            if not df_receitas.empty
            else 0
        )

        st.metric(
            "Maior receita",
            formatar_moeda(
                maior_receita
            )
        )

    with col3:

        maior_despesa = (
            df_despesas["valor"].max()
            if not df_despesas.empty
            else 0
        )

        st.metric(
            "Maior despesa",
            formatar_moeda(
                maior_despesa
            )
        )


# ============================================================
# RECEITAS
# ============================================================

elif pagina == "Receitas":

    st.title("💰 Receitas")

    if df_receitas.empty:

        st.info(
            "Nenhuma receita cadastrada."
        )

    else:

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Total",
                formatar_moeda(
                    df_receitas["valor"].sum()
                )
            )

        with col2:

            st.metric(
                "Quantidade",
                len(df_receitas)
            )

        with col3:

            st.metric(
                "Maior receita",
                formatar_moeda(
                    df_receitas["valor"].max()
                )
            )

        st.divider()

        categorias = [
            "Todas"
        ] + sorted(
            df_receitas[
                "categoria"
            ]
            .dropna()
            .unique()
            .tolist()
        )

        categoria_filtro = st.selectbox(
            "Filtrar por categoria",
            categorias
        )

        df_filtrado = df_receitas.copy()

        if categoria_filtro != "Todas":

            df_filtrado = df_filtrado[
                df_filtrado["categoria"]
                == categoria_filtro
            ]

        for _, receita in df_filtrado.iterrows():

            col1, col2, col3, col4, col5, col6 = st.columns(
                [1.2, 2, 1.5, 1.3, 0.7, 0.7]
            )

            with col1:

                st.write(
                    formatar_data(
                        receita["data"]
                    )
                )

            with col2:

                st.write(
                    receita["descricao"]
                )

            with col3:

                st.write(
                    receita["categoria"]
                )

            with col4:

                st.write(
                    formatar_moeda(
                        receita["valor"]
                    )
                )

            with col5:

                if st.button(
                    "✏️",
                    key=(
                        f"editar_receita_"
                        f"{receita['id']}"
                    )
                ):

                    st.session_state[
                        "editar_receita"
                    ] = int(
                        receita["id"]
                    )

                    st.rerun()

            with col6:

                if st.button(
                    "🗑️",
                    key=(
                        f"excluir_receita_"
                        f"{receita['id']}"
                    )
                ):

                    st.session_state[
                        "confirmar_exclusao"
                    ] = (
                        "receita",
                        int(
                            receita["id"]
                        )
                    )

                    st.rerun()

            st.divider()

    # ========================================================
    # EDIÇÃO DE RECEITA
    # ========================================================

    if "editar_receita" in st.session_state:

        receita_id = (
            st.session_state[
                "editar_receita"
            ]
        )

        receita = df_receitas[
            df_receitas["id"]
            == receita_id
        ]

        if not receita.empty:

            receita = receita.iloc[0]

            st.subheader(
                "✏️ Editar receita"
            )

            with st.form(
                "form_editar_receita"
            ):

                descricao = st.text_input(
                    "Descrição",
                    value=str(
                        receita["descricao"]
                    )
                )

                categoria = st.text_input(
                    "Categoria",
                    value=str(
                        receita["categoria"]
                    )
                )

                valor = st.number_input(
                    "Valor",
                    min_value=0.01,
                    value=float(
                        receita["valor"]
                    ),
                    step=10.0
                )

                data_original = (
                    receita["data"]
                )

                if pd.isna(
                    data_original
                ):

                    data_original = (
                        pd.Timestamp.today()
                    )

                data = st.date_input(
                    "Data",
                    value=data_original
                )

                col1, col2 = st.columns(2)

                with col1:

                    salvar = (
                        st.form_submit_button(
                            "💾 Salvar",
                            width="stretch"
                        )
                    )

                with col2:

                    cancelar = (
                        st.form_submit_button(
                            "Cancelar",
                            width="stretch"
                        )
                    )

                if salvar:

                    atualizar_receita(
                        receita_id,
                        descricao,
                        categoria,
                        valor,
                        data.strftime(
                            "%Y-%m-%d"
                        )
                    )

                    del st.session_state[
                        "editar_receita"
                    ]

                    st.success(
                        "Receita atualizada "
                        "com sucesso."
                    )

                    st.rerun()

                if cancelar:

                    del st.session_state[
                        "editar_receita"
                    ]

                    st.rerun()


# ============================================================
# DESPESAS
# ============================================================

elif pagina == "Despesas":

    st.title("💸 Despesas")

    if df_despesas.empty:

        st.info(
            "Nenhuma despesa cadastrada."
        )

    else:

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Total",
                formatar_moeda(
                    df_despesas["valor"].sum()
                )
            )

        with col2:

            st.metric(
                "Quantidade",
                len(df_despesas)
            )

        with col3:

            st.metric(
                "Maior despesa",
                formatar_moeda(
                    df_despesas["valor"].max()
                )
            )

        st.divider()

        categorias = [
            "Todas"
        ] + sorted(
            df_despesas[
                "categoria"
            ]
            .dropna()
            .unique()
            .tolist()
        )

        categoria_filtro = st.selectbox(
            "Filtrar por categoria",
            categorias
        )

        df_filtrado = df_despesas.copy()

        if categoria_filtro != "Todas":

            df_filtrado = df_filtrado[
                df_filtrado["categoria"]
                == categoria_filtro
            ]

        for _, despesa in df_filtrado.iterrows():

            col1, col2, col3, col4, col5, col6 = st.columns(
                [1.2, 2, 1.5, 1.3, 0.7, 0.7]
            )

            with col1:

                st.write(
                    formatar_data(
                        despesa["data"]
                    )
                )

            with col2:

                st.write(
                    despesa["descricao"]
                )

            with col3:

                st.write(
                    despesa["categoria"]
                )

            with col4:

                st.write(
                    formatar_moeda(
                        despesa["valor"]
                    )
                )

            with col5:

                if st.button(
                    "✏️",
                    key=(
                        f"editar_despesa_"
                        f"{despesa['id']}"
                    )
                ):

                    st.session_state[
                        "editar_despesa"
                    ] = int(
                        despesa["id"]
                    )

                    st.rerun()

            with col6:

                if st.button(
                    "🗑️",
                    key=(
                        f"excluir_despesa_"
                        f"{despesa['id']}"
                    )
                ):

                    st.session_state[
                        "confirmar_exclusao"
                    ] = (
                        "despesa",
                        int(
                            despesa["id"]
                        )
                    )

                    st.rerun()

            st.divider()

    # ========================================================
    # EDIÇÃO DE DESPESA
    # ========================================================

    if "editar_despesa" in st.session_state:

        despesa_id = (
            st.session_state[
                "editar_despesa"
            ]
        )

        despesa = df_despesas[
            df_despesas["id"]
            == despesa_id
        ]

        if not despesa.empty:

            despesa = despesa.iloc[0]

            st.subheader(
                "✏️ Editar despesa"
            )

            with st.form(
                "form_editar_despesa"
            ):

                descricao = st.text_input(
                    "Descrição",
                    value=str(
                        despesa["descricao"]
                    )
                )

                categoria = st.text_input(
                    "Categoria",
                    value=str(
                        despesa["categoria"]
                    )
                )

                valor = st.number_input(
                    "Valor",
                    min_value=0.01,
                    value=float(
                        despesa["valor"]
                    ),
                    step=10.0
                )

                data_original = (
                    despesa["data"]
                )

                if pd.isna(
                    data_original
                ):

                    data_original = (
                        pd.Timestamp.today()
                    )

                data = st.date_input(
                    "Data",
                    value=data_original
                )

                col1, col2 = st.columns(2)

                with col1:

                    salvar = (
                        st.form_submit_button(
                            "💾 Salvar",
                            width="stretch"
                        )
                    )

                with col2:

                    cancelar = (
                        st.form_submit_button(
                            "Cancelar",
                            width="stretch"
                        )
                    )

                if salvar:

                    atualizar_despesa(
                        despesa_id,
                        descricao,
                        categoria,
                        valor,
                        data.strftime(
                            "%Y-%m-%d"
                        )
                    )

                    del st.session_state[
                        "editar_despesa"
                    ]

                    st.success(
                        "Despesa atualizada "
                        "com sucesso."
                    )

                    st.rerun()

                if cancelar:

                    del st.session_state[
                        "editar_despesa"
                    ]

                    st.rerun()


# ============================================================
# METAS
# ============================================================

elif pagina == "Metas":

    st.title(
        "🎯 Metas financeiras"
    )

    st.subheader(
        "Criar nova meta"
    )

    with st.form(
        "form_nova_meta"
    ):

        nome = st.text_input(
            "Nome da meta"
        )

        valor_objetivo = st.number_input(
            "Valor objetivo",
            min_value=0.01,
            step=100.0
        )

        criar = st.form_submit_button(
            "Criar meta",
            width="stretch"
        )

        if criar:

            if not nome.strip():

                st.error(
                    "Digite o nome da meta."
                )

            else:

                salvar_meta(
                    nome,
                    valor_objetivo
                )

                st.success(
                    "Meta criada com sucesso."
                )

                st.rerun()

    st.divider()

    if df_metas.empty:

        st.info(
            "Nenhuma meta cadastrada."
        )

    else:

        for _, meta in df_metas.iterrows():

            percentual_meta = (
                meta["valor_atual"]
                /
                meta["valor_objetivo"]
                *
                100
                if meta["valor_objetivo"] > 0
                else 0
            )

            percentual_meta = min(
                percentual_meta,
                100
            )

            st.subheader(
                f"🎯 {meta['nome']}"
            )

            st.write(
                f"{formatar_moeda(meta['valor_atual'])} "
                f"de "
                f"{formatar_moeda(meta['valor_objetivo'])}"
            )

            st.progress(
                percentual_meta / 100
            )

            st.caption(
                f"{percentual_meta:.1f}% concluído"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                valor_adicionar = st.number_input(
                    "Adicionar valor",
                    min_value=0.0,
                    step=50.0,
                    key=(
                        f"valor_meta_"
                        f"{meta['id']}"
                    )
                )

            with col2:

                if st.button(
                    "💰 Adicionar",
                    key=(
                        f"adicionar_meta_"
                        f"{meta['id']}"
                    )
                ):

                    novo_valor = (
                        meta["valor_atual"]
                        +
                        valor_adicionar
                    )

                    atualizar_meta(
                        int(meta["id"]),
                        novo_valor
                    )

                    st.success(
                        "Valor adicionado "
                        "à meta."
                    )

                    st.rerun()

            with col3:

                if st.button(
                    "🗑️ Excluir",
                    key=(
                        f"excluir_meta_"
                        f"{meta['id']}"
                    )
                ):

                    st.session_state[
                        "confirmar_exclusao"
                    ] = (
                        "meta",
                        int(meta["id"])
                    )

                    st.rerun()

            st.divider()


# ============================================================
# RELATÓRIOS
# ============================================================

elif pagina == "Relatórios":

    mostrar_relatorios(
        df_receitas,
        df_despesas
    )

    st.divider()

    st.subheader(
        "🤖 Automação de Relatórios"
    )

    st.caption(
        "Gere automaticamente relatórios "
        "com os dados atuais do FinPilot."
    )

    if st.button(
        "🤖 Gerar relatório automaticamente",
        type="primary",
        width="stretch"
    ):

        try:

            resultado = (
                gerar_relatorio_automatico()
            )

            caminho_excel = (
                resultado["excel"]
            )

            caminho_csv = (
                resultado["csv"]
            )

            st.session_state[
                "relatorios_gerados"
            ] = {
                "excel": caminho_excel,
                "csv": caminho_csv
            }

            st.success(
                "✅ Relatórios gerados "
                "com sucesso!"
            )

        except Exception as erro:

            st.error(
                f"❌ Erro ao gerar relatórios: {erro}"
            )

    if "relatorios_gerados" in st.session_state:

        relatorios = (
            st.session_state[
                "relatorios_gerados"
            ]
        )

        st.write(
            "📊 Seus relatórios estão prontos:"
        )

        caminho_excel = Path(
            relatorios["excel"]
        )

        caminho_csv = Path(
            relatorios["csv"]
        )

        col1, col2 = st.columns(2)

        with col1:

            if caminho_excel.exists():

                with open(
                    caminho_excel,
                    "rb"
                ) as arquivo:

                    st.download_button(
                        label="📗 Baixar relatório Excel",
                        data=arquivo.read(),
                        file_name=caminho_excel.name,
                        mime=(
                            "application/"
                            "vnd.openxmlformats-officedocument."
                            "spreadsheetml.sheet"
                        ),
                        width="stretch"
                    )

        with col2:

            if caminho_csv.exists():

                with open(
                    caminho_csv,
                    "rb"
                ) as arquivo:

                    st.download_button(
                        label="📄 Baixar relatório CSV",
                        data=arquivo.read(),
                        file_name=caminho_csv.name,
                        mime="text/csv",
                        width="stretch"
                    )


# ============================================================
# IMPORTAR EXTRATO
# ============================================================

elif pagina == "📥 Importar Extrato":

    st.title("📥 Importar Extrato")

    st.caption(
        "Importe seus lançamentos financeiros "
        "automaticamente a partir de arquivos CSV ou Excel."
    )

    st.divider()

    # --------------------------------------------------------
    # INFORMAÇÕES
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.info(
            "📄 O arquivo precisa conter as colunas: "
            "**data**, **descricao** e **valor**."
        )

    with col2:

        st.info(
            "🤖 O FinPilot identifica automaticamente "
            "receitas, despesas e categorias."
        )

    st.divider()

    # --------------------------------------------------------
    # UPLOAD
    # --------------------------------------------------------

    arquivo = st.file_uploader(
        "Escolha seu extrato",
        type=["csv", "xlsx"],
        help=(
            "Formatos aceitos: CSV e Excel (.xlsx)"
        )
    )

    if arquivo is not None:

        st.success(
            f"📄 Arquivo selecionado: **{arquivo.name}**"
        )

        extensao = Path(
            arquivo.name
        ).suffix.lower()

        # ----------------------------------------------------
        # SALVA TEMPORARIAMENTE O ARQUIVO
        # ----------------------------------------------------

        try:

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=extensao
            ) as arquivo_temporario:

                arquivo_temporario.write(
                    arquivo.getbuffer()
                )

                caminho_temporario = (
                    arquivo_temporario.name
                )

            # ------------------------------------------------
            # PROCESSAMENTO
            # ------------------------------------------------

            dados_importacao = processar_csv(
                caminho_temporario
            )

            # ------------------------------------------------
            # REMOVE ARQUIVO TEMPORÁRIO
            # ------------------------------------------------

            try:

                Path(
                    caminho_temporario
                ).unlink()

            except Exception:

                pass

            if dados_importacao is None:

                st.error(
                    "❌ Não foi possível processar "
                    "o arquivo."
                )

            elif dados_importacao.empty:

                st.warning(
                    "⚠️ Nenhum lançamento válido "
                    "foi encontrado no arquivo."
                )

            else:

                st.subheader(
                    "📋 Pré-visualização"
                )

                # --------------------------------------------
                # MÉTRICAS
                # --------------------------------------------

                total_importacao = len(
                    dados_importacao
                )

                total_receitas_importacao = len(
                    dados_importacao[
                        dados_importacao["tipo"]
                        == "receita"
                    ]
                )

                total_despesas_importacao = len(
                    dados_importacao[
                        dados_importacao["tipo"]
                        == "despesa"
                    ]
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "📊 Lançamentos",
                        total_importacao
                    )

                with col2:

                    st.metric(
                        "💰 Receitas",
                        total_receitas_importacao
                    )

                with col3:

                    st.metric(
                        "💸 Despesas",
                        total_despesas_importacao
                    )

                st.divider()

                # --------------------------------------------
                # TABELA
                # --------------------------------------------

                tabela_preview = (
                    dados_importacao[
                        [
                            "data",
                            "descricao",
                            "valor",
                            "tipo"
                        ]
                    ]
                    .copy()
                )

                tabela_preview["data"] = (
                    tabela_preview["data"]
                    .dt.strftime("%d/%m/%Y")
                )

                tabela_preview["tipo"] = (
                    tabela_preview["tipo"]
                    .replace({
                        "receita": "Receita",
                        "despesa": "Despesa"
                    })
                )

                tabela_preview["valor"] = (
                    tabela_preview["valor"]
                    .map(formatar_moeda)
                )

                tabela_preview.columns = [
                    "Data",
                    "Descrição",
                    "Valor",
                    "Tipo"
                ]

                st.dataframe(
                    tabela_preview,
                    width="stretch",
                    hide_index=True
                )

                st.divider()

                # --------------------------------------------
                # CATEGORIZAÇÃO
                # --------------------------------------------

                st.subheader(
                    "🏷️ Categorização automática"
                )

                categorias_preview = (
                    dados_importacao[
                        ["descricao", "tipo"]
                    ]
                    .copy()
                )

                categorias_preview["categoria"] = (
                    dados_importacao["descricao"]
                    .apply(
                        lambda descricao:
                        __import__(
                            "importador"
                        ).categorizar_lancamento(
                            descricao
                        )
                    )
                )

                categorias_preview["tipo"] = (
                    categorias_preview["tipo"]
                    .replace({
                        "receita": "Receita",
                        "despesa": "Despesa"
                    })
                )

                categorias_preview.columns = [
                    "Descrição",
                    "Tipo",
                    "Categoria"
                ]

                st.dataframe(
                    categorias_preview,
                    width="stretch",
                    hide_index=True
                )

                st.divider()

                # --------------------------------------------
                # BOTÃO DE IMPORTAÇÃO
                # --------------------------------------------

                st.subheader(
                    "🚀 Importar para o FinPilot"
                )

                st.write(
                    "O FinPilot verificará automaticamente "
                    "se os lançamentos já existem no banco "
                    "de dados antes de salvá-los."
                )

                if st.button(
                    "🚀 Importar lançamentos",
                    type="primary",
                    width="stretch"
                ):

                    resultado = salvar_lancamentos(
                        dados_importacao
                    )

                    st.session_state[
                        "resultado_importacao"
                    ] = resultado

                    st.rerun()

        except Exception as erro:

            st.error(
                f"❌ Erro ao processar arquivo: {erro}"
            )


# ============================================================
# RESULTADO DA IMPORTAÇÃO
# ============================================================

if "resultado_importacao" in st.session_state:

    resultado = (
        st.session_state[
            "resultado_importacao"
        ]
    )

    st.divider()

    st.subheader(
        "✅ Importação concluída"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "🆕 Novos lançamentos",
            resultado["novos"]
        )

    with col2:

        st.metric(
            "🔁 Duplicados",
            resultado["duplicados"]
        )

    with col3:

        st.metric(
            "🏷️ Categorias atualizadas",
            resultado[
                "categorias_atualizadas"
            ]
        )

    if resultado["novos"] > 0:

        st.success(
            f"🎉 {resultado['novos']} "
            "novos lançamentos foram adicionados."
        )

    elif resultado["duplicados"] > 0:

        st.info(
            "ℹ️ Todos os lançamentos enviados "
            "já estavam registrados no FinPilot."
        )

    detalhes = resultado.get(
        "detalhes"
    )

    if (
        detalhes is not None
        and not detalhes.empty
    ):

        st.subheader(
            "📋 Resultado dos lançamentos"
        )

        st.dataframe(
            detalhes,
            width="stretch",
            hide_index=True
        )

    if st.button(
        "✖️ Fechar resultado"
    ):

        del st.session_state[
            "resultado_importacao"
        ]

        st.rerun()


# ============================================================
# INSIGHTS
# ============================================================

if pagina == "Insights":

    st.title(
        "🤖 Insights financeiros"
    )

    st.caption(
        "Análises automáticas baseadas "
        "nos seus dados."
    )

    if total_receitas == 0:

        st.info(
            "Cadastre receitas para gerar insights."
        )

    else:

        if percentual >= 90:

            st.warning(
                "⚠️ Suas despesas estão consumindo "
                "uma parcela muito alta da sua renda."
            )

        elif percentual >= 70:

            st.warning(
                "⚠️ Mais de 70% da sua renda está "
                "comprometida com despesas."
            )

        else:

            st.success(
                "✅ Suas despesas estão abaixo "
                "de 70% da sua renda."
            )

        if saldo > 0:

            st.success(
                f"💰 Você possui um saldo positivo "
                f"de {formatar_moeda(saldo)}."
            )

        elif saldo < 0:

            st.error(
                f"🚨 Suas despesas ultrapassaram "
                f"suas receitas em "
                f"{formatar_moeda(abs(saldo))}."
            )

        else:

            st.info(
                "Seu saldo está zerado."
            )

        if not df_despesas.empty:

            categoria_maior = (
                df_despesas
                .groupby("categoria")["valor"]
                .sum()
                .idxmax()
            )

            valor_categoria = (
                df_despesas
                .groupby("categoria")["valor"]
                .sum()
                .max()
            )

            st.info(
                f"🏷️ Sua maior categoria de "
                f"despesas é **{categoria_maior}**, "
                f"com "
                f"{formatar_moeda(valor_categoria)}."
            )


# ============================================================
# CONFIRMAÇÃO DE EXCLUSÃO
# ============================================================

if "confirmar_exclusao" in st.session_state:

    tipo, item_id = (
        st.session_state[
            "confirmar_exclusao"
        ]
    )

    st.warning(
        "⚠️ Tem certeza que deseja "
        "excluir este lançamento?"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Sim, excluir",
            width="stretch"
        ):

            if tipo == "receita":

                excluir_receita(
                    item_id
                )

            elif tipo == "despesa":

                excluir_despesa(
                    item_id
                )

            elif tipo == "meta":

                excluir_meta(
                    item_id
                )

            del st.session_state[
                "confirmar_exclusao"
            ]

            st.success(
                "Registro excluído "
                "com sucesso."
            )

            st.rerun()

    with col2:

        if st.button(
            "Cancelar",
            width="stretch"
        ):

            del st.session_state[
                "confirmar_exclusao"
            ]

            st.rerun()