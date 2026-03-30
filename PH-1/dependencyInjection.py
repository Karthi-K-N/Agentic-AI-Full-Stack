# dependency injection -> a design pattern where an object receives other objects that it depends on, 
# rather than creating them itself. This promotes loose coupling and makes code more modular and testable.
# used for sessions, DB, authentication, logging, normal code etc..
# types: function, class, sub-dependency, global dependency, yield dependencies, etc..

from fastapi import FastAPI, Depends
from datetime import datetime



# Global dependency injection - used for session authentication, logging, etc.., it will be executed for every request

def tok_check(tok: str = '123'):
    if tok != '123':
        raise Exception("Invalid token")
    return True

app = FastAPI(dependencies = [Depends(tok_check)])

#functional dependency injection - used for simple dependencies, where you just need to execute a function and return a value. It allows you to separate the logic of creating the dependency from the logic of using it, making your code cleaner and more maintainable.
def db():
    return "This is a database connection example"

@app.get("/functional-dependency")
async def functional_dependency(db: str = Depends(db)):
    return {"message": "This is a functional dependency example", "dependency": db}

# Class based dependency injection - used for complex dependencies, where you need to maintain state or have multiple related methods. It allows you to encapsulate the logic and data related to the dependency in a class, making it easier to manage and reuse across different parts of your application.

class User:
    def __init__(self):
        self.name = 'karthi'
        self.age = 28

def get_user():
    return User()

@app.get('/class-dependency')
async def class_dependency(user: User = Depends(get_user)):
    return {"name": user.name, "age": user.age}


# Sub Dependency injection - used for dependencies that depend on other dependencies. It allows you to create a hierarchy of dependencies, where one dependency can depend on another, making it easier to manage complex relationships between different parts of your application.

def gp():
    return {"message": "This is from grandparent dependency"}

def pa(gp: str = Depends(gp)):
    return { "message": f"this is from parent dependency, and it depends on -> {gp}"}

@app.get('/sub-dependency')
def sub_dependency(pa: str = Depends(pa)):
    return {"message": f"This is from child dependency, and it depends on -> {pa}"}

# Yield dependencies - used for dependencies that need to perform some cleanup after they are used. It allows you to define a dependency that can yield a value, and then perform some cleanup code after the value is used, making it easier to manage resources and ensure that they are properly released.

def bb():
    print("Book taken from self", datetime.now())
    Book = "Wheels of Time"
    yield Book # yield will pause here after executing the above code, and will execute endpoint code, after that it will come back and execute the below code.
    print("Book returned to self", datetime.now())

@app.get("/yield-dependency")
def library(book: str = Depends(bb)):
    return {"message": f" reading {book} at {datetime.now()}"}