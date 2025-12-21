import streamlit as st
from config.config import Base, engine, session
from models.models import Comanda, ItemComanda, Status
from sqlalchemy import desc
from sqlalchemy.orm import selectinload
from service.servicos import GerenciadorComandas
import time


try:
    Base.metadata.create_all(engine)
except Exception as e:
    st.error(f"Erro Real: {e}") 

gc = GerenciadorComandas(session)

st.set_page_config(layout="wide", page_title="Sistema de Gestão de Comandas")
st.markdown("<h1 style='text-align: center; color: #007BFF;'>🍽️ Gestão de Comandas</h1>", unsafe_allow_html=True)

# Funções Auxiliares de Visualização 

def formatar_comanda(comanda):
    """Formata a exibição de uma comanda."""
    total = gc.calcular_total_comanda(comanda.id)
    itens_str = ", ".join([f"{item.quantidade}x {item.produto.nome}" for item in comanda.itens])
    return f"Comanda #{comanda.id} | Mesa {comanda.mesa_numero} | Total: R$ {total:.2f} | Status: {comanda.status.value}"


#Estrutura da Interface com Abas 
tab_pedidos, tab_comandas, tab_pagamento, tab_produtos = st.tabs(["Pedidos", "Comandas", "Pagamento e Fechamento", "Gestão de Cardápio"])


# Gestão de Pedidos
with tab_pedidos:
    st.markdown("<h2 style='text-align: lefth; color: #000000;'>Pedidos</h2>", unsafe_allow_html=True)
    col1, col2 = st.tabs(["Add Comandas", "Add Produtos"])

    with col1:
        st.subheader("Nova Comanda")
        mesa_numero_nova = st.number_input("Número da Mesa", min_value=1, value=1, key="mesa_numero_nova")
        if st.button("Abrir Nova Comanda"):
            gc.criar_comanda(mesa_numero_nova)
            st.success(f"Nova Comanda aberta para a Mesa {mesa_numero_nova}!")
            time.sleep(0.5)
            st.rerun()
    
    with col2:
        st.markdown("Adicionar Item ao Pedido")
        comandas_abertas = (
        gc.session.query(Comanda).options(
        selectinload(Comanda.itens).joinedload(ItemComanda.produto)  )
        .filter(Comanda.status == Status.aberta).all() )
       
        produtos = gc.listar_produtos()

        if not comandas_abertas or not produtos:
            st.warning("Não há comandas abertas ou produtos cadastrados.")
        
        comanda_selecionada = st.selectbox(
            "Selecione a Comanda e Mesa",
            options=comandas_abertas,
            format_func=lambda c: f"Comanda #{c.id} - Mesa {c.mesa_numero}",
            key="comanda_adicionar_item")
        
        produto_selecionado = st.selectbox(
            "Selecione o Produto",
            options=produtos,
            format_func=lambda p: f"{p.nome} (R$ {p.preco:.2f})",
            key="produto_adicionar_item")

        quantidade = st.number_input("Quantidade", min_value=1, value=1, key="qtd_adicionar") 
        
        if st.button("Add item à Comanda"):
            status_placeholder = st.empty()
            status_placeholder.info("Adicionando item ao pedido...")
            progress_bar = status_placeholder.progress(0)
            
            for percent_complete in range(10, 101, 10):
                progress_bar.progress(percent_complete)
                time.sleep(0.01) # pequena pausa para simular o progresso
            
            gc.adicionar_item_a_comanda(
                comanda_selecionada.id,
                produto_selecionado.id,
                quantidade )
            
            status_placeholder.empty() 
            st.success(f"{quantidade}x {produto_selecionado.nome} adicionado à Comanda {comanda_selecionada.id}!")
            time.sleep(0.5)
            st.rerun()

        st.markdown("**Itens na Comanda Selecionada:**")
        if comanda_selecionada.itens:
            itens_data = []
            for item in comanda_selecionada.itens:
                subtotal = item.quantidade * item.preco_unitario
                itens_data.append({
                    "Qtd": item.quantidade,
                    "Produto": item.produto.nome,
                    "Preço Unit.": f"R$ {item.preco_unitario:.2f}",
                    "Subtotal": f"R$ {subtotal:.2f}"
                })
            
            st.dataframe(
                itens_data,
                hide_index=True, 
                use_container_width=True 
            )
        else:
            st.info("Nenhum item adicionado a esta comanda ainda.")


# Exibição das Comandas 
with tab_comandas:
    st.markdown("<h2 style='text-align: lefth; color: #000000;'>Comandas</h2>", unsafe_allow_html=True)
    st.subheader("Visualizar Comandas")

    col_filtro_status, col_filtro_itens = st.columns(2)
    with col_filtro_status:
        status_options = ["TODAS"] + [s.value for s in Status]
        filtro_status = st.selectbox("Filtrar por Status", options=status_options, key="filtro_status")
    
        st.markdown("<br>", unsafe_allow_html=True) # Espaçamento para alinhar com o selectbox
        filtro_com_itens = st.checkbox("Mostrar apenas comandas com pedidos", key="filtro_com_itens")

    query = gc.session.query(Comanda) 

    # 1. Aplica o filtro de STATUS
    if filtro_status != "TODAS":
        try:
            status_enum_obj = next(s for s in Status if s.value == filtro_status)
            query = query.filter(Comanda.status == status_enum_obj)
        except StopIteration:
            pass

    if filtro_com_itens:
        query = query.filter(Comanda.itens.any()) 

    todas_comandas = query.order_by(desc(Comanda.data_abertura)).all()
    if todas_comandas:
        for comanda in todas_comandas:
            total = gc.calcular_total_comanda(comanda.id)
            
            with st.expander(f"Comanda #{comanda.id} | Mesa {comanda.mesa_numero} | Status: {comanda.status.value} | Total: R$ {total:.2f}"):               
                st.write(f"**Data de Abertura:** {comanda.data_abertura.strftime('%d/%m/%Y %H:%M')}")
                st.write(f"**Data de Fechamento:** {comanda.data_fechamento.strftime('%d/%m/%Y %H:%M') if comanda.data_fechamento else 'Aberto'}")
                st.write(f"**Status:** {comanda.status.value}")
                
                st.markdown("---")
                st.write(f"**Itens da Comanda {comanda.id}:**")
                if comanda.itens:
                    # Cria uma lista para armazenar os dados dos itens
                    itens_data = []                    
                    for item in comanda.itens:
                        subtotal = item.quantidade * item.preco_unitario

                        itens_data.append({
                            "Qtd": item.quantidade,
                            "Produto": item.produto.nome,
                            "Preço Unit.": f"R$ {item.preco_unitario:.2f}",
                            "Subtotal": f"R$ {subtotal:.2f}"
                        })
                        
                    # Exibe a lista de dicionários como uma tabela interativa
                    st.dataframe(
                        itens_data,
                        hide_index=True, 
                        use_container_width=True 
                    )
                    
                else:
                    st.write("Nenhum item nesta comanda.")
                
                col_acoes1, col_acoes2 = st.columns(2)
                
                with col_acoes1:
                    if comanda.status == Status.aberta and st.button("Encerrar Comanda", key=f"encerrar_{comanda.id}"):
                        gc.fechar_comanda(comanda.id)
                        st.success(f"Comanda {comanda.id} encerrada!")
                        time.sleep(0.5)
                        st.rerun()

                with col_acoes2:
                    if comanda.status == Status.aberta and st.button("Cancelar Comanda", key=f"cancelar_{comanda.id}"):
                        if gc.cancelar_comanda(comanda.id):
                            st.success(f"Comanda {comanda.id} cancelada e removida!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("Erro ao cancelar comanda.")

    else:
        st.info("Nenhuma comanda encontrada com o filtro selecionado.")


# Pagamento e Fechamento de Comandas
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
        
        if comanda_a_pagar and st.button(f"Confirmar Pagamento"):
            if gc.pagar_comanda(comanda_a_pagar.id):
                st.success(f"Pagamento da Comanda {comanda_a_pagar.id} efetuado com sucesso!")
                time.sleep(0.5)
            else:
                st.error("Erro ao processar pagamento.")
                time.sleep(0.5)
            st.rerun()


# Gestão de Cardápio
with tab_produtos:
    st.header("Gestão de Cardápio")
    
    col1, col2 = st.tabs(["Cadastro", "Atualização"])

# --- COLUNA 1: CADASTRO ---
    with col1:
        st.subheader("Cadastro de Novo Produto")
        
        with st.form("form_novo_produto"):
            novo_nome = st.text_input("Nome do Produto", max_chars=100).capitalize()
            novo_preco = st.number_input("Preço (R$)", min_value=0.01, format="%.2f", value=10.00)
            submitted = st.form_submit_button("Cadastrar Produto")
            
            if submitted:
                if novo_nome and novo_preco:
                    gc.adicionar_produto(novo_nome, novo_preco)
                    st.success(f"Produto '{novo_nome}' cadastrado!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Preencha todos os campos.")

    # --- COLUNA 2: ATUALIZAÇÃO ---
    with col2:
        st.subheader("Atualizar Produto")
        
        with st.form("Atualizar_produto"):
            produto_id = st.number_input("ID do Produto a Atualizar", min_value=1, step=1)
            novo_nome_att = st.text_input("Novo Nome do Produto", max_chars=100).capitalize()
            novo_preco_att = st.number_input("Novo Preço (R$)", min_value=0.01, format="%.2f", value=10.00)
            atualizar_submitted = st.form_submit_button("Atualizar Produto")

            if atualizar_submitted:
                if produto_id and novo_nome_att and novo_preco_att:
                    gc.atualizar_produto(produto_id, novo_nome_att, novo_preco_att)
                    st.success(f"Produto ID {produto_id} atualizado!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Preencha todos os campos.")

                    
    st.markdown("---")
    st.subheader("Cardápio Atual")
    produtos_atuais = gc.listar_produtos()
    if produtos_atuais:
        produtos_data = [{"ID": p.id, "Nome": p.nome, "Preço": f"R$ {p.preco:.2f}"} for p in produtos_atuais]

        st.dataframe(
            produtos_data, 
            hide_index=True,  
            use_container_width=True 
        )
        
    else:
        st.info("Nenhum produto cadastrado.")