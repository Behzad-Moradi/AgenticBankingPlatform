from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from backend.agents.router import classify_intent
from backend.agents.state import BankingState
from backend.agents.context import BankingContext
from backend.agents.workflows.card_security import (
    card_not_found,
    confirm_card_freeze,
    execute_card_freeze,
    reject_card_freeze,
    resolve_card_for_freeze,
    route_card_security_action,
    route_freeze_confirmation,
    route_resolved_card,
)

from backend.agents.specialists import (
    account_agent,
    account_confirmation_agent,
    account_details_agent,
    account_opening_agent,
    card_security_agent,
    chat_agent,
    knowledge_agent,
)

from backend.agents.workflows.account_opening import (
    account_already_exists,
    check_existing_account,
    route_existing_account,
    route_account_type_selection,
    route_personal_details,
    personal_details_complete,
    show_application_summary,
    cancel_account_application,
    prepare_for_staff_approval,
    route_customer_confirmation,
    confirm_account_application_by_staff,
    reject_account_application,
    route_staff_approval,
    create_approved_account,
)

builder = StateGraph(
    BankingState,
    context_schema=BankingContext,
)

def route_intent(state: BankingState) -> str:
    intent = state.get("intent")
    if intent is None:
        raise ValueError("Intent has not been classified.")
    return intent

def route_entry(state: BankingState) -> str:
    if not state.get("account_opening_active"):
        return "new_request"

    stage = state.get("account_opening_stage")

    if stage == "personal_details":
        return "account_details"

    if stage == "customer_confirmation":
        return "show_application_summary"
    
    if stage == "customer_confirmation_response":
        return "customer_confirmation_response"
    
    if stage == "staff_approval":
        return "staff_approval"

    return "new_request"

builder.add_node("router", classify_intent)
builder.add_node("chat_agent", chat_agent)
builder.add_node("account_agent", account_agent)
builder.add_node("knowledge_agent", knowledge_agent)
builder.add_node("card_security_agent", card_security_agent)
builder.add_node("confirm_card_freeze", confirm_card_freeze)
builder.add_node("resolve_card_for_freeze", resolve_card_for_freeze)
builder.add_node("card_not_found", card_not_found)
builder.add_node("reject_card_freeze", reject_card_freeze)
builder.add_node("execute_card_freeze", execute_card_freeze)
builder.add_node("account_opening_agent", account_opening_agent)
builder.add_node("check_existing_account", check_existing_account)
builder.add_node("account_already_exists", account_already_exists)
builder.add_node("account_details_agent", account_details_agent)
builder.add_node("personal_details_complete", personal_details_complete)
builder.add_node("show_application_summary", show_application_summary)
builder.add_node("account_confirmation_agent", account_confirmation_agent)
builder.add_node("cancel_account_application", cancel_account_application)
builder.add_node("prepare_for_staff_approval", prepare_for_staff_approval)
builder.add_node("confirm_account_application_by_staff", confirm_account_application_by_staff)
builder.add_node("reject_account_application", reject_account_application)
builder.add_node("create_approved_account", create_approved_account)



builder.add_conditional_edges(START, route_entry, {"new_request": "router", "account_details": "account_details_agent", "show_application_summary": "show_application_summary", "customer_confirmation_response": "account_confirmation_agent", "staff_approval": "confirm_account_application_by_staff"})
builder.add_conditional_edges("router", route_intent, {"chat": "chat_agent", "knowledge": "knowledge_agent", "account": "account_agent", "card_security": "card_security_agent", "account_opening": "account_opening_agent"})
builder.add_edge("chat_agent", END)
builder.add_edge("knowledge_agent", END)
builder.add_edge("account_agent", END)
builder.add_conditional_edges("card_security_agent", route_card_security_action, {"freeze_requested": "resolve_card_for_freeze", "done": END})
builder.add_conditional_edges("resolve_card_for_freeze", route_resolved_card, {"resolved": "confirm_card_freeze", "not_found": "card_not_found"})
builder.add_edge("card_not_found", END)
builder.add_conditional_edges("confirm_card_freeze", route_freeze_confirmation, {"approved": "execute_card_freeze", "rejected": "reject_card_freeze"})
builder.add_edge("execute_card_freeze", END)
builder.add_edge("reject_card_freeze", END)
builder.add_conditional_edges("account_opening_agent", route_account_type_selection, {"selected": "check_existing_account", "not_selected": END,})
builder.add_conditional_edges("check_existing_account", route_existing_account, {"already_exists": "account_already_exists", "continue": "account_details_agent"})
builder.add_edge("account_already_exists", END)
builder.add_conditional_edges("account_details_agent", route_personal_details, {"incomplete": END, "complete": "personal_details_complete"})
builder.add_edge("personal_details_complete", END)
builder.add_edge("show_application_summary", END)
builder.add_conditional_edges("account_confirmation_agent", route_customer_confirmation, {"confirmed": "prepare_for_staff_approval", "cancelled": "cancel_account_application"})
builder.add_edge("prepare_for_staff_approval", END)
builder.add_edge("cancel_account_application", END)
builder.add_conditional_edges("confirm_account_application_by_staff", route_staff_approval, {"approved": "create_approved_account", "rejected": "reject_account_application"})
builder.add_edge("reject_account_application", END)
builder.add_edge("create_approved_account", END)


checkpointer = InMemorySaver()

graph = builder.compile(checkpointer=checkpointer)

graph.get_graph().draw_mermaid_png(output_file_path='graph.png')
