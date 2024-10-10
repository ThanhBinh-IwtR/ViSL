from fastapi import FastAPI, Request, APIRouter,Depends,Form,HTTPException,Response, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from schema import Token
import os
import logging
from connection import Base,engine, sess_db
from sqlalchemy.orm import Session
from security import get_password_hash,verify_password, create_access_token, verify_token, COOKIE_NAME, oauth2_scheme, OAuth2PasswordRequestFormWithEmail
from starlette.responses  import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import repositoryuser
from repositoryuser import SendEmailVerify
from models import User
from datetime import timedelta
import security

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
userRouter=APIRouter()
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, 'Frontend'))

logging.basicConfig(level=logging.DEBUG)

# app = FastAPI(debug=True)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://127.0.0.1:8000"],  # Địa chỉ của frontend
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @userRouter.exception_handler(Exception)
# async def global_exception_handler(request: Request, exc: Exception):
#     logging.error(f"Unhandled error: {exc}")
#     return Response(content=f"An error occurred: {exc}", status_code=500)


Base.metadata.create_all(bind=engine)
# --------------------------------------------------------------------------------------------

@userRouter.get("/")
def get_index(request:Request):
    return templates.TemplateResponse("index.html",{"request":request})

@userRouter.get("/index")
def get_index(request:Request):
    return templates.TemplateResponse("index.html",{"request":request})



# --------------------------------------------------------------------------------------------

@userRouter.get("/contact")
def get_index(request:Request):
    return templates.TemplateResponse("contact.html",{"request":request})

# --------------------------------------------------------------------------------------------

@userRouter.get("/account")
def get_index(request:Request):
    return templates.TemplateResponse("login.html",{"request":request})
    
# --------------------------------------------------------------------------------------------

@userRouter.post("/register")
def signup_user(db: Session = Depends(sess_db),form_data:OAuth2PasswordRequestFormWithEmail=Depends()):
    email = form_data.email
    username = form_data.username
    password = form_data.password
    print(f"Username: {username}, \n Email: {email}, \n Password: {password}")

    db_user = repositoryuser.get_user_by_username(db=db,username=username)

    db_email = repositoryuser.get_user_by_email(db=db,email = email)

    if db_user or db_email:

        return JSONResponse(content={"error": "User_name or email is available"}, status_code=400)

    signup = User(email=email, username=username, password=get_password_hash(password))
    success = repositoryuser.create_user(db=db, signup=signup)
    token = create_access_token(signup)
    
    logging.info(f"Generated token: {token}")
    
    SendEmailVerify.sendVerify(token, email)
    if success:
        return JSONResponse(content={"success": "create user successfully"})
    else:
        raise HTTPException(
            status_code=401, detail="Đã xảy ra lỗi khi tạo tài khoản."
        )

# --------------------------------------------------------------------------------------------
# Đăng nhập người dùng

# @userRouter.post("/login")
# async def login(username: str = Form(), password: str = Form(), db: Session = Depends(sess_db)):
    
#     db_user = repositoryuser.get_user_by_username(username)
    
#     # Nếu người dùng không tồn tại hoặc mật khẩu sai, trả về JSON với lỗi
#     if not db_user or not verify_password(password, db_user.password):
#         return JSONResponse(content={"error": "invalid_credentials"}, status_code=400)
    
#     # Nếu đăng nhập thành công, chuyển hướng về trang chủ với tên người dùng
#     return RedirectResponse(url=f"/?username={username}", status_code=302)

# --------------------------------------------------------------------------------------------
@userRouter.post("/login", response_model=Token)
def login_for_access_token(
    response: Response, request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(sess_db)
):
    # Xác thực người dùng bằng username và password
    user = repositoryuser.authenticate_user(
        db=db,
        username=form_data.username,
        password=form_data.password
    )
    if not user:
        # error = "Incorrect username or password"
        return JSONResponse(content={"error": "invalid_credentials"}, status_code=400)

    # Tạo token nếu xác thực thành công
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username, "user_id": user.id}, expires_delta=access_token_expires
    )

    # Lưu token trong cookie
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True) 
    return response
    
# --------------------------------------------------------------------------------------------

# @app.get("/logout", response_class=HTMLResponse)
# async def login_page():
#     with open(frontend_path / "login.html", "r", encoding="utf-8") as file:
#         return HTMLResponse(content=file.read())

# --------------------------------------------------------------------------------------------
@userRouter.get('/user/verify/{token}')
def verify_user(token,db:Session=Depends(sess_db)):
    
    payload=verify_token(token)
    username=payload.get("username")
    db_user=repositoryuser.get_user_by_username(username)
 
    if not username:
        raise  HTTPException(
            status_code=401, detail="Credentials not correct"
        )
    if db_user.is_active==True:
        return "your account  has been allreay activeed"
 
    db_user.is_active=True
    db.commit()
    response=RedirectResponse(url="/user/signin")
    return response
 