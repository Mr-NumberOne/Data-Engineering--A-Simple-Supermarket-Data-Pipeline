"""
Configuration settings for the Nora's Supermarket Data Pipeline.
Centralizes all constants, database credentials, file paths, and catalog data.
"""

import os

# ──────────────────────────── Database ────────────────────────────
DB_USERNAME = "postgres"
DB_PASSWORD = "root"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "store_data_db"
DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ──────────────────────────── File Paths ────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

# ──────────────────────────── Branches ────────────────────────────
BRANCHES = ["Branch_A", "Branch_B", "Branch_C"]

# ──────────────────────────── Item Catalog ────────────────────────────
# Each item maps to its unit price
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
CASHIER_NAMES = [
    "Ahmed", "Nora", "Fatima", "Omar",
    "Sara", "Ali", "Layla", "Hassan",
    "Reem", "Khalid",
]

# ──────────────────────────── Payment Methods ────────────────────────────
PAYMENT_METHODS = ["Cash", "Credit"]

# ──────────────────────────── Scheduler Intervals (seconds) ────────────────────────────
GENERATOR_INTERVAL = 300       # 5 minutes
SUMMARIZER_INTERVAL = 14400    # 4 hours

# ──────────────────────────── Data Quality ────────────────────────────
# Probability of injecting dirty data (nulls, bad values) per field
DIRTY_DATA_PROBABILITY = 0.15  # 15%
