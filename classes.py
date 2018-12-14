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
    VALOR = Column(Float)

class Provision(Base):
    #[IDPROD, DATACOMP, DATAARREC, QTDE,VALOR]
    __tablename__ = 'COMPRA'
    IDCOMPRA = Column(Integer, primary_key=True, autoincrement=True)
    IDPROD = Column(String(length=100), ForeignKey("PRODUTO.IDPROD"))
    DATACOMP = Column(Date)
    DATAARREC = Column(Date)
    QTDE = Column(Integer)
    VALOR = Column(Float)

class TimeDimension(Base):
    __tablename__ = "DW_DIMENSAO_TEMPO"
    ID = Column(Integer, primary_key=True)
    ANO = Column(Integer)
    TRIMESTRE = Column(Integer)

class NumOrdersFact(Base):
    __tablename__ = "DW_TOTAL_PEDIDO"
    IDPROD = Column(String(length=100), ForeignKey("PRODUTO.IDPROD"), primary_key=True)
    IDTEMPO = Column(Integer, ForeignKey("DW_DIMENSAO_TEMPO.ID"), primary_key=True)
    TOTAL_PEDIDO = Column(Float)

class ProjectedDemandFact(Base):
    __tablename__ = "DW_PROJECAO_DEMANDA"
    IDPROD = Column(String(length=100), ForeignKey("PRODUTO.IDPROD"), primary_key=True)
    IDTEMPO = Column(Integer, ForeignKey("DW_DIMENSAO_TEMPO.ID"), primary_key=True)
    QTDE = Column(Integer)
    DEMANDA_PROJETADA = Column(Float)

class InventoryControlFact(Base):
    __tablename__ = "DW_CONTROLE_INVENTARIO"
    IDPROD = Column(String(length=100), ForeignKey("PRODUTO.IDPROD"), primary_key=True)
    IDTEMPO = Column(Integer, ForeignKey("DW_DIMENSAO_TEMPO.ID"), primary_key=True)
    NS  = Column(Float)
    NRS = Column(Float)
    TPA = Column(Integer)
    DAM = Column(Float)
