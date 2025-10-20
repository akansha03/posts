from typing import Optional, List
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schema, utils
from ..database import get_db
from sqlalchemy.orm import Session
 
router = APIRouter(prefix="/users", tags=['Users'])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.UserOut)
def create_a_user(user: schema.UserCreate, db: Session = Depends(get_db)):   

    # hash the password
    encrypted_pass = utils.hash(user.password)
    user.password = encrypted_pass
    new_user = models.User(**user.dict()) 

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/{id}", response_model=schema.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, details=f"User with id: {id} doesnot exist")
    return user