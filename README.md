# Book Crawler API

A scalable, async web crawling and monitoring system for `books.toscrape.com` built with **FastAPI**, **MongoDB**, and **APScheduler**.

### Features
- Async crawler using `aiohttp`  
- MongoDB storage with deduplication  
- Daily scheduler for change detection  
- REST API with authentication & rate limiting  
- OpenAPI docs & Postman collection

---

### 🚀 Setup

```
git clone https://github.com/yourusername/book_crawler_api.git
cd book_crawler_api
cp .env.example .env
docker-compose up -d
```
### Run API
```
uvicorn api.main:app --reload
```
Run scheduler:
```
python -m scheduler.scheduler
```
Run Crawler
```aiignore
python -m crawler.crawler
```

[//]: # (Example API Endpoints)

[//]: # (```)

[//]: # (GET /books?category=Travel&min_price=20)

[//]: # ()
[//]: # (GET /books/{book_id})

[//]: # ()
[//]: # (GET /changes)[README.md](README.md)

[//]: # (```)

Use case:
Selectolax—written in C, memory efficient around < 10% memory efficient than BeautifulSoup, Async support.
Slowapi-- Native, redis backed and async support.
Motor—Official MongoDB async driver, async support.

# (Pytest)
pytest-asyncio → for async tests
aioresponses → to mock aiohttp requests
asynctest → to mock async DB calls


