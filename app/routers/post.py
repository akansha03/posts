from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schema, utils
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix = "/posts", tags=['Posts'])
 
@router.get("/", response_model=List[schema.Post])
def get_posts(db: Session = Depends(get_db)):
    #cursor.execute("""SELECT * FROM posts""")
    #posts = cursor.fetchall()

    posts = db.query(models.Post).all()
    return posts

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.Post)
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


@router.get("/{id}", response_model=schema.Post)
def get_post(id: int, db: Session = Depends(get_db)):
    #cursor.execute("""SELECT * FROM posts where id = %s""", str(id))
    #post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} was not found')
    return post

@router.put("/{id}", response_model=schema.Post)
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

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
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