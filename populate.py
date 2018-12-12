import os
import csv
import uuid
import random
from datetime import date
import names
from sqlalchemy.orm import *
from classes import *

engine = create_engine('mysql+mysqlconnector://'+
        os.environ.get('MYSQL_USER', 'root')+':'+
        os.environ.get('MYSQL_PASSWORD','')+'@'+
        os.environ.get('MYSQL_HOST','127.0.0.1')+'/dw', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

def import_product_table():
#IDPROD,DESCRICAO,Valor                R$,,PRECO,DEMANDA MEDIA MENSAL
    with open ('PRODUTO.csv') as product_file:
        products = csv.reader(product_file, delimiter=',', quotechar='"')
        i=0
        product_to_operate = []
        for product in products:
            product_to_operate += [product]
            i += 1
            if i == 100:
                break
    return product_to_operate

def generate_users():
    #[IDUSUARIO, NOME, SOBRENOME, SEXO]
    user_list = []
    for i in range(0,200):
        item = []
        item.append(uuid.uuid4().hex)
        gender = bool(random.getrandbits(1))
        if (gender):
            item.append(names.get_first_name(gender='male'))
            item.append(names.get_last_name())
            item.append('MALE')
        else:
            item.append(names.get_first_name(gender='female'))
            item.append(names.get_last_name())
            item.append('FEMALE')
        user_list.append(item)
    return user_list

def generate_orders(product_list, user_list):
    #["IDPROD","IDUSUARIO","DATAPED","QTDE","VALOR"]
    list_orders = []
    for product in product_list:
        for year in range(2016,2018):
            for month in range(1,13):
                num_elements = random.randint(1,10) #number of orders per month
                monthly_demand = int(product[5]) #monthly mean demand
                for i in range(0,num_elements):
                    item = []
                    item.append(product[0])
                    item.append(user_list[random.randint(0,len(user_list) - 1)][0])
                    item.append(date(year, month, random.randint(1,28)))
                    random_deviation = random.randint(-4,4)
                    qtd = (monthly_demand/num_elements)+(random_deviation)
                    item.append(qtd)
                    item.append(qtd * float(str(product[4]).replace(",", "")))
                    list_orders.append(item)
    return list_orders


def generate_provision(product_list):
    #[IDPROD, DATACOMP, DATAARREC, QTDE,VALOR]
    provision_list = []
    for product in product_list:
        num_orders = random.randint(1,10)
        qtd_total = int(product[5]) * num_orders
        for order in range(0,num_orders):
           item = []
           item.append(product[0])
           order_date = date(random.randint(2016,2017), random.randint(1,12), random.randint(1,27))
           item.append(order_date)

           while True:
               arrival_date = date(order_date.year, random.randint(order_date.month,min(order_date.month+3,12)), random.randint(1,28))
               if order_date < arrival_date:
                   item.append(arrival_date)
                   break

           qtd = int(random.uniform(0, qtd_total - 5*num_orders)) + 5
           qtd_total -= qtd
           item.append(qtd)
           item.append(qtd*float(product[2]))
           provision_list.append(item)
    return provision_list

def populate_tables():
    user_list = generate_users()
    for item in user_list:
    #[IDUSUARIO, NOME, SOBRENOME, SEXO]
       user = User(
               IDUSUARIO = item[0],
               NOME = item[1],
               SOBRENOME = item[2],
               SEXO = item[3])
       session.add(user)
    session.commit()
    product_list = import_product_table()
    for item in product_list:
    #IDPROD,DESCRICAO,Valor                R$,,PRECO,DEMANDA MEDIA MENSAL
        prod = Product(
                IDPROD = item[0],
                DESCRICAO = item[1],
                VALOR = item[2],
                PRECO = item[4],
                DEMANDA_MEDIA = item[5])
        session.add(prod)
    session.commit()
    order_list = generate_orders(product_list, user_list)
    #["IDPROD","IDUSUARIO","DATAPED","QTDE","VALOR"]
    for item in order_list:
        order = Order(
            IDPROD = item[0],
            IDUSUARIO = item[1],
            DATAPED = item[2],
            QTDE = item[3],
            VALOR = item[4])
        session.add(order)
    session.commit()
    provision_list = generate_provision(product_list)
    for item in provision_list:
    #[IDPROD, DATACOMP, DATAARREC, QTDE,VALOR]
        provision = Provision(
                IDPROD = item[0],
                DATACOMP = item[1],
                DATAARREC = item[2],
                QTDE = item[3],
                VALOR = item[4])
        session.add(provision)
    session.commit()
    print('DB was populated with success')

populate_tables()
