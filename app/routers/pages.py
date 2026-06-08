from fastapi import APIRouter, Request, Depends, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os

from app.core.database import get_db
from app.models.models import Quote, Brand, QuoteType, Template
from app.services import quote as quote_service
from app.core.config import settings

from datetime import date

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
templates.env.globals['date'] = date

# Simple helper to verify if user is logged in
def is_authenticated(request: Request) -> bool:
    return request.cookies.get("session_id") == "logged_in"

def auth_required(request: Request):
    if not is_authenticated(request):
        raise HTTPException(status_code=302, detail="Redirecting to login")


@router.get("/login", response_class=HTMLResponse)
def get_login(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/")
    return templates.TemplateResponse(request=request, name="login.html", context={"error": None})

@router.post("/login")
async def post_login(request: Request, response: Response):
    form_data = await request.form()
    username = form_data.get("username")
    password = form_data.get("password")
    
    if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
        redirect = RedirectResponse(url="/", status_code=303)
        redirect.set_cookie(key="session_id", value="logged_in", httponly=True)
        return redirect
    
    return templates.TemplateResponse(request=request, name="login.html", context={
        "error": "Invalid username or password"
    })

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("session_id")
    return response

@router.get("/", response_class=HTMLResponse)
def get_dashboard(request: Request, db: Session = Depends(get_db)):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")
        
    quotes = quote_service.get_all_quotes(db)
    
    # Format dates and states for the UI list
    formatted_quotes = []
    for q in quotes:
        details_dict = quote_service.build_quote_details_dict(q)
        formatted_quotes.append({
            "id": q.id,
            "quotation_number": q.quotation_number,
            "quotation_date": q.quotation_date.strftime("%d %b %Y") if q.quotation_date else "",
            "client_name": q.contact.name,
            "quote_type": q.quote_type.name,
            "quote_type_code": q.quote_type.code,
            "total_amount": f"{q.total_amount:,.2f}",
            "status": q.status,
            "pdf_path": q.pdf_path
        })
        
    return templates.TemplateResponse(request=request, name="dashboard.html", context={
        "quotes": formatted_quotes
    })

@router.get("/quotes/new", response_class=HTMLResponse)
def new_quote(request: Request, type: str = "wedding", db: Session = Depends(get_db)):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")
        
    # Get all brand and type presets
    brand = db.query(Brand).first()
    quote_types = db.query(QuoteType).all()
    selected_type = db.query(QuoteType).filter(QuoteType.code == type).first()
    
    if not selected_type:
        selected_type = quote_types[0] if quote_types else None
        
    templates_list = db.query(Template).all()
    
    # Generate a draft quote number
    draft_number = quote_service.generate_unique_quote_number(db)
    
    return templates.TemplateResponse(request=request, name="quote_form.html", context={
        "brand": brand,
        "quote_types": quote_types,
        "selected_type": selected_type,
        "templates": templates_list,
        "draft_number": draft_number,
        "quote": None,
        "is_edit": False
    })

@router.get("/quotes/{quote_id}/edit", response_class=HTMLResponse)
def edit_quote(request: Request, quote_id: int, db: Session = Depends(get_db)):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")
        
    db_quote = quote_service.get_quote_by_id(db, quote_id)
    if not db_quote:
        raise HTTPException(status_code=404, detail="Quote not found")
        
    brand = db.query(Brand).first()
    quote_types = db.query(QuoteType).all()
    templates_list = db.query(Template).all()
    
    # Map details to simple dictionary
    details_dict = quote_service.build_quote_details_dict(db_quote)
    
    return templates.TemplateResponse(request=request, name="quote_form.html", context={
        "brand": brand,
        "quote_types": quote_types,
        "selected_type": db_quote.quote_type,
        "templates": templates_list,
        "quote": db_quote,
        "details": details_dict,
        "is_edit": True
    })

@router.get("/quotes/{quote_id}/preview", response_class=HTMLResponse)
def preview_quote(request: Request, quote_id: int, db: Session = Depends(get_db)):
    # Preview page should be accessible without login so PDF generator or external systems can fetch it easily
    # (or we can secure it if needed, but since it's read-only document presentation it's fine)
    db_quote = quote_service.get_quote_by_id(db, quote_id)
    if not db_quote:
        raise HTTPException(status_code=404, detail="Quote not found")
        
    details_dict = quote_service.build_quote_details_dict(db_quote)
    
    import json
    fields_config = []
    if db_quote.quote_type and db_quote.quote_type.fields_schema:
        try:
            schema_data = json.loads(db_quote.quote_type.fields_schema)
            fields_config = schema_data.get("fields", [])
        except Exception:
            pass
            
    # Calculate sorted components
    sorted_sections = []
    selected_packages_total = 0.0
    for section in db_quote.sections:
        selected_items = [item for item in section.line_items if item.is_selected]
        selected_items.sort(key=lambda x: (x.display_order, x.sort_order or 0))
        for item in selected_items:
            selected_packages_total += float(item.qty) * float(item.unit_price)
        if selected_items:
            sorted_sections.append({
                "title": section.title,
                "line_items": selected_items
            })
            
    # Filter and sort deliverables
    selected_deliverables = [d for d in db_quote.deliverables if d.is_selected]
    selected_paid_deliverables_total = 0.0
    grouped_deliverables = {}
    for d in selected_deliverables:
        if not d.is_complimentary:
            selected_paid_deliverables_total += float(d.qty or 1) * float(d.price or 0.0)
        g_name = d.group_name or d.type.capitalize()
        if g_name not in grouped_deliverables:
            grouped_deliverables[g_name] = []
        grouped_deliverables[g_name].append(d)
        
    for g_name in grouped_deliverables:
        grouped_deliverables[g_name].sort(key=lambda x: (x.display_order, x.id or 0))
        
    sorted_groups = sorted(grouped_deliverables.keys())
    sorted_deliverables = [{"group_name": g, "items": grouped_deliverables[g]} for g in sorted_groups]
    
    # Subtotal
    subtotal = selected_packages_total + selected_paid_deliverables_total
    
    # Addons
    active_addons = [add for add in db_quote.add_ons if add.is_selected]
    addons_total = sum(float(add.price) for add in active_addons)
    
    # Total before discount
    total_before_discount = subtotal + addons_total
    
    # Discount
    discount_amount = 0.0
    discount_val = float(db_quote.discount_value)
    if db_quote.discount_type == "fixed":
        discount_amount = discount_val
    elif db_quote.discount_type == "percentage":
        discount_amount = total_before_discount * (discount_val / 100.0)
        
    total_formatted = f"{db_quote.total_amount:,.2f}"
    
    return templates.TemplateResponse(request=request, name="quote_preview.html", context={
        "quote": db_quote,
        "details": details_dict,
        "fields_config": fields_config,
        "total_formatted": total_formatted,
        "is_pdf": False,
        "sorted_sections": sorted_sections,
        "sorted_deliverables": sorted_deliverables,
        "subtotal": subtotal,
        "active_addons": active_addons,
        "addons_total": addons_total,
        "discount_amount": discount_amount
    })

@router.get("/settings", response_class=HTMLResponse)
def get_settings_page(request: Request, db: Session = Depends(get_db)):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")
        
    brand = db.query(Brand).first()
    return templates.TemplateResponse(request=request, name="settings.html", context={
        "brand": brand,
        "webhook_url": settings.WEBHOOK_URL
    })

# Helper function to render a quote to HTML string (used by PDF exporter)
def render_quote_to_html(quote: Quote, db: Session) -> str:
    details_dict = quote_service.build_quote_details_dict(quote)
    
    # Calculate sorted components
    sorted_sections = []
    selected_packages_total = 0.0
    for section in quote.sections:
        selected_items = [item for item in section.line_items if item.is_selected]
        selected_items.sort(key=lambda x: (x.display_order, x.sort_order or 0))
        for item in selected_items:
            selected_packages_total += float(item.qty) * float(item.unit_price)
        if selected_items:
            sorted_sections.append({
                "title": section.title,
                "line_items": selected_items
            })
            
    # Filter and sort deliverables
    selected_deliverables = [d for d in quote.deliverables if d.is_selected]
    selected_paid_deliverables_total = 0.0
    grouped_deliverables = {}
    for d in selected_deliverables:
        if not d.is_complimentary:
            selected_paid_deliverables_total += float(d.qty or 1) * float(d.price or 0.0)
        g_name = d.group_name or d.type.capitalize()
        if g_name not in grouped_deliverables:
            grouped_deliverables[g_name] = []
        grouped_deliverables[g_name].append(d)
        
    for g_name in grouped_deliverables:
        grouped_deliverables[g_name].sort(key=lambda x: (x.display_order, x.id or 0))
        
    sorted_groups = sorted(grouped_deliverables.keys())
    sorted_deliverables = [{"group_name": g, "items": grouped_deliverables[g]} for g in sorted_groups]
    
    # Subtotal
    subtotal = selected_packages_total + selected_paid_deliverables_total
    
    # Addons
    active_addons = [add for add in quote.add_ons if add.is_selected]
    addons_total = sum(float(add.price) for add in active_addons)
    
    # Total before discount
    total_before_discount = subtotal + addons_total
    
    # Discount
    discount_amount = 0.0
    discount_val = float(quote.discount_value)
    if quote.discount_type == "fixed":
        discount_amount = discount_val
    elif quote.discount_type == "percentage":
        discount_amount = total_before_discount * (discount_val / 100.0)
        
    total_formatted = f"{quote.total_amount:,.2f}"
    
    # We render the template directly from jinja
    template_obj = templates.get_template("quote_preview.html")
    html_str = template_obj.render({
        "request": None, # request is not needed when rendering to string
        "quote": quote,
        "details": details_dict,
        "total_formatted": total_formatted,
        "is_pdf": True,
        "sorted_sections": sorted_sections,
        "sorted_deliverables": sorted_deliverables,
        "subtotal": subtotal,
        "active_addons": active_addons,
        "addons_total": addons_total,
        "discount_amount": discount_amount
    })
    return html_str
