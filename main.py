from typing import Optional, Union
from random import randrange
from fastapi import Body, FastAPI, Response, status, HTTPException
from pydantic import BaseModel
app = FastAPI()

# @ is the decorator and app is the FastAPI instance 

'''
Two Requests comes in with same paths - "/", then the API first in order 
will be hit
'''
class Posts(BaseModel):
    title: str
    content: str
    published: bool = True #optional field - default to True
    rating: Optional[int] = None

my_posts = [{"title" : "title of post 1", "content" : "content of post 1", "id" : 1},
            {"title" : "favorite foods", "content" : "I like pizzas and burgers", "id" : 2} ]    

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

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/posts")
def get_posts():
    return {"data" : my_posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Posts, response: Response):
    #this will print the dictionary data - dict() is depreceated so model_dump() will be used
    #print(post.model_dump()) 
    post_dict = post.model_dump()
    post_dict['id'] = randrange(0, 1000000)
    my_posts.append(post_dict)
    return {"data" : post_dict}

@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} was not found')
        #response.status_code = status.HTTP_404_NOT_FOUND
        #return {'message' : f'post with id: {id} was not found'}
    return {"post_detail" :  post}

@app.put("/posts/{id}")
def update_post(id: int, update_post: Posts):
    post = find_post(id)
    update_post_dict = update_post.model_dump()

    post['title'] = update_post_dict['title']
    post['content'] = update_post_dict['content']
    return {"Updated Post Detail" : post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def update_post(id: int):
    index = find_index_post(id)
    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} was not found')
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
