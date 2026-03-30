from fastapi import FastAPI, Query, Path


app = FastAPI()

@app.get("/") ##decorator will start with @
def home_load():
    return "Hello!! Home loaded successfully!"

#path parameter

product_info = [
    {"sku": "009", "name": "Dove soap", "price": 100},
    {"sku": "008", "name": "Lux soap", "price": 50},
    {"sku": "010", "name": "Himalayan soap", "price": 60}
]

@app.get("/product/{sku}")
def get_product_info(sku :str = Path(min_length=3, max_length=50, pattern="^[0-9]")):
    for p in product_info:
        if "sku" in p and p["sku"]==sku:
            return p
    else:
        return f"Product not found"
    
#Query parameter - used for big application, big api
@app.get("/Queryproduct")
def query_product_info(sku :str = Query(min_length=3, max_length=50, pattern="^[0-9]")): #Query for valudation
    for p in product_info:
        if "sku" in p and p["sku"]==sku:
            return p
    else:
        return f"Product not found"

@app.get("/getProducts")
def get_all_products():
    return {"message": "Here all the available products",
            "response": product_info}
    

#pydantic model, 
# validation -> validate the request, 
# seralisation -> convert data structure eg: json -> xml, 
# documention -> document preparation

from pydantic import BaseModel, Field
from typing import Optional

class manf(BaseModel):
    company_name: str = Field(min_length=3, max_length=50, pattern="^[a-zA-Z0-9]")
    location: str = Field(min_length=3, max_length=50, pattern="^[a-zA-Z0-9]")

class product(BaseModel):
    sku: str = Field(min_length=3, max_length=50, pattern="^[0-9]")
    name: str = Field(min_length=3, max_length=50, pattern="^[a-zA-Z0-9]")
    price: float = Field(gt=0, lt=9999)
    #nested model
    manufacturer: Optional[manf] = None
    # in_stock: Optional[bool] = False

@app.post("/addproduct")
def add_product(item :product):
    product_info.append(item.dict())
    return {"message": "New item added",
            "response": item}