# JWT -> Json Web Token, used for secure data transmission between parties as a JSON object, 
# commonly used for authentication and authorization in web applications.

# JWT consists of three parts: header, payload, and signature. 
# The header typically contains the type of token and the signing algorithm (HS256 or RSA) used. 
# The payload contains the claims, which are statements about an entity (typically, the user) and additional data. 
# The signature is created by taking the encoded header, the encoded payload, a secret key, and the algorithm specified in the header, and signing them together.

# below example of : login -> screte screen -> JWT -> verify

from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
from jose import JWTError,jwt

app = FastAPI()

ALGORITHM = 'HS256'
SECRET_KEY = 'SDFSLKGSDPLKMGSFGDDS'
TOKEN_EXPIRY_TIME = 10 # token expire in 10 seconds

def create_token(username: str):
    expiry = datetime.utcnow() + timedelta(minutes = TOKEN_EXPIRY_TIME)
    payload = {"username": username, "password": 'admin123', "expiry": expiry.timestamp()}
    return jwt.encode(payload, SECRET_KEY, ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms={ALGORITHM})
        return payload['username']
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post('/login')
def login(username: str, password: str):
    if username == 'admin' and password == 'admin123':
        token = create_token(username)
        return {"message": "Login successful!", "token": token}
    raise HTTPException(status_code=401, detail= "Invalid credentials")

@app.post('/Home')
def home_screen(token: str):
    name = verify_token(token)
    if name:
        return {"message": f"Welcome to the home screen, {name}!"}
    raise HTTPException(status_code=401, detail= "Unauthorized")