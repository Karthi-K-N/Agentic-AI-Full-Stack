from fastapi import FastAPI, Form

app = FastAPI()

#form default format is not json, 
# 'Content-Type: application/x-www-form-urlencoded' \-d 'name=Demo&email=Demo%40gmail.com&age=11'
@app.post("/submitForm")
def submit_form(name: str = Form(...),
                email: str = Form(...),
                age: int = Form()):
    return {"name": name, "email": email, "age": age}
