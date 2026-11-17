# FlowIQ — AI Business Process & Data Intelligence Platform

A **runnable Django MVP** for uploading sales CSVs, validating and storing rows in SQL, viewing a responsive business intelligence dashboard, querying safe precomputed metrics over REST, exporting reports, and optionally generating an LLM-based narrative summary from aggregate metrics.

**Important:** This is a demonstration project, not a production-hardened enterprise product. Example data is synthetic. The core Q&A assistant is deterministic, not a free-form LLM chatbot. LLM narrative summaries are optional and require your own API key or local Ollama model. Do not put confidential data into an external AI provider without permission.

## Features

- Account signup / login and per-user dataset access restrictions
- Validated CSV import (UTF-8, max 2 MB and 10,000 rows)
- PostgreSQL with Docker, SQLite for easy local development
- Dashboard: revenue, quantity, order records, average revenue per record, countries, customers, products, yearly totals
- REST API: dataset list, metrics, safe questions, optional LLM summary
- CSV summary report download and dataset deletion
- Django admin, test suite, sample sales data, Docker Compose
- Git-ready source structure and responsive UI

## Quick start A — Docker Compose (PostgreSQL)

Install Docker Desktop, unzip, open a terminal in this folder, then:

```bash
# Optional: create .env from .env.example and replace secrets
# For Linux/macOS: cp .env.example .env
# For Windows PowerShell: Copy-Item .env.example .env
docker compose up --build
```

Go to **http://localhost:8000/signup/**, create an account, download the provided sample CSV from the upload page, and upload it. To stop: `docker compose down`. Data persists in the `postgres_data` volume. To completely erase database data: `docker compose down -v` (destructive).

**Note:** Docker Compose automatically configures PostgreSQL for its `web` container. If `.env` contains `DATABASE_URL`, Compose still uses the Compose database URL for this service.

## Quick start B — Local Python (SQLite)

Python 3.11+ recommended (3.12 is the Docker target). In the project directory:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux:
# source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Local defaults use SQLite and have AI disabled. Open **http://127.0.0.1:8000/signup/**. For a Django admin account: `python manage.py createsuperuser` then visit `/admin/`.

### Use the bundled demo data

`static/sample_sales.csv` is synthetic. Create an account, click Upload data, enter a dataset name and choose the file.

## Configure optional generative AI

Core metrics and question buttons run **without** AI credentials.

To enable an OpenAI-generated summary based **only on aggregated KPI data**:

1. Copy `.env.example` to `.env` and set `AI_PROVIDER=openai` and `OPENAI_API_KEY=...`.
2. Use `docker compose up --build`, or export those variables into your local shell if running Python directly. Django does **not** automatically load `.env` on the non-Docker path.
3. Click **AI summary (optional)** on the dashboard.

The code submits the aggregate metric JSON, including top customer/product/country names, to the configured provider; use synthetic or approved data only. OpenAI API usage may incur costs; account access and model availability vary. You may change `OPENAI_MODEL` to a supported model in your account.

For local Ollama: install and run Ollama, pull your chosen model (`ollama pull llama3.2`), then set `AI_PROVIDER=ollama`. In Docker, the default URL points at the host via `host.docker.internal`; configure Ollama to accept connections from Docker if necessary. Ollama does not require a paid API key, but the machine needs enough memory/resources. Local requests default to localhost.

## REST API

API access requires login via Django session cookie. Browser POST requests require CSRF token. Endpoints:

| Method | Route | Action |
|---|---|---|
| GET | `/health/` | Health status (demo only) |
| GET | `/api/datasets/` | Your datasets |
| GET | `/api/datasets/<id>/metrics/` | Dataset aggregated metrics |
| POST | `/api/datasets/<id>/ask/` | JSON `{"question":"top customers"}` |
| POST | `/api/datasets/<id>/ai-summary/` | Optional provider-backed summary |
| GET | `/export/<id>/` | Download summary CSV |
| POST | `/delete/<id>/` | Delete one of your datasets |

The web dashboard is the easiest way to exercise authenticated APIs. Invalid IDs or other users' datasets return 404. See tests for examples.

## Input CSV schema

```csv
order_date,customer,product,country,quantity,unit_price
2026-01-05,Acme,Widget A,Germany,3,19.99
2026-02-05,Northwind,Widget B,France,1,50.00
```

- Dates: ISO 8601 `YYYY-MM-DD`
- `quantity`: positive integer
- `unit_price`: nonnegative decimal, dot separator
- `revenue = quantity × unit_price` (computed during import)
- Data is processed in an atomic transaction: invalid rows prevent dataset creation
- Reporting currency is **assumed EUR** (no FX conversion). Upload only EUR datasets or adapt the code.
- One row is interpreted as one order *record*, not necessarily a unique order or invoice.

## Run tests

```bash
python manage.py test
python manage.py check
```

With Docker:

```bash
docker compose exec web python manage.py test
```

## Suggested CV wording (only after you have actually built and tested it)

> Built a Django/Python business intelligence prototype with validated CSV ingestion, PostgreSQL storage, REST endpoints, KPI dashboards, and an optional LLM-generated summary grounded in precomputed business metrics. Containerized the solution with Docker and added access controls and automated tests.

## Production considerations

Before any public deployment: use a strong secret key, disable DEBUG, enforce HTTPS and secure cookies, use a production WSGI/ASGI server, configure static hosting, add throttling/rate limits, monitoring and logging, protect credentials, implement data retention and GDPR controls, add explicit AI data-processing consent, tighten file and user quotas, and conduct security review. The Docker configuration is intentionally **development only**.

## Project layout

```text
config/              Django settings and root URLs
intelligence/        Models, forms, views, analysis services, URLs, admin, tests, migration
templates/           Pages for login, registration, upload and dashboard
static/              Styles and synthetic sample CSV
Dockerfile           Web container
docker-compose.yml   PostgreSQL + web service
.env.example         Environment configuration reference
requirements.txt     Python dependencies
```


## FlowIQ 2.0 upgrades (November 2026)

- **Interactive data visualizations:** monthly-revenue line chart and country-comparison bars, rendered with local browser SVG (no CDN needed). Hover over points and bars for revenue values.
- **Automated computed insights:** reproducible total revenue, leading customer/product/market, revenue share, and unadjusted year change. No external AI required.
- **Filtered business questions:** ask `Revenue in Germany in 2025`, `Sales of Widget`, `Revenue for Alice` or `Monthly revenue in 2026`. Matching operates only on known customer/product/country values and uses Django ORM filtering.
- **Optional generative AI Q&A:** click `Ask AI` for a narrative based on calculated metrics. Requires `AI_PROVIDER=openai` + key or local Ollama. The application does **not** support arbitrary SQL or arbitrary CSV schemas.
- **New routes:** `GET /api/datasets/<id>/insights/` and `POST /api/datasets/<id>/ai-ask/` with JSON `{"question":"..."}`. Authenticated and dataset-owner scoped.

### Upgrade an existing Docker installation

Extract the new ZIP into a **new directory** (do not remove your prior directory until your data has been backed up). If you run `docker compose` inside the new directory, Compose uses a different project name and will create a different PostgreSQL volume; your previous uploaded datasets won't appear by default. To **preserve existing local datasets**, back up the database and then replace only your prior source files (or keep the original Compose project name using `docker compose -p ORIGINAL_PROJECT_NAME up --build`). Never delete a PostgreSQL volume without a backup.

### Configuration details

The base analytics, filtered answers, charts and computed insights work with `AI_PROVIDER=none`. Generative AI needs optional configuration in `.env`, supplied to Docker Compose. An OpenAI API may incur charges; local Ollama is free but requires a downloaded model and enough system resources. AI responses should be reviewed before business use. Generated sales sample data is synthetic.
