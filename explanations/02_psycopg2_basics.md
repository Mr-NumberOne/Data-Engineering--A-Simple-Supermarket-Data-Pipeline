# Psycopg2 — Complete Beginner Guide

Psycopg2 is the most popular **PostgreSQL adapter for Python**. Unlike SQLAlchemy (which is an ORM), psycopg2 lets you write **raw SQL commands** directly.

---

## 📦 Installation

```bash
pip install psycopg2-binary
```

> `psycopg2-binary` is a pre-compiled version that's easier to install.
> For production, use `psycopg2` (requires PostgreSQL dev libraries).

---

## 🔗 Step 1: Connect to the Database

```python
import psycopg2

# Connect to an existing PostgreSQL database
conn = psycopg2.connect(
    host="localhost",       # Database server address
    port="5432",            # PostgreSQL default port
    dbname="store_data_db", # Name of the database
    user="postgres",        # Username
    password="root"         # Password
)

print("Connected successfully!")
```

### Connection with a URL String

```python
conn = psycopg2.connect("postgresql://postgres:root@localhost:5432/store_data_db")
```

---

## 📌 Step 2: Create a Cursor

A **cursor** is used to execute SQL commands and fetch results:

```python
# Create a cursor object
cursor = conn.cursor()
```

---

## 🏗️ Step 3: Create a Table

```python
# Define the CREATE TABLE SQL command
create_table_sql = """
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        price FLOAT NOT NULL,
        category VARCHAR(50) DEFAULT 'General',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""

# Execute the SQL
cursor.execute(create_table_sql)

# Commit the transaction (saves the changes to the database)
conn.commit()

print("Table created!")
```

---

## ✏️ Step 4: CRUD Operations

### CREATE — Insert Records

```python
# Insert a single record
cursor.execute(
    "INSERT INTO products (name, price, category) VALUES (%s, %s, %s)",
    ("Milk", 1.50, "Dairy")  # Parameters are passed as a tuple
)
conn.commit()

# Insert multiple records at once
records = [
    ("Bread", 2.00, "Bakery"),
    ("Eggs", 3.25, "Dairy"),
    ("Rice", 4.00, "Grains"),
    ("Coffee", 6.00, "Beverages"),
]
cursor.executemany(
    "INSERT INTO products (name, price, category) VALUES (%s, %s, %s)",
    records
)
conn.commit()

print("Records inserted!")
```

> ⚠️ **Always use `%s` placeholders** — NEVER use f-strings or string concatenation.
> This prevents **SQL injection** attacks.

```python
# ❌ WRONG — vulnerable to SQL injection
cursor.execute(f"INSERT INTO products (name) VALUES ('{user_input}')")

# ✅ CORRECT — safe parameterized query
cursor.execute("INSERT INTO products (name) VALUES (%s)", (user_input,))
```

### READ — Query Records

```python
# Fetch ALL records
cursor.execute("SELECT * FROM products")
rows = cursor.fetchall()  # Returns a list of tuples

for row in rows:
    print(row)
# Output: (1, 'Milk', 1.5, 'Dairy', datetime(...))
#         (2, 'Bread', 2.0, 'Bakery', datetime(...))

# Fetch ONE record
cursor.execute("SELECT * FROM products WHERE id = %s", (1,))
row = cursor.fetchone()  # Returns a single tuple, or None
print(row)  # (1, 'Milk', 1.5, 'Dairy', datetime(...))

# Fetch specific number of records
cursor.execute("SELECT * FROM products ORDER BY price DESC")
top_3 = cursor.fetchmany(3)  # Returns first 3 rows

# Filter with conditions
cursor.execute("SELECT * FROM products WHERE price > %s AND category = %s", (2.0, "Dairy"))
expensive_dairy = cursor.fetchall()

# Count records
cursor.execute("SELECT COUNT(*) FROM products")
count = cursor.fetchone()[0]  # fetchone returns a tuple, [0] gets the first value
print(f"Total products: {count}")
```

### Getting Column Names

```python
cursor.execute("SELECT * FROM products")

# cursor.description contains column metadata
column_names = [desc[0] for desc in cursor.description]
print(column_names)  # ['id', 'name', 'price', 'category', 'created_at']

# Combine with data to make dicts
rows = cursor.fetchall()
products = [dict(zip(column_names, row)) for row in rows]
print(products)
# [{'id': 1, 'name': 'Milk', 'price': 1.5, ...}, ...]
```

### UPDATE — Modify Records

```python
# Update a single record
cursor.execute(
    "UPDATE products SET price = %s WHERE name = %s",
    (1.75, "Milk")
)
conn.commit()

# Update multiple records (bulk)
cursor.execute(
    "UPDATE products SET price = price * 1.10 WHERE category = %s",
    ("Dairy",)  # Increase all dairy prices by 10%
)
conn.commit()

print(f"{cursor.rowcount} rows updated")  # cursor.rowcount = number of affected rows
```

### DELETE — Remove Records

```python
# Delete a specific record
cursor.execute("DELETE FROM products WHERE id = %s", (1,))
conn.commit()

# Delete all records in a category
cursor.execute("DELETE FROM products WHERE category = %s", ("Expired",))
conn.commit()

print(f"{cursor.rowcount} rows deleted")
```

---

## 🔄 Step 5: Transaction Management

```python
try:
    cursor.execute("INSERT INTO products (name, price) VALUES (%s, %s)", ("Apple", 0.80))
    cursor.execute("INSERT INTO products (name, price) VALUES (%s, %s)", ("Banana", 0.50))

    # Commit only if both inserts succeed
    conn.commit()
    print("Transaction committed!")

except Exception as e:
    # If any error occurs, undo ALL changes
    conn.rollback()
    print(f"Transaction rolled back: {e}")
```

---

## 🗄️ Step 6: Creating a Database

`CREATE DATABASE` cannot run inside a transaction, so you need `AUTOCOMMIT` mode:

```python
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connect to the default 'postgres' database
conn = psycopg2.connect(
    host="localhost", port="5432",
    user="postgres", password="root",
    dbname="postgres"  # Default DB that always exists
)

# Enable AUTOCOMMIT mode (required for CREATE DATABASE)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()

# Check if database exists
cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", ("my_new_db",))

if not cursor.fetchone():
    cursor.execute('CREATE DATABASE "my_new_db"')
    print("Database created!")
else:
    print("Database already exists.")

cursor.close()
conn.close()
```

---

## 🧹 Step 7: Always Clean Up

```python
# Always close cursor and connection when done
cursor.close()
conn.close()
```

### Using `with` Statement (Recommended)

```python
import psycopg2

# 'with' automatically handles commit/rollback
with psycopg2.connect(host="localhost", dbname="store_data_db",
                       user="postgres", password="root") as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
# Connection is NOT closed automatically with 'with' — only commits/rollbacks
# You still need to close it explicitly in production code
```

---

## 📝 Quick Reference — Complete Flow

```python
import psycopg2

# 1. Connect
conn = psycopg2.connect(host="localhost", dbname="store_data_db",
                         user="postgres", password="root")

# 2. Create cursor
cursor = conn.cursor()

# 3. Create table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        price FLOAT NOT NULL
    )
""")
conn.commit()

# 4. INSERT
cursor.execute("INSERT INTO items (name, price) VALUES (%s, %s)", ("Apple", 0.50))
conn.commit()

# 5. SELECT
cursor.execute("SELECT * FROM items")
print(cursor.fetchall())

# 6. UPDATE
cursor.execute("UPDATE items SET price = %s WHERE name = %s", (0.75, "Apple"))
conn.commit()

# 7. DELETE
cursor.execute("DELETE FROM items WHERE name = %s", ("Apple",))
conn.commit()

# 8. Clean up
cursor.close()
conn.close()
```

---

## ⚖️ psycopg2 vs SQLAlchemy

| Feature        | psycopg2                  | SQLAlchemy                  |
|----------------|---------------------------|-----------------------------|
| SQL Style      | Raw SQL strings           | Python objects & methods    |
| Learning Curve | Easier (just SQL)         | Steeper (ORM concepts)     |
| Safety         | Manual parameterization   | Built-in protection        |
| Flexibility    | Full SQL control          | Some SQL is harder to write |
| Best For       | Simple scripts, DB admin  | Large apps, complex models |
