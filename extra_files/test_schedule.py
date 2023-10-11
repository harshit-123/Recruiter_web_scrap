import schedule
import time

def job():
    print("Running Python file every night at 11 PM")

schedule.every().day.at("10:19").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
