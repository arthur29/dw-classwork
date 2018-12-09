from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):
#IDPROD,DESCRICAO,Valor                R$,,PRECO,DEMANDA MEDIA MENSAL
    __tablename__ = 'PRODUTO'
    IDPROD = Column(String(length=100), primary_key = True)
    DESCRICAO = Column(String(length=100))
    VALOR = Column(Float)
    PRECO = Column(Float)
    DEMANDA_MEDIA = Column(Integer)

class User(Base):
    #[IDUSUARIO, NOME, SOBRENOME, SEXO]
    __tablename__ = 'USUARIO'
    IDUSUARIO = Column(String(length=100), primary_key = True)
    NOME = Column(String(length=100))
    SOBRENOME = Column(String(length=100))
    SEXO = Column(String(6))

class Order(Base):
    #["IDPROD","IDUSUARIO","DATAPED","QTDE","VALOR"]
    __tablename__ = 'PEDIDO'
    IDPEDIDO = Column(Integer, primary_key=True, autoincrement=True)
    IDPROD = Column(String(length=100), ForeignKey("PRODUTO.IDPROD"))
    IDUSUARIO = Column(String(length=100), ForeignKey("USUARIO.IDUSUARIO"))
    DATAPED = Column(Date)
    QTDE = Column(Integer)
    VALOR = column(Float)

class Provision(Base):
    #[IDPROD, DATACOMP, DATAARREC, QTDE,VALOR]
    __tablename__ = 'COMPRA'
    IDCOMPRA = Column(Integer, primary_key=True, autoincrement=True)
    IDPROD = Column(String(length=100), ForeignKey("PRODUTO.IDPROD"))
    DATACOMP = Column(Date)
    DATAARREC = Column(Date)
    QTDE = Column(Integer)
    VALOR = column(Float)

class OrderFact(Base):
    __tablename__ = "DW_Pedido"
    IDPROD = Column(String(length=100), ForeignKey("PRODUTO.IDPROD"), primary_key=True)
    TRIMESTRE = Column(Integer, primary_key=True)
    ANO = Column(Integer, primary_key=True)
    DEMANDA_REAL=Column(Integer)
    PROJECTED_DEMAND = Column(Float)
