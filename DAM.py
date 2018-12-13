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

def DAM():
    DAM=[]

    real_demand = session.query(
            Order.IDPROD,
            func.year(Order.DATAPED),
            func.month(Order.DATAPED),
            func.sum(Order.QTDE)
        ).group_by(
            Order.IDPROD,
            func.year(Order.DATAPED),
            func.month(Order.DATAPED)
        ).all()
    aux_data=[] #data for standard deviation calculation
    i=0

    for demand in real_demand:
        aux_data.append(demand[3])
        i+=1

        if(i==3):
            if(demand[2]<4):
                tri=1
            elif(demand[2]<7):
                tri=2
            elif(demand[2]<10):
                tri=3
            else:
                tri=4

            DAM.append([statistics.stdev(aux_data),
                demand[1],
                tri, demand[0]
            ])
            aux_data=[]
            i=0

    for dam in DAM:
        time = session.query(TimeDimension).filter(TimeDimension.TRIMESTRE == dam[2], TimeDimension.ANO == dam[1]).first()
        if (time is None):
            time = TimeDimension(TRIMESTRE = dam[2], ANO = dam[1])
            session.add(time)
            session.commit()
        time = session.query(TimeDimension.ID).filter(TimeDimension.TRIMESTRE == dam[2], TimeDimension.ANO == dam[1]).first()

        statement = insert(InventoryControlFact). values(IDPROD = dam[3], DAM = float(dam[0]), IDTEMPO = time[0]).on_duplicate_key_update(DAM = float(dam[0]))
        engine.execute(statement)
        session.commit()
    return DAM

DAM()
