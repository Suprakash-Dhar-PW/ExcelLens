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
    
    daily_rows = [{"date": r.date, "collection": r.collection, "target": r.target} for r in db.query(DailyPerformance).filter_by(workbook_id=wb_id).all()]
    offering_rows = [{"offering": r.offering, "revenue": r.revenue, "period": r.period} for r in db.query(OfferingPerformance).filter_by(workbook_id=wb_id).all()]
    batch_rows = [{"batch_name": r.batch_name, "revenue": r.revenue, "enrollments": r.enrollments} for r in db.query(BatchPerformance).filter_by(workbook_id=wb_id).all()]
    leader_rows = [{"name": r.leader_name, "revenue": r.revenue, "target": r.target} for r in db.query(LeaderPerformance).filter_by(workbook_id=wb_id).all()]
    
    return {
        "daily_count": len(daily_rows),
        "offering_count": len(offering_rows),
        "batch_count": len(batch_rows),
        "leader_count": len(leader_rows),
        "sample_daily_rows": daily_rows[:5],
        "sample_offering_rows": offering_rows[:5],
        "sample_batch_rows": batch_rows[:5]
    }

@router.get("/full-diagnostics")
def get_full_diagnostics(db: Session = Depends(get_db)):
    """Returns a full diagnostic report including table counts and samples."""
    latest_wb = db.query(Workbook).order_by(Workbook.upload_date.desc()).first()
    if not latest_wb:
        return {"error": "No workbooks found"}
        
    wb_id = latest_wb.id
    
    counts = {
        "executive_summary": db.query(ExecutiveSummary).filter_by(workbook_id=wb_id).count(),
        "daily_performance": db.query(DailyPerformance).filter_by(workbook_id=wb_id).count(),
        "category_performance": db.query(CategoryPerformance).filter_by(workbook_id=wb_id).count(),
        "offering_performance": db.query(OfferingPerformance).filter_by(workbook_id=wb_id).count(),
        "batch_performance": db.query(BatchPerformance).filter_by(workbook_id=wb_id).count(),
        "leader_performance": db.query(LeaderPerformance).filter_by(workbook_id=wb_id).count()
    }
    
    daily_sample = [{"date": r.date, "collection": r.collection, "target": r.target} for r in db.query(DailyPerformance).filter_by(workbook_id=wb_id).limit(5).all()]
    offering_sample = [{"offering": r.offering, "revenue": r.revenue, "period": r.period} for r in db.query(OfferingPerformance).filter_by(workbook_id=wb_id).limit(5).all()]
    batch_sample = [{"batch_name": r.batch_name, "revenue": r.revenue, "enrollments": r.enrollments} for r in db.query(BatchPerformance).filter_by(workbook_id=wb_id).limit(5).all()]
    
    return {
        "latest_workbook": latest_wb.filename,
        "workbook_id": wb_id,
        "table_counts": counts,
        "daily_sample": daily_sample,
        "offering_sample": offering_sample,
        "batch_sample": batch_sample
    }


