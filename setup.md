# Setup Guide — Nora's Supermarket Data Pipeline

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.10 or higher |
| PostgreSQL | 13 or higher |
| pip | latest |

---

## 1. Clone / Navigate to the Project

```bash
cd Data_Pipeline_Demo_Project
```

---

## 2. Create a Virtual Environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Set Up PostgreSQL Database

Open **pgAdmin** or the `psql` CLI and run:

```sql
CREATE DATABASE store_data_db;
```

> The project uses these default credentials (editable in `config/settings.py`):
>
> | Setting  | Value      |
> |----------|------------|
> | Username | `postgres` |
> | Password | `root`     |
> | Host     | `localhost`|
> | Port     | `5432`     |

---

## 5. Running the Pipeline

Each phase is a separate entry point. Open a **separate terminal** for each one.

### Phase 1 — Data Generator

Generates dirty sales JSON files every 5 minutes into the `data/` folder.

```bash
python run_generator.py
```

Press `Ctrl+C` to stop.

### Phase 2 — Data Ingestion (Clean & Store)

Reads JSON files from `data/`, cleans them, and inserts into the `raw_store_data` table.

```bash
python run_ingestion.py
```

Run this whenever new files have been generated, or set up a scheduled task.

### Phase 3 — Sales Summarizer

Aggregates `raw_store_data` into the `sales_summary` table every 4 hours.

```bash
python run_summarizer.py
```

Press `Ctrl+C` to stop.

### Phase 4 — FastAPI Server

Starts the REST API at `http://localhost:8000`.

```bash
uvicorn api.main:app --reload
```

Open **Swagger docs** at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 6. Recommended Run Order

1. Start the **generator** (`run_generator.py`) — wait for the first cycle to produce files.
2. Run the **ingestion** (`run_ingestion.py`) — loads & cleans data into PostgreSQL.
3. Run the **summarizer** (`run_summarizer.py`) — creates branch summaries.
4. Start the **API** (`uvicorn api.main:app --reload`) — query data via REST.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `psycopg2` install fails | Install `psycopg2-binary` instead (already in requirements.txt) |
| Connection refused | Make sure PostgreSQL is running and the `store_data_db` database exists |
| No data in API | Run `run_generator.py` first, then `run_ingestion.py` |
| Port 8000 in use | Use `uvicorn api.main:app --reload --port 8001` |
