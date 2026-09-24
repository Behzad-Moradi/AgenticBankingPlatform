from langchain.agents import create_agent
from langgraph.runtime import Runtime
from backend.agents.context import BankingContext
from backend.agents.state import BankingState
from backend.tools.customer import get_customer_by_email
from backend.tools.account import get_my_recent_transactions, get_my_accounts
from backend.schemas.agent import AccountAgentResponse
from langchain.chat_models import init_chat_model
from langchain.messages import AIMessage, SystemMessage
from backend.tools.knowledge import search_bank_knowledge
from backend.tools.card import get_customer_cards, get_recent_card_transactions
from backend.schemas.agent import KnowledgeAgentResponse
from typing import Literal
from pydantic import BaseModel, Field

from dotenv import load_dotenv

load_dotenv()

account_agent_executor = create_agent(
    model="gpt-4.1-mini",
    tools=[
        get_my_accounts,
        get_my_recent_transactions,
    ],
    context_schema=BankingContext,
    response_format=AccountAgentResponse,
    system_prompt=(
        "You are a banking account assistant. "
        "Help the authenticated customer understand their accounts "
        "and transactions. "
        "Use the available tools whenever banking data is required. "
        "Never invent balances, transactions, or customer information."
    ),
)


def account_agent(
    state: BankingState,
    runtime: Runtime[BankingContext],
) -> dict:
    result = account_agent_executor.invoke(
        {
            "messages": state["messages"],
        },
        context=runtime.context,
    )

    response = result["structured_response"]

    return {
        "messages": [
            AIMessage(content=response.answer)
        ]
    }


################################################################################

chat_llm = init_chat_model("gpt-4.1-mini")

def chat_agent(state: BankingState) -> dict:
    response = chat_llm.invoke(
        [
            SystemMessage(
                content=(
                    "You are a helpful banking assistant. "
                    "Handle general conversation naturally and concisely. "
                    "Do not invent customer account information."
                )
            ),
            *state["messages"],
        ]
    )

    return {
        "messages": [
            AIMessage(content=response.content)
        ]
    }

################################################################################

knowledge_agent_executor = create_agent(
    model="gpt-4.1-mini",
    tools=[search_bank_knowledge],
    response_format=KnowledgeAgentResponse,
    system_prompt=(
        "You are a banking knowledge assistant. "
        "Answer questions about bank policies, products, fees, "
        "security, and documentation. "
        "Use the search_bank_knowledge tool whenever bank-specific "
        "information is required. "
        "Base bank-specific answers only on information returned "
        "by the knowledge tool. "
        "Include only sources actually returned by the knowledge tool. "
        "If no relevant information is found, say that the bank's "
        "knowledge base does not contain enough information and "
        "return an empty sources list. "
        "Never invent banking policies, fees, product details, or sources."
    ),
)
        
def knowledge_agent(state: BankingState) -> dict:
    result = knowledge_agent_executor.invoke(
        {
            "messages": state["messages"],
        }
    )

    response = result["structured_response"]

    return {
        "messages": [
            AIMessage(content=response.answer)
        ],
        "sources": [
            {
                "source": item.source,
                "page": item.page,
                "chunk_index": item.chunk_index,
            }
            for item in response.sources
        ],
    }
    
################################################################################

class CardSecurityDecision(BaseModel):
    action: Literal["respond", "request_freeze"] = Field(
        description=(
            "Use request_freeze only when the customer is asking "
            "to freeze a specific card."
        )
    )

    response: str = Field(
        description="Response to send to the customer."
    )

    card_last_four: str | None = Field(
        default=None,
        description=(
            "Last four digits of the card to freeze. "
            "Required when action is request_freeze."
        ),
    )
    
card_security_agent_executor = create_agent(
    model="gpt-4.1-mini",
    tools=[
        get_customer_cards,
        get_recent_card_transactions,
    ],
    context_schema=BankingContext,
    response_format=CardSecurityDecision,
    system_prompt=(
        "You are a banking card security assistant. "
        "Help authenticated customers with lost, stolen, compromised, "
        "or suspicious cards. "

        "Use get_customer_cards when you need to identify the "
        "customer's cards. "
        "Use get_recent_card_transactions when investigating "
        "unrecognized or suspicious card transactions. "

        "If the customer explicitly asks to freeze a specific card, "
        "return action='request_freeze' and provide that card's "
        "last four digits. "

        "Do not claim that the card has already been frozen. "
        "Freezing requires explicit customer confirmation. "

        "If it is unclear which card should be frozen, ask the customer "
        "which card and return action='respond'. "

        "Never invent card or transaction information."
    ),
)


def card_security_agent(
    state: BankingState,
    runtime,
) -> dict:

    result = card_security_agent_executor.invoke(
        {
            "messages": state["messages"],
        },
        context=runtime.context,
    )

    decision: CardSecurityDecision = result[
        "structured_response"
    ]

    if decision.action == "request_freeze":
        return {
            "messages": [
                AIMessage(content=decision.response)
            ],
            "pending_card_last_four": decision.card_last_four,
        }

    return {
        "messages": [
            AIMessage(content=decision.response)
        ],
        "pending_card_last_four": None,
    }
    
################################################################################

class AccountOpeningDecision(BaseModel):
    action: Literal[
        "ask_account_type",
        "account_selected",
    ]

    response: str = Field(
        description="Message to send to the customer."
    )

    account_type: Literal["everyday", "savings"] | None = Field(
        default=None,
        description=(
            "The account type selected by the customer. "
            "Set when the customer clearly selects an account type."
        ),
    )
    
account_opening_agent_executor = create_agent(
    model="gpt-4.1-mini",
    tools=[],
    context_schema=BankingContext,
    response_format=AccountOpeningDecision,
    system_prompt=(
        "You are a bank account opening assistant. "
        "You help authenticated customers begin opening a new bank account. "

        "The bank currently offers two account types: "
        "'everyday' and 'savings'. "

        "An everyday account is intended for regular spending, payments, "
        "and day-to-day banking. "
        "A savings account is intended for saving money. "

        "If the customer has not clearly selected an account type, briefly "
        "explain the available options and ask them to choose. "
        "Return action='ask_account_type'. "

        "If the customer clearly selects an account type, return "
        "action='account_selected' and set account_type to either "
        "'everyday' or 'savings'. "

        "Do not claim that an account has been opened. "
        "Do not perform eligibility or existing-account checks."
    ),
)

def account_opening_agent(
    state: BankingState,
    runtime,
) -> dict:

    result = account_opening_agent_executor.invoke(
        {"messages": state["messages"]},
        context=runtime.context,
    )

    decision: AccountOpeningDecision = result["structured_response"]

    if decision.action == "account_selected":
        return {
            "messages": [AIMessage(content=decision.response)],
            "account_opening_type": decision.account_type,
        }

    return {
        "messages": [AIMessage(content=decision.response)],
        "account_opening_type": None,
    }
################################################################################

class AccountDetailsCollection(BaseModel):
    response: str = Field(
        description="The response to send to the customer."
    )

    full_name: str | None = None
    date_of_birth: str | None = None
    address: str | None = None
    phone: str | None = None

    details_complete: bool = Field(
        description=(
            "True only when full name, date of birth, "
            "residential address, and phone number have all been provided."
        )
    )
    
account_details_agent_executor = create_agent(
    model="gpt-4.1-mini",
    tools=[],
    context_schema=BankingContext,
    response_format=AccountDetailsCollection,
    system_prompt=(
        "You are collecting personal details for a bank account application. "

        "You must collect exactly these four fields: "
        "full name, date of birth, residential address, and phone number. "

        "Extract any of these details that the customer provides. "
        "Ask for information that is still missing. "

        "Do not ask for identification documents, driver licences, passports, "
        "tax information, employment information, or any other information. "
        "Document verification is handled by a separate workflow after these "
        "four personal details have been collected. "

        "Do not invent or assume missing information. "
        "Set details_complete=true only when all four required fields "
        "have been provided."
    )
)

def account_details_agent(
    state: BankingState,
    runtime,
) -> dict:

    existing_details = (
        "Details already collected:\n"
        f"Full name: {state.get('account_opening_name') or 'missing'}\n"
        f"Date of birth: {state.get('account_opening_date_of_birth') or 'missing'}\n"
        f"Address: {state.get('account_opening_address') or 'missing'}\n"
        f"Phone: {state.get('account_opening_phone') or 'missing'}"
    )

    result = account_details_agent_executor.invoke(
        {
            "messages": [
                SystemMessage(content=existing_details),
                *state["messages"],
            ]
        },
        context=runtime.context,
    )

    details: AccountDetailsCollection = result["structured_response"]

    return {
        "messages": [
            AIMessage(content=details.response)
        ],

        "account_opening_name": (
            details.full_name
            or state.get("account_opening_name")
        ),

        "account_opening_date_of_birth": (
            details.date_of_birth
            or state.get("account_opening_date_of_birth")
        ),

        "account_opening_address": (
            details.address
            or state.get("account_opening_address")
        ),

        "account_opening_phone": (
            details.phone
            or state.get("account_opening_phone")
        ),
    }
    
################################################################################

class ApplicationConfirmationDecision(BaseModel):
    confirmed: bool = Field(
        description=(
            "True if the customer clearly confirms they want to submit "
            "the account application. False if they decline or cancel."
        )
    )

    response: str = Field(
        description="A short response to the customer."
    )
    
account_confirmation_agent_executor = create_agent(
    model="gpt-4.1-mini",
    tools=[],
    context_schema=BankingContext,
    response_format=ApplicationConfirmationDecision,
    system_prompt=(
        "Determine whether the customer confirms submission of their "
        "bank account application. "
        "Set confirmed=true only when they clearly approve submission, "
        "for example 'yes', 'confirm', 'submit it', or similar. "
        "Set confirmed=false when they clearly decline or cancel. "
        "Do not submit or create the account yourself."
    ),
)

def account_confirmation_agent(
    state: BankingState,
    runtime,
) -> dict:

    result = account_confirmation_agent_executor.invoke(
        {"messages": state["messages"]},
        context=runtime.context,
    )

    decision: ApplicationConfirmationDecision = (
        result["structured_response"]
    )

    return {
        "messages": [
            AIMessage(content=decision.response)
        ],
        "account_opening_customer_confirmed": decision.confirmed,
    }