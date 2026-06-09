from fastapi import APIRouter, Depends
import logging
from sqlalchemy.orm import Session
from core.database import get_db
from services.analytics_service import AnalyticsService

router = APIRouter()
logger = logging.getLogger('dashboard')

@router.get("/kpis")
def get_kpis(db: Session = Depends(get_db)):
    result = AnalyticsService.get_kpis(db)
    logger.info(f"KPIs returned: {result}")
    return result

@router.get("/daily-trend")
def get_daily_trend(db: Session = Depends(get_db)):
    result = AnalyticsService.get_daily_trend(db)
    logger.info(f"Daily trend returned: {result}")
    return result

@router.get("/categories/{rank_type}")
def get_categories(rank_type: str, db: Session = Depends(get_db)):
    result = AnalyticsService.get_categories(db, rank_type=rank_type)
    logger.info(f"Categories ({rank_type}) returned: {result}")
    return result

@router.get("/offerings")
def get_offerings(db: Session = Depends(get_db)):
    result = AnalyticsService.get_offerings(db)
    logger.info(f"Offerings returned: {result}")
    return result

@router.get("/batches")
def get_batches(db: Session = Depends(get_db)):
    result = AnalyticsService.get_batches(db)
    logger.info(f"Batches returned: {result}")
    return result

@router.get("/leaders")
def get_leaders(db: Session = Depends(get_db)):
    result = AnalyticsService.get_leaders(db)
    logger.info(f"Leaders returned: {result}")
    return result

@router.get("/insights")
def get_insights(db: Session = Depends(get_db)):
    result = AnalyticsService.get_insights(db)
    logger.info(f"Insights returned: {result}")
    return result

@router.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    # Alerts can be derived from the KPI gap
    kpis = AnalyticsService.get_kpis(db)
    alerts = []
    if kpis.get("revenueGap", 0) < 0:
        alerts.append(f"Revenue is below target by ${abs(kpis['revenueGap']):,.2f}.")
    if kpis.get("totalOrders", 0) < kpis.get("targetOrders", 0):
        alerts.append("Order volume is lagging behind expectations.")
    if not alerts:
        alerts.append("All metrics are healthy and on track.")
    return alerts

import time
start_time = time.time()

@router.get("/health")
def get_health():
    uptime = time.time() - start_time
    return {
        "status": "ok",
        "uptime_seconds": round(uptime, 2),
        "version": "1.0.0"
    }
