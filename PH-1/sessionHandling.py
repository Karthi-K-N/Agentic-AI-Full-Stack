#after user + pass -> check in server (db) -> if success -> gets id from server (sessionid) -> home view (username+id) -> stored in cookies -> when calling api again (account + id will be sent in API)
#cookies -> small data, stored in client side, sent with every request, used for session management, personalization, tracking
#session -> server side storage of user data, session id stored in cookie, used for authentication

from fastapi import FastAPI, HTTPException, Cookie, Response
import uuid
from typing import Optional
from datetime import datetime, timedelta

app = FastAPI()

storedUsersCreds = [
    {"username": "admin1", "password": "admin123"},
    {"username": "admin2", "password": "admin1234"},
]

sessions = {}
time = 10 # session expire in 10 seconds

@app.post("/Login")
def login(username: str, password: str, response: Response):
    for user in storedUsersCreds:
        if user["username"] == username and user["password"] == password:
            sid = str(uuid.uuid4())

            #session expiry
            current_time = datetime.now()
            expiry_time = current_time+timedelta(seconds=time)

            sessions[sid]= {"username": username, "expiry": expiry_time}
            response.set_cookie(key="sid", value=sid, httponly=True)
            return {"message": f"{username} logged in successfully!"}
        else:
            raise HTTPException(status_code=401, detail= "invalid credentials")
    else:
        raise HTTPException(status_code=500, detail= "Internal server error")

@app.get("/Home")
def home(sid: Optional[str] = Cookie(None)):
    if sid is None or sid not in sessions:
        raise HTTPException(status_code=401, detail= "Unauthorized")
    session_data = sessions[sid]
    if session_data['expiry'] < datetime.now():
        sessions.pop(sid)
        raise HTTPException(status_code=401, detail= "Session expired")
    return {"message": f"Welcome {sessions[sid]['username']} to the home page!, your session id is {sid}"}
