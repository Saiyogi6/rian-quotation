import os
import sys
import time
import subprocess
import pytest
from playwright.sync_api import sync_playwright

# Setup module level fixture to spin up the FastAPI app on port 8001
@pytest.fixture(scope="module")
def server():
    # Setup test env variables
    env = os.environ.copy()
    env["DATABASE_URL"] = "sqlite:///./rian_test_e2e.db"
    
    # Seed the database
    subprocess.run(["python", "seed.py"], env=env, stdout=subprocess.DEVNULL)
    
    # Start FastAPI server on port 8001
    log_file = open("rian_e2e_server.log", "w")
    proc = subprocess.Popen(
        ["python", "-m", "uvicorn", "app.main:app", "--port", "8001"],
        env=env,
        stdout=log_file,
        stderr=log_file
    )
    # Wait for startup
    time.sleep(2)
    yield "http://127.0.0.1:8001"
    
    # Terminate and clean
    proc.terminate()
    proc.wait()
    log_file.close()
    if os.path.exists("rian_test_e2e.db"):
        try:
            os.remove("rian_test_e2e.db")
        except:
            pass

def test_workflow(server):
    """
    Consolidated Playwright test script running the entire user flow:
    Login -> Dashboard list check -> Create quote -> Duplicate quote -> Preview -> Mobile check.
    """
    with sync_playwright() as p:
        # Launch browser in headless mode
        # If chromium executable is missing, playwright will warn.
        # We start it as headless to run in automated pipelines.
        try:
            browser = p.chromium.launch(headless=True)
        except Exception as e:
            pytest.skip(f"Skipping E2E tests: Playwright browser not installed. Run 'playwright install chromium' ({e})")
            return
            
        context = browser.new_context()
        page = context.new_page()
        
        # 1. Login flow
        page.goto(f"{server}/login")
        page.wait_for_selector("#username")
        assert "Login" in page.title()
        
        page.fill("#username", "admin")
        page.fill("#password", "rianstudioz123")
        page.click("button[type='submit']")
        
        page.wait_for_url(f"{server}/")
        page.wait_for_selector(".quote-table-container")
        assert "Dashboard" in page.title()
        
        # Verify seeded quotes are displayed
        assert page.locator("text=RS-WD26-0255").is_visible()
        assert page.locator("text=Anand & Divya").is_visible()
        
        # 2. Create Quote Flow
        page.goto(f"{server}/quotes/new")
        page.wait_for_selector("#client_name")
        assert "New Quote" in page.title()
        
        # Select Retirement card chip
        page.click(".preset-card[data-type='retirement']")
        
        # Fill administrative data
        page.fill("#client_name", "E2E Test Client")
        page.fill("#client_phone", "+91 91111 91111")
        page.fill("#client_email", "e2e@example.com")
        page.fill("#client_address", "E2E Road, Chennai")
        
        # Fill Retirement meta specifications
        page.fill("#fields_retirement input[name='client_name']", "Dr. Sundararajan")
        page.fill("#fields_retirement input[name='event_date']", "30th November 2026")
        page.fill("#fields_retirement input[name='venue']", "Leela Palace, Chennai")
        
        # Sync line items description and price
        page.locator(".item-desc-select").first.select_option("__custom__")
        page.locator(".item-desc").first.fill("E2E Traditional Retirement Photography")
        page.locator(".item-qty").first.fill("1")
        page.locator(".item-price").first.fill("25000")
        
        # Verify right side live preview updates
        page.wait_for_selector("#preview_client_name")
        assert page.locator("#preview_client_name").text_content() == "E2E Test Client"
        assert "₹48,000.00" in page.locator("#preview_grand_total").text_content()
        
        # Click "Save & Finalize"
        page.click("button:has-text('Save & Finalize')")
        
        # Verify redirect to dashboard and visibility of new quote
        page.wait_for_url(f"{server}/")
        assert page.locator("text=E2E Test Client").is_visible()
        
        # 3. Duplicate Quote Flow
        # Locate the new row
        row = page.locator("tr", has_text="E2E Test Client")
        assert row.count() > 0
        
        # Click duplicate action button on that row
        # Duplication prompts a confirmation dialog, handle it:
        page.once("dialog", lambda dialog: dialog.accept())
        row.locator("button[title='Duplicate Quote']").click()
        
        # Wait for reload
        page.wait_for_timeout(1500)
        
        # Verify duplicated quote exists with prefix "RS-DUP-"
        assert page.locator("text=RS-DUP-").is_visible()
        
        # 4. Standalone Preview page test
        # Get first row ID link (preview view opens in a new tab, so we intercept)
        with context.expect_page() as new_page_info:
            page.locator("a[title='View Proposal Preview']").first.click()
        new_page = new_page_info.value
        new_page.wait_for_load_state()
        
        # Verify elements are rendered in standalone document canvas
        assert new_page.locator(".quote-canvas").is_visible()
        assert new_page.locator(".studio-name").text_content() == "Rian Studioz"
        new_page.close()
        
        # 5. Mobile responsive smoke test
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(f"{server}/")
        page.wait_for_selector(".quote-table-container")
        assert page.locator(".quote-table-container").is_visible()
        
        # Open editor in mobile view
        page.goto(f"{server}/quotes/new")
        page.wait_for_selector(".form-panel")
        assert page.locator(".form-panel").is_visible()
        
        browser.close()
