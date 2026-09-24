from langchain.messages import HumanMessage, AIMessage
from fastapi import File, HTTPException, UploadFile, APIRouter, Depends
from backend.agents.context import BankingContext
from backend.agents.graph import graph
from backend.api.dependencies import get_current_customer
from backend.services.document_extraction import extract_driver_licence
from backend.models.customer import Customer
from backend.schemas.chat import ChatRequest, ChatResponse, ChatResumeRequest, InterruptInfo
from langgraph.types import Command
from backend.agents.workflows.account_opening import verify_driver_licence_details
from backend.services.document_extraction import extract_driver_licence
from backend.agents.state import BankingState

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_customer: Customer = Depends(get_current_customer),
) -> ChatResponse:
    
    scoped_thread_id = (f"{current_customer.id}:{request.thread_id}")
    
    config = {
        "configurable": {
            "thread_id": scoped_thread_id,
        }
    }

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(content=request.message)
            ],
            "sources": [],
        },
        config=config,
        context=BankingContext(
            customer_id=current_customer.id
        ),
    )
    interrupts = result.get("__interrupt__", [])
    
    if interrupts:
        interrupt_value = interrupts[0].value

        return ChatResponse(
            message=None,
            thread_id=request.thread_id,
            sources=result.get("sources", []),
            interrupt=InterruptInfo(
                **interrupt_value
            ),
        )

    return ChatResponse(
        message=result["messages"][-1].content,
        thread_id=request.thread_id,
        sources=result.get("sources", []),
        interrupt=None,
    )
    
@router.post(
    "/resume",
    response_model=ChatResponse,
)
def resume_chat(
    request: ChatResumeRequest,
    current_customer: Customer = Depends(
        get_current_customer
    ),
) -> ChatResponse:

    scoped_thread_id = (
        f"{current_customer.id}:{request.thread_id}"
    )

    config = {
        "configurable": {
            "thread_id": scoped_thread_id,
        }
    }

    result = graph.invoke(
        Command(resume=request.approved),
        config=config,
        context=BankingContext(
            customer_id=current_customer.id
        ),
    )

    return ChatResponse(
        message=result["messages"][-1].content,
        thread_id=request.thread_id,
        sources=result.get("sources", []),
        interrupt=None,
    )
    
@router.post("/account-opening/document")
async def upload_account_opening_document(
    thread_id: str,
    file: UploadFile = File(...),
    current_customer: Customer = Depends(get_current_customer),
):
    allowed_content_types = {
        "image/jpeg",
        "image/png",
        "application/pdf",
    }

    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG, and PDF files are supported.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    # Get the customer's existing account-opening checkpoint.
    scoped_thread_id = f"{current_customer.id}:{thread_id}"

    config = {
        "configurable": {
            "thread_id": scoped_thread_id,
        }
    }

    snapshot = graph.get_state(config)
    state = snapshot.values

    # Make sure an application is actually waiting for a licence.
    if (
        not state.get("account_opening_active")
        or state.get("account_opening_stage") != "document_upload"
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "No account application is currently "
                "waiting for a document."
            ),
        )

    # Extract information from the licence.
    details = extract_driver_licence(
        content=content,
        content_type=file.content_type,
    )
    
    
    print("\n--- APPLICATION DETAILS ---")
    print("Name:", state["account_opening_name"])
    print("DOB:", state["account_opening_date_of_birth"])
    print("Address:", state["account_opening_address"])

    print("\n--- LICENCE DETAILS ---")
    print("Name:", details.full_name)
    print("DOB:", details.date_of_birth)
    print("Address:", details.address)
    print("Licence number:", details.licence_number)

    # Compare licence information with information provided by customer.
    verified = verify_driver_licence_details(
        application_name=state["account_opening_name"],
        application_date_of_birth=state[
            "account_opening_date_of_birth"
        ],
        application_address=state["account_opening_address"],
        licence_name=details.full_name,
        licence_date_of_birth=details.date_of_birth,
        licence_address=details.address,
    )

    # Store extraction + verification result in LangGraph state.
    graph.update_state(
        config,
        {
            "account_opening_licence_name": details.full_name,
            "account_opening_licence_date_of_birth": (
                details.date_of_birth
            ),
            "account_opening_licence_address": details.address,
            "account_opening_licence_number": (
                details.licence_number
            ),
            "account_opening_document_verified": verified,
            "account_opening_stage": (
                "customer_confirmation"
                if verified
                else "document_upload"
            ),
        },
    )

    if not verified:
        return {
            "message": (
                "The driver licence details could not be verified "
                "against the information provided in your application. "
                "Please check your details or upload another licence."
            ),
            "thread_id": thread_id,
            "verified": False,
        }

    return {
        "message": (
            "Your driver licence details have been "
            "successfully verified."
        ),
        "thread_id": thread_id,
        "verified": True,
    }
    