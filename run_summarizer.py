"""
Run Summarizer — Entry Point for Phase 3.

Reads raw_store_data from the database, computes per-branch summaries,
and rewrites the sales_summary table.  Repeats every 4 hours
using the schedule library.
"""

import time
from datetime import datetime

import schedule

from analytics.summarizer import SalesSummarizer

summarizer = SalesSummarizer()
cycle = 0


def run_summary():
    """Generate the sales summary for all branches."""
    global cycle
    cycle += 1
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[Cycle {cycle}] {now} — Generating summary …")
    summarizer.generate_summary()


def main():
    print("=" * 60)
    print("  Nora's Supermarket — Sales Summarizer")
    print("  Regenerating summary every 4 hours")
    print("=" * 60)

    # Run once immediately, then schedule every 4 hours
    run_summary()
    schedule.every(4).hours.do(run_summary)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
