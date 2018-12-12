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

OrderFact.__table__.drop(engine, checkfirst=True)
OrderFact.__table__.create(engine, checkfirst=True)

def real_demand():
    real_demand = session.query(
        Order.IDPROD,
            case([
            (func.month(Order.DATAPED) < 4, 1),
            (func.month(Order.DATAPED) < 7, 2),
            (func.month(Order.DATAPED) < 10, 3)
            ],
            else_=4),
            func.year(Order.DATAPED),
        func.sum(Order.QTDE)
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
    for demand in real_demand:
        order = OrderFact(IDPROD = demand[0], TRIMESTRE = demand[1], ANO = demand[2], DEMANDA_REAL = float(demand[3]))
        session.add(order)
    session.commit()

    print (real_demand[:3])
real_demand()
