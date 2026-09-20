import sys
from datetime import datetime

print("PYTHON DO PYCHARM:", sys.executable)

from database import (
    salvar_receita,
    salvar_despesa,
    buscar_receitas,
    buscar_despesas,
    salvar_meta,
    buscar_metas,
    atualizar_meta,
    excluir_receita,
    excluir_despesa,
    excluir_meta
)

from analytics import gerar_relatorio


LARGURA = 64


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def linha():
    print("═" * LARGURA)


def formatar_moeda(valor):

    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def formatar_data(data):

    if not data:
        return "-"

    try:

        data_objeto = datetime.strptime(
            data,
            "%Y-%m-%d"
        )

        return data_objeto.strftime(
            "%d/%m/%Y"
        )

    except ValueError:

        return str(data)


# ============================================================
# CARREGAMENTO
# ============================================================

def carregar_dados():

    receitas = buscar_receitas()
    despesas = buscar_despesas()

    return receitas, despesas


# ============================================================
# CÁLCULOS
# ============================================================

def calcular_saldo():

    receitas, despesas = (
        carregar_dados()
    )

    total_receitas = sum(
        receita[3]
        for receita in receitas
    )

    total_despesas = sum(
        despesa[3]
        for despesa in despesas
    )

    return (
        total_receitas -
        total_despesas
    )


def calcular_percentual_despesas():

    receitas, despesas = (
        carregar_dados()
    )

    total_receitas = sum(
        receita[3]
        for receita in receitas
    )

    total_despesas = sum(
        despesa[3]
        for despesa in despesas
    )

    if total_receitas == 0:

        return 0

    return (
        total_despesas /
        total_receitas *
        100
    )


# ============================================================
# HISTÓRICO
# ============================================================

def mostrar_historico():

    receitas, despesas = (
        carregar_dados()
    )

    print()

    linha()

    print(
        "📋 HISTÓRICO FINANCEIRO"
        .center(LARGURA)
    )

    linha()

    print()

    if not receitas and not despesas:

        print(
            "⚠️ Nenhum lançamento cadastrado."
        )

        return

    if receitas:

        print("💰 RECEITAS")
        print()

        for receita in receitas:

            receita_id = receita[0]
            descricao = receita[1]
            categoria = receita[2]
            valor = receita[3]
            data = receita[4]

            print(
                f"🆔 ID: {receita_id}"
            )

            print(
                f"📅 {formatar_data(data)}"
            )

            print(
                f"   💰 {descricao}"
            )

            print(
                f"   📂 {categoria}"
            )

            print(
                f"   💵 {formatar_moeda(valor)}"
            )

            print()

    if despesas:

        print("💳 DESPESAS")
        print()

        for despesa in despesas:

            despesa_id = despesa[0]
            descricao = despesa[1]
            categoria = despesa[2]
            valor = despesa[3]
            data = despesa[4]

            print(
                f"🆔 ID: {despesa_id}"
            )

            print(
                f"📅 {formatar_data(data)}"
            )

            print(
                f"   💳 {descricao}"
            )

            print(
                f"   📂 {categoria}"
            )

            print(
                f"   💵 {formatar_moeda(valor)}"
            )

            print()


# ============================================================
# RESUMO
# ============================================================

def mostrar_resumo():

    receitas, despesas = (
        carregar_dados()
    )

    total_receitas = sum(
        receita[3]
        for receita in receitas
    )

    total_despesas = sum(
        despesa[3]
        for despesa in despesas
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

    print()

    linha()

    print(
        "📊 RESUMO FINANCEIRO"
        .center(LARGURA)
    )

    linha()

    print()

    print(
        f"💰 Total de receitas: "
        f"{formatar_moeda(total_receitas)}"
    )

    print(
        f"💳 Total de despesas: "
        f"{formatar_moeda(total_despesas)}"
    )

    print(
        f"💵 Saldo: "
        f"{formatar_moeda(saldo)}"
    )

    print(
        f"📊 Renda comprometida: "
        f"{percentual:.1f}%"
    )

    print()

    print(
        f"📈 Quantidade de receitas: "
        f"{len(receitas)}"
    )

    print(
        f"📉 Quantidade de despesas: "
        f"{len(despesas)}"
    )

    print()

    linha()


# ============================================================
# ANÁLISE
# ============================================================

def analisar_financas():

    receitas, despesas = (
        carregar_dados()
    )

    total_receitas = sum(
        receita[3]
        for receita in receitas
    )

    total_despesas = sum(
        despesa[3]
        for despesa in despesas
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

    print()

    linha()

    print(
        "🤖 ANÁLISE FINANCEIRA"
        .center(LARGURA)
    )

    linha()

    print()

    if saldo > 0:

        print(
            f"✅ Seu saldo está positivo "
            f"em {formatar_moeda(saldo)}."
        )

    elif saldo == 0:

        print(
            "⚠️ Suas receitas e despesas "
            "estão equilibradas."
        )

    else:

        print(
            f"🚨 Suas despesas superam "
            f"suas receitas em "
            f"{formatar_moeda(abs(saldo))}."
        )

    print()

    print(
        f"📊 Você está comprometendo "
        f"{percentual:.1f}% da sua renda."
    )

    if percentual < 50:

        print(
            "🟢 O percentual de despesas "
            "está abaixo de 50%."
        )

    elif percentual <= 70:

        print(
            "🟡 O percentual de despesas "
            "está entre 50% e 70%."
        )

    else:

        print(
            "🔴 O percentual de despesas "
            "está acima de 70%."
        )

    print()

    linha()


# ============================================================
# METAS
# ============================================================

def adicionar_meta():

    print()

    linha()

    print(
        "🎯 NOVA META".center(LARGURA)
    )

    linha()

    print()

    nome = input(
        "Nome da meta: "
    ).strip()

    if not nome:

        print(
            "❌ O nome da meta "
            "não pode ficar vazio."
        )

        return

    try:

        valor_objetivo = float(
            input(
                "Valor objetivo: R$ "
            ).replace(",", ".")
        )

        valor_atual = float(
            input(
                "Valor inicial: R$ "
            ).replace(",", ".")
        )

        if valor_objetivo <= 0:

            print(
                "❌ O valor objetivo "
                "deve ser maior que zero."
            )

            return

        if valor_atual < 0:

            print(
                "❌ O valor inicial "
                "não pode ser negativo."
            )

            return

        if valor_atual > valor_objetivo:

            print(
                "❌ O valor inicial "
                "não pode ser maior que o objetivo."
            )

            return

        salvar_meta(
            nome,
            valor_objetivo,
            valor_atual
        )

        print()

        print(
            "✅ Meta criada com sucesso!"
        )

    except ValueError:

        print(
            "❌ Digite valores numéricos válidos."
        )


def mostrar_metas():

    metas = buscar_metas()

    print()

    linha()

    print(
        "🎯 METAS FINANCEIRAS"
        .center(LARGURA)
    )

    linha()

    print()

    if not metas:

        print(
            "⚠️ Nenhuma meta cadastrada."
        )

        return

    for meta in metas:

        meta_id = meta[0]
        nome = meta[1]
        objetivo = meta[2]
        atual = meta[3]

        percentual = (
            atual /
            objetivo *
            100
            if objetivo > 0
            else 0
        )

        if percentual > 100:

            percentual = 100

        print(
            f"🎯 {nome}"
        )

        print(
            f"   💰 "
            f"{formatar_moeda(atual)} / "
            f"{formatar_moeda(objetivo)}"
        )

        print(
            f"   📊 Progresso: "
            f"{percentual:.1f}%"
        )

        print(
            f"   🆔 ID: {meta_id}"
        )

        print()


def adicionar_dinheiro_meta():

    metas = buscar_metas()

    if not metas:

        print(
            "⚠️ Nenhuma meta cadastrada."
        )

        return

    mostrar_metas()

    try:

        meta_id = int(
            input(
                "Digite o ID da meta: "
            )
        )

        valor = float(
            input(
                "Quanto deseja adicionar? R$ "
            ).replace(",", ".")
        )

        if valor <= 0:

            print(
                "❌ O valor deve ser maior que zero."
            )

            return

        meta_encontrada = None

        for meta in metas:

            if meta[0] == meta_id:

                meta_encontrada = meta

                break

        if meta_encontrada is None:

            print(
                "❌ Meta não encontrada."
            )

            return

        valor_atual = meta_encontrada[3]

        valor_objetivo = meta_encontrada[2]

        novo_valor = (
            valor_atual +
            valor
        )

        if novo_valor > valor_objetivo:

            novo_valor = valor_objetivo

        atualizar_meta(
            meta_id,
            novo_valor
        )

        print()

        print(
            "✅ Valor adicionado à meta!"
        )

        print(
            f"💰 Novo valor: "
            f"{formatar_moeda(novo_valor)}"
        )

    except ValueError:

        print(
            "❌ Digite valores válidos."
        )


def excluir_meta_menu():

    metas = buscar_metas()

    if not metas:

        print(
            "⚠️ Nenhuma meta cadastrada."
        )

        return

    mostrar_metas()

    try:

        meta_id = int(
            input(
                "Digite o ID da meta que deseja excluir: "
            )
        )

        meta_encontrada = None

        for meta in metas:

            if meta[0] == meta_id:

                meta_encontrada = meta

                break

        if meta_encontrada is None:

            print(
                "❌ Meta não encontrada."
            )

            return

        confirmacao = input(
            f"⚠️ Excluir a meta "
            f"'{meta_encontrada[1]}'? "
            f"(s/n): "
        ).strip().lower()

        if confirmacao == "s":

            excluir_meta(
                meta_id
            )

            print(
                "✅ Meta excluída com sucesso!"
            )

        else:

            print(
                "❌ Exclusão cancelada."
            )

    except ValueError:

        print(
            "❌ Digite um ID válido."
        )


def menu_metas():

    while True:

        print()

        linha()

        print(
            "🎯 METAS".center(LARGURA)
        )

        linha()

        print()

        print(
            "1 - Criar meta"
        )

        print(
            "2 - Ver metas"
        )

        print(
            "3 - Adicionar dinheiro"
        )

        print(
            "4 - Excluir meta"
        )

        print(
            "0 - Voltar"
        )

        print()

        opcao = input(
            "Escolha uma opção: "
        ).strip()

        if opcao == "1":

            adicionar_meta()

        elif opcao == "2":

            mostrar_metas()

        elif opcao == "3":

            adicionar_dinheiro_meta()

        elif opcao == "4":

            excluir_meta_menu()

        elif opcao == "0":

            break

        else:

            print(
                "❌ Opção inválida."
            )


# ============================================================
# RECEITAS
# ============================================================

def adicionar_receita():

    print()

    linha()

    print(
        "💰 NOVA RECEITA".center(LARGURA)
    )

    linha()

    print()

    descricao = input(
        "Descrição: "
    ).strip()

    if not descricao:

        print(
            "❌ A descrição "
            "não pode ficar vazia."
        )

        return

    categoria = input(
        "Categoria: "
    ).strip()

    if not categoria:

        categoria = "outros"

    try:

        valor = float(
            input(
                "Valor: R$ "
            ).replace(",", ".")
        )

        if valor <= 0:

            print(
                "❌ O valor deve ser maior que zero."
            )

            return

    except ValueError:

        print(
            "❌ Digite um valor válido."
        )

        return

    data = input(
        "Data (DD/MM/AAAA) "
        "ou Enter para hoje: "
    ).strip()

    if not data:

        data = datetime.now().strftime(
            "%Y-%m-%d"
        )

    else:

        try:

            data_objeto = datetime.strptime(
                data,
                "%d/%m/%Y"
            )

            data = data_objeto.strftime(
                "%Y-%m-%d"
            )

        except ValueError:

            print(
                "❌ Data inválida. "
                "Use o formato DD/MM/AAAA."
            )

            return

    salvar_receita(
        descricao,
        categoria,
        valor,
        data
    )

    print()

    print(
        "✅ Receita adicionada com sucesso!"
    )


def excluir_receita_menu():

    receitas, _ = carregar_dados()

    if not receitas:

        print(
            "⚠️ Nenhuma receita cadastrada."
        )

        return

    print()

    print("💰 RECEITAS")

    print()

    for receita in receitas:

        print(
            f"🆔 {receita[0]} | "
            f"{formatar_data(receita[4])} | "
            f"{receita[1]} | "
            f"{formatar_moeda(receita[3])}"
        )

    print()

    try:

        receita_id = int(
            input(
                "Digite o ID da receita que deseja excluir: "
            )
        )

        receita_encontrada = None

        for receita in receitas:

            if receita[0] == receita_id:

                receita_encontrada = receita

                break

        if receita_encontrada is None:

            print(
                "❌ Receita não encontrada."
            )

            return

        confirmacao = input(
            f"⚠️ Excluir "
            f"'{receita_encontrada[1]}'? "
            f"(s/n): "
        ).strip().lower()

        if confirmacao == "s":

            excluir_receita(
                receita_id
            )

            print(
                "✅ Receita excluída com sucesso!"
            )

        else:

            print(
                "❌ Exclusão cancelada."
            )

    except ValueError:

        print(
            "❌ Digite um ID válido."
        )


# ============================================================
# DESPESAS
# ============================================================

def adicionar_despesa():

    print()

    linha()

    print(
        "💳 NOVA DESPESA".center(LARGURA)
    )

    linha()

    print()

    descricao = input(
        "Descrição: "
    ).strip()

    if not descricao:

        print(
            "❌ A descrição "
            "não pode ficar vazia."
        )

        return

    categoria = input(
        "Categoria: "
    ).strip()

    if not categoria:

        categoria = "outros"

    try:

        valor = float(
            input(
                "Valor: R$ "
            ).replace(",", ".")
        )

        if valor <= 0:

            print(
                "❌ O valor deve ser maior que zero."
            )

            return

    except ValueError:

        print(
            "❌ Digite um valor válido."
        )

        return

    data = input(
        "Data (DD/MM/AAAA) "
        "ou Enter para hoje: "
    ).strip()

    if not data:

        data = datetime.now().strftime(
            "%Y-%m-%d"
        )

    else:

        try:

            data_objeto = datetime.strptime(
                data,
                "%d/%m/%Y"
            )

            data = data_objeto.strftime(
                "%Y-%m-%d"
            )

        except ValueError:

            print(
                "❌ Data inválida. "
                "Use o formato DD/MM/AAAA."
            )

            return

    salvar_despesa(
        descricao,
        categoria,
        valor,
        data
    )

    print()

    print(
        "✅ Despesa adicionada com sucesso!"
    )


def excluir_despesa_menu():

    _, despesas = carregar_dados()

    if not despesas:

        print(
            "⚠️ Nenhuma despesa cadastrada."
        )

        return

    print()

    print("💳 DESPESAS")

    print()

    for despesa in despesas:

        print(
            f"🆔 {despesa[0]} | "
            f"{formatar_data(despesa[4])} | "
            f"{despesa[1]} | "
            f"{formatar_moeda(despesa[3])}"
        )

    print()

    try:

        despesa_id = int(
            input(
                "Digite o ID da despesa que deseja excluir: "
            )
        )

        despesa_encontrada = None

        for despesa in despesas:

            if despesa[0] == despesa_id:

                despesa_encontrada = despesa

                break

        if despesa_encontrada is None:

            print(
                "❌ Despesa não encontrada."
            )

            return

        confirmacao = input(
            f"⚠️ Excluir "
            f"'{despesa_encontrada[1]}'? "
            f"(s/n): "
        ).strip().lower()

        if confirmacao == "s":

            excluir_despesa(
                despesa_id
            )

            print(
                "✅ Despesa excluída com sucesso!"
            )

        else:

            print(
                "❌ Exclusão cancelada."
            )

    except ValueError:

        print(
            "❌ Digite um ID válido."
        )


# ============================================================
# MENU PRINCIPAL
# ============================================================

def mostrar_menu():

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
        "1 - 💰 Adicionar receita"
    )

    print(
        "2 - 💳 Adicionar despesa"
    )

    print(
        "3 - 📋 Ver histórico"
    )

    print(
        "4 - 📊 Ver resumo"
    )

    print(
        "5 - 🤖 Análise financeira"
    )

    print(
        "6 - 🎯 Metas"
    )

    print(
        "7 - 🗑️ Excluir receita"
    )

    print(
        "8 - 🗑️ Excluir despesa"
    )

    print(
        "0 - 🚪 Sair"
    )

    print()


# ============================================================
# EXECUÇÃO
# ============================================================

while True:

    mostrar_menu()

    opcao = input(
        "Escolha uma opção: "
    ).strip()

    if opcao == "1":

        adicionar_receita()

    elif opcao == "2":

        adicionar_despesa()

    elif opcao == "3":

        mostrar_historico()

    elif opcao == "4":

        mostrar_resumo()

    elif opcao == "5":

        gerar_relatorio()

    elif opcao == "6":

        menu_metas()

    elif opcao == "7":

        excluir_receita_menu()

    elif opcao == "8":

        excluir_despesa_menu()

    elif opcao == "0":

        print()

        print(
            "👋 Até logo!"
        )

        break

    else:

        print()

        print(
            "❌ Opção inválida."
        )