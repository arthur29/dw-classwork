import os
from datetime import date
from sqlalchemy import *
from sqlalchemy.orm import *
from classes import *
from sqlalchemy.dialects.mysql import insert
from collections import namedtuple

engine = create_engine('mysql+mysqlconnector://'+
        os.environ.get('MYSQL_USER', 'root')+':'+
        os.environ.get('MYSQL_PASSWORD','')+'@'+
        os.environ.get('MYSQL_HOST','127.0.0.1')+'/dw', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

def absError(l):
    sum=0
    for i in range(0,len(l)):
        f=l[i]#fact
        if(f["DP"]!=None):
            sum+=(f["DR"]-f["DP"]) if (f["DR"]-f["DP"])>=0 else (f["DP"]-f["DR"])
        else:
            if(len(l)!=1):
                abs_error=sum/(len(l)-1)
                return abs_error
            else:
                return sum 
    abs_error=sum/(len(l))
    return abs_error

def DAM():
    DAM= []
    list = session.query(OrderFact.ANO,OrderFact.TRIMESTRE,OrderFact.IDPROD,OrderFact.DEMANDA_REAL,OrderFact.DEMANDA_PROJETADA).all()
    facts = []

    for i in range(0,len(list)):
        facts.append(dict(Ano=list[i][0],Trimestre=list[i][1],ProdID=list[i][2],DR=list[i][3],DP=list[i][4], DAM = None))

    for i in range(0,len(facts)):
        fact = facts[i]
        if fact["Ano"]==2016:
            if fact["Trimestre"]==1:
                fact["DAM"] = absError([fact])
            elif fact["Trimestre"]==2:
                fact["DAM"] = absError([fact,facts[i-1]])
            elif fact["Trimestre"]==3:
                fact["DAM"] = absError([fact,facts[i-1],facts[i-2]])
            elif fact["Trimestre"]==4:
                fact["DAM"] = absError([fact,facts[i-1],facts[i-2],facts[i-3]])
        elif fact["Ano"]==2017:
            fact["DAM"] = absError([fact,facts[i-1],facts[i-2],facts[i-3]])
        else:
            fact["DAM"] = ""
    for fact in facts:
        statement = insert(OrderFact).values(IDPROD = fact["ProdID"], ANO = fact["Ano"], TRIMESTRE = fact["Trimestre"], DAM= fact["DAM"]).on_duplicate_key_update(DAM = fact["DAM"])

        engine.execute(statement)
    session.commit()
    return DAM

DAM()
