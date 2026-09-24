from typing import Literal
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from langchain.messages import SystemMessage, HumanMessage, AIMessage
from backend.agents.state import BankingState
from dotenv import load_dotenv

load_dotenv()

class IntentClassification(BaseModel):
    intent: Literal[
        "chat",
        "account",
        "knowledge",
        "card_security",
        "account_opening",
    ] = Field(
        description=(
            "Classify the customer's request into exactly one intent. "
            "'chat' is for greetings, casual conversation, or requests that "
            "do not require banking information or actions. "
            "'account' is for requests concerning the customer's existing "
            "accounts, balances, or transactions. "
            "'knowledge' is for general questions about bank products, "
            "policies, fees, requirements, or documentation that do not "
            "involve opening an account. "
            "'card_security' is for lost, stolen, or compromised cards, "
            "suspicious or unauthorised card transactions, and requests to "
            "freeze a card. "
            "'account_opening' is for requests to open, create, apply for, "
            "or start the process of opening a new bank account."
        )
    )


llm = init_chat_model("gpt-4.1-mini")

router_llm = llm.with_structured_output(IntentClassification)


def classify_intent(state: BankingState) -> dict[str, str]:
    result = router_llm.invoke(
        [
            SystemMessage(
                content=(
                    "You are an intent router for a banking assistant. "
                    "Classify the customer's latest message into one intent.\n\n"

                    "Use 'chat' for greetings and general conversation.\n"

                    "Use 'account' when the customer is asking about their "
                    "existing accounts, balances, or transactions.\n"

                    "Use 'knowledge' when the customer is asking for general "
                    "information about bank products, policies, fees, "
                    "requirements, or documentation.\n"

                    "Use 'card_security' for lost, stolen, or compromised "
                    "cards, suspicious or unauthorised card transactions, "
                    "or requests to freeze a card.\n"

                    "Use 'account_opening' when the customer wants to open, "
                    "create, apply for, or begin opening a new bank account.\n\n"

                    "Examples:\n"
                    "'What is my balance?' -> account\n"
                    "'Show my recent transactions.' -> account\n"
                    "'What are your savings account fees?' -> knowledge\n"
                    "'What documents are required to open an account?' -> knowledge\n"
                    "'I want to open a savings account.' -> account_opening\n"
                    "'Can you help me open a new account?' -> account_opening\n"
                    "'My card was stolen.' -> card_security\n"
                    "'Freeze my credit card.' -> card_security"
                )
            ),
            HumanMessage(content=state["messages"][-1].content),
        ]
    )

    return {"intent": result.intent}