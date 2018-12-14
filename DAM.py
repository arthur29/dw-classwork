import os
from datetime import date
from sqlalchemy import *
from sqlalchemy.orm import *
from classes import *
from sqlalchemy.dialects.mysql import insert
from collections import namedtuple
import statistics

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

def DAM(demand_list):
    DAM=[]

    for demand in demand_list:
        [min,max] = min_max_trimester(demand[2])
        count_demand = session.query(
                func.count(Order.QTDE)).filter(
                Order.IDPROD == demand[0],
                func.month(Order.DATAPED) >= min,
                func.month(Order.DATAPED) <= max,
                func.year(Order.DATAPED) == demand[1]
                ).group_by(
                    case([
                    (func.month(Order.DATAPED) < 4, 1),
                    (func.month(Order.DATAPED) < 7, 2),
                    (func.month(Order.DATAPED) < 10, 3)
                    ],
                    else_=4),
                    func.year(Order.DATAPED),
                    Order.IDPROD
                ).first()
        count_demand = count_demand[0]

        all_demands = session.query(
                Order.QTDE).filter(
                Order.IDPROD == demand[0],
                func.month(Order.DATAPED) >= min,
                func.month(Order.DATAPED) <= max,
                func.year(Order.DATAPED) == demand[1]
                ).all()
        absolute_error = 0.0
        for item in all_demands:
            absolute_error += item[0] - demand[3]

        dam = absolute_error / float(count_demand)
        if dam < 0:
            dam = dam *-1
        time = session.query(TimeDimension).filter(TimeDimension.TRIMESTRE == demand[2], TimeDimension.ANO == demand[1]).first()
        if (time is None):
            time = TimeDimension(TRIMESTRE = demand[2], ANO = demand[1])
            session.add(time)
            session.commit()
        time = session.query(TimeDimension.ID).filter(TimeDimension.TRIMESTRE == demand[2], TimeDimension.ANO == demand[1]).first()

        statement = insert(InventoryControlFact). values(IDPROD = demand[0], DAM = dam, IDTEMPO = time[0]).on_duplicate_key_update(DAM = dam)
        engine.execute(statement)
        session.commit()

DAM(average_demand())
