import streamlit as st
from config.config import Base, engine, session
from models.models import Comanda, Status
from sqlalchemy import desc
from sqlalchemy.orm import selectinload
from service.servicos import GerenciadorComandas

# Inicializa o banco de dados e o gerenciador
Base.metadata.create_all(engine)
gc = GerenciadorComandas(session)

st.set_page_config(layout="wide", page_title="Sistema de Gestão de Comandas")
st.markdown("<h1 style='text-align: center; color: #007BFF;'>🍽️ Gestão de Comandas</h1>", unsafe_allow_html=True)

# --- Funções Auxiliares de Visualização ---

def formatar_comanda(comanda):
    """Formata a exibição de uma comanda."""
    total = gc.calcular_total_comanda(comanda.id)
    itens_str = ", ".join([f"{item.quantidade}x {item.produto.nome}" for item in comanda.itens])
    return f"Mesa_numero: {comanda.mesa_numero} | Total: R$ {total:.2f} | Status: {comanda.status.value}"

# --- Estrutura da Interface com Abas ---

tab_pedidos, tab_comandas, tab_pagamento, tab_produtos = st.tabs(["Pedidos", "Comandas", "Pagamento e Fechamento", "Gestão de Cardápio"])


with tab_pedidos:
    st.markdown("<h2 style='text-align: lefth; color: #000000;'>Pedidos</h2>", unsafe_allow_html=True)
    # st.header("Comandas Abertas")
    
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Nova Comanda")
        mesa_numero_nova = st.number_input("Número da Mesa_numero", min_value=1, value=1, key="mesa_numero_nova")
        if st.button("Abrir Nova Comanda"):
            gc.criar_comanda(mesa_numero_nova)
            st.success(f"Comanda aberta para a Mesa_numero {mesa_numero_nova}!")
            st.warning(f"Nova Comanda Aberta para a mesa {mesa_numero_nova}.")
            st.rerun()

    # with col2:
        st.subheader("Adicionar Item ao Pedido")
        comandas_abertas = (
            gc.session.query(Comanda)
            .options(selectinload(Comanda.itens))  # Mantém o Eager Loading para evitar DetachedInstanceError
            .filter(Comanda.status == Status.aberta)
            .all()
        )
        produtos = gc.listar_produtos()

        if not comandas_abertas or not produtos:
            st.warning("Não há comandas abertas ou produtos cadastrados.")
        else:
            col_select, col_display = st.columns([1, 1.5]) 

            with col_select:
                comanda_selecionada = st.selectbox(
                    "Selecione a Comanda e Mesa",
                    options=comandas_abertas,
                    format_func=lambda c: f"Comanda #{c.id} - Mesa {c.mesa_numero}",
                    key="comanda_adicionar_item"
                )
                
                produto_selecionado = st.selectbox(
                    "Selecione o Produto",
                    options=produtos,
                    format_func=lambda p: f"{p.nome} (R$ {p.preco:.2f})",
                    key="produto_adicionar_item"
                )

                quantidade = st.number_input("Quantidade", min_value=1, value=1, key="qtd_adicionar")

                # 1. CRIA UM PLACEHOLDER PARA O PROGRESSO/STATUS
                #status_placeholder = st.empty()
                
                if st.button("Add item à Comanda"):
                    status_placeholder = st.empty()
                    # 2. INICIA A BARRA DE PROGRESSO
                    status_placeholder.info("Adicionando item ao pedido...")
                    progress_bar = status_placeholder.progress(0)
                    
                    # Simula um pequeno tempo de processamento (para a barra ser visível)
                    import time
                    for percent_complete in range(10, 101, 10):
                        progress_bar.progress(percent_complete)
                        time.sleep(0.01) # Pausa mínima
                    
                    # 3. EXECUTA A AÇÃO
                    gc.adicionar_item_a_comanda(
                        comanda_selecionada.id,
                        produto_selecionado.id,
                        quantidade
                    )
                    
                    # 4. LIMPA A BARRA E MOSTRA SUCESSO
                    status_placeholder.empty() # Limpa o placeholder (remove a barra)
                    st.success(f"{quantidade}x {produto_selecionado.nome} adicionado à Comanda {comanda_selecionada.id}!")
                    
                    # 5. RECARREGA PARA LIMPAR O FORMULÁRIO
                    # O st.rerun() recarrega o script, o que efetivamente 'limpa' o campo, 
                    # redefinindo-o para a primeira opção da lista.
                    st.rerun()

   
with tab_comandas:
    st.markdown("<h2 style='text-align: lefth; color: #000000;'>Comandas</h2>", unsafe_allow_html=True)
    # ... (Blocos de "Nova Comanda" e "Adicionar Item" - não mostrados aqui, mas assumidos como presentes no código completo) ...
    
    st.subheader("Visualizar Comandas")

    # --- NOVO BLOCO DE FILTROS ---
    col_filtro_status, col_filtro_itens = st.columns(2)

    with col_filtro_status:
        status_options = ["TODAS"] + [s.value for s in Status]
        filtro_status = st.selectbox("Filtrar por Status", options=status_options, key="filtro_status")
    
    # with col_filtro_itens:
        # Checkbox para filtrar comandas que contenham pelo menos 1 item
        st.markdown("<br>", unsafe_allow_html=True) # Espaçamento para alinhar com o selectbox
        filtro_com_itens = st.checkbox("Mostrar apenas comandas com pedidos", key="filtro_com_itens")

    # --- LÓGICA DE FILTRAGEM ---
    query = gc.session.query(Comanda) 

    # 1. Aplica o filtro de STATUS
    if filtro_status != "TODAS":
        try:
            # Encontra o membro Enum pelo seu VALOR de string
            status_enum_obj = next(s for s in Status if s.value == filtro_status)
            query = query.filter(Comanda.status == status_enum_obj)
        except StopIteration:
            pass
            
    # 2. Aplica o filtro de ITENS (a sua necessidade principal: Comandas com pelo menos 1 item)
    if filtro_com_itens:
        # Se a caixa estiver marcada, aplica a condição: onde a lista de 'itens' não está vazia.
        query = query.filter(Comanda.itens.any()) 
    
    # 3. Finaliza a consulta com ordenação
    todas_comandas = query.order_by(desc(Comanda.data_abertura)).all()
    # --- FIM DA LÓGICA DE FILTRAGEM ---

    if todas_comandas:
        for comanda in todas_comandas:
            total = gc.calcular_total_comanda(comanda.id)
            
            with st.expander(f"Comanda #{comanda.id} | Mesa {comanda.mesa_numero} | Status: {comanda.status.value} | Total: R$ {total:.2f}"):
                
                st.write(f"**Data de Abertura:** {comanda.data_abertura.strftime('%d/%m/%Y %H:%M')}")
                
                st.write(f"**Data de Fechamento:** {comanda.data_fechamento.strftime('%d/%m/%Y %H:%M') if comanda.data_fechamento else 'Aberto'}")
                st.write(f"**Status:** {comanda.status.value}")
                
                st.markdown("---")
                
                st.write("**Itens do Pedido:**")

                if comanda.itens:
                    # Cria uma lista para armazenar os dados dos itens
                    itens_data = []
                    
                    for item in comanda.itens:
                        subtotal = item.quantidade * item.preco_unitario
                        
                        # Adiciona um dicionário para cada item
                        itens_data.append({
                            "Qtd": item.quantidade,
                            "Produto": item.produto.nome,
                            "Preço Unit.": f"R$ {item.preco_unitario:.2f}",
                            "Subtotal": f"R$ {subtotal:.2f}"
                        })
                        
                    # Exibe a lista de dicionários como uma tabela interativa
                    st.dataframe(
                        itens_data,
                        hide_index=True,  # Esconde o índice numérico
                        use_container_width=True # Ocupa toda a largura do container
                    )
                    
                else:
                    st.write("Nenhum item nesta comanda.")
                
                col_acoes1, col_acoes2 = st.columns(2)
                
                with col_acoes1:
                    if comanda.status == Status.aberta and st.button("Encerrar Comanda", key=f"encerrar_{comanda.id}"):
                        gc.fechar_comanda(comanda.id)
                        st.success(f"Comanda {comanda.id} encerrada!")
                        st.rerun()

                with col_acoes2:
                    if comanda.status == Status.aberta and st.button("Cancelar Comanda", key=f"cancelar_{comanda.id}"):
                        if gc.cancelar_comanda(comanda.id):
                            st.success(f"Comanda {comanda.id} cancelada e removida!")
                            st.rerun()
                        else:
                            st.error("Erro ao cancelar comanda.")
    else:
        st.info("Nenhuma comanda encontrada com o filtro selecionado.")

with tab_pagamento:
    st.header("Pagamento e Fechamento")
    
    comandas_fechadas = gc.session.query(Comanda).filter(Comanda.status == Status.fechada).all()
    
    st.subheader("Comandas Prontas para Pagamento")

    if not comandas_fechadas:
        st.info("Não há comandas fechadas aguardando pagamento.")
    else:
        comanda_a_pagar = st.selectbox(
            "Selecione a Comanda para Pagar",
            options=comandas_fechadas,
            format_func=formatar_comanda,
            key="comanda_pagar"
        )
        
        if comanda_a_pagar and st.button(f"Confirmar Pagamento da Comanda {comanda_a_pagar.id}"):
            if gc.pagar_comanda(comanda_a_pagar.id):
                st.success(f"Pagamento da Comanda {comanda_a_pagar.id} efetuado com sucesso!")
            else:
                st.error("Erro ao processar pagamento.")
            st.rerun()



with tab_produtos:
    st.header("Gestão de Cardápio")
    st.subheader("Cadastro de Novo Produto")
    
    with st.form("form_novo_produto"):
        novo_nome = st.text_input("Nome do Produto", max_chars=100)
        novo_preco = st.number_input("Preço (R$)", min_value=0.01, format="%.2f", value=10.00)
        submitted = st.form_submit_button("Cadastrar Produto")
        
        if submitted:
            if novo_nome and novo_preco:
                gc.adicionar_produto(novo_nome, novo_preco)
                st.success(f"Produto '{novo_nome}' cadastrado por R$ {novo_preco:.2f}!")
                st.rerun()
            else:
                st.error("Preencha todos os campos.")

    st.markdown("---")
    st.subheader("Cardápio Atual")
    produtos_atuais = gc.listar_produtos()

    if produtos_atuais:
        produtos_data = [{"ID": p.id, "Nome": p.nome, "Preço": f"R$ {p.preco:.2f}"} for p in produtos_atuais]
        st.table(produtos_data)
    else:
        st.info("Nenhum produto cadastrado.")