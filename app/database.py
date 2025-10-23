from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor
import time 
from .config import settings

SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# To work with the database, use session local

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()    

def connect_db_driver():
    while True:
        try:
            conn = psycopg2.connect(host ='localhost', port=5433, database='fastapi-posts', user='postgres', password='admin123', cursor_factory=RealDictCursor)
            cursor = conn.cursor()
            print("Databse Connection Successful")
            break
        except Exception as error:
            print('Connection failed!')  
            print('Error:' , error)  
            time.sleep(2)