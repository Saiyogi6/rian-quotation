from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Brand(Base):
    __tablename__ = "brands"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    logo_path = Column(String(255), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    website = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    terms_and_conditions = Column(Text, nullable=True)
    payment_info = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    quotes = relationship("Quote", back_populates="brand")

class QuoteType(Base):
    __tablename__ = "quote_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True) # e.g. wedding, retirement, convocation_ad, election, custom
    fields_schema = Column(Text, nullable=True) # Stores JSON schema describing dynamic fields

    quotes = relationship("Quote", back_populates="quote_type")

class Template(Base):
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    html_content = Column(Text, nullable=False)
    
    quotes = relationship("Quote", back_populates="template")

class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    quotes = relationship("Quote", back_populates="contact")

class Quote(Base):
    __tablename__ = "quotes"
    
    id = Column(Integer, primary_key=True, index=True)
    quotation_number = Column(String(50), unique=True, nullable=False, index=True)
    quotation_date = Column(Date, nullable=False)
    status = Column(String(20), default="draft", nullable=False) # draft, sent, approved, cancelled
    total_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    pdf_path = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    
    # New discount fields and intro content
    discount_type = Column(String(20), default="none", nullable=False)
    discount_value = Column(Numeric(12, 2), default=0.00, nullable=False)
    intro_content = Column(Text, nullable=True)
    
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    quote_type_id = Column(Integer, ForeignKey("quote_types.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    brand = relationship("Brand", back_populates="quotes")
    quote_type = relationship("QuoteType", back_populates="quotes")
    template = relationship("Template", back_populates="quotes")
    contact = relationship("Contact", back_populates="quotes")
    
    details = relationship("QuoteDetailsJson", back_populates="quote", cascade="all, delete-orphan")
    sections = relationship("QuoteSection", back_populates="quote", order_by="QuoteSection.sort_order", cascade="all, delete-orphan")
    deliverables = relationship("Deliverable", back_populates="quote", cascade="all, delete-orphan")
    payment_splits = relationship("PaymentSplit", back_populates="quote", cascade="all, delete-orphan")
    add_ons = relationship("AddOn", back_populates="quote", cascade="all, delete-orphan")

class QuoteDetailsJson(Base):
    __tablename__ = "quote_details_json"
    
    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id", ondelete="CASCADE"), nullable=False)
    field_key = Column(String(100), nullable=False)
    field_value = Column(Text, nullable=True)
    
    quote = relationship("Quote", back_populates="details")

class QuoteSection(Base):
    __tablename__ = "quote_sections"
    
    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(100), nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    
    quote = relationship("Quote", back_populates="sections")
    line_items = relationship("QuoteLineItem", back_populates="section", order_by="QuoteLineItem.sort_order", cascade="all, delete-orphan")

class QuoteLineItem(Base):
    __tablename__ = "quote_line_items"
    
    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("quote_sections.id", ondelete="CASCADE"), nullable=False)
    description = Column(String(255), nullable=False)
    qty = Column(Numeric(10, 2), default=1.00, nullable=False)
    unit_price = Column(Numeric(12, 2), default=0.00, nullable=False)
    total_price = Column(Numeric(12, 2), default=0.00, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    
    # New fields for checklist, category and ordering
    is_selected = Column(Boolean, default=True, nullable=False)
    group_name = Column(String(100), nullable=True)
    display_order = Column(Integer, default=0, nullable=False)
    item_category = Column(String(50), nullable=True)
    
    section = relationship("QuoteSection", back_populates="line_items")

class Deliverable(Base):
    __tablename__ = "deliverables"
    
    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False) # e.g. photo, video, album, turnaround, other
    description = Column(Text, nullable=False)
    qty = Column(Integer, nullable=True)
    
    # New fields for checklist, category, pricing, complimentary, and ordering
    is_selected = Column(Boolean, default=True, nullable=False)
    price = Column(Numeric(12, 2), default=0.00, nullable=False)
    is_complimentary = Column(Boolean, default=False, nullable=False)
    group_name = Column(String(100), nullable=True)
    display_order = Column(Integer, default=0, nullable=False)
    item_category = Column(String(50), nullable=True)
    
    quote = relationship("Quote", back_populates="deliverables")

class PaymentSplit(Base):
    __tablename__ = "payment_splits"
    
    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id", ondelete="CASCADE"), nullable=False)
    stage_name = Column(String(100), nullable=False) # e.g. advance, event, final
    amount = Column(Numeric(12, 2), nullable=False)
    percentage = Column(Numeric(5, 2), nullable=True)
    due_date = Column(String(100), nullable=True)
    
    quote = relationship("Quote", back_populates="payment_splits")

class AddOn(Base):
    __tablename__ = "add_ons"
    
    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id", ondelete="CASCADE"), nullable=False)
    description = Column(String(255), nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    is_selected = Column(Boolean, default=True, nullable=False)
    
    quote = relationship("Quote", back_populates="add_ons")
