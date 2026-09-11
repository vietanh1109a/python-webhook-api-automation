# Python Webhook & API Automation Service

## Business Problem

Businesses often receive customer or lead data from multiple forms, platforms, or CRMs. Manual spreadsheet copying creates duplicates, formatting inconsistencies, and repetitive work.

## Solution

This project demonstrates a reusable Python automation workflow that:

- receives JSON webhooks
- validates and normalizes records
- prevents duplicate entries
- optionally calls external APIs
- stores clean data in SQL
- provides REST API access
- generates statistics
- exports CSV and formatted Excel files

## Technology

- **Python 3.12**
- **FastAPI**
- **SQLAlchemy 2.x**
- **pandas**
- **httpx**
- **SQLite / PostgreSQL support**
- **openpyxl**
- **pytest**

## Reliability

- **Deterministic deduplication**: Prevents duplicate database records based on source and external ID or email.
- **Input validation**: Enforces RFC-compliant email and schema constraints via Pydantic v2.
- **Retry/backoff handling**: 3-attempt exponential backoff retries on transient external API failures.
- **Timeout handling**: Configurable network timeout guards prevent hanging processes.
- **Persistent processing events**: Durable event logging table maintains audit metrics across reboots.
- **Automated tests**: Comprehensive test suite covering normalization, deduplication, HTTP mocking, and exports.
- **Safe configuration**: 12-factor environment variable management with zero secrets stored in code.

## Example Use Cases

- website lead intake
- CRM data synchronization
- Shopify/customer imports
- marketing lead processing
- form submission automation
- recurring business data workflows

## Testing

The project includes an automated test suite executed via `pytest`. All 28 tests pass consistently with zero failures and zero warnings, validating input normalization, deduplication, error handling, mock HTTP enrichment, and multi-sheet Excel generation.
