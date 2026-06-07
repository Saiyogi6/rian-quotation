# Rian Studioz - Premium Quotation Engine

A production-ready, database-backed quotation management system designed for **Rian Studioz** (photography and video studio). This application supports multiple quotation presets (Wedding, Retirement, Convocation/Ad Shoot, Election Campaign, Custom) under a single master brand visual system. It features a rich, responsive two-panel admin workspace (real-time form editor on the left and a live-rendering document preview on the right), automated PDF compilation using WeasyPrint, and webhook triggers ready for n8n/WhatsApp integrations.

---

## 🚀 Key Features

*   **Unified Presets Engine**: Manage distinct photography and videography presets:
    *   **Wedding**: Capture details for groom, bride, multiple venues, and dates.
    *   **Retirement**: Dedicated retiree name and event dates.
    *   **Convocation & Ad Shoot**: Track shoot dates, campaigns, and commercial licensing.
    *   **Election Campaign**: Custom constituency locations and durational campaign plans.
    *   **Custom**: Completely open-ended, freeform scope details.
*   **Dynamic Document Canvas**: Left-hand editing controls dynamically update the right-hand A4-proportioned paper preview in real-time without screen refreshes.
*   **A4 PDF Compilation**: Generate clean, elegant client-facing PDFs using WeasyPrint with custom CSS, paged-media support, and page-break guards.
*   **Payment Split Milestones**: Create customized milestone payment terms (e.g. 50/40/10) with automatic price calculations.
*   **n8n & Webhook Dispatcher**: Outbound HTTP requests dispatch structured JSON payloads upon quotation finalization, perfect for CRM updates, automated invoicing, or sending WhatsApp notices.
*   **Dockerized Deployment**: Configured with a multi-stage Docker build and compose orchestration for simple VPS hosting.

---

## 📁 Project Directory Structure

```text
rian-quotation/
├── app/
│   ├── core/
│   │   ├── config.py           # Configuration parser & Pydantic settings
│   │   └── database.py         # SQLAlchemy engine & session factory
│   ├── models/
│   │   └── models.py           # Relational SQLAlchemy models
│   ├── schemas/
│   │   └── schemas.py          # Pydantic validation schemas
│   ├── services/
│   │   ├── pdf.py              # WeasyPrint PDF compiler
│   │   └── webhook.py          # Webhook event dispatcher
│   ├── routers/
│   │   ├── api.py              # CRUD API Router (REST)
│   │   └── pages.py            # Jinja2 views router (HTML)
│   ├── templates/              # Server-rendered Jinja2 layouts
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── quote_form.html
│   │   ├── quote_preview.html
│   │   └── settings.html
│   ├── static/                 # Stylesheets, JS modules, and logos
│   │   ├── css/style.css
│   │   ├── js/main.js
│   │   ├── js/preview.js
│   │   └── images/logo.png
│   └── main.py                 # FastAPI application root & table generator
├── tests/                      # Testing suites
│   ├── conftest.py             # Shared fixtures (SQLite in-memory, TestClient)
│   ├── test_routes.py          # Router unit & API validation tests
│   └── test_e2e.py             # E2E browser user-flow verification (Playwright)
├── Dockerfile                  # Application container builder
├── docker-compose.yml          # Local orchestration
├── seed.py                     # Initial database seeding script
├── requirements.txt            # Python dependencies
└── .env.example                # Template for environment variables
```

---

## 🛠️ Installation & Setup (Local Development)

### 1. Prerequisites
Ensure you have the following installed:
*   Python 3.10 or higher
*   [WeasyPrint Dependencies](https://doc.weasyprint.org/en/stable/first_steps.html#installation) (GTK+ or cairo/pango library depending on your platform)
*   SQLite3 or PostgreSQL

### 2. Setup Virtual Environment
Clone the repository, navigate to the directory, and set up your virtual environment:
```powershell
python -m venv venv
venv\Scripts\Activate.ps1   # On Windows
source venv/bin/activate     # On macOS/Linux
```

### 3. Install Python Dependencies
Install required packages:
```powershell
pip install -r requirements.txt
```

### 4. Install Playwright Browsers (For E2E Testing)
Playwright E2E browser tests require chromium binaries:
```powershell
playwright install chromium
```

### 5. Create Local Configuration
Copy the `.env.example` file and configure it as needed. By default, it uses a local SQLite database:
```powershell
copy .env.example .env
```

### 6. Run Database Seeding
Populate the database with default metadata, templates, and 5 realistic sample quotations:
```powershell
python seed.py
```

### 7. Run the Local Development Server
Start the development server:
```powershell
python -m uvicorn app.main:app --reload --port 8000
```
Open your browser to `http://127.0.0.1:8000`. 
*   **Username**: `admin`
*   **Password**: `rianstudioz123`

---

## 🐳 Docker Deployment (VPS / Production)

The application is dockerized and ready for cloud deployment. To build and start the containers:

```bash
docker-compose up -d --build
```

### Configuration notes:
*   The production setup runs on port `8000`. You can configure a reverse proxy (Nginx, Caddy) to map your domain and handle SSL/HTTPS.
*   By default, it will spawn a PostgreSQL service container. The FastAPI application waits for database readiness before booting.
*   To seed the database inside the running Docker container:
    ```bash
    docker-compose exec web python seed.py
    ```

---

## 🧪 Testing Suite

We maintain a high level of test coverage, separating backend endpoint integrations from browser-simulated flows.

### Running Backend Unit & Router Tests
Run the standard pytest suite:
```bash
python -m pytest tests/test_routes.py -v
```

### Running End-to-End Browser Flows
E2E tests will spin up a headless Chromium instance, navigate through the login interface, perform form entries, verify calculations, and execute duplication flows:
```bash
python -m pytest tests/test_e2e.py -v
```

---

## 🪝 Outbound Webhook Integration (n8n/WhatsApp)

When a quote's status updates (e.g. from `draft` to `approved`) or a quote is finalized, the system sends an HTTP POST webhook request containing the entire JSON description of the proposal and the generated public PDF download link.

### Payload Schema:
```json
{
  "event": "quotation.generated",
  "quote_id": 7,
  "quotation_number": "RS-WD26-0255",
  "client_name": "Anand & Divya",
  "client_phone": "+91 99999 88888",
  "total_amount": 185000.0,
  "pdf_url": "http://127.0.0.1:8000/static/pdfs/RS-WD26-0255.pdf",
  "data": {
    "groom_name": "Anand",
    "bride_name": "Divya",
    "venue": "Leela Palace, Chennai",
    "sections": [...]
  }
}
```
You can update the endpoint in the **Settings** view of the admin interface to point directly to an n8n webhook listener node to trigger automated messages (e.g. WhatsApp Cloud API notifications, Google Drive uploads, or calendar entries).
