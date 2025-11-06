# FastAPI Posts Service

A production-ready FastAPI service for creating, reading, updating, deleting, and voting on posts. The project includes:

- **FastAPI** application with modular routers (`posts`, `users`, `auth`, `vote`)
- **SQLAlchemy** ORM and **Alembic** for database migrations
- **PostgreSQL** database
- **Docker** and **Docker Compose** for local/dev/prod
- **CORS**, JWT auth, and basic test suite with `pytest`
- Optional reverse proxy and process manager for production (Nginx + Gunicorn)

---

## Tech stack

- **API**: FastAPI, Starlette
- **Auth**: `python-jose`, `passlib`
- **DB/ORM**: PostgreSQL, SQLAlchemy 2.x
- **Migrations**: Alembic
- **Containerization**: Docker, Docker Compose
- **Prod runtime**: Gunicorn (optional), Nginx reverse proxy
- **Tests**: pytest, FastAPI TestClient

---

## Project structure

```text
app/
  main.py                # FastAPI app, router includes, CORS
  database.py            # SQLAlchemy engine, SessionLocal, Base
  config.py              # Pydantic Settings (env-based)
  models.py              # SQLAlchemy models
  schema.py              # Pydantic schemas
  oauth2.py              # JWT helpers
  routers/
    auth.py, post.py, user.py, vote.py
alembic/
  env.py                 # Alembic config (reads env via Settings)
  versions/              # Migration revision scripts
docker-compose-dev.yml   # Dev compose (reload, bind-mount)
docker-compose-prod.yml  # Prod compose (build, port 80)
Dockerfile               # App image
tests/                   # pytest suite and fixtures
```

---

## Configuration (.env)

The app reads environment variables via `app/config.py` (`pydantic-settings`). Create a `.env` in the project root for local runs:

```env
DATABASE_HOSTNAME=localhost
DATABASE_PORT=5432
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=admin123
DATABASE_NAME=fastapi
SECRET_KEY=replace-with-strong-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Notes:
- Tests use `<DATABASE_NAME>_test` automatically (see `tests/conftest.py`).
- In dev compose, service env overrides are declared in `docker-compose-dev.yml`.

---

## Database: PostgreSQL

You can run PostgreSQL either with Docker or a local install.

### Option A: Run PostgreSQL via Docker (standalone)

```bash
docker run --name posts-db \
  -e POSTGRES_PASSWORD=admin123 \
  -e POSTGRES_DB=fastapi \
  -p 5432:5432 -d postgres
```

Common psql commands:

```bash
# Connect
psql postgresql://postgres:admin123@localhost:5432/fastapi

# List databases and tables
\\l
\\dt

# Create test database
CREATE DATABASE fastapi_test;
```

### Option B: Run PostgreSQL via Docker Compose (dev)

`docker-compose-dev.yml` defines an `api` and `postgres` service.

```bash
docker compose -f docker-compose-dev.yml up -d

# View logs
docker compose -f docker-compose-dev.yml logs -f postgres
```

Compose dev defaults (from file):
- Postgres exposed on `localhost:5432`
- App exposed on `http://localhost:8000`

For production-like compose, see [Docker (prod)](#docker-prod).

---

## Migrations: Alembic

Alembic is configured in `alembic/env.py` to read the DB URL from `Settings`.

Common commands:

```bash
# 1) Create a new revision (auto-generate from model changes)
alembic revision --autogenerate -m "your message"

# 2) Apply migrations to latest
alembic upgrade head

# 3) Roll back one step
alembic downgrade -1

# 4) Show current revision
alembic current
```

If `alembic` can’t locate the config, run from the project root where `alembic.ini` resides.

---

## Local development (without Docker)

```bash
# 1) Create venv
python3 -m venv venv
source venv/bin/activate

# 2) Install deps
pip install -r requirements.txt

# 3) Ensure PostgreSQL is running and .env is set (see above)

# 4) Run migrations
alembic upgrade head

# 5) Start API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API will be available at:
# http://localhost:8000
# http://localhost:8000/docs
```

Tip: The raw psycopg2 connection helper in `app/database.py` uses `localhost:5433` in `connect_db_driver()` for manual checks. If you want to use it locally, either run Postgres on 5433 or update that function.

---

## Running tests

Tests use a separate database `<DATABASE_NAME>_test` (e.g., `fastapi_test`). Ensure it exists or that your DB user can create it.

```bash
# Activate venv first
source venv/bin/activate

# Ensure DB is up and .env configured

# Create the test DB once (if needed)
psql postgresql://postgres:admin123@localhost:5432/postgres -c "CREATE DATABASE fastapi_test;" || true

# Run tests
pytest -q
```

`tests/conftest.py` creates/drops tables per test session and overrides `get_db` for isolation.

---

## Docker (dev)

`docker-compose-dev.yml` uses live-reload and a bind mount of your source for fast iteration.

```bash
# Build and start
docker compose -f docker-compose-dev.yml up --build

# Or detached
docker compose -f docker-compose-dev.yml up -d --build

# Stop and remove
docker compose -f docker-compose-dev.yml down
```

Endpoints:
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`

---

## Docker (prod)

`docker-compose-prod.yml` builds the image and exposes the app on port 80.

```bash
docker compose -f docker-compose-prod.yml up -d --build

# Check services
docker compose -f docker-compose-prod.yml ps
```

Environment variables are passed via the shell or a `.env` file referenced by compose (the file uses `${VAR}` references). Ensure you set these before running.

You can pair this with an external **Nginx** reverse proxy (see `nginx/` directory) and **Gunicorn** (see `gunicorn.service` / `Procfile`) if deploying outside of Compose-managed networks.

---

## Useful commands (quick reference)

```bash
# Alembic
alembic revision --autogenerate -m "<message>"
alembic upgrade head
alembic downgrade -1

# Local API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Docker Compose (dev)
docker compose -f docker-compose-dev.yml up -d --build
docker compose -f docker-compose-dev.yml down

# Docker Compose (prod)
docker compose -f docker-compose-prod.yml up -d --build
docker compose -f docker-compose-prod.yml down

# Postgres (standalone via Docker)
docker run --name posts-db -e POSTGRES_PASSWORD=admin123 -e POSTGRES_DB=fastapi -p 5432:5432 -d postgres

# psql
psql postgresql://postgres:admin123@localhost:5432/fastapi

# Tests
pytest -q
```

---

## API quick start

After starting the app (local or Docker), open:
- Swagger UI: `http://localhost:<port>/docs`
- Health/root: `GET /` → returns a JSON greeting

Routers are included in `app.main`:

```12:38:app/main.py
from fastapi import FastAPI
from . import models
from .database import engine
from .routers import post, user, auth, vote
from .config import settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
def root():
    return {"message" : "Hello World! My First Production Deployment and server"}
```

---

## Troubleshooting

- If Alembic can’t find models: ensure `app.models.Base` is imported in `alembic/env.py` (it is), and you run commands from the project root.
- If UVicorn can’t connect to DB: verify `.env` and Postgres availability. Match ports between your runtime and `DATABASE_PORT`.
- If tests fail with connection errors: create `fastapi_test` DB and confirm env vars.

---

## License

Personal learning project. No license specified.
