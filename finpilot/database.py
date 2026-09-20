import sqlite3
from pathlib import Path


# ============================================================
# CONFIGURAÇÃO DO BANCO
# ============================================================

CAMINHO_BANCO = Path(__file__).resolve().parent / "finpilot.db"


def conectar_banco():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    return conexao


# ============================================================
# CRIAÇÃO DAS TABELAS
# ============================================================

def criar_tabelas():

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS receitas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            categoria TEXT NOT NULL,
            valor REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS despesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            categoria TEXT NOT NULL,
            valor REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            valor_objetivo REAL NOT NULL,
            valor_atual REAL NOT NULL DEFAULT 0
        )
    """)

    conexao.commit()
    conexao.close()


# ============================================================
# ADICIONA COLUNA DE DATA
# ============================================================

def adicionar_coluna_data():

    conexao = conectar_banco()
    cursor = conexao.cursor()

    tabelas = [
        "receitas",
        "despesas"
    ]

    for tabela in tabelas:

        cursor.execute(
            f"PRAGMA table_info({tabela})"
        )

        colunas = [
            coluna[1]
            for coluna in cursor.fetchall()
        ]

        if "data" not in colunas:

            cursor.execute(
                f"""
                ALTER TABLE {tabela}
                ADD COLUMN data TEXT
                """
            )

    conexao.commit()
    conexao.close()


# ============================================================
# RECEITAS
# ============================================================

def receita_existe(
    descricao,
    valor,
    data=None
):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    if data is None:

        cursor.execute(
            """
            SELECT id
            FROM receitas
            WHERE descricao = ?
            AND valor = ?
            AND data IS NULL
            """,
            (
                descricao,
                valor
            )
        )

    else:

        cursor.execute(
            """
            SELECT id
            FROM receitas
            WHERE descricao = ?
            AND valor = ?
            AND data = ?
            """,
            (
                descricao,
                valor,
                data
            )
        )

    resultado = cursor.fetchone()

    conexao.close()

    return resultado is not None


def salvar_receita(
    descricao,
    categoria,
    valor,
    data=None
):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO receitas
        (
            descricao,
            categoria,
            valor,
            data
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            descricao,
            categoria,
            valor,
            data
        )
    )

    conexao.commit()
    conexao.close()


def buscar_receitas():

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            id,
            descricao,
            categoria,
            valor,
            data
        FROM receitas
        ORDER BY
            CASE
                WHEN data IS NULL THEN 1
                ELSE 0
            END,
            date(data) DESC,
            id DESC
        """
    )

    receitas = cursor.fetchall()

    conexao.close()

    return receitas


def atualizar_receita(
    receita_id,
    descricao,
    categoria,
    valor,
    data
):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        """
        UPDATE receitas
        SET
            descricao = ?,
            categoria = ?,
            valor = ?,
            data = ?
        WHERE id = ?
        """,
        (
            descricao,
            categoria,
            valor,
            data,
            receita_id
        )
    )

    conexao.commit()
    conexao.close()


def atualizar_categoria_receita(
    descricao,
    categoria
):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        """
        UPDATE receitas
        SET categoria = ?
        WHERE descricao = ?
        """,
        (
            categoria,
            descricao
        )
    )

    conexao.commit()
    conexao.close()


def excluir_receita(receita_id):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        """
        DELETE FROM receitas
        WHERE id = ?
        """,
        (receita_id,)
    )

    conexao.commit()
    conexao.close()


# ============================================================
# DESPESAS
# ============================================================

def despesa_existe(
    descricao,
    valor,
    data=None
):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    if data is None:

        cursor.execute(
            """
            SELECT id
            FROM despesas
            WHERE descricao = ?
            AND valor = ?
            AND data IS NULL
            """,
            (
                descricao,
                valor
            )
        )

    else:

        cursor.execute(
            """
            SELECT id
            FROM despesas
            WHERE descricao = ?
            AND valor = ?
            AND data = ?
            """,
            (
                descricao,
                valor,
                data
            )
        )

    resultado = cursor.fetchone()

    conexao.close()

    return resultado is not None


def salvar_despesa(
    descricao,
    categoria,
    valor,
    data=None
):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO despesas
        (
            descricao,
            categoria,
            valor,
            data
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            descricao,
            categoria,
            valor,
            data
        )
    )

    conexao.commit()
    conexao.close()


def buscar_despesas():

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            id,
            descricao,
            categoria,
            valor,
            data
        FROM despesas
        ORDER BY
            CASE
                WHEN data IS NULL THEN 1
                ELSE 0
            END,
            date(data) DESC,
            id DESC
        """
    )

    despesas = cursor.fetchall()

    conexao.close()

    return despesas


def atualizar_despesa(
    despesa_id,
    descricao,
    categoria,
    valor,
    data
):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        """
        UPDATE despesas
        SET
            descricao = ?,
            categoria = ?,
            valor = ?,
            data = ?
        WHERE id = ?
        """,
        (
            descricao,
            categoria,
            valor,
            data,
            despesa_id
        )
    )

    conexao.commit()
    conexao.close()


def atualizar_categoria_despesa(
    descricao,
    categoria
):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        """
        UPDATE despesas
        SET categoria = ?
        WHERE descricao = ?
        """,
        (
            categoria,
            descricao
        )
    )

    conexao.commit()
    conexao.close()


def excluir_despesa(despesa_id):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        """
        DELETE FROM despesas
        WHERE id = ?
        """,
        (despesa_id,)
    )

    conexao.commit()
    conexao.close()


# ============================================================
# METAS
# ============================================================

def salvar_meta(
    nome,
    valor_objetivo,
    valor_atual=0
):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO metas
        (
            nome,
            valor_objetivo,
            valor_atual
        )
        VALUES (?, ?, ?)
        """,
        (
            nome,
            valor_objetivo,
            valor_atual
        )
    )

    conexao.commit()
    conexao.close()


def buscar_metas():

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            id,
            nome,
            valor_objetivo,
            valor_atual
        FROM metas
        ORDER BY id DESC
        """
    )

    metas = cursor.fetchall()

    conexao.close()

    return metas


def atualizar_meta(
    meta_id,
    valor_atual
):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        """
        UPDATE metas
        SET valor_atual = ?
        WHERE id = ?
        """,
        (
            valor_atual,
            meta_id
        )
    )

    conexao.commit()
    conexao.close()


def excluir_meta(meta_id):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        """
        DELETE FROM metas
        WHERE id = ?
        """,
        (meta_id,)
    )

    conexao.commit()
    conexao.close()


# ============================================================
# INICIALIZAÇÃO
# ============================================================

criar_tabelas()
adicionar_coluna_data()

print("🗄️ Banco de dados conectado!")
print(f"📁 Local: {CAMINHO_BANCO}")