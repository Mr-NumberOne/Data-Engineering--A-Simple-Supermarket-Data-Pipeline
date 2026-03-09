"""
Run Summarizer — Entry Point for Phase 3.

Reads raw_store_data from the database, computes per-branch summaries,
and rewrites the sales_summary table.  Repeats every 4 hours
using the schedule library.

Usage:
    python run_summarizer.py
    (Press Ctrl+C to stop)
"""

# time: used for time.sleep() in the main loop
import time

# datetime: used to print timestamps in status messages
from datetime import datetime

# schedule: lightweight job scheduling library
import schedule

# Import our summarizer class (aggregates raw data into summaries)
from analytics.summarizer import SalesSummarizer

# Create a single instance of the summarizer (reused across all cycles)
summarizer = SalesSummarizer()

# Counter to track how many summarization cycles have run
cycle = 0


def run_summary():
    """
    Generate the sales summary for all branches.
    This function is called by the scheduler every 4 hours.
    """
    # Use 'global' to modify the module-level cycle counter
    global cycle
    cycle += 1  # Increment cycle count

    # Print timestamp and cycle number for logging
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[Cycle {cycle}] {now} — Generating summary …")

    # Run the summarizer: reads raw_store_data → computes metrics → rewrites sales_summary
    summarizer.generate_summary()


def main():
    """Main function — sets up the schedule and runs the summarizer loop."""

    # Print a startup banner
    print("=" * 60)
    print("  Nora's Supermarket — Sales Summarizer")
    print("  Regenerating summary every 4 hours")
    print("=" * 60)

    # Run immediately on startup (don't wait 4 hours for the first summary)
    run_summary()

    # Schedule the summarizer to run every 4 hours after the initial run
    schedule.every(4).hours.do(run_summary)

    # Main loop: check for pending scheduled tasks every second
    while True:
        schedule.run_pending()  # Run any tasks that are due
        time.sleep(1)          # Wait 1 second before checking again


# Only run main() when this file is executed directly
if __name__ == "__main__":
    main()
