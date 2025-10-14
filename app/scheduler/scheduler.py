from apscheduler.schedulers.background import BackgroundScheduler
from app.crawler.crawler import crawl_books
from app.scheduler.detector import detect_changes
import asyncio

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('cron', hour=0)
def daily_job():
    asyncio.run(crawl_books())
    asyncio.run(detect_changes())

if __name__ == "__main__":
    scheduler.start()
    print("Scheduler started. Press Ctrl+C to exit.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        scheduler.shutdown()
