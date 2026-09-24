from typing import Literal, TypedDict

from langgraph.graph import MessagesState


Intent = Literal["chat", "account", "knowledge", "card_security",]


class SourceInfo(TypedDict):
    source: str
    page: int | None
    chunk_index: int


class BankingState(MessagesState):
    intent: Intent | None
    sources: list[SourceInfo]
    pending_card_id: int | None
    pending_card_last_four: str | None
    freeze_approved: bool | None
    
    account_opening_type: str | None
    account_opening_name: str | None
    account_opening_date_of_birth: str | None
    account_opening_address: str | None
    account_opening_phone: str | None

    account_opening_document_verified: bool | None
    account_opening_customer_confirmed: bool | None
    account_opening_staff_approved: bool | None
    account_opening_existing_account: bool | None
    account_opening_active: bool | None
    account_opening_stage: str | None
    
    account_opening_licence_name: str | None
    account_opening_licence_date_of_birth: str | None
    account_opening_licence_address: str | None
    account_opening_licence_number: str | None
    
    account_opening_document_verified: bool | None