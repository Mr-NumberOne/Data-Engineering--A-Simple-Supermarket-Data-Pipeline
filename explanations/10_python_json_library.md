# Python `json` Library — Complete Beginner Guide

The `json` module lets you **read and write JSON data** in Python. JSON (JavaScript Object Notation) is the most common format for exchanging data between systems.

---

## 📦 Import

```python
import json
```

No installation needed — `json` is a **built-in Python module**.

---

## 📋 What is JSON?

JSON is a text format for storing structured data. It looks very similar to Python dictionaries and lists:

```json
{
    "name": "Ahmed",
    "age": 25,
    "is_student": false,
    "courses": ["Math", "Science"],
    "address": {
        "city": "Riyadh",
        "country": "Saudi Arabia"
    }
}
```

### Python ↔ JSON Type Mapping

| Python Type    | JSON Type   | Example              |
|---------------|-------------|----------------------|
| `dict`        | Object      | `{"key": "value"}`   |
| `list`        | Array       | `[1, 2, 3]`          |
| `str`         | String      | `"hello"`            |
| `int`         | Number      | `42`                 |
| `float`       | Number      | `3.14`               |
| `True`        | `true`      | `true`               |
| `False`       | `false`     | `false`              |
| `None`        | `null`      | `null`               |

---

## 🔄 Step 1: Converting Between Python and JSON

### `json.dumps()` — Python → JSON String

```python
import json

# Convert a Python dictionary to a JSON string
data = {"name": "Ahmed", "age": 25, "city": "Riyadh"}

json_string = json.dumps(data)
print(json_string)       # '{"name": "Ahmed", "age": 25, "city": "Riyadh"}'
print(type(json_string)) # <class 'str'>
```

### `json.loads()` — JSON String → Python

```python
import json

# Convert a JSON string back to a Python dictionary
json_string = '{"name": "Ahmed", "age": 25, "city": "Riyadh"}'

data = json.loads(json_string)
print(data)              # {'name': 'Ahmed', 'age': 25, 'city': 'Riyadh'}
print(type(data))        # <class 'dict'>
print(data["name"])      # "Ahmed"
```

> **Memory trick:** `dumps` = dump **s**tring, `loads` = load **s**tring

---

## 📄 Step 2: Reading and Writing JSON Files

### `json.dump()` — Write Python Data → JSON File

```python
import json

data = {
    "branch": "Branch_A",
    "items": [
        {"name": "Milk", "price": 1.50, "quantity": 5},
        {"name": "Bread", "price": 2.00, "quantity": 3},
    ],
    "total": 13.50
}

# Write data to a JSON file
with open("sales.json", "w", encoding="utf-8") as f:
    json.dump(data, f)

print("Data written to sales.json")
```

### `json.load()` — Read JSON File → Python Data

```python
import json

# Read data from a JSON file
with open("sales.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(data["branch"])          # "Branch_A"
print(data["items"][0]["name"]) # "Milk"
print(data["total"])           # 13.5
```

> **Memory trick:** `dump` = write to **f**ile, `load` = read from **f**ile
> (no "s" = file operations, with "s" = string operations)

---

## 🎨 Step 3: Formatting Options

### Pretty-Print with Indentation

```python
import json

data = {"name": "Ahmed", "scores": [95, 88, 76], "passed": True}

# indent=2 adds 2-space indentation for readability
pretty = json.dumps(data, indent=2)
print(pretty)
```

Output:

```json
{
  "name": "Ahmed",
  "scores": [
    95,
    88,
    76
  ],
  "passed": true
}
```

### Sort Keys Alphabetically

```python
sorted_json = json.dumps(data, indent=2, sort_keys=True)
print(sorted_json)
```

Output:

```json
{
  "name": "Ahmed",
  "passed": true,
  "scores": [
    95,
    88,
    76
  ]
}
```

### Handle Non-ASCII Characters

```python
data = {"name": "أحمد", "city": "الرياض"}

# Default: non-ASCII characters are escaped
print(json.dumps(data))
# '{"name": "\\u0623\\u062d\\u0645\\u062f", ...}'

# ensure_ascii=False: keep the original characters
print(json.dumps(data, ensure_ascii=False))
# '{"name": "أحمد", "city": "الرياض"}'
```

### Write Pretty JSON to a File

```python
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
```

---

## 📋 Step 4: Working with Lists of Records

A very common pattern — list of dictionaries:

```python
import json

# A list of sales records (like our supermarket data)
records = [
    {"branch": "Branch_A", "item": "Milk", "quantity": 5, "price": 1.50},
    {"branch": "Branch_A", "item": "Bread", "quantity": 3, "price": 2.00},
    {"branch": "Branch_B", "item": "Eggs", "quantity": 2, "price": 3.25},
]

# Write to file
with open("sales_data.json", "w", encoding="utf-8") as f:
    json.dump(records, f, indent=2)

# Read from file
with open("sales_data.json", "r", encoding="utf-8") as f:
    loaded_records = json.load(f)

# Now loaded_records is a Python list of dicts
for record in loaded_records:
    total = record["quantity"] * record["price"]
    print(f"{record['item']}: {record['quantity']} × {record['price']} = {total}")
```

Output:

```
Milk: 5 × 1.5 = 7.5
Bread: 3 × 2.0 = 6.0
Eggs: 2 × 3.25 = 6.5
```

---

## ⚠️ Step 5: Error Handling

### Handling Invalid JSON

```python
import json

bad_json = '{"name": "Ahmed", "age": }'  # Invalid JSON (missing value)

try:
    data = json.loads(bad_json)
except json.JSONDecodeError as e:
    print(f"Invalid JSON: {e}")
    # Invalid JSON: Expecting value: line 1 column 27 (char 26)
```

### Handling Missing Files

```python
import json
import os

filepath = "data.json"

if os.path.exists(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)
else:
    print(f"File {filepath} not found!")
    data = []  # Default to empty list
```

---

## 🧩 Step 6: Converting Non-Standard Types

JSON can only store basic types (str, int, float, bool, None, list, dict). For other types, you need a **custom serializer**:

```python
import json
from datetime import datetime

data = {
    "event": "Sale",
    "timestamp": datetime.now(),  # datetime is NOT JSON-serializable!
}

# This will FAIL:
# json.dumps(data)  # TypeError: Object of type datetime is not JSON serializable

# Solution 1: Convert manually before dumping
data["timestamp"] = data["timestamp"].isoformat()
print(json.dumps(data))
# '{"event": "Sale", "timestamp": "2026-03-09T14:30:00"}'

# Solution 2: Use default parameter with a custom serializer
def custom_serializer(obj):
    """Convert non-standard types to JSON-compatible formats."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

data = {"event": "Sale", "timestamp": datetime.now()}
print(json.dumps(data, default=custom_serializer))
```

---

## 📝 Quick Reference

| Function        | Direction                | What it Does                      |
|-----------------|--------------------------|-----------------------------------|
| `json.dumps()`  | Python → JSON string     | Convert Python object to string   |
| `json.loads()`  | JSON string → Python     | Parse JSON string to Python       |
| `json.dump()`   | Python → JSON file       | Write Python object to a file     |
| `json.load()`   | JSON file → Python       | Read a file into a Python object  |

### Common Parameters

| Parameter        | Used In           | Purpose                              |
|-----------------|-------------------|--------------------------------------|
| `indent=2`      | `dump` / `dumps`  | Pretty-print with indentation        |
| `sort_keys=True`| `dump` / `dumps`  | Sort dictionary keys alphabetically  |
| `ensure_ascii=False` | `dump` / `dumps` | Keep non-ASCII chars as-is      |
| `encoding="utf-8"` | `open()`       | Handle all character encodings       |
| `default=func`  | `dump` / `dumps`  | Custom serializer for special types  |

### Complete Example

```python
import json

# ── Write ──
data = [
    {"name": "Milk", "price": 1.50},
    {"name": "Bread", "price": 2.00},
]

with open("products.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# ── Read ──
with open("products.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)

for item in loaded:
    print(f"{item['name']}: ${item['price']}")
# Milk: $1.5
# Bread: $2.0
```
