from typing import Optional, List
from random import randrange
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends
import psycopg2
from psycopg2.extras import RealDictCursor
import time 
from . import models, schema, utils
from .database import engine, SessionLocal
from sqlalchemy.orm import Session
from .routers import post, user, auth

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# @ is the decorator and app is the FastAPI instance 

'''
Two Requests comes in with same paths - "/", then the API first in order will be hit
'''
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


my_posts = [{"title" : "title of post 1", "content" : "content of post 1", "id" : 1},
            {"title" : "favorite foods", "content" : "I like pizzas and burgers", "id" : 2}]    

def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p

def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i       

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

