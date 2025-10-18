from typing import Optional, Union
from random import randrange
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time 
from . import models
from .database import engine, SessionLocal
from sqlalchemy.orm import Session
models.Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()    


# @ is the decorator and app is the FastAPI instance 

'''
Two Requests comes in with same paths - "/", then the API first in order will be hit
'''
class Posts(BaseModel):
    title: str
    content: str
    published: bool = True #optional field - default to True
    rating: Optional[int] = None

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

@app.get("/")
async def read_root():
    return {"Hello": "Welcome to my world!"}

@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):

    # query handles the select statement - so no need to write the whole select query - print posts and check it will return the select statment from posts
    posts = db.query(models.Post).all()
    return {"data": posts}    

@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data" : posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Posts, response: Response):   
    '''
    This statement might work, but this is prone to sql injection so avoid this 

    cursor.execute(f"INSERT INTO posts (title, content, published) VALUES ({post.title}, {post.content} , {post.published})")
    '''
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s ) RETURNING * """, (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data" : new_post}

@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute("""SELECT * FROM posts where id = %s""", str(id))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} was not found')
    return {"post_detail" :  post}

@app.put("/posts/{id}")
def update_post(id: int, post: Posts):
    
    cursor.execute("""UPDATE posts set title = %s , content = %s, published = %s where id = %s RETURNING *""", (post.title, post.content, post.published, id))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} doesnot exist')
    return {"data" : updated_post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def update_post(id: int):
    
    # if you cause an issue here use str(id), - append a comma
    cursor.execute("""DELETE FROM posts where id = %s RETURNING *""" , str(id))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} was not found')
    
