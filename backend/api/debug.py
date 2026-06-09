from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from core.database import get_db
from models.database import (
    Workbook, ExecutiveSummary, DailyPerformance, 
    CategoryPerformance, OfferingPerformance, 
    BatchPerformance, LeaderPerformance
)
from services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/db-state")
def get_db_state(db: Session = Depends(get_db)):
    """Returns row counts for all key analytics tables in the SQLite database."""
    counts = {
        "workbooks": db.query(func.count()).select_from(Workbook).scalar(),
        "executive_summary": db.query(func.count()).select_from(ExecutiveSummary).scalar(),
        "daily_performance": db.query(func.count()).select_from(DailyPerformance).scalar(),
        "category_performance": db.query(func.count()).select_from(CategoryPerformance).scalar(),
        "offering_performance": db.query(func.count()).select_from(OfferingPerformance).scalar(),
        "batch_performance": db.query(func.count()).select_from(BatchPerformance).scalar(),
        "leader_performance": db.query(func.count()).select_from(LeaderPerformance).scalar()
    }
    return counts

@router.get("/upload-status")
def get_upload_status(db: Session = Depends(get_db)):
    """Returns permanent diagnostics including latest workbook info and parser output equivalents."""
    from sqlalchemy import desc
    latest_wb = db.query(Workbook).order_by(desc(Workbook.upload_date)).first()
    
    wb_info = None
    if latest_wb:
        wb_info = {
            "id": str(latest_wb.id),
            "filename": latest_wb.filename,
            "upload_date": latest_wb.upload_date.isoformat(),
            "status": latest_wb.status
        }
        
    counts = get_db_state(db)
    
    latest_kpis = AnalyticsService.get_kpis(db) if latest_wb else {}
    
    return {
        "latest_workbook": wb_info,
        "table_counts": counts,
        "latest_kpis": latest_kpis
    }
