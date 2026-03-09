# 🏪 Nora's Supermarket — Data Pipeline Demo Project

A complete **data pipeline simulation** that generates, cleans, stores, summarizes, and serves daily sales data for a multi-branch supermarket chain.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Pipeline Phases](#pipeline-phases)
- [API Endpoints](#api-endpoints)
- [Getting Started](#getting-started)

---

## Overview

This project simulates a real-world data pipeline for **Nora's Supermarkets** — a chain with multiple branches. The pipeline covers the full lifecycle of sales data:

1. **Generate** → Dirty sales data is produced every 5 minutes (with nulls, duplicates, invalid values)
2. **Clean & Store** → Raw data is cleaned using Pandas and stored in PostgreSQL
3. **Summarize** → Per-branch analytics are computed every 4 hours
4. **Serve** → A FastAPI REST API exposes both raw data (full CRUD) and summaries (read-only)

---

## Architecture

```
┌─────────────────┐     JSON files     ┌─────────────────────┐
│  Data Generator  │ ──────────────────▶│   data/ directory    │
│  (Faker+Random)  │   every 5 min      └──────────┬──────────┘
└─────────────────┘                                │
                                                   ▼
                                        ┌─────────────────────┐
                                        │  Ingestion Pipeline  │
                                        │  (Pandas cleaning)   │
                                        └──────────┬──────────┘
                                                   │
                                                   ▼
                                        ┌─────────────────────┐
                                        │     PostgreSQL       │
                                        │  ┌───────────────┐   │
                                        │  │raw_store_data │   │
                                        │  └───────┬───────┘   │
                                        │          │           │
                                        │          ▼           │
                                        │  ┌───────────────┐   │
                                        │  │sales_summary  │   │
                                        │  └───────────────┘   │
                                        └──────────┬──────────┘
                                                   │
                                                   ▼
                                        ┌─────────────────────┐
                                        │   FastAPI REST API   │
                                        │  /raw-data (CRUD)    │
                                        │  /sales-summary (R)  │
                                        └─────────────────────┘
```

---

## Tech Stack

| Library | Purpose |
|---------|---------|
| **NumPy** | Numerical computations in summarizer |
| **Pandas** | Data cleaning, transformation, aggregation |
| **Faker** | Generating realistic fake names & timestamps |
| **JSON** | Reading/writing data files |
| **Random** | Randomized data generation & dirty-data injection |
| **SQLAlchemy** | ORM & database connection |
| **psycopg2** | PostgreSQL driver |
| **FastAPI** | REST API framework |
| **Pydantic** | Request/response schema validation |
| **Uvicorn** | ASGI server for FastAPI |

---

## Project Structure

```
Data_Pipeline_Demo_Project/
│
├── config/                  # Configuration & constants
│   └── settings.py
│
├── generators/              # Phase 1: Data generation
│   ├── data_generator.py    #   Faker + Random based generator
│   └── file_writer.py       #   Writes to JSON files
│
├── cleaning/                # Phase 2: Data cleaning
│   └── data_cleaner.py      #   Pandas-based cleaning
│
├── database/                # Database connection
│   └── connection.py        #   SQLAlchemy engine & session
│
├── models/                  # SQLAlchemy ORM models
│   ├── raw_store_data.py    #   raw_store_data table
│   └── sales_summary.py     #   sales_summary table
│
├── pipeline/                # Phase 2: Ingestion pipeline
│   └── data_ingestion.py    #   Read → Clean → Store
│
├── analytics/               # Phase 3: Summarization
│   └── summarizer.py        #   Aggregate → Rewrite summary
│
├── api/                     # Phase 4: REST API
│   ├── main.py              #   FastAPI application
│   ├── dependencies.py      #   DB session injection
│   ├── schemas/             #   Pydantic models
│   │   ├── raw_data.py
│   │   └── sales_summary.py
│   └── routers/             #   API route handlers
│       ├── raw_data.py      #     CRUD + filters
│       └── sales_summary.py #     Read-only + filters
│
├── data/                    # Generated JSON files (auto-created)
│   └── processed/           # Ingested files moved here
│
├── run_generator.py         # Entry point: Phase 1
├── run_ingestion.py         # Entry point: Phase 2
├── run_summarizer.py        # Entry point: Phase 3
├── requirements.txt
├── setup.md                 # Installation guide
└── Readme.md                # This file
```

---

## Pipeline Phases

### Phase 1 — Data Generator 🏭

- Generates sales records for 3 branches: `Branch_A`, `Branch_B`, `Branch_C`
- Each record: `branch`, `item`, `quantity`, `unit_price`, `total_price`, `sold_at`, `payment_method`, `cashier_name`
- **Intentionally dirty data**: ~15% null fields, negative quantities, invalid prices, duplicate rows
- Outputs JSON files to `data/` every **5 minutes**
- Run: `python run_generator.py`

### Phase 2 — Data Cleaning & Storage 🧹

- Reads unprocessed JSON files from `data/`
- Cleans with Pandas: drops nulls, fixes negatives, recalculates totals, validates payment methods, parses timestamps, removes duplicates
- Stores clean records in PostgreSQL table `raw_store_data`
- Moves processed files to `data/processed/`
- Run: `python run_ingestion.py`

### Phase 3 — Data Summarization 📊

- Reads all `raw_store_data` records
- Computes **per-branch** metrics: total sales, transaction count, unique cashiers, items sold, popular items (top 5), rush hours (top 5)
- **Rewrites** `sales_summary` table on each run (handles new data)
- Runs every **4 hours**
- Run: `python run_summarizer.py`

### Phase 4 — Data Delivery 🚀

- FastAPI REST API with Swagger docs at `/docs`
- Run: `uvicorn api.main:app --reload`

---

## API Endpoints

### Raw Store Data (`/raw-data`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/raw-data/` | List records with filters (branch, cashier, item, date range) |
| `GET` | `/raw-data/{id}` | Get a single record |
| `POST` | `/raw-data/` | Create a new record |
| `PUT` | `/raw-data/{id}` | Update a record |
| `DELETE` | `/raw-data/{id}` | Delete a record |

**Query Parameters**: `branch`, `cashier`, `item`, `start_date`, `end_date`, `skip`, `limit`

### Sales Summary (`/sales-summary`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/sales-summary/` | Get all summaries with filters |
| `GET` | `/sales-summary/{branch}` | Get summary for a specific branch |

**Query Parameters**: `branch`, `min_sales`, `fields` (comma-separated column names)

---

## Getting Started

See the full **[setup.md](setup.md)** for detailed installation instructions.

**Quick start:**

```bash
pip install -r requirements.txt
# Create PostgreSQL database: CREATE DATABASE store_data_db;
python run_generator.py        # Terminal 1: generate data
python run_ingestion.py        # Terminal 2: clean & store
python run_summarizer.py       # Terminal 3: summarize
uvicorn api.main:app --reload  # Terminal 4: start API
```

Open Swagger docs at: **<http://localhost:8000/docs>**
