# from os import stat
# from typing import Optional
# from fastapi import APIRouter, Body, HTTPException, Depends, status
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from Backend.app.dbclass import Database
from Backend.app.config import settings
from Backend.app.schemas import LoginFormData
# from Backend.app.schemas import User, UpdateUser, LoginUser

# from datetime import datetime, timedelta
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from jose import JWTError, jwt
from passlib.context import CryptContext
# from pydantic import BaseModel

Project21Database=Database()
Project21Database.initialise(settings.DB_NAME)
login_router=APIRouter()


pwd_context = CryptContext(schemes=["bcrypt"])
# oauth2_scheme=OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password,hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


@login_router.post('/api/logincheck')
def check_server_status():
    return JSONResponse({"login_router":"working"})

@login_router.post('/api/login')
def login_user(loginFormData:LoginFormData):
    loginFormData=dict(loginFormData)
    try:
        #make necessary changes to the below method in case of multiple users with the same username
        #replace find_one with find and accordingly traverse and find
        user=Project21Database.find_one(settings.DB_COLLECTION_USER,{"username":loginFormData["username"]})
        if user is not None:
            if verify_password(loginFormData["password"],user["password"]):
                return JSONResponse({"Success":True,"userID":user["userID"],"username":user["username"]})
            else:
                print({"Success":False,"Error":"Incorrect Password"})
                return JSONResponse({"Success":False,"Error":"Incorrect Password"})
        else:
            print({"Success":False,"Error":"No Such User in the DB"})
            return JSONResponse({"Success":False,"Error":"No Such User in the DB"})
    except Exception as e:
        print("An Error Occured: ",e)
        print({"Success":False,"Error":"Some Error Occured"})
        return JSONResponse({"Success":False,"Error":"Some Error Occured"})

# to get a string like this run:
# openssl rand -hex 32
# SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# fake_users_db = {
#     "johndoe": {
#         "username": "johndoe",
#         "full_name": "John Doe",
#         "email": "johndoe@example.com",
#         "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
#         "disabled": False,
#     }
# }

# class Token(BaseModel):
#     access_token: str
#     token_type: str

# class TokenData(BaseModel):
#     username: Optional[str]=None

# class MyUser(BaseModel):
#     username: str
#     email: Optional[str]=None
#     full_name: Optional[str]=None
#     disable: Optional[bool]=None

# class MyUserInDB(MyUser):
#     hashed_password: str

# def get_user(db,username:str):
#     if username in db:
#         user_dict=db[username]
#         return MyUserInDB(**user_dict)

# def authenticate_user(fake_db,username:str,password:str):
#     user=get_user(fake_db,username)
#     if not user:
#         return False
#     if not verify_password(password,user.hashed_password):
#         return False
#     return user

# def create_access_token(data:dict, expires_delta: Optional[timedelta]=None):
#     to_encode=data.copy()
#     if expires_delta:
#         expire=datetime.utcnow()+expires_delta
#     else:
#         expire=datetime.utcnow()+timedelta(minutes=15)
#     to_encode.update({"exp":expire})
#     encoded_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
#     return encoded_jwt

# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate the credentials",
#         headers={"WWW-Authenticate":"Bearer"})
#     try:
#         payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data=TokenData(username=username)
#     except JWTError:
#         raise credentials_exception
#     user=get_user(fake_users_db,username=token_data.username)
#     if user is None:
#         raise credentials_exception
#     return user

# async def get_current_active_user(curent_user:MyUser=Depends(get_current_user)):
#     if curent_user.disabled:
#         raise HTTPException(status_code=400,detail="Inactive User")
#     return curent_user

# @login_router.post("/token", response_model=Token)
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm=Depends()):
#     user=authenticate_user(fake_users_db,form_data.username,form_data.password)
#     if not User:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate":"Bearer"}
#         )
#     access_token_expires=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token=create_access_token(
#         data={"sub":user.username},
#         expires_delta=access_token_expires
#     )
#     return {"access_token":access_token,"token_type":"bearer"}