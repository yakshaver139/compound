# Compound

Personal finance tracker — record transactions, set savings goals, and view spending summaries.

Built with FastAPI (Python) and vanilla JS. The UI is served directly by the backend, so a single process gives you the full app.

## Quickstart

### Option A — Docker (recommended)

```bash
make up
```

Open <http://localhost:8000>.

### Option B — Local Python

Requires Python 3.12+.

```bash
make install   # pip install -r requirements.txt
make run       # uvicorn with --reload
```

Open <http://localhost:8000>.

## Pages

| URL | What it does |
|-----|-------------|
| `/` | Add & view transactions |
| `/goals-page` | Create savings goals with projections |
| `/summary-page` | Income, expenses & spend-by-category |

## API

Swagger docs are auto-generated at <http://localhost:8000/docs>.

Key endpoints:

```
POST   /transactions          Create a transaction
GET    /transactions          List (filter: from, to, category)

POST   /goals                 Create a goal
GET    /goals                 List with projections

GET    /summary               Income / expense / net (filter: from, to)
GET    /health                Health check
```

## Tests

```bash
make test      # or: pytest
make test-v    # verbose
```

## Project structure

```
app/
  main.py              FastAPI app + CORS config
  models.py            Pydantic models & computations
  storage.py           JSON file persistence (data/compound.json)
  routers/             Endpoint modules (transactions, goals, summary, ui)
  templates/           HTML pages (vanilla JS)
tests/                 Pytest suite
Dockerfile
docker-compose.yml
```

## Make targets

Run `make help` for the full list:

```
  install          Install Python dependencies
  run              Run the app locally (backend + UI on :8000)
  test             Run the test suite
  test-v           Run the test suite (verbose)
  up               Build & start with Docker Compose
  up-d             Build & start in the background
  down             Stop Docker Compose services
  clean            Remove data file and __pycache__
```
