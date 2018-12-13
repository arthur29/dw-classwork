import os
from datetime import date,datetime
from sqlalchemy import *
from sqlalchemy.orm import *
from classes import *
from collections import namedtuple
from sqlalchemy.dialects.mysql import insert
import time as timer

engine = create_engine('mysql+mysqlconnector://'+
        os.environ.get('MYSQL_USER', 'root')+':'+
        os.environ.get('MYSQL_PASSWORD','')+'@'+
        os.environ.get('MYSQL_HOST','127.0.0.1')+'/dw', echo=True)

Session = sessionmaker(bind=engine)
session = Session()

def lead_time():
    product_list = session.query(Provision.IDPROD).distinct(Provision.IDPROD).all()
    for product in product_list:
        for year in range(2016,2018):
            for trimester in range(1,5):
                if year == 2018 and trimester > 1:
                    break
                else:
                    min = 0
                    max = 0
                    if trimester == 1:
                        min = 1
                        max = 3
                    elif trimester == 2:
                        min = 4
                        max = 6
                    elif trimester == 3:
                        min = 7
                        max = 9
                    else:
                        min = 10
                        max = 12

                provision_time = session.query(Provision.DATACOMP, Provision.DATAARREC).filter(func.month(Provision.DATACOMP) >= min, func.month(Provision.DATACOMP) <= max, Provision.IDPROD == product[0]).all()

                total_time = 0
                for item in provision_time:
                    total_time += abs(item[1] - item[0]).days
                time = session.query(TimeDimension).filter(TimeDimension.TRIMESTRE == trimester, TimeDimension.ANO == year).first()
                if (time is None):
                    time = TimeDimension(TRIMESTRE = trimester, ANO = year)
                    session.add(time)
                    session.commit()
                time = session.query(TimeDimension.ID).filter(TimeDimension.TRIMESTRE == trimester, TimeDimension.ANO == year).first()

                statement = insert(InventoryControlFact). values(IDPROD = product[0], TPA = total_time, IDTEMPO = time[0]).on_duplicate_key_update(TPA = total_time)
                engine.execute(statement)
                session.commit()
lead_time()
