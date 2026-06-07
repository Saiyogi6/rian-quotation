import pytest
from datetime import date

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_quote_types(client):
    response = client.get("/api/quote-types")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["code"] == "wedding"

def test_create_quote(client):
    quote_data = {
        "quotation_number": "RS-TEST-0001",
        "quotation_date": str(date.today()),
        "status": "draft",
        "notes": "Testing notes",
        "brand_id": 1,
        "quote_type_code": "wedding",
        "template_id": 1,
        "client_name": "John Doe",
        "client_email": "john@example.com",
        "client_phone": "+91 99999 99999",
        "client_address": "Test Road, Chennai",
        "details": {
            "groom_name": "John",
            "bride_name": "Jane",
            "venue": "Test Mahal"
        },
        "sections": [
            {
                "title": "Reception Coverage",
                "line_items": [
                    {
                        "description": "Candid Photography",
                        "qty": 1,
                        "unit_price": 25000
                    }
                ]
            }
        ],
        "deliverables": [
            {
                "type": "photo",
                "description": "High res photos",
                "qty": 100
            }
        ],
        "payment_splits": [
            {
                "stage_name": "Advance",
                "percentage": 100,
                "amount": 25000,
                "due_date": "On Booking"
            }
        ],
        "add_ons": [
            {
                "description": "Additional Album",
                "price": 5000,
                "is_selected": False
            }
        ]
    }
    
    # Send request
    response = client.post("/api/quotes", json=quote_data)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["quotation_number"] == "RS-TEST-0001"
    assert float(res_data["total_amount"]) == 25000.00
    assert res_data["contact"]["name"] == "John Doe"
    assert res_data["details"]["groom_name"] == "John"
    assert len(res_data["sections"]) == 1
    assert res_data["sections"][0]["title"] == "Reception Coverage"
    assert len(res_data["sections"][0]["line_items"]) == 1
    assert res_data["sections"][0]["line_items"][0]["description"] == "Candid Photography"

def test_update_quote(client):
    # First create one
    quote_data = {
        "quotation_number": "RS-TEST-0002",
        "quotation_date": str(date.today()),
        "status": "draft",
        "brand_id": 1,
        "quote_type_code": "wedding",
        "template_id": 1,
        "client_name": "Sam Smith",
        "details": {"groom_name": "Sam"},
        "sections": [
            {
                "title": "Standard Section",
                "line_items": [{"description": "Traditional Photo", "qty": 1, "unit_price": 10000}]
            }
        ],
        "deliverables": [],
        "payment_splits": [],
        "add_ons": []
    }
    create_res = client.post("/api/quotes", json=quote_data)
    quote_id = create_res.json()["id"]

    # Now update it
    update_data = quote_data.copy()
    update_data["client_name"] = "Sam Smith Jr"
    update_data["sections"] = [
        {
            "title": "Premium Section",
            "line_items": [
                {"description": "Cinematic Video", "qty": 1, "unit_price": 20000},
                {"description": "Candid Photo", "qty": 1, "unit_price": 15000}
            ]
        }
    ]

    response = client.put(f"/api/quotes/{quote_id}", json=update_data)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["contact"]["name"] == "Sam Smith Jr"
    assert float(res_data["total_amount"]) == 35000.00
    assert len(res_data["sections"]) == 1
    assert res_data["sections"][0]["title"] == "Premium Section"
    assert len(res_data["sections"][0]["line_items"]) == 2

def test_duplicate_quote(client):
    # Create original
    quote_data = {
        "quotation_number": "RS-ORIGINAL",
        "quotation_date": str(date.today()),
        "status": "draft",
        "brand_id": 1,
        "quote_type_code": "wedding",
        "template_id": 1,
        "client_name": "Original Client",
        "details": {"groom_name": "Groom A"},
        "sections": [
            {
                "title": "Photoshoot",
                "line_items": [{"description": "Shoot", "qty": 1, "unit_price": 5000}]
            }
        ],
        "deliverables": [],
        "payment_splits": [],
        "add_ons": []
    }
    create_res = client.post("/api/quotes", json=quote_data)
    quote_id = create_res.json()["id"]

    # Duplicate
    dup_res = client.post(f"/api/quotes/{quote_id}/duplicate")
    assert dup_res.status_code == 200
    dup_data = dup_res.json()
    assert dup_data["id"] != quote_id
    assert "RS-DUP-" in dup_data["quotation_number"]
    assert dup_data["contact"]["name"] == "Original Client"
    assert float(dup_data["total_amount"]) == 5000.00

def test_update_status(client):
    # Create
    quote_data = {
        "quotation_number": "RS-STATUS",
        "quotation_date": str(date.today()),
        "status": "draft",
        "brand_id": 1,
        "quote_type_code": "wedding",
        "template_id": 1,
        "client_name": "Status Client",
        "details": {},
        "sections": [{"title": "S", "line_items": [{"description": "I", "qty": 1, "unit_price": 100}]}],
        "deliverables": [],
        "payment_splits": [],
        "add_ons": []
    }
    create_res = client.post("/api/quotes", json=quote_data)
    quote_id = create_res.json()["id"]

    # Update status to approved
    response = client.post(f"/api/quotes/{quote_id}/status", json={"status": "approved"})
    assert response.status_code == 200
    assert response.json()["new_status"] == "approved"

    # Verify status in database
    get_res = client.get(f"/api/quotes/{quote_id}")
    assert get_res.json()["status"] == "approved"
