"""Midtrans Payment Gateway Service."""

import base64
import logging
import uuid
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


async def create_midtrans_snap_token(
    user_name: str,
    user_email: str,
    amount: int = 29000,
    order_id: str | None = None,
) -> dict:
    """Create a Midtrans Snap transaction token."""
    if not order_id:
        order_id = f"RF-{uuid.uuid4().hex[:12]}"

    server_key = settings.MIDTRANS_SERVER_KEY or ""
    is_prod = getattr(settings, "MIDTRANS_IS_PRODUCTION", False)
    
    url = "https://app.midtrans.com/snap/v1/transactions" if is_prod else "https://app.sandbox.midtrans.com/snap/v1/transactions"

    if server_key and "SampleServerKey" not in server_key:
        try:
            auth_header = base64.b64encode(f"{server_key.strip()}:".encode()).decode()
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(
                    url,
                    headers={
                        "Authorization": f"Basic {auth_header}",
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    json={
                        "transaction_details": {
                            "order_id": order_id,
                            "gross_amount": amount,
                        },
                        "customer_details": {
                            "first_name": user_name,
                            "email": user_email,
                        },
                        "item_details": [
                            {
                                "id": "PRO_STUDENT",
                                "price": amount,
                                "quantity": 1,
                                "name": "ResearchFinder Pro Student Plan",
                            }
                        ],
                    },
                )
                if res.status_code in (200, 201):
                    data = res.json()
                    return {
                        "token": data.get("token"),
                        "redirect_url": data.get("redirect_url"),
                        "order_id": order_id,
                    }
                else:
                    logger.warning(f"Midtrans API returned {res.status_code}: {res.text}")
        except Exception as e:
            logger.error(f"Failed to communicate with Midtrans API: {e}", exc_info=True)

    # Sandbox / Demo Fallback Mode
    mock_token = f"snap_mock_{uuid.uuid4().hex[:16]}"
    return {
        "token": mock_token,
        "redirect_url": f"https://app.sandbox.midtrans.com/snap/v2/vtweb/{mock_token}",
        "order_id": order_id,
    }
