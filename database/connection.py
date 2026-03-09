"""
Database connection module.

Provides the SQLAlchemy engine, session factory, and declarative Base
for the Nora's Supermarket pipeline.
Auto-creates the database if it does not exist.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config.settings import DATABASE_URL, DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USERNAME


def _ensure_database_exists():
    """
    Connect to the default 'postgres' database and create the target
    database if it doesn't already exist.

    CREATE DATABASE cannot run inside a transaction, so we use
    psycopg2 directly with AUTOCOMMIT isolation level.
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USERNAME,
            password=DB_PASSWORD,
            dbname="postgres",
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,)
        )
        if not cursor.fetchone():
            cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
            print(f"✔ Database '{DB_NAME}' created.")
        else:
            print(f"✔ Database '{DB_NAME}' already exists.")

        cursor.close()
        conn.close()
    except psycopg2.OperationalError as e:
        print(f"⚠ Could not check/create database: {e}")
        raise


# ── Ensure DB exists before creating engine ──────────────────────────
_ensure_database_exists()

# ── Engine ───────────────────────────────────────────────────────────
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

# ── Session factory ──────────────────────────────────────────────────
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ── Declarative Base ─────────────────────────────────────────────────
Base = declarative_base()


def init_db():
    """
    Create all tables that inherit from Base.
    Safe to call multiple times — existing tables are not recreated.
    """
    # Import models so they register with Base.metadata
    import models.raw_store_data  # noqa: F401
    import models.sales_summary   # noqa: F401

    Base.metadata.create_all(bind=engine)
    print("✔ Database tables created / verified.")
