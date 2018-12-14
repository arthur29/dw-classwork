import os
from datetime import date
from sqlalchemy import *
from sqlalchemy.orm import *
from classes import *
from sqlalchemy import func
from sqlalchemy.dialects.mysql import insert

engine = create_engine('mysql+mysqlconnector://'+
        os.environ.get('MYSQL_USER', 'root')+':'+
        os.environ.get('MYSQL_PASSWORD','')+'@'+
        os.environ.get('MYSQL_HOST','127.0.0.1')+'/dw', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

def min_max_trimester(trim):
    min = 0
    max = 0
    if trim == 1:
        min = 1
        max = 3
    elif trim == 2:
        min = 4
        max = 6
    elif trim == 3:
        min = 7
        max = 9
    else:
        min = 10
        max = 12
    return [min,max]

def average_demand():
    total_orders = session.query(
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
    mean_list = []
    for total in total_orders:
        #[IDPROD, YEAR, TRIMESTER, AVERAGE_DEMAND]
        mean_list.append([total[0], total[2], total[1], float(total[3])/3.0])
    return mean_list

def ressuply_level():
    demand_list = average_demand()
    for demand in demand_list:
        time = session.query(TimeDimension.ID).filter(
                TimeDimension.ANO == demand[1],
                TimeDimension.TRIMESTRE == demand[2]).first()
        time = time[0]

        invent = session.query(InventoryControlFact).filter(
                InventoryControlFact.IDTEMPO == time,
                InventoryControlFact.IDPROD == demand[0]
            ).first()
        nrs = demand[3] * invent.TPA + invent.NS

        statement = insert(InventoryControlFact).values(IDPROD = demand[0], NRS = nrs, IDTEMPO = time).on_duplicate_key_update(NRS = nrs)
        engine.execute(statement)
        session.commit()
ressuply_level()
