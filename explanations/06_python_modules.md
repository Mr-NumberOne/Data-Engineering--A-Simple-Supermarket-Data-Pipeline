# Python Modules — Complete Beginner Guide

A **module** is simply a `.py` file containing Python code (functions, classes, variables). A **package** is a folder containing multiple modules with an `__init__.py` file.

---

## 📁 Step 1: What is a Module?

Any `.py` file is a module:

```
my_project/
├── math_utils.py     ← This is a module
├── string_utils.py   ← This is a module
└── main.py           ← This is also a module
```

```python
# math_utils.py
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

PI = 3.14159
```

---

## 📥 Step 2: Importing Modules

### Import the Entire Module

```python
# main.py
import math_utils

result = math_utils.add(3, 5)        # 8
result = math_utils.multiply(4, 7)   # 28
print(math_utils.PI)                 # 3.14159
```

### Import Specific Items

```python
from math_utils import add, PI

result = add(3, 5)   # 8 — no need for "math_utils." prefix
print(PI)            # 3.14159
```

### Import with an Alias

```python
import math_utils as mu

result = mu.add(3, 5)  # 8
```

### Import Everything (Not Recommended)

```python
from math_utils import *

result = add(3, 5)       # Works, but you don't know where 'add' came from
result = multiply(4, 7)  # Can cause naming conflicts
```

---

## 📦 Step 3: Packages (Folders of Modules)

A **package** is a folder with an `__init__.py` file:

```
my_project/
├── main.py
├── utils/                ← This is a package
│   ├── __init__.py       ← Makes 'utils' a package (can be empty)
│   ├── math_utils.py     ← Module inside the package
│   └── string_utils.py   ← Another module
└── models/               ← Another package
    ├── __init__.py
    └── user.py
```

### Importing from Packages

```python
# Method 1: Full import path
from utils.math_utils import add
result = add(3, 5)

# Method 2: Import the module
from utils import math_utils
result = math_utils.add(3, 5)

# Method 3: Import the package (uses __init__.py)
import utils
```

---

## 🏗️ Step 4: The `__init__.py` File

`__init__.py` runs when the package is imported. It can be empty or used to expose specific items:

```python
# utils/__init__.py

# Make specific functions available directly from the package
from utils.math_utils import add, multiply
from utils.string_utils import capitalize
```

```python
# main.py — now you can import directly from the package
from utils import add, multiply

result = add(3, 5)  # No need for utils.math_utils.add
```

---

## 🏢 Step 5: Real Project Structure

Here's how the Nora's Supermarket project uses modules:

```
DE_Simple_Supermarket_Data_Pipeline/
├── config/
│   ├── __init__.py            ← Makes config a package
│   └── settings.py            ← Configuration constants
├── generators/
│   ├── __init__.py
│   ├── data_generator.py      ← SalesDataGenerator class
│   └── file_writer.py         ← FileWriter class
├── cleaning/
│   ├── __init__.py
│   └── data_cleaner.py        ← DataCleaner class
├── database/
│   ├── __init__.py
│   └── connection.py          ← engine, SessionLocal, Base
├── models/
│   ├── __init__.py
│   ├── raw_store_data.py      ← RawStoreData model
│   └── sales_summary.py       ← SalesSummary model
├── pipeline/
│   ├── __init__.py
│   └── data_ingestion.py      ← DataIngestionPipeline class
├── analytics/
│   ├── __init__.py
│   └── summarizer.py          ← SalesSummarizer class
├── api/
│   ├── __init__.py
│   ├── main.py                ← FastAPI app
│   ├── dependencies.py        ← get_db()
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── raw_data.py        ← Pydantic schemas
│   │   └── sales_summary.py
│   └── routers/
│       ├── __init__.py
│       ├── raw_data.py        ← API endpoints
│       └── sales_summary.py
├── run_generator.py           ← Entry point: Phase 1
├── run_ingestion.py           ← Entry point: Phase 2
└── run_summarizer.py          ← Entry point: Phase 3
```

### How Imports Work in This Project

```python
# In run_generator.py (root level):
from generators.data_generator import SalesDataGenerator
from generators.file_writer import FileWriter

# In pipeline/data_ingestion.py:
from cleaning.data_cleaner import DataCleaner
from config.settings import DATA_DIR, PROCESSED_DIR
from database.connection import SessionLocal, init_db
from models.raw_store_data import RawStoreData

# In api/routers/raw_data.py:
from api.dependencies import get_db
from api.schemas.raw_data import RawDataCreate, RawDataResponse
from models.raw_store_data import RawStoreData
```

---

## 🔑 Step 6: `if __name__ == "__main__"`

This special pattern checks if a file is being run directly or imported:

```python
# math_utils.py
def add(a, b):
    return a + b

# This code ONLY runs when you execute: python math_utils.py
# It does NOT run when someone does: from math_utils import add
if __name__ == "__main__":
    print("Testing add:", add(3, 5))
    print("Testing add:", add(10, 20))
```

### How it Works

| Scenario                            | `__name__` value   | Code runs? |
|-------------------------------------|--------------------|------------|
| Run: `python math_utils.py`        | `"__main__"`       | ✅ Yes     |
| Import: `from math_utils import add`| `"math_utils"`     | ❌ No      |

---

## 📚 Step 7: Built-in Modules

Python comes with many useful built-in modules:

```python
import os       # Operating system operations (files, paths, directories)
import json     # Reading and writing JSON data
import random   # Random numbers and choices
import time     # Time-related functions (sleep, timestamps)
import datetime # Date and time manipulation
import shutil   # High-level file operations (copy, move, delete)
import math     # Mathematical functions (sqrt, cos, sin, etc.)
import sys      # System-specific parameters and functions
```

---

## 📝 Quick Reference

```python
# ── Basic Import ──
import os                              # Import entire module
from os import path                    # Import specific item
from os import path as p              # Import with alias
import os as operating_system         # Module alias

# ── Package Import ──
from config.settings import DATA_DIR   # module.submodule pattern
from api.routers import raw_data       # Nested package import

# ── Check if Running Directly ──
if __name__ == "__main__":
    main()

# ── Create Package ──
# Just add an empty __init__.py to any folder!
```
