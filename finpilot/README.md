# 💰 FinPilot

> **Seu dinheiro. Seu controle.**

O **FinPilot** é uma aplicação de controle e análise financeira desenvolvida em Python.

O projeto começou como uma aplicação de terminal e evoluiu para uma plataforma com
**banco de dados SQLite, dashboard web, análise de dados, relatórios financeiros,
gráficos interativos e exportação de informações**.

O objetivo do projeto é transformar dados financeiros em informações que facilitem
o acompanhamento da vida financeira.

---

## 📸 Interface

### Dashboard

![Dashboard](screenshots/dashboard.png)

### Receitas

![Receitas](screenshots/receitas.png)

### Despesas

![Despesas](screenshots/despesas.png)

### Metas

![Metas](screenshots/metas.png)

### Relatórios

![Relatórios](screenshots/relatorios.png)

---

## 🚀 Funcionalidades

### 💰 Controle financeiro

- Cadastro de receitas
- Cadastro de despesas
- Categorias financeiras
- Registro de datas
- Cálculo automático do saldo
- Identificação da maior receita
- Identificação da maior despesa
- Percentual da renda comprometida
- Contagem de lançamentos
- Edição de lançamentos
- Exclusão de lançamentos

### 🎯 Metas financeiras

- Criação de metas
- Definição de valor objetivo
- Controle do valor acumulado
- Cálculo automático do progresso
- Adição de valores às metas
- Exclusão de metas

### 📊 Dashboard

- Indicadores financeiros
- Saldo atual
- Total de receitas
- Total de despesas
- Evolução financeira
- Distribuição das despesas por categoria
- Gráficos interativos

### 📈 Relatórios e Analytics

- Filtro por ano
- Filtro por mês
- Filtro por categoria
- Filtro por tipo de lançamento
- Total de receitas no período
- Total de despesas no período
- Saldo do período
- Quantidade de lançamentos
- Média de receitas
- Média de despesas
- Média diária de gastos
- Percentual da renda comprometida
- Evolução mensal
- Evolução do saldo
- Análise de gastos por categoria
- Comparação entre períodos
- Identificação da maior categoria de gasto

### 📤 Exportação

- Exportação de dados para CSV
- Exportação de relatórios para Excel

### 🤖 Insights financeiros

O FinPilot possui uma camada inicial de análise baseada em regras para identificar
situações financeiras relevantes.

A arquitetura foi preparada para que essa camada possa evoluir posteriormente
para recursos de **inteligência artificial**.

---

## 🏗️ Arquitetura

O projeto está organizado buscando separar interface, dados, regras de negócio
e análise.

```text
FinPilot
│
├── main.py
│
├── dashboard.py
│
├── database.py
│
├── analytics.py
│
├── relatorios.py
│
├── importador.py
│
├── finpilot.db
│
└── screenshots/
    ├── dashboard.png
    ├── receitas.png
    ├── despesas.png
    ├── metas.png
    └── relatorios.png