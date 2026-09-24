from langchain.messages import AIMessage
from langchain.tools import ToolRuntime
from backend.agents.context import BankingContext
from backend.agents.state import BankingState
from backend.tools.account import customer_has_account_type
import re
from datetime import datetime
from langgraph.types import interrupt
from backend.tools.account import (
    create_customer_account,
    customer_has_account_type,
)

    
def route_existing_account(state: BankingState) -> str:
    if state.get("account_opening_existing_account"):
        return "already_exists"

    return "continue"

def account_already_exists(state: BankingState) -> dict:
    account_type = state["account_opening_type"]

    return {
        "messages": [
            AIMessage(
                content=(
                    f"You already have an {account_type} account, "
                    "so another account of the same type cannot be opened."
                )
            )
        ],
        "account_opening_type": None,
        "account_opening_existing_account": None,
        "account_opening_active": False,
        "account_opening_stage": None,
    }
    
def route_account_type_selection(state: BankingState) -> str:
    if state.get("account_opening_type") is not None:
        return "selected"

    return "not_selected"

def route_personal_details(state: BankingState) -> str:
    required_details = [
        state.get("account_opening_name"),
        state.get("account_opening_date_of_birth"),
        state.get("account_opening_address"),
        state.get("account_opening_phone"),
    ]

    if all(required_details):
        return "complete"

    return "incomplete"

def check_existing_account(
    state: BankingState,
    runtime: ToolRuntime[BankingContext],
) -> dict:

    account_type = state.get("account_opening_type")

    if account_type is None:
        return {
            "account_opening_existing_account": None,
        }

    already_exists = customer_has_account_type(
        customer_id=runtime.context.customer_id,
        account_type=account_type,
    )

    return {
        "account_opening_existing_account": already_exists,
        "account_opening_active": not already_exists,
        "account_opening_stage": (
            "personal_details" if not already_exists else None
        ),
    }
    
def personal_details_complete(state: BankingState) -> dict:
    return {
        "account_opening_stage": "document_upload",
        "messages": [
            AIMessage(
                content=(
                    "Thank you. I have all the required personal details. "
                    "The next step is to upload your driver licence for "
                    "identity verification."
                )
            )
        ],
    }


def normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def normalize_address(value: str) -> str:
    value = value.lower()

    replacements = {
        "street": "st",
        "road": "rd",
        "avenue": "ave",
        "drive": "dr",
        "court": "ct",
        "place": "pl",
    }

    for full, abbreviation in replacements.items():
        value = re.sub(
            rf"\b{full}\b",
            abbreviation,
            value,
        )

    return re.sub(r"[^a-z0-9]", "", value)    

def normalize_date_of_birth(value: str) -> str | None:
    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d %B %Y",
        "%d %b %Y",
    ]

    value = value.strip()

    for date_format in formats:
        try:
            parsed = datetime.strptime(
                value,
                date_format,
            )

            return parsed.strftime("%Y-%m-%d")

        except ValueError:
            continue

    return None


def verify_driver_licence_details(
    application_name: str,
    application_date_of_birth: str,
    application_address: str,
    licence_name: str | None,
    licence_date_of_birth: str | None,
    licence_address: str | None,
) -> bool:

    if not all([
        licence_name,
        licence_date_of_birth,
        licence_address,
    ]):
        return False

    name_matches = (
        normalize_name(application_name)
        == normalize_name(licence_name)
    )

    dob_matches = (
        normalize_date_of_birth(application_date_of_birth)
        == normalize_date_of_birth(licence_date_of_birth)
    )

    address_matches = (
        normalize_address(application_address)
        == normalize_address(licence_address)
    )

    return (
        name_matches
        and dob_matches
        and address_matches
    )
    
def show_application_summary(state: BankingState) -> dict:
    account_type = state.get("account_opening_type")
    name = state.get("account_opening_name")
    dob = state.get("account_opening_date_of_birth")
    address = state.get("account_opening_address")
    phone = state.get("account_opening_phone")

    return {
        "messages": [
            AIMessage(
                content=(
                    "Your account application is ready for submission.\n\n"
                    f"Account type: {account_type}\n"
                    f"Full name: {name}\n"
                    f"Date of birth: {dob}\n"
                    f"Residential address: {address}\n"
                    f"Phone number: {phone}\n\n"
                    "Would you like to submit this application?"
                )
            )
        ],
        "account_opening_stage": "customer_confirmation_response",
    }
    
def route_customer_confirmation(state: BankingState) -> str:
    if state.get("account_opening_customer_confirmed"):
        return "confirmed"

    return "cancelled"

def cancel_account_application(state: BankingState) -> dict:
    return {
        "messages": [
            AIMessage(
                content="Your account application has been cancelled."
            )
        ],
        "account_opening_active": False,
        "account_opening_stage": None,
        "account_opening_customer_confirmed": False,
    }
    
def prepare_for_staff_approval(state: BankingState) -> dict:
    return {
        "account_opening_stage": "staff_approval",
    }
    
def confirm_account_application_by_staff(
    state: BankingState,
) -> dict:

    approved = interrupt(
        {
            "action": "approve_account_opening",
            "account_type": state.get("account_opening_type"),
            "full_name": state.get("account_opening_name"),
            "date_of_birth": state.get(
                "account_opening_date_of_birth"
            ),
            "address": state.get("account_opening_address"),
            "phone": state.get("account_opening_phone"),
            "licence_number": state.get(
                "account_opening_licence_number"
            ),
            "message": (
                "Review this account application and approve or reject it."
            ),
        }
    )

    return {
        "account_opening_staff_approved": bool(approved)
    }
    
def route_staff_approval(state: BankingState) -> str:
    if state.get("account_opening_staff_approved"):
        return "approved"

    return "rejected"

def reject_account_application(state: BankingState) -> dict:
    return {
        "messages": [
            AIMessage(
                content=(
                    "Your account application was not approved. "
                    "No account has been created."
                )
            )
        ],
        "account_opening_active": False,
        "account_opening_stage": None,
        "account_opening_staff_approved": False,
    }
    
def create_approved_account(
    state: BankingState,
    runtime: ToolRuntime[BankingContext],
) -> dict:

    account_type = state.get("account_opening_type")

    if account_type is None:
        return {
            "messages": [
                AIMessage(
                    content=(
                        "The account could not be created because "
                        "the account type is missing."
                    )
                )
            ]
        }

    try:
        account = create_customer_account(
            customer_id=runtime.context.customer_id,
            account_type=account_type,
        )

    except ValueError as exc:
        return {
            "messages": [
                AIMessage(content=str(exc))
            ],
            "account_opening_active": False,
            "account_opening_stage": None,
        }

    return {
        "messages": [
            AIMessage(
                content=(
                    f"Your {account_type} account has been "
                    f"successfully opened. "
                    f"Your account number is {account.account_number}."
                )
            )
        ],
        "account_opening_active": False,
        "account_opening_stage": None,
        "account_opening_customer_confirmed": None,
        "account_opening_staff_approved": None,
    }