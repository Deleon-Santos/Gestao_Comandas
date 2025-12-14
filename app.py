


from config.config import session, engine, Base
from service.servicos import GerenciadorComandas


if __name__ == '__main__':
    # 1. Garante que as tabelas existam no SQLite
    print("Criando tabelas no DB...")
    Base.metadata.create_all(engine)
    
    # Instancia o gerenciador de comandos
    gc = GerenciadorComandas(session)

    # 2. Adiciona Produtos
    print("\n--- Cadastro de Produtos ---")
    gc.adicionar_produto("Refrigerante Cola", 6.00)
    gc.adicionar_produto("Porção de Batata Frita", 25.50)
    gc.adicionar_produto("Hamburger Gourmet", 35.00)
    
    produtos = gc.listar_produtos()
    print("\nProdutos Atuais:")
    for p in produtos:
        print(p)

    # 3. Cria e Gerencia Comandas
    
    # Comanda para Mesa 5
    comanda1 = gc.criar_comanda(mesa_numero=5)
    
    # Adiciona itens usando os IDs dos produtos
    # Refri ID=1, Batata ID=2, Burger ID=3 (assumindo a ordem de inserção)
    gc.adicionar_item_a_comanda(comanda1.id, 1, quantidade=2) # 2x Refri
    gc.adicionar_item_a_comanda(comanda1.id, 3, quantidade=1) # 1x Burger

    # Comanda para Mesa 10
    comanda2 = gc.criar_comanda(mesa_numero=10)
    gc.adicionar_item_a_comanda(comanda2.id, 2, quantidade=3) # 3x Batata

    # 4. Cálculo e Fechamento
    
    print("\n--- Fechamento da Comanda 1 ---")
    total1 = gc.calcular_total_comanda(comanda1.id)
    print(f"Total da Comanda {comanda1.id} (Mesa {comanda1.mesa_numero}): R$ {total1:.2f}")

    gc.fechar_comanda(comanda1.id)
    
    # Tenta adicionar item em comanda fechada
    gc.adicionar_item_a_comanda(comanda1.id, 1, quantidade=1)
    
    print("\n--- Fechamento da Comanda 2 ---")
    total2 = gc.calcular_total_comanda(comanda2.id)
    print(f"Total da Comanda {comanda2.id} (Mesa {comanda2.mesa_numero}): R$ {total2:.2f}")
    gc.fechar_comanda(comanda2.id)