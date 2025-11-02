
from fastapi import FastAPI
from . import models
from .database import engine
from .routers import post, user, auth, vote
from .config import settings
from fastapi.middleware.cors import CORSMiddleware

# Not needed with alembic
# models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# all domains have access 

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @ is the decorator and app is the FastAPI instance 
'''
Two Requests comes in with same paths - "/", then the API first in order will be hit - python runs from top to bottom
'''
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/")
def root():
    return {"message" : "Hello Akansha ! deployed to CI/CD"}
