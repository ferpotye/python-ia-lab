import pandas as pd
from pathlib import Path

from database import (
    salvar_receita,
    salvar_despesa,
    receita_existe,
    despesa_existe,
    atualizar_categoria_receita,
    atualizar_categoria_despesa
)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

COLUNAS_OBRIGATORIAS = [
    "data",
    "descricao",
    "valor"
]


# ============================================================
# LEITURA DO CSV / EXCEL
# ============================================================

def importar_arquivo(caminho):

    try:

        extensao = Path(caminho).suffix.lower()

        if extensao == ".csv":

            df = pd.read_csv(caminho)

        elif extensao == ".xlsx":

            df = pd.read_excel(
                caminho,
                engine="openpyxl"
            )

        else:

            print(
                "❌ Formato de arquivo não suportado."
            )

            return None

        # ----------------------------------------------------
        # NORMALIZAÇÃO DOS NOMES DAS COLUNAS
        # ----------------------------------------------------

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.lower()
        )

        print(
            "📋 Colunas encontradas:",
            list(df.columns)
        )

        return df

    except Exception as erro:

        print(
            f"❌ Erro ao importar arquivo: {erro}"
        )

        return None


# ============================================================
# VALIDAÇÃO
# ============================================================

def validar_csv(df):

    if df is None:

        return False

    for coluna in COLUNAS_OBRIGATORIAS:

        if coluna not in df.columns:

            print(
                f"❌ Coluna obrigatória "
                f"não encontrada: {coluna}"
            )

            return False

    return True


# ============================================================
# CLASSIFICAÇÃO
# ============================================================

def classificar_lancamentos(df):

    df = df.copy()

    # --------------------------------------------------------
    # CONVERSÃO DA DATA
    # --------------------------------------------------------

    df["data"] = pd.to_datetime(
        df["data"],
        dayfirst=True
    )

    # --------------------------------------------------------
    # IDENTIFICAÇÃO DO TIPO
    # --------------------------------------------------------

    df["tipo"] = df["valor"].apply(
        lambda valor:
        "receita"
        if valor > 0
        else "despesa"
    )

    # --------------------------------------------------------
    # TRANSFORMA DESPESAS EM VALORES POSITIVOS
    # --------------------------------------------------------

    df["valor"] = df["valor"].abs()

    return df


# ============================================================
# CATEGORIZAÇÃO AUTOMÁTICA
# ============================================================

def categorizar_lancamento(descricao):

    descricao = descricao.lower()

    categorias = {

        "moradia": [
            "aluguel",
            "condominio",
            "condomínio",
            "energia",
            "luz",
            "água",
            "agua",
            "gás",
            "gas"
        ],

        "alimentação": [
            "mercado",
            "supermercado",
            "ifood",
            "restaurante",
            "lanche",
            "padaria"
        ],

        "transporte": [
            "uber",
            "99",
            "combustível",
            "combustivel",
            "gasolina",
            "estacionamento"
        ],

        "lazer": [
            "netflix",
            "spotify",
            "cinema",
            "prime video",
            "disney"
        ],

        "saúde": [
            "farmácia",
            "farmacia",
            "médico",
            "medico",
            "hospital",
            "consulta"
        ],

        "trabalho": [
            "salário",
            "salario",
            "freelance",
            "pagamento",
            "comissão",
            "comissao"
        ]
    }

    for categoria, palavras in categorias.items():

        for palavra in palavras:

            if palavra in descricao:

                return categoria

    return "outros"


# ============================================================
# PROCESSAMENTO
# ============================================================

def processar_csv(caminho):

    df = importar_arquivo(caminho)

    if not validar_csv(df):

        return None

    df = classificar_lancamentos(df)

    return df


# ============================================================
# SALVAR E ATUALIZAR LANÇAMENTOS
# ============================================================

def salvar_lancamentos(df):

    novos = 0
    duplicados = 0
    categorias_atualizadas = 0

    for _, linha in df.iterrows():

        data = linha["data"]
        descricao = linha["descricao"]
        valor = linha["valor"]
        tipo = linha["tipo"]

        # ----------------------------------------------------
        # CONVERTE DATA PARA TEXTO
        # ----------------------------------------------------

        data = data.strftime("%Y-%m-%d")

        # ----------------------------------------------------
        # CATEGORIZAÇÃO
        # ----------------------------------------------------

        categoria = categorizar_lancamento(
            descricao
        )

        # ----------------------------------------------------
        # RECEITA
        # ----------------------------------------------------

        if tipo == "receita":

            if receita_existe(
                descricao,
                valor,
                data
            ):

                atualizar_categoria_receita(
                    descricao,
                    categoria
                )

                duplicados += 1
                categorias_atualizadas += 1

                continue

            salvar_receita(
                descricao,
                categoria,
                valor,
                data
            )

            novos += 1

        # ----------------------------------------------------
        # DESPESA
        # ----------------------------------------------------

        else:

            if despesa_existe(
                descricao,
                valor,
                data
            ):

                atualizar_categoria_despesa(
                    descricao,
                    categoria
                )

                duplicados += 1
                categorias_atualizadas += 1

                continue

            salvar_despesa(
                descricao,
                categoria,
                valor,
                data
            )

            novos += 1

    # --------------------------------------------------------
    # RESULTADO
    # --------------------------------------------------------

    print()

    print(
        f"✅ Novos lançamentos salvos: {novos}"
    )

    print(
        f"🔁 Lançamentos já existentes: {duplicados}"
    )

    print(
        f"🏷️ Categorias atualizadas: "
        f"{categorias_atualizadas}"
    )


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    print("🤖 Importador FinPilot")
    print()

    pasta_projeto = Path(__file__).resolve().parent

    arquivo = pasta_projeto / "extrato_excel_teste.xlsx"

    print()
    print("📂 Arquivo utilizado:")
    print(arquivo)

    dados = processar_csv(arquivo)

    if dados is not None:

        print()
        print("✅ Arquivo importado com sucesso!")
        print()

        print(dados)

        print()
        print("📊 Resumo:")

        print(
            f"Total de lançamentos: {len(dados)}"
        )

        print(
            f"Receitas: "
            f"{len(dados[dados['tipo'] == 'receita'])}"
        )

        print(
            f"Despesas: "
            f"{len(dados[dados['tipo'] == 'despesa'])}"
        )

        print()
        print("🏷️ Categorização automática:")
        print()

        print(
            dados[["descricao", "tipo"]].assign(
                categoria=dados["descricao"].apply(
                    categorizar_lancamento
                )
            )
        )

        print()
        print("💾 Salvando lançamentos...")

        salvar_lancamentos(dados)