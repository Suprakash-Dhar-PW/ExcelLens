from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from core.database import get_db
from models.database import Workbook, ExecutiveSummary, DailyPerformance, CategoryPerformance, OfferingPerformance, BatchPerformance, LeaderPerformance

router = APIRouter()

@router.get("/db-state")
def get_db_state(db: Session = Depends(get_db)):
    """Returns exact table counts and the latest workbook ID."""
    latest_wb = db.query(Workbook).order_by(Workbook.upload_date.desc()).first()
    
    counts = {
        "workbooks": db.query(Workbook).count(),
        "executive_summary": db.query(ExecutiveSummary).count(),
        "daily_performance": db.query(DailyPerformance).count(),
        "category_performance": db.query(CategoryPerformance).count(),
        "offering_performance": db.query(OfferingPerformance).count(),
        "batch_performance": db.query(BatchPerformance).count(),
        "leader_performance": db.query(LeaderPerformance).count()
    }
    
    return {
        "status": "ok",
        "latest_workbook_id": latest_wb.id if latest_wb else None,
        "table_counts": counts
    }

@router.get("/upload-status")
def get_upload_status(db: Session = Depends(get_db)):
    """Check the status of the most recent upload."""
    latest_wb = db.query(Workbook).order_by(Workbook.upload_date.desc()).first()
    if not latest_wb:
        return {"status": "no_workbooks"}
        
    return {
        "workbook_id": latest_wb.id,
        "filename": latest_wb.filename,
        "upload_date": latest_wb.upload_date,
        "status": latest_wb.status
    }

@router.get("/parser-test")
def get_parser_test():
    """Returns the expected mappings for the parser to aid debugging."""
    return {
        "DOD View": "daily_performance",
        "Leader Performance": "leader_performance",
        "MTD Offerings": "offering_performance",
        "YTD Offerings": "offering_performance",
        "Top Categories": "category_performance",
        "Bottom Categories": "category_performance"
    }

@router.get("/dashboard-data")
def get_dashboard_data(db: Session = Depends(get_db)):
    """Raw dump of all metrics for the latest workbook without analytics aggregation."""
    latest_wb = db.query(Workbook).order_by(Workbook.upload_date.desc()).first()
    if not latest_wb:
        return {"error": "No workbooks found"}
        
    wb_id = latest_wb.id
    
    return {
        "workbook_id": wb_id,
        "daily_performance": [{"date": r.date, "collection": r.collection, "target": r.target} for r in db.query(DailyPerformance).filter_by(workbook_id=wb_id).all()],
        "leader_performance": [{"name": r.leader_name, "revenue": r.revenue, "target": r.target} for r in db.query(LeaderPerformance).filter_by(workbook_id=wb_id).all()],
        "offering_performance": [{"name": r.offering, "revenue": r.revenue, "period": r.period} for r in db.query(OfferingPerformance).filter_by(workbook_id=wb_id).all()]
    }
