import pytest
from unittest.mock import AsyncMock, patch
from app.scheduler.scheduler import daily_job_async

@pytest.mark.asyncio
async def test_daily_job_async():
    with patch("app.scheduler.scheduler.BookCrawler") as MockCrawler, \
         patch("app.scheduler.scheduler.detect_changes", new_callable=AsyncMock) as mock_detect:

        mock_crawler_instance = MockCrawler.return_value
        mock_crawler_instance.crawl = AsyncMock()
        await daily_job_async()
        mock_crawler_instance.crawl.assert_called_once()
        mock_detect.assert_called_once()
