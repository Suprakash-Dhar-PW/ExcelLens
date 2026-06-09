import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base

class Workbook(Base):
    __tablename__ = "workbooks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, index=True, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, default="pending", nullable=False)
    
    executive_summaries = relationship("ExecutiveSummary", back_populates="workbook", cascade="all, delete-orphan")
    daily_performances = relationship("DailyPerformance", back_populates="workbook", cascade="all, delete-orphan")
    category_performances = relationship("CategoryPerformance", back_populates="workbook", cascade="all, delete-orphan")
    offering_performances = relationship("OfferingPerformance", back_populates="workbook", cascade="all, delete-orphan")
    batch_performances = relationship("BatchPerformance", back_populates="workbook", cascade="all, delete-orphan")
    leader_performances = relationship("LeaderPerformance", back_populates="workbook", cascade="all, delete-orphan")

class ExecutiveSummary(Base):
    __tablename__ = "executive_summary"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workbook_id = Column(UUID(as_uuid=True), ForeignKey("workbooks.id", ondelete="CASCADE"), nullable=False)
    metric_name = Column(String)
    value = Column(Float, default=0.0)
    workbook = relationship("Workbook", back_populates="executive_summaries")

class DailyPerformance(Base):
    __tablename__ = "daily_performance"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workbook_id = Column(UUID(as_uuid=True), ForeignKey("workbooks.id", ondelete="CASCADE"), nullable=False)
    date = Column(DateTime)
    collection = Column(Float, default=0.0)
    target = Column(Float, default=0.0)
    workbook = relationship("Workbook", back_populates="daily_performances")

class CategoryPerformance(Base):
    __tablename__ = "category_performance"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workbook_id = Column(UUID(as_uuid=True), ForeignKey("workbooks.id", ondelete="CASCADE"), nullable=False)
    category = Column(String)
    revenue = Column(Float, default=0.0)
    rank_type = Column(String) # 'top' or 'bottom'
    workbook = relationship("Workbook", back_populates="category_performances")

class OfferingPerformance(Base):
    __tablename__ = "offering_performance"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workbook_id = Column(UUID(as_uuid=True), ForeignKey("workbooks.id", ondelete="CASCADE"), nullable=False)
    offering = Column(String)
    revenue = Column(Float, default=0.0)
    period = Column(String) # 'MTD' or 'YTD'
    workbook = relationship("Workbook", back_populates="offering_performances")

class BatchPerformance(Base):
    __tablename__ = "batch_performance"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workbook_id = Column(UUID(as_uuid=True), ForeignKey("workbooks.id", ondelete="CASCADE"), nullable=False)
    batch_name = Column(String)
    revenue = Column(Float, default=0.0)
    enrollments = Column(Integer, default=0)
    workbook = relationship("Workbook", back_populates="batch_performances")

class LeaderPerformance(Base):
    __tablename__ = "leader_performance"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workbook_id = Column(UUID(as_uuid=True), ForeignKey("workbooks.id", ondelete="CASCADE"), nullable=False)
    leader_name = Column(String)
    revenue = Column(Float, default=0.0)
    target = Column(Float, default=0.0)
    workbook = relationship("Workbook", back_populates="leader_performances")

class CopilotSession(Base):
    __tablename__ = "copilot_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    context_filters = Column(JSON)
    messages = relationship("CopilotMessage", back_populates="session", cascade="all, delete-orphan")

class CopilotMessage(Base):
    __tablename__ = "copilot_messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("copilot_sessions.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String, nullable=False) # 'user' or 'ai'
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    session = relationship("CopilotSession", back_populates="messages")
