from fastapi import FastAPI
from utils import *

fastapi_app = FastAPI()

@fastapi_app.get("/v2")
def hello_world():
    return {"message": "Hello World"}