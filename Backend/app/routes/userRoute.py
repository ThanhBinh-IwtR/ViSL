from fastapi import Depends,APIRouter,Request,Response,status,HTTPException
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from database.connection import get_db
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from controller import userController
from model.userModel import User
from schema.userSchema import Token
from security.authSecurity import create_access_token,get_password_hash,ACCESS_TOKEN_EXPIRE_MINUTES,OAuth2PasswordRequestFormWithEmail,get_current_user,verify_token
from datetime import timedelta
from starlette.responses import RedirectResponse
import os
from io import BytesIO
from PIL import Image
import logging
import numpy as np
import cv2
import json
import base64
import mediapipe as mp
from modelAI.predictor import load_model, predict_pytorch, extract_keypoints




userRouter=APIRouter()


#-----------------Basic-------------------

templates = Jinja2Templates(directory=os.path.join("..", "Frontend"))
logging.basicConfig(level=logging.DEBUG)

@userRouter.get("/index")
def get_index(request:Request):
    return templates.TemplateResponse("index.html",{"request":request})

@userRouter.get("/")
def get_index(request:Request):
    return templates.TemplateResponse("index.html",{"request":request})

@userRouter.get("/contact")
def get_contact(request:Request):
    return templates.TemplateResponse("contact.html",{"request":request})

@userRouter.get("/account")
def get_account(request:Request):
    return templates.TemplateResponse("login.html",{"request":request})

@userRouter.get("/demo")
def get_video(request:Request):
    return templates.TemplateResponse("livedemo.html",{"request":request})

#-----------------User-------------------

#-----------------Register-------------------

@userRouter.post("/register")
async def create_new_user(request: Request, db: Session = Depends(get_db), form_data: OAuth2PasswordRequestFormWithEmail = Depends()):
    db_user = userController.get_user_by_username(db=db, username=form_data.username)
    
    # Trường hợp email hoặc username đã tồn tại
    if db_user:
        return {"status": "error", "message": "Tên đăng ký hoặc email đã được sử dụng."}
    
    # Tạo người dùng mới và lưu vào cơ sở dữ liệu
    new_user = User(
        email=form_data.email,
        username=form_data.username,
        password=get_password_hash(form_data.password)
    )
    userController.create_user(db=db, signup=new_user)
    
    # Phản hồi thành công
    return {"status": "success", "message": "Đăng ký thành công. Vui lòng kiểm tra email để xác nhận tài khoản."}

#-----------------Login-------------------

@userRouter.post("/login", response_model=Token)
def login_for_access_token(response: Response, request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = userController.authenticate_user(
        db=db,
        username=form_data.username,
        password=form_data.password
    )
    if not user:
        error = "Incorrect account information."
        return templates.TemplateResponse('login.html', {"error": error, "request": request}, status_code=status.HTTP_301_MOVED_PERMANENTLY)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.is_Admin}, expires_delta=access_token_expires
    )
    print(f"Access token: {access_token}")
    # Lưu token vào cookie
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=False,path="/")
    
    # Chuyển hướng sau khi đăng nhập thành công
    return RedirectResponse(url="/index", status_code=status.HTTP_303_SEE_OTHER)

#-----------------Cookie-------------------

@userRouter.get("/user-info")
def get_user_info(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")  # Lấy token từ cookie
    logging.info(f"Generated token: {request.cookies}")
    logging.info(f"Generated token: {token}")
    if not token:
        raise HTTPException(status_code=401, detail="Token không tìm thấy")

    payload = verify_token(token.replace("Bearer ", ""))  # Bỏ tiền tố "Bearer" khi xác thực
    username = payload.get("sub")

    if not username:
        raise HTTPException(status_code=401, detail="Token không hợp lệ")
    
    
    db_user = userController.get_user_by_username(username)
    
    return {"username": db_user.username}

# @userRouter.get("/index")
# def get_signup(request:Request,current_user:User=Depends(get_current_user)):
#     return templates.TemplateResponse("index.html",{"request":request,"user":current_user})

#-----------------ModelAI-------------------

model = load_model()
with open('app/modelAI/sign_to_prediction_index_map.json', 'r', encoding='utf-8') as json_file:
    label_map = json.load(json_file)

mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)

@userRouter.post("/process-frame")
async def process_frame(request: Request):
    data = await request.json()
    frame_data = data.get("frame")

    # Log lại chuỗi base64 nhận được từ frontend
    print("Base64 data received:", frame_data[:100])  # Log 100 ký tự đầu tiên của chuỗi base64

    try:
        # Chuyển đổi chuỗi base64 thành hình ảnh
        img = Image.open(BytesIO(base64.b64decode(frame_data)))
        img_np = np.array(img)

        # Chuyển đổi từ RGB sang BGR (Mediapipe cần xử lý trên ảnh RGB)
        img_rgb = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        # Dùng Mediapipe để xử lý landmarks (chuyển đổi frame từ BGR sang RGB)
        results = holistic.process(cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB))
        
        # Trích xuất các keypoints
        keypoints = extract_keypoints(results)

        # Chuẩn bị dữ liệu cho mô hình
        sequence = [keypoints]  # Sử dụng sequence đơn giản với một frame

        # Dự đoán bằng mô hình PyTorch
        predicted = predict_pytorch(sequence, model, label_map)

        # Trả về kết quả dự đoán
        return {"result": predicted}

    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}