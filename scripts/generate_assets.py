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
    """Render a clean, high-contrast, thumbnail-optimized architecture & workflow cover."""
    print("Generating 03_workflow_overview.png...")

    html = """<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        background: #080c14;
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
        background: #0f172a;
        border-radius: 20px;
        border: 1.5px solid #223249;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 42px 48px 30px 48px;
    }
    .header {
        text-align: center;
    }
    .header h1 {
        font-size: 52px;
        font-weight: 900;
        color: #ffffff;
        letter-spacing: -0.5px;
    }
    .header .subtitle {
        font-size: 22px;
        color: #38bdf8;
        font-weight: 700;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-top: 8px;
    }

    .workflow-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        margin: 18px 0;
    }
    .card {
        flex: 1;
        background: #172439;
        border: 2px solid #283e5e;
        border-radius: 18px;
        padding: 32px 18px;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        height: 380px;
        justify-content: space-between;
        box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.4);
    }
    .step-tag {
        font-size: 14px;
        font-weight: 800;
        letter-spacing: 1.5px;
        color: #38bdf8;
        background: rgba(56, 189, 248, 0.15);
        border: 1.5px solid rgba(56, 189, 248, 0.4);
        padding: 6px 18px;
        border-radius: 9999px;
        text-transform: uppercase;
    }
    .card-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 4px 0;
    }
    .card-title {
        font-size: 28px;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.2;
    }
    .card-sub {
        font-size: 18px;
        font-weight: 600;
        color: #e2e8f0;
        line-height: 1.4;
        background: rgba(8, 14, 26, 0.75);
        border: 1.5px solid #2a4163;
        padding: 12px 14px;
        border-radius: 10px;
        width: 100%;
    }
    .arrow {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    .footer {
        text-align: center;
        padding-top: 18px;
        border-top: 1px solid #1e293b;
    }
    .footer-text {
        font-size: 22px;
        font-weight: 700;
        color: #94a3b8;
        letter-spacing: 2.5px;
    }
</style>
</head>
<body>
<div class='container'>
    <div class='header'>
        <h1>Python Webhook & API Automation</h1>
        <div class='subtitle'>Validate • Deduplicate • Process • Export</div>
    </div>

    <div class='workflow-row'>
        <!-- Card 1 -->
        <div class='card'>
            <div class='step-tag'>Step 1</div>
            <div class='card-icon'>
                <svg width='58' height='58' viewBox='0 0 24 24' fill='none' stroke='#38bdf8' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'>
                    <circle cx='18' cy='5' r='3'></circle>
                    <circle cx='6' cy='12' r='3'></circle>
                    <circle cx='18' cy='19' r='3'></circle>
                    <line x1='8.59' y1='13.51' x2='15.42' y2='17.49'></line>
                    <line x1='15.41' y1='6.51' x2='8.59' y2='10.49'></line>
                </svg>
            </div>
            <div class='card-title'>Webhook Input</div>
            <div class='card-sub'>Forms • CRM • Shopify</div>
        </div>

        <div class='arrow'>
            <svg width='46' height='46' viewBox='0 0 24 24' fill='none' stroke='#94a3b8' stroke-width='2.8' stroke-linecap='round' stroke-linejoin='round'>
                <line x1='5' y1='12' x2='19' y2='12'></line>
                <polyline points='12 5 19 12 12 19'></polyline>
            </svg>
        </div>

        <!-- Card 2 -->
        <div class='card'>
            <div class='step-tag'>Step 2</div>
            <div class='card-icon'>
                <svg width='58' height='58' viewBox='0 0 24 24' fill='none' stroke='#38bdf8' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'>
                    <path d='M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'></path>
                    <polyline points='9 12 11 14 15 10'></polyline>
                </svg>
            </div>
            <div class='card-title'>Clean & Deduplicate</div>
            <div class='card-sub'>Validate • Normalize • Prevent duplicates</div>
        </div>

        <div class='arrow'>
            <svg width='46' height='46' viewBox='0 0 24 24' fill='none' stroke='#94a3b8' stroke-width='2.8' stroke-linecap='round' stroke-linejoin='round'>
                <line x1='5' y1='12' x2='19' y2='12'></line>
                <polyline points='12 5 19 12 12 19'></polyline>
            </svg>
        </div>

        <!-- Card 3 -->
        <div class='card'>
            <div class='step-tag'>Step 3</div>
            <div class='card-icon'>
                <svg width='58' height='58' viewBox='0 0 24 24' fill='none' stroke='#38bdf8' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'>
                    <ellipse cx='12' cy='5' rx='9' ry='3'></ellipse>
                    <path d='M21 12c0 1.66-4 3-9 3s-9-1.34-9-3'></path>
                    <path d='M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5'></path>
                </svg>
            </div>
            <div class='card-title'>API + SQL</div>
            <div class='card-sub'>FastAPI • API Integration • Database</div>
        </div>

        <div class='arrow'>
            <svg width='46' height='46' viewBox='0 0 24 24' fill='none' stroke='#94a3b8' stroke-width='2.8' stroke-linecap='round' stroke-linejoin='round'>
                <line x1='5' y1='12' x2='19' y2='12'></line>
                <polyline points='12 5 19 12 12 19'></polyline>
            </svg>
        </div>

        <!-- Card 4 -->
        <div class='card'>
            <div class='step-tag'>Step 4</div>
            <div class='card-icon'>
                <svg width='58' height='58' viewBox='0 0 24 24' fill='none' stroke='#38bdf8' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'>
                    <rect x='3' y='3' width='18' height='18' rx='2' ry='2'></rect>
                    <line x1='3' y1='9' x2='21' y2='9'></line>
                    <line x1='3' y1='15' x2='21' y2='15'></line>
                    <line x1='9' y1='3' x2='9' y2='21'></line>
                    <line x1='15' y1='3' x2='15' y2='21'></line>
                </svg>
            </div>
            <div class='card-title'>Business Outputs</div>
            <div class='card-sub'>REST API • CSV • Excel</div>
        </div>
    </div>

    <div class='footer'>
        <div class='footer-text'>Python &nbsp;•&nbsp; FastAPI &nbsp;•&nbsp; SQLAlchemy &nbsp;•&nbsp; pandas &nbsp;•&nbsp; Excel</div>
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
