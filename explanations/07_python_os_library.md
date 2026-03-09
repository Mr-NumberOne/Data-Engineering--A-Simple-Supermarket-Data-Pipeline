# Python `os` Library — Complete Beginner Guide

The `os` module provides functions for interacting with the **operating system** — managing files, directories, paths, and environment variables.

---

## 📦 Import

```python
import os
```

No installation needed — `os` is a **built-in Python module**.

---

## 📂 Step 1: Working with Directories

### Get the Current Working Directory

```python
cwd = os.getcwd()
print(cwd)  # e.g., "E:\DataEngineering\DE_Projects\my_project"
```

### List Files and Folders in a Directory

```python
# List everything in the current directory
entries = os.listdir(".")
print(entries)  # ['data', 'config', 'main.py', 'requirements.txt']

# List a specific directory
entries = os.listdir("data")
print(entries)  # ['file1.json', 'file2.json', 'processed']
```

### Create a Directory

```python
# Create a single directory (parent must exist)
os.mkdir("output")

# Create nested directories (creates all missing parents)
os.makedirs("output/reports/2026", exist_ok=True)
# exist_ok=True → don't error if directory already exists
```

### Delete a Directory

```python
# Remove an empty directory
os.rmdir("output")

# Remove a directory and all its contents → use shutil instead
import shutil
shutil.rmtree("output")  # Deletes the folder and everything inside it
```

### Check if a Directory Exists

```python
if os.path.exists("data"):
    print("data/ directory exists!")

if os.path.isdir("data"):
    print("data/ is a directory!")
```

---

## 📄 Step 2: Working with Files

### Check if a File Exists

```python
if os.path.exists("config/settings.py"):
    print("File exists!")

if os.path.isfile("config/settings.py"):
    print("It's a file (not a directory)!")
```

### Rename a File

```python
os.rename("old_name.txt", "new_name.txt")
```

### Delete a File

```python
os.remove("unwanted_file.txt")
```

### Get File Size

```python
size = os.path.getsize("data/sales.json")
print(f"File size: {size} bytes")
```

---

## 🛤️ Step 3: Path Operations (`os.path`)

### Join Paths (Cross-Platform)

```python
# ✅ CORRECT — works on Windows, Mac, and Linux
filepath = os.path.join("data", "processed", "file.json")
print(filepath)
# Windows: "data\processed\file.json"
# Linux:   "data/processed/file.json"

# ❌ WRONG — only works on one OS
filepath = "data/processed/file.json"   # Fails on Windows sometimes
filepath = "data\\processed\\file.json" # Fails on Linux
```

### Get the File Name from a Path

```python
path = "E:/projects/data/Branch_A_20260309.json"

filename = os.path.basename(path)
print(filename)  # "Branch_A_20260309.json"
```

### Get the Directory from a Path

```python
path = "E:/projects/data/Branch_A_20260309.json"

directory = os.path.dirname(path)
print(directory)  # "E:/projects/data"
```

### Get the File Extension

```python
path = "data/sales.json"

name, ext = os.path.splitext(path)
print(name)  # "data/sales"
print(ext)   # ".json"
```

### Get the Absolute Path

```python
# Convert a relative path to an absolute path
abs_path = os.path.abspath("data/sales.json")
print(abs_path)  # "E:\DataEngineering\projects\data\sales.json"
```

### Get the Current File's Directory

```python
# __file__ is the path of the current Python file
# This is commonly used to find the project root directory

# Get the directory containing this file
this_dir = os.path.dirname(os.path.abspath(__file__))
print(this_dir)  # e.g., "E:\projects\config"

# Go up one level to get the project root
project_root = os.path.dirname(this_dir)
print(project_root)  # e.g., "E:\projects"
```

This pattern is used in our project's `settings.py`:

```python
# settings.py is in config/ → go up one level to get the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#          ↑ Go up one level  ↑ Go up another   ↑ Get absolute path of settings.py

DATA_DIR = os.path.join(BASE_DIR, "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
```

---

## 🌍 Step 4: Environment Variables

```python
# Read an environment variable
db_host = os.environ.get("DB_HOST", "localhost")  # "localhost" is the default
db_name = os.environ.get("DB_NAME")               # Returns None if not set

# Check if an environment variable exists
if "DB_HOST" in os.environ:
    print("DB_HOST is set!")

# Set an environment variable (only for this process)
os.environ["API_KEY"] = "my-secret-key"
```

---

## 🔍 Step 5: Walking Through Directories

### List All Files Recursively

```python
# os.walk() traverses a directory tree
for dirpath, dirnames, filenames in os.walk("data"):
    # dirpath  = current directory being visited
    # dirnames = list of subdirectories in dirpath
    # filenames = list of files in dirpath
    for filename in filenames:
        full_path = os.path.join(dirpath, filename)
        print(full_path)
```

Output:

```
data/Branch_A_20260309.json
data/Branch_B_20260309.json
data/processed/Branch_A_20260308.json
data/processed/Branch_B_20260308.json
```

### Find All JSON Files

```python
json_files = []
for dirpath, dirnames, filenames in os.walk("data"):
    for f in filenames:
        if f.endswith(".json"):
            json_files.append(os.path.join(dirpath, f))

print(json_files)
```

### Simple Version (Non-Recursive)

```python
# List only .json files in a specific directory (not in subdirectories)
json_files = [
    os.path.join("data", f)
    for f in os.listdir("data")
    if f.endswith(".json") and os.path.isfile(os.path.join("data", f))
]
```

---

## 📝 Quick Reference

| Function                           | Description                            |
|------------------------------------|----------------------------------------|
| `os.getcwd()`                     | Get current working directory          |
| `os.listdir(path)`               | List entries in a directory            |
| `os.mkdir(path)`                  | Create a single directory              |
| `os.makedirs(path, exist_ok=True)`| Create nested directories              |
| `os.remove(path)`                | Delete a file                          |
| `os.rmdir(path)`                 | Delete an empty directory              |
| `os.rename(old, new)`            | Rename a file or directory             |
| `os.path.exists(path)`           | Check if path exists                   |
| `os.path.isfile(path)`           | Check if path is a file                |
| `os.path.isdir(path)`            | Check if path is a directory           |
| `os.path.join(a, b)`            | Join path components                   |
| `os.path.basename(path)`         | Get filename from path                 |
| `os.path.dirname(path)`          | Get directory from path                |
| `os.path.abspath(path)`          | Get absolute path                      |
| `os.path.splitext(path)`         | Split name and extension               |
| `os.path.getsize(path)`          | Get file size in bytes                 |
| `os.environ.get(key, default)`    | Read environment variable              |
| `os.walk(path)`                  | Recursively walk directory tree        |
