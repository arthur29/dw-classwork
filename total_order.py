import os
from datetime import date
from sqlalchemy import *
from sqlalchemy.orm import *
from classes import *
from sqlalchemy import func

engine = create_engine('mysql+mysqlconnector://'+
        os.environ.get('MYSQL_USER', 'root')+':'+
        os.environ.get('MYSQL_PASSWORD','')+'@'+
        os.environ.get('MYSQL_HOST','127.0.0.1')+'/dw', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

NumOrdersFact.__table__.drop(engine, checkfirst=True)
NumOrdersFact.__table__.create(engine, checkfirst=True)

def total_orders():
    total_orders = session.query(
        Order.IDPROD,
            case([
            (func.month(Order.DATAPED) < 4, 1),
            (func.month(Order.DATAPED) < 7, 2),
            (func.month(Order.DATAPED) < 10, 3)
            ],
            else_=4),
            func.year(Order.DATAPED),
            func.sum(Order.IDPEDIDO)
        ).group_by(
            case([
            (func.month(Order.DATAPED) < 4, 1),
            (func.month(Order.DATAPED) < 7, 2),
            (func.month(Order.DATAPED) < 10, 3)
            ],
            else_=4),
            func.year(Order.DATAPED),
            Order.IDPROD
        ).all()

    for demand in total_orders:
        time = session.query(TimeDimension).filter(TimeDimension.TRIMESTRE == demand[1], TimeDimension.ANO == demand[2]).first()
        if (time is None):
            time = TimeDimension(TRIMESTRE = demand[1], ANO = demand[2])
            session.add(time)
        time = session.query(TimeDimension).filter(TimeDimension.TRIMESTRE == time.TRIMESTRE, TimeDimension.ANO == time.ANO).first()
        order = NumOrdersFact(IDPROD = demand[0], IDTEMPO = time.ID, TOTAL_PEDIDO = demand[3])
        session.add(order)
    session.commit()
total_orders()
