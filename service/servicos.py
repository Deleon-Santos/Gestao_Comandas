
from datetime import datetime
from models.models import Produto, Comanda, ItemComanda, Status


class GerenciadorComandas:
    def __init__(self, session):
        self.session = session

    # --- Métodos de Produto ---

    def adicionar_produto(self, nome, preco):
        """Adiciona um novo produto ao cardápio."""
        try:
            novo_produto = Produto(nome=nome, preco=preco)
            self.session.add(novo_produto)
            self.session.commit()
            print(f"Produto '{nome}' adicionado com sucesso.")
            return novo_produto
        except Exception as e:
            self.session.rollback()
            print(f"Erro ao adicionar produto: {e}")
            return None

    def listar_produtos(self):
        """Lista todos os produtos no cardápio."""
        return self.session.query(Produto).all()

    # --- Métodos de Comanda ---

    def criar_comanda(self, mesa_numero):
        """Cria uma nova comanda para uma mesa."""
        nova_comanda = Comanda(mesa=mesa_numero)
        self.session.add(nova_comanda)
        self.session.commit()
        print(f"\nComanda #{nova_comanda.id} para Mesa {mesa_numero} criada.")
        return nova_comanda

    def adicionar_item_a_comanda(self, comanda_id, produto_id, quantidade=1):
        """Adiciona um item a uma comanda existente."""
        comanda = self.session.get(Comanda, comanda_id)
        produto = self.session.get(Produto, produto_id)

        if not comanda or not produto:
            print("Comanda ou Produto não encontrado.")
            return

        if comanda.status != Status.aberta:
             print(f"Não é possível adicionar itens. Comanda está {comanda.status.value}.")
             return

        # Garante que o preço unitário seja o preço atual do produto no momento do pedido
        novo_item = ItemComanda(
            comanda_id=comanda_id,
            produto_id=produto_id,
            quantidade=quantidade,
            preco_unitario=produto.preco
        )
        self.session.add(novo_item)
        self.session.commit()
        print(f"-> {quantidade}x '{produto.nome}' adicionado à Comanda #{comanda_id}.")

    def calcular_total_comanda(self, comanda_id):
        """Calcula o valor total de uma comanda."""
        comanda = self.session.get(Comanda, comanda_id)
        if not comanda:
            return 0.0

        total = sum(item.quantidade * item.preco_unitario for item in comanda.itens)
        return total

    def fechar_comanda(self, comanda_id):
        """Fecha a comanda, definindo a data de fechamento e status."""
        comanda = self.session.get(Comanda, comanda_id)
        if not comanda:
            return False

        if comanda.status == Status.aberta:
            comanda.status = Status.fechada
            comanda.data_fechamento = datetime.now()
            self.session.commit()
            print(f"Comanda #{comanda_id} Fechada. Total a pagar: R$ {self.calcular_total_comanda(comanda_id):.2f}")
            return True
        else:
            print(f"Comanda #{comanda_id} já está {comanda.status.value}.")
            return False