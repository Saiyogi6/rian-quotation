import os
import sys
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
            )
        )
        db.add(brand)
        db.flush()
        
        # 2. Seed Quote Types
        types = [
            QuoteType(
                name="Wedding Quotation",
                code="wedding",
                fields_schema='{"fields": [{"name": "groom_name", "label": "Groom\'s Name", "type": "text", "required": true}, {"name": "bride_name", "label": "Bride\'s Name", "type": "text", "required": true}, {"name": "event_dates", "label": "Event Dates (e.g. 15th-16th Oct)", "type": "text", "required": true}, {"name": "venue", "label": "Venue(s)", "type": "text", "required": true}]}'
            ),
            QuoteType(
                name="Retirement Function",
                code="retirement",
                fields_schema='{"fields": [{"name": "client_name", "label": "Retiree Name", "type": "text", "required": true}, {"name": "event_date", "label": "Event Date", "type": "text", "required": true}, {"name": "venue", "label": "Venue", "type": "text", "required": true}]}'
            ),
            QuoteType(
                name="Convocation & Ad Shoot",
                code="convocation_ad",
                fields_schema='{"fields": [{"name": "event_name", "label": "Event / Campaign Name", "type": "text", "required": true}, {"name": "event_date", "label": "Shoot Date(s)", "type": "text", "required": true}, {"name": "venue", "label": "Location / Venue", "type": "text", "required": true}]}'
            ),
            QuoteType(
                name="Election Campaign",
                code="election",
                fields_schema='{"fields": [{"name": "campaign_name", "label": "Candidate / Campaign Name", "type": "text", "required": true}, {"name": "event_dates", "label": "Campaign Duration (Dates)", "type": "text", "required": true}, {"name": "venue", "label": "Constituency / Venue", "type": "text", "required": true}]}'
            ),
            QuoteType(
                name="Custom Quotation",
                code="custom",
                fields_schema='{"fields": [{"name": "custom_details", "label": "Custom Quotation Description", "type": "textarea", "required": false}]}'
            )
        ]
        for t in types:
            db.add(t)
        db.flush()
        
        # 3. Seed Master Template placeholder
        # The main HTML content is stored in the database. 
        # When rendering, we can read this HTML and pass it to Jinja2 rendering.
        # We will build an elegant, premium layout.
        template = Template(
            name="Rian Studioz Master Premium Layout",
            code="master_premium",
            html_content="" # We will store this in Jinja2 template folder for code maintainability, and load it dynamically!
        )
        db.add(template)
        db.flush()

        # 4. Seed Contacts
        contacts = [
            Contact(name="Anand & Divya", email="anand@example.com", phone="+91 99999 88888", address="Adyar, Chennai"),
            Contact(name="Venkatesh Prasad", email="venkatesh@example.com", phone="+91 94444 33333", address="Mylapore, Chennai"),
            Contact(name="St. Joseph's College", email="admin@stjosephs.edu", phone="+91 98400 12345", address="Trichy, TN"),
            Contact(name="Dr. K. Sivaraman (Election)", email="candidate@election.in", phone="+91 90000 11111", address="Madurai constituency"),
            Contact(name="Rakesh Khanna", email="rakesh@khannaproductions.com", phone="+91 98200 98200", address="Juhu, Mumbai")
        ]
        for c in contacts:
            db.add(c)
        db.flush()

        # 5. Create Sample Quotes
        
        # 5.1 Wedding Quote
        q1 = Quote(
            quotation_number="RS-WD26-0255",
            quotation_date=date.today(),
            status="approved",
            total_amount=Decimal("175000.00"),
            notes="Exclusive wedding photography package including customized premium leather albums and drone services.",
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
        s1 = QuoteSection(quote_id=q1.id, title="Pre-Wedding Shoot & Reception", sort_order=0)
        s2 = QuoteSection(quote_id=q1.id, title="Muhurtham & Wedding Events", sort_order=1)
        db.add(s1)
        db.add(s2)
        db.flush()
        
        db.add(QuoteLineItem(section_id=s1.id, description="Outdoor Pre-Wedding shoot (half day, including costumes)", qty=Decimal("1"), unit_price=Decimal("35000.00"), total_price=Decimal("35000.00"), sort_order=0))
        db.add(QuoteLineItem(section_id=s1.id, description="Candid Photography & Cinematic Video (Reception Coverage)", qty=Decimal("1"), unit_price=Decimal("45000.00"), total_price=Decimal("45000.00"), sort_order=1))
        db.add(QuoteLineItem(section_id=s2.id, description="Wedding Muhurtham Coverage (Traditional Photo + Video + Candid)", qty=Decimal("1"), unit_price=Decimal("75000.00"), total_price=Decimal("75000.00"), sort_order=0))
        db.add(QuoteLineItem(section_id=s2.id, description="Drone / Aerial Coverage (Muhurtham)", qty=Decimal("1"), unit_price=Decimal("20000.00"), total_price=Decimal("20000.00"), sort_order=1))
        
        # Deliverables
        db.add(Deliverable(quote_id=q1.id, type="photo", description="150 edited high-res photos for selection, 800+ raw photos shared via cloud link", qty=1))
        db.add(Deliverable(quote_id=q1.id, type="video", description="4-minute Cinematic Teaser and 40-minute Wedding Highlights Video", qty=1))
        db.add(Deliverable(quote_id=q1.id, type="album", description="12x15 Premium Flushmount Leather Bound Wedding Album (40 sheets / 80 pages)", qty=2))
        db.add(Deliverable(quote_id=q1.id, type="turnaround", description="Teaser in 10 days, final deliverables in 45 days after selection", qty=1))
        
        # Payment Splits
        db.add(PaymentSplit(quote_id=q1.id, stage_name="Advance Booking Fee (50%)", amount=Decimal("87500.00"), percentage=Decimal("50.00"), due_date="On Signing"))
        db.add(PaymentSplit(quote_id=q1.id, stage_name="Event Date Milestone (40%)", amount=Decimal("70000.00"), percentage=Decimal("40.00"), due_date="12-Sep-2026"))
        db.add(PaymentSplit(quote_id=q1.id, stage_name="Album Delivery Balance (10%)", amount=Decimal("17500.00"), percentage=Decimal("10.00"), due_date="On Album Handover"))

        # Add-ons
        db.add(AddOn(quote_id=q1.id, description="Additional Candid photographer for Reception", price=Decimal("15000.00"), is_selected=False))
        db.add(AddOn(quote_id=q1.id, description="LED Wall (12x8 ft) for live broadcast at Muhurtham venue", price=Decimal("20000.00"), is_selected=False))

        # 5.2 Retirement Quote
        q2 = Quote(
            quotation_number="RS-RT26-0103",
            quotation_date=date.today(),
            status="sent",
            total_amount=Decimal("48000.00"),
            notes="Retirement celebration function photography package including traditional print and digital shareable gallery.",
            brand_id=brand.id,
            quote_type_id=types[1].id,
            template_id=template.id,
            contact_id=contacts[1].id
        )
        db.add(q2)
        db.flush()
        
        db.add(QuoteDetailsJson(quote_id=q2.id, field_key="client_name", field_value="Venkatesh Prasad"))
        db.add(QuoteDetailsJson(quote_id=q2.id, field_key="event_date", field_value="October 28th, 2026"))
        db.add(QuoteDetailsJson(quote_id=q2.id, field_key="venue", field_value="Vani Mahal, T. Nagar, Chennai"))
        
        s3 = QuoteSection(quote_id=q2.id, title="Retirement Ceremony", sort_order=0)
        db.add(s3)
        db.flush()
        
        db.add(QuoteLineItem(section_id=s3.id, description="Traditional Photography + High-res Digital Copies", qty=Decimal("1"), unit_price=Decimal("18000.00"), total_price=Decimal("18000.00"), sort_order=0))
        db.add(QuoteLineItem(section_id=s3.id, description="Candid Video Coverage & Short Tribute Video", qty=Decimal("1"), unit_price=Decimal("20000.00"), total_price=Decimal("20000.00"), sort_order=1))
        db.add(QuoteLineItem(section_id=s3.id, description="Premium Photo Frame (A3 Size, Wooden border)", qty=Decimal("2"), unit_price=Decimal("5000.00"), total_price=Decimal("10000.00"), sort_order=2))
        
        db.add(Deliverable(quote_id=q2.id, type="photo", description="300+ edited digital images delivered via high-speed gallery link", qty=1))
        db.add(Deliverable(quote_id=q2.id, type="album", description="12x18 Magazine Style Layflat Hardcover Album (30 pages)", qty=1))
        db.add(Deliverable(quote_id=q2.id, type="other", description="Complimentary digital invitation card (JPG/PDF format)", qty=1))
        
        db.add(PaymentSplit(quote_id=q2.id, stage_name="Advance Booking Fee (50%)", amount=Decimal("24000.00"), percentage=Decimal("50.00"), due_date="On Signing"))
        db.add(PaymentSplit(quote_id=q2.id, stage_name="Event Day Payment (50%)", amount=Decimal("24000.00"), percentage=Decimal("50.00"), due_date="28-Oct-2026"))

        # 5.3 Convocation Quote
        q3 = Quote(
            quotation_number="RS-CA26-0166",
            quotation_date=date.today(),
            status="draft",
            total_amount=Decimal("110000.00"),
            notes="Shoot quotation for annual convocation plus promotional campaign video shoot.",
            brand_id=brand.id,
            quote_type_id=types[2].id,
            template_id=template.id,
            contact_id=contacts[2].id
        )
        db.add(q3)
        db.flush()
        
        db.add(QuoteDetailsJson(quote_id=q3.id, field_key="event_name", field_value="Annual Convocation Ceremony & Campus Walkthrough Video"))
        db.add(QuoteDetailsJson(quote_id=q3.id, field_key="event_date", field_value="August 10th - 11th, 2026"))
        db.add(QuoteDetailsJson(quote_id=q3.id, field_key="venue", field_value="College Auditorium & Campus Grounds, Trichy"))
        
        s4 = QuoteSection(quote_id=q3.id, title="Convocation Event Coverage", sort_order=0)
        s5 = QuoteSection(quote_id=q3.id, title="Promotional Video Shoot", sort_order=1)
        db.add(s4)
        db.add(s5)
        db.flush()
        
        db.add(QuoteLineItem(section_id=s4.id, description="Traditional Event Photography (2 photographers, 2 days)", qty=Decimal("1"), unit_price=Decimal("40000.00"), total_price=Decimal("40000.00"), sort_order=0))
        db.add(QuoteLineItem(section_id=s4.id, description="Standard multi-camera video setup with raw outputs", qty=Decimal("1"), unit_price=Decimal("30000.00"), total_price=Decimal("30000.00"), sort_order=1))
        db.add(QuoteLineItem(section_id=s5.id, description="Direction and Cinematography for Campus Walkthrough (1 day)", qty=Decimal("1"), unit_price=Decimal("40000.00"), total_price=Decimal("40000.00"), sort_order=0))
        
        db.add(Deliverable(quote_id=q3.id, type="video", description="Full length Convocation recording (around 3 hours) and 3-minute Campus Promo Reel", qty=1))
        db.add(Deliverable(quote_id=q3.id, type="photo", description="Selected stage photography and group class photos in digital layout", qty=1))
        
        db.add(PaymentSplit(quote_id=q3.id, stage_name="Retainer Payment (50%)", amount=Decimal("55000.00"), percentage=Decimal("50.00"), due_date="Upon PO confirmation"))
        db.add(PaymentSplit(quote_id=q3.id, stage_name="Delivery Milestone (50%)", amount=Decimal("55000.00"), percentage=Decimal("50.00"), due_date="Upon video draft submission"))

        # 5.4 Election Campaign Quote
        q4 = Quote(
            quotation_number="RS-EL26-0089",
            quotation_date=date.today(),
            status="draft",
            total_amount=Decimal("320000.00"),
            notes="Election campaign digital visual package. Continuous photo/video coverage for constituency visits.",
            brand_id=brand.id,
            quote_type_id=types[3].id,
            template_id=template.id,
            contact_id=contacts[3].id
        )
        db.add(q4)
        db.flush()
        
        db.add(QuoteDetailsJson(quote_id=q4.id, field_key="campaign_name", field_value="Constituency Public Outreach Campaign"))
        db.add(QuoteDetailsJson(quote_id=q4.id, field_key="event_dates", field_value="10 Days Campaign (1st - 10th November 2026)"))
        db.add(QuoteDetailsJson(quote_id=q4.id, field_key="venue", field_value="Madurai City & Rural Constituencies"))
        
        s6 = QuoteSection(quote_id=q4.id, title="Outreach Video Production", sort_order=0)
        db.add(s6)
        db.flush()
        
        db.add(QuoteLineItem(section_id=s6.id, description="Dedicated Cameraman + Editor on site for 10 days", qty=Decimal("10"), unit_price=Decimal("25000.00"), total_price=Decimal("250000.00"), sort_order=0))
        db.add(QuoteLineItem(section_id=s6.id, description="Drone aerial coverage (Constituency rallies - 5 key locations)", qty=Decimal("5"), unit_price=Decimal("10000.00"), total_price=Decimal("50000.00"), sort_order=1))
        db.add(QuoteLineItem(section_id=s6.id, description="Social media format editing (Instagram reels / WhatsApp clips)", qty=Decimal("1"), unit_price=Decimal("20000.00"), total_price=Decimal("20000.00"), sort_order=2))
        
        db.add(Deliverable(quote_id=q4.id, type="video", description="Daily reels (2 per day), 1 consolidated campaign highlights film (8 minutes)", qty=1))
        db.add(Deliverable(quote_id=q4.id, type="photo", description="Unlimited rally and candidate portfolio photos edited daily", qty=1))
        
        db.add(PaymentSplit(quote_id=q4.id, stage_name="Advance Retainer (40%)", amount=Decimal("128000.00"), percentage=Decimal("40.00"), due_date="Before Campaign"))
        db.add(PaymentSplit(quote_id=q4.id, stage_name="Mid-Campaign Milestone (40%)", amount=Decimal("128000.00"), percentage=Decimal("40.00"), due_date="Day 5 of Campaign"))
        db.add(PaymentSplit(quote_id=q4.id, stage_name="Final Settlement (20%)", amount=Decimal("64000.00"), percentage=Decimal("20.00"), due_date="Within 3 days of Campaign wrap"))

        # 5.5 Custom Quote
        q5 = Quote(
            quotation_number="RS-CU26-0012",
            quotation_date=date.today(),
            status="draft",
            total_amount=Decimal("95000.00"),
            notes="Custom creative media coverage for high-end boutique brand launch.",
            brand_id=brand.id,
            quote_type_id=types[4].id,
            template_id=template.id,
            contact_id=contacts[4].id
        )
        db.add(q5)
        db.flush()
        
        db.add(QuoteDetailsJson(quote_id=q5.id, field_key="custom_details", field_value="Brand Launch and Boutique Walkthrough - 1 Day Session"))
        
        s7 = QuoteSection(quote_id=q5.id, title="Boutique Creative Launch", sort_order=0)
        db.add(s7)
        db.flush()
        
        db.add(QuoteLineItem(section_id=s7.id, description="Fashion Creative Photographer + Studio lights setup", qty=Decimal("1"), unit_price=Decimal("45000.00"), total_price=Decimal("45000.00"), sort_order=0))
        db.add(QuoteLineItem(section_id=s7.id, description="Instagram Highlights Cinematic Editing (1 Reel + 1 Short teaser)", qty=Decimal("1"), unit_price=Decimal("35000.00"), total_price=Decimal("35000.00"), sort_order=1))
        db.add(QuoteLineItem(section_id=s7.id, description="Model portfolio photoshoot editing fee", qty=Decimal("1"), unit_price=Decimal("15000.00"), total_price=Decimal("15000.00"), sort_order=2))
        
        db.add(Deliverable(quote_id=q5.id, type="photo", description="50 retouched high-fashion boutique photos, 20 model lookbook cuts", qty=1))
        db.add(Deliverable(quote_id=q5.id, type="video", description="1 Brand launch cinematic video (90 seconds, vertical and landscape formats)", qty=1))
        
        db.add(PaymentSplit(quote_id=q5.id, stage_name="Booking Deposit (50%)", amount=Decimal("47500.00"), percentage=Decimal("50.00"), due_date="On Booking"))
        db.add(PaymentSplit(quote_id=q5.id, stage_name="Post-Shoot Submission (50%)", amount=Decimal("47500.00"), percentage=Decimal("50.00"), due_date="On Deliverables Draft"))

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
