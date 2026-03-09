# SQLAlchemy + Pydantic + FastAPI — Integration Guide

This guide shows how to connect **SQLAlchemy** (database ORM), **Pydantic** (data validation), and **FastAPI** (web framework) together to build a complete REST API.

---

## 🏗️ The Big Picture

```
Client Request (JSON)
        ↓
   FastAPI Route
        ↓
   Pydantic Schema (validates the input)
        ↓
   SQLAlchemy Model (talks to the database)
        ↓
   PostgreSQL Database
        ↓
   SQLAlchemy Model (reads from DB)
        ↓
   Pydantic Schema (formats the output)
        ↓
Client Response (JSON)
```

| Layer      | Tool       | Purpose                              |
|------------|-----------|--------------------------------------|
| API        | FastAPI    | Receives requests, returns responses |
| Validation | Pydantic  | Validates input/output data shapes   |
| Database   | SQLAlchemy | Maps Python objects ↔ DB tables      |

---

## 📁 Recommended Folder Structure

```
project/
├── database/
│   ├── __init__.py
│   └── connection.py      ← Engine, Session, Base
├── models/
│   ├── __init__.py
│   └── product.py          ← SQLAlchemy model (table definition)
├── api/
│   ├── __init__.py
│   ├── main.py             ← FastAPI app
│   ├── dependencies.py     ← get_db() dependency
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── product.py      ← Pydantic schemas (Create, Update, Response)
│   └── routers/
│       ├── __init__.py
│       └── product.py      ← API endpoints (CRUD routes)
└── requirements.txt
```

---

## Step 1: Database Connection (`database/connection.py`)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql://postgres:root@localhost:5432/store_data_db"

# Create the engine (connection pool)
engine = create_engine(DATABASE_URL, echo=False)

# Create the session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()

def init_db():
    """Create all tables."""
    import models.product  # Register models with Base
    Base.metadata.create_all(bind=engine)
```

---

## Step 2: SQLAlchemy Model (`models/product.py`)

This defines the **database table**:

```python
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database.connection import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}')>"
```

---

## Step 3: Pydantic Schemas (`api/schemas/product.py`)

These define the **API request/response formats** — separate from the DB model:

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# ── CREATE schema (POST request body) ──
class ProductCreate(BaseModel):
    """What the client sends to create a new product."""
    name: str = Field(..., min_length=1, example="Milk")
    price: float = Field(..., gt=0, example=1.50)
    category: str = Field(..., example="Dairy")


# ── UPDATE schema (PUT request body) ──
class ProductUpdate(BaseModel):
    """What the client sends to update a product (all fields optional)."""
    name: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None


# ── RESPONSE schema (what the API returns) ──
class ProductResponse(BaseModel):
    """What the client receives when reading a product."""
    id: int
    name: str
    price: float
    category: str
    created_at: datetime

    class Config:
        from_attributes = True  # Allow conversion from SQLAlchemy objects
```

### Why Separate Schemas?

| Schema           | Has `id`? | Has `created_at`? | Fields Required? |
|------------------|-----------|-------------------|------------------|
| `ProductCreate`  | ❌ No     | ❌ No             | ✅ All required  |
| `ProductUpdate`  | ❌ No     | ❌ No             | ❌ All optional  |
| `ProductResponse`| ✅ Yes    | ✅ Yes            | ✅ All included  |

---

## Step 4: Dependency Injection (`api/dependencies.py`)

```python
from database.connection import SessionLocal

def get_db():
    """Provide a database session for each request, auto-close when done."""
    db = SessionLocal()
    try:
        yield db      # Give the session to the endpoint
    finally:
        db.close()    # Always close when the request finishes
```

---

## Step 5: API Endpoints (`api/routers/product.py`)

This connects everything together:

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from api.dependencies import get_db
from api.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from models.product import Product

router = APIRouter(prefix="/products", tags=["Products"])


# ── LIST (GET all, with filters) ──
@router.get("/", response_model=list[ProductResponse])
def list_products(
    category: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),            # ← Injected DB session
):
    query = db.query(Product)                  # ← SQLAlchemy query

    if category:
        query = query.filter(Product.category == category)

    return query.offset(skip).limit(limit).all()
    # FastAPI auto-converts SQLAlchemy objects → ProductResponse using from_attributes


# ── GET one by ID ──
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product  # Auto-converted to ProductResponse


# ── CREATE ──
@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(
    data: ProductCreate,          # ← Pydantic validates the request body
    db: Session = Depends(get_db),
):
    # Convert Pydantic schema → SQLAlchemy model
    new_product = Product(
        name=data.name,
        price=data.price,
        category=data.category,
    )

    db.add(new_product)     # Stage for insertion
    db.commit()             # Save to database
    db.refresh(new_product) # Reload to get auto-generated fields (id, created_at)

    return new_product      # Auto-converted to ProductResponse


# ── UPDATE ──
@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,          # ← All fields optional
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Only update fields that were explicitly provided
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


# ── DELETE ──
@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
```

---

## Step 6: Main App (`api/main.py`)

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.routers import product
from database.connection import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # Create tables on startup
    yield

app = FastAPI(title="My Store API", lifespan=lifespan)
app.include_router(product.router)

@app.get("/")
def root():
    return {"status": "ok"}
```

---

## 📊 Data Flow Summary

```
POST /products {"name": "Milk", "price": 1.50, "category": "Dairy"}

1. FastAPI receives the JSON request
2. Pydantic (ProductCreate) validates: name ✅, price > 0 ✅, category ✅
3. We create a SQLAlchemy Product object from the validated data
4. SQLAlchemy inserts it into the PostgreSQL products table
5. We refresh to get the auto-generated id and created_at
6. Pydantic (ProductResponse) formats the response
7. FastAPI returns JSON: {"id": 1, "name": "Milk", "price": 1.5, ...}
```
