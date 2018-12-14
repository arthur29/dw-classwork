import os
from datetime import date
from sqlalchemy import *
from sqlalchemy.orm import *
from classes import *
from sqlalchemy import func
from sqlalchemy.dialects.mysql import insert
import statistics
import math

engine = create_engine('mysql+mysqlconnector://'+
        os.environ.get('MYSQL_USER', 'root')+':'+
        os.environ.get('MYSQL_PASSWORD','')+'@'+
        os.environ.get('MYSQL_HOST','127.0.0.1')+'/dw', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

Z = 1.65

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

def standard_deviation_demand(demand_list):
    for demand in demand_list:
        [min,max] = min_max_trimester(demand[2])
        query = session.query(
                Order.QTDE
            ).filter(
                func.month(Order.DATAPED) >= min,
                func.month(Order.DATAPED) <= max,
                func.year(Order.DATAPED) == demand[1],
                Order.IDPROD == demand[0]
            )
        qtd_list = query.all()
        qtd_array = []
        for qtd in qtd_list:
            qtd_array.append(qtd[0])
        demand.append(statistics.stdev(qtd_array))
        #[IDPROD, YEAR, TRIMESTER, AVERAGE_DEMAND, STANDARD_DEVIATION_DEMAND]
    return demand_list

def lead_time_mean(demand_list):
    for demand in demand_list:
        [min,max] = min_max_trimester(demand[2])
        query = session.query(
                    Provision.DATACOMP,
                    Provision.DATAARREC
                ).filter(
                    Provision.IDPROD == demand[0],
                    func.month(Order.DATAPED) >= min,
                    func.month(Order.DATAPED) <= max,
                    func.year(Order.DATAPED) == demand[1]
                )
        provision_time = query.all()
        total_time = 0
        for item in provision_time:
            total_time += abs(item[1] - item[0]).days
        demand.append(total_time / float(query.count()))
    #[IDPROD, YEAR, TRIMESTER, AVERAGE_DEMAND, STANDARD_DEVIATION_DEMAND, lead_time_mean]
    return demand_list

def lead_time_standard_deviation(demand_list):
    for demand in demand_list:
        [min,max] = min_max_trimester(demand[2])
        query = session.query(
                    Provision.DATACOMP,
                    Provision.DATAARREC
                ).filter(
                    Provision.IDPROD == demand[0],
                    func.month(Order.DATAPED) >= min,
                    func.month(Order.DATAPED) <= max,
                    func.year(Order.DATAPED) == demand[1]
                )
        provision_time = query.all()
        provision_array = []
        for item in provision_time:
            provision_array.append(abs(item[1] - item[0]).days)
        demand.append(statistics.stdev(provision_array))
    #[IDPROD, YEAR, TRIMESTER, AVERAGE_DEMAND, STANDARD_DEVIATION_DEMAND, lead_time_mean, lead_time_standard_deviation]
    return demand_list

def security_level(demand_list):
    #demand = [IDPROD, YEAR, TRIMESTER, AVERAGE_DEMAND, STANDARD_DEVIATION_DEMAND, lead_time_mean, lead_time_standard_deviation]
    for demand in demand_list:
        ns = Z * math.sqrt((demand[4]* demand[4]) * demand[5] + (demand[6] * demand[6]) * (demand[3] * demand[3]))

        time = session.query(TimeDimension).filter(TimeDimension.TRIMESTRE == demand[2], TimeDimension.ANO == demand[1]).first()
        if (time is None):
            time = TimeDimension(TRIMESTRE = demand[2], ANO = demand[1])
            session.add(time)
            session.commit()
        time = session.query(TimeDimension.ID).filter(TimeDimension.TRIMESTRE == demand[2], TimeDimension.ANO == demand[1]).first()

        statement = insert(InventoryControlFact). values(IDPROD = demand[0], NS = ns, IDTEMPO = time[0]).on_duplicate_key_update(NS = ns)
        engine.execute(statement)
        session.commit()






security_level(lead_time_standard_deviation(lead_time_mean(standard_deviation_demand(average_demand()))))
