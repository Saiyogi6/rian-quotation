from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import List, Dict, Any
import json

from app.models.models import (
    Quote, Brand, QuoteType, Template, Contact,
    QuoteDetailsJson, QuoteSection, QuoteLineItem,
    Deliverable, PaymentSplit, AddOn
)
from app.schemas.schemas import QuoteCreate

def get_quote_by_id(db: Session, quote_id: int) -> Quote:
    return db.query(Quote).filter(Quote.id == quote_id).first()

def get_quote_by_number(db: Session, quote_number: str) -> Quote:
    return db.query(Quote).filter(Quote.quotation_number == quote_number).first()

def get_all_quotes(db: Session, skip: int = 0, limit: int = 100) -> List[Quote]:
    return db.query(Quote).order_by(Quote.updated_at.desc()).offset(skip).limit(limit).all()

def build_quote_details_dict(quote: Quote) -> Dict[str, str]:
    """Helper to convert detail list into dict"""
    details_dict = {}
    for detail in quote.details:
        details_dict[detail.field_key] = detail.field_value
    return details_dict

def generate_unique_quote_number(db: Session, prefix: str = "RS-") -> str:
    """Generates a unique quote number based on current count or timestamp"""
    count = db.query(Quote).count()
    year = datetime.now().year % 100
    new_number = f"{prefix}{year}{count + 1:04d}"
    
    # Verify uniqueness
    while db.query(Quote).filter(Quote.quotation_number == new_number).first() is not None:
        count += 1
        new_number = f"{prefix}{year}{count + 1:04d}"
    return new_number

def create_quote(db: Session, obj_in: QuoteCreate) -> Quote:
    # 1. Resolve Brand, Template, QuoteType
    brand = db.query(Brand).filter(Brand.id == obj_in.brand_id).first()
    if not brand:
        raise ValueError(f"Brand with id {obj_in.brand_id} not found")
        
    quote_type = db.query(QuoteType).filter(QuoteType.code == obj_in.quote_type_code).first()
    if not quote_type:
        raise ValueError(f"QuoteType with code '{obj_in.quote_type_code}' not found")
        
    template = db.query(Template).filter(Template.id == obj_in.template_id).first()
    if not template:
        raise ValueError(f"Template with id {obj_in.template_id} not found")

    # 2. Handle Contact creation or linking
    contact = db.query(Contact).filter(
        Contact.name == obj_in.client_name,
        Contact.phone == obj_in.client_phone
    ).first()
    
    if not contact:
        contact = Contact(
            name=obj_in.client_name,
            email=obj_in.client_email,
            phone=obj_in.client_phone,
            address=obj_in.client_address
        )
        db.add(contact)
        db.flush() # gets contact.id

    # 3. Calculate Total Amount
    # Sum up selected line items in sections + active add-ons + selected non-complimentary deliverables
    total = 0.0
    for section in obj_in.sections:
        for item in section.line_items:
            if item.is_selected:
                total += float(item.qty) * float(item.unit_price)
            
    for addon in obj_in.add_ons:
        if addon.is_selected:
            total += float(addon.price)

    for deliverable in obj_in.deliverables:
        if deliverable.is_selected and not deliverable.is_complimentary:
            total += float(deliverable.qty or 1) * float(deliverable.price or 0.0)

    # Apply Discount
    discount_amount = 0.0
    discount_val = float(obj_in.discount_value)
    if obj_in.discount_type == "fixed":
        discount_amount = discount_val
    elif obj_in.discount_type == "percentage":
        discount_amount = total * (discount_val / 100.0)
        
    total = max(0.0, total - discount_amount)

    # 4. Create main quote object
    db_quote = Quote(
        quotation_number=obj_in.quotation_number,
        quotation_date=obj_in.quotation_date,
        status=obj_in.status,
        total_amount=total,
        notes=obj_in.notes,
        discount_type=obj_in.discount_type,
        discount_value=obj_in.discount_value,
        intro_content=obj_in.intro_content,
        brand_id=brand.id,
        quote_type_id=quote_type.id,
        template_id=template.id,
        contact_id=contact.id
    )
    db.add(db_quote)
    db.flush() # gets db_quote.id

    # 5. Save quote details json as separate key-value rows
    for key, val in obj_in.details.items():
        detail_row = QuoteDetailsJson(
            quote_id=db_quote.id,
            field_key=key,
            field_value=str(val) if val is not None else ""
        )
        db.add(detail_row)

    # 6. Save Sections and Line Items
    for s_idx, section in enumerate(obj_in.sections):
        db_section = QuoteSection(
            quote_id=db_quote.id,
            title=section.title,
            sort_order=s_idx
        )
        db.add(db_section)
        db.flush()
        
        for i_idx, item in enumerate(section.line_items):
            line_total = float(item.qty) * float(item.unit_price)
            db_item = QuoteLineItem(
                section_id=db_section.id,
                description=item.description,
                qty=item.qty,
                unit_price=item.unit_price,
                total_price=line_total,
                sort_order=i_idx,
                is_selected=item.is_selected,
                group_name=item.group_name,
                display_order=item.display_order,
                item_category=item.item_category
            )
            db.add(db_item)

    # 7. Save Deliverables
    for deliverable in obj_in.deliverables:
        db_deliv = Deliverable(
            quote_id=db_quote.id,
            type=deliverable.type,
            description=deliverable.description,
            qty=deliverable.qty,
            is_selected=deliverable.is_selected,
            price=deliverable.price,
            is_complimentary=deliverable.is_complimentary,
            group_name=deliverable.group_name,
            display_order=deliverable.display_order,
            item_category=deliverable.item_category
        )
        db.add(db_deliv)

    # 8. Save Payment Splits
    for split in obj_in.payment_splits:
        db_split = PaymentSplit(
            quote_id=db_quote.id,
            stage_name=split.stage_name,
            amount=split.amount,
            percentage=split.percentage,
            due_date=split.due_date
        )
        db.add(db_split)

    # 9. Save Add-ons
    for addon in obj_in.add_ons:
        db_addon = AddOn(
            quote_id=db_quote.id,
            description=addon.description,
            price=addon.price,
            is_selected=addon.is_selected
        )
        db.add(db_addon)

    db.commit()
    db.refresh(db_quote)
    return db_quote

def update_quote(db: Session, quote_id: int, obj_in: QuoteCreate) -> Quote:
    db_quote = get_quote_by_id(db, quote_id)
    if not db_quote:
        raise ValueError("Quote not found")

    # 1. Update core info
    db_quote.quotation_date = obj_in.quotation_date
    db_quote.status = obj_in.status
    db_quote.notes = obj_in.notes
    db_quote.template_id = obj_in.template_id
    
    # Update Contact details (link to existing or modify name)
    contact = db_quote.contact
    contact.name = obj_in.client_name
    contact.email = obj_in.client_email
    contact.phone = obj_in.client_phone
    contact.address = obj_in.client_address
    db.add(contact)

    # 2. Recalculate totals
    total = 0.0
    for section in obj_in.sections:
        for item in section.line_items:
            if item.is_selected:
                total += float(item.qty) * float(item.unit_price)
            
    for addon in obj_in.add_ons:
        if addon.is_selected:
            total += float(addon.price)

    for deliverable in obj_in.deliverables:
        if deliverable.is_selected and not deliverable.is_complimentary:
            total += float(deliverable.qty or 1) * float(deliverable.price or 0.0)

    # Apply Discount
    discount_amount = 0.0
    discount_val = float(obj_in.discount_value)
    if obj_in.discount_type == "fixed":
        discount_amount = discount_val
    elif obj_in.discount_type == "percentage":
        discount_amount = total * (discount_val / 100.0)
        
    total = max(0.0, total - discount_amount)
    
    db_quote.total_amount = total
    db_quote.discount_type = obj_in.discount_type
    db_quote.discount_value = obj_in.discount_value
    db_quote.intro_content = obj_in.intro_content

    # 3. Clean and delete previous child relationships (Cascaded via ORM delete-orphan)
    # db_quote.details, db_quote.sections, etc. clear
    db_quote.details.clear()
    db_quote.sections.clear()
    db_quote.deliverables.clear()
    db_quote.payment_splits.clear()
    db_quote.add_ons.clear()
    db.flush()

    # 4. Insert new child relationships
    # Details JSON
    for key, val in obj_in.details.items():
        detail_row = QuoteDetailsJson(
            quote_id=db_quote.id,
            field_key=key,
            field_value=str(val) if val is not None else ""
        )
        db.add(detail_row)

    # Sections & Line Items
    for s_idx, section in enumerate(obj_in.sections):
        db_section = QuoteSection(
            quote_id=db_quote.id,
            title=section.title,
            sort_order=s_idx
        )
        db.add(db_section)
        db.flush()
        
        for i_idx, item in enumerate(section.line_items):
            line_total = float(item.qty) * float(item.unit_price)
            db_item = QuoteLineItem(
                section_id=db_section.id,
                description=item.description,
                qty=item.qty,
                unit_price=item.unit_price,
                total_price=line_total,
                sort_order=i_idx,
                is_selected=item.is_selected,
                group_name=item.group_name,
                display_order=item.display_order,
                item_category=item.item_category
            )
            db.add(db_item)

    # Deliverables
    for deliverable in obj_in.deliverables:
        db_deliv = Deliverable(
            quote_id=db_quote.id,
            type=deliverable.type,
            description=deliverable.description,
            qty=deliverable.qty,
            is_selected=deliverable.is_selected,
            price=deliverable.price,
            is_complimentary=deliverable.is_complimentary,
            group_name=deliverable.group_name,
            display_order=deliverable.display_order,
            item_category=deliverable.item_category
        )
        db.add(db_deliv)

    # Payment Splits
    for split in obj_in.payment_splits:
        db_split = PaymentSplit(
            quote_id=db_quote.id,
            stage_name=split.stage_name,
            amount=split.amount,
            percentage=split.percentage,
            due_date=split.due_date
        )
        db.add(db_split)

    # Add-ons
    for addon in obj_in.add_ons:
        db_addon = AddOn(
            quote_id=db_quote.id,
            description=addon.description,
            price=addon.price,
            is_selected=addon.is_selected
        )
        db.add(db_addon)

    db_quote.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_quote)
    return db_quote

def duplicate_quote(db: Session, quote_id: int) -> Quote:
    original = get_quote_by_id(db, quote_id)
    if not original:
        raise ValueError("Original quote not found")

    new_number = generate_unique_quote_number(db, prefix="RS-DUP-")
    
    # Create copy of main quote
    duplicated = Quote(
        quotation_number=new_number,
        quotation_date=date.today(),
        status="draft",
        total_amount=original.total_amount,
        notes=original.notes,
        discount_type=original.discount_type,
        discount_value=original.discount_value,
        intro_content=original.intro_content,
        brand_id=original.brand_id,
        quote_type_id=original.quote_type_id,
        template_id=original.template_id,
        contact_id=original.contact_id
    )
    db.add(duplicated)
    db.flush()

    # Duplicate Details
    for detail in original.details:
        new_detail = QuoteDetailsJson(
            quote_id=duplicated.id,
            field_key=detail.field_key,
            field_value=detail.field_value
        )
        db.add(new_detail)

    # Duplicate Sections & Line Items
    for section in original.sections:
        new_section = QuoteSection(
            quote_id=duplicated.id,
            title=section.title,
            sort_order=section.sort_order
        )
        db.add(new_section)
        db.flush()
        
        for item in section.line_items:
            new_item = QuoteLineItem(
                section_id=new_section.id,
                description=item.description,
                qty=item.qty,
                unit_price=item.unit_price,
                total_price=item.total_price,
                sort_order=item.sort_order,
                is_selected=item.is_selected,
                group_name=item.group_name,
                display_order=item.display_order,
                item_category=item.item_category
            )
            db.add(new_item)

    # Duplicate Deliverables
    for deliv in original.deliverables:
        new_deliv = Deliverable(
            quote_id=duplicated.id,
            type=deliv.type,
            description=deliv.description,
            qty=deliv.qty,
            is_selected=deliv.is_selected,
            price=deliv.price,
            is_complimentary=deliv.is_complimentary,
            group_name=deliv.group_name,
            display_order=deliv.display_order,
            item_category=deliv.item_category
        )
        db.add(new_deliv)

    # Duplicate Payment Splits
    for split in original.payment_splits:
        new_split = PaymentSplit(
            quote_id=duplicated.id,
            stage_name=split.stage_name,
            amount=split.amount,
            percentage=split.percentage,
            due_date=split.due_date
        )
        db.add(new_split)

    # Duplicate Addons
    for addon in original.add_ons:
        new_addon = AddOn(
            quote_id=duplicated.id,
            description=addon.description,
            price=addon.price,
            is_selected=addon.is_selected
        )
        db.add(new_addon)

    db.commit()
    db.refresh(duplicated)
    return duplicated

def update_quote_status(db: Session, quote_id: int, status: str) -> Quote:
    db_quote = get_quote_by_id(db, quote_id)
    if not db_quote:
        raise ValueError("Quote not found")
    
    db_quote.status = status
    db_quote.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_quote)
    return db_quote

def save_quote_pdf_path(db: Session, quote_id: int, pdf_path: str) -> Quote:
    db_quote = get_quote_by_id(db, quote_id)
    if not db_quote:
        raise ValueError("Quote not found")
    db_quote.pdf_path = pdf_path
    db.commit()
    return db_quote
