from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base

if TYPE_CHECKING:
    from backend.models.account import Account
    from backend.models.card import Card


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)

    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id"),
        index=True,
    )
    
    card_id: Mapped[int | None] = mapped_column(
        ForeignKey("cards.id"),
        nullable=True,
        index=True,
    )

    description: Mapped[str] = mapped_column(String(255))

    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    transaction_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    account: Mapped["Account"] = relationship(
        back_populates="transactions",
    )
    
    card: Mapped["Card | None"] = relationship(
        back_populates="transactions",
    )