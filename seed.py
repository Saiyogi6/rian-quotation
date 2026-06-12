import os
import sys
import json
from datetime import date, datetime
from decimal import Decimal

# Add root directory to path to allow importing app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, Base, engine
from app.models.models import (
    Brand, QuoteType, Template, Contact, Quote,
    QuoteDetailsJson, QuoteSection, QuoteLineItem,
    Deliverable, PaymentSplit, AddOn
)

DEFAULT_PRESETS_JSON_DATA = {
    "presets": {
        "wedding_reception": {
            "intro": "Hey! A big hello from Rian Studioz. First of all, congratulations! We are as excited as you are for the Wedding & Reception Ceremony. Thank you for considering Rian Studioz for your big day. We guarantee to capture your best moments, which you will look back on with a smile in the future. We eagerly await to surprise you with amazing pictures and videos.",
            "sections": [
                {
                    "title": "Reception Coverage",
                    "items": [
                        { "description": "Candid Photography", "qty": 1, "unit_price": 20000, "is_selected": True, "group_name": "Reception", "display_order": 0, "item_category": "photo" },
                        { "description": "Traditional Photography", "qty": 1, "unit_price": 10000, "is_selected": True, "group_name": "Reception", "display_order": 1, "item_category": "photo" },
                        { "description": "Candid Videography (4K)", "qty": 1, "unit_price": 20000, "is_selected": True, "group_name": "Reception", "display_order": 2, "item_category": "video" },
                        { "description": "Traditional Videography (4K)", "qty": 1, "unit_price": 15000, "is_selected": True, "group_name": "Reception", "display_order": 3, "item_category": "video" }
                    ]
                },
                {
                    "title": "Wedding Coverage",
                    "items": [
                        { "description": "Candid Photography", "qty": 1, "unit_price": 20000, "is_selected": True, "group_name": "Wedding", "display_order": 0, "item_category": "photo" },
                        { "description": "Traditional Photography", "qty": 1, "unit_price": 10000, "is_selected": True, "group_name": "Wedding", "display_order": 1, "item_category": "photo" },
                        { "description": "Candid Videography (4K)", "qty": 1, "unit_price": 20000, "is_selected": True, "group_name": "Wedding", "display_order": 2, "item_category": "video" },
                        { "description": "Traditional Videography (4K)", "qty": 1, "unit_price": 15000, "is_selected": True, "group_name": "Wedding", "display_order": 3, "item_category": "video" }
                    ]
                }
            ],
            "deliverables": [
                { "type": "photo", "description": "All Candid & Traditional Photos (Raw Images)", "qty": 1, "price": 0, "is_complimentary": True, "group_name": "Photos", "display_order": 0 },
                { "type": "album", "description": "2 Albums (250 Photos per Album, 40 Sheets / 80 Pages, Canvera Album with Mini Replica)", "qty": 2, "price": 0, "is_complimentary": True, "group_name": "Albums", "display_order": 1 },
                { "type": "video", "description": "Full-Length Traditional Video", "qty": 1, "price": 0, "is_complimentary": True, "group_name": "Videos", "display_order": 2 },
                { "type": "turnaround", "description": "Color Corrected Photos: Within 10 Days", "qty": 1, "price": 0, "is_complimentary": True, "group_name": "Delivery Timeline", "display_order": 3 }
            ]
        },
        "reception_only": {
            "intro": "Hey! A big hello from Rian Studioz. First of all, congratulations! We are as excited as you are for the Reception. Thank you for considering Rian Studioz for your big day. We guarantee to capture your best moments, which you will look back on with a smile in the future.",
            "sections": [
                {
                    "title": "Reception Coverage",
                    "items": [
                        { "description": "Candid Photography", "qty": 1, "unit_price": 20000, "is_selected": True, "group_name": "Reception", "display_order": 0, "item_category": "photo" },
                        { "description": "Traditional Photography", "qty": 1, "unit_price": 10000, "is_selected": True, "group_name": "Reception", "display_order": 1, "item_category": "photo" },
                        { "description": "Candid Videography (4K)", "qty": 1, "unit_price": 20000, "is_selected": True, "group_name": "Reception", "display_order": 2, "item_category": "video" },
                        { "description": "Traditional Videography (4K)", "qty": 1, "unit_price": 15000, "is_selected": True, "group_name": "Reception", "display_order": 3, "item_category": "video" }
                    ]
                }
            ],
            "deliverables": [
                { "type": "photo", "description": "Digital Photo Gallery (Raw & Edits)", "qty": 1, "price": 0, "is_complimentary": True, "group_name": "Photos", "display_order": 0 },
                { "type": "album", "description": "1 Premium Photobook Album", "qty": 1, "price": 0, "is_complimentary": True, "group_name": "Albums", "display_order": 1 }
            ]
        },
        "marriage_only": {
            "intro": "Hey! A big hello from Rian Studioz. First of all, congratulations! We are as excited as you are for the Marriage Ceremony. Thank you for considering Rian Studioz for your big day.",
            "sections": [
                {
                    "title": "Marriage Coverage",
                    "items": [
                        { "description": "Candid Photography", "qty": 1, "unit_price": 20000, "is_selected": True, "group_name": "Marriage Only", "display_order": 0, "item_category": "photo" },
                        { "description": "Traditional Photography", "qty": 1, "unit_price": 10000, "is_selected": True, "group_name": "Marriage Only", "display_order": 1, "item_category": "photo" },
                        { "description": "Traditional Videography (4K)", "qty": 1, "unit_price": 15000, "is_selected": True, "group_name": "Marriage Only", "display_order": 2, "item_category": "video" }
                    ]
                }
            ],
            "deliverables": [
                { "type": "photo", "description": "High-res Photo Delivery (Digital)", "qty": 1, "price": 0, "is_complimentary": True, "group_name": "Photos", "display_order": 0 },
                { "type": "album", "description": "1 Standard Wedding Album", "qty": 1, "price": 0, "is_complimentary": True, "group_name": "Albums", "display_order": 1 }
            ]
        },
        "muslim_wedding": {
            "intro": "Hey! A big hello from Rian Studioz. First of all, congratulations! We are as excited as you are for the Nikah & Reception. Thank you for considering Rian Studioz for your big day.",
            "sections": [
                {
                    "title": "Nikah Ceremony",
                    "items": [
                        { "description": "Candid Photography", "qty": 1, "unit_price": 20000, "is_selected": True, "group_name": "Nikah", "display_order": 0, "item_category": "photo" },
                        { "description": "Traditional Photography", "qty": 1, "unit_price": 10000, "is_selected": True, "group_name": "Nikah", "display_order": 1, "item_category": "photo" },
                        { "description": "Traditional Videography (4K)", "qty": 1, "unit_price": 15000, "is_selected": True, "group_name": "Nikah", "display_order": 2, "item_category": "video" }
                    ]
                },
                {
                    "title": "Reception Coverage",
                    "items": [
                        { "description": "Candid Photography", "qty": 1, "unit_price": 20000, "is_selected": True, "group_name": "Reception", "display_order": 0, "item_category": "photo" },
                        { "description": "Candid Videography", "qty": 1, "unit_price": 20000, "is_selected": True, "group_name": "Reception", "display_order": 1, "item_category": "video" }
                    ]
                }
            ],
            "deliverables": [
                { "type": "photo", "description": "All RAW + Edited Photos", "qty": 1, "price": 0, "is_complimentary": True, "group_name": "Photos", "display_order": 0 },
                { "type": "album", "description": "2 Premium Wedding Albums", "qty": 2, "price": 0, "is_complimentary": True, "group_name": "Albums", "display_order": 1 }
            ]
        },
        "retirement": {
            "intro": "Hey! A big hello from Rian Studioz. First of all, congratulations! We are as excited as you are for the Retirement Function. Thank you for considering Rian Studioz for your big day.",
            "sections": [
                {
                    "title": "Retirement Coverage",
                    "items": [
                        { "description": "Traditional Photography", "qty": 1, "unit_price": 10000, "is_selected": True, "group_name": "Retirement", "display_order": 0, "item_category": "photo" },
                        { "description": "Candid Photography", "qty": 1, "unit_price": 15000, "is_selected": True, "group_name": "Retirement", "display_order": 1, "item_category": "photo" },
                        { "description": "Album (Magazine)", "qty": 1, "unit_price": 8000, "is_selected": True, "group_name": "Retirement", "display_order": 2, "item_category": "album" }
                    ]
                }
            ],
            "deliverables": [
                { "type": "photo", "description": "All Candid & Traditional Photos (Raw Images)", "qty": 1, "price": 0, "is_complimentary": True, "group_name": "Photos", "display_order": 0 },
                { "type": "album", "description": "1 Magazine Album (20 Sheets / 40 Pages)", "qty": 1, "price": 0, "is_complimentary": True, "group_name": "Album", "display_order": 1 }
            ]
        },
        "convocation_ad": {
            "intro": "Hey! A big hello from Rian Studioz. First of all, congratulations! We are as excited as you are for the Convocation Ceremony & Ad Shoot. Thank you for considering Rian Studioz for your event.",
            "sections": [
                {
                    "title": "Ad Shoot",
                    "items": [
                        { "description": "Candid Photography", "qty": 2, "unit_price": 15000, "is_selected": True, "group_name": "Ad Shoot", "display_order": 0, "item_category": "photo" },
                        { "description": "Candid Videography", "qty": 2, "unit_price": 15000, "is_selected": True, "group_name": "Ad Shoot", "display_order": 1, "item_category": "video" }
                    ]
                },
                {
                    "title": "Convocation",
                    "items": [
                        { "description": "Candid Photography", "qty": 1, "unit_price": 15000, "is_selected": True, "group_name": "Convocation", "display_order": 0, "item_category": "photo" },
                        { "description": "Candid Videography", "qty": 1, "unit_price": 15000, "is_selected": True, "group_name": "Convocation", "display_order": 1, "item_category": "video" },
                        { "description": "Traditional Photography", "qty": 2, "unit_price": 10000, "is_selected": True, "group_name": "Convocation", "display_order": 2, "item_category": "photo" },
                        { "description": "Traditional Videography", "qty": 2, "unit_price": 15000, "is_selected": True, "group_name": "Convocation", "display_order": 3, "item_category": "video" },
                        { "description": "Drone", "qty": 1, "unit_price": 15000, "is_selected": True, "group_name": "Convocation", "display_order": 4, "item_category": "video" }
                    ]
                }
            ],
            "deliverables": [
                { "type": "photo", "description": "All Candid & Traditional Photos (Raw Images)", "qty": 1, "price": 0, "is_complimentary": True, "group_name": "Photos", "display_order": 0 },
                { "type": "video", "description": "Full-Length Traditional Video", "qty": 1, "price": 0, "is_complimentary": True, "group_name": "Videos", "display_order": 1 }
            ]
        },
        "election": {
            "intro": "Hey! A big hello from Rian Studioz. First of all, congratulations! We are as excited as you are for the Election Campaign. Thank you for considering Rian Studioz for your campaign.",
            "sections": [
                {
                    "title": "Election Campaign",
                    "items": [
                        { "description": "Traditional Photography", "qty": 10, "unit_price": 12000, "is_selected": True, "group_name": "Campaign", "display_order": 0, "item_category": "photo" },
                        { "description": "Traditional Videography", "qty": 10, "unit_price": 12000, "is_selected": True, "group_name": "Campaign", "display_order": 1, "item_category": "video" },
                        { "description": "Drone", "qty": 10, "unit_price": 12000, "is_selected": True, "group_name": "Campaign", "display_order": 2, "item_category": "video" }
                    ]
                }
            ],
            "deliverables": [
                { "type": "photo", "description": "Daily Photo Feed (Raw Images)", "qty": 1, "price": 0, "is_complimentary": True, "group_name": "Photos", "display_order": 0 },
                { "type": "video", "description": "Campaign Highlight Videos", "qty": 1, "price": 0, "is_complimentary": True, "group_name": "Videos", "display_order": 1 }
            ]
        },
        "birthday": {
            "intro": "Hey! A big hello from Rian Studioz. First of all, congratulations! We are as excited as you are for the Birthday Celebration. Thank you for considering Rian Studioz for your event.",
            "sections": [
                {
                    "title": "Birthday Celebration",
                    "items": [
                        { "description": "Candid Photography", "qty": 1, "unit_price": 12000, "is_selected": True, "group_name": "Birthday", "display_order": 0, "item_category": "photo" },
                        { "description": "Traditional Photography", "qty": 1, "unit_price": 8000, "is_selected": True, "group_name": "Birthday", "display_order": 1, "item_category": "photo" },
                        { "description": "Traditional Videography", "qty": 1, "unit_price": 10000, "is_selected": True, "group_name": "Birthday", "display_order": 2, "item_category": "video" }
                    ]
                }
            ],
            "deliverables": [
                { "type": "photo", "description": "All photos in digital gallery", "qty": 1, "price": 0, "is_complimentary": True, "group_name": "Photos", "display_order": 0 },
                { "type": "album", "description": "1 Standard Birthday Album", "qty": 1, "price": 0, "is_complimentary": True, "group_name": "Albums", "display_order": 1 }
            ]
        },
        "baby_shower": {
            "intro": "Hey! A big hello from Rian Studioz. First of all, congratulations! We are as excited as you are for the Baby Shower. Thank you for considering Rian Studioz for your event.",
            "sections": [
                {
                    "title": "Baby Shower",
                    "items": [
                        { "description": "Candid Photography", "qty": 1, "unit_price": 15000, "is_selected": True, "group_name": "Baby Shower", "display_order": 0, "item_category": "photo" },
                        { "description": "Traditional Photography", "qty": 1, "unit_price": 8000, "is_selected": True, "group_name": "Baby Shower", "display_order": 1, "item_category": "photo" },
                        { "description": "Cinematic Teaser", "qty": 1, "unit_price": 12000, "is_selected": True, "group_name": "Baby Shower", "display_order": 2, "item_category": "video" }
                    ]
                }
            ],
            "deliverables": [
                { "type": "photo", "description": "Digital Photo Gallery", "qty": 1, "price": 0, "is_complimentary": True, "group_name": "Photos", "display_order": 0 },
                { "type": "album", "description": "1 Premium photobook", "qty": 1, "price": 0, "is_complimentary": True, "group_name": "Albums", "display_order": 1 }
            ]
        },
        "custom": {
            "intro": "Hey! A big hello from Rian Studioz. Thank you for considering Rian Studioz for your creative needs. Below is the custom tailored quotation and list of deliverables based on our discussion.",
            "sections": [
                {
                    "title": "Custom Services",
                    "items": [
                        { "description": "Standard Photography", "qty": 1, "unit_price": 10000, "is_selected": True, "group_name": "Custom", "display_order": 0, "item_category": "photo" }
                    ]
                }
            ],
            "deliverables": [
                { "type": "photo", "description": "Digital Deliverable Package", "qty": 1, "price": 0, "is_complimentary": True, "group_name": "Digital", "display_order": 0 }
            ]
        }
    },
    "addons": [
        { "description": "1 Extra Traditional Photography", "price": 10000 },
        { "description": "1 Extra Traditional Videography(4K)", "price": 15000 },
        { "description": "1 Extra Candid Photography", "price": 15000 },
        { "description": "1 Extra Candid Videography", "price": 15000 },
        { "description": "Drone", "price": 12000 },
        { "description": "1 Extra Album", "price": 20000 },
        { "description": "LED Wall (6 x 8)", "price": 13000 },
        { "description": "LED TV(50\u2019Inches)", "price": 5000 },
        { "description": "Spot Mixing", "price": 10000 },
        { "description": "PhotoBooth", "price": 25000 },
        { "description": "360o Spinny", "price": 15000 },
        { "description": "Youtube Live Streaming 1080p", "price": 10000 }
    ]
}

def seed_database():
    # Re-create tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("Seeding database...")
        
        # 1. Seed Brand
        brand = Brand(
            name="Rian Studioz",
            logo_path="/static/images/logo.png",
            email="contact@rianstudioz.com",
            phone="+91 98765 43210",
            website="www.rianstudioz.com",
            address="12, Royal Plaza, Cathedral Road, Chennai - 600086, India",
            terms_and_conditions=(
                "1. Booking Confirmation: 50% advance payment is required to block the dates.\n"
                "2. Mid Payment: 40% of the total quote value must be paid on the event date.\n"
                "3. Final Balance: The remaining 10% balance is payable upon delivery of final albums.\n"
                "4. Raw files will not be shared unless explicitly agreed upon in writing.\n"
                "5. Turnaround time for deliverables is 4 to 6 weeks from selection of photos."
            ),
            payment_info=(
                "Bank: HDFC Bank Ltd\n"
                "Account Name: RIAN STUDIOZ\n"
                "Account No: 50200087654321\n"
                "IFSC Code: HDFC0001234\n"
                "UPI ID: rianstudioz@hdfcbank"
            ),
            presets_json=json.dumps(DEFAULT_PRESETS_JSON_DATA, indent=2)
        )
        db.add(brand)
        db.flush()
        
        # 2. Seed Quote Types
        types = [
            QuoteType(
                name="Wedding & Reception",
                code="wedding_reception",
                fields_schema='{"fields": [{"name": "groom_name", "label": "Groom\'s Name", "type": "text", "required": true}, {"name": "bride_name", "label": "Bride\'s Name", "type": "text", "required": true}, {"name": "event_dates", "label": "Event Dates", "type": "text", "required": true}, {"name": "venue", "label": "Venue(s)", "type": "text", "required": true}, {"name": "contact_number", "label": "Contact Number", "type": "text", "required": false}, {"name": "email", "label": "Email Address", "type": "text", "required": false}]}'
            ),
            QuoteType(
                name="Reception Only",
                code="reception_only",
                fields_schema='{"fields": [{"name": "client_name", "label": "Bride/Groom or Client Name", "type": "text", "required": true}, {"name": "event_date", "label": "Event Date", "type": "text", "required": true}, {"name": "venue", "label": "Venue", "type": "text", "required": true}, {"name": "contact", "label": "Contact Info", "type": "text", "required": false}]}'
            ),
            QuoteType(
                name="Marriage Only",
                code="marriage_only",
                fields_schema='{"fields": [{"name": "groom_name", "label": "Groom\'s Name", "type": "text", "required": true}, {"name": "bride_name", "label": "Bride\'s Name", "type": "text", "required": true}, {"name": "marriage_date", "label": "Marriage Date", "type": "text", "required": true}, {"name": "venue", "label": "Venue", "type": "text", "required": true}, {"name": "contact", "label": "Contact Info", "type": "text", "required": false}]}'
            ),
            QuoteType(
                name="Muslim Wedding",
                code="muslim_wedding",
                fields_schema='{"fields": [{"name": "groom_name", "label": "Groom\'s Name", "type": "text", "required": true}, {"name": "bride_name", "label": "Bride\'s Name", "type": "text", "required": true}, {"name": "nikah_date", "label": "Nikah Date", "type": "text", "required": true}, {"name": "reception_date", "label": "Reception Date (Optional)", "type": "text", "required": false}, {"name": "venue", "label": "Venue", "type": "text", "required": true}, {"name": "contact", "label": "Contact Info", "type": "text", "required": false}]}'
            ),
            QuoteType(
                name="Retirement Function",
                code="retirement",
                fields_schema='{"fields": [{"name": "client_name", "label": "Retiree Name", "type": "text", "required": true}, {"name": "event_date", "label": "Event Date", "type": "text", "required": true}, {"name": "venue", "label": "Venue", "type": "text", "required": true}, {"name": "contact", "label": "Contact Info", "type": "text", "required": false}]}'
            ),
            QuoteType(
                name="Convocation Ceremony & Ad Shoot",
                code="convocation_ad",
                fields_schema='{"fields": [{"name": "event_name", "label": "Event / Campaign Name", "type": "text", "required": true}, {"name": "event_date", "label": "Shoot Date(s)", "type": "text", "required": true}, {"name": "venue", "label": "Location / Venue", "type": "text", "required": true}, {"name": "contact", "label": "Contact Info", "type": "text", "required": false}]}'
            ),
            QuoteType(
                name="Election Campaign",
                code="election",
                fields_schema='{"fields": [{"name": "campaign_name", "label": "Candidate / Campaign Name", "type": "text", "required": true}, {"name": "event_dates", "label": "Campaign Duration (Dates)", "type": "text", "required": true}, {"name": "venue", "label": "Constituency / Venue", "type": "text", "required": true}, {"name": "contact", "label": "Contact Info", "type": "text", "required": false}]}'
            ),
            QuoteType(
                name="Birthday",
                code="birthday",
                fields_schema='{"fields": [{"name": "celebrant_name", "label": "Celebrant Name", "type": "text", "required": true}, {"name": "age", "label": "Age (Optional)", "type": "text", "required": false}, {"name": "event_date", "label": "Event Date", "type": "text", "required": true}, {"name": "venue", "label": "Venue", "type": "text", "required": true}, {"name": "contact", "label": "Contact Info", "type": "text", "required": false}, {"name": "parent_name", "label": "Parent Name (Optional)", "type": "text", "required": false}]}'
            ),
            QuoteType(
                name="Baby Shower",
                code="baby_shower",
                fields_schema='{"fields": [{"name": "mother_name", "label": "Mother\'s Name", "type": "text", "required": true}, {"name": "father_name", "label": "Father\'s Name (Optional)", "type": "text", "required": false}, {"name": "event_date", "label": "Event Date", "type": "text", "required": true}, {"name": "venue", "label": "Venue", "type": "text", "required": true}, {"name": "contact", "label": "Contact Info", "type": "text", "required": false}]}'
            ),
            QuoteType(
                name="Custom",
                code="custom",
                fields_schema='{"fields": [{"name": "custom_details", "label": "Custom Quotation Description", "type": "textarea", "required": false}]}'
            )
        ]
        for t in types:
            db.add(t)
        db.flush()
        
        # 3. Seed Master Template placeholder
        template = Template(
            name="Rian Studioz Master Premium Layout",
            code="master_premium",
            html_content=""
        )
        db.add(template)
        db.flush()

        # 4. Seed Contacts
        contacts = [
            Contact(name="Anand & Divya", email="anand@example.com", phone="+91 99999 88888", address="Adyar, Chennai"),
            Contact(name="Venkatesh Prasad", email="venkatesh@example.com", phone="+91 94444 33333", address="Vani Mahal, Chennai"),
            Contact(name="St. Joseph's College", email="admin@stjosephs.edu", phone="+91 98400 12345", address="Trichy, TN"),
            Contact(name="Dr. K. Sivaraman (Election)", email="candidate@election.in", phone="+91 90000 11111", address="Madurai constituency"),
            Contact(name="Rakesh Khanna", email="rakesh@khannaproductions.com", phone="+91 98200 98200", address="Juhu, Mumbai")
        ]
        for c in contacts:
            db.add(c)
        db.flush()

        # 5. Create Sample Quotes
        
        # 5.1 Wedding & Reception Quote
        q1 = Quote(
            quotation_number="RS-WD26-0255",
            quotation_date=date.today(),
            status="approved",
            total_amount=Decimal("165000.00"), # Subtotal: 175,000, Discount: 10,000 fixed
            notes="Exclusive wedding photography package including customized premium leather albums and drone services.",
            discount_type="fixed",
            discount_value=Decimal("10000.00"),
            intro_content="Hey! A big hello from Rian Studioz. First of all, congratulations! We are as excited as you are for the Wedding & Reception Ceremony. Thank you for considering Rian Studioz for your big day. We guarantee to capture your best moments, which you will look back on with a smile in the future. We eagerly await to surprise you with amazing pictures and videos.",
            brand_id=brand.id,
            quote_type_id=types[0].id,
            template_id=template.id,
            contact_id=contacts[0].id
        )
        db.add(q1)
        db.flush()
        
        # Detail fields
        db.add(QuoteDetailsJson(quote_id=q1.id, field_key="groom_name", field_value="Anand"))
        db.add(QuoteDetailsJson(quote_id=q1.id, field_key="bride_name", field_value="Divya"))
        db.add(QuoteDetailsJson(quote_id=q1.id, field_key="event_dates", field_value="September 12th & 13th, 2026"))
        db.add(QuoteDetailsJson(quote_id=q1.id, field_key="venue", field_value="MRC Kalyana Mandapam, Santhome, Chennai"))
        
        # Sections & Items
        s1 = QuoteSection(quote_id=q1.id, title="Reception Coverage", sort_order=0)
        s2 = QuoteSection(quote_id=q1.id, title="Wedding Coverage", sort_order=1)
        db.add(s1)
        db.add(s2)
        db.flush()
        
        db.add(QuoteLineItem(section_id=s1.id, description="Candid Photography", qty=Decimal("1"), unit_price=Decimal("20000.00"), total_price=Decimal("20000.00"), sort_order=0, is_selected=True, group_name="Reception", display_order=0, item_category="photo"))
        db.add(QuoteLineItem(section_id=s1.id, description="Traditional Photography", qty=Decimal("1"), unit_price=Decimal("10000.00"), total_price=Decimal("10000.00"), sort_order=1, is_selected=True, group_name="Reception", display_order=1, item_category="photo"))
        db.add(QuoteLineItem(section_id=s1.id, description="Candid Videography (4K)", qty=Decimal("1"), unit_price=Decimal("20000.00"), total_price=Decimal("20000.00"), sort_order=2, is_selected=True, group_name="Reception", display_order=2, item_category="video"))
        db.add(QuoteLineItem(section_id=s1.id, description="Traditional Videography (4K)", qty=Decimal("1"), unit_price=Decimal("15000.00"), total_price=Decimal("15000.00"), sort_order=3, is_selected=True, group_name="Reception", display_order=3, item_category="video"))
        
        db.add(QuoteLineItem(section_id=s2.id, description="Candid Photography", qty=Decimal("1"), unit_price=Decimal("20000.00"), total_price=Decimal("20000.00"), sort_order=0, is_selected=True, group_name="Wedding", display_order=0, item_category="photo"))
        db.add(QuoteLineItem(section_id=s2.id, description="Traditional Photography", qty=Decimal("1"), unit_price=Decimal("10000.00"), total_price=Decimal("10000.00"), sort_order=1, is_selected=True, group_name="Wedding", display_order=1, item_category="photo"))
        db.add(QuoteLineItem(section_id=s2.id, description="Candid Videography (4K)", qty=Decimal("1"), unit_price=Decimal("20000.00"), total_price=Decimal("20000.00"), sort_order=2, is_selected=True, group_name="Wedding", display_order=2, item_category="video"))
        db.add(QuoteLineItem(section_id=s2.id, description="Traditional Videography (4K)", qty=Decimal("1"), unit_price=Decimal("15000.00"), total_price=Decimal("15000.00"), sort_order=3, is_selected=True, group_name="Wedding", display_order=3, item_category="video"))
        
        # Deliverables
        db.add(Deliverable(quote_id=q1.id, type="photo", description="All Candid & Traditional Photos (Raw Images)", qty=1, is_selected=True, price=Decimal("0.00"), is_complimentary=True, group_name="Photos", display_order=0))
        db.add(Deliverable(quote_id=q1.id, type="album", description="2 Albums (250 Photos per Album, 40 Sheets / 80 Pages, Canvera Album with Mini Replica)", qty=2, is_selected=True, price=Decimal("0.00"), is_complimentary=True, group_name="Albums", display_order=1))
        db.add(Deliverable(quote_id=q1.id, type="video", description="Full-Length Traditional Video", qty=1, is_selected=True, price=Decimal("0.00"), is_complimentary=True, group_name="Videos", display_order=2))
        db.add(Deliverable(quote_id=q1.id, type="turnaround", description="Color Corrected Photos: Within 10 Days", qty=1, is_selected=True, price=Decimal("0.00"), is_complimentary=True, group_name="Delivery Timeline", display_order=3))
        
        # Payment Splits
        db.add(PaymentSplit(quote_id=q1.id, stage_name="Advance Booking Fee (50%)", amount=Decimal("82500.00"), percentage=Decimal("50.00"), due_date="On Signing"))
        db.add(PaymentSplit(quote_id=q1.id, stage_name="Event Date Milestone (40%)", amount=Decimal("66000.00"), percentage=Decimal("40.00"), due_date="12-Sep-2026"))
        db.add(PaymentSplit(quote_id=q1.id, stage_name="Album Delivery Balance (10%)", amount=Decimal("16500.00"), percentage=Decimal("10.00"), due_date="On Album Handover"))

        # Add-ons
        db.add(AddOn(quote_id=q1.id, description="Additional Candid photographer for Reception", price=Decimal("15000.00"), is_selected=False))
        db.add(AddOn(quote_id=q1.id, description="LED Wall (12x8 ft) for live broadcast at Muhurtham venue", price=Decimal("20000.00"), is_selected=False))

        # 5.2 Retirement Quote
        q2 = Quote(
            quotation_number="RS-RT26-0103",
            quotation_date=date.today(),
            status="sent",
            total_amount=Decimal("33000.00"),
            notes="Retirement celebration function photography package including traditional print and digital shareable gallery.",
            discount_type="none",
            discount_value=Decimal("0.00"),
            intro_content="Hey! A big hello from Rian Studioz. First of all, congratulations! We are as excited as you are for the Retirement Function. Thank you for considering Rian Studioz for your big day. We guarantee to capture your best moments, which you will look back on with a smile in the future. We eagerly await to surprise you with amazing pictures and videos.",
            brand_id=brand.id,
            quote_type_id=types[4].id,
            template_id=template.id,
            contact_id=contacts[1].id
        )
        db.add(q2)
        db.flush()
        
        db.add(QuoteDetailsJson(quote_id=q2.id, field_key="client_name", field_value="Venkatesh Prasad"))
        db.add(QuoteDetailsJson(quote_id=q2.id, field_key="event_date", field_value="October 28th, 2026"))
        db.add(QuoteDetailsJson(quote_id=q2.id, field_key="venue", field_value="Vani Mahal, T. Nagar, Chennai"))
        
        s3 = QuoteSection(quote_id=q2.id, title="Retirement Function", sort_order=0)
        db.add(s3)
        db.flush()
        
        db.add(QuoteLineItem(section_id=s3.id, description="Traditional Photography", qty=Decimal("1"), unit_price=Decimal("10000.00"), total_price=Decimal("10000.00"), sort_order=0, is_selected=True, group_name="Retirement Function", display_order=0))
        db.add(QuoteLineItem(section_id=s3.id, description="Candid Photography", qty=Decimal("1"), unit_price=Decimal("15000.00"), total_price=Decimal("15000.00"), sort_order=1, is_selected=True, group_name="Retirement Function", display_order=1))
        db.add(QuoteLineItem(section_id=s3.id, description="Album (Magazine)", qty=Decimal("1"), unit_price=Decimal("8000.00"), total_price=Decimal("8000.00"), sort_order=2, is_selected=True, group_name="Retirement Function", display_order=2))
        
        db.add(Deliverable(quote_id=q2.id, type="photo", description="All Candid & Traditional Photos (Raw Images)", qty=1, is_selected=True, price=Decimal("0.00"), is_complimentary=True, group_name="Photos", display_order=0))
        db.add(Deliverable(quote_id=q2.id, type="album", description="1 Magazine Album (80-100 Photos, 20 Sheets / 40 Pages)", qty=1, is_selected=True, price=Decimal("0.00"), is_complimentary=True, group_name="Album", display_order=1))
        
        db.add(PaymentSplit(quote_id=q2.id, stage_name="Advance Booking Fee (50%)", amount=Decimal("16500.00"), percentage=Decimal("50.00"), due_date="On Signing"))
        db.add(PaymentSplit(quote_id=q2.id, stage_name="Event Day Payment (50%)", amount=Decimal("16500.00"), percentage=Decimal("50.00"), due_date="28-Oct-2026"))

        # 5.3 Convocation Quote
        q3 = Quote(
            quotation_number="RS-CA26-0166",
            quotation_date=date.today(),
            status="draft",
            total_amount=Decimal("115000.00"),
            notes="Shoot quotation for annual convocation plus promotional campaign video shoot.",
            discount_type="none",
            discount_value=Decimal("0.00"),
            intro_content="Hey! A big hello from Rian Studioz. First of all, congratulations! We are as excited as you are for the Convocation Ceremony & Ad Shoot. Thank you for considering Rian Studioz for your big day. We guarantee to capture your best moments, which you will look back on with a smile in the future. We eagerly await to surprise you with amazing pictures and videos.",
            brand_id=brand.id,
            quote_type_id=types[5].id,
            template_id=template.id,
            contact_id=contacts[2].id
        )
        db.add(q3)
        db.flush()
        
        db.add(QuoteDetailsJson(quote_id=q3.id, field_key="event_name", field_value="Annual Convocation Ceremony & Campus Walkthrough Video"))
        db.add(QuoteDetailsJson(quote_id=q3.id, field_key="event_date", field_value="August 10th - 11th, 2026"))
        db.add(QuoteDetailsJson(quote_id=q3.id, field_key="venue", field_value="College Auditorium & Campus Grounds, Trichy"))
        
        s4 = QuoteSection(quote_id=q3.id, title="Ad Shoot", sort_order=0)
        s5 = QuoteSection(quote_id=q3.id, title="Convocation", sort_order=1)
        db.add(s4)
        db.add(s5)
        db.flush()
        
        db.add(QuoteLineItem(section_id=s4.id, description="Candid Photography", qty=Decimal("2"), unit_price=Decimal("15000.00"), total_price=Decimal("30000.00"), sort_order=0, is_selected=True, group_name="Ad Shoot", display_order=0))
        db.add(QuoteLineItem(section_id=s4.id, description="Candid Videography", qty=Decimal("2"), unit_price=Decimal("15000.00"), total_price=Decimal("30000.00"), sort_order=1, is_selected=True, group_name="Ad Shoot", display_order=1))
        
        db.add(QuoteLineItem(section_id=s5.id, description="Candid Photography", qty=Decimal("1"), unit_price=Decimal("15000.00"), total_price=Decimal("15000.00"), sort_order=0, is_selected=True, group_name="Convocation", display_order=0))
        db.add(QuoteLineItem(section_id=s5.id, description="Candid Videography", qty=Decimal("1"), unit_price=Decimal("15000.00"), total_price=Decimal("15000.00"), sort_order=1, is_selected=True, group_name="Convocation", display_order=1))
        db.add(QuoteLineItem(section_id=s5.id, description="Traditional Photography", qty=Decimal("2"), unit_price=Decimal("10000.00"), total_price=Decimal("20000.00"), sort_order=2, is_selected=True, group_name="Convocation", display_order=2))
        db.add(QuoteLineItem(section_id=s5.id, description="Traditional Videography", qty=Decimal("2"), unit_price=Decimal("15000.00"), total_price=Decimal("30000.00"), sort_order=3, is_selected=False, group_name="Convocation", display_order=3)) # UNSELECTED
        db.add(QuoteLineItem(section_id=s5.id, description="Drone", qty=Decimal("1"), unit_price=Decimal("15000.00"), total_price=Decimal("15000.00"), sort_order=4, is_selected=True, group_name="Convocation", display_order=4))
        
        db.add(Deliverable(quote_id=q3.id, type="photo", description="All Candid & Traditional Photos (Raw Images)", qty=1, is_selected=True, price=Decimal("0.00"), is_complimentary=True, group_name="Photos", display_order=0))
        db.add(Deliverable(quote_id=q3.id, type="video", description="Full-Length Traditional Video", qty=1, is_selected=True, price=Decimal("0.00"), is_complimentary=True, group_name="Videos", display_order=1))
        
        db.add(PaymentSplit(quote_id=q3.id, stage_name="Retainer Payment (50%)", amount=Decimal("57500.00"), percentage=Decimal("50.00"), due_date="Upon PO confirmation"))
        db.add(PaymentSplit(quote_id=q3.id, stage_name="Delivery Milestone (50%)", amount=Decimal("57500.00"), percentage=Decimal("50.00"), due_date="Upon video draft submission"))

        # 5.4 Election Campaign Quote
        q4 = Quote(
            quotation_number="RS-EL26-0089",
            quotation_date=date.today(),
            status="draft",
            total_amount=Decimal("360000.00"),
            notes="Election campaign digital visual package. Continuous photo/video coverage for constituency visits.",
            discount_type="none",
            discount_value=Decimal("0.00"),
            intro_content="Hey! A big hello from Rian Studioz. First of all, congratulations! We are as excited as you are for the Election Campaign. Thank you for considering Rian Studioz for your big day. We guarantee to capture your best moments, which you will look back on with a smile in the future. We eagerly await to surprise you with amazing pictures and videos.",
            brand_id=brand.id,
            quote_type_id=types[6].id,
            template_id=template.id,
            contact_id=contacts[3].id
        )
        db.add(q4)
        db.flush()
        
        db.add(QuoteDetailsJson(quote_id=q4.id, field_key="campaign_name", field_value="Constituency Public Outreach Campaign"))
        db.add(QuoteDetailsJson(quote_id=q4.id, field_key="event_dates", field_value="10 Days Campaign (1st - 10th November 2026)"))
        db.add(QuoteDetailsJson(quote_id=q4.id, field_key="venue", field_value="Madurai City & Rural Constituencies"))
        
        s6 = QuoteSection(quote_id=q4.id, title="Election Campaign", sort_order=0)
        db.add(s6)
        db.flush()
        
        db.add(QuoteLineItem(section_id=s6.id, description="Traditional Photography", qty=Decimal("10"), unit_price=Decimal("12000.00"), total_price=Decimal("120000.00"), sort_order=0, is_selected=True, group_name="Election Campaign", display_order=0))
        db.add(QuoteLineItem(section_id=s6.id, description="Traditional Videography", qty=Decimal("10"), unit_price=Decimal("12000.00"), total_price=Decimal("120000.00"), sort_order=1, is_selected=True, group_name="Election Campaign", display_order=1))
        db.add(QuoteLineItem(section_id=s6.id, description="Drone", qty=Decimal("10"), unit_price=Decimal("12000.00"), total_price=Decimal("120000.00"), sort_order=2, is_selected=True, group_name="Election Campaign", display_order=2))
        
        db.add(Deliverable(quote_id=q4.id, type="photo", description="All Traditional Photos (Raw Images)", qty=1, is_selected=True, price=Decimal("0.00"), is_complimentary=True, group_name="Photos", display_order=0))
        db.add(Deliverable(quote_id=q4.id, type="video", description="Full-Length Traditional Video", qty=1, is_selected=True, price=Decimal("0.00"), is_complimentary=True, group_name="Videos", display_order=1))
        
        db.add(PaymentSplit(quote_id=q4.id, stage_name="Advance Retainer (40%)", amount=Decimal("144000.00"), percentage=Decimal("40.00"), due_date="Before Campaign"))
        db.add(PaymentSplit(quote_id=q4.id, stage_name="Mid-Campaign Milestone (40%)", amount=Decimal("144000.00"), percentage=Decimal("40.00"), due_date="Day 5 of Campaign"))
        db.add(PaymentSplit(quote_id=q4.id, stage_name="Final Settlement (20%)", amount=Decimal("72000.00"), percentage=Decimal("20.00"), due_date="Within 3 days of Campaign wrap"))

        # 5.5 Custom Quote
        q5 = Quote(
            quotation_number="RS-CU26-0012",
            quotation_date=date.today(),
            status="draft",
            total_amount=Decimal("95000.00"),
            notes="Custom creative media coverage for high-end boutique brand launch.",
            discount_type="none",
            discount_value=Decimal("0.00"),
            intro_content="Hey! A big hello from Rian Studioz. First of all, congratulations! We are as excited as you are for the event. Thank you for considering Rian Studioz for your big day. We guarantee to capture your best moments, which you will look back on with a smile in the future. We eagerly await to surprise you with amazing pictures and videos.",
            brand_id=brand.id,
            quote_type_id=types[9].id,
            template_id=template.id,
            contact_id=contacts[4].id
        )
        db.add(q5)
        db.flush()
        
        db.add(QuoteDetailsJson(quote_id=q5.id, field_key="custom_details", field_value="Brand Launch and Boutique Walkthrough - 1 Day Session"))
        
        s7 = QuoteSection(quote_id=q5.id, title="Boutique Creative Launch", sort_order=0)
        db.add(s7)
        db.flush()
        
        db.add(QuoteLineItem(section_id=s7.id, description="Fashion Creative Photographer + Studio lights setup", qty=Decimal("1"), unit_price=Decimal("45000.00"), total_price=Decimal("45000.00"), sort_order=0, is_selected=True, group_name="Boutique Creative Launch", display_order=0))
        db.add(QuoteLineItem(section_id=s7.id, description="Instagram Highlights Cinematic Editing (1 Reel + 1 Short teaser)", qty=Decimal("1"), unit_price=Decimal("35000.00"), total_price=Decimal("35000.00"), sort_order=1, is_selected=True, group_name="Boutique Creative Launch", display_order=1))
        db.add(QuoteLineItem(section_id=s7.id, description="Model portfolio photoshoot editing fee", qty=Decimal("1"), unit_price=Decimal("15000.00"), total_price=Decimal("15000.00"), sort_order=2, is_selected=True, group_name="Boutique Creative Launch", display_order=2))
        
        db.add(Deliverable(quote_id=q5.id, type="photo", description="50 retouched high-fashion boutique photos, 20 model lookbook cuts", qty=1, is_selected=True, price=Decimal("0.00"), is_complimentary=True, group_name="Photos", display_order=0))
        db.add(Deliverable(quote_id=q5.id, type="video", description="1 Brand launch cinematic video (90 seconds, vertical and landscape formats)", qty=1, is_selected=True, price=Decimal("0.00"), is_complimentary=True, group_name="Videos", display_order=1))
        
        db.add(PaymentSplit(quote_id=q5.id, stage_name="Booking Deposit (50%)", amount=Decimal("47500.00"), percentage=Decimal("50.00"), due_date="On Booking"))
        db.commit()
        print("Database seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
