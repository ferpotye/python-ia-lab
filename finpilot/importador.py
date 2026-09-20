import pandas as pd
import unicodedata
from pathlib import Path

from database import (
    salvar_receita,
    salvar_despesa,
    receita_existe,
    despesa_existe,
    atualizar_categoria_receita,
    atualizar_categoria_despesa,
)


COLUNAS_OBRIGATORIAS = ["data", "descricao", "valor"]


# ============================================================
# NORMALIZAÇÃO DE TEXTO
# ============================================================

def normalizar_texto(texto):
    """
    Normaliza textos para facilitar a categorização.

    Exemplos:
    Farmácia -> farmacia
    SALÁRIO -> salario
    "  Uber  " -> uber
    """

    texto = str(texto).strip().lower()

    texto = unicodedata.normalize("NFKD", texto)

    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )

    return texto


# ============================================================
# REGRAS DE CATEGORIZAÇÃO
# ============================================================

REGRAS_CATEGORIAS = {

    "moradia": [
        "aluguel",
        "condominio",
        "energia",
        "enel",
        "cpfl",
        "cemig",
        "light",
        "luz",
        "sabesp",
        "agua",
        "saneamento",
        "gas",
        "naturgy",
        "comgas",
        "vivo fibra",
        "claro internet",
        "tim fibra",
        "telefone",
        "internet",
    ],

    "alimentação": [
        "mercado",
        "supermercado",
        "carrefour",
        "atacadao",
        "pao de acucar",
        "assai",
        "extra",
        "dia supermercado",
        "ifood",
        "rappi",
        "uber eats",
        "restaurante",
        "lanchonete",
        "lanche",
        "padaria",
        "pizzaria",
        "hamburguer",
        "burger",
        "mcdonald",
        "subway",
        "habibs",
        "bk",
        "outback",
    ],

    "transporte": [
        "uber",
        "99",
        "99pop",
        "combustivel",
        "gasolina",
        "etanol",
        "alcool",
        "shell",
        "ipiranga",
        "br distribuidora",
        "posto",
        "estacionamento",
        "sem parar",
        "pedagio",
        "metro",
        "trem",
        "onibus",
        "bilhete unico",
    ],

    "lazer": [
        "netflix",
        "spotify",
        "prime video",
        "amazon prime",
        "disney",
        "disney+",
        "hbo",
        "hbo max",
        "max",
        "paramount",
        "globoplay",
        "youtube premium",
        "cinema",
        "ingresso",
        "teatro",
        "show",
        "steam",
        "playstation",
        "xbox",
        "nintendo",
        "jogo",
        "games",
    ],

    "saúde": [
        "farmacia",
        "drogasil",
        "droga raia",
        "pague menos",
        "drogaria",
        "hospital",
        "clinica",
        "medico",
        "consulta",
        "laboratorio",
        "exame",
        "dentista",
        "odontologia",
        "plano de saude",
        "unimed",
        "amil",
        "bradesco saude",
    ],

    "trabalho": [
        "salario",
        "freelance",
        "pagamento",
        "comissao",
        "bonus",
        "premio",
        "pro labore",
        "vale alimentacao",
        "vale refeicao",
        "beneficio",
    ],

    "educação": [
        "faculdade",
        "universidade",
        "escola",
        "curso",
        "udemy",
        "alura",
        "coursera",
        "descomplica",
        "livro",
        "livraria",
        "material escolar",
    ],

    "compras": [
        "amazon",
        "mercado livre",
        "mercadolivre",
        "magalu",
        "magazine luiza",
        "shopee",
        "shein",
        "renner",
        "riachuelo",
        "cea",
        "c&a",
        "zattini",
        "loja",
        "shopping",
        "roupa",
        "calcado",
        "sapato",
        "eletronico",
    ],

    "serviços": [
        "servico",
        "manutencao",
        "conserto",
        "assistencia tecnica",
        "faxina",
        "diarista",
        "cabeleireiro",
        "barbearia",
        "salao",
        "manicure",
        "pedicure",
    ],
}


# ============================================================
# CATEGORIZAÇÃO AUTOMÁTICA
# ============================================================

def categorizar_lancamento(descricao):
    """
    Identifica automaticamente a categoria de um lançamento.
    """

    descricao_normalizada = normalizar_texto(descricao)

    for categoria, palavras_chave in REGRAS_CATEGORIAS.items():

        for palavra in palavras_chave:

            palavra_normalizada = normalizar_texto(palavra)

            if palavra_normalizada in descricao_normalizada:
                return categoria

    return "outros"


# ============================================================
# IMPORTAÇÃO DO ARQUIVO
# ============================================================

def importar_arquivo(caminho):
    """
    Importa arquivos CSV ou XLSX.
    """

    caminho = Path(caminho)

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    extensao = caminho.suffix.lower()

    if extensao == ".csv":

        df = pd.read_csv(caminho)

    elif extensao == ".xlsx":

        df = pd.read_excel(
            caminho,
            engine="openpyxl"
        )

    else:

        raise ValueError(
            "Formato não suportado. "
            "Utilize CSV ou XLSX."
        )

    df.columns = [
        str(coluna).strip().lower()
        for coluna in df.columns
    ]

    return df


# ============================================================
# VALIDAÇÃO
# ============================================================

def validar_csv(df):

    colunas_faltantes = [
        coluna
        for coluna in COLUNAS_OBRIGATORIAS
        if coluna not in df.columns
    ]

    if colunas_faltantes:

        raise ValueError(
            "Colunas obrigatórias ausentes: "
            + ", ".join(colunas_faltantes)
        )

    return True


# ============================================================
# CLASSIFICAÇÃO DOS LANÇAMENTOS
# ============================================================

def classificar_lancamentos(df):

    df = df.copy()

    df["data"] = pd.to_datetime(
        df["data"],
        dayfirst=True,
        errors="coerce"
    )

    df["valor"] = pd.to_numeric(
        df["valor"],
        errors="coerce"
    )

    df["descricao"] = (
        df["descricao"]
        .astype(str)
        .str.strip()
    )

    df = df.dropna(
        subset=[
            "data",
            "descricao",
            "valor"
        ]
    )

    df["tipo"] = df["valor"].apply(
        lambda valor:
        "receita"
        if valor > 0
        else "despesa"
    )

    df["valor"] = df["valor"].abs()

    df["categoria"] = df["descricao"].apply(
        categorizar_lancamento
    )

    return df


# ============================================================
# PROCESSAMENTO COMPLETO
# ============================================================

def processar_csv(caminho):

    df = importar_arquivo(caminho)

    validar_csv(df)

    df = classificar_lancamentos(df)

    return df


# ============================================================
# SALVAMENTO NO BANCO
# ============================================================

def salvar_lancamentos(df):

    novos = 0
    duplicados = 0
    categorias_atualizadas = 0

    detalhes = []

    for _, linha in df.iterrows():

        data = linha["data"].strftime("%Y-%m-%d")

        descricao = str(
            linha["descricao"]
        ).strip()

        valor = float(
            linha["valor"]
        )

        tipo = linha["tipo"]

        categoria = categorizar_lancamento(
            descricao
        )

        # ----------------------------------------------------
        # RECEITA
        # ----------------------------------------------------

        if tipo == "receita":

            existe = receita_existe(
                descricao,
                valor,
                data
            )

            if existe:

                atualizar_categoria_receita(
                    descricao,
                    categoria
                )

                duplicados += 1
                categorias_atualizadas += 1

                status = "Duplicado"

            else:

                salvar_receita(
                    descricao,
                    categoria,
                    valor,
                    data
                )

                novos += 1

                status = "Novo"

        # ----------------------------------------------------
        # DESPESA
        # ----------------------------------------------------

        else:

            existe = despesa_existe(
                descricao,
                valor,
                data
            )

            if existe:

                atualizar_categoria_despesa(
                    descricao,
                    categoria
                )

                duplicados += 1
                categorias_atualizadas += 1

                status = "Duplicado"

            else:

                salvar_despesa(
                    descricao,
                    categoria,
                    valor,
                    data
                )

                novos += 1

                status = "Novo"

        detalhes.append(
            {
                "descricao": descricao,
                "tipo": (
                    "Receita"
                    if tipo == "receita"
                    else "Despesa"
                ),
                "categoria": categoria,
                "status": status,
            }
        )

    return {
        "novos": novos,
        "duplicados": duplicados,
        "categorias_atualizadas": categorias_atualizadas,
        "total": len(df),
        "detalhes": pd.DataFrame(detalhes),
    }


# ============================================================
# TESTE DO MÓDULO
# ============================================================

if __name__ == "__main__":

    caminho = (
        Path(__file__).parent
        / "extrato_excel_teste.xlsx"
    )

    print("\n📂 Arquivo utilizado:")
    print(caminho)

    dados = processar_csv(caminho)

    print("\n✅ Arquivo importado com sucesso!\n")

    print(
        dados[
            [
                "data",
                "descricao",
                "valor",
                "tipo",
                "categoria",
            ]
        ]
    )

    print("\n📊 Resumo:")

    print(
        f"Total de lançamentos: {len(dados)}"
    )

    print(
        "Receitas:",
        len(
            dados[
                dados["tipo"] == "receita"
            ]
        )
    )

    print(
        "Despesas:",
        len(
            dados[
                dados["tipo"] == "despesa"
            ]
        )
    )

    print("\n🏷️ Categorização automática:")

    print(
        dados[
            [
                "descricao",
                "tipo",
                "categoria",
            ]
        ]
    )

    print("\n💾 Salvando lançamentos...")

    resultado = salvar_lancamentos(
        dados
    )

    print(
        "\n📊 Resultado da importação:"
    )

    print(
        f"Novos: {resultado['novos']}"
    )

    print(
        f"Duplicados: {resultado['duplicados']}"
    )

    print(
        "Categorias atualizadas:",
        resultado["categorias_atualizadas"]
    )