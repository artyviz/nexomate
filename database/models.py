# database/models.py
"""SQLAlchemy models for all Nexomate tables."""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base


class Client(Base):
    __tablename__ = "clients"

    client_id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    website = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    country = Column(String, nullable=True)
    target_country = Column(String, nullable=True)
    target_cities = Column(Text, nullable=True)
    target_geography = Column(String, nullable=True)
    services = Column(Text, nullable=True)
    ideal_customer_description = Column(Text, nullable=True)
    company_size = Column(String, nullable=True)
    target_job_titles = Column(Text, nullable=True)
    pain_points = Column(Text, nullable=True)
    value_proposition = Column(Text, nullable=True)
    preferred_tone = Column(String, default="Professional")
    sender_name = Column(String, nullable=True)
    sender_email = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    business_profile = relationship("BusinessProfile", back_populates="client", uselist=False)
    icp_profile = relationship("ICPProfile", back_populates="client", uselist=False)
    leads = relationship("Lead", back_populates="client")
    campaigns = relationship("Campaign", back_populates="client")


class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    profile_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    business_name = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    services = Column(Text, nullable=True)
    products = Column(Text, nullable=True)
    locations = Column(Text, nullable=True)
    service_areas = Column(Text, nullable=True)
    target_customers = Column(Text, nullable=True)
    customer_problems = Column(Text, nullable=True)
    value_propositions = Column(Text, nullable=True)
    pricing_signals = Column(Text, nullable=True)
    differentiators = Column(Text, nullable=True)
    competitors = Column(Text, nullable=True)
    keywords = Column(Text, nullable=True)
    raw_analysis = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    client = relationship("Client", back_populates="business_profile")


class ICPProfile(Base):
    __tablename__ = "icp_profiles"

    icp_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    target_customer = Column(Text, nullable=True)
    company_type = Column(String, nullable=True)
    job_titles = Column(Text, nullable=True)
    industry = Column(String, nullable=True)
    location = Column(String, nullable=True)
    company_size = Column(String, nullable=True)
    buying_signals = Column(Text, nullable=True)
    pain_points = Column(Text, nullable=True)
    search_keywords = Column(Text, nullable=True)
    exclusion_criteria = Column(Text, nullable=True)
    raw_icp = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    client = relationship("Client", back_populates="icp_profile")


class Lead(Base):
    __tablename__ = "leads"

    lead_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=True)

    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    company = Column(String, nullable=True)
    website = Column(String, nullable=True)

    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    country = Column(String, nullable=True)
    state = Column(String, nullable=True)
    city = Column(String, nullable=True)

    industry = Column(String, nullable=True)
    company_size = Column(String, nullable=True)

    source = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    source_type = Column(String, nullable=True)
    discovery_date = Column(DateTime, default=func.now())

    fit_score = Column(Float, nullable=True)
    score_level = Column(String, nullable=True)  # HIGH / MEDIUM / LOW
    score_reason = Column(Text, nullable=True)
    explee_relevance = Column(Float, nullable=True)  # Explee's relevance score (0-1)
    email_verified = Column(Boolean, default=False)  # Whether email was verified by Explee
    explee_company_id = Column(String, nullable=True)  # Explee company ID for dedup

    buying_signals = Column(Text, nullable=True)
    pain_points = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    email_status = Column(String, default="NONE")
    whatsapp_status = Column(String, default="NONE")
    sms_status = Column(String, default="NONE")

    lead_status = Column(String, default="NEW")
    is_demo = Column(Boolean, default=False)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    client = relationship("Client", back_populates="leads")
    messages = relationship("Message", back_populates="lead")
    replies = relationship("Reply", back_populates="lead")


class Campaign(Base):
    __tablename__ = "campaigns"

    campaign_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    industry = Column(String, nullable=True)
    location = Column(String, nullable=True)
    status = Column(String, default="DRAFT")  # DRAFT, READY, RUNNING, PAUSED, COMPLETED
    total_leads = Column(Integer, default=0)
    selected_leads = Column(Integer, default=0)
    emails_sent = Column(Integer, default=0)
    replies_count = Column(Integer, default=0)
    interested_count = Column(Integer, default=0)
    not_interested_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    client = relationship("Client", back_populates="campaigns")


class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.lead_id"), nullable=False)
    campaign_id = Column(Integer, nullable=True)
    channel = Column(String, default="email")  # email, whatsapp, sms
    subject = Column(String, nullable=True)
    body = Column(Text, nullable=True)
    status = Column(String, default="DRAFT")  # DRAFT, SCHEDULED, SENDING, SENT, DELIVERED, OPENED, CLICKED, REPLIED, BOUNCED, FAILED
    sent_at = Column(DateTime, nullable=True)
    smtp_message_id = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    lead = relationship("Lead", back_populates="messages")


class Reply(Base):
    __tablename__ = "replies"

    reply_id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.lead_id"), nullable=False)
    message_id = Column(Integer, ForeignKey("messages.message_id"), nullable=True)
    sender = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    body = Column(Text, nullable=True)
    classification = Column(String, nullable=True)  # INTERESTED, NOT_INTERESTED, QUESTION, FOLLOW_UP, OUT_OF_OFFICE, UNKNOWN
    confidence = Column(Float, nullable=True)
    user_override = Column(String, nullable=True)
    is_demo = Column(Boolean, default=False)
    received_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())

    lead = relationship("Lead", back_populates="replies")


class Source(Base):
    __tablename__ = "sources"

    source_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    source_type = Column(String, nullable=True)  # web_search, manual, excel_import, website_scrape
    url = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())


class BatchJob(Base):
    """Track async Explee API jobs (batch enrichment, find-and-enrich)."""
    __tablename__ = "batch_jobs"

    job_id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, nullable=False)  # Explee task ID
    job_type = Column(String, nullable=False)  # batch_enrich, find_and_enrich
    status = Column(String, default="pending")  # pending, completed, failed
    result_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

