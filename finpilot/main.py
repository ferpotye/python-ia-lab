# ============================================================
# FINPILOT
# Seu dinheiro. Seu controle.
# ============================================================

receitas = 0
despesas = 0

lista_receitas = []
lista_despesas = []
lista_metas = []


opcao = ""

def adicionar_valor_meta(lista_metas):
    if not lista_metas:
        print("⚠️ Nenhuma meta cadastrada.")
        return

    mostrar_metas(lista_metas)

    try:
        escolha = int(input("Digite o número da meta: ")) - 1
    except ValueError:
        print("⚠️ Digite apenas o número da meta.")
        return

    if escolha < 0 or escolha >= len(lista_metas):
        print("⚠️ Meta inválida.")
        return

    valor = ler_valor_positivo("Digite o valor a adicionar: R$ ")

    lista_metas[escolha]["valor_atual"] += valor

    print("✅ Valor adicionado à meta com sucesso!")

def analisar_financas(receitas, despesas):
    print("🤖 ANÁLISE FINANCEIRA")
    print("=" * 60)

    if receitas == 0:
        print("⚠️ Cadastre pelo menos uma receita para gerar a análise.")
        return

    percentual = calcular_percentual_despesas(receitas, despesas)
    saldo = calcular_saldo(receitas, despesas)

    print(f"💰 Renda total: R$ {receitas:.2f}")
    print(f"💳 Despesas totais: R$ {despesas:.2f}")
    print(f"💵 Saldo: R$ {saldo:.2f}")
    print(f"📊 Renda comprometida: {percentual:.1f}%")
    print()

    if percentual < 50:
        print("🟢 Suas despesas estão abaixo de 50% da sua renda.")
    elif percentual < 80:
        print("🟡 Suas despesas estão consumindo uma parcela significativa da renda.")
    else:
        print("🔴 Suas despesas estão consumindo uma parcela elevada da renda.")

    if saldo > 0:
        print("✅ Você está com saldo positivo.")
    elif saldo == 0:
        print("⚠️ Sua renda e suas despesas estão equilibradas.")
    else:
        print("🚨 Suas despesas estão maiores que suas receitas.")

# ============================================================
# VALIDAÇÕES
# ============================================================

def ler_valor_positivo(mensagem):
    while True:
        try:
            valor = float(input(mensagem))

            if valor > 0:
                return valor

            print("⚠️ O valor precisa ser maior que zero.")

        except ValueError:
            print("⚠️ Digite um valor numérico válido.")
# ============================================================
# FUNÇÕES FINANCEIRAS
# ============================================================


def calcular_percentual_despesas(receitas, despesas):
    if receitas > 0:
        return (despesas / receitas) * 100
    return 0

def calcular_saldo(receitas, despesas):
    return receitas - despesas

def encontrar_maior_despesa(lista_despesas):
    if lista_despesas:
        return max(lista_despesas, key=lambda despesa: despesa["valor"])
    return None

def encontrar_maior_receita(lista_receitas):
    if lista_receitas:
        return max(lista_receitas, key=lambda receita: receita["valor"])
    return None
# ============================================================
# FUNÇÕES DE METAS
# ============================================================

def adicionar_meta(lista_metas):
    print("🎯 Nova Meta")

    nome = input("Digite o nome da meta: ")
    valor_objetivo = ler_valor_positivo("Digite o valor objetivo: R$ ")
    valor_atual = float(input("Quanto você já tem guardado? R$ "))

    meta = {
        "nome": nome,
        "valor_objetivo": valor_objetivo,
        "valor_atual": valor_atual
    }

    lista_metas.append(meta)

    print(f"✅ Meta '{nome}' criada com sucesso!")


def mostrar_metas(lista_metas):
    print("🎯 Minhas Metas")

    if not lista_metas:
        print("   Nenhuma meta cadastrada.")
        return

    for meta in lista_metas:
        percentual = (meta["valor_atual"] / meta["valor_objetivo"]) * 100

        if percentual > 100:
            percentual = 100

        print()
        print(f"🎯 {meta['nome']}")
        print(f"   💰 Guardado: R$ {meta['valor_atual']:.2f}")
        print(f"   🎯 Objetivo: R$ {meta['valor_objetivo']:.2f}")
        print(f"   📊 Progresso: {percentual:.1f}%")
# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

while opcao != "0":

    print("=" * 60)
    print("                 💰 FINPILOT")
    print("          Seu dinheiro. Seu controle.")
    print("=" * 60)

    print()
    print("1 - 💰 Receitas")
    print("2 - 💳 Despesas")
    print("3 - 📊 Resumo financeiro")
    print("4 - 🎯 Metas")
    print("5 - 🤖 Análise com IA")
    print("6 - 📋 Histórico")
    print("0 - 🚪 Sair")

    print("=" * 60)

    opcao = input("Escolha uma opção: ")

    print()

    if opcao == "1":
        print("💰 Área de Receitas")

        descricao = input("Digite a descrição da receita: ")
        categoria = input("Digite a categoria da receita: ")

        receita = ler_valor_positivo("Digite o valor da receita: R$ ")

        receitas += receita
        lista_receitas.append({
            "descricao": descricao,
            "categoria": categoria,
            "valor": receita
        })

        print(f"✅ Receita de R$ {receita:.2f} registrada!")




    elif opcao == "2":

        print("💳 Área de Despesas")

        descricao = input("Digite a descrição da despesa: ")
        categoria = input("Digite a categoria da despesa: ")
        despesa = ler_valor_positivo("Digite o valor da despesa: R$ ")

        despesas += despesa

        lista_despesas.append({
            "descricao": descricao,
            "categoria": categoria,
            "valor": despesa
        })

        print(f"✅ Despesa de R$ {despesa:.2f} registrada!")

    elif opcao == "3":

        print("📊 Resumo Financeiro")

        saldo = calcular_saldo(receitas, despesas)

        print()

        print(f"💰 Total de receitas: R$ {receitas:.2f}")

        print(f"💳 Total de despesas: R$ {despesas:.2f}")

        print(f"💵 Saldo atual: R$ {saldo:.2f}")

        print()

        print(f"📈 Quantidade de receitas: {len(lista_receitas)}")

        print(f"📉 Quantidade de despesas: {len(lista_despesas)}")

        if lista_despesas:
            maior_despesa = encontrar_maior_despesa(lista_despesas)

            print()

            print(f"🔝 Maior despesa: {maior_despesa['descricao']} — R$ {maior_despesa['valor']:.2f}")

        if lista_receitas:
            maior_receita = encontrar_maior_receita(lista_receitas)

            print()

            print(f"🔝 Maior receita: {maior_receita['descricao']} — R$ {maior_receita['valor']:.2f}")

        percentual_despesas = calcular_percentual_despesas(receitas, despesas)

        print()

        print(f"📊 Percentual da renda comprometida: {percentual_despesas:.1f}%")


    elif opcao == "4":

        print("🎯 Área de Metas")

        print()

        print("1 - ➕ Criar nova meta")

        print("2 - 📊 Ver minhas metas")

        print("3 - 💰 Adicionar dinheiro a uma meta")

        print("0 - ↩️ Voltar")

        escolha_meta = input("Escolha uma opção: ")

        if escolha_meta == "1":

            adicionar_meta(lista_metas)


        elif escolha_meta == "2":

            mostrar_metas(lista_metas)


        elif escolha_meta == "3":

            adicionar_valor_meta(lista_metas)


        elif escolha_meta == "0":

            print("↩️ Voltando...")


        else:

            print("⚠️ Opção inválida.")


    elif opcao == "5":

        analisar_financas(receitas, despesas)




    elif opcao == "6":

        print("📋 HISTÓRICO DE LANÇAMENTOS")

        print("=" * 60)

        total_lancamentos = len(lista_receitas) + len(lista_despesas)

        print(f"📊 Total de lançamentos: {total_lancamentos}")

        print()

        print("💰 RECEITAS")

        if lista_receitas:

            for receita in lista_receitas:
                print(

                    f"   + {receita['categoria']} | "

                    f"{receita['descricao']} — "

                    f"R$ {receita['valor']:.2f}"

                )

        else:

            print("   Nenhuma receita cadastrada.")

        print()

        print("💳 DESPESAS")

        if lista_despesas:

            for despesa in lista_despesas:
                print(

                    f"   - {despesa['categoria']} | "

                    f"{despesa['descricao']} — "

                    f"R$ {despesa['valor']:.2f}"

                )

        else:

            print("   Nenhuma despesa cadastrada.")

        print()

        print("=" * 60)

        saldo_historico = calcular_saldo(receitas, despesas)

        print(f"💰 Total de receitas: R$ {receitas:.2f}")

        print(f"💳 Total de despesas: R$ {despesas:.2f}")

        print(f"💵 Saldo atual: R$ {saldo_historico:.2f}")


    elif opcao == "0":

        print("👋 Até logo!")


    else:

        print("⚠️ Opção inválida.")