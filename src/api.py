import os
import jwt
import json
from fastapi import FastAPI, Request, UploadFile, Header, Depends
from typing import Union
from bson.objectid import ObjectId
import pydantic
from pydantic import BaseModel
import time
from bson.objectid import ObjectId
from passlib.context import CryptContext
from passlib.hash import bcrypt
from datetime import datetime, timedelta
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from tasks import transcribe
from mongo_client import users_collection, results_collection

security = HTTPBearer()
pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

@app.get("/")
async def read_root() -> dict:
    return { "message": "System is live" }

class User(BaseModel):
    username: str
    password: str

@app.post("/register")
async def register(body: User) -> dict:
    try:
        find = users_collection.find({ "username": body.username })
        if (len(list(find))):
            raise Exception("username already exists")
        password_hashed = pwd_context.hash(body.password, salt="a"*22)
        users_collection.insert_one({ "username": body.username, "password_hashed": password_hashed })
        return { "message": "user created" }
    except Exception as e:
        return str(e)

@app.post("/login")
async def login(body: User):
    try:
        count = users_collection.count_documents({ "username": body.username })
        if (count <= 0):
            return "wrong username/password combination"
        expire = datetime.utcnow() + timedelta(minutes=15)
        user = users_collection.find_one({ "username": body.username })
        hash = pwd_context.hash(body.password, salt="a"*22)
        if (hash != user["password_hashed"]):
            return "wrong username/password combination"
        encoded = jwt.encode({ "username": body.username, "exp": datetime.utcnow() + timedelta(minutes=15) }, "JWT_SECRET", algorithm="HS256")
        return { "token": encoded }
    except Exception as e:
        return str(e)

def authenticate(credentials: HTTPAuthorizationCredentials= Depends(security)):
    try:
        decoded = jwt.decode(credentials.credentials, "JWT_SECRET", algorithms="HS256", options={ "verify_exp": True })
        return decoded
    except Exception as e:
        return str(e)

@app.post("/upload-transcribe")
async def upload_transcribe(file: UploadFile, user = Depends(authenticate), authorization: Union[str, None] = Header(default=None)) -> str:
    try:
        find = users_collection.find({ "username": user["username"] })
        if (len(list(find)) <= 0):
            raise Exception("username doesn't exists")
        contents = await file.read()
        filename = user["username"] + "-" + str( time.time() ) + "-" + file.filename
        newFile = open(filename, "wb")
        newFile.write(contents)
        result = transcribe.delay(filename)
        text = result.get(timeout=100)
        os.remove(filename)
        user_id = users_collection.find({ "username": user["username"] })[0]["_id"]
        results_collection.insert_one({ "user_id": user_id, "text": text, "file": contents, "filename": file.filename })
        return text
    except Exception as e:
        return str(e)

@app.get("/transcribes/")
async def transcribes(user = Depends(authenticate), authorization: Union[str, None] = Header(default=None)):
    try:
        user_id = users_collection.find({ "username": user["username"] })[0]["_id"]
        results = results_collection.find({ "user_id": ObjectId(user_id) }, { "filename": 1, "text": 1, "_id": 0 })
        return list(results)
    except Exception as e:
        return str(e)