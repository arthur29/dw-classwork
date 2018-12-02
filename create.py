import os
from sqlalchemy import *

engine = create_engine('mysql+mysqlconnector://'+
        os.environ.get('MYSQL_USER', 'root')+':'+
        os.environ.get('MYSQL_PASSWORD','')+'@'+
        os.environ.get('MYSQL_HOST','127.0.0.1'), echo=True)
engine.execute("DROP DATABASE IF EXISTS dw")
engine.execute("CREATE DATABASE dw") #create db
