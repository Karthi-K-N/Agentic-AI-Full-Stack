import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

conn = sqlite3.connect("test.db", check_same_thread=False) #check_same_thread=False -> allows multiple threads to access the database connection, useful for web applications where multiple requests may be handled concurrently. It prevents the "SQLite objects created in a thread can only be used in that same thread" error.
cursor = conn.cursor()

# cursor.execute('''CREATE TABLE IF NOT EXISTS ITEMS(
#                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                name TEXT NOT NULL,
#                des TEXT)''')
# conn.commit()

class Items(BaseModel):
    name: str
    des: str

@app.post("/items/update")
def update_db(item: Items):
    try:
        cursor.execute("Insert into Items (name, des) values (?, ?)",(item.name, item.des))
        conn.commit()
        return {"message": "Items added successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail= f"Internal server error: {e}") 
    
@app.get("/items/read")
def read_items():
    try:
        cursor.execute("Select * from items")
        rows = cursor.fetchall()
        print(rows)
        return [{"id": r[0], "name": r[1], "des": r[2]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail= f"Internal server error: {e}") 
    
@app.get("/items/read-one/{name}")
def read_one_item(name: str):
    try:
        cursor.execute("select * from items where name = ?", (name,))
        row = cursor.fetchone()
        return {"id": row[0], "name": row[1], "des": row[2]}
    except Exception as e:
        raise HTTPException(status_code=500, detail= f"Internal server error: {e}")
    
@app.put("/items/update/{item_id}")
def update_items(item_id: int, item:Items):
    try:
        cursor.execute("update items set name=?,des=? where item_id=?",(item.name, item.des, item_id))
        conn.commit()
        return {"message": "item updated successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail= f"Internal server error: {e}")

@app.delete("/item/delete/{item_id}")
def delete_item(item_id: int):
    try:
        cursor.execute("delete from items where item_id=?", (item_id,))
        conn.commit()
        return {"message": "item deleted successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail= f"Internal server error: {e}")