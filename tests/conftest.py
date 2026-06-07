import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date
from decimal import Decimal

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.core.database import Base, get_db
from app.models.models import Brand, QuoteType, Template, Contact

from sqlalchemy.pool import StaticPool

# Use in-memory SQLite for testing with StaticPool
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        # Seed required testing dependencies
        brand = Brand(
            name="Rian Studioz",
            email="contact@rianstudioz.com",
            phone="+91 98765 43210",
            address="Cathedral Road, Chennai",
            terms_and_conditions="50/40/10 Split.",
            payment_info="HDFC Bank"
        )
        db.add(brand)
        db.flush()
        
        qtype = QuoteType(
            name="Wedding Quotation",
            code="wedding",
            fields_schema='{"fields": [{"name": "groom_name", "label": "Groom", "type": "text"}]}'
        )
        db.add(qtype)
        db.flush()
        
        template = Template(
            name="Master Layout",
            code="master_premium",
            html_content="<h1>Test Template</h1>"
        )
        db.add(template)
        db.flush()
        
        contact = Contact(
            name="Test Client",
            email="test@example.com",
            phone="+91 90000 90000",
            address="Chennai"
        )
        db.add(contact)
        db.commit()
        
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        # Set authentication cookie directly to bypass login page in API/integration testing
        c.cookies.set("session_id", "logged_in")
        yield c
    app.dependency_overrides.clear()
