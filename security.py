from datetime import datetime, timedelta
from passlib.context import  CryptContext #pip install passlib
from jose import jwt,JWTError #https://pypi.org/project/python-jose/ = pip install python-jose
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi import Depends, APIRouter, Request, Response, status
import repositoryuser
from models import User
from sqlalchemy.orm import Session
from typing import Union
from connection import sess_db
from cookie import OAuth2PasswordBearerWithCookie
import logging
from fastapi import Form
 
SECRET_KEY="visl$§%§$vietnam"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=15
COOKIE_NAME = "Authorization"

pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto") #pip install bcrypt
# save token to oauth2_scheme
oauth2_scheme=OAuth2PasswordBearerWithCookie(tokenUrl="login")

authRouter = APIRouter()
 
# create Token
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
    
    
# create verify Token
def verify_token(token):
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])  # Đảm bảo bạn chỉ định thuật toán
        return payload
    except jwt.ExpiredSignatureError:
        logging.error("Token đã hết hạn")
        raise HTTPException(status_code=401, detail="Token đã hết hạn")
    except jwt.JWTError as e:
        logging.error(f'Lỗi verify token: {e}')
        raise HTTPException(status_code=401, detail="Token không hợp lệ")
 
# password hash
def get_password_hash(password):
    return pwd_context.hash(password)
 
# password verify
def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)
 
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(sess_db)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user: str = repositoryuser.get_user_by_username(
        db=db, username=payload.get("sub"))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user.username

def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(sess_db)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],)
    user: str = repositoryuser.get_user_by_username(db=db, username=payload.get("sub"))
    if user and user.is_Admin==True:
        return user.username
    else:
        raise HTTPException(status_code=302, detail="Not authorized", headers={"Location": "/signin"})

class OAuth2PasswordRequestFormWithEmail:
    def __init__(self, username: str = Form(), email: str = Form(), password: str = Form()):
        self.email = email
        self.password = password
        self.username = username