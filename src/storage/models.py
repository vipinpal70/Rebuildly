import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey, UniqueConstraint
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
    # Operator-curated extra pages (team, contact-us, about-us, or any URL) that
    # enrich_lead always reads on top of whatever BusinessResearcher auto-discovers —
    # [{"url": str, "label": str}, ...]. See src/scraper/business_researcher.py.
    additional_urls = Column(JSON, nullable=True)

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
    # Accumulated admin feedback from past regenerations — [{"text": str, "created_at": str}, ...].
    # Every regeneration re-reads the FULL history (not just the latest note), so
    # earlier feedback keeps being honored rather than getting overwritten each time.
    regeneration_feedback = Column(JSON, nullable=True)
    # Extra entropy for the archetype/layout hash seed. Without this, regenerating
    # a site is a pure function of business_id+name and produces an IDENTICAL
    # design every time — clicking "Regenerate" silently did nothing visually.
    regeneration_count = Column(Integer, default=0, nullable=False)

    business = relationship("BusinessModel")


class ClientSiteVersionModel(Base):
    """Immutable snapshot of a client site archived right before a regeneration
    overwrites it, so every past design stays browsable — by the admin and, via
    a public /sites/{slug}/v/{n} URL, by the client too — instead of only ever
    being able to see the latest version."""
    __tablename__ = "client_site_versions"
    __table_args__ = (
        UniqueConstraint("site_id", "version_number", name="uq_client_site_versions_site_version"),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id = Column(String, ForeignKey("client_sites.id", ondelete="CASCADE"), nullable=False, index=True)
    slug = Column(String(255), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    archetype = Column(String(100), nullable=True)
    site_config = Column(JSON, nullable=False)
    # regeneration_feedback as it stood when THIS version was the live one — lets
    # the history view show which admin note produced which design.
    feedback_snapshot = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


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
    buying_power_score = Column(Integer, default=0, nullable=False)
    tier = Column(String(50), nullable=False)
    score_breakdown = Column(JSON, nullable=True)
    audited_at = Column(DateTime, default=datetime.utcnow)

    business = relationship("BusinessModel", back_populates="audits")


class AppSettingModel(Base):
    """Admin-editable runtime settings (e.g. the LLM provider/key), one JSON document per key.
    Secrets inside `value` are Fernet-encrypted by src/llm/config.py before being stored."""
    __tablename__ = "app_settings"

    key = Column(String(100), primary_key=True)
    value = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SignalFindingModel(Base):
    """One evidence-backed finding from a signal detector (see src/signals). Findings are
    replaced wholesale each time a business is re-analysed, so the table always reflects
    the latest run."""
    __tablename__ = "signal_findings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    detector = Column(String(50), nullable=False)
    signal_type = Column(String(100), nullable=False, index=True)
    severity = Column(String(20), nullable=False)
    title = Column(String(500), nullable=False)
    detail = Column(Text, nullable=True)
    evidence = Column(JSON, nullable=True)
    offers = Column(JSON, nullable=True)  # ["analytics_setup", ...]
    detected_at = Column(DateTime, default=datetime.utcnow)


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
    # Job title of contact_name (e.g. "Owner", "Practice Manager"), set when auto-resolved
    # from the scraped team page — see src/outreach/contact_resolver.py.
    decision_maker_role = Column(String(255), nullable=True)

    # 0-100: how confidently we can reach a real decision-maker (name/email/LinkedIn found).
    contactability_score = Column(Integer, default=0, nullable=False)
    # Weighted blend of modernization + buying power + contactability — see contact_resolver.py.
    composite_lead_score = Column(Integer, nullable=True)

    outreach_status = Column(String(50), default="NEW", nullable=False, index=True)
    # Statuses: NEW, VIEWED, LINKEDIN_SENT, EMAIL_SENT, WA_SENT, CALLED, HOT_ENGAGED,
    # REPLIED, MEETING_BOOKED, CONVERTED, OPTED_OUT
    # HOT_ENGAGED is set automatically (see src/outreach/click_tracker.py) when a prospect
    # revisits their preview link after being contacted. REPLIED/MEETING_BOOKED are set
    # manually via POST /admin/crm/leads/{id}/status to record inbound response, distinct
    # from the outbound *_SENT statuses.

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

