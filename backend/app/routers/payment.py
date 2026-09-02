"""Payment router for Midtrans Payment Gateway transactions and webhooks."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.payment import PaymentTransaction
from app.models.user import User
from app.services import midtrans as midtrans_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/create-midtrans-snap")
async def create_midtrans_snap(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a Midtrans Snap transaction token for Pro Student Plan (Rp 29.000)."""
    snap_data = await midtrans_service.create_midtrans_snap_token(
        user_name=current_user.name,
        user_email=current_user.email,
        amount=29000,
    )

    try:
        transaction = PaymentTransaction(
            user_id=current_user.id,
            invoice_id=snap_data["order_id"],
            amount=29000,
            status="PENDING",
            payment_method="MIDTRANS",
            payment_url=snap_data.get("redirect_url"),
        )
        db.add(transaction)
        await db.flush()
    except Exception as e:
        logger.warning(f"Could not save Midtrans transaction: {e}")

    return {
        "token": snap_data["token"],
        "redirect_url": snap_data["redirect_url"],
        "order_id": snap_data["order_id"],
        "client_key": settings.MIDTRANS_CLIENT_KEY,
    }


@router.get("/status/{order_id}")
async def get_payment_status(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check payment status by order_id."""
    res = await db.execute(
        select(PaymentTransaction).where(
            PaymentTransaction.invoice_id == order_id,
            PaymentTransaction.user_id == current_user.id,
        )
    )
    transaction = res.scalar_one_or_none()
    if not transaction:
        raise HTTPException(status_code=404, detail="Order transaksi tidak ditemukan")

    return {
        "order_id": transaction.invoice_id,
        "status": transaction.status,
        "paid_at": transaction.paid_at.isoformat() if transaction.paid_at else None,
        "plan_tier": current_user.plan_tier,
    }


@router.post("/midtrans-notification")
async def midtrans_notification(request: Request, db: AsyncSession = Depends(get_db)):
    """Midtrans Notification Webhook Callback for real-time payment notifications."""
    try:
        payload = await request.json()
        logger.info(f"Midtrans Notification Payload: {payload}")

        order_id = payload.get("order_id")
        transaction_status = payload.get("transaction_status", "").lower()
        fraud_status = payload.get("fraud_status", "").lower()

        is_paid = False
        if transaction_status in ("capture", "settlement"):
            if transaction_status == "capture":
                if fraud_status == "accept":
                    is_paid = True
            else:
                is_paid = True

        if is_paid and order_id:
            res = await db.execute(
                select(PaymentTransaction).where(PaymentTransaction.invoice_id == order_id)
            )
            transaction = res.scalar_one_or_none()

            user = None
            if transaction:
                transaction.status = "PAID"
                transaction.paid_at = datetime.now(timezone.utc)
                u_res = await db.execute(select(User).where(User.id == transaction.user_id))
                user = u_res.scalar_one_or_none()

            if user:
                user.plan_tier = "pro"
                user.storage_quota_bytes = 5368709120  # 5 GB
                logger.info(f"User {user.email} upgraded to PRO via Midtrans Notification!")

            await db.commit()
            return {"status": "SUCCESS", "message": "Midtrans payment notification processed"}

        return {"status": "IGNORED", "message": f"Status {transaction_status} ignored"}
    except Exception as e:
        logger.error(f"Error processing Midtrans Notification: {e}", exc_info=True)
        return {"status": "ERROR", "detail": str(e)}
