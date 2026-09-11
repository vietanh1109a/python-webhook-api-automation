"""Generate high-resolution portfolio screenshots and workflow diagram assets."""

import ctypes
import time
from pathlib import Path

from PIL import Image
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

        page.add_style_tag(
            content="""
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
        """
        )
        page.wait_for_timeout(500)
        page.screenshot(path="portfolio/01_api_overview.png", full_page=False)
        browser.close()
    print("01_api_overview.png generated successfully.")


def generate_excel_report_screenshot():
    """Capture real Microsoft Excel application screenshot of leads_export.xlsx."""
    print("Capturing 02_excel_report.png using Microsoft Excel...")
    excel_path = Path("exports/leads_export.xlsx").resolve()
    if not excel_path.exists():
        print("Warning: exports/leads_export.xlsx not found. Run scripts/run_demo.py first.")
        return

    try:
        import win32com.client
        import win32con
        import win32gui
        import win32ui

        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = True
        excel.WindowState = win32con.SW_MAXIMIZE
        wb = excel.Workbooks.Open(str(excel_path))
        try:
            ws = wb.Sheets("Summary")
            ws.Activate()
            time.sleep(1.5)

            hwnd = win32gui.FindWindow("XLMAIN", None)
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 1600, 900, 0)
            time.sleep(1.0)

            left, top, right, bot = win32gui.GetWindowRect(hwnd)
            w = right - left
            h = bot - top

            hwnd_dc = win32gui.GetWindowDC(hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()
            save_bitmap = win32ui.CreateBitmap()
            save_bitmap.CreateCompatibleBitmap(mfc_dc, w, h)
            save_dc.SelectObject(save_bitmap)

            ctypes.windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 2)

            bmp_info = save_bitmap.GetInfo()
            bmp_str = save_bitmap.GetBitmapBits(True)
            img = Image.frombuffer(
                "RGB",
                (bmp_info["bmWidth"], bmp_info["bmHeight"]),
                bmp_str,
                "raw",
                "BGRX",
                0,
                1,
            )

            img.save("portfolio/02_excel_report.png")
            print("02_excel_report.png captured from Microsoft Excel successfully.")

            win32gui.DeleteObject(save_bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)
        finally:
            wb.Close(False)
            excel.Quit()

    except Exception as exc:
        print(
            f"Notice: Could not capture via Microsoft Excel ({exc}). Preserving existing 02_excel_report.png."
        )


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
