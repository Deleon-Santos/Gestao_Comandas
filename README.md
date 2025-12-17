# 🍽️ Sistema de Gestão de Comandas (Bar/Restaurante)

## 📌 Objetivo do Projeto

O Sistema de Gestão de Comandas é uma aplicação web leve, desenvolvida em Python, que visa digitalizar e simplificar a gestão de pedidos, mesas e pagamentos em pequenos bares, restaurantes ou cafeterias. Ele utiliza um banco de dados local (SQLite) para garantir a persistência dos dados de forma rápida e segura.

## ✨ Funcionalidades Principais

O sistema é dividido em três abas principais, oferecendo controle total sobre o ciclo de vida da comanda. 

### 1. Comandas e Pedidos
* **Abertura de Comanda:** Permite abrir uma nova comanda associada a um número de mesa específico.
* **Adição de Itens:** Adiciona múltiplos produtos do cardápio à comanda selecionada, registrando a quantidade e o preço unitário.
* **Visualização Detalhada:** Exibe todas as comandas, mostrando a data de abertura, status, itens pedidos e o total parcial.
* **Filtro por Status:** Permite visualizar comandas filtradas por `TODAS`, `Aberta`, `Fechada`, `Cancelada` ou `Paga`.
* **Ações Rápidas:** Botões para encerrar a comanda (pronta para pagamento) ou cancelar a comanda.

### 2. Pagamento e Fechamento
* **Processamento de Pagamento:** Exibe comandas no status "Fechada" prontas para serem processadas.
* **Finalização:** Ao confirmar o pagamento, a comanda é movida para o status "Paga".

### 3. Gestão de Cardápio
* **Cadastro de Produtos:** Formulário para adicionar novos itens ao cardápio (Nome e Preço).
* **Cardápio Atual:** Exibe em formato de tabela todos os produtos cadastrados.

## 💻 Tecnologias Utilizadas

A aplicação é construída com uma arquitetura modular, separando a interface (front-end) da lógica de negócios e do acesso aos dados.

| Categoria | Tecnologia | Função |
| :--- | :--- | :--- |
| **Interface (UI)** | **Streamlit** | Criação da interface web interativa com Python. |
| **Banco de Dados** | **SQLite** | Banco de dados leve e local, ideal para ambientes pequenos. |
| **Acesso a Dados (ORM)** | **SQLAlchemy** | Mapeador Objeto-Relacional para gerenciar o banco de dados usando classes Python. |
| **Linguagem Principal** | **Python 3.x** | Linguagem utilizada para todo o desenvolvimento, incluindo o front-end e o back-end. |

## ⚙️ Configuração e Execução

Siga os passos abaixo para clonar e executar o projeto em sua máquina local.

### Pré-requisitos
Certifique-se de ter o Python 3 instalado.

### 1. Clonar o Repositório
```bash
git clone https://github.com/Deleon-Santos/Gestao_Comandas.git

```
### 2. Instale as dependencial e rode o script
```bash
streamlit run app.py
```
### Melhorias
Comverter o Banco de Dados para PostgreSQL e efetuar deploy.

## Licença
MIT License.
Copyright (c) 2025 DELEON SANTOS.

