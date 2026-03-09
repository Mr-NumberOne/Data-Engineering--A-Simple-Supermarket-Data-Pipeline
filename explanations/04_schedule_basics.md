# Schedule Library — Complete Beginner Guide

The `schedule` library is a lightweight Python package for running functions at set intervals — like a simple cron job in pure Python.

---

## 📦 Installation

```bash
pip install schedule
```

---

## 🚀 Step 1: Basic Usage

```python
import schedule
import time

def my_task():
    print("Task is running!")

# Schedule the task to run every 5 seconds
schedule.every(5).seconds.do(my_task)

# Main loop — keeps checking for pending tasks
while True:
    schedule.run_pending()  # Run any tasks that are due
    time.sleep(1)           # Wait 1 second before checking again
```

---

## ⏰ Step 2: Scheduling Intervals

```python
import schedule

def job():
    print("Running job...")

# ── Every X units ──
schedule.every(10).seconds.do(job)    # Every 10 seconds
schedule.every(5).minutes.do(job)     # Every 5 minutes
schedule.every(2).hours.do(job)       # Every 2 hours
schedule.every(1).day.do(job)         # Every day
schedule.every(1).week.do(job)        # Every week

# ── At specific times ──
schedule.every().day.at("10:30").do(job)      # Every day at 10:30 AM
schedule.every().day.at("22:00").do(job)      # Every day at 10:00 PM
schedule.every().monday.do(job)               # Every Monday
schedule.every().wednesday.at("13:15").do(job) # Every Wednesday at 1:15 PM

# ── Every unit (shorthand for every 1) ──
schedule.every().minute.do(job)      # Every minute
schedule.every().hour.do(job)        # Every hour
schedule.every().day.do(job)         # Every day
schedule.every().week.do(job)        # Every week
```

---

## 🧩 Step 3: Passing Arguments to Jobs

```python
def greet(name):
    print(f"Hello, {name}!")

# Pass arguments to the scheduled function
schedule.every(3).seconds.do(greet, name="Ahmed")
# This calls greet(name="Ahmed") every 3 seconds

def process_data(branch, verbose=False):
    print(f"Processing {branch} (verbose={verbose})")

schedule.every(5).minutes.do(process_data, branch="Branch_A", verbose=True)
```

---

## 🏷️ Step 4: Tagging Jobs

Tags let you manage groups of jobs:

```python
# Add tags to jobs
schedule.every(5).minutes.do(job).tag("data", "critical")
schedule.every(1).hour.do(job).tag("reporting")
schedule.every(10).seconds.do(job).tag("data", "monitoring")

# Get all jobs with a specific tag
data_jobs = schedule.get_jobs("data")

# Cancel all jobs with a specific tag
schedule.clear("reporting")  # Removes all jobs tagged "reporting"

# Cancel ALL jobs
schedule.clear()
```

---

## 🔄 Step 5: Run Once and Cancel

```python
def one_time_setup():
    print("Setting up... (this runs only once)")
    return schedule.CancelJob  # Returning CancelJob removes this job from the schedule

schedule.every(1).seconds.do(one_time_setup)
# This will run once and then never again
```

---

## ⏳ Step 6: Run Immediately + Schedule

A common pattern is to run the job once immediately, then schedule it for the future:

```python
def generate_report():
    print("Generating report...")

# Run once immediately (not using schedule)
generate_report()

# Then schedule it for every 4 hours
schedule.every(4).hours.do(generate_report)

# Main loop
while True:
    schedule.run_pending()
    time.sleep(1)
```

---

## 🛡️ Step 7: Error Handling

```python
import schedule
import time
import traceback

def safe_job():
    try:
        print("Running job...")
        # Your actual work here
        result = 10 / 0  # This will cause an error
    except Exception:
        traceback.print_exc()
        # Don't re-raise — prevents the scheduler from crashing

schedule.every(5).seconds.do(safe_job)

while True:
    schedule.run_pending()
    time.sleep(1)
```

---

## 📝 Complete Example — Data Pipeline

```python
import schedule
import time
from datetime import datetime

cycle = 0

def generate_data():
    """Generate sales data every 5 minutes."""
    global cycle
    cycle += 1
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[Cycle {cycle}] {now} — Generating data...")
    # ... your data generation logic here ...

def main():
    print("Data Generator Started")
    print("Generating data every 5 minutes")

    # Run immediately
    generate_data()

    # Schedule for every 5 minutes
    schedule.every(5).minutes.do(generate_data)

    # Keep running forever
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
```

---

## 📊 Quick Reference

| Code                                    | Frequency                   |
|-----------------------------------------|-----------------------------|
| `schedule.every(10).seconds.do(job)`    | Every 10 seconds            |
| `schedule.every(5).minutes.do(job)`     | Every 5 minutes             |
| `schedule.every(2).hours.do(job)`       | Every 2 hours               |
| `schedule.every().day.at("09:00").do(job)` | Daily at 9:00 AM        |
| `schedule.every().monday.do(job)`       | Every Monday                |
| `schedule.clear()`                      | Cancel all scheduled jobs   |
| `schedule.get_jobs()`                   | List all scheduled jobs     |
| `return schedule.CancelJob`            | Cancel this job after run   |
