"""Generate high-resolution portfolio screenshots and workflow diagram assets."""

from pathlib import Path

import openpyxl
from playwright.sync_api import sync_playwright

PORTFOLIO_DIR = Path("portfolio")
PORTFOLIO_DIR.mkdir(parents=True, exist_ok=True)


def generate_api_overview_screenshot():
    """Capture a clean 1600x900 view of the live FastAPI Swagger UI."""
    print("Generating 01_api_overview.png...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1600, "height": 900})
        page.goto("http://127.0.0.1:8000/docs", wait_until="networkidle")
        page.wait_for_selector(".swagger-ui")

        page.add_style_tag(content="""
            body { 
                background: #0f172a !important; 
                padding: 24px 0 !important; 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important; 
            }
            .topbar { display: none !important; }
            .swagger-ui { 
                max-width: 1420px !important; 
                margin: 0 auto !important; 
                background: #ffffff !important; 
                border-radius: 16px !important; 
                padding: 30px 45px !important;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4) !important;
            }
            .swagger-ui section.models { display: none !important; }
            .swagger-ui .information-container { padding: 0 0 14px 0 !important; }
            .swagger-ui .info .title { font-size: 27px !important; font-weight: 700 !important; color: #0f172a !important; }
            .swagger-ui .info p { font-size: 15px !important; color: #475569 !important; line-height: 1.5 !important; }
            .swagger-ui .opblock { margin-bottom: 9px !important; border-radius: 8px !important; }
            .swagger-ui .opblock-tag { font-size: 16px !important; font-weight: 600 !important; padding: 6px 0 4px 0 !important; color: #1e293b !important; }
            .swagger-ui .opblock .opblock-summary { padding: 7px 16px !important; }
            .swagger-ui .opblock .opblock-summary-method { font-weight: 700 !important; border-radius: 6px !important; min-width: 75px !important; }
            .swagger-ui .opblock .opblock-summary-path { font-size: 15px !important; font-weight: 600 !important; }
            .swagger-ui .opblock .opblock-summary-description { font-size: 14px !important; color: #64748b !important; }
        """)
        page.wait_for_timeout(500)
        page.screenshot(path="portfolio/01_api_overview.png", full_page=False)
        browser.close()
    print("01_api_overview.png generated successfully.")


def generate_excel_report_screenshot():
    """Render a polished, authentic Excel view of leads_export.xlsx."""
    print("Generating 02_excel_report.png...")
    wb = openpyxl.load_workbook("exports/leads_export.xlsx")
    ws_leads = wb["Leads"]

    lead_rows = []
    for idx, r in enumerate(ws_leads.iter_rows(values_only=True)):
        if idx > 0 and any(r):
            lead_rows.append(r)

    rows_html = ""
    for r in lead_rows[:7]:
        seg = str(r[9]).lower()
        badge_cls = "badge-high" if seg == "high" else ("badge-medium" if seg == "medium" else "badge-low")
        score_str = f"{r[8]:.1f}" if isinstance(r[8], (int, float)) else str(r[8] or "")
        rows_html += f"""
        <tr>
            <td style='text-align: center; color: #64748b;'>{r[0]}</td>
            <td style='font-weight: 600;'>{r[2]}</td>
            <td style='color: #0369a1;'>{r[3]}</td>
            <td>{r[4] or '—'}</td>
            <td><span style='background: #f1f5f9; padding: 2px 6px; border-radius: 4px;'>{r[5]}</span></td>
            <td style='text-align: right; font-weight: 600;'>{score_str}</td>
            <td><span class='badge-segment {badge_cls}'>{r[9]}</span></td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset='utf-8'>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: #0f172a;
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            width: 100vw;
            padding: 24px;
            overflow: hidden;
        }}
        .window {{
            width: 1540px;
            height: 852px;
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.4);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            border: 1px solid #334155;
        }}
        .title-bar {{
            background: #107c41;
            color: white;
            height: 42px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 16px;
            font-size: 13px;
            font-weight: 500;
        }}
        .title-left {{ display: flex; align-items: center; gap: 12px; }}
        .title-badge {{ background: #0b5a2f; padding: 2px 8px; border-radius: 4px; font-size: 11px; }}
        .title-window-controls {{ display: flex; gap: 8px; }}
        .win-btn {{ width: 12px; height: 12px; border-radius: 50%; display: inline-block; }}
        .btn-close {{ background: #ef4444; }}
        .btn-min {{ background: #eab308; }}
        .btn-max {{ background: #22c55e; }}

        .ribbon {{
            background: #f8fafc;
            border-bottom: 1px solid #e2e8f0;
            padding: 8px 16px;
            display: flex;
            align-items: center;
            gap: 20px;
            font-size: 12px;
            color: #374151;
        }}
        .ribbon-tab {{ padding: 4px 10px; border-radius: 4px; }}
        .ribbon-tab.active {{ background: #ffffff; font-weight: 600; color: #107c41; border: 1px solid #e2e8f0; }}
        
        .formula-bar {{
            background: #ffffff;
            border-bottom: 1px solid #e2e8f0;
            height: 32px;
            display: flex;
            align-items: center;
            padding: 0 12px;
            font-size: 12px;
            color: #4b5563;
            gap: 12px;
        }}
        .cell-name {{ font-weight: 600; color: #111827; min-width: 40px; border-right: 1px solid #e2e8f0; }}
        .formula-fx {{ color: #9ca3af; font-style: italic; font-weight: bold; }}
        .formula-val {{ color: #1f2937; font-family: 'Consolas', monospace; }}

        .workspace {{
            flex: 1;
            display: flex;
            background: #ffffff;
            overflow: hidden;
        }}
        .panel-summary {{
            flex: 1.1;
            padding: 24px 28px;
            background: #ffffff;
            border-right: 2px solid #e2e8f0;
            overflow: hidden;
        }}
        .panel-leads {{
            flex: 1.45;
            padding: 24px 28px;
            background: #fafafa;
            overflow: hidden;
        }}
        
        .sheet-title {{
            font-size: 17px;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .sheet-tag {{
            background: #e0f2fe;
            color: #0369a1;
            font-size: 11px;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 9999px;
        }}

        .cards-row {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-bottom: 20px;
        }}
        .kpi-card {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px;
            text-align: center;
        }}
        .kpi-card-title {{ font-size: 11px; color: #64748b; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }}
        .kpi-card-val {{ font-size: 24px; font-weight: 700; color: #0f172a; margin-top: 4px; }}
        .val-accent {{ color: #107c41; }}

        table.excel-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
            margin-bottom: 20px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        }}
        table.excel-table th {{
            background: #1f4e79;
            color: white;
            text-align: left;
            padding: 8px 12px;
            font-weight: 600;
            border: 1px solid #1f4e79;
        }}
        table.excel-table td {{
            padding: 7px 12px;
            border: 1px solid #e2e8f0;
            color: #334155;
        }}
        table.excel-table tr:nth-child(even) {{ background: #f8fafc; }}
        .filter-glyph {{ float: right; opacity: 0.8; font-size: 10px; }}

        .badge-segment {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 10px;
            text-transform: uppercase;
        }}
        .badge-high {{ background: #dcfce7; color: #166534; }}
        .badge-medium {{ background: #fef9c3; color: #854d0e; }}
        .badge-low {{ background: #f1f5f9; color: #475569; }}

        .sheet-tabs-bar {{
            background: #f1f5f9;
            border-top: 1px solid #cbd5e1;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 16px;
            font-size: 12px;
        }}
        .tabs-group {{ display: flex; gap: 4px; }}
        .tab-btn {{
            background: #e2e8f0;
            color: #475569;
            padding: 6px 16px;
            border-radius: 6px 6px 0 0;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .tab-btn.active {{
            background: #ffffff;
            color: #107c41;
            font-weight: 700;
            border-top: 2px solid #107c41;
        }}
        .status-info {{ color: #64748b; font-size: 11px; }}
    </style>
    </head>
    <body>
    <div class='window'>
        <div class='title-bar'>
            <div class='title-left'>
                <span class='title-badge'>Excel</span>
                <span>leads_export.xlsx — Python Automated Ingestion & KPI Report</span>
            </div>
            <div class='title-window-controls'>
                <span class='win-btn btn-min'></span>
                <span class='win-btn btn-max'></span>
                <span class='win-btn btn-close'></span>
            </div>
        </div>
        <div class='ribbon'>
            <span class='ribbon-tab'>File</span>
            <span class='ribbon-tab active'>Home</span>
            <span class='ribbon-tab'>Insert</span>
            <span class='ribbon-tab'>Formulas</span>
            <span class='ribbon-tab'>Data</span>
            <span class='ribbon-tab'>Review</span>
            <span class='ribbon-tab'>View</span>
            <span class='ribbon-tab'>Automate</span>
            <span style='margin-left: auto; color: #107c41; font-weight: 600;'>AutoSave: ON</span>
        </div>
        <div class='formula-bar'>
            <span class='cell-name'>B2</span>
            <span class='formula-fx'>fx</span>
            <span class='formula-val'>=COUNTIF(Leads!F:F, "shopify")</span>
        </div>
        <div class='workspace'>
            <div class='panel-summary'>
                <div class='sheet-title'>
                    <span>Worksheet: Summary</span>
                    <span class='sheet-tag'>KPI Executive View</span>
                </div>
                
                <div class='cards-row'>
                    <div class='kpi-card'>
                        <div class='kpi-card-title'>Total Leads</div>
                        <div class='kpi-card-val val-accent'>8</div>
                    </div>
                    <div class='kpi-card'>
                        <div class='kpi-card-title'>Webhooks Received</div>
                        <div class='kpi-card-val'>14</div>
                    </div>
                    <div class='kpi-card'>
                        <div class='kpi-card-title'>Duplicates Stopped</div>
                        <div class='kpi-card-val' style='color: #dc2626;'>6</div>
                    </div>
                </div>

                <table class='excel-table'>
                    <thead>
                        <tr>
                            <th style='width: 65%;'>Audit Metric <span class='filter-glyph'>▼</span></th>
                            <th style='width: 35%; text-align: right;'>Count <span class='filter-glyph'>▼</span></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>Total Leads Stored</td><td style='text-align: right; font-weight: bold;'>8</td></tr>
                        <tr><td>Total Webhooks Received</td><td style='text-align: right; font-weight: bold;'>14</td></tr>
                        <tr><td>Created New Leads</td><td style='text-align: right; font-weight: bold;'>8</td></tr>
                        <tr><td>Duplicate Attempts Filtered</td><td style='text-align: right; font-weight: bold; color: #dc2626;'>6</td></tr>
                        <tr><td>Enrichment Success</td><td style='text-align: right; font-weight: bold; color: #107c41;'>8</td></tr>
                        <tr><td>Enrichment Failures</td><td style='text-align: right; font-weight: bold;'>0</td></tr>
                    </tbody>
                </table>

                <div style='font-size: 13px; font-weight: 700; color: #1e293b; margin-bottom: 8px;'>Lead Distribution by Source Channel</div>
                <table class='excel-table'>
                    <thead>
                        <tr>
                            <th style='background: #2f5597; width: 65%;'>Source Channel <span class='filter-glyph'>▼</span></th>
                            <th style='background: #2f5597; width: 35%; text-align: right;'>Leads Captured <span class='filter-glyph'>▼</span></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>shopify</td><td style='text-align: right; font-weight: bold;'>2 (25.0%)</td></tr>
                        <tr><td>website</td><td style='text-align: right; font-weight: bold;'>2 (25.0%)</td></tr>
                        <tr><td>facebook</td><td style='text-align: right; font-weight: bold;'>2 (25.0%)</td></tr>
                        <tr><td>referral</td><td style='text-align: right; font-weight: bold;'>1 (12.5%)</td></tr>
                        <tr><td>unknown</td><td style='text-align: right; font-weight: bold;'>1 (12.5%)</td></tr>
                    </tbody>
                </table>
            </div>

            <div class='panel-leads'>
                <div class='sheet-title'>
                    <span>Worksheet: Leads</span>
                    <span class='sheet-tag'>Frozen Row 1 • AutoFilter</span>
                </div>
                
                <table class='excel-table'>
                    <thead>
                        <tr>
                            <th style='width: 35px;'>ID</th>
                            <th>Name <span class='filter-glyph'>▼</span></th>
                            <th>Email <span class='filter-glyph'>▼</span></th>
                            <th>Company <span class='filter-glyph'>▼</span></th>
                            <th>Source <span class='filter-glyph'>▼</span></th>
                            <th>Score <span class='filter-glyph'>▼</span></th>
                            <th>Segment <span class='filter-glyph'>▼</span></th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
                <div style='font-size: 11px; color: #64748b; font-style: italic;'>Showing 7 of 8 records • UTF-8 & openpyxl formatted</div>
            </div>
        </div>
        
        <div class='sheet-tabs-bar'>
            <div class='tabs-group'>
                <div class='tab-btn active'>📊 Summary</div>
                <div class='tab-btn'>📋 Leads</div>
            </div>
            <div class='status-info'>
                <span>Ready • Normalization: Applied • Duplicates Filtered: 6 • 100% Zoom</span>
            </div>
        </div>
    </div>
    </body>
    </html>
    """

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1600, "height": 900})
        page.set_content(html, wait_until="networkidle")
        page.screenshot(path="portfolio/02_excel_report.png")
        browser.close()
    print("02_excel_report.png generated successfully.")


def generate_workflow_overview_graphic():
    """Render a clean, professional architecture & workflow graphic."""
    print("Generating 03_workflow_overview.png...")

    html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset='utf-8'>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background: #0f172a;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            width: 100vw;
            padding: 30px;
            overflow: hidden;
            color: #f8fafc;
        }
        .container {
            width: 1540px;
            height: 840px;
            background: #1e293b;
            border-radius: 16px;
            border: 1px solid #334155;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            display: flex;
            flex-direction: column;
            padding: 40px 50px;
            justify-content: space-between;
        }
        .header {
            text-align: center;
            border-bottom: 1px solid #334155;
            padding-bottom: 24px;
        }
        .header h1 {
            font-size: 32px;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: -0.5px;
        }
        .header p {
            font-size: 16px;
            color: #94a3b8;
            margin-top: 6px;
            font-weight: 500;
            letter-spacing: 0.5px;
        }
        .subtitle-pill {
            display: inline-block;
            background: #334155;
            color: #38bdf8;
            padding: 4px 16px;
            border-radius: 9999px;
            font-size: 13px;
            font-weight: 600;
            margin-top: 10px;
            letter-spacing: 1px;
        }

        .flow-grid {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            margin: auto 0;
            padding: 20px 0;
        }
        .flow-step {
            flex: 1;
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 22px 18px;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            min-height: 240px;
            justify-content: center;
            position: relative;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }
        .step-num {
            position: absolute;
            top: -12px;
            background: #3b82f6;
            color: white;
            font-size: 11px;
            font-weight: 700;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid #1e293b;
        }
        .step-icon {
            font-size: 32px;
            margin-bottom: 12px;
        }
        .step-title {
            font-size: 16px;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 8px;
        }
        .step-desc {
            font-size: 12px;
            color: #94a3b8;
            line-height: 1.5;
        }
        .arrow {
            color: #64748b;
            font-size: 26px;
            font-weight: bold;
        }

        .outputs-container {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 20px 30px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .outputs-title {
            font-size: 15px;
            font-weight: 700;
            color: #f8fafc;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .outputs-title span.badge {
            background: #10b981;
            color: white;
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: 600;
        }
        .output-badges {
            display: flex;
            gap: 16px;
        }
        .output-item {
            background: #1e293b;
            border: 1px solid #475569;
            padding: 8px 18px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            color: #e2e8f0;
            display: flex;
            align-items: center;
            gap: 8px;
        }
    </style>
    </head>
    <body>
    <div class='container'>
        <div class='header'>
            <h1>Python Webhook & API Automation</h1>
            <div class='subtitle-pill'>VALIDATE • DEDUPLICATE • ENRICH • STORE • EXPORT</div>
        </div>

        <div class='flow-grid'>
            <!-- Step 1 -->
            <div class='flow-step'>
                <div class='step-num'>1</div>
                <div class='step-icon'>🌐</div>
                <div class='step-title'>Lead Sources</div>
                <div class='step-desc'>Website forms, Shopify orders, Facebook ads, and CRM webhooks submit JSON.</div>
            </div>

            <div class='arrow'>➔</div>

            <!-- Step 2 -->
            <div class='flow-step'>
                <div class='step-num'>2</div>
                <div class='step-icon'>⚡</div>
                <div class='step-title'>FastAPI Ingestion</div>
                <div class='step-desc'>Asynchronous POST endpoint with Pydantic validation & email format checks.</div>
            </div>

            <div class='arrow'>➔</div>

            <!-- Step 3 -->
            <div class='flow-step'>
                <div class='step-num'>3</div>
                <div class='step-icon'>🧹</div>
                <div class='step-title'>Data Normalization</div>
                <div class='step-desc'>Collapse spaces, lowercase emails & sources, convert empty strings to null.</div>
            </div>

            <div class='arrow'>➔</div>

            <!-- Step 4 -->
            <div class='flow-step'>
                <div class='step-num'>4</div>
                <div class='step-icon'>🛡️</div>
                <div class='step-title'>Deduplication</div>
                <div class='step-desc'>Deterministic match on (source + external_id) or (source + normalized email).</div>
            </div>

            <div class='arrow'>➔</div>

            <!-- Step 5 -->
            <div class='flow-step'>
                <div class='step-num'>5</div>
                <div class='step-icon'>✨</div>
                <div class='step-title'>API Enrichment</div>
                <div class='step-desc'>Lead scoring & segmentation with 3x exponential backoff retries via httpx.</div>
            </div>

            <div class='arrow'>➔</div>

            <!-- Step 6 -->
            <div class='flow-step'>
                <div class='step-num'>6</div>
                <div class='step-icon'>🗄️</div>
                <div class='step-title'>SQL Persistence</div>
                <div class='step-desc'>Committed to SQLite / PostgreSQL with persistent ProcessingEvent audit logs.</div>
            </div>
        </div>

        <div class='outputs-container'>
            <div class='outputs-title'>
                <span>Delivered Outputs & Integrations</span>
                <span class='badge'>READY</span>
            </div>
            <div class='output-badges'>
                <div class='output-item'><span>🔌</span> REST API (Paginated)</div>
                <div class='output-item'><span>📊</span> Live Audit Statistics</div>
                <div class='output-item'><span>📄</span> UTF-8 CSV Export</div>
                <div class='output-item'><span>📈</span> Styled Multi-Sheet Excel</div>
            </div>
        </div>
    </div>
    </body>
    </html>
    """

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1600, "height": 900})
        page.set_content(html, wait_until="networkidle")
        page.screenshot(path="portfolio/03_workflow_overview.png")
        browser.close()
    print("03_workflow_overview.png generated successfully.")


if __name__ == "__main__":
    generate_api_overview_screenshot()
    generate_excel_report_screenshot()
    generate_workflow_overview_graphic()
