import os
import jwt
import json
from fastapi import FastAPI, Request, UploadFile, Header
from typing import Union
from bson.objectid import ObjectId
import pydantic
from pydantic import BaseModel
import time
from bson.objectid import ObjectId
from tasks import transcribe
from mongo_client import users_collection, results_collection

pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str

app = FastAPI()

@app.get("/")
async def read_root() -> dict:
    return { "message": "System is live" }

class User(BaseModel):
    username: str

@app.post("/register")
async def register(body: User) -> dict:
    try:
        find = users_collection.find({ "username": body.username })
        if (len(list(find))):
            raise Exception("username already exists")
        encoded = jwt.encode({ "username": body.username }, "JWT_SECRET", algorithm="HS256")
        user = { "username": body.username, "token": encoded }
        users_collection.insert_one(user)
        return user
    except Exception as e:
        return str(e)

@app.post("/upload-transcribe")
async def upload_transcribe(file: UploadFile, authorization: Union[str, None] = Header(default=None)) -> str:
    try:
        bearer, _, token = authorization.partition(' ')
        if bearer != 'Bearer':
            raise ValueError('Invalid token')
        decoded = jwt.decode(token, "JWT_SECRET", algorithms="HS256")
        find = users_collection.find({ "username": decoded["username"] })
        if (len(list(find)) <= 0):
            raise Exception("username doesn't exists")
        contents = await file.read()
        filename = decoded["username"] + "-" + str( time.time() ) + "-" + file.filename
        newFile = open(filename, "wb")
        newFile.write(contents)
        result = transcribe.delay(filename)
        text = result.get(timeout=100)
        os.remove(filename)
        user_id = users_collection.find({ "username": decoded["username"] })[0]["_id"]
        results_collection.insert_one({ "user_id": user_id, "text": text, "file": contents, "filename": file.filename })
        return text
    except Exception as e:
        return str(e)

@app.get("/transcribes/")
async def transcribes(authorization: Union[str, None] = Header(default=None)):
    try:
        bearer, _, token = authorization.partition(' ')
        if bearer != 'Bearer':
            raise ValueError('Invalid token')
        decoded = jwt.decode(token, "JWT_SECRET", algorithms="HS256")
        user_id = users_collection.find({ "username": decoded["username"] })[0]["_id"]
        results = list(results_collection.find({ "user_id": ObjectId(user_id) }, { "filename": 1, "text": 1, "_id": 0 }))
        return results
    except Exception as e:
        return str(e)