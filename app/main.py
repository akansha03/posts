from typing import Optional, List
from random import randrange
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends
import psycopg2
from psycopg2.extras import RealDictCursor
import time 
from . import models, schema
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

@app.get("/posts", response_model=List[schema.Post])
def get_posts(db: Session = Depends(get_db)):
    #cursor.execute("""SELECT * FROM posts""")
    #posts = cursor.fetchall()

    posts = db.query(models.Post).all()
    return posts

@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schema.Post)
def create_posts(post: schema.PostCreate, db: Session = Depends(get_db)):   
    '''
    This statement might work, but this is prone to sql injection so avoid this 

    cursor.execute(f"INSERT INTO posts (title, content, published) VALUES ({post.title}, {post.content} , {post.published})")
    '''
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s ) RETURNING * """, (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    # new_post = models.Post(title=post.title, content=post.content, published=post.published)

    new_post = models.Post(**post.dict()) 
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get("/posts/{id}", response_model=schema.Post)
def get_post(id: int, db: Session = Depends(get_db)):
    #cursor.execute("""SELECT * FROM posts where id = %s""", str(id))
    #post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} was not found')
    return post

@app.put("/posts/{id}", response_model=schema.Post)
def update_post(id: int, post: schema.PostCreate, db: Session = Depends(get_db)):
    
    #cursor.execute("""UPDATE posts set title = %s , content = %s, published = %s where id = %s RETURNING *""", (post.title, post.content, post.published, id))
    #updated_post = cursor.fetchone()
    #conn.commit()
    update_post = db.query(models.Post).filter(models.Post.id == id)
    post_db = update_post.first()
    if post_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} doesnot exist')

    update_post.update(post.dict(), synchronize_session=False)
    db.commit()    
    return update_post.first()

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    
    # if you cause an issue here use str(id), - append a comma
    #cursor.execute("""DELETE FROM posts where id = %s RETURNING *""" , str(id))
    #deleted_post = cursor.fetchone()
    #conn.commit()

    post = db.query(models.Post).filter(models.Post.id == id)
    print(post)
    if post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} was not found')
    post.delete(synchronize_session=False)    
    db.commit()
    
