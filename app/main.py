import os
import logging
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import Base, engine, get_db
from app.routers import api, pages

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger("app.main")

# Initialize FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-ready quotation engine for Rian Studioz",
    version="1.0.0"
)

from fastapi import HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc: HTTPException):
    if exc.status_code == 302:
        return RedirectResponse(url="/login")
    return HTMLResponse(content=str(exc.detail), status_code=exc.status_code)

# Ensure PDF output directory exists
os.makedirs(settings.PDF_OUTPUT_DIR, exist_ok=True)

# Ensure static files directory exists
os.makedirs("app/static", exist_ok=True)
os.makedirs("app/static/css", exist_ok=True)
os.makedirs("app/static/js", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Register Routers
app.include_router(pages.router)
app.include_router(api.router)

from sqlalchemy import text

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint for Docker and VPS load balancers.
    Checks database connection.
    """
    try:
        # Simple query to verify DB is online
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "project": settings.PROJECT_NAME
        }
    except Exception as e:
        logger.error(f"Healthcheck failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )

# Create tables on startup if they don't exist
@app.on_event("startup")
def startup_event():
    logger.info("Starting up Rian Studioz Quotation Engine...")
    Base.metadata.create_all(bind=engine)
    
    # Dynamic SQLite migration: add presets_json column if it doesn't exist
    try:
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(brands)")).fetchall()
            columns = [row[1] for row in result]
            if "presets_json" not in columns:
                logger.info("Running DB migration: Adding presets_json column to brands table")
                conn.execute(text("ALTER TABLE brands ADD COLUMN presets_json TEXT"))
                conn.commit()
                logger.info("DB migration: Column added successfully")
            
            # Populate presets_json if null on any existing brand
            brand_records = conn.execute(text("SELECT id, presets_json FROM brands")).fetchall()
            for row in brand_records:
                if not row[1]:
                    from app.core.presets import DEFAULT_PRESETS_JSON_DATA
                    import json
                    logger.info(f"DB migration: Populating default presets_json for brand ID {row[0]}")
                    conn.execute(
                        text("UPDATE brands SET presets_json = :presets_json WHERE id = :id"),
                        {"presets_json": json.dumps(DEFAULT_PRESETS_JSON_DATA, indent=2), "id": row[0]}
                    )
            conn.commit()
    except Exception as e:
        logger.error(f"Dynamic DB migration failed: {e}")
        
    logger.info("Database tables initialized.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
