#restrict the number of request attempt

from fastapi import FastAPI, HTTPException, Request
import uuid
from typing import Optional
from datetime import datetime, timedelta

app = FastAPI()

req_count = {}
max_req = 5

@app.get('/limitedRequest')
def limited_request(request: Request):
    client_ip = request.client.host
    req_count[client_ip] = req_count.get(client_ip,0)+1

    if req_count[client_ip] > max_req:
        raise HTTPException(status_code=429, detail="Too many requests, please try again later.")
    return {"message": f"Request successful! You have made {req_count[client_ip]} requests. {max_req - req_count[client_ip]} more requests left."}