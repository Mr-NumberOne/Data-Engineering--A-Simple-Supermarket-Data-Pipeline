# SQLAlchemy — Complete Beginner Guide

SQLAlchemy is a Python SQL toolkit and **Object Relational Mapper (ORM)** that lets you interact with databases using Python objects instead of writing raw SQL.

---

## 📦 Installation

```bash
pip install sqlalchemy psycopg2-binary
```

- `sqlalchemy` — the ORM library itself
- `psycopg2-binary` — PostgreSQL driver (SQLAlchemy needs a driver to talk to the actual database)

---

## 🔗 Step 1: Connect to the Database

```python
from sqlalchemy import create_engine

# Connection URL format: "dialect://username:password@host:port/database_name"
DATABASE_URL = "postgresql://postgres:root@localhost:5432/store_data_db"

# create_engine() creates a connection pool (not a single connection)
# echo=True prints all SQL queries to the console (great for debugging)
engine = create_engine(DATABASE_URL, echo=True)
```

### Common Database URLs

| Database   | URL Format                                            |
|------------|-------------------------------------------------------|
| PostgreSQL | `postgresql://user:pass@host:port/dbname`             |
| MySQL      | `mysql+pymysql://user:pass@host:port/dbname`          |
| SQLite     | `sqlite:///path/to/database.db`                       |

---

## 🏗️ Step 2: Create a Session Factory

A **session** is like an open conversation with the database. You use it to add, query, update, and delete data.

```python
from sqlalchemy.orm import sessionmaker

# sessionmaker creates a factory — calling SessionLocal() gives you a new session
SessionLocal = sessionmaker(
    autocommit=False,   # We control when to commit (save) changes
    autoflush=False,    # We control when to flush (send) changes to DB
    bind=engine         # Link this session factory to our engine
)

# Create a session
session = SessionLocal()
```

---

## 📋 Step 3: Define a Model (Table)

A **model** is a Python class that represents a database table. Each attribute is a column.

```python
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

# Base is the parent class for all models
Base = declarative_base()


class Product(Base):
    """Each instance of this class = one row in the 'products' table."""

    __tablename__ = "products"  # The actual table name in the database

    # Define columns:
    id = Column(Integer, primary_key=True, autoincrement=True)  # Auto-generated ID
    name = Column(String(100), nullable=False)                   # Required text field
    price = Column(Float, nullable=False)                        # Required decimal field
    category = Column(String(50), nullable=True, default="General")  # Optional with default
    created_at = Column(DateTime, default=datetime.utcnow)       # Auto-set to current time

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
```

### Column Types

| SQLAlchemy Type | Python Type | SQL Type          |
|-----------------|-------------|-------------------|
| `Integer`       | `int`       | `INTEGER`         |
| `String(100)`   | `str`       | `VARCHAR(100)`    |
| `Text`          | `str`       | `TEXT`            |
| `Float`         | `float`     | `FLOAT`           |
| `Boolean`       | `bool`      | `BOOLEAN`         |
| `DateTime`      | `datetime`  | `TIMESTAMP`       |

### Column Options

| Option          | Description                                  |
|-----------------|----------------------------------------------|
| `primary_key`   | Makes this column the primary key            |
| `autoincrement` | Auto-generates sequential IDs                |
| `nullable`      | `False` = required, `True` = optional        |
| `default`       | Default value if none is provided            |
| `unique`        | No duplicate values allowed                  |
| `index`         | Creates a database index for faster queries  |

---

## 🏗️ Step 4: Create the Tables

```python
# This creates all tables defined by models that inherit from Base
# If tables already exist, they are NOT recreated (safe to call multiple times)
Base.metadata.create_all(bind=engine)
```

---

## ✏️ Step 5: CRUD Operations

### CREATE — Insert New Records

```python
session = SessionLocal()

# Create a new Product object
new_product = Product(name="Milk", price=1.50, category="Dairy")

# Add it to the session (staged, not saved yet)
session.add(new_product)

# Commit the transaction (saves to database)
session.commit()

# After commit, the object now has an auto-generated ID
print(new_product.id)  # e.g., 1

# You can also add multiple records at once
products = [
    Product(name="Bread", price=2.00, category="Bakery"),
    Product(name="Eggs", price=3.25, category="Dairy"),
    Product(name="Rice", price=4.00, category="Grains"),
]
session.add_all(products)
session.commit()
```

### READ — Query Records

```python
# Get ALL records
all_products = session.query(Product).all()
# Returns: [<Product(id=1, ...)>, <Product(id=2, ...)>, ...]

# Get ONE record by primary key
product = session.query(Product).get(1)
# Returns: <Product(id=1, name='Milk', price=1.5)>

# Filter with conditions
dairy_products = session.query(Product).filter(Product.category == "Dairy").all()
# Returns all products where category is "Dairy"

# Filter with multiple conditions (AND)
cheap_dairy = (
    session.query(Product)
    .filter(Product.category == "Dairy")
    .filter(Product.price < 2.00)
    .all()
)

# Get the first matching record (or None)
first_product = session.query(Product).filter(Product.name == "Milk").first()

# Order results
sorted_products = session.query(Product).order_by(Product.price.desc()).all()

# Limit results
top_5 = session.query(Product).order_by(Product.price.desc()).limit(5).all()

# Count records
total = session.query(Product).count()

# Pagination (skip first 10, take next 20)
page = session.query(Product).offset(10).limit(20).all()
```

### UPDATE — Modify Existing Records

```python
# Method 1: Query, modify, commit
product = session.query(Product).filter(Product.id == 1).first()
product.price = 1.75      # Change the price
product.name = "Whole Milk"  # Change the name
session.commit()           # Save changes

# Method 2: Bulk update
session.query(Product).filter(Product.category == "Dairy").update(
    {"price": 2.00}  # Set all dairy products to price 2.00
)
session.commit()
```

### DELETE — Remove Records

```python
# Method 1: Query, delete, commit
product = session.query(Product).filter(Product.id == 1).first()
session.delete(product)
session.commit()

# Method 2: Bulk delete
session.query(Product).filter(Product.category == "Expired").delete()
session.commit()
```

---

## 🔄 Step 6: Session Management (Best Practices)

Always close sessions and handle errors properly:

```python
session = SessionLocal()

try:
    # Do your database operations here
    new_product = Product(name="Coffee", price=6.00)
    session.add(new_product)
    session.commit()

except Exception as e:
    # If anything fails, undo all changes in this session
    session.rollback()
    print(f"Error: {e}")

finally:
    # Always close the session when done
    session.close()
```

---

## 🔗 Step 7: Using Raw SQL (When Needed)

Sometimes you need to run raw SQL:

```python
from sqlalchemy import text

# Execute a raw SQL query
result = session.execute(text("SELECT * FROM products WHERE price > :min_price"), {"min_price": 2.0})

# Iterate over results
for row in result:
    print(row)

# Delete all rows from a table
session.execute(text("DELETE FROM products"))
session.commit()
```

---

## 📊 Step 8: Reading Tables into Pandas

SQLAlchemy works great with Pandas:

```python
import pandas as pd

# Read an entire table into a DataFrame
df = pd.read_sql_table("products", con=engine)

# Run a custom query and load results into a DataFrame
df = pd.read_sql("SELECT * FROM products WHERE price > 2.0", con=engine)

print(df.head())
```

---

## 📝 Quick Reference — Complete Flow

```python
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Connect
engine = create_engine("postgresql://postgres:root@localhost:5432/mydb")

# 2. Create session factory
SessionLocal = sessionmaker(bind=engine)

# 3. Define model
Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)

# 4. Create tables
Base.metadata.create_all(bind=engine)

# 5. Use it!
session = SessionLocal()
try:
    session.add(Item(name="Apple", price=0.50))  # CREATE
    session.commit()
    items = session.query(Item).all()             # READ
    print(items)
finally:
    session.close()
```
