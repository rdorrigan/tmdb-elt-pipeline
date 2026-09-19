import sys
import datetime
from src.extract import run_extraction_batch

if __name__ == "__main__":
    # Default to yesterday's ID export if no date is passed
    target_date = datetime.date.today() - datetime.timedelta(days=1)
    
    if len(sys.argv) > 1:
        try:
            target_date = datetime.datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")
            sys.exit(1)

    print(f"Starting extraction execution for target date: {target_date}")
    run_extraction_batch(target_date=target_date, limit=500)
    print("Execution complete.")