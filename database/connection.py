"""
Database connection module.

Provides the SQLAlchemy engine, session factory, and declarative Base
for the Nora's Supermarket pipeline.
Auto-creates the database if it does not exist.
"""

# psycopg2: PostgreSQL adapter for Python — lets us run raw SQL commands
import psycopg2

# ISOLATION_LEVEL_AUTOCOMMIT: needed because CREATE DATABASE cannot run inside a transaction
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# create_engine: creates a connection pool to the database
from sqlalchemy import create_engine

# declarative_base: base class for our ORM models (tables)
# sessionmaker: factory that creates new database sessions
from sqlalchemy.orm import declarative_base, sessionmaker

# Import database configuration from our settings
from config.settings import DATABASE_URL, DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USERNAME


def _ensure_database_exists():
    """
    Connect to the default 'postgres' database and create the target
    database (store_data_db) if it doesn't already exist.

    We use psycopg2 directly (not SQLAlchemy) because CREATE DATABASE
    cannot run inside a transaction — it needs AUTOCOMMIT mode.
    """
    try:
        # Connect to the default 'postgres' database (it always exists)
        conn = psycopg2.connect(
            host=DB_HOST,         # "localhost"
            port=DB_PORT,         # "5432"
            user=DB_USERNAME,     # "postgres"
            password=DB_PASSWORD, # "root"
            dbname="postgres",    # Connect to the default DB first
        )

        # Set isolation level to AUTOCOMMIT so CREATE DATABASE works
        # (PostgreSQL doesn't allow CREATE DATABASE inside a transaction block)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        # Create a cursor to execute SQL commands
        cursor = conn.cursor()

        # Check if our target database already exists in pg_database system catalog
        # %s is a parameterized query to prevent SQL injection
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,)
        )

        # fetchone() returns None if no matching row was found
        if not cursor.fetchone():
            # Database doesn't exist yet — create it
            cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
            print(f"✔ Database '{DB_NAME}' created.")
        else:
            # Database already exists — nothing to do
            print(f"✔ Database '{DB_NAME}' already exists.")

        # Clean up: close cursor and connection
        cursor.close()
        conn.close()

    except psycopg2.OperationalError as e:
        # If we can't connect to PostgreSQL at all, print the error and re-raise
        print(f"⚠ Could not check/create database: {e}")
        raise


# ── Ensure DB exists before creating engine ──────────────────────────
# This runs at module import time — before any other code uses the database
_ensure_database_exists()

# ── Engine ───────────────────────────────────────────────────────────
# create_engine creates a connection pool to our PostgreSQL database
# echo=False: don't print every SQL query to the console
# pool_pre_ping=True: test connections before using them (handles dropped connections)
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

# ── Session factory ──────────────────────────────────────────────────
# SessionLocal is a factory function — calling SessionLocal() gives us a new DB session
# autocommit=False: we control when transactions are committed
# autoflush=False: we control when changes are flushed to the DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ── Declarative Base ─────────────────────────────────────────────────
# Base is the parent class for all our ORM models (RawStoreData, SalesSummary)
# Each model that inherits from Base will become a database table
Base = declarative_base()


def init_db():
    """
    Create all tables that inherit from Base in the database.
    Safe to call multiple times — existing tables are not recreated.
    """
    # Import the model modules so their classes register with Base.metadata
    # Without these imports, SQLAlchemy wouldn't know about the tables to create
    import models.raw_store_data  # noqa: F401  (tells linters: this import is intentional)
    import models.sales_summary   # noqa: F401

    # create_all() inspects Base.metadata and creates any tables that don't exist yet
    Base.metadata.create_all(bind=engine)
    print("✔ Database tables created / verified.")
