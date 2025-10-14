from apscheduler.schedulers.background import BackgroundScheduler
from app.crawler.crawler import BookCrawler
from app.scheduler.detector import detect_changes
import asyncio

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('cron', hour=0)
def daily_job():
    asyncio.run(BookCrawler().crawl())
    asyncio.run(detect_changes())

if __name__ == "__main__":
    scheduler.start()
    print("Scheduler started. Press Ctrl+C to exit.")
    try:
        # Keep the main thread alive to let the scheduler run
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down scheduler...")
        scheduler.shutdown()
        print("Scheduler stopped.")
