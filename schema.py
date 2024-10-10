# #loginregister/schema.py
# from datetime import date
# from pydantic import BaseModel, EmailStr #pip install pydantic[email]
# from enum import Enum
# from fastapi import Form
 
 
# class UserSchema(BaseModel):
#     email: EmailStr
#     username: str
#     password: str
 
#     class Config:
#         from_attributes = True
 
# class Role(Enum):
#     user = "user"
#     admin = "admin"

from pydantic import BaseModel
from typing import Union


class Token(BaseModel):
    access_token:str
    token_type:str