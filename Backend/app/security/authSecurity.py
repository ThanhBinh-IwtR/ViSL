from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, APIRouter, Form
from jose import jwt
from passlib.context import CryptContext
from controller import userController
from sqlalchemy.orm import Session
from typing import Union
from database.connection import get_db
from security.cookie import OAuth2PasswordBearerWithCookie
from fastapi import Depends, APIRouter, Request, Response, status
import logging

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
COOKIE_NAME = "Authorization"


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="login")

authRouter = APIRouter()


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        print(f"Token received: {token}")  # Kiểm tra token có được truyền không
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        print(f"Decoded username: {username}")  # Kiểm tra username được giải mã
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không hợp lệ",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user: str = userController.get_user_by_username(db=db, username=username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Không tìm thấy người dùng",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user.username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],)
    user: str = userController.get_user_by_username(db=db, username=payload.get("sub"))
    if user and user.is_Admin==True:
        return user.username
    else:
        raise HTTPException(status_code=302, detail="Not authorized", headers={"Location": "/signin"})

def verify_token(token: str):
    try:
        # Nếu token có tiền tố "Bearer", hãy bỏ tiền tố đó đi
        if token.startswith("Bearer "):
            token = token[len("Bearer "):]

        # Giải mã token với khóa bí mật và thuật toán đã chỉ định
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])

        # Trả về payload nếu không có lỗi
        return payload
    except jwt.ExpiredSignatureError:
        logging.error("Token đã hết hạn")
        raise HTTPException(status_code=401, detail="Token đã hết hạn")
    except jwt.JWTError as e:
        logging.error(f'Lỗi verify token: {e}')
        raise HTTPException(status_code=401, detail="Token không hợp lệ")

class OAuth2PasswordRequestFormWithEmail:
    def __init__(self, username: str = Form(), email: str = Form(), password: str = Form()):
        self.email = email
        self.password = password
        self.username = username