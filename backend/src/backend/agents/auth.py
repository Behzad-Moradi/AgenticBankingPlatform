from langgraph.types import interrupt
from sqlalchemy import select

from backend.agents.state import BankingState
from backend.db.session import SessionLocal
from backend.models.customer import Customer
from langchain.messages import SystemMessage, HumanMessage, AIMessage



DEMO_PIN = "1234"
MAX_PIN_ATTEMPTS = 3


def authenticate_customer(state: BankingState) -> dict:
    email = interrupt(
        {
            "type": "authentication",
            "field": "email",
            "message": "Please enter your email address.",
        }
    )

    with SessionLocal() as db:
        customer = db.scalar(
            select(Customer).where(Customer.email == email)
        )

        if customer is None:
            return {
                "authenticated": False,
                "customer_id": None,
                "authentication_error": "Customer not found.",
            }

        customer_id = customer.id

    for attempt in range(MAX_PIN_ATTEMPTS):
        pin = interrupt(
            {
                "type": "authentication",
                "field": "pin",
                "message": (
                    f"Please enter your demo PIN "
                    f"(attempt {attempt + 1}/{MAX_PIN_ATTEMPTS})."
                ),
            }
        )

        if pin == DEMO_PIN:
            return {
                "authenticated": True,
                "customer_id": customer_id,
                "authentication_error": None,
            }

    return {
        "authenticated": False,
        "customer_id": None,
        "authentication_error": "Authentication failed.",
    }
    
    
def authentication_failed(state: BankingState) -> dict:
    error = state.get("authentication_error")

    if error == "Customer not found.":
        message = (
            "Authentication could not be completed. "
            "Please check your details and try again."
        )
    else:
        message = (
            "Authentication failed after the maximum number of attempts. "
            "Please try again later."
        )

    return {
        "messages": [
            AIMessage(content=message)
        ]
    }