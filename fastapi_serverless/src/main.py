from fastapi.responses import RedirectResponse
from helpers import (
    handle_request_create_avatar,
    handle_request_create_image,
    send_request_to_serverless,
    CharacterConfig,
    CreateImageRequest,
)
from fastapi import FastAPI
import base64
import json
import base64
import requests
import os
app = FastAPI()

MODEL_ID = os.environ.get("MODEL_ID")
API_KEY = os.environ.get("API_KEY")
print("MODEL_ID and API_KEY:", MODEL_ID, API_KEY)

@app.post("/create-avatar/")
async def create_avatar(request: dict):
    print("Request:", request)
    serverless_values = handle_request_create_avatar(request)
    print("Serverless values:", serverless_values)
    # Call model endpoint
    s3_link = send_request_to_serverless(serverless_values, model_id=MODEL_ID, api_key=API_KEY)
    print("S3 link:", s3_link)
    return s3_link

@app.post("/create-image/") 
async def create_image(
    avatar: str, 
    create_image_request: dict | CreateImageRequest
):
    print("Request:", create_image_request)
    serverless_values = handle_request_create_image(avatar, create_image_request)
    print("Serverless values:", serverless_values)
    if serverless_values is None:
        return "Invalid avatar!"

    # Call model endpoint
    s3_link = send_request_to_serverless(serverless_values, model_id=MODEL_ID, api_key=API_KEY)
    print("S3 link:", s3_link)
    return s3_link

@app.post("/test")
async def test(request: dict):
    return "Hello, World!"

@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")