# OnRoute

A multi-tenant SaaS platform for last-mile delivery tracking, built for small local delivery businesses in India — tiffin services, pharmacies, florists, water can delivery, and similar operations.

Built independently as a learning project to go deep on backend engineering: real-time systems, async Python, multi-tenancy, and production-grade architecture patterns.

---

## What it does

Businesses sign up, add their drivers, and create deliveries. Each delivery generates unique tokenized links for the driver and the customer. The driver opens their link, shares GPS location in real time, and the customer can watch the driver move on a live map. No apps to install on either side.

---

## Tech Stack

- **FastAPI** — async Python web framework
- **async SQLAlchemy + asyncpg** — non-blocking database access
- **PostgreSQL** — primary data store
- **Redis** — live driver location storage (key-value, in-memory)
- **WebSockets** — real-time bidirectional communication
- **Jinja2** — server-side HTML templates for driver and customer pages
- **Leaflet.js** — map rendering (OpenStreetMap tiles, no API key)
- **OSRM** — open source routing engine for road-based route drawing

---

## Architecture

### Multi-tenancy
Every resource (drivers, deliveries) is scoped to a tenant. JWT tokens carry `tenant_id` in the payload. All queries filter by tenant — no data leaks across businesses.

### Real-time location flow
1. Driver opens their tokenized link → browser gets GPS via `watchPosition`
2. Driver's browser sends `{lat, lng}` to the server over a WebSocket connection
3. Server stores the coordinates in Redis under `delivery:{id}:location`
4. Customer's WebSocket connection receives the updated coordinates and re-renders the driver marker on the map
5. Route is drawn using OSRM between the driver's current position and the customer's pinned location

### Auth
- Tenants authenticate with email and password
- OTP verification via Gmail SMTP on registration
- Access tokens (short-lived) + refresh tokens (7 days), both stored in HTTP-only cookies
- Drivers and customers are token-based — no login required, unique UUID per delivery

### Tokenized links
Each delivery generates a `driver_token` and `customer_token` (UUID). These are the only credentials needed to access the driver and customer pages. No accounts, no passwords.

---

## Features

- Real-time driver tracking via WebSockets and Redis
- Live route drawing from driver to customer using OSRM
- Delivery lifecycle management (assigned → en route → delivered → cancelled)
- Customer location pinning on map
- Email notifications to driver and customer on delivery creation (Gmail SMTP)
- JWT auth with access + refresh token rotation
- Soft deletes on all records
- Multi-tenant data isolation

---

## Project Structure

```
onroute/
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── oauth2.py
│   ├── config.py
│   └── routers/
│       ├── tenants.py
│       ├── auth.py
│       ├── drivers.py
│       ├── customers.py
│       ├── deliveries.py
│       └── ws.py
└── frontend/
    ├── driver.html
    ├── customer.html
    ├── dashboard.html
    └── static/
```

---

## Running locally

### Prerequisites
- Python 3.11+
- PostgreSQL
- Redis

### Setup

```bash
git clone https://github.com/yourusername/onroute
cd onroute/backend

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in `backend/`:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/onroute
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
MY_GMAIL_ID=your@gmail.com
GMAIL_APP_PASSWORD=your-app-password
```

Run migrations:

```bash
alembic upgrade head
```

Start the server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Status

Actively in development. Core features are working — WebSocket tracking, multi-tenant auth, delivery management, email notifications, live route drawing.

Planned next: Prometheus + Grafana observability, Redis Streams for event-driven location updates, webhook system for tenant notifications, per-tenant rate limiting, Docker setup, CI/CD with GitHub Actions, and a full test suite.

---

## Why I built this

I'm a first-year CS undergrad trying to actually understand backend systems rather than just follow tutorials. This project forced me to deal with real problems — async SQLAlchemy gotchas, WebSocket connection management, multi-tenant data isolation, token-based auth without user accounts, and real-time data flow through Redis. Still a lot to build.
```