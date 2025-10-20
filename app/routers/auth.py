from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from .. import database, models, schema, utils

router = APIRouter(tags=['Authentication'])

@router.post('/login')
def login(user_credentials: schema.UserLogin, db: Session=Depends(database.get_db)):
    
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credentials")

    flag = utils.verify(user_credentials.password, user.password)    
    if not flag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credentials")

    return {"token" : "Sample token"}


