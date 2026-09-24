import json
from langchain.tools import ToolRuntime, tool
from sqlalchemy import select, func
from backend.agents.context import BankingContext
from backend.db.session import SessionLocal
from backend.models.account import Account
from backend.models.transaction import Transaction
import secrets
from decimal import Decimal


@tool
def get_my_accounts(
    runtime: ToolRuntime[BankingContext],
) -> str:
    """Get all bank accounts belonging to the authenticated customer."""

    customer_id = runtime.context.customer_id

    with SessionLocal() as db:
        statement = select(Account).where(
            Account.customer_id == customer_id
        )

        accounts = list(db.scalars(statement).all())

        if not accounts:
            return "No accounts found."

        return "\n".join(
            (
                f"Account ID: {account.id}, "
                f"Type: {account.account_type}, "
                f"Balance: {account.balance} {account.currency}"
            )
            for account in accounts
        )


@tool
def get_my_recent_transactions(
    runtime: ToolRuntime[BankingContext],
    limit: int = 10,
) -> str:
    """Get recent transactions belonging to the authenticated customer."""

    customer_id = runtime.context.customer_id

    with SessionLocal() as db:
        statement = (
            select(Transaction)
            .join(Account)
            .where(Account.customer_id == customer_id)
            .order_by(Transaction.transaction_date.desc())
            .limit(limit)
        )

        transactions = list(db.scalars(statement).all())

        if not transactions:
            return "No transactions found."

        return "\n".join(
            (
                f"{transaction.transaction_date}: "
                f"{transaction.description}, "
                f"{transaction.amount}, "
                f"{transaction.category}"
            )
            for transaction in transactions
        )
        

def customer_has_account_type(
    customer_id: int,
    account_type: str,
) -> bool:
    """Check whether a customer already owns the specified account type."""

    with SessionLocal() as db:
        account = db.scalar(
            select(Account).where(
                Account.customer_id == customer_id,
                func.lower(Account.account_type) == account_type.lower(),
            )
        )

    return account is not None


def generate_account_number(db) -> str:
    """Generate a unique mock bank account number."""

    while True:
        account_number = str(
            secrets.randbelow(90_000_000) + 10_000_000
        )

        existing = db.scalar(
            select(Account.id).where(
                Account.account_number == account_number
            )
        )

        if existing is None:
            return account_number

def create_customer_account(
    customer_id: int,
    account_type: str,
) -> Account:
    """Create a new bank account for an authenticated customer."""

    with SessionLocal() as db:
        existing_account = db.scalar(
            select(Account).where(
                Account.customer_id == customer_id,
                func.lower(Account.account_type)
                == account_type.lower(),
            )
        )

        if existing_account is not None:
            raise ValueError(
                f"Customer already has an {account_type} account."
            )

        account_number = generate_account_number(db)

        account = Account(
            customer_id=customer_id,
            account_number=account_number,
            account_type=account_type.capitalize(),
            balance=Decimal("0.00"),
            currency="AUD",
        )

        db.add(account)
        db.commit()
        db.refresh(account)

        return account