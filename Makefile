.DEFAULT_GOAL := help

# ── Local ────────────────────────────────────────────────────
install:            ## Install Python dependencies
	pip install -r requirements.txt

run:                ## Run the app locally (backend + UI on :8000)
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

test:               ## Run the test suite
	pytest

test-v:             ## Run the test suite (verbose)
	pytest -v

# ── Docker ───────────────────────────────────────────────────
up:                 ## Build & start with Docker Compose
	docker compose up --build

up-d:               ## Build & start in the background
	docker compose up --build -d

down:               ## Stop Docker Compose services
	docker compose down

# ── Misc ─────────────────────────────────────────────────────
clean:              ## Remove data file and __pycache__
	rm -rf data/compound.json __pycache__ app/__pycache__ tests/__pycache__

help:               ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

.PHONY: install run test test-v up up-d down clean help
