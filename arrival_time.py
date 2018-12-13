import os
from datetime import date
from sqlalchemy import *
from sqlalchemy.orm import *
from classes import *
from collections import namedtuple

engine = create_engine('mysql+mysqlconnector://'+
        os.environ.get('MYSQL_USER', 'root')+':'+
        os.environ.get('MYSQL_PASSWORD','')+'@'+
        os.environ.get('MYSQL_HOST','127.0.0.1')+'/dw', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
def arrival_time():
    query = session.query(OrderFact.IDPROD, OrderFact.ANO, OrderFact.TRIMESTRE).all()
    order_list = []
    for item in query:
        order_list.append(dict(ID = item[0], Year = item[1], Trimester = item[1]))

    for item in order_list:
        query = session.query(Provision.DATACOMP, Provision.DATAAREC).filter(Provision.IDPROD == item["ID"], )
