

import enum

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum

from config.config import Base


class Status(enum.Enum):
    aberta = "aberta"
    fechada = "fechada"
    paga = "paga"
    cancelada = "cancelada"

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    preco = Column(Float, nullable=False)

    def __repr__(self):
        return f"<Produto(id={self.id}, nome={self.nome}, preco={self.preco})>"
    
class Comanda(Base):
    __tablename__ = "comandas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    mesa_numero = Column(Integer, nullable=False)
    status = Column(Enum(Status), default=Status.aberta, nullable=False)
    itens = relationship("ItemComanda", back_populates="comanda", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Comanda(id={self.id}, mesa_numero={self.mesa_numero}, status={self.status})>" 
    
class ItemComanda(Base):
    __tablename__ = "itens_comanda"

    id = Column(Integer, primary_key=True, autoincrement=True)
    comanda_id = Column(Integer, ForeignKey("comandas.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False, default=1)

    comanda = relationship("Comanda", back_populates="itens")
    produto = relationship("Produto")

    def __repr__(self):
        return f"<ItemComanda(id={self.id}, comanda_id={self.comanda_id}, produto_id={self.produto_id}, quantidade={self.quantidade})>"