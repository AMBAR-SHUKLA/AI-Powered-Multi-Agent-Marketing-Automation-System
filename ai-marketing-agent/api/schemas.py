from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ─── Campaign ─────────────────────────────────────────────────────────────────

class CampaignRunRequest(BaseModel):
    product: str = Field(..., description="Product or service name", example="SaaS Analytics Tool")
    target_audience: str = Field(..., description="Target audience description", example="B2B SaaS startups")
    goal: str = Field(..., description="Campaign goal", example="lead generation")
    budget: Optional[float] = Field(None, description="Campaign budget in USD", example=5000.0)


class CampaignRunResponse(BaseModel):
    campaign_id: int
    status: str
    strategy_preview: Optional[str] = None
    content_count: Optional[int] = None
    outreach_count: Optional[int] = None
    error: Optional[str] = None


class CampaignDetail(BaseModel):
    id: int
    product: str
    target_audience: str
    goal: str
    budget: Optional[float]
    status: str
    strategy: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Content ──────────────────────────────────────────────────────────────────

class ContentGenerateRequest(BaseModel):
    campaign_id: int
    product: str
    target_audience: str
    goal: str
    strategy: Optional[str] = None


class ContentItem(BaseModel):
    id: int
    campaign_id: int
    content_type: str
    title: Optional[str]
    body: str
    validated: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Outreach ─────────────────────────────────────────────────────────────────

class OutreachExecuteRequest(BaseModel):
    campaign_id: int


class OutreachItem(BaseModel):
    id: int
    campaign_id: int
    channel: str
    recipient: Optional[str]
    subject: Optional[str]
    message: str
    status: str
    sent_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Audit ────────────────────────────────────────────────────────────────────

class AuditEntry(BaseModel):
    id: int
    campaign_id: Optional[int]
    agent: str
    action: str
    detail: Optional[str]
    status: str
    timestamp: datetime

    class Config:
        from_attributes = True


class AuditResponse(BaseModel):
    total: int
    logs: List[AuditEntry]
