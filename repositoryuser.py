#loginregister/repositoryuser.py
from sqlalchemy.orm import Session
from models import User
from typing import  Dict,Any
from sqlalchemy.orm import Session
import smtplib
import logging
from email.message import EmailMessage
 
def create_user(db: Session,signup:User) -> bool:
        try:
            db.add(signup)
            db.commit()
        except:
            return False
        return True

def get_user_by_username(db: Session, username: str):
    try:
        user = db.query(User).filter(User.username == username).first()
        if user:
            logging.debug(f"User {username} found: {user}")
        else:
            logging.debug(f"User {username} not found.")
        return user
    except Exception as e:
        logging.error(f"Error querying user by username {username}: {e}")
        return None

def get_user_by_email(db: Session,email:str):
    return db.query(User).filter(User.email==email).first()

def authenticate_user(db: Session, username: str, password: str):
    from security import verify_password
    user = get_user_by_username(db=db, username=username)
    if not user:
        logging.debug(f"User {username} not found.")
        return False
    if not verify_password(password, user.password):
        logging.debug(f"Password for user {username} is incorrect.")
        return False
    logging.debug(f"User {username} authenticated successfully.")
    return user
 
class SendEmailVerify:
 
  def sendVerify(token, email: str):
    email_address = "phanhuynhthanhbinh@gmail.com" # type Email
    email_password = "uwcn vsvn kpjg gxsw" 
 
    # create email
    msg = EmailMessage()
    msg['Subject'] = "Xác nhận đăng ký tài khoản"
    msg['From'] = email_address
    msg['To'] = email # type Email
    msg.set_content(
       f"""\
    Vui lòng nhấn vào liên kết sau để xác nhận tài khoản của bạn:       
    http://localhost:8080/user/verify/{token}
    """,
         
    )
    # send email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_address, email_password)
            smtp.send_message(msg)  # Gửi đối tượng email 'msg'
    except Exception as e:
        print(f"Lỗi khi gửi email: {e}")