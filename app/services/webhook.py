import requests
import logging
from typing import Any, Dict
from app.core.config import settings

logger = logging.getLogger("app.services.webhook")

def trigger_n8n_webhook(payload: Dict[str, Any], pdf_url: str) -> bool:
    """
    Triggers the n8n webhook with the quote payload and PDF URL.
    """
    webhook_url = settings.WEBHOOK_URL
    if not webhook_url:
        logger.info("Webhook url is not set in configuration, skipping webhook trigger.")
        return False
    
    # Enrich the payload with the PDF URL
    full_payload = {
        "event": "quotation.generated",
        "pdf_url": pdf_url,
        "data": payload
    }
    
    try:
        logger.info(f"Triggering webhook: {webhook_url}")
        # Send POST request, timeout after 5 seconds to prevent hanging
        response = requests.post(webhook_url, json=full_payload, timeout=5)
        response.raise_for_status()
        logger.info(f"Webhook triggered successfully. Status code: {response.status_code}")
        return True
    except Exception as e:
        logger.error(f"Failed to trigger webhook: {e}")
        return False
