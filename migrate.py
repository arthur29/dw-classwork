import os
from sqlalchemy import *
from sqlalchemy.orm import *
from classes import *

engine = create_engine('mysql+mysqlconnector://'+
        os.environ.get('MYSQL_USER', 'root')+':'+
        os.environ.get('MYSQL_PASSWORD','')+'@'+
        os.environ.get('MYSQL_HOST','127.0.0.1')+'/dw', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

def migrate():
    Base.metadata.create_all(engine)

migrate()
