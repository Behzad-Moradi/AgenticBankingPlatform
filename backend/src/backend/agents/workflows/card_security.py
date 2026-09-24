from langchain.messages import AIMessage
from langchain.tools import ToolRuntime
from langgraph.types import interrupt
from sqlalchemy import select

from backend.agents.context import BankingContext
from backend.agents.state import BankingState
from backend.db.session import SessionLocal
from backend.models.card import Card
from backend.tools.card import freeze_customer_card


def route_card_security_action(
    state: BankingState,
) -> str:
    if state.get("pending_card_last_four"):
        return "freeze_requested"

    return "done"


def resolve_card_for_freeze(
    state: BankingState,
    runtime: ToolRuntime[BankingContext],
) -> dict:
    last_four = state.get("pending_card_last_four")

    if last_four is None:
        return {"pending_card_id": None}

    customer_id = runtime.context.customer_id

    with SessionLocal() as db:
        card = db.scalar(
            select(Card).where(
                Card.customer_id == customer_id,
                Card.last_four == last_four,
            )
        )

        if card is None:
            return {"pending_card_id": None}

        return {
            "pending_card_id": card.id,
            "pending_card_last_four": card.last_four,
        }


def route_resolved_card(
    state: BankingState,
) -> str:
    if state.get("pending_card_id") is not None:
        return "resolved"

    return "not_found"


def card_not_found(
    state: BankingState,
) -> dict:
    return {
        "messages": [
            AIMessage(
                content=(
                    "I couldn't find that card among "
                    "your cards, so no action was taken."
                )
            )
        ],
        "pending_card_id": None,
        "pending_card_last_four": None,
        "freeze_approved": None,
    }


def confirm_card_freeze(
    state: BankingState,
) -> dict:
    approved = interrupt(
        {
            "action": "freeze_card",
            "card_id": state["pending_card_id"],
            "last_four": state["pending_card_last_four"],
            "message": (
                f"Do you want to freeze the card ending in "
                f"{state['pending_card_last_four']}?"
            ),
        }
    )

    return {
        "freeze_approved": bool(approved),
    }


def route_freeze_confirmation(
    state: BankingState,
) -> str:
    if state.get("freeze_approved"):
        return "approved"

    return "rejected"


def reject_card_freeze(
    state: BankingState,
) -> dict:
    return {
        "messages": [
            AIMessage(content="The card was not frozen.")
        ],
        "pending_card_id": None,
        "pending_card_last_four": None,
        "freeze_approved": None,
    }


def execute_card_freeze(
    state: BankingState,
    runtime: ToolRuntime[BankingContext],
) -> dict:
    card_id = state.get("pending_card_id")

    if card_id is None:
        return {
            "messages": [
                AIMessage(
                    content=(
                        "The card could not be frozen because "
                        "no valid card was selected."
                    )
                )
            ],
        }

    result = freeze_customer_card(
        card_id=card_id,
        customer_id=runtime.context.customer_id,
    )

    return {
        "messages": [
            AIMessage(content=result)
        ],
        "pending_card_id": None,
        "pending_card_last_four": None,
        "freeze_approved": None,
    }