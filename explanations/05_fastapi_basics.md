# FastAPI — Complete Beginner Guide

FastAPI is a modern, high-performance **Python web framework** for building REST APIs. It uses Python type hints for automatic validation, serialization, and documentation.

---

## 📦 Installation

```bash
pip install fastapi uvicorn[standard]
```

- `fastapi` — the web framework
- `uvicorn` — the ASGI server that runs your FastAPI app

---

## 🚀 Step 1: Create Your First API

```python
# main.py
from fastapi import FastAPI

# Create the FastAPI application
app = FastAPI()

# Define a route (endpoint)
@app.get("/")
def home():
    return {"message": "Hello, World!"}
```

### Run the Server

```bash
uvicorn main:app --reload
```

- `main` — the Python file name (main.py)
- `app` — the FastAPI instance variable
- `--reload` — auto-restart on code changes (development only)

Visit `http://localhost:8000` — you'll see `{"message": "Hello, World!"}`

Visit `http://localhost:8000/docs` — **auto-generated Swagger UI documentation!**

---

## 🛣️ Step 2: HTTP Methods (GET, POST, PUT, DELETE)

```python
from fastapi import FastAPI

app = FastAPI()

# GET — Read/retrieve data
@app.get("/items")
def get_items():
    return {"items": ["Milk", "Bread", "Eggs"]}

# POST — Create new data
@app.post("/items")
def create_item():
    return {"message": "Item created"}

# PUT — Update existing data
@app.put("/items/{item_id}")
def update_item(item_id: int):
    return {"message": f"Item {item_id} updated"}

# DELETE — Remove data
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    return {"message": f"Item {item_id} deleted"}
```

---

## 📌 Step 3: Parameter Types

### 3.1 Path Parameters

Values embedded in the URL path:

```python
# {item_id} is a path parameter — it's part of the URL itself
@app.get("/items/{item_id}")
def get_item(item_id: int):  # Type hint auto-validates: must be an integer
    return {"item_id": item_id}
```

```
GET /items/42       → {"item_id": 42}    ✅
GET /items/hello    → 422 Error           ❌ (not an integer)
```

### 3.2 Query Parameters

Values after the `?` in the URL:

```python
# Query parameters are any function parameters NOT in the path
@app.get("/items")
def list_items(
    skip: int = 0,        # Default value = 0 (optional)
    limit: int = 10,      # Default value = 10 (optional)
    search: str = None,   # Default value = None (optional)
):
    return {"skip": skip, "limit": limit, "search": search}
```

```
GET /items                     → {"skip": 0, "limit": 10, "search": null}
GET /items?skip=20&limit=5     → {"skip": 20, "limit": 5, "search": null}
GET /items?search=milk         → {"skip": 0, "limit": 10, "search": "milk"}
```

### 3.3 Query Parameters with Validation

```python
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/items")
def list_items(
    # Query() adds validation and documentation
    skip: int = Query(default=0, ge=0, description="Records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max records"),
    branch: str = Query(default=None, description="Filter by branch"),
):
    return {"skip": skip, "limit": limit, "branch": branch}
```

### 3.4 Request Body Parameters

Data sent in the body of POST/PUT requests (uses Pydantic):

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Define the request body schema
class ItemCreate(BaseModel):
    name: str
    price: float
    quantity: int = 1

# FastAPI reads the JSON body and validates it against ItemCreate
@app.post("/items")
def create_item(item: ItemCreate):
    return {"name": item.name, "price": item.price, "total": item.price * item.quantity}
```

```
POST /items
Body: {"name": "Milk", "price": 1.50, "quantity": 3}
→ {"name": "Milk", "price": 1.50, "total": 4.50}
```

### 3.5 Combining All Parameter Types

```python
from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()

class ItemUpdate(BaseModel):
    name: str
    price: float

@app.put("/stores/{store_id}/items/{item_id}")
def update_item(
    store_id: int,                          # Path parameter
    item_id: int,                           # Path parameter
    item: ItemUpdate,                       # Request body (Pydantic model)
    notify: bool = Query(default=False),    # Query parameter
):
    return {
        "store_id": store_id,
        "item_id": item_id,
        "updated": item.model_dump(),
        "notification_sent": notify,
    }
```

```
PUT /stores/1/items/42?notify=true
Body: {"name": "Whole Milk", "price": 1.75}
```

---

## 📤 Step 4: Response Models

Control what the API returns:

```python
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    created_at: datetime

    class Config:
        from_attributes = True

# response_model tells FastAPI the shape of the response
@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    # Even if you return extra fields, only ItemResponse fields are sent
    return {"id": item_id, "name": "Milk", "price": 1.50,
            "created_at": datetime.now(), "secret": "hidden"}
    # "secret" won't appear in the response!
```

### Return a List

```python
@app.get("/items", response_model=list[ItemResponse])
def list_items():
    return [
        {"id": 1, "name": "Milk", "price": 1.50, "created_at": datetime.now()},
        {"id": 2, "name": "Bread", "price": 2.00, "created_at": datetime.now()},
    ]
```

---

## ⚠️ Step 5: Error Handling

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

items_db = {1: "Milk", 2: "Bread"}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in items_db:
        # Raise an HTTP 404 error with a message
        raise HTTPException(
            status_code=404,
            detail=f"Item with id {item_id} not found"
        )
    return {"id": item_id, "name": items_db[item_id]}
```

### Common HTTP Status Codes

| Code | Meaning               | When to Use                  |
|------|----------------------|------------------------------|
| 200  | OK                   | Successful GET/PUT           |
| 201  | Created              | Successful POST (new record) |
| 204  | No Content           | Successful DELETE            |
| 400  | Bad Request          | Invalid input data           |
| 404  | Not Found            | Record doesn't exist         |
| 422  | Unprocessable Entity | Validation error             |
| 500  | Internal Server Error| Server bug                   |

---

## 📁 Step 6: Routers (Organizing Endpoints)

Split your API into separate files:

```python
# routers/items.py
from fastapi import APIRouter

# Create a router with a URL prefix and Swagger tag
router = APIRouter(prefix="/items", tags=["Items"])

@router.get("/")
def list_items():
    return {"items": ["Milk", "Bread"]}

@router.get("/{item_id}")
def get_item(item_id: int):
    return {"item_id": item_id}
```

```python
# main.py
from fastapi import FastAPI
from routers import items

app = FastAPI()

# Include the router — all its endpoints become part of the app
app.include_router(items.router)
# Now the endpoints are: GET /items/, GET /items/{item_id}
```

---

## 🔌 Step 7: Dependency Injection

Share common logic (like DB sessions) across endpoints:

```python
from fastapi import FastAPI, Depends

app = FastAPI()

# A dependency function
def get_current_user():
    # In real apps, this would verify a token/session
    return {"user_id": 1, "name": "Ahmed"}

# Use Depends() to inject the dependency
@app.get("/profile")
def get_profile(user=Depends(get_current_user)):
    return {"profile": user}

# Database session dependency (common pattern)
def get_db():
    db = SessionLocal()
    try:
        yield db        # Provide the session to the route
    finally:
        db.close()      # Always close when done

@app.get("/items")
def list_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

---

## 🚀 Step 8: Lifespan Events (Startup/Shutdown)

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup code runs here ──
    print("Starting up... Creating tables...")
    init_db()
    yield  # App is now running
    # ── Shutdown code runs here ──
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)
```

---

## 📝 Step 9: Custom Status Codes

```python
from fastapi import FastAPI

app = FastAPI()

# Return 201 Created instead of default 200
@app.post("/items", status_code=201)
def create_item():
    return {"message": "Created!"}

# Return 204 No Content for delete operations
@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    # No return needed for 204
    pass
```

---

## 📝 Quick Reference — Complete App

```python
from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="My API", version="1.0.0")

# Pydantic schemas
class ItemCreate(BaseModel):
    name: str
    price: float

class ItemResponse(BaseModel):
    id: int
    name: str
    price: float

# In-memory storage (use a real DB in production)
items = {}
next_id = 1

@app.get("/items", response_model=list[ItemResponse])
def list_items(min_price: Optional[float] = Query(None, ge=0)):
    result = list(items.values())
    if min_price:
        result = [i for i in result if i["price"] >= min_price]
    return result

@app.post("/items", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate):
    global next_id
    new = {"id": next_id, **item.model_dump()}
    items[next_id] = new
    next_id += 1
    return new

@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    if item_id not in items:
        raise HTTPException(404, detail="Not found")
    return items[item_id]

@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    if item_id not in items:
        raise HTTPException(404, detail="Not found")
    del items[item_id]
```

```bash
# Run with:
uvicorn main:app --reload
# Docs at: http://localhost:8000/docs
```
