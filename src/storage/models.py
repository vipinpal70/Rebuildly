import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class BusinessModel(Base):
    __tablename__ = "businesses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    place_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    address = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    website = Column(String(500), nullable=True)
    google_rating = Column(Float, nullable=True)
    review_count = Column(Integer, default=0)
    google_maps_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    audits = relationship("AuditModel", back_populates="business", cascade="all, delete-orphan")
    outreach = relationship("OutreachLeadModel", back_populates="business", uselist=False, cascade="all, delete-orphan")


class AdminUserModel(Base):
    __tablename__ = "admin_users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="admin", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ClientSiteModel(Base):
    """A generated dynamic client website tracked in the DB (google map, website,
    archetype, preview url and full render config) so the dashboard can list them."""
    __tablename__ = "client_sites"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    archetype = Column(String(100), nullable=True)
    website = Column(String(500), nullable=True)
    google_maps_url = Column(String(500), nullable=True)
    preview_url = Column(String(500), nullable=True)
    status = Column(String(50), default="GENERATED", nullable=False, index=True)
    site_config = Column(JSON, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)

    business = relationship("BusinessModel")


class AuditModel(Base):
    __tablename__ = "audits"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    is_accessible = Column(Boolean, default=True)
    has_ssl = Column(Boolean, default=False)
    is_mobile_responsive = Column(Boolean, default=True)
    has_horizontal_overflow = Column(Boolean, default=False)
    pagespeed_score = Column(Integer, default=50)
    has_meta_title = Column(Boolean, default=False)
    has_meta_description = Column(Boolean, default=False)
    has_h1_tag = Column(Boolean, default=False)
    has_schema_markup = Column(Boolean, default=False)
    has_online_booking = Column(Boolean, default=False)
    has_ai_chatbot = Column(Boolean, default=False)
    has_review_widget = Column(Boolean, default=False)
    modernization_score = Column(Integer, nullable=False)
    tier = Column(String(50), nullable=False)
    score_breakdown = Column(JSON, nullable=True)
    audited_at = Column(DateTime, default=datetime.utcnow)

    business = relationship("BusinessModel", back_populates="audits")


class OutreachLeadModel(Base):
    """Tracks outreach campaigns, AI generated drafts for 4 channels (LinkedIn, Email, WhatsApp, Call),
    and CRM engagement status per lead."""
    __tablename__ = "outreach_leads"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String, ForeignKey("businesses.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    contact_name = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    
    outreach_status = Column(String(50), default="NEW", nullable=False, index=True)
    # Statuses: NEW, LINKEDIN_SENT, EMAIL_SENT, WA_SENT, CALLED, CONVERTED, OPTED_OUT

    linkedin_draft = Column(Text, nullable=True)
    email_subject_draft = Column(String(500), nullable=True)
    email_body_draft = Column(Text, nullable=True)
    whatsapp_draft = Column(Text, nullable=True)
    call_script_notes = Column(Text, nullable=True)

    preview_clicked = Column(Boolean, default=False)
    click_count = Column(Integer, default=0)
    last_clicked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    business = relationship("BusinessModel", back_populates="outreach")
    logs = relationship("OutreachLogModel", back_populates="lead", cascade="all, delete-orphan")


class OutreachLogModel(Base):
    """Log entry for every channel interaction (manual email sent, LinkedIn note copied, WhatsApp opened, Call logged)."""
    __tablename__ = "outreach_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    outreach_lead_id = Column(String, ForeignKey("outreach_leads.id", ondelete="CASCADE"), nullable=False, index=True)
    channel = Column(String(50), nullable=False) # LINKEDIN, EMAIL, WHATSAPP, CALL
    action = Column(String(100), nullable=False) # MANUAL_EMAIL_SENT, LINKEDIN_COPIED, WA_OPENED, CALLED, LINK_CLICKED
    sent_subject = Column(String(500), nullable=True)
    sent_body = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    lead = relationship("OutreachLeadModel", back_populates="logs")


class SuppressionModel(Base):
    """Opt-out / Unsubscribe suppression list across all 4 outreach channels."""
    __tablename__ = "suppression_list"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email_or_phone = Column(String(255), unique=True, nullable=False, index=True)
    reason = Column(String(255), default="USER_OPT_OUT")
    added_at = Column(DateTime, default=datetime.utcnow)

