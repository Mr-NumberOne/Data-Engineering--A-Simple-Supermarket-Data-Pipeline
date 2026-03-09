# Psycopg2 + Pydantic + FastAPI — Integration Guide

This guide shows how to build a REST API using **psycopg2** (raw SQL) instead of SQLAlchemy. You still use Pydantic for validation and FastAPI for the web layer.

---

## 🏗️ The Big Picture

```
Client Request (JSON)
        ↓
   FastAPI Route
        ↓
   Pydantic Schema (validates the input)
        ↓
   psycopg2 (executes raw SQL)
        ↓
   PostgreSQL Database
        ↓
   psycopg2 (fetches rows as tuples)
        ↓
   Convert to dict → Pydantic Schema (formats the output)
        ↓
Client Response (JSON)
```

| Layer      | Tool      | Purpose                               |
|------------|-----------|---------------------------------------|
| API        | FastAPI   | Receives requests, returns responses  |
| Validation | Pydantic  | Validates input/output data shapes    |
| Database   | psycopg2  | Executes raw SQL against PostgreSQL   |

---

## Step 1: Database Connection Helper

```python
# database/connection.py
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "dbname": "store_data_db",
    "user": "postgres",
    "password": "root",
}


def get_connection():
    """Create and return a new database connection."""
    return psycopg2.connect(**DB_CONFIG)


def get_db():
    """
    FastAPI dependency that provides a database connection.
    Uses RealDictCursor so rows are returned as dictionaries
    instead of tuples (makes it easier to work with Pydantic).
    """
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            price FLOAT NOT NULL,
            category VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("✔ Tables created / verified.")
```

---

## Step 2: Pydantic Schemas (Same as SQLAlchemy Version)

```python
# api/schemas/product.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ProductCreate(BaseModel):
    """Request body for creating a new product."""
    name: str = Field(..., min_length=1, example="Milk")
    price: float = Field(..., gt=0, example=1.50)
    category: str = Field(..., example="Dairy")


class ProductUpdate(BaseModel):
    """Request body for updating a product (all fields optional)."""
    name: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None


class ProductResponse(BaseModel):
    """Response body when reading a product."""
    id: int
    name: str
    price: float
    category: str
    created_at: datetime
```

> **Note:** No `from_attributes = True` needed — we'll convert DB rows to dicts manually.

---

## Step 3: API Endpoints with Raw SQL

```python
# api/routers/product.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from psycopg2.extras import RealDictCursor

from database.connection import get_db
from api.schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])


# ── Helper: Convert cursor results to list of dicts ──
def fetch_all_dicts(cursor):
    """Fetch all rows and convert to list of dicts using column names."""
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def fetch_one_dict(cursor):
    """Fetch one row and convert to dict."""
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))


# ── LIST (GET all with filters) ──
@router.get("/", response_model=list[ProductResponse])
def list_products(
    category: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    conn=Depends(get_db),          # ← psycopg2 connection injected
):
    cursor = conn.cursor()

    # Build SQL dynamically based on filters
    sql = "SELECT * FROM products"
    params = []

    if category:
        sql += " WHERE category = %s"
        params.append(category)

    sql += " ORDER BY id OFFSET %s LIMIT %s"
    params.extend([skip, limit])

    cursor.execute(sql, params)
    products = fetch_all_dicts(cursor)
    cursor.close()

    return products  # Pydantic validates each dict against ProductResponse


# ── GET one by ID ──
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, conn=Depends(get_db)):
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = fetch_one_dict(cursor)
    cursor.close()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


# ── CREATE ──
@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(data: ProductCreate, conn=Depends(get_db)):
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO products (name, price, category)
           VALUES (%s, %s, %s)
           RETURNING *""",         # RETURNING * gives us the inserted row back
        (data.name, data.price, data.category),
    )

    new_product = fetch_one_dict(cursor)
    conn.commit()         # Important: commit the transaction!
    cursor.close()

    return new_product


# ── UPDATE ──
@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, data: ProductUpdate, conn=Depends(get_db)):
    cursor = conn.cursor()

    # Check if product exists
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    if not cursor.fetchone():
        cursor.close()
        raise HTTPException(status_code=404, detail="Product not found")

    # Build UPDATE query dynamically from provided fields
    update_data = data.model_dump(exclude_unset=True)  # Only fields that were sent
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Build: UPDATE products SET name = %s, price = %s WHERE id = %s
    set_clause = ", ".join(f"{key} = %s" for key in update_data.keys())
    values = list(update_data.values()) + [product_id]

    cursor.execute(
        f"UPDATE products SET {set_clause} WHERE id = %s RETURNING *",
        values,
    )

    updated = fetch_one_dict(cursor)
    conn.commit()
    cursor.close()

    return updated


# ── DELETE ──
@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, conn=Depends(get_db)):
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM products WHERE id = %s", (product_id,))
    if not cursor.fetchone():
        cursor.close()
        raise HTTPException(status_code=404, detail="Product not found")

    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
    conn.commit()
    cursor.close()
```

---

## Step 4: Main App

```python
# api/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.routers import product
from database.connection import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="My Store API (psycopg2)", lifespan=lifespan)
app.include_router(product.router)

@app.get("/")
def root():
    return {"status": "ok"}
```

---

## ⚖️ Key Differences: psycopg2 vs SQLAlchemy Approach

| Aspect                  | psycopg2 (Raw SQL)                    | SQLAlchemy (ORM)                     |
|------------------------|---------------------------------------|--------------------------------------|
| **Queries**            | Write SQL strings manually            | Use Python methods `.query()`, `.filter()` |
| **Results**            | Tuples → must convert to dicts        | ORM objects → auto-convert with `from_attributes` |
| **Insert**             | `INSERT INTO ... VALUES (%s, %s)`     | `session.add(Product(...))` |
| **Migrations**         | Manual SQL `ALTER TABLE`              | Can use Alembic for auto-migrations |
| **Pydantic Config**    | No `from_attributes` needed           | Needs `from_attributes = True` |
| **Error Handling**     | `conn.rollback()` + `conn.close()`    | `session.rollback()` + `session.close()` |
| **Best For**           | Simple apps, full SQL control         | Complex apps, many relationships |

---

## 📝 Using RealDictCursor (Alternative to Manual Conversion)

Instead of converting tuples to dicts manually, use `RealDictCursor`:

```python
from psycopg2.extras import RealDictCursor

conn = get_connection()
cursor = conn.cursor(cursor_factory=RealDictCursor)

cursor.execute("SELECT * FROM products")
rows = cursor.fetchall()
# rows is already a list of dicts!
# [{'id': 1, 'name': 'Milk', 'price': 1.5, ...}, ...]

cursor.close()
conn.close()
```

This is even simpler — no need for the `fetch_all_dicts` helper!
