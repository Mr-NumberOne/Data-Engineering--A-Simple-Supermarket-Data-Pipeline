"""
Configuration settings for the Nora's Supermarket Data Pipeline.
Centralizes all constants, database credentials, file paths, and catalog data.
All other modules import their settings from this single file.
"""

# os module provides functions for interacting with the operating system (file paths, etc.)
import os

# ──────────────────────────── Database ────────────────────────────

# PostgreSQL connection credentials
DB_USERNAME = "postgres"       # Database username
DB_PASSWORD = "root"           # Database password
DB_HOST = "localhost"          # Database server host (local machine)
DB_PORT = "5432"               # Default PostgreSQL port
DB_NAME = "store_data_db"      # Name of the database to use

# Construct the full database connection URL using the credentials above
# Format: postgresql://username:password@host:port/database_name
DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ──────────────────────────── File Paths ────────────────────────────

# BASE_DIR = the root directory of the project (one level up from config/)
# __file__ is the path to this settings.py file
# os.path.abspath(__file__) gets the absolute path of this file
# os.path.dirname() called twice goes up two levels: config/ -> project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# DATA_DIR = where generated JSON files are saved
DATA_DIR = os.path.join(BASE_DIR, "data")

# PROCESSED_DIR = where already-ingested JSON files are moved to
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

# ──────────────────────────── Branches ────────────────────────────

# List of supermarket branch names; the generator creates data for each branch
BRANCHES = ["Branch_A", "Branch_B", "Branch_C"]

# ──────────────────────────── Item Catalog ────────────────────────────

# Dictionary mapping each product name to its unit price
# Used by both the data generator (to set prices) and the cleaner (to fix bad prices)
ITEM_CATALOG = {
    "Milk":         1.50,
    "Bread":        2.00,
    "Eggs (12)":    3.25,
    "Rice (1kg)":   4.00,
    "Chicken (1kg)":7.50,
    "Tomatoes":     1.20,
    "Bananas":      0.80,
    "Cheese":       5.00,
    "Butter":       3.50,
    "Orange Juice": 2.75,
    "Pasta":        1.80,
    "Coffee":       6.00,
    "Sugar (1kg)":  2.20,
    "Olive Oil":    8.00,
    "Yogurt":       1.60,
}

# ──────────────────────────── Cashier Names ────────────────────────────

# List of possible cashier names used when generating sales records
CASHIER_NAMES = [
    "Ahmed", "Nora", "Fatima", "Omar",
    "Sara", "Ali", "Layla", "Hassan",
    "Reem", "Khalid",
]

# ──────────────────────────── Payment Methods ────────────────────────────

# The two accepted payment methods in the supermarket
PAYMENT_METHODS = ["Cash", "Credit"]

# ──────────────────────────── Scheduler Intervals (seconds) ────────────────────────────

# How often the data generator creates new files (5 minutes = 300 seconds)
GENERATOR_INTERVAL = 300       # 5 minutes

# How often the summarizer recalculates branch analytics (4 hours = 14400 seconds)
SUMMARIZER_INTERVAL = 14400    # 4 hours

# ──────────────────────────── Data Quality ────────────────────────────

# Probability (0.0 to 1.0) that any individual field in a generated record
# will be replaced with None (null) to simulate dirty/missing data
DIRTY_DATA_PROBABILITY = 0.15  # 15% chance per field
