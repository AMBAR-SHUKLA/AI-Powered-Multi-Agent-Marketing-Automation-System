from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, DeclarativeBase
import enum


class Base(DeclarativeBase):
    pass


class CampaignStatus(str, enum.Enum):
    PENDING = "pending"
    PLANNING = "planning"
    GENERATING = "generating"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    product = Column(String(255), nullable=False)
    target_audience = Column(String(255), nullable=False)
    goal = Column(String(255), nullable=False)
    budget = Column(Float, nullable=True)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.PENDING)
    strategy = Column(Text, nullable=True)          # output from planner agent
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    contents = relationship("Content", back_populates="campaign", cascade="all, delete")
    outreaches = relationship("Outreach", back_populates="campaign", cascade="all, delete")
    audit_logs = relationship("AuditLog", back_populates="campaign", cascade="all, delete")


class Content(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    content_type = Column(String(100), nullable=False)   # email, social, ad_copy, etc.
    title = Column(String(255), nullable=True)
    body = Column(Text, nullable=False)
    validated = Column(String(10), default="pending")    # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="contents")


class Outreach(Base):
    __tablename__ = "outreaches"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    channel = Column(String(100), nullable=False)        # email, linkedin, etc.
    recipient = Column(String(255), nullable=True)
    subject = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)
    status = Column(String(50), default="queued")        # queued, sent, failed
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="outreaches")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    agent = Column(String(100), nullable=False)
    action = Column(String(255), nullable=False)
    detail = Column(Text, nullable=True)
    status = Column(String(50), default="success")       # success, error, warning
    timestamp = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="audit_logs")
