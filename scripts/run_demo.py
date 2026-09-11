"""Portfolio demonstration script for Python Webhook & API Automation Service.

Executes a full end-to-end demonstration against a running API instance:
1. Verifies health endpoint
2. Ingests valid lead
3. Tests duplicate detection with whitespace/case variation
4. Tests error handling with a malformed payload
5. Ingests additional diverse leads across multiple channels
6. Queries paginated leads list
7. Queries processing statistics
8. Downloads CSV and formatted Excel exports to exports/
"""

import json
from pathlib import Path

import httpx

BASE_URL = "http://127.0.0.1:8000"
EXPORTS_DIR = Path("exports")
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
PAYLOADS_DIR = Path("sample_payloads")


def print_step(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def main() -> None:
    print("\nStarting Lead Intake & API Automation Service Demo...")
    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    # 1. Health check
    print_step("1. Health Check")
    try:
        res = client.get("/health")
        print(f"GET /health -> HTTP {res.status_code}")
        print(f"Response: {res.json()}")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    except httpx.ConnectError:
        print("\n[ERROR] Could not connect to service at http://127.0.0.1:8000")
        print(
            "Please start the server first with: "
            "uvicorn app.main:app --host 127.0.0.1 --port 8000"
        )
        return

    # 2. Ingest valid lead
    print_step("2. Ingest Valid Lead (First Time)")
    with open(PAYLOADS_DIR / "valid_lead.json", encoding="utf-8") as f:
        valid_payload = json.load(f)
    res = client.post("/webhooks/leads", json=valid_payload)
    print(f"POST /webhooks/leads -> HTTP {res.status_code}")
    print(f"Response: {json.dumps(res.json(), indent=2)}")

    # 3. Test duplicate detection
    print_step("3. Test Duplicate Detection (Whitespace & Casing Variations)")
    with open(PAYLOADS_DIR / "duplicate_lead.json", encoding="utf-8") as f:
        duplicate_payload = json.load(f)
    res = client.post("/webhooks/leads", json=duplicate_payload)
    print(f"POST /webhooks/leads -> HTTP {res.status_code}")
    print(f"Response: {json.dumps(res.json(), indent=2)}")
    assert res.status_code == 200, "Expected HTTP 200 for duplicate lead"
    assert res.json().get("status") == "duplicate", "Expected status 'duplicate'"

    # 4. Test validation error handling
    print_step("4. Test Malformed Payload Handling")
    with open(PAYLOADS_DIR / "malformed_lead.json", encoding="utf-8") as f:
        malformed_payload = json.load(f)
    res = client.post("/webhooks/leads", json=malformed_payload)
    print(f"POST /webhooks/leads (Invalid Email) -> HTTP {res.status_code}")
    print(f"Graceful error response: {json.dumps(res.json(), indent=2)}")
    assert res.status_code == 422, "Expected HTTP 422 for invalid email"

    # 5. Ingest additional leads
    print_step("5. Ingest Additional Leads from Different Sources")
    additional_leads = [
        {"name": "Bob Miller", "email": "bob.miller@company.org"},
        {
            "external_id": "shopify-9901",
            "name": "Alice Cooper",
            "email": "alice@coopertech.io",
            "company": "Cooper Tech",
            "source": "Shopify",
            "notes": "Interested in enterprise plan",
        },
        {
            "external_id": "fb-4412",
            "name": "David Zhang",
            "email": "david.zhang@growth.co",
            "company": "Growth Co",
            "source": "Facebook",
            "notes": "Ad campaign inquiry",
        },
    ]

    for lead_data in additional_leads:
        res = client.post("/webhooks/leads", json=lead_data)
        source_label = lead_data.get("source", "unknown")
        print(f"POST Lead ({lead_data['name']} / {source_label}) -> HTTP {res.status_code}")
        print(f"Response: {res.json()}")

    # 6. Fetch paginated leads list
    print_step("6. Fetch Leads via REST API")
    res = client.get("/api/leads?page=1&page_size=10")
    print(f"GET /api/leads -> HTTP {res.status_code}")
    leads_data = res.json()
    print(f"Total leads stored: {leads_data['total']}")
    print(f"Fetched {len(leads_data['items'])} items on page 1:")
    for item in leads_data["items"][:5]:
        print(
            f"  - [{item['id']}] {item['name']} ({item['email']}) "
            f"| Source: {item['source']} | Status: {item['enrichment_status']} "
            f"| Score: {item['enrichment_score']} | Segment: {item['enrichment_segment']}"
        )

    # 7. Fetch processing statistics
    print_step("7. Fetch Processing Statistics")
    res = client.get("/api/stats")
    print(f"GET /api/stats -> HTTP {res.status_code}")
    stats_data = res.json()
    print(json.dumps(stats_data, indent=2))

    # 8. Export CSV
    print_step("8. Download CSV Export")
    res = client.get("/api/export/csv")
    csv_file = EXPORTS_DIR / "leads_export.csv"
    csv_file.write_bytes(res.content)
    print(f"GET /api/export/csv -> HTTP {res.status_code} ({len(res.content)} bytes)")
    print(f"Saved CSV export to: {csv_file.resolve()}")

    # 9. Export Excel
    print_step("9. Download Formatted Excel Export")
    res = client.get("/api/export/excel")
    excel_file = EXPORTS_DIR / "leads_export.xlsx"
    excel_file.write_bytes(res.content)
    print(f"GET /api/export/excel -> HTTP {res.status_code} ({len(res.content)} bytes)")
    print(f"Saved Excel export to: {excel_file.resolve()}")

    print_step("Demo Completed Successfully")
    print("All endpoints verified. Reports generated in exports/ directory.\n")


if __name__ == "__main__":
    main()
