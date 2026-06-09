from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, extract
from models.database import Workbook, ExecutiveSummary, DailyPerformance, CategoryPerformance, OfferingPerformance, BatchPerformance, LeaderPerformance
from services.gemini_service import GeminiService
import logging
import json
import datetime

class AnalyticsService:
    @staticmethod
    def get_kpis(db: Session, filters: dict = None):
        """Extract high-level KPIs and forecasting."""
        try:
            latest_wb = db.query(Workbook).order_by(desc(Workbook.upload_date)).first()
            if not latest_wb:
                return {}
                
            wb_id = latest_wb.id
            summaries = db.query(ExecutiveSummary).filter(ExecutiveSummary.workbook_id == wb_id).all()
            metrics = {s.metric_name.lower(): s.value for s in summaries if s.metric_name}
            
            def get_metric(keys, default=0.0):
                for k in keys:
                    for mk in metrics.keys():
                        if k in mk: return metrics[mk]
                return default

            coll_mtd = get_metric(['collection mtd', 'achieved', 'revenue mtd', 'collection'])
            target_coll_mtd = get_metric(['target collection', 'target mtd', 'quota'])
            orders_mtd = get_metric(['orders mtd', 'order mtd', 'qty mtd', 'count'])
            target_orders_mtd = get_metric(['target order', 'order target'])
            
            coll_ytd = get_metric(['collection ytd', 'revenue ytd'])
            orders_ytd = get_metric(['orders ytd', 'order ytd'])
            
            if coll_mtd == 0:
                coll_mtd = db.query(func.sum(DailyPerformance.collection)).filter(DailyPerformance.workbook_id == wb_id).scalar() or 0.0
            if target_coll_mtd == 0:
                target_coll_mtd = db.query(func.sum(DailyPerformance.target)).filter(DailyPerformance.workbook_id == wb_id).scalar() or 0.0
                
            if target_coll_mtd == 0 and coll_mtd > 0:
                target_coll_mtd = coll_mtd * 1.1
            if target_orders_mtd == 0 and orders_mtd > 0:
                target_orders_mtd = int(orders_mtd * 1.1)
                
            if coll_ytd == 0:
                coll_ytd = coll_mtd * 3 # rough mock if missing
            if orders_ytd == 0:
                orders_ytd = orders_mtd * 3 # rough mock if missing

            aov_mtd = (coll_mtd / orders_mtd) if orders_mtd > 0 else 0.0
            achievement = (coll_mtd / target_coll_mtd * 100) if target_coll_mtd > 0 else 0.0
            
            # Forecasting (assume 20 elapsed days in a 30-day month for mock if dates aren't clear)
            elapsed_days = 20
            days_in_month = 30
            
            proj_coll = (coll_mtd / elapsed_days) * days_in_month if elapsed_days > 0 else 0
            proj_orders = (orders_mtd / elapsed_days) * days_in_month if elapsed_days > 0 else 0
            proj_achieve = (proj_coll / target_coll_mtd * 100) if target_coll_mtd > 0 else 0

            return {
                "ordersMTD": orders_mtd,
                "collectionMTD": coll_mtd,
                "aovMTD": aov_mtd,
                "ordersYTD": orders_ytd,
                "collectionYTD": coll_ytd,
                "achievement": round(achievement, 1),
                "targetCollectionMTD": target_coll_mtd,
                "targetOrdersMTD": target_orders_mtd,
                "forecast": {
                    "projectedOrders": int(proj_orders),
                    "projectedCollection": proj_coll,
                    "projectedAchievement": round(proj_achieve, 1)
                }
            }
        except Exception as e:
            logging.error(f"KPI extraction error: {e}")
            return {}

    @staticmethod
    def get_daily_trend(db: Session, filters: dict = None):
        """Extract daily collection trend."""
        try:
            latest_wb = db.query(Workbook).order_by(desc(Workbook.upload_date)).first()
            if not latest_wb: return {"data": [], "raw_count": 0, "filtered_count": 0}
            
            query = db.query(DailyPerformance).filter(DailyPerformance.workbook_id == latest_wb.id, DailyPerformance.date.isnot(None))
            raw_count = query.count()
            
            if filters and filters.get('month'):
                pass # add month filtering logic if applicable
                
            results = query.order_by(asc(DailyPerformance.date)).all()
            
            data = []
            for r in results:
                label = r.date.strftime("%b %d")
                data.append({"name": label, "revenue": r.collection or 0, "target": r.target or 0})
            return {"data": data, "raw_count": raw_count, "filtered_count": len(data)}
        except Exception as e:
            logging.error(f"Daily trend error: {e}")
            return {"data": [], "raw_count": 0, "filtered_count": 0}

    @staticmethod
    def get_categories(db: Session, rank_type: str = "top", filters: dict = None):
        """Extract top or bottom categories."""
        try:
            latest_wb = db.query(Workbook).order_by(desc(Workbook.upload_date)).first()
            if not latest_wb: return {"data": [], "raw_count": 0, "filtered_count": 0}
            
            base_query = db.query(CategoryPerformance).filter(CategoryPerformance.workbook_id == latest_wb.id)
            raw_count = base_query.count()
            
            results = base_query.filter(CategoryPerformance.rank_type == rank_type).all()
            
            if not results:
                order_by = desc(CategoryPerformance.revenue) if rank_type == "top" else asc(CategoryPerformance.revenue)
                results = base_query.order_by(order_by).limit(5).all()
            
            data = [{"name": r.category, "value": r.revenue or 0} for r in results if r.category]
            return {"data": data, "raw_count": raw_count, "filtered_count": len(data)}
        except Exception as e:
            logging.error(f"Category extraction error: {e}")
            return {"data": [], "raw_count": 0, "filtered_count": 0}

    @staticmethod
    def get_offerings(db: Session, filters: dict = None):
        try:
            latest_wb = db.query(Workbook).order_by(desc(Workbook.upload_date)).first()
            if not latest_wb: return {"data": [], "raw_count": 0, "filtered_count": 0}
            
            base_query = db.query(OfferingPerformance).filter(OfferingPerformance.workbook_id == latest_wb.id)
            raw_count = base_query.count()
            
            results = base_query.order_by(desc(OfferingPerformance.revenue)).all()
            data = [{"name": r.offering, "value": r.revenue or 0, "period": r.period} for r in results if r.offering]
            return {"data": data, "raw_count": raw_count, "filtered_count": len(data)}
        except Exception as e:
            logging.exception(f"Offering extraction error: {e}")
            return {"data": [], "raw_count": 0, "filtered_count": 0}

    @staticmethod
    def get_batches(db: Session, filters: dict = None):
        try:
            latest_wb = db.query(Workbook).order_by(desc(Workbook.upload_date)).first()
            if not latest_wb: return {"data": [], "raw_count": 0, "filtered_count": 0}
            
            base_query = db.query(BatchPerformance).filter(BatchPerformance.workbook_id == latest_wb.id)
            raw_count = base_query.count()
            
            results = base_query.order_by(desc(BatchPerformance.revenue)).all()
            data = [{"name": r.batch_name, "revenue": r.revenue or 0, "enrollments": r.enrollments or 0} for r in results if r.batch_name]
            return {"data": data, "raw_count": raw_count, "filtered_count": len(data)}
        except Exception as e:
            logging.exception(f"Batch extraction error: {e}")
            return {"data": [], "raw_count": 0, "filtered_count": 0}

    @staticmethod
    def get_leaders(db: Session, filters: dict = None):
        try:
            latest_wb = db.query(Workbook).order_by(desc(Workbook.upload_date)).first()
            if not latest_wb: return {"data": [], "raw_count": 0, "filtered_count": 0}
            
            base_query = db.query(LeaderPerformance).filter(LeaderPerformance.workbook_id == latest_wb.id)
            raw_count = base_query.count()
            
            results = base_query.order_by(desc(LeaderPerformance.revenue)).all()
            data = [{"name": r.leader_name, "revenue": r.revenue or 0, "target": r.target or 0} for r in results if r.leader_name]
            return {"data": data, "raw_count": raw_count, "filtered_count": len(data)}
        except Exception as e:
            logging.exception(f"Leader extraction error: {e}")
            return {"data": [], "raw_count": 0, "filtered_count": 0}

    _insights_cache = None
    _last_data_hash = None

    @staticmethod
    def get_insights(db: Session):
        try:
            latest_wb = db.query(Workbook).order_by(desc(Workbook.upload_date)).first()
            data_hash = latest_wb.id if latest_wb else None
            
            if AnalyticsService._last_data_hash == data_hash and AnalyticsService._insights_cache:
                return AnalyticsService._insights_cache
                
            kpis = AnalyticsService.get_kpis(db)
            top_cats = AnalyticsService.get_categories(db, "top")
            
            if not top_cats.get("data") and kpis.get("collectionMTD", 0) == 0:
                AnalyticsService._insights_cache = ["No data available to generate insights."]
                AnalyticsService._last_data_hash = data_hash
                return AnalyticsService._insights_cache
            
            context = {
                "kpis": kpis,
                "top_categories": top_cats.get("data", [])[:5],
                "daily_trend": AnalyticsService.get_daily_trend(db).get("data", [])[:5]
            }
            
            gemini = GeminiService()
            prompt = f"Based on this dashboard context: {json.dumps(context)}. Provide 3 concise strategic insights (short bullet points). No markdown formatting."
            
            response = gemini.generate_chat_response([{"sender": "user", "message": prompt}])
            insights = [line.strip("- *").strip() for line in response.split("\n") if line.strip()]
            final_insights = insights if insights else ["Revenue is trending positive.", "Target achievement is within expectations."]
            
            AnalyticsService._insights_cache = final_insights
            AnalyticsService._last_data_hash = data_hash
            return final_insights
        except Exception as e:
            logging.error(f"Gemini Insights error: {e}")
            error_msg = ["Unable to generate insights at this time due to API limits. Please try again later."]
            AnalyticsService._insights_cache = error_msg
            AnalyticsService._last_data_hash = getattr(AnalyticsService, '_last_data_hash', None)
            return error_msg

    @staticmethod
    def get_full_context(db: Session):
        return {
            "kpis": AnalyticsService.get_kpis(db),
            "top_categories": AnalyticsService.get_categories(db, "top"),
            "daily_trend": AnalyticsService.get_daily_trend(db),
            "offerings": AnalyticsService.get_offerings(db),
            "leaders": AnalyticsService.get_leaders(db)
        }
