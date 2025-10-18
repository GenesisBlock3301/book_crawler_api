
```markdown
# Book Crawler API 📚

A production-grade, scalable web crawling and monitoring system for **books.toscrape.com** built with **FastAPI**, **MongoDB**, **Redis**, and **APScheduler**.

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

1. [Tech Stack](#tech-stack)
2. [Project Structure](#project-structure)
3. [Prerequisites](#prerequisites)
4. [Installation & Setup](#installation--setup)
5. [Running the Application](#running-the-application)
6. [API Documentation](#api-documentation)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)

---

## 🛠 Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Web Framework** | FastAPI | High-performance async REST API |
| **Database** | MongoDB (Motor) | NoSQL storage with async driver |
| **Cache & Rate Limiting** | Redis | Token bucket rate limiting |
| **HTML Parsing** | Selectolax | Fast, memory-efficient parsing |
| **HTTP Client** | aiohttp | Async web crawling |
| **Scheduler** | APScheduler | Daily change detection jobs |
| **Validation** | Pydantic | Data schema validation |
| **Testing** | pytest, pytest-asyncio | Async unit/integration tests |

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
│   │   └── crawler.py          # BookCrawler class
│   ├── db/
│   │   ├── __init__.py
│   │   └── mongodb.py          # MongoDB connection
│   ├── scheduler/
│   │   ├── __init__.py
│   │   ├── scheduler.py        # APScheduler setup
│   │   └── detector.py         # Change detection logic
│   ├── schemas/                # Pydantic models
│   ├── services/               # Business logic
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── security.py         # API key generation/verification
│   │   └── rate_limiter.py     # Redis-backed rate limiting
│   ├── tests/                  # Pytest test suite
│   ├── __init__.py
│   └── main.py                 # FastAPI app entry point
├── .env                        # Environment variables (DO NOT COMMIT)
├── .env.example                # Template for .env
├── docker-compose.yml          # MongoDB + Redis services
├── Dockerfile                  # App containerization
├── requirements.txt            # Python dependencies
└── README.md
```
---

## ✅ Prerequisites

- **Python**: 3.10+ (Tested on 3.13.5)
- **Docker & Docker Compose**: For MongoDB and Redis
- **Git**: For cloning the repository

---

## 🚀 Installation & Setup

### Step 1: Clone the Repository
```
bash
git clone https://github.com/yourusername/book_crawler_api.git
cd book_crawler_api
```
### Step 2: Create Virtual Environment
```
bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```
### Step 3: Install Dependencies
```
bash
pip install --upgrade pip
pip install -r requirements.txt
```
### Step 4: Configure Environment Variables
```
bash
cp .env.example .env
```
Edit `.env` with your settings:
```
env
# MongoDB
MONGO_URI=mongodb://localhost:27017
DB_NAME=book_crawler_db

# Redis
REDIS_URL=redis://localhost:6379

# API Settings
HOST=http://localhost:8000
API_RATE_LIMIT=100/hour

# Admin User (Auto-created on first run)
ADMIN_USERNAME=admin
ADMIN_API_KEY=your-secure-admin-key-here

# Crawler Settings
MAX_RETRIES=3
TIMEOUT=30
```
### Step 5: Start Infrastructure Services
```
bash
docker-compose up -d
```
This starts:
- **MongoDB** on `localhost:27017`
- **Redis** on `localhost:6379`

Verify services are running:
```
bash
docker-compose ps
```
---

## 🎯 Running the Application

**IMPORTANT**: Always run commands from the **project root** (`book_crawler_api/`), not from inside `app/`.

### 1. Run the Crawler (First Time Setup)
```
bash
python -m app.crawler.crawler
```
This will:
- Crawl all books from `books.toscrape.com`
- Store data in MongoDB (`books` collection)
- Save raw HTML snapshots

Expected output:
```

✓ Crawled 1000 books in 45.3s
✓ Stored in MongoDB: book_crawler_db.books
```
### 2. Start the FastAPI Server
```
bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Or use the development script:
```
bash
python -m app.main
```
API will be available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Run the Scheduler (Change Detection)

In a separate terminal:
```
bash
python -m app.scheduler.scheduler
```
This runs daily at midnight (00:00) to:
- Detect new books
- Track price/availability changes
- Log changes to `book_changes` collection

---

## 🔑 API Documentation

### Authentication

All API endpoints require an **API key** in the header:
```
bash
-H "x-api-key: YOUR_API_KEY"
```
#### Creating Users (Admin Only)

The first user (admin) is auto-created using `ADMIN_USERNAME` and `ADMIN_API_KEY` from `.env`.

**Create a new user** (admin only):
```
bash
POST /api/users
Content-Type: application/json
x-api-key: <ADMIN_API_KEY>

{
  "username": "developer"
}
```
Response:
```
json
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

#### 1. Get All Books (with Filters)
```
bash
GET /api/books
```
**Query Parameters:**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `category` | string | Filter by category | `Travel` |
| `min_price` | float | Minimum price | `20.0` |
| `max_price` | float | Maximum price | `50.0` |
| `rating` | int | Filter by rating (1-5) | `4` |
| `sort_by` | string | Sort field | `price`, `rating`, `reviews` |
| `page` | int | Page number (default: 1) | `1` |
| `limit` | int | Items per page (default: 20) | `20` |

**Example Request:**
```
bash
curl -X GET "http://localhost:8000/api/books?category=Travel&min_price=20&max_price=50&rating=4&sort_by=price&page=1&limit=10" \
  -H "x-api-key: YOUR_API_KEY"
```
**Response:**
```
json
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
bash
GET /api/books/{book_id}
```
**Example:**
```
bash
curl -X GET "http://localhost:8000/api/books/68ef592250ca2000ff19b001" \
  -H "x-api-key: YOUR_API_KEY"
```
---

### Change Tracking Endpoints

#### 1. Get All Changes
```
bash
GET /api/changes
```
**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20)
- `change_type` (string): Filter by type (`price_change`, `new_book`, `availability_change`)

**Example:**
```
bash
curl -X GET "http://localhost:8000/api/changes?change_type=price_change&limit=5" \
  -H "x-api-key: YOUR_API_KEY"
```
**Response:**
```
json
{
  "total": 23,
  "page": 1,
  "limit": 5,
  "results": [
    {
      "_id": "68ef6a0050ca2000ff19c123",
      "book_id": "68ef592250ca2000ff19b001",
      "book_name": "A Light in the Attic",
      "change_type": "price_change",
      "old_value": 51.77,
      "new_value": 48.99,
      "detected_at": "2025-01-16T00:05:00Z"
    }
  ]
}
```
#### 2. Get Change by ID
```
bash
GET /api/changes/{change_id}
```
---

### Rate Limiting

- **Default**: 100 requests per hour per API key
- **Response when exceeded**:
```
json
{
  "detail": "Too Many Requests"
}
```
Status Code: `429 TOO MANY REQUESTS`

---

## 🧪 Testing

### Run All Tests
```
bash
pytest
```
### Run Specific Test Files
```
bash
pytest app/tests/test_crawler.py -v
pytest app/tests/test_book_api.py -v
pytest app/tests/test_change_book_api.py -v
pytest app/tests/test_schedular.py -v
```
### Test Coverage
```
bash
pytest --cov=app --cov-report=html
```
View coverage report: `open htmlcov/index.html`

---

## 🐳 Deployment

### Using Docker Compose (Full Stack)

Build and run all services:
```
bash
docker-compose up --build
```
This starts:
- MongoDB
- Redis
- FastAPI app (port 8000)
- Scheduler (background)

### Environment Variables for Production

Update `.env`:
```
env
MONGO_URI=mongodb://mongo:27017  # Use service name in Docker
REDIS_URL=redis://redis:6379
HOST=https://your-domain.com
ADMIN_API_KEY=<strong-random-key>
```
### Manual Deployment (VM/Cloud)

1. **Install dependencies** on server
2. **Use process manager** (systemd, supervisor, or PM2)

Example systemd service (`/etc/systemd/system/book-api.service`):
```
ini
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
Start service:
```
bash
sudo systemctl enable book-api
sudo systemctl start book-api
```
---

## ❗ Troubleshooting

### 1. `ModuleNotFoundError: No module named 'app'`

**Cause**: Running scripts from wrong directory.

**Solution**: Always run from project root:
```
bash
cd /path/to/book_crawler_api
python -m app.scheduler.scheduler
```
### 2. MongoDB Connection Error

**Check if MongoDB is running**:
```
bash
docker-compose ps
```
**Verify connection**:
```
bash
docker exec -it book_crawler_api_mongo_1 mongosh
```
### 3. Redis Connection Error

**Test Redis**:
```
bash
docker exec -it book_crawler_api_redis_1 redis-cli PING
# Should return: PONG
```
### 4. Scheduler Not Detecting Changes

**Verify scheduler is running**:
```
bash
ps aux | grep scheduler
```
**Check logs**:
```
bash
tail -f logs/scheduler.log
```
**Manually trigger change detection**:
```
bash
python -m app.scheduler.detector
```
---

## 📞 Support

For questions or issues:
- **Email**: sudipto@filerskeepers.co
- **GitHub Issues**: https://github.com/yourusername/book_crawler_api/issues

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- **Books to Scrape**: https://books.toscrape.com (practice site)
- **FastAPI**: Modern async web framework
- **MongoDB**: Flexible NoSQL database
- **Selectolax**: Lightning-fast HTML parser

---

**Happy Crawling! 🚀**
```


---

## Key Points for Users

1. **Always run from project root**: `python -m app.scheduler.scheduler` (not from `app/` directory)
2. **Admin setup**: First user is auto-created from `.env` - use that API key to create other users
3. **Docker required**: MongoDB and Redis must be running via `docker-compose up -d`
4. **Testing**: Run `pytest` to verify everything works before deployment

This README provides complete step-by-step instructions from installation to deployment, with clear examples for every API endpoint! 🎯