from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select

from backend.db.session import SessionLocal
from backend.models.account import Account
from backend.models.customer import Customer
from backend.models.transaction import Transaction


with SessionLocal() as db:
    customer = db.scalar(
        select(Customer).where(Customer.email == "a.m@gmail.com")
    )

    if customer is None:
        raise ValueError("Customer not found.")

    account = Account(
        customer_id=customer.id,
        account_number="10000001",
        account_type="Everyday",
        balance=Decimal("4250.75"),
        currency="AUD",
    )

    db.add(account)
    db.flush()

    now = datetime.now(timezone.utc)

    transactions = [
        Transaction(
            account_id=account.id,
            description="Salary",
            amount=Decimal("4500.00"),
            category="Income",
            transaction_date=now - timedelta(days=2),
        ),
        Transaction(
            account_id=account.id,
            description="Woolworths",
            amount=Decimal("-86.40"),
            category="Groceries",
            transaction_date=now - timedelta(days=1),
        ),
        Transaction(
            account_id=account.id,
            description="Netflix",
            amount=Decimal("-22.99"),
            category="Entertainment",
            transaction_date=now - timedelta(hours=12),
        ),
        Transaction(
            account_id=account.id,
            description="Shell",
            amount=Decimal("-74.50"),
            category="Transport",
            transaction_date=now - timedelta(hours=5),
        ),
    ]

    db.add_all(transactions)
    db.commit()

    print(f"Created account {account.account_number}")
    print(f"Created {len(transactions)} transactions")