import ollama


MODELO = "qwen2.5:3b"


# ============================================================
# IA LOCAL
# ============================================================

def perguntar_ia(prompt):
    """
    Envia um prompt para o modelo local
    executado pelo Ollama.
    """

    resposta = ollama.chat(
        model=MODELO,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return resposta["message"]["content"]


# ============================================================
# CONTEXTO FINANCEIRO
# ============================================================

def construir_contexto_financeiro(
    df_receitas,
    df_despesas,
    df_metas=None
):
    """
    Constrói um resumo estruturado dos dados financeiros
    para ser utilizado pela IA.
    """

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

    percentual_comprometido = (
        (total_despesas / total_receitas) * 100
        if total_receitas > 0
        else 0
    )

    contexto = f"""
DADOS FINANCEIROS DO FINPILOT

Total de receitas:
R$ {total_receitas:.2f}

Total de despesas:
R$ {total_despesas:.2f}

Saldo:
R$ {saldo:.2f}

Percentual da renda comprometida:
{percentual_comprometido:.1f}%

Quantidade de receitas:
{len(df_receitas)}

Quantidade de despesas:
{len(df_despesas)}
"""

    # --------------------------------------------------------
    # GASTOS POR CATEGORIA
    # --------------------------------------------------------

    if not df_despesas.empty:

        gastos_categoria = (
            df_despesas
            .groupby("categoria")["valor"]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        contexto += (
            "\nGASTOS POR CATEGORIA:\n"
        )

        for categoria, valor in gastos_categoria.items():

            percentual_categoria = (
                (valor / total_despesas) * 100
                if total_despesas > 0
                else 0
            )

            contexto += (
                f"- {categoria}: "
                f"R$ {valor:.2f} "
                f"({percentual_categoria:.1f}%)\n"
            )

    # --------------------------------------------------------
    # MAIORES DESPESAS
    # --------------------------------------------------------

    if not df_despesas.empty:

        maiores_despesas = (
            df_despesas
            .sort_values(
                "valor",
                ascending=False
            )
            .head(5)
        )

        contexto += (
            "\nMAIORES DESPESAS:\n"
        )

        for _, despesa in maiores_despesas.iterrows():

            contexto += (
                f"- {despesa['descricao']}: "
                f"R$ {despesa['valor']:.2f} "
                f"({despesa['categoria']})\n"
            )

    # --------------------------------------------------------
    # METAS
    # --------------------------------------------------------

    if (
        df_metas is not None
        and not df_metas.empty
    ):

        contexto += (
            "\nMETAS FINANCEIRAS:\n"
        )

        for _, meta in df_metas.iterrows():

            objetivo = meta["valor_objetivo"]
            atual = meta["valor_atual"]

            progresso = (
                (atual / objetivo) * 100
                if objetivo > 0
                else 0
            )

            contexto += (
                f"- {meta['nome']}: "
                f"R$ {atual:.2f} "
                f"de R$ {objetivo:.2f} "
                f"({progresso:.1f}%)\n"
            )

    return contexto


# ============================================================
# HISTÓRICO DA CONVERSA
# ============================================================

def construir_historico_conversa(
    historico
):
    """
    Converte o histórico da conversa em texto
    para fornecer contexto ao modelo.
    """

    if not historico:

        return (
            "HISTÓRICO DA CONVERSA:\n"
            "Nenhuma conversa anterior."
        )

    contexto = (
        "HISTÓRICO DA CONVERSA:\n"
    )

    for mensagem in historico:

        contexto += (
            f"{mensagem['papel']}: "
            f"{mensagem['conteudo']}\n"
        )

    return contexto


# ============================================================
# PROMPT CONVERSACIONAL
# ============================================================

def criar_prompt_financeiro(
    pergunta,
    df_receitas,
    df_despesas,
    df_metas=None,
    historico=None
):
    """
    Cria o prompt completo utilizado pelo
    assistente financeiro conversacional.

    V4.6:
    - dados financeiros;
    - metas;
    - histórico da conversa;
    - pergunta atual.
    """

    contexto_financeiro = (
        construir_contexto_financeiro(
            df_receitas,
            df_despesas,
            df_metas
        )
    )

    contexto_historico = (
        construir_historico_conversa(
            historico
        )
    )

    prompt = f"""
Você é o assistente financeiro inteligente do FinPilot.

O FinPilot é um sistema de controle financeiro pessoal
que utiliza inteligência artificial local para ajudar
o usuário a compreender seus próprios dados financeiros.

{contexto_financeiro}

{contexto_historico}

PERGUNTA ATUAL DO USUÁRIO:

{pergunta}

REGRAS IMPORTANTES:

1. Responda sempre em português do Brasil.
2. Responda diretamente à pergunta atual.
3. Utilize somente os dados fornecidos.
4. Considere o histórico da conversa quando ele ajudar
   a compreender perguntas de continuidade.
5. Nunca invente valores, transações, categorias ou datas.
6. Se os dados forem insuficientes, diga claramente.
7. Sempre que possível, utilize valores em reais.
8. Seja objetivo, claro e fácil de entender.
9. Pode utilizar pequenos títulos e listas quando ajudarem.
10. Não faça diagnóstico financeiro profissional.
11. Não faça promessas de resultados financeiros.
12. Não recomende investimentos específicos.
13. Não assuma informações que não estejam nos dados.
14. Se a pergunta não puder ser respondida pelos dados
    disponíveis, explique essa limitação.

Seu objetivo é ajudar o usuário a compreender melhor
a própria situação financeira.

Responda agora à pergunta do usuário.
"""

    return prompt


# ============================================================
# TESTE DO MÓDULO
# ============================================================

if __name__ == "__main__":

    import pandas as pd

    receitas = pd.DataFrame({
        "valor": [3900, 800],
        "categoria": [
            "trabalho",
            "trabalho"
        ]
    })

    despesas = pd.DataFrame({
        "valor": [
            1200,
            450,
            180,
            50,
            120,
            90
        ],
        "categoria": [
            "moradia",
            "alimentação",
            "transporte",
            "lazer",
            "moradia",
            "saúde"
        ],
        "descricao": [
            "Aluguel",
            "Supermercado",
            "Combustível",
            "Cinema",
            "Condomínio",
            "Farmácia"
        ]
    })

    metas = pd.DataFrame({
        "nome": [
            "Reserva de emergência"
        ],
        "valor_objetivo": [
            5000
        ],
        "valor_atual": [
            1500
        ]
    })

    historico = [
        {
            "papel": "Usuário",
            "conteudo": "Onde estou gastando mais?"
        },
        {
            "papel": "FinPilot",
            "conteudo": (
                "Você está gastando mais "
                "com moradia."
            )
        }
    ]

    pergunta = (
        "E quanto foi nessa categoria?"
    )

    prompt = criar_prompt_financeiro(
        pergunta,
        receitas,
        despesas,
        metas,
        historico
    )

    print(
        "\n📊 PROMPT ENVIADO PARA A IA:\n"
    )

    print(prompt)

    print(
        "\n🤖 RESPOSTA DA IA:\n"
    )

    resposta = perguntar_ia(
        prompt
    )

    print(resposta)