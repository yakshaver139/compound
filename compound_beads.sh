#!/usr/bin/env bash
set -euo pipefail

# Compound PoC: single script to
# 1) create issues with SHORT titles + rich --description
# 2) resolve IDs via `bd list` by matching titles
# 3) wire dependencies using `bd dep add <blocked_id> <blocker_id>`

need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing required command: $1" >&2; exit 1; }; }
need bd
need grep

create_issue () {
  local title="$1"
  local description="$2"
  echo "Creating: $title" >&2
  bd create "$title" --description "$description" >/dev/null
}

get_id_by_title() {
  local title="$1"
  local line
  # Expecting: "○ compound-xxxx ... - <TITLE>"
  line="$(bd list | grep -F " - ${title}" | head -n 1 || true)"
  if [[ -z "${line}" ]]; then
    echo "ERROR: Could not find issue with title: ${title}" >&2
    echo "Hint: run 'bd list' and verify the exact title text matches." >&2
    exit 1
  fi
  echo "${line}" | grep -Eo 'compound-[a-z0-9]+' | head -n 1
}

# --- Canonical short titles (must match exactly for ID resolution) ---
TITLE_SCAFFOLD="Compound PoC: scaffold minimal FastAPI app"
TITLE_STORE="Compound PoC: core models + JSON file storage"
TITLE_TX_ADD="Compound PoC API: add transaction (POST /transactions)"
TITLE_TX_LIST="Compound PoC API: list transactions (GET /transactions)"
TITLE_SUMMARY_CORE="Compound PoC core: compute simple summaries"
TITLE_SUMMARY_API="Compound PoC API: summary endpoint (GET /summary)"
TITLE_GOALS_CORE="Compound PoC feature: goals + simple projection"
TITLE_GOALS_API="Compound PoC API: goals endpoints (POST /goals, GET /goals)"
TITLE_UI_SKELETON="Compound PoC UI: minimal React app skeleton + API client"
TITLE_UI_TX="Compound PoC UI: transactions screen (list + add)"
TITLE_UI_SUMMARY="Compound PoC UI: summary screen"
TITLE_UI_GOALS="Compound PoC UI: goals screen"
TITLE_DOCKER="Compound PoC: dockerise backend + UI"

echo "Creating issues (titles + descriptions)..."

create_issue "$TITLE_SCAFFOLD" \
"Goal: create a tiny personal finance backend to prove Beadloom workflows.

Stack:
- Backend: FastAPI (Python) + Pydantic v2
- Persistence: local JSON file (no DB / ORM)
- Frontend: minimal React app calling the API

Domain:
- Transaction: { id, date, amount, merchant, category, notes }
  - amount: positive = income, negative = expense
- Goal: { id, name, target_amount, monthly_contribution, start_date }
- Summary: totals + spend by category (+ optional monthly net)

Endpoints (eventual):
- GET  /health
- POST /transactions
- GET  /transactions
- GET  /summary
- POST /goals
- GET  /goals

Requirements:
- /health returns 200 and JSON {\"status\":\"ok\"}
- Router structure for /transactions, /goals, /summary
- Enable CORS for localhost:3000 and/or 5173
- No auth, no docker, no database

Definition of Done:
- \`uvicorn app.main:app --reload\` runs
- /health works via browser/curl
"

create_issue "$TITLE_STORE" \
"Implement core domain models + JSON persistence.

Pydantic models:
- Transaction:
  - id: string (uuid)
  - date: YYYY-MM-DD string
  - amount: number (positive income, negative expense)
  - merchant: string
  - category: string (groceries, rent, salary, bills, fun, other)
  - notes: optional string
- Goal:
  - id: string (uuid)
  - name: string
  - target_amount: number
  - monthly_contribution: number
  - start_date: YYYY-MM-DD string

Persistence:
- Single JSON file: data/compound.json, shape:
  { \"transactions\": [...], \"goals\": [...] }
- Helpers:
  - load_data() -> dict (create file if missing)
  - save_data(data) -> None (atomic write if easy)
  - append_transaction(tx) / append_goal(goal)
- Create data folder/file automatically.

DoD:
- Can load/save without errors
- File created on first run
"

create_issue "$TITLE_TX_ADD" \
"Implement POST /transactions.

Behaviour:
- Accept TransactionCreate (Transaction minus id)
- Generate id (uuid)
- Persist to JSON store
- Return created Transaction

Validation:
- date must look like YYYY-MM-DD
- amount numeric
- category defaults to 'other' if blank/missing

DoD:
- curl POST works and persists
"

create_issue "$TITLE_TX_LIST" \
"Implement GET /transactions.

Behaviour:
- Return all transactions (most recent first)
- Optional query params:
  - from=YYYY-MM-DD
  - to=YYYY-MM-DD
  - category=string

DoD:
- Filters work
- Returns JSON array of Transaction
"

create_issue "$TITLE_SUMMARY_CORE" \
"Compute summary from transactions.

Summary fields:
- total_income: sum(amount where amount > 0)
- total_expense: abs(sum(amount where amount < 0))
- net: sum(all amounts)
- spend_by_category: map(category -> abs(sum(negative amounts)))

Optional:
- monthly_net: map(YYYY-MM -> net)

DoD:
- Pure function(s) that take list[Transaction] and return Summary dict/model
"

create_issue "$TITLE_SUMMARY_API" \
"Implement GET /summary.

Behaviour:
- Return Summary computed from stored transactions
- Optional query params from/to to scope the summary (same semantics as GET /transactions)

DoD:
- Returns totals + spend_by_category
"

create_issue "$TITLE_GOALS_CORE" \
"Implement goals + simple projection.

Goal fields:
- name, target_amount, monthly_contribution, start_date (+ id)

Projection:
- months_to_target = ceil(target_amount / monthly_contribution) (handle zero safely)
- target_date = start_date + months_to_target months (approx ok)

DoD:
- Functions compute projection for a goal
- Projection included in API responses
"

create_issue "$TITLE_GOALS_API" \
"Implement goals endpoints.

- POST /goals: create goal (uuid), persist, return
- GET /goals: return goals including computed projection:
  - months_to_target
  - target_date (YYYY-MM-DD)

DoD:
- curl create + list works
"

create_issue "$TITLE_UI_SKELETON" \
"Create minimal React UI (Vite ok) + API client.

UI requirements:
- 3 pages/tabs:
  - Transactions
  - Summary
  - Goals
- Minimal API client module:
  - base URL default http://localhost:8000 (or env)

DoD:
- npm install && npm run dev works
- Navigation visible
"

create_issue "$TITLE_UI_TX" \
"Transactions page:
- List transactions (GET /transactions)
- Add transaction form: date, amount, merchant, category, notes
- Submit -> POST /transactions then refresh list

DoD:
- Can add expense and see it appear
"

create_issue "$TITLE_UI_SUMMARY" \
"Summary page:
- Call GET /summary
- Display total_income, total_expense, net
- Display spend_by_category table/list

DoD:
- Updates after adding transactions
"

create_issue "$TITLE_UI_GOALS" \
"Goals page:
- Create goal form (POST /goals)
- List goals (GET /goals) incl months_to_target + target_date

DoD:
- Can create a goal and see projection
"

create_issue "$TITLE_DOCKER" \
"Dockerise backend + UI (lightweight).

Deliverables:
- Dockerfile(s) for backend + UI
- docker-compose.yml
- Ensure UI can call backend (base URL / env wiring)
- Expose API on 8000 and UI on 3000/5173

DoD:
- docker compose up --build starts both services
- UI can call API successfully
"

echo ""
echo "Resolving IDs from bd list..."
SCAFFOLD="$(get_id_by_title "$TITLE_SCAFFOLD")"
STORE="$(get_id_by_title "$TITLE_STORE")"
TX_ADD="$(get_id_by_title "$TITLE_TX_ADD")"
TX_LIST="$(get_id_by_title "$TITLE_TX_LIST")"
SUMMARY_CORE="$(get_id_by_title "$TITLE_SUMMARY_CORE")"
SUMMARY_API="$(get_id_by_title "$TITLE_SUMMARY_API")"
GOALS_CORE="$(get_id_by_title "$TITLE_GOALS_CORE")"
GOALS_API="$(get_id_by_title "$TITLE_GOALS_API")"
UI_SKELETON="$(get_id_by_title "$TITLE_UI_SKELETON")"
UI_TX="$(get_id_by_title "$TITLE_UI_TX")"
UI_SUMMARY="$(get_id_by_title "$TITLE_UI_SUMMARY")"
UI_GOALS="$(get_id_by_title "$TITLE_UI_GOALS")"
DOCKER="$(get_id_by_title "$TITLE_DOCKER")"

echo ""
echo "Wiring dependencies..."

# --- Foundations ---
bd dep add "$STORE" "$SCAFFOLD"

# --- Transactions ---
bd dep add "$TX_ADD" "$STORE"
bd dep add "$TX_ADD" "$SCAFFOLD"

bd dep add "$TX_LIST" "$STORE"
bd dep add "$TX_LIST" "$SCAFFOLD"

# --- Summaries ---
bd dep add "$SUMMARY_CORE" "$TX_LIST"
bd dep add "$SUMMARY_API" "$SUMMARY_CORE"
bd dep add "$SUMMARY_API" "$SCAFFOLD"

# --- Goals ---
bd dep add "$GOALS_CORE" "$STORE"
bd dep add "$GOALS_CORE" "$SUMMARY_CORE"
bd dep add "$GOALS_API" "$GOALS_CORE"
bd dep add "$GOALS_API" "$SCAFFOLD"

# --- UI ---
bd dep add "$UI_SKELETON" "$SCAFFOLD"

bd dep add "$UI_TX" "$UI_SKELETON"
bd dep add "$UI_TX" "$TX_ADD"
bd dep add "$UI_TX" "$TX_LIST"

bd dep add "$UI_SUMMARY" "$UI_SKELETON"
bd dep add "$UI_SUMMARY" "$SUMMARY_API"

bd dep add "$UI_GOALS" "$UI_SKELETON"
bd dep add "$UI_GOALS" "$GOALS_API"

# --- Dockerise (last step) ---
bd dep add "$DOCKER" "$UI_GOALS"
bd dep add "$DOCKER" "$UI_SUMMARY"
bd dep add "$DOCKER" "$UI_TX"
bd dep add "$DOCKER" "$SCAFFOLD"

echo ""
echo "Done."
echo "Root issue (should be unblocked): $SCAFFOLD"
echo "Sanity checks:"
echo "  bd cycles"
echo "  bd tree $SCAFFOLD"

