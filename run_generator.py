"""
Run Generator — Entry Point for Phase 1.

Generates dirty sales data for all Nora's Supermarket branches
every 5 minutes using the schedule library, and writes
the data as JSON files into the data/ directory.

Usage:
    python run_generator.py
    (Press Ctrl+C to stop)
"""

# time: used for time.sleep() in the main loop
import time

# datetime: used to print the current time in status messages
from datetime import datetime

# schedule: a lightweight Python job scheduling library
# Lets us define recurring tasks like "run this function every 5 minutes"
import schedule

# Import the data generator class (creates fake sales records)
from generators.data_generator import SalesDataGenerator

# Import the file writer class (saves records to JSON files)
from generators.file_writer import FileWriter

# Create instances of the generator and writer (these persist between cycles)
generator = SalesDataGenerator()  # Generates sales data with dirty values
writer = FileWriter()             # Writes data to JSON files in data/

# Counter to track how many generation cycles have run
cycle = 0


def generate_data():
    """
    Generate sales data for all branches and write to JSON files.
    This function is called by the scheduler every 5 minutes.
    """
    # Use 'global' to modify the module-level cycle counter
    global cycle
    cycle += 1  # Increment cycle count

    # Print timestamp and cycle number for logging
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[Cycle {cycle}] {now} — Generating data …")

    # Generate a batch of sales records for every branch
    # Returns: {"Branch_A": [{...}, ...], "Branch_B": [{...}, ...], ...}
    branch_data = generator.generate_all_branches()

    # Write each branch's data to a separate JSON file
    # Returns: list of file paths that were created
    files = writer.write_all_branches(branch_data)

    # Calculate and print the total number of records generated
    total_records = sum(len(records) for records in branch_data.values())
    print(f"  ✔ {total_records} records written to {len(files)} files:")

    # Print each file path for reference
    for fp in files:
        print(f"    → {fp}")


def main():
    """Main function — sets up the schedule and runs the generator loop."""

    # Print a startup banner
    print("=" * 60)
    print("  Nora's Supermarket — Data Generator Started")
    print("  Generating data every 5 minutes")
    print("=" * 60)

    # Run the generator immediately on startup (don't wait for the first schedule tick)
    generate_data()

    # Schedule the generator to run every 5 minutes after the initial run
    # schedule.every(5).minutes.do(func) registers func to be called every 5 min
    schedule.every(5).minutes.do(generate_data)

    # Main loop: check for pending scheduled tasks every second
    # schedule.run_pending() checks if any tasks are due and runs them
    # time.sleep(1) prevents the loop from consuming 100% CPU
    while True:
        schedule.run_pending()
        time.sleep(1)


# Standard Python pattern: only run main() when this file is executed directly
# (not when imported as a module by another file)
if __name__ == "__main__":
    main()
