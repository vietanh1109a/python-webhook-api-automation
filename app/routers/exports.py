"""Data export endpoints for CSV and Excel files."""

import logging

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.exporters import export_leads_csv, export_leads_excel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/export", tags=["Exports"])


@router.get("/csv")
def export_csv(db: Session = Depends(get_db)) -> Response:
    """Export all leads as a downloadable UTF-8 CSV file."""
    csv_bytes = export_leads_csv(db)
    logger.info("Generated CSV export (%d bytes)", len(csv_bytes))
    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="leads_export.csv"'},
    )


@router.get("/excel")
def export_excel(db: Session = Depends(get_db)) -> Response:
    """Export leads and a statistical summary as a styled multi-sheet Excel file."""
    excel_bytes = export_leads_excel(db)
    logger.info("Generated Excel export (%d bytes)", len(excel_bytes))
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="leads_export.xlsx"'},
    )
