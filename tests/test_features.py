import pytest
from datetime import date
from decimal import Decimal
from app.models.models import Quote, QuoteLineItem, Deliverable
from app.services import quote as quote_service

def test_feature_create_quote(client):
    # Test quote creation with new fields (intro note, discounts, checklists)
    payload = {
        "quotation_number": "RS-FEAT-0001",
        "quotation_date": str(date.today()),
        "status": "draft",
        "notes": "Feature test notes",
        "discount_type": "percentage",
        "discount_value": 10.00,
        "intro_content": "Hello client, welcome to Rian Studioz!",
        "brand_id": 1,
        "quote_type_code": "wedding",
        "template_id": 1,
        "client_name": "Alice Bob",
        "client_email": "alice@example.com",
        "client_phone": "+91 99999 11111",
        "client_address": "Main Street, Chennai",
        "details": {"groom_name": "Bob"},
        "sections": [
            {
                "title": "Reception",
                "line_items": [
                    {
                        "description": "Candid Photo",
                        "qty": 1,
                        "unit_price": 50000,
                        "is_selected": True,
                        "group_name": "Reception",
                        "display_order": 0,
                        "item_category": "photo"
                    },
                    {
                        "description": "Unselected Package",
                        "qty": 1,
                        "unit_price": 25000,
                        "is_selected": False,
                        "group_name": "Reception",
                        "display_order": 1,
                        "item_category": "photo"
                    }
                ]
            }
        ],
        "deliverables": [
            {
                "type": "photo",
                "description": "RAW images",
                "qty": 1,
                "is_selected": True,
                "price": 0.00,
                "is_complimentary": True,
                "group_name": "Photos",
                "display_order": 0,
                "item_category": "photo"
            },
            {
                "type": "album",
                "description": "Paid Extra Album",
                "qty": 1,
                "is_selected": True,
                "price": 10000.00,
                "is_complimentary": False,
                "group_name": "Albums",
                "display_order": 1,
                "item_category": "album"
            },
            {
                "type": "video",
                "description": "Unselected video deliverable",
                "qty": 1,
                "is_selected": False,
                "price": 5000.00,
                "is_complimentary": False,
                "group_name": "Videos",
                "display_order": 2,
                "item_category": "video"
            }
        ],
        "payment_splits": [
            {
                "stage_name": "Advance",
                "percentage": 100,
                "amount": 54000,
                "due_date": "On Booking"
            }
        ],
        "add_ons": [
            {
                "description": "LED Wall",
                "price": 10000,
                "is_selected": False
            }
        ]
    }
    
    response = client.post("/api/quotes", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Assertions
    assert data["quotation_number"] == "RS-FEAT-0001"
    assert data["discount_type"] == "percentage"
    assert float(data["discount_value"]) == 10.00
    assert data["intro_content"] == "Hello client, welcome to Rian Studioz!"
    
    # Subtotal calculation:
    # Candid Photo (selected): 50,000
    # Unselected Package: skipped (0)
    # RAW images (complimentary): skipped (0)
    # Paid Extra Album (selected, paid): 10,000
    # Unselected deliverable: skipped (0)
    # Addon LED Wall (unselected): skipped (0)
    # Total before discount = 50,000 + 10,000 = 60,000
    # 10% Discount = 6,000
    # Expected grand total = 60,000 - 6,000 = 54,000
    assert float(data["total_amount"]) == 54000.00

    # Verify checklist persistence in items
    sec = data["sections"][0]
    assert len(sec["line_items"]) == 2
    assert sec["line_items"][0]["description"] == "Candid Photo"
    assert sec["line_items"][0]["is_selected"] is True
    assert sec["line_items"][0]["group_name"] == "Reception"
    assert sec["line_items"][0]["item_category"] == "photo"
    assert sec["line_items"][1]["description"] == "Unselected Package"
    assert sec["line_items"][1]["is_selected"] is False

    # Verify deliverable checklist persistence
    assert len(data["deliverables"]) == 3
    assert data["deliverables"][0]["is_selected"] is True
    assert data["deliverables"][0]["is_complimentary"] is True
    assert float(data["deliverables"][0]["price"]) == 0.0
    assert data["deliverables"][1]["is_selected"] is True
    assert data["deliverables"][1]["is_complimentary"] is False
    assert float(data["deliverables"][1]["price"]) == 10000.0
    assert data["deliverables"][2]["is_selected"] is False

def test_feature_edit_quote(client):
    # 1. Create a draft quote first
    payload = {
        "quotation_number": "RS-FEAT-0002",
        "quotation_date": str(date.today()),
        "status": "draft",
        "discount_type": "none",
        "discount_value": 0.00,
        "intro_content": "Old intro content",
        "brand_id": 1,
        "quote_type_code": "wedding",
        "template_id": 1,
        "client_name": "Bob Marley",
        "sections": [
            {
                "title": "Coverage",
                "line_items": [{"description": "Traditional Photo", "qty": 1, "unit_price": 20000, "is_selected": True}]
            }
        ],
        "deliverables": [],
        "payment_splits": [],
        "add_ons": []
    }
    create_res = client.post("/api/quotes", json=payload)
    quote_id = create_res.json()["id"]
    
    # 2. Modify features: apply fixed discount and edit intro note
    update_payload = payload.copy()
    update_payload["intro_content"] = "Updated intro content!"
    update_payload["discount_type"] = "fixed"
    update_payload["discount_value"] = 5000.00
    
    # Expected grand total = 20,000 - 5,000 = 15,000
    
    response = client.put(f"/api/quotes/{quote_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intro_content"] == "Updated intro content!"
    assert data["discount_type"] == "fixed"
    assert float(data["discount_value"]) == 5000.00
    assert float(data["total_amount"]) == 15000.00

def test_feature_duplicate_quote(client):
    # 1. Create original quote
    payload = {
        "quotation_number": "RS-FEAT-ORIG",
        "quotation_date": str(date.today()),
        "status": "draft",
        "discount_type": "fixed",
        "discount_value": 3000.00,
        "intro_content": "Original duplicate note",
        "brand_id": 1,
        "quote_type_code": "wedding",
        "template_id": 1,
        "client_name": "Dup Client",
        "sections": [
            {
                "title": "Photoshoot",
                "line_items": [
                    {
                        "description": "Shoot",
                        "qty": 1,
                        "unit_price": 30000,
                        "is_selected": True,
                        "group_name": "Main",
                        "display_order": 0,
                        "item_category": "photo"
                    }
                ]
            }
        ],
        "deliverables": [
            {
                "type": "photo",
                "description": "Dup Photos",
                "qty": 1,
                "is_selected": True,
                "price": 0.00,
                "is_complimentary": True,
                "group_name": "Media",
                "display_order": 0,
                "item_category": "photo"
            }
        ],
        "payment_splits": [],
        "add_ons": []
    }
    create_res = client.post("/api/quotes", json=payload)
    quote_id = create_res.json()["id"]

    # 2. Duplicate quote
    dup_res = client.post(f"/api/quotes/{quote_id}/duplicate")
    assert dup_res.status_code == 200
    data = dup_res.json()
    
    # 3. Assert duplicated fields are identical
    assert data["id"] != quote_id
    assert "RS-DUP-" in data["quotation_number"]
    assert data["intro_content"] == "Original duplicate note"
    assert data["discount_type"] == "fixed"
    assert float(data["discount_value"]) == 3000.00
    assert float(data["total_amount"]) == 27000.00 # 30000 - 3000 = 27000
    
    # Assert item details duplicated
    item = data["sections"][0]["line_items"][0]
    assert item["description"] == "Shoot"
    assert item["group_name"] == "Main"
    assert item["item_category"] == "photo"
    assert item["is_selected"] is True

    # Assert deliverables duplicated
    deliv = data["deliverables"][0]
    assert deliv["description"] == "Dup Photos"
    assert deliv["is_complimentary"] is True
    assert deliv["group_name"] == "Media"

def test_feature_preset_switching_and_preview(client):
    # 1. Create a quote
    payload = {
        "quotation_number": "RS-FEAT-PREV",
        "quotation_date": str(date.today()),
        "status": "draft",
        "discount_type": "none",
        "discount_value": 0.00,
        "intro_content": "A premium welcome note",
        "brand_id": 1,
        "quote_type_code": "wedding",
        "template_id": 1,
        "client_name": "Preview Client",
        "sections": [
            {
                "title": "Reception",
                "line_items": [{"description": "Standard", "qty": 1, "unit_price": 10000, "is_selected": True}]
            }
        ],
        "deliverables": [],
        "payment_splits": [],
        "add_ons": []
    }
    create_res = client.post("/api/quotes", json=payload)
    quote_id = create_res.json()["id"]

    # 2. Render preview endpoint
    preview_res = client.get(f"/quotes/{quote_id}/preview")
    assert preview_res.status_code == 200
    assert "A premium welcome note" in preview_res.text
    assert "Preview Client" in preview_res.text

def test_feature_pdf_smoke_test(client):
    # 1. Create a quote
    payload = {
        "quotation_number": "RS-FEAT-PDF",
        "quotation_date": str(date.today()),
        "status": "draft",
        "discount_type": "none",
        "discount_value": 0.00,
        "intro_content": "Welcome to our studio proposal",
        "brand_id": 1,
        "quote_type_code": "wedding",
        "template_id": 1,
        "client_name": "PDF Client",
        "sections": [
            {
                "title": "Coverage",
                "line_items": [{"description": "Shoot", "qty": 1, "unit_price": 10000, "is_selected": True}]
            }
        ],
        "deliverables": [],
        "payment_splits": [],
        "add_ons": []
    }
    create_res = client.post("/api/quotes", json=payload)
    quote_id = create_res.json()["id"]

    # 2. Export PDF endpoint
    pdf_res = client.post(f"/api/quotes/{quote_id}/export-pdf")
    assert pdf_res.status_code == 200
    data = pdf_res.json()
    assert data["status"] == "success"
    assert "pdf_path" in data
    assert data["pdf_path"].endswith(".pdf")
