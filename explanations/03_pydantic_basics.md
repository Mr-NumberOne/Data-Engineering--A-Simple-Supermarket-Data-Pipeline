# Pydantic — Complete Beginner Guide

Pydantic is a **data validation library** for Python. It uses Python type hints to define the structure of your data and automatically validates it. If the data doesn't match, Pydantic raises clear error messages.

---

## 📦 Installation

```bash
pip install pydantic
```

---

## 🏗️ Step 1: Create a Basic Schema (Model)

A **schema** (or model) defines what your data should look like:

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str        # Must be a string
    age: int         # Must be an integer
    email: str       # Must be a string
```

### Using the Schema

```python
# ✅ Valid data — works perfectly
user = User(name="Ahmed", age=25, email="ahmed@example.com")
print(user.name)   # "Ahmed"
print(user.age)    # 25
print(user.email)  # "ahmed@example.com"

# ✅ Auto-conversion — Pydantic converts "25" (string) to 25 (int)
user = User(name="Ahmed", age="25", email="ahmed@example.com")
print(user.age)    # 25 (converted to int)
print(type(user.age))  # <class 'int'>

# ❌ Invalid data — raises ValidationError
user = User(name="Ahmed", age="not_a_number", email="ahmed@example.com")
# Error: value is not a valid integer
```

---

## 📋 Step 2: Field Types

### Basic Types

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Product(BaseModel):
    name: str                          # Required string
    price: float                       # Required float
    quantity: int                      # Required integer
    in_stock: bool                     # Required boolean
    created_at: datetime               # Required datetime
    description: Optional[str] = None  # Optional (can be None), defaults to None
    category: str = "General"          # Has a default value
```

```python
# Using it:
product = Product(
    name="Milk",
    price=1.50,
    quantity=100,
    in_stock=True,
    created_at="2026-03-09T10:30:00"  # Pydantic auto-parses datetime strings!
)

print(product.created_at)  # 2026-03-09 10:30:00
print(product.description) # None (used the default)
print(product.category)    # "General" (used the default)
```

### Lists and Dicts

```python
from pydantic import BaseModel

class Order(BaseModel):
    items: list[str]                  # A list of strings
    prices: list[float]              # A list of floats
    metadata: dict[str, str]         # A dict with string keys and values
    quantities: list[int] = []       # Default to empty list
```

```python
order = Order(
    items=["Milk", "Bread"],
    prices=[1.50, 2.00],
    metadata={"source": "online", "priority": "high"}
)
```

---

## ✅ Step 3: Field Validation with `Field()`

Add constraints to your fields:

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(
        ...,                    # ... means "required" (no default)
        min_length=1,           # Must be at least 1 character
        max_length=100,         # Must be at most 100 characters
        description="Product name"  # Documentation for Swagger/OpenAPI
    )
    price: float = Field(
        ...,
        gt=0,                   # Greater than 0 (must be positive)
        description="Price in USD"
    )
    quantity: int = Field(
        default=1,              # Default value
        ge=0,                   # Greater than or equal to 0
        le=10000,               # Less than or equal to 10000
    )
    discount: float = Field(
        default=0.0,
        ge=0.0,                 # Min discount: 0%
        le=1.0,                 # Max discount: 100% (as 1.0)
    )
```

### Field Constraint Reference

| Constraint   | Applies To | Meaning                        |
|-------------|------------|--------------------------------|
| `gt`        | Numbers    | Greater than                   |
| `ge`        | Numbers    | Greater than or equal to       |
| `lt`        | Numbers    | Less than                      |
| `le`        | Numbers    | Less than or equal to          |
| `min_length`| Strings    | Minimum string length          |
| `max_length`| Strings    | Maximum string length          |
| `pattern`   | Strings    | Must match regex pattern       |
| `...`       | Any        | Field is required (no default) |

---

## 🔄 Step 4: Converting Data

### To Dictionary

```python
user = User(name="Ahmed", age=25, email="ahmed@example.com")

# Convert to a dictionary
data = user.model_dump()
print(data)  # {'name': 'Ahmed', 'age': 25, 'email': 'ahmed@example.com'}

# Exclude specific fields
data = user.model_dump(exclude={"email"})
print(data)  # {'name': 'Ahmed', 'age': 25}

# Only include specific fields
data = user.model_dump(include={"name", "age"})
print(data)  # {'name': 'Ahmed', 'age': 25}

# Exclude fields that weren't explicitly set (useful for updates)
data = user.model_dump(exclude_unset=True)
```

### To JSON String

```python
json_str = user.model_dump_json()
print(json_str)  # '{"name":"Ahmed","age":25,"email":"ahmed@example.com"}'
```

### From Dictionary

```python
data = {"name": "Ahmed", "age": 25, "email": "ahmed@example.com"}
user = User(**data)  # Unpack dict as keyword arguments
# or
user = User.model_validate(data)
```

### From JSON String

```python
json_str = '{"name": "Ahmed", "age": 25, "email": "ahmed@example.com"}'
user = User.model_validate_json(json_str)
```

---

## 🔗 Step 5: Nested Models

Models can contain other models:

```python
from pydantic import BaseModel
from typing import Optional

class Address(BaseModel):
    street: str
    city: str
    country: str = "Saudi Arabia"

class Customer(BaseModel):
    name: str
    age: int
    address: Address                    # Nested model (required)
    shipping_address: Optional[Address] = None  # Nested model (optional)
```

```python
customer = Customer(
    name="Ahmed",
    age=30,
    address={"street": "123 Main St", "city": "Riyadh"}
    # Pydantic auto-converts the dict to an Address object!
)

print(customer.address.city)     # "Riyadh"
print(customer.address.country)  # "Saudi Arabia" (used default)
```

---

## ⚙️ Step 6: Model Configuration

```python
from pydantic import BaseModel

class Product(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        # Allow creating from ORM objects (SQLAlchemy models)
        from_attributes = True

        # Example data shown in documentation
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Milk",
                "price": 1.50,
            }
        }
```

### Using `from_attributes = True` with SQLAlchemy

```python
# SQLAlchemy ORM object
class ProductDB(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    price = Column(Float)

# Query from database
db_product = session.query(ProductDB).first()
# db_product.name, db_product.price, etc.

# Convert ORM object → Pydantic model
product_response = Product.from_orm(db_product)
# or with Config from_attributes = True:
product_response = Product.model_validate(db_product)
```

---

## 🧩 Step 7: Separate Schemas for Create/Update/Response

A common pattern in APIs:

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Schema for creating new records (no id, no timestamps)
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)

# Schema for updating records (all fields optional)
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)

# Schema for responses (includes auto-generated fields)
class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    created_at: datetime

    class Config:
        from_attributes = True
```

---

## 📝 Quick Reference

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Define a schema
class Item(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    qty: int = Field(default=1, ge=0)
    notes: Optional[str] = None

# Create from data
item = Item(name="Milk", price=1.50)

# Access fields
print(item.name)             # "Milk"
print(item.price)            # 1.50

# Convert to dict/JSON
print(item.model_dump())     # {'name': 'Milk', 'price': 1.5, 'qty': 1, 'notes': None}
print(item.model_dump_json())# '{"name":"Milk","price":1.5,"qty":1,"notes":null}'

# Validation (this will raise an error)
try:
    bad = Item(name="", price=-5)
except Exception as e:
    print(e)  # Shows detailed validation errors
```
