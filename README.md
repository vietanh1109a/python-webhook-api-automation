# Python Webhook & API Automation Service

A lightweight Python automation service that receives lead webhooks, validates and cleans records, prevents duplicates, integrates with external APIs, stores structured data, and exports business-ready CSV and Excel reports.

> **Project Classification**: Portfolio Project / Reference Implementation for freelance data engineering, API integration, and automation workflows.

---

### Key Highlights for Clients
- **Problem**: Manual lead intake and spreadsheet cleanup wastes time and creates duplicate/inconsistent records.
- **Solution**: Webhook → validation → normalization → deduplication → optional API enrichment → database → API/CSV/Excel outputs.
- **Core Skills**: `Python` • `FastAPI` • `REST API` • `Webhooks` • `API Integration` • `Data Processing` • `SQLAlchemy` • `SQLite` • `PostgreSQL support` • `pandas` • `Excel` • `CSV` • `pytest`

---

## Portfolio Preview

| 01. Interactive REST API & Webhooks | 02. Formatted Multi-Sheet Excel Report |
| :---: | :---: |
| ![API Overview](portfolio/01_api_overview.png) | ![Excel Report](portfolio/02_excel_report.png) |

<p align="center">
  <b>03. End-to-End Automation Workflow</b><br>
  <img src="portfolio/03_workflow_overview.png" alt="Workflow Overview" width="95%">
</p>

---

## 1. Project Title
**Python Webhook & API Automation Service** (`python-webhook-api-automation`)

---

## 2. Short Business Explanation
Small businesses frequently capture sales inquiries and customer interest from diverse digital channels—including website contact forms, Shopify storefronts, Facebook ads, and partner CRMs. Instead of manually copying, verifying, and formatting each inbound submission in spreadsheets, this service acts as an autonomous intake hub that ingests webhooks in real time, standardizes dirty inputs, eliminates duplicate submissions, optionally enriches records with third-party intelligence, and delivers clean REST APIs and formatted Excel reports for leadership and sales teams.

---

## 3. The Problem
- **Human Error & Inefficiencies**: Manual copy-pasting from email alerts into spreadsheets results in lost leads, typos, and delayed outreach.
- **Inconsistent & Corrupt Data**: Users submit arbitrary formatting (`"  JOHN.SMITH@EXAMPLE.COM "`, multiple spaces, erratic company names) which pollutes downstream CRMs.
- **Duplicate Records**: Multiple clicks or re-submissions result in sales reps contacting the same customer repeatedly and skewed funnel metrics.
- **Fragile Integrations**: Direct third-party API dependencies frequently fail or time out, which often causes typical scripts to crash and drop leads entirely.
- **Lack of Clean Reporting**: Non-technical stakeholders cannot easily obtain structured, formatted spreadsheet exports with automated KPI summaries.

---

## 4. The Solution
This service provides a resilient, automated middle layer:
1. Validates webhook payloads via Pydantic schemas.
2. Applies strict whitespace collapsing and email/source normalization.
3. Deterministically detects duplicates using external reference IDs or channel-scoped email matching.
4. Enhances lead data via an extensible enrichment interface with automated retries and exponential backoff.
5. Persists records and audit events in a relational database (SQLite zero-config default, PostgreSQL supported).
6. Exposes paginated REST query endpoints and persistent processing metrics.
7. Produces downloadable CSV exports and formatted multi-sheet Excel reports (`openpyxl`).

---

## 5. End-to-End Workflow
1. **Webhook Reception**: Inbound HTTP POST payload received at `/webhooks/leads`.
2. **Schema & Email Validation**: Enforces required fields and RFC-compliant email formats.
3. **Data Normalization**: Strips leading/trailing whitespace, collapses internal consecutive spaces, lowercases email/source, preserves name capitalization, and converts empty strings to `None`.
4. **Deduplication Check**:
   - If `external_id` is supplied: checks for existing `(source, external_id)`.
   - If `external_id` is missing: checks for existing `(source, email)`.
   - If matched: logs audit event and returns HTTP 200 with existing lead ID.
5. **Enrichment Engine**:
   - Executes active provider (`off`, `mock`, or `http`).
   - In HTTP mode: attempts request with Bearer authentication and up to 3 retries (0.25s, 0.5s, 1.0s exponential backoff).
   - If enrichment times out or fails, lead ingestion still succeeds gracefully with a `failed` audit flag.
6. **Persistence & Auditing**: Saves lead and corresponding event records to the database.
7. **Reporting & REST Access**: Data is immediately accessible via paginated endpoints, CSV download, or styled multi-sheet Excel workbooks.

---

## 6. Key Features
- **Deterministic Deduplication**: Prevents duplicate database rows while acknowledging webhooks with HTTP 200.
- **Resilient Third-Party Integration**: HTTP enrichment provider with automatic exponential backoff retries on network errors, timeouts, and 5xx/429 responses.
- **Fault-Tolerant Error Handling**: Client errors return clean JSON payloads; unhandled exceptions are logged with safe generic messages (no exposed stack traces).
- **Persistent Processing KPIs**: Audits every event (`webhook_received`, `lead_created`, `duplicate_detected`, `enrichment_success`, `enrichment_failed`).
- **Professional Multi-Sheet Excel Reports**: Formatted with bold headers, freeze panes, autofilters, date/number formatting, and summary KPI distribution.
- **Zero-Configuration Setup**: Works instantly with local SQLite database file creation.

---

## 7. Architecture Diagram

```mermaid
graph TD
    A["Lead Source\n(Website / CRM / Shopify / Ads)"] -->|"POST /webhooks/leads (JSON)"| B["FastAPI Webhook Handler"]
    B --> C["Validation & Schema Enforcement\n(Pydantic v2 + EmailValidator)"]
    C --> D["Data Normalization Engine\n(Strip & collapse whitespace, lowercase emails)"]
    D --> E{"Deduplication Engine"}
    E -->|"Duplicate Found\n(source + external_id OR source + email)"| F["Log Audit Event\nReturn HTTP 200 (duplicate)"]
    E -->|"New Record"| G["Enrichment Service\n(off / mock / http with retries)"]
    G --> H["SQLAlchemy 2.x Session"]
    H --> I[("SQL Database\nSQLite (default) / PostgreSQL")]
    I --> J["Lead Table + ProcessingEvent Table"]
    J --> K["REST API\n(/api/leads, /api/leads/{id})"]
    J --> L["Processing Statistics\n(/api/stats)"]
    J --> M["CSV Export Engine\n(/api/export/csv)"]
    J --> N["Styled Excel Generator\n(/api/export/excel)"]
```

---

## 8. Tech Stack
- **Runtime**: Python 3.12
- **Web Framework**: FastAPI, Uvicorn
- **Validation**: Pydantic v2, email-validator
- **Database ORM**: SQLAlchemy 2.0
- **Databases**: SQLite (zero-config demo), PostgreSQL supported via `DATABASE_URL`
- **HTTP Client**: httpx (with `MockTransport` for isolated unit testing)
- **Data & Excel Processing**: pandas, openpyxl
- **Code Quality & Testing**: pytest, pytest-asyncio, ruff
- **Configuration**: python-dotenv

---

## 9. Project Structure
```text
python-webhook-api-automation/
├── app/
│   ├── __init__.py
│   ├── config.py              # Environment variable loader & settings
│   ├── crud.py                # Database queries and statistical aggregations
│   ├── database.py            # SQLAlchemy engine, sessionmaker, and init
│   ├── main.py                # FastAPI app setup, lifecycle, and middleware
│   ├── models.py              # Lead and ProcessingEvent SQLAlchemy models
│   ├── schemas.py             # Pydantic v2 request & response schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── exports.py         # CSV & Excel file download endpoints
│   │   ├── health.py          # GET /health
│   │   ├── leads.py           # GET /api/leads & GET /api/leads/{id}
│   │   ├── stats.py           # GET /api/stats
│   │   └── webhooks.py        # POST /webhooks/leads
│   └── services/
│       ├── __init__.py
│       ├── deduplication.py   # Deterministic duplicate detection logic
│       ├── enrichment.py      # Abstract enrichment service (off, mock, http)
│       ├── exporters.py       # pandas and openpyxl report builders
│       └── normalization.py   # Pure string cleaning & normalization rules
├── data/                      # Local SQLite storage directory
│   └── .gitkeep
├── exports/                   # Downloaded CSV and Excel reports
│   └── .gitkeep
├── portfolio/
│   ├── 01_api_overview.png    # High-resolution Swagger UI screenshot
│   ├── 02_excel_report.png    # Styled Excel report screenshot
│   ├── 03_workflow_overview.png # System workflow diagram
│   └── README.md              # Client-facing Upwork portfolio case study
├── sample_payloads/
│   ├── duplicate_lead.json    # Payload testing duplicate detection & cleaning
│   ├── malformed_lead.json    # Payload testing validation error handling
│   ├── minimal_lead.json      # Minimal payload with required fields only
│   └── valid_lead.json        # Standard valid lead payload
├── scripts/
│   ├── generate_assets.py     # Portfolio screenshot generator
│   └── run_demo.py            # End-to-end demo script
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Isolated in-memory DB & TestClient fixtures
│   ├── test_enrichment.py     # Unit & retry tests for enrichment providers
│   ├── test_exports.py        # CSV & Excel formatting tests
│   ├── test_health.py         # Health endpoint test
│   ├── test_leads.py          # Query & pagination tests
│   ├── test_normalization.py  # Pure normalization rule tests
│   ├── test_stats.py          # Audit event & KPI count tests
│   └── test_webhooks.py       # Webhook ingestion & duplicate tests
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── pyproject.toml             # Ruff and pytest configuration
├── README.md                  # Comprehensive documentation
└── requirements.txt           # Project dependencies
```

---

## 10. Installation
Clone the repository and install dependencies in your Python 3.12 environment:

```bash
# Clone repository
git clone https://github.com/example/python-webhook-api-automation.git
cd python-webhook-api-automation

# Optional: Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 11. Configuration
Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

### Configuration Variables
| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data/leads.db` | SQLAlchemy connection string |
| `ENRICHMENT_MODE` | `mock` | Enrichment mode: `off`, `mock`, or `http` |
| `ENRICHMENT_API_URL` | `""` | Outbound endpoint when mode is `http` |
| `ENRICHMENT_API_KEY` | `""` | Optional Bearer token for outbound API |
| `ENRICHMENT_TIMEOUT_SECONDS` | `5` | Request timeout in seconds |
| `LOG_LEVEL` | `INFO` | Python logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

---

## 12. Running the Server
Start the Uvicorn ASGI server locally:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- API Base URL: `http://127.0.0.1:8000`
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc Documentation: `http://127.0.0.1:8000/redoc`

---

## 13. API Endpoints

| Method | Endpoint | Description | Success Code |
|---|---|---|---|
| `GET` | `/health` | Service health status check | `200 OK` |
| `POST` | `/webhooks/leads` | Ingest, clean, deduplicate, and enrich lead | `201 Created` / `200 OK (duplicate)` |
| `GET` | `/api/leads` | Paginated lead list with `page`, `page_size`, `source` | `200 OK` |
| `GET` | `/api/leads/{lead_id}` | Retrieve individual lead by primary ID | `200 OK` (or `404 Not Found`) |
| `GET` | `/api/stats` | Ingestion metrics, duplicate totals, and source breakdown | `200 OK` |
| `GET` | `/api/export/csv` | Download all leads as UTF-8 CSV | `200 OK` |
| `GET` | `/api/export/excel` | Download multi-sheet formatted `.xlsx` report | `200 OK` |

---

## 14. Example Webhook
Send an HTTP POST to `http://127.0.0.1:8000/webhooks/leads`:

```bash
curl -X POST "http://127.0.0.1:8000/webhooks/leads" \
     -H "Content-Type: application/json" \
     -d '{
       "external_id": "shopify-10492",
       "name": "  John   Smith ",
       "email": " JOHN.SMITH@example.com ",
       "company": "  Acme Furniture  ",
       "source": "Shopify",
       "notes": " Interested in 20 office chairs "
     }'
```

### Response (New Lead Created - HTTP 201)
```json
{
  "status": "created",
  "lead_id": 1,
  "message": "Lead created successfully"
}
```

### Response (Duplicate Ingested - HTTP 200)
```json
{
  "status": "duplicate",
  "lead_id": 1,
  "message": "Lead already exists"
}
```

---

## 15. Demo Script
An automated demonstration script exercises the full pipeline against a running server:

```bash
python scripts/run_demo.py
```

The script:
1. Verifies `/health`.
2. Posts `sample_payloads/valid_lead.json`.
3. Posts `sample_payloads/duplicate_lead.json` to prove whitespace/case-insensitive deduplication.
4. Posts `sample_payloads/malformed_lead.json` to verify non-crashing 422 error handling.
5. Ingests diverse multi-channel leads.
6. Queries `/api/leads` and `/api/stats`.
7. Downloads and validates `exports/leads_export.csv` and `exports/leads_export.xlsx`.

---

## 16. CSV Export
- Endpoint: `GET /api/export/csv`
- Default Filename: `leads_export.csv`
- Header: UTF-8 encoded with standard comma separators.
- Fields: `ID, External ID, Name, Email, Company, Source, Notes, Enrichment Status, Enrichment Score, Enrichment Segment, Created At`.

---

## 17. Excel Export
- Endpoint: `GET /api/export/excel`
- Default Filename: `leads_export.xlsx`
- Built using **pandas** and **openpyxl**:
  - **Sheet 1: `Leads`**:
    - Freeze pane on first row (`A2`).
    - Autofilter enabled on entire data range.
    - Dark navy branded header styling with white bold text.
    - Auto-fitted column widths.
    - Numeric formatting for scores (`0.0`) and date-time formatting for timestamps.
    - No raw index columns.
  - **Sheet 2: `Summary`**:
    - KPI Table: Total Leads, Total Webhooks, Created, Duplicates, Enrichment Success, Enrichment Failed.
    - Source Breakdown Table: Lead count grouped by acquisition source.

---

## 18. Testing
The test suite utilizes isolated, in-memory SQLite instances via pytest fixtures, ensuring test isolation without modifying the demo database:

```bash
# Run test suite
pytest -v

# Run with coverage/quiet
pytest -q
```

### Linter & Style Checks
```bash
ruff check .
```

---

## 19. PostgreSQL Configuration
PostgreSQL is supported through `DATABASE_URL` configuration.

To connect this service to a PostgreSQL instance:

1. Ensure psycopg binary is installed (included in `requirements.txt`):
   ```bash
   pip install "psycopg[binary]>=3.1.0"
   ```
2. Set the `DATABASE_URL` environment variable:
   ```bash
   DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/leads_db
   ```
3. Start the server. The application automatically initializes tables upon startup via SQLAlchemy 2.0 DeclarativeBase metadata.

---

## 20. Limitations & Production Notes
- **Authentication**: Intentionally omitted per portfolio specification to keep the architecture accessible for demonstration. In production, protect endpoints with API keys, HMAC webhook signatures (e.g., Shopify HMAC), or OAuth2.
- **Background Worker**: In this single-process service, API enrichment is performed synchronously with exponential backoff. For high-volume scenarios (>1,000 req/sec), offload external HTTP enrichment to a background task queue.
- **Rate Limiting**: For public-facing webhooks, place reverse proxies (Nginx/Cloudflare) or FastAPI rate limiters (`slowapi`) in front of `/webhooks/leads`.
