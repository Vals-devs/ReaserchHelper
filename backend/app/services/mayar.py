"""Mayar.id Payment Gateway Integration Service."""

import logging
import uuid
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


async def create_mayar_invoice(
    user_name: str,
    user_email: str,
    amount: int = 29000,
    description: str = "ResearchFinder Pro Student Plan (1 Bulan)",
    redirect_url: str = "https://research.ivalpermana.my.id/dashboard",
) -> dict:
    """Create a payment invoice via Mayar.id API (with automatic sandbox fallback)."""
    mayar_api_key = getattr(settings, "MAYAR_API_KEY", "") or ""
    mayar_url = getattr(settings, "MAYAR_API_URL", "https://api.mayar.id/hl/v1/payment/create") or "https://api.mayar.id/hl/v1/payment/create"

    if mayar_api_key and mayar_api_key.strip():
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    mayar_url,
                    headers={
                        "Authorization": f"Bearer {mayar_api_key.strip()}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "name": user_name,
                        "email": user_email,
                        "mobile": "08123456789",
                        "amount": amount,
                        "description": description,
                        "redirectUrl": redirect_url,
                    },
                )
                if response.status_code in (200, 201):
                    res_data = response.json()
                    payload = res_data.get("data", res_data)
                    return {
                        "invoice_id": payload.get("id", f"inv_mayar_{uuid.uuid4().hex[:10]}"),
                        "payment_url": payload.get("link") or payload.get("paymentUrl") or redirect_url,
                        "qr_code_url": payload.get("qrcode") or payload.get("qrCodeUrl"),
                        "status": "PENDING",
                    }
                else:
                    logger.warning(f"Mayar.id API returned {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Failed to communicate with Mayar.id API: {e}", exc_info=True)

    # Sandbox Fallback Mode
    mock_id = f"inv_mayar_{uuid.uuid4().hex[:12]}"
    logger.info(f"Generated Mayar Sandbox invoice {mock_id} for {user_email}")
    return {
        "invoice_id": mock_id,
        "payment_url": f"https://mayar.id/pay/sandbox-{mock_id}",
        "qr_code_url": f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=MAYAR_QRIS_{mock_id}",
        "status": "PENDING",
    }
