"""Payment router for Mayar.id transactions and webhooks."""

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
from app.services import mayar as mayar_service, midtrans as midtrans_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/create-checkout")
async def create_checkout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a Mayar.id checkout session & invoice for Pro Student Plan (Rp 29.000)."""
    amount = 29000
    description = "ResearchFinder Pro Student Plan (1 Bulan - 5 GB Storage)"

    invoice_data = await mayar_service.create_mayar_invoice(
        user_name=current_user.name,
        user_email=current_user.email,
        amount=amount,
        description=description,
    )

    transaction = PaymentTransaction(
        user_id=current_user.id,
        invoice_id=invoice_data["invoice_id"],
        amount=amount,
        status="PENDING",
        payment_url=invoice_data["payment_url"],
        qr_code_url=invoice_data["qr_code_url"],
    )
    db.add(transaction)
    await db.flush()
    await db.refresh(transaction)

    return {
        "id": transaction.id,
        "invoice_id": transaction.invoice_id,
        "amount": transaction.amount,
        "status": transaction.status,
        "payment_url": transaction.payment_url,
        "qr_code_url": transaction.qr_code_url,
    }


@router.get("/status/{invoice_id}")
async def get_payment_status(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check payment status by invoice_id."""
    res = await db.execute(
        select(PaymentTransaction).where(
            PaymentTransaction.invoice_id == invoice_id,
            PaymentTransaction.user_id == current_user.id,
        )
    )
    transaction = res.scalar_one_or_none()
    if not transaction:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")

    return {
        "invoice_id": transaction.invoice_id,
        "status": transaction.status,
        "paid_at": transaction.paid_at.isoformat() if transaction.paid_at else None,
        "plan_tier": current_user.plan_tier,
    }


@router.post("/simulate-confirm/{invoice_id}")
async def simulate_confirm_payment(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Simulate successful payment confirmation in test mode."""
    res = await db.execute(
        select(PaymentTransaction).where(
            PaymentTransaction.invoice_id == invoice_id,
            PaymentTransaction.user_id == current_user.id,
        )
    )
    transaction = res.scalar_one_or_none()
    if not transaction:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")

    transaction.status = "PAID"
    transaction.paid_at = datetime.now(timezone.utc)

    # Upgrade User to Pro
    current_user.plan_tier = "pro"
    current_user.storage_quota_bytes = 5368709120  # 5 GB

    await db.flush()
    await db.refresh(current_user)

    return {
        "status": "PAID",
        "message": "Pembayaran berhasil dikonfirmasi. Akun di-upgrade ke Paket Pro Student!",
        "plan_tier": current_user.plan_tier,
        "storage_quota_bytes": current_user.storage_quota_bytes,
    }


@router.post("/mayar-webhook")
async def mayar_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Mayar.id Webhook Callback for real-time payment success notifications."""
    try:
        payload = await request.json()
        logger.info(f"Mayar Webhook Payload: {payload}")

        event = payload.get("event") or payload.get("type", "")
        data = payload.get("data", payload)

        invoice_id = data.get("id") or data.get("invoiceId") or data.get("transactionId")
        user_email = data.get("email") or data.get("customerEmail")
        payment_status = data.get("status", "").upper()

        if payment_status in ("PAID", "SUCCESS", "COMPLETED") or "success" in event.lower():
            # Find transaction & user
            tx_res = await db.execute(
                select(PaymentTransaction).where(PaymentTransaction.invoice_id == invoice_id)
            )
            transaction = tx_res.scalar_one_or_none()

            user = None
            if transaction:
                user_res = await db.execute(select(User).where(User.id == transaction.user_id))
                user = user_res.scalar_one_or_none()
            elif user_email:
                user_res = await db.execute(select(User).where(User.email == user_email))
                user = user_res.scalar_one_or_none()

            if transaction:
                transaction.status = "PAID"
                transaction.paid_at = datetime.now(timezone.utc)

            if user:
                user.plan_tier = "pro"
                user.storage_quota_bytes = 5368709120  # 5 GB
                logger.info(f"User {user.email} upgraded to PRO via Mayar Webhook!")

            await db.commit()
            return {"status": "SUCCESS", "message": "Webhook processed successfully"}

        return {"status": "IGNORED", "message": f"Event {event} with status {payment_status} ignored"}
    except Exception as e:
        logger.error(f"Error processing Mayar Webhook: {e}", exc_info=True)
        return {"status": "ERROR", "detail": str(e)}


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


@router.post("/confirm-direct")
async def confirm_direct_payment(
    method: str = "qris",
    sender_name: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Direct QRIS & Bank Transfer Confirmation without third-party API fees."""
    import uuid
    tx_id = f"tx_direct_{uuid.uuid4().hex[:10]}"
    
    try:
        transaction = PaymentTransaction(
            user_id=current_user.id,
            invoice_id=tx_id,
            amount=29000,
            status="PAID",
            payment_method=method.upper(),
            paid_at=datetime.now(timezone.utc),
        )
        db.add(transaction)
    except Exception as e:
        logger.warning(f"Could not log payment_transaction: {e}")

    # Upgrade User to Pro
    current_user.plan_tier = "pro"
    current_user.storage_quota_bytes = 5368709120  # 5 GB

    await db.flush()
    await db.refresh(current_user)

    return {
        "status": "SUCCESS",
        "message": f"Konfirmasi pembayaran via {method.upper()} berhasil! Akun di-upgrade ke Paket Pro Student.",
        "plan_tier": current_user.plan_tier,
        "storage_quota_bytes": current_user.storage_quota_bytes,
        "invoice_id": tx_id,
    }
