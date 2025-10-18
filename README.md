# Book Crawler API 📚

A **production-grade**, scalable web crawling and monitoring system for [books.toscrape.com](https://books.toscrape.com) built with **FastAPI**, **MongoDB**, **Redis**, and **APScheduler**.

---

## 🌟 Features

- ✅ **Async Web Crawler** using `aiohttp` and `selectolax`
- ✅ **MongoDB Storage** with deduplication and change tracking
- ✅ **Scheduled Change Detection** via APScheduler
- ✅ **RESTful API** with OpenAPI documentation
- ✅ **User Authentication** with API key-based access control
- ✅ **Rate Limiting** using Redis-backed `slowapi`
- ✅ **Admin/Main User** system for user management
- ✅ **Comprehensive Test Suite** with `pytest-asyncio`

---

## 📋 Table of Contents

1. [Tech Stack](#-tech-stack)
2. [Project Structure](#-project-structure)
3. [Prerequisites](#-prerequisites)
4. [Installation & Setup](#-installation--setup)
5. [Running the Application](#-running-the-application)
6. [API Documentation](#-api-documentation)
7. [Testing](#-testing)
8. [Deployment](#-deployment)
9. [Troubleshooting](#-troubleshooting)
10. [Support & License](#-support--license)

---

## 🛠 Tech Stack

| Component                 | Technology             | Purpose                         |
|---------------------------|------------------------|---------------------------------|
| **Web Framework**         | FastAPI                | High-performance async REST API |
| **Database**              | MongoDB (Motor)        | NoSQL storage with async driver |
| **Cache & Rate Limiting** | Redis                  | Token bucket rate limiting      |
| **HTML Parsing**          | Selectolax             | Fast, memory-efficient parsing  |
| **HTTP Client**           | aiohttp                | Async web crawling              |
| **Scheduler**             | APScheduler            | Daily change detection jobs     |
| **Validation**            | Pydantic               | Data schema validation          |
| **Testing**               | pytest, pytest-asyncio | Async unit/integration tests    |

---

## 📁 Project Structure

```
book_crawler_api/
├── app/
│   ├── api/                    # FastAPI routes
│   │   ├── __init__.py
│   │   ├── book_router.py      # GET /books, /books/{id}
│   │   ├── change_router.py    # GET /changes, /changes/{id}
│   │   └── user_router.py      # POST /users (admin only)
│   ├── crawler/
│   │   ├── __init__.py
│   │   ├── crawler.py          # BookCrawler class
│   │   └── parser.py           # HTML parsing logic
│   ├── db/
│   │   ├── __init__.py
│   │   ├── repository
│   │   │   ├── __init__.py
│   │   │   ├── book_repository.py
│   │   │   ├── cache.py
│   │   │   ├── change_book_repo.py
│   │   │   └── user_repository.py
│   │   └── database.py          # MongoDB connection
│   ├── scheduler/
│   │   ├── __init__.py
│   │   ├── scheduler.py        # APScheduler setup
│   │   └── detector.py         # Change detection logic
│   ├── schemas/                # Pydantic models
│   │   ├── __init__.py 
│   │   ├── book_schemas.py
│   │   └── user_schemas.py 
│   ├── services/           
│   │   ├── __init__.py 
│   │   ├── book_service.py
│   │   ├── change_book_service.py
│   │   └── user_service.py 
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── security.py         
│   │   ├── enums.py
│   │   ├── logger.py                
│   │   └── pagination.py  
│   ├── tests/                
│   │   ├── __init__.py 
│   │   ├── test_book_api.py
│   │   ├── test_change_book_api.py
│   │   ├── test_scheduler.py
│   │   └── test_crawler.py 
│   ├── __init__.py
│   └── main.py                 # FastAPI app entry point
├── .env                        # Environment variables (DO NOT COMMIT)
├── .env.example                # Template for .env
├── docker-compose.yml          # MongoDB + Redis services
├── Dockerfile                  # App containerization
├── requirements.txt            # Python dependencies
└── README.md

````

---

## ✅ Prerequisites

- **Python**: 3.10+ (tested on 3.13.5)
- **Docker & Docker Compose**: For MongoDB and Redis
- **Git**: For cloning the repository

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```
git clone https://github.com/yourusername/book_crawler_api.git
cd book_crawler_api
````

### 2. Create Virtual Environment

```
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```
cp .env.example .env
```

Edit `.env` with your settings:

```
MONGO_URL=mongodb://localhost:27017
DB_NAME=bookstore
BASE_URL=https://books.toscrape.com
ADMIN_API_KEY=supersecretkey123
REDIS_URL=redis://localhost:6379
HOST=http://localhost:8000
```

Edit `.env` with your settings for containerization:
```
MONGO_URL=mongodb://mongo:27017
DB_NAME=bookstore
BASE_URL=https://books.toscrape.com
ADMIN_API_KEY=supersecretkey123
REDIS_URL=redis://redis:6379
HOST=http://localhost:8000
```

### 5. Start Infrastructure Services

```bash
docker-compose up -d
```

Verify services:

```bash
docker-compose ps
```

---

## 🎯 Running the Application

**Always run commands from the project root** (`book_crawler_api/`).

### 1. Run the Crawler (Initial Setup)

```bash
python -m app.crawler.crawler
```

This will:

* Crawl all books from `books.toscrape.com`
* Store data in MongoDB (`books` collection)
* Save raw HTML snapshots

Expected output:

```
✓ Crawled 1000 books in 45.3s
✓ Stored in MongoDB: book_crawler_db.books
```

### 2. Start the FastAPI Server

```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or via Python module:

```
python -m app.main
```

API docs:

* **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 3. Run the Scheduler (Change Detection)

```
python -m app.scheduler.scheduler
```

This runs daily at midnight to:

* Detect new books
* Track price/availability changes
* Log changes to `book_changes` collection

---

## 🔑 API Documentation

### Authentication

All endpoints require an **API key**:

```
-H "x-api-key: YOUR_API_KEY"
```

#### Admin: Create Users

The first admin user is auto-created from `.env`.

**Create a new user**:

```
POST /api/users
Content-Type: application/json
x-api-key: <ADMIN_API_KEY>

{
  "username": "developer"
}
```

Response:

```json
{
  "message": "User & API key created successfully",
  "user": {
    "username": "developer",
    "api_key": "a3f8c2e1d5b9f7a2c4e6d8f0b2a4c6e8",
    "is_active": true,
    "role": "user",
    "created_at": "2025-01-15T10:30:00Z"
  }
}
```

---

### Book Endpoints

#### 1. Get All Books

```
GET /api/books
```

**Query Parameters:**

| Parameter   | Type   | Description            | Example                      |
|-------------|--------|------------------------|------------------------------|
| `category`  | string | Filter by category     | `Travel`                     |
| `min_price` | float  | Minimum price          | `20.0`                       |
| `max_price` | float  | Maximum price          | `50.0`                       |
| `rating`    | int    | Filter by rating (1-5) | `4`                          |
| `sort_by`   | string | Sort field             | `price`, `rating`, `reviews` |
| `page`      | int    | Page number            | `1`                          |
| `limit`     | int    | Items per page         | `20`                         |

**Example Request:**

```
curl -X GET "http://localhost:8000/api/books?category=Travel&min_price=20&max_price=50&rating=4&sort_by=price&page=1&limit=10" \
  -H "x-api-key: YOUR_API_KEY"
```

**Response:**

```json
{
  "total": 47,
  "page": 1,
  "limit": 10,
  "results": [
    {
      "_id": "68ef592250ca2000ff19b001",
      "name": "A Light in the Attic",
      "description": "It's hard to imagine a world without...",
      "category": "Poetry",
      "price": {
        "including_tax": 51.77,
        "excluding_tax": 51.77
      },
      "availability": "In stock (22 available)",
      "num_reviews": 0,
      "image_url": "https://books.toscrape.com/media/cache/...",
      "rating": 3,
      "source_url": "https://books.toscrape.com/catalogue/...",
      "crawl_timestamp": "2025-01-15T08:00:00Z"
    }
  ]
}
```

#### 2. Get Single Book by ID

```
GET /api/books/{book_id}
```

---

### Change Tracking Endpoints

#### 1. Get All Changes

```
GET /api/changes
```

**Query Parameters:**

* `page` (int)
* `limit` (int)
* `change_type` (string): `price_change`, `new_book`, `availability_change`

#### 2. Get Change by ID

```
GET /api/changes/{change_id}
```

---

### Rate Limiting

* **Default**: 100 requests per hour per API key
* **Exceeding Limit Response**:

```json
{
  "detail": "Too Many Requests"
}
```

Status Code: `429 TOO MANY REQUESTS`

---

## 🧪 Testing

Run all tests:

```bash
pytest
```

Run specific test files:

```bash
pytest app/tests/test_crawler.py -v
pytest app/tests/test_book_api.py -v
pytest app/tests/test_change_book_api.py -v
pytest app/tests/test_schedular.py -v
```

Test coverage:

```bash
pytest --cov=app --cov-report=html
```

Open report:

```bash
open htmlcov/index.html
```

---

## 🐳 Deployment

### Docker Compose (Full Stack)

```bash
docker-compose up --build
```

Services started:

* MongoDB
* Redis
* FastAPI (port 8000)
* Scheduler

### Production Environment Variables

```env
MONGO_URI=mongodb://mongo:27017
REDIS_URL=redis://redis:6379
HOST=https://your-domain.com
ADMIN_API_KEY=<strong-random-key>
```

### Manual Deployment (VM/Cloud)

Example `systemd` service:

```ini
[Unit]
Description=Book Crawler API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/book_crawler_api
Environment="PATH=/opt/book_crawler_api/.venv/bin"
ExecStart=/opt/book_crawler_api/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
sudo systemctl enable book-api
sudo systemctl start book-api
```

---

## ❗ Troubleshooting

* **ModuleNotFoundError: No module named 'app'**
  Run from project root.

* **MongoDB Connection Error**
  Ensure MongoDB is running: `docker-compose ps`

* **Redis Connection Error**
  Test Redis: `docker exec -it book_crawler_api_redis_1 redis-cli PING`

* **Scheduler Not Detecting Changes**
  Check if scheduler is running: `ps aux | grep scheduler`
  Trigger manually: `python -m app.scheduler.detector`

---

## 📞 Support & License

* **Email**: [sudipto@filerskeepers.co](mailto:sudipto@filerskeepers.co)
* **GitHub Issues**: [Open Issue](https://github.com/yourusername/book_crawler_api/issues)
* **License**: MIT - see [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

* [Books to Scrape](https://books.toscrape.com)
* [FastAPI](https://fastapi.tiangolo.com/)
* [MongoDB](https://www.mongodb.com/)
* [Selectolax](https://github.com/rushter/selectolax)

---

**Happy Crawling! 🚀**

```

---

If you want, I can also **create a shorter, “quick-start” version** suitable for GitHub so users can set up and run the API in **under 5 minutes**, without going through the full detailed guide. This is great for attracting more users.  

Do you want me to do that?
```
