"""
Run Ingestion — Entry Point for Phase 2.

Reads generated JSON files from data/, cleans the data,
and stores valid rows into the raw_store_data table in PostgreSQL.
"""

from datetime import datetime

from pipeline.data_ingestion import DataIngestionPipeline


def main():
    print("=" * 60)
    print("  Nora's Supermarket — Data Ingestion Pipeline")
    print("=" * 60)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{now}] Starting ingestion …")

    pipeline = DataIngestionPipeline()
    pipeline.run()

    print("\nIngestion complete.")


if __name__ == "__main__":
    main()
