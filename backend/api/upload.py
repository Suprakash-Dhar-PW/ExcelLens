from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from core.database import get_db
from repositories.workbook_repo import WorkbookRepository
from services.excel_parser import parse_excel_file
import logging
import os

router = APIRouter()

logger = logging.getLogger('upload')

def get_api_key(api_key: str = Security(APIKeyHeader(name="X-API-Key", auto_error=False))):
    expected = os.getenv('API_KEY')
    # If no API_KEY is set, skip authentication (useful for local development)
    if not expected:
        return None
    if api_key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return api_key

@router.post("/", dependencies=[Depends(get_api_key)])
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    repo = WorkbookRepository(db)
    logger.info(f"Received upload request for file: {file.filename}")
    try:
        content = await file.read()
        logger.debug(f"File size: {len(content)} bytes")

        # 1. Parse Excel (Returns dict of lists)
        records_dict = parse_excel_file(content, file.filename)
        for key, value in records_dict.items():
            logger.info(f"{key}: {len(value)} rows")
        if not any(len(v) for v in records_dict.values()):
            logger.warning("No data extracted from any sheet.")
            raise HTTPException(status_code=400, detail="Could not parse Excel or file is empty")

        # 2. Create Workbook Record
        workbook = repo.create_workbook(filename=file.filename)
        logger.info(f"Created workbook ID: {workbook.id}")
        logger.info(f"Created workbook record with ID: {workbook.id}")

        # 3. Create Analytics Records
        total_rows = repo.bulk_create_analytics_records(workbook_id=workbook.id, records_dict=records_dict)
        logger.info(f"Inserted total {total_rows} analytics rows for workbook {workbook.id}")
        logger.info("Analytics insertion breakdown:")
        for k, v in records_dict.items():
            logger.info(f"  - {k}: {len(v)} rows")

        # 4. Update status
        repo.update_workbook_status(workbook.id, "completed")
        logger.info(f"Workbook {workbook.id} status set to completed")

        # 5. Broadcast update to clients
        from api.ws import manager
        await manager.broadcast("refresh")
        logger.debug("Broadcasted refresh message via WebSocket")

        # After insertion, fetch counts for each analytics table
        from models.database import ExecutiveSummary, DailyPerformance, CategoryPerformance, OfferingPerformance, BatchPerformance, LeaderPerformance
        counts = {
            "executive_summaries": db.query(ExecutiveSummary).filter(ExecutiveSummary.workbook_id == workbook.id).count(),
            "daily_performances": db.query(DailyPerformance).filter(DailyPerformance.workbook_id == workbook.id).count(),
            "category_performances": db.query(CategoryPerformance).filter(CategoryPerformance.workbook_id == workbook.id).count(),
            "offering_performances": db.query(OfferingPerformance).filter(OfferingPerformance.workbook_id == workbook.id).count(),
            "batch_performances": db.query(BatchPerformance).filter(BatchPerformance.workbook_id == workbook.id).count(),
            "leader_performances": db.query(LeaderPerformance).filter(LeaderPerformance.workbook_id == workbook.id).count()
        }
        logger.info(f"Analytics table counts for workbook {workbook.id}: {counts}")
        warnings = []
        if counts["daily_performances"] == 0:
            warnings.append("Warning: Daily Performance count is zero")
        if counts["offering_performances"] == 0:
            warnings.append("Warning: Offering Performance count is zero")
        if counts["batch_performances"] == 0:
            warnings.append("Warning: Batch Performance count is zero")
        if counts["leader_performances"] == 0:
            warnings.append("Warning: Leader Performance count is zero")
            
        if warnings:
            logger.warning("Upload generated warnings: " + ", ".join(warnings))

        return {
            "message": "File uploaded successfully",
            "workbook_id": str(workbook.id),
            "rows_processed": total_rows,
            "executive_summaries": counts["executive_summaries"],
            "daily_performances": counts["daily_performances"],
            "category_performances": counts["category_performances"],
            "offering_performances": counts["offering_performances"],
            "batch_performances": counts["batch_performances"],
            "leader_performances": counts["leader_performances"],
            "warnings": warnings
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback()
        logger.error(f"Upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/history", dependencies=[Depends(get_api_key)])
def get_upload_history(db: Session = Depends(get_db)):
    from models.database import Workbook
    from sqlalchemy import desc
    workbooks = db.query(Workbook).order_by(desc(Workbook.upload_date)).limit(5).all()
    return [{"filename": w.filename, "upload_date": w.upload_date, "status": w.status} for w in workbooks]

@router.get("/verify_counts", dependencies=[Depends(get_api_key)])
def verify_counts(db: Session = Depends(get_db)):
    from models.database import Workbook, ExecutiveSummary, DailyPerformance, CategoryPerformance, OfferingPerformance, BatchPerformance, LeaderPerformance
    from sqlalchemy import func
    tables = {
        "Workbook": db.query(func.count()).select_from(Workbook).scalar(),
        "ExecutiveSummary": db.query(func.count()).select_from(ExecutiveSummary).scalar(),
        "DailyPerformance": db.query(func.count()).select_from(DailyPerformance).scalar(),
        "CategoryPerformance": db.query(func.count()).select_from(CategoryPerformance).scalar(),
        "OfferingPerformance": db.query(func.count()).select_from(OfferingPerformance).scalar(),
        "BatchPerformance": db.query(func.count()).select_from(BatchPerformance).scalar(),
        "LeaderPerformance": db.query(func.count()).select_from(LeaderPerformance).scalar()
    }
    logger = logging.getLogger('verify')
    logger.info(f"Verification counts: {tables}")
    return tables
