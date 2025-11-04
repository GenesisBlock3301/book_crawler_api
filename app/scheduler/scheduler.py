from apscheduler.schedulers.background import BackgroundScheduler
from app.crawler.crawler import BookCrawler
from app.scheduler.detector import detect_changes
import asyncio

scheduler = BackgroundScheduler()


async def daily_job_async():
    await BookCrawler().crawl()
    await detect_changes()


@scheduler.scheduled_job('cron', hour=0)
def daily_job():
    loop = asyncio.get_event_loop()
    loop.create_task(daily_job_async())


if __name__ == "__main__":
    scheduler.start()
    print("Scheduler started. Press Ctrl+C to exit.")
    try:
        import time

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down scheduler...")
        scheduler.shutdown()
        print("Scheduler stopped.")
