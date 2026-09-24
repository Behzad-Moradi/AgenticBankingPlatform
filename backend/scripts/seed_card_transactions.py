from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select

from backend.db.session import SessionLocal
from backend.models.account import Account
from backend.models.card import Card
from backend.models.transaction import Transaction


CUSTOMER_ID = 7


with SessionLocal() as db:
    account = db.scalar(
        select(Account).where(
            Account.customer_id == CUSTOMER_ID
        )
    )

    if account is None:
        raise ValueError(
            f"No account found for customer {CUSTOMER_ID}."
        )

    debit_card = db.scalar(
        select(Card).where(
            Card.customer_id == CUSTOMER_ID,
            Card.last_four == "4821",
        )
    )

    credit_card = db.scalar(
        select(Card).where(
            Card.customer_id == CUSTOMER_ID,
            Card.last_four == "7314",
        )
    )

    if debit_card is None or credit_card is None:
        raise ValueError("Test cards were not found.")

    now = datetime.now(timezone.utc)

    transactions = [
        Transaction(
            account_id=account.id,
            card_id=debit_card.id,
            description="Woolworths Melbourne",
            amount=Decimal("-54.30"),
            category="groceries",
            transaction_date=now - timedelta(days=1),
        ),
        Transaction(
            account_id=account.id,
            card_id=debit_card.id,
            description="Melbourne Coffee Co",
            amount=Decimal("-6.50"),
            category="dining",
            transaction_date=now - timedelta(days=2),
        ),
        Transaction(
            account_id=account.id,
            card_id=credit_card.id,
            description="Online Electronics Store",
            amount=Decimal("-899.99"),
            category="shopping",
            transaction_date=now - timedelta(hours=5),
        ),
    ]

    db.add_all(transactions)
    db.commit()


print("Card transactions created.")