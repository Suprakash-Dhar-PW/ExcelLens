import uuid
from sqlalchemy.orm import Session
from models.database import Workbook, ExecutiveSummary, DailyPerformance, CategoryPerformance, OfferingPerformance, BatchPerformance, LeaderPerformance

class WorkbookRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_workbook(self, filename: str) -> Workbook:
        wb = Workbook(filename=filename, status="processing")
        self.db.add(wb)
        self.db.commit()
        self.db.refresh(wb)
        return wb

    def update_workbook_status(self, workbook_id: str | uuid.UUID, status: str):
        wb = self.db.query(Workbook).filter(Workbook.id == workbook_id).first()
        if wb:
            wb.status = status
            self.db.commit()

    def bulk_create_analytics_records(self, workbook_id: str | uuid.UUID, records_dict: dict):
        total_rows = 0
        
        # Executive Summary
        exec_summaries = []
        for data in records_dict.get("executive_summaries", []):
            exec_summaries.append(ExecutiveSummary(workbook_id=workbook_id, **data))
        if exec_summaries:
            self.db.add_all(exec_summaries)
            total_rows += len(exec_summaries)
            
        # Daily Performance
        daily_perfs = []
        for data in records_dict.get("daily_performances", []):
            daily_perfs.append(DailyPerformance(workbook_id=workbook_id, **data))
        if daily_perfs:
            self.db.add_all(daily_perfs)
            total_rows += len(daily_perfs)
            
        # Category Performance
        category_perfs = []
        for data in records_dict.get("category_performances", []):
            category_perfs.append(CategoryPerformance(workbook_id=workbook_id, **data))
        if category_perfs:
            self.db.add_all(category_perfs)
            total_rows += len(category_perfs)
            
        # Offering Performance
        offering_perfs = []
        for data in records_dict.get("offering_performances", []):
            offering_perfs.append(OfferingPerformance(workbook_id=workbook_id, **data))
        if offering_perfs:
            self.db.add_all(offering_perfs)
            total_rows += len(offering_perfs)
            
        # Batch Performance
        batch_perfs = []
        for data in records_dict.get("batch_performances", []):
            batch_perfs.append(BatchPerformance(workbook_id=workbook_id, **data))
        if batch_perfs:
            self.db.add_all(batch_perfs)
            total_rows += len(batch_perfs)
            
        # Leader Performance
        leader_perfs = []
        for data in records_dict.get("leader_performances", []):
            leader_perfs.append(LeaderPerformance(workbook_id=workbook_id, **data))
        if leader_perfs:
            self.db.add_all(leader_perfs)
            total_rows += len(leader_perfs)
            
        self.db.commit()
        return total_rows
