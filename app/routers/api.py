from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging

from app.core.database import get_db
from app.schemas.schemas import (
    QuoteCreate, QuoteResponse, SettingsUpdate, BrandResponse,
    QuoteTypeResponse, ContactResponse, SectionResponse,
    DeliverableResponse, PaymentSplitResponse, AddOnResponse
)
from app.models.models import Quote, QuoteType, Brand, Template
from app.services import quote as quote_service
from app.services import pdf as pdf_service
from app.services import webhook as webhook_service
from app.core.config import settings

logger = logging.getLogger("app.routers.api")

router = APIRouter(prefix="/api")

def to_quote_response(db_quote: Quote) -> QuoteResponse:
    """Helper to convert a DB Quote model to a QuoteResponse Pydantic schema manually"""
    details_dict = quote_service.build_quote_details_dict(db_quote)
    
    # Manually compile sections with items
    sections_response = []
    for s in db_quote.sections:
        items = []
        for item in s.line_items:
            items.append(
                LineItemResponse(
                    id=item.id,
                    section_id=item.section_id,
                    description=item.description,
                    qty=item.qty,
                    unit_price=item.unit_price,
                    total_price=item.total_price,
                    is_selected=item.is_selected,
                    group_name=item.group_name,
                    display_order=item.display_order,
                    item_category=item.item_category
                )
            )
        sections_response.append(
            SectionResponse(
                id=s.id,
                title=s.title,
                sort_order=s.sort_order,
                line_items=items
            )
        )
        
    return QuoteResponse(
        id=db_quote.id,
        quotation_number=db_quote.quotation_number,
        quotation_date=db_quote.quotation_date,
        status=db_quote.status,
        total_amount=db_quote.total_amount,
        pdf_path=db_quote.pdf_path,
        notes=db_quote.notes,
        discount_type=db_quote.discount_type,
        discount_value=db_quote.discount_value,
        intro_content=db_quote.intro_content,
        brand=BrandResponse.model_validate(db_quote.brand),
        quote_type=QuoteTypeResponse.model_validate(db_quote.quote_type),
        contact=ContactResponse.model_validate(db_quote.contact),
        details=details_dict,
        sections=sections_response,
        deliverables=[
            DeliverableResponse(
                id=d.id,
                type=d.type,
                description=d.description,
                qty=d.qty,
                is_selected=d.is_selected,
                price=d.price,
                is_complimentary=d.is_complimentary,
                group_name=d.group_name,
                display_order=d.display_order,
                item_category=d.item_category
            ) for d in db_quote.deliverables
        ],
        payment_splits=[PaymentSplitResponse.model_validate(p) for p in db_quote.payment_splits],
        add_ons=[AddOnResponse.model_validate(a) for a in db_quote.add_ons],
        created_at=db_quote.created_at,
        updated_at=db_quote.updated_at
    )

# Import LineItemResponse here so to_quote_response can instantiate it
from app.schemas.schemas import LineItemResponse

@router.get("/quote-types")
def get_quote_types(db: Session = Depends(get_db)):
    types = db.query(QuoteType).all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "code": t.code,
            "fields_schema": t.fields_schema
        }
        for t in types
    ]

@router.get("/quotes", response_model=List[QuoteResponse])
def read_quotes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_quotes = quote_service.get_all_quotes(db, skip=skip, limit=limit)
    return [to_quote_response(q) for q in db_quotes]

@router.get("/quotes/{quote_id}", response_model=QuoteResponse)
def read_quote(quote_id: int, db: Session = Depends(get_db)):
    db_quote = quote_service.get_quote_by_id(db, quote_id)
    if not db_quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    return to_quote_response(db_quote)

@router.post("/quotes", response_model=QuoteResponse)
def create_quote(quote_in: QuoteCreate, db: Session = Depends(get_db)):
    try:
        # Generate quotation number if not provided or empty
        if not quote_in.quotation_number or quote_in.quotation_number.strip() == "":
            quote_in.quotation_number = quote_service.generate_unique_quote_number(db)
            
        db_quote = quote_service.create_quote(db, quote_in)
        return to_quote_response(db_quote)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating quote: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/quotes/{quote_id}", response_model=QuoteResponse)
def update_quote(quote_id: int, quote_in: QuoteCreate, db: Session = Depends(get_db)):
    try:
        db_quote = quote_service.update_quote(db, quote_id, quote_in)
        return to_quote_response(db_quote)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating quote: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/quotes/{quote_id}/duplicate", response_model=QuoteResponse)
def duplicate_quote(quote_id: int, db: Session = Depends(get_db)):
    try:
        db_quote = quote_service.duplicate_quote(db, quote_id)
        return to_quote_response(db_quote)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error duplicating quote: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/quotes/{quote_id}/status")
def update_status(quote_id: int, payload: Dict[str, str], db: Session = Depends(get_db)):
    status_val = payload.get("status")
    if not status_val or status_val not in ["draft", "sent", "approved", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status value")
        
    try:
        db_quote = quote_service.update_quote_status(db, quote_id, status_val)
        return {"status": "success", "quote_id": db_quote.id, "new_status": db_quote.status}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/quotes/{quote_id}/export-pdf")
def export_pdf(quote_id: int, db: Session = Depends(get_db)):
    db_quote = quote_service.get_quote_by_id(db, quote_id)
    if not db_quote:
        raise HTTPException(status_code=404, detail="Quote not found")
        
    try:
        from app.routers.pages import render_quote_to_html
        
        # Render HTML
        html_content = render_quote_to_html(db_quote, db)
        
        # Define output filename
        filename = f"Quotation_{db_quote.quotation_number.replace('-', '_')}.pdf"
        
        # Compile PDF
        pdf_relative_path = pdf_service.generate_pdf_from_html(html_content, filename)
        
        # Save PDF path in database
        quote_service.save_quote_pdf_path(db, db_quote.id, pdf_relative_path)
        
        # Trigger n8n webhook
        if settings.WEBHOOK_URL:
            q_resp = to_quote_response(db_quote)
            webhook_service.trigger_n8n_webhook(
                payload=q_resp.dict(),
                pdf_url=pdf_relative_path
            )
            
        return {"status": "success", "pdf_path": pdf_relative_path}
    except Exception as e:
        logger.error(f"Failed to export PDF: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@router.get("/settings")
def get_settings(db: Session = Depends(get_db)):
    brand = db.query(Brand).first()
    return {
        "webhook_url": settings.WEBHOOK_URL,
        "brand": brand
    }

@router.put("/settings")
def update_settings(payload: SettingsUpdate, db: Session = Depends(get_db)):
    brand = db.query(Brand).first()
    if not brand:
        brand = Brand()
        db.add(brand)
        
    # Update brand info
    brand.name = payload.brand.name
    brand.email = payload.brand.email
    brand.phone = payload.brand.phone
    brand.website = payload.brand.website
    brand.address = payload.brand.address
    brand.terms_and_conditions = payload.brand.terms_and_conditions
    brand.payment_info = payload.brand.payment_info
    brand.presets_json = payload.brand.presets_json
    
    # Update webhook settings
    import os
    settings.WEBHOOK_URL = payload.webhook_url or ""
    os.environ["WEBHOOK_URL"] = settings.WEBHOOK_URL
    
    db.commit()
    db.refresh(brand)
    
    return {
        "webhook_url": settings.WEBHOOK_URL,
        "brand": brand
    }

@router.post("/webhook-receiver")
def webhook_receiver(payload: Dict[str, Any]):
    logger.info(f"Received Webhook event: {payload.get('event')}")
    logger.info(f"PDF URL: {payload.get('pdf_url')}")
    return {"status": "received", "event": payload.get("event")}
