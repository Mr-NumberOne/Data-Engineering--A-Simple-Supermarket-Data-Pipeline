"""
Run Generator — Entry Point for Phase 1.

Generates dirty sales data for all Nora's Supermarket branches
every 5 minutes using the schedule library, and writes
the data as JSON files into the data/ directory.
"""

import time
from datetime import datetime

import schedule

from generators.data_generator import SalesDataGenerator
from generators.file_writer import FileWriter

generator = SalesDataGenerator()
writer = FileWriter()
cycle = 0


def generate_data():
    """Generate sales data for all branches and write to JSON files."""
    global cycle
    cycle += 1
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[Cycle {cycle}] {now} — Generating data …")

    branch_data = generator.generate_all_branches()
    files = writer.write_all_branches(branch_data)

    total_records = sum(len(records) for records in branch_data.values())
    print(f"  ✔ {total_records} records written to {len(files)} files:")
    for fp in files:
        print(f"    → {fp}")


def main():
    print("=" * 60)
    print("  Nora's Supermarket — Data Generator Started")
    print("  Generating data every 5 minutes")
    print("=" * 60)

    # Run once immediately, then schedule every 5 minutes
    generate_data()
    schedule.every(1).minutes.do(generate_data)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
