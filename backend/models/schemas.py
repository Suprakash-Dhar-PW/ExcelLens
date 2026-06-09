from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class PerformanceData(BaseModel):
    id: Optional[str] = None
    upload_id: str
    date: date
    category: str
    revenue: float
    orders: int
    target_revenue: float
    target_orders: int

class UploadMetadata(BaseModel):
    id: Optional[str] = None
    filename: str
    upload_date: datetime
    status: str
