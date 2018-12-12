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

def projected_demand():
    product_list = session.query(func.distinct(OrderFact.IDPROD)).all()
    dp_mm_list = []
    dp_ae_list = []
    dp_rl_list = []
    for product in product_list:

        best = [0]*3
        for year in range(2016,2019):
            num = 0
            for trim in range (1, 5):
                if (year == 2018 and trim>1):
                    dp_ae_list.pop(0)
                    break
                elif (not(year == 2016 and trim == 1)):
                    dp_mm_list.append(dp_mm(product[0], year, trim))
                    dp_ae_list.append(dp_ae(product[0], year, trim, dp_ae_list[-1][3]))
                    num +=1
                    dp_rl_list.append(dp_rl(product[0], year, trim, num))
                    best = better_between_projects(dp_mm_list[-1], dp_ae_list[-1], dp_rl_list[-1], best)
                else:
                    actual_demand = real_retroactive_demand(product[0], year, trim, 0)
                    [xy, cont, x, y, x2, y2] = [1.0 * actual_demand, 1, 1.0, actual_demand, 1.0, actual_demand * actual_demand]
                    dp_ae_list.append([product[0], year, trim, actual_demand])

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
    elif demand[0] is None:
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

def dp_rl(product, year, trim, num):

    xy = 0
    cont = 0
    x = 0
    y = 0
    x2 = 0
    y2 = 0
    if (num>4):
        num = 4
    for i in range(1,num+1):
        actual_y = real_retroactive_demand(product, year, trim, (num+1)-i)
        if (actual_y != 0):
            cont += i
            x += cont
            y += actual_y
            xy += cont * actual_y
            x2 += cont * cont
            y2 += actual_y * actual_y
    try:
        beta = (cont * xy - x*y) / float(cont*x2 - x*x)
        alpha = (y/cont) - (x/cont) * beta
        dp_rl_plus_one = [product, year, trim, alpha + beta * cont]
        return dp_rl_plus_one
    except ZeroDivisionError:
        return [product, year, trim, 0]

def better_between_projects(dp_mm, dp_ae, dp_rl, best):
    real_demand = real_retroactive_demand(dp_mm[0],dp_mm[1], dp_mm[2],0)
    insert_dp = 0
    if (real_demand != 0):
        dp = [None, None]*3
        dp[0] = [dp_mm[3] - real_demand, dp_mm[3]]
        dp[1] = [dp_ae[3] - real_demand, dp_ae[3]]
        dp[2] = [dp_rl[3] - real_demand, dp_rl[3]]
        if (dp[2][1] != 0 ):
            for i in range(0,3):
                best[i] += dp[i][0]
            better = best[0]
            insert_dp = dp[0][1]
            for i in range(1,3):
                if (best[i] < better):
                    better = best[i]
                    insert_dp = dp[i][1]
        else:
            if (dp[0][0] < dp[1][0]):
                insert_dp = dp[0][1]
            else:
                insert_dp = dp[1][1]
    else:
        dp = [0]*3
        dp[0] = dp_mm[3]
        dp[1] = dp_ae[3]
        dp[2] = dp_rl[3]
        smaller = best[0]
        insert_dp = dp[0]
        for i in range(1,3):
            if (best[i] < smaller):
                smaller = best[i]
                insert_dp = dp[i]
    statement = insert(OrderFact).values(IDPROD = dp_mm[0], ANO = dp_mm[1], TRIMESTRE = dp_mm[2], DEMANDA_PROJETADA = insert_dp).on_duplicate_key_update(DEMANDA_PROJETADA = insert_dp)
    engine.execute(statement)
    session.commit()
    return best
projected_demand()
