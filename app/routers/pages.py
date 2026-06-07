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
    
    # Format monetary values
    total_formatted = f"{db_quote.total_amount:,.2f}"
    
    return templates.TemplateResponse(request=request, name="quote_preview.html", context={
        "quote": db_quote,
        "details": details_dict,
        "total_formatted": total_formatted,
        "is_pdf": False
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
    total_formatted = f"{quote.total_amount:,.2f}"
    
    # Resolve image path to absolute local path or serve file URL for WeasyPrint
    # WeasyPrint runs locally, so referencing relative static paths like "/static/images/logo.png"
    # might not resolve unless base_url is set or we pass absolute paths.
    # In weasyprint base_url is set to ".", which means relative paths like "./app/static/images/logo.png" will work.
    # We will adjust the logo path inside the template depending on is_pdf.
    
    # We render the template directly from jinja
    template_obj = templates.get_template("quote_preview.html")
    html_str = template_obj.render({
        "request": None, # request is not needed when rendering to string
        "quote": quote,
        "details": details_dict,
        "total_formatted": total_formatted,
        "is_pdf": True
    })
    return html_str
