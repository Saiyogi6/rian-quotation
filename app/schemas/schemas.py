from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict
from datetime import date, datetime
from decimal import Decimal

# Brand Schemas
class BrandBase(BaseModel):
    name: str
    logo_path: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    payment_info: Optional[str] = None

class BrandResponse(BrandBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Contact Schemas
class ContactBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class ContactResponse(ContactBase):
    id: int

    class Config:
        from_attributes = True

# Quote Type Schemas
class QuoteTypeResponse(BaseModel):
    id: int
    name: str
    code: str
    fields_schema: Optional[str] = None

    class Config:
        from_attributes = True

# Line Item Schemas
class LineItemBase(BaseModel):
    description: str
    qty: Decimal = Decimal('1.00')
    unit_price: Decimal = Decimal('0.00')
    total_price: Optional[Decimal] = None
    is_selected: bool = True
    group_name: Optional[str] = None
    display_order: int = 0
    item_category: Optional[str] = None

class LineItemCreate(LineItemBase):
    pass

class LineItemResponse(LineItemBase):
    id: int
    section_id: int

    class Config:
        from_attributes = True

# Section Schemas
class SectionBase(BaseModel):
    title: str
    sort_order: int = 0

class SectionCreate(SectionBase):
    line_items: List[LineItemCreate] = []

class SectionResponse(SectionBase):
    id: int
    line_items: List[LineItemResponse] = []

    class Config:
        from_attributes = True

# Deliverables
class DeliverableBase(BaseModel):
    type: str # photo, video, album, turnaround, other
    description: str
    qty: Optional[int] = None
    is_selected: bool = True
    price: Decimal = Decimal('0.00')
    is_complimentary: bool = False
    group_name: Optional[str] = None
    display_order: int = 0
    item_category: Optional[str] = None

class DeliverableCreate(DeliverableBase):
    pass

class DeliverableResponse(DeliverableBase):
    id: int

    class Config:
        from_attributes = True

# Payment Split
class PaymentSplitBase(BaseModel):
    stage_name: str
    amount: Decimal
    percentage: Optional[Decimal] = None
    due_date: Optional[str] = None

class PaymentSplitCreate(PaymentSplitBase):
    pass

class PaymentSplitResponse(PaymentSplitBase):
    id: int

    class Config:
        from_attributes = True

# Add-on
class AddOnBase(BaseModel):
    description: str
    price: Decimal
    is_selected: bool = True

class AddOnCreate(AddOnBase):
    pass

class AddOnResponse(AddOnBase):
    id: int

    class Config:
        from_attributes = True

# Details JSON field key-value
class DetailItem(BaseModel):
    key: str
    value: str

# Master Quote Schema
class QuoteCreate(BaseModel):
    quotation_number: str
    quotation_date: date
    status: str = "draft" # draft, sent, approved, cancelled
    notes: Optional[str] = None
    discount_type: str = "none"
    discount_value: Decimal = Decimal('0.00')
    intro_content: Optional[str] = None
    
    brand_id: int
    quote_type_code: str # e.g. "wedding" -> we will map to quote_type_id
    template_id: int
    
    # Nested Client Data
    client_name: str
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    client_address: Optional[str] = None
    
    # Dynamic fields
    details: Dict[str, str] = {} # e.g. {"groom_name": "John", "bride_name": "Jane"}
    
    # Nested Items
    sections: List[SectionCreate] = []
    deliverables: List[DeliverableCreate] = []
    payment_splits: List[PaymentSplitCreate] = []
    add_ons: List[AddOnCreate] = []

class QuoteResponse(BaseModel):
    id: int
    quotation_number: str
    quotation_date: date
    status: str
    total_amount: Decimal
    pdf_path: Optional[str] = None
    notes: Optional[str] = None
    discount_type: str
    discount_value: Decimal
    intro_content: Optional[str] = None
    
    brand: BrandResponse
    quote_type: QuoteTypeResponse
    contact: ContactResponse
    
    details: Dict[str, str] = {}
    sections: List[SectionResponse] = []
    deliverables: List[DeliverableResponse] = []
    payment_splits: List[PaymentSplitResponse] = []
    add_ons: List[AddOnResponse] = []
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        
# Settings Schema
class SettingsUpdate(BaseModel):
    webhook_url: Optional[str] = None
    brand: BrandBase
