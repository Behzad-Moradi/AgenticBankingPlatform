from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.models.transaction import Transaction
    
class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True)

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )

    last_four: Mapped[str] = mapped_column(
        String(4),
        nullable=False,
    )

    card_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="card",
    )