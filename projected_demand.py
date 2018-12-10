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

def projected_demand():
    product_list = session.query(func.distinct(OrderFact.IDPROD)).all()
    dp_mm_list = []
    dp_ae_list = []
    dp_rl_list = []
    product = product_list[0]

    xy = 0
    cont = 0
    x = 0
    y = 0
    x2 = 0
    y2 = 0
    for year in range(2016,2019):
        for trim in range (1, 5):
            if (year == 2018 and trim>1):
                dp_ae_list.pop(0)
                break
            elif (not(year == 2016 and trim == 1)):
                dp_mm_list.append(dp_mm(product[0], year, trim))
                dp_ae_list.append(dp_ae(product[0], year, trim, dp_ae_list[-1][3]))
                [xy, cont, x, y, x2, y2, dp_rl_actual] = dp_rl(product[0], year, trim, xy, cont, x, y, x2, y2)
                dp_rl_list.append(dp_rl_actual)
            else:
                actual_demand = real_retroactive_demand(product[0], year, trim, 0)
                [xy, cont, x, y, x2, y2] = [1.0 * actual_demand, 1, 1.0, actual_demand, 1.0, actual_demand * actual_demand]
                dp_ae_list.append([product[0], year, trim, actual_demand])
    print(product[0])
    print(dp_mm_list)
    print()
    print(dp_ae_list)
    print()
    print(dp_rl_list)

def real_retroactive_demand(product, year, trimester, num):
    demand = None
    if ((trimester - num)<1):
        year = year - 1
        num = 4 + (trimester - num)
        demand = session.query(OrderFact.DEMANDA_REAL).filter(OrderFact.ANO == year, OrderFact.TRIMESTRE == num, OrderFact.IDPROD == product).first()
    else:
        num = trimester - num
        demand = session.query(OrderFact.DEMANDA_REAL).filter(OrderFact.ANO == year, OrderFact.TRIMESTRE == num, OrderFact.IDPROD == product).first()

    if demand is None:
        return int(0)
    else:
        return int(demand[0])

def dp_mm(product, year, trim):
    cont = 0
    dpmm = 0
    for i in range(1,5):
        demand_on_trimester = real_retroactive_demand(product,year,trim,i)
        if demand_on_trimester > 0:
            cont += 1
            dpmm += demand_on_trimester
    return [product, year, trim, dpmm/float(cont)]

def dp_ae(product, year, trimester, dp_minus_one):
    alpha = 0.5
    real_demand = real_retroactive_demand(product,year,trimester,1)
    return [product, year, trimester, alpha * real_demand + (1 - alpha) * dp_minus_one]

def dp_rl(product, year, trim, xy, cont, x, y, x2, y2):
    cont += 1
    x += cont
    actual_y = real_retroactive_demand(product, year, trim, 1)
    y += actual_y
    xy += cont * actual_y
    x2 += cont * cont
    y2 += actual_y * actual_y
    beta = (cont * xy - x*y) / float(cont*x2 - x*x)
    alpha = (y/cont) - (x/cont) * beta
    dp_rl_plus_one = [product, year, trim, alpha + beta * cont]
    return [xy, cont, x, y, x2, y2, dp_rl_plus_one]
projected_demand()
