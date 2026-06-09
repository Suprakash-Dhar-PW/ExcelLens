from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, extract
from models.database import Workbook, ExecutiveSummary, DailyPerformance, CategoryPerformance, OfferingPerformance, BatchPerformance, LeaderPerformance
from services.gemini_service import GeminiService
import logging
import json

class AnalyticsService:
    @staticmethod
    def get_kpis(db: Session):
        """Extract high-level KPIs from ExecutiveSummary and DailyPerformance."""
        try:
            # Get latest workbook to scope data
            latest_wb = db.query(Workbook).order_by(desc(Workbook.upload_date)).first()
            if not latest_wb:
                return {"totalRevenue": 0, "targetRevenue": 0, "totalOrders": 0, "targetOrders": 0, "activeCategories": 0, "revenueGap": 0, "achievement": 0}
                
            wb_id = latest_wb.id
            
            # Fetch summaries
            summaries = db.query(ExecutiveSummary).filter(ExecutiveSummary.workbook_id == wb_id).all()
            metrics = {s.metric_name.lower(): s.value for s in summaries if s.metric_name}
            
            # Match common names
            def get_metric(keys, default=0.0):
                for k in keys:
                    for mk in metrics.keys():
                        if k in mk: return metrics[mk]
                return default

            achieved_coll = get_metric(['achieved', 'revenue', 'collection'])
            target_coll = get_metric(['target', 'quota'])
            orders = get_metric(['order', 'qty', 'count'])
            target_orders = get_metric(['target order', 'order target'])
            
            # If not in summary, compute from DailyPerformance
            if achieved_coll == 0:
                achieved_coll = db.query(func.sum(DailyPerformance.collection)).filter(DailyPerformance.workbook_id == wb_id).scalar() or 0.0
            if target_coll == 0:
                target_coll = db.query(func.sum(DailyPerformance.target)).filter(DailyPerformance.workbook_id == wb_id).scalar() or 0.0
                
            # If still 0, fallback
            if target_coll == 0 and achieved_coll > 0:
                target_coll = achieved_coll * 1.1
            if target_orders == 0 and orders > 0:
                target_orders = int(orders * 1.1)
                
            active_cats = db.query(CategoryPerformance.category).filter(CategoryPerformance.workbook_id == wb_id).distinct().count()

            gap = achieved_coll - target_coll
            achievement = (achieved_coll / target_coll * 100) if target_coll > 0 else 0.0

            return {
                "totalRevenue": achieved_coll,
                "targetRevenue": target_coll,
                "totalOrders": orders,
                "targetOrders": target_orders,
                "activeCategories": active_cats,
                "revenueGap": gap,
                "achievement": round(achievement, 1)
            }
        except Exception as e:
            logging.error(f"KPI extraction error: {e}")
            return {"totalRevenue": 0, "targetRevenue": 0, "totalOrders": 0, "targetOrders": 0, "activeCategories": 0, "revenueGap": 0, "achievement": 0}

    @staticmethod
    def get_daily_trend(db: Session):
        """Extract daily collection trend."""
        try:
            latest_wb = db.query(Workbook).order_by(desc(Workbook.upload_date)).first()
            if not latest_wb: return []
            
            results = db.query(DailyPerformance).filter(DailyPerformance.workbook_id == latest_wb.id, DailyPerformance.date.isnot(None)).order_by(asc(DailyPerformance.date)).all()
            
            data = []
            for r in results:
                label = r.date.strftime("%b %d")
                data.append({"name": label, "revenue": r.collection or 0, "target": r.target or 0})
            return data
        except Exception as e:
            logging.error(f"Daily trend error: {e}")
            return []

    @staticmethod
    def get_categories(db: Session, rank_type: str = "top"):
        """Extract top or bottom categories."""
        try:
            latest_wb = db.query(Workbook).order_by(desc(Workbook.upload_date)).first()
            if not latest_wb: return []
            
            # If explicit rank_type exists in DB, use it
            results = db.query(CategoryPerformance).filter(
                CategoryPerformance.workbook_id == latest_wb.id,
                CategoryPerformance.rank_type == rank_type
            ).all()
            
            # If empty but we have unranked categories, order them manually
            if not results:
                order_by = desc(CategoryPerformance.revenue) if rank_type == "top" else asc(CategoryPerformance.revenue)
                results = db.query(CategoryPerformance).filter(
                    CategoryPerformance.workbook_id == latest_wb.id
                ).order_by(order_by).limit(5).all()
            
            return [{"name": r.category, "value": r.revenue or 0} for r in results if r.category]
        except Exception as e:
            logging.error(f"Category extraction error: {e}")
            return []

    @staticmethod
    def get_offerings(db: Session):
        try:
            latest_wb = db.query(Workbook).order_by(desc(Workbook.upload_date)).first()
            if not latest_wb: return []
            results = db.query(OfferingPerformance).filter(OfferingPerformance.workbook_id == latest_wb.id).order_by(desc(OfferingPerformance.revenue)).all()
            return [{"name": r.offering, "value": r.revenue or 0, "period": r.period} for r in results if r.offering]
        except:
            return []

    @staticmethod
    def get_batches(db: Session):
        try:
            latest_wb = db.query(Workbook).order_by(desc(Workbook.upload_date)).first()
            if not latest_wb: return []
            results = db.query(BatchPerformance).filter(BatchPerformance.workbook_id == latest_wb.id).order_by(desc(BatchPerformance.revenue)).all()
            return [{"name": r.batch_name, "revenue": r.revenue or 0, "enrollments": r.enrollments or 0} for r in results if r.batch_name]
        except:
            return []

    @staticmethod
    def get_leaders(db: Session):
        try:
            latest_wb = db.query(Workbook).order_by(desc(Workbook.upload_date)).first()
            if not latest_wb: return []
            results = db.query(LeaderPerformance).filter(LeaderPerformance.workbook_id == latest_wb.id).order_by(desc(LeaderPerformance.revenue)).all()
            return [{"name": r.leader_name, "revenue": r.revenue or 0, "target": r.target or 0} for r in results if r.leader_name]
        except:
            return []

    # In-memory cache to prevent Gemini quota exhaustion
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
            
            if not top_cats and kpis.get("totalRevenue", 0) == 0:
                AnalyticsService._insights_cache = ["No data available to generate insights."]
                AnalyticsService._last_data_hash = data_hash
                return AnalyticsService._insights_cache
            
            context = {
                "kpis": kpis,
                "top_categories": top_cats,
                "daily_trend": AnalyticsService.get_daily_trend(db)[:5] # Just sample
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
