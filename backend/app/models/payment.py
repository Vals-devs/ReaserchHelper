"""PaymentTransaction model for tracking Mayar.id payments."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    invoice_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    amount: Mapped[int] = mapped_column(BigInteger, default=29000)
    status: Mapped[str] = mapped_column(String(50), default="PENDING")  # PENDING, PAID, FAILED, EXPIRED
    payment_method: Mapped[str | None] = mapped_column(String(100), nullable=True)
    payment_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    qr_code_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationship
    user = relationship("User", backref="payments")
