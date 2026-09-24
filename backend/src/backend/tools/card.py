import json
from langchain.tools import ToolRuntime, tool
from sqlalchemy import select
from backend.agents.context import BankingContext
from backend.db.session import SessionLocal
from backend.models.card import Card
from backend.models.account import Account
from backend.models.transaction import Transaction

@tool
def get_customer_cards(
    runtime: ToolRuntime[BankingContext],
) -> str:
    """Get the authenticated customer's bank cards."""

    customer_id = runtime.context.customer_id

    with SessionLocal() as db:
        cards = db.scalars(
            select(Card).where(
                Card.customer_id == customer_id
            )
        ).all()

        if not cards:
            return "The customer has no cards."

        return json.dumps(
            [
                {
                    "card_id": card.id,
                    "last_four": card.last_four,
                    "card_type": card.card_type,
                    "status": card.status,
                }
                for card in cards
            ]
        )
 


@tool
def get_recent_card_transactions(
    runtime: ToolRuntime[BankingContext],
) -> str:
    """Get recent card transactions belonging to the authenticated customer."""

    customer_id = runtime.context.customer_id

    with SessionLocal() as db:
        transactions = db.execute(
            select(Transaction, Card)
            .join(
                Card,
                Transaction.card_id == Card.id,
            )
            .join(
                Account,
                Transaction.account_id == Account.id,
            )
            .where(
                Account.customer_id == customer_id,
                Card.customer_id == customer_id,
                Transaction.card_id.is_not(None),
            )
            .order_by(
                Transaction.transaction_date.desc()
            )
            .limit(10)
        ).all()

        if not transactions:
            return "No recent card transactions were found."

        return "\n".join(
            (
                f"Transaction ID: {transaction.id}, "
                f"Card ending: {card.last_four}, "
                f"Description: {transaction.description}, "
                f"Amount: {transaction.amount}, "
                f"Category: {transaction.category}, "
                f"Date: {transaction.transaction_date}"
            )
            for transaction, card in transactions
        )
        
        
def freeze_customer_card(
    card_id: int,
    customer_id: int,
) -> str:
    """Freeze a card after ownership has been verified."""

    with SessionLocal() as db:
        card = db.scalar(
            select(Card).where(
                Card.id == card_id,
                Card.customer_id == customer_id,
            )
        )

        if card is None:
            return "Card not found."

        if card.status == "frozen":
            return (
                f"Card ending in {card.last_four} "
                "is already frozen."
            )

        card.status = "frozen"
        db.commit()

        return (
            f"Card ending in {card.last_four} "
            "has been frozen."
        )
        
@tool
def freeze_card(
    card_id: int,
    runtime: ToolRuntime[BankingContext],
) -> str:
    """Freeze one of the authenticated customer's cards."""

    return freeze_customer_card(
        card_id=card_id,
        customer_id=runtime.context.customer_id,
    )
