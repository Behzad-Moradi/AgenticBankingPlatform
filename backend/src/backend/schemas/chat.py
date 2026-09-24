from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    thread_id: str


class InterruptInfo(BaseModel):
    action: str
    card_id: int | None = None
    last_four: str | None = None
    account_type: str | None = None
    full_name: str | None = None
    date_of_birth: str | None = None
    address: str | None = None
    phone: str | None = None
    licence_number: str | None = None
    message: str


class ChatResponse(BaseModel):
    message: str | None = None
    thread_id: str
    sources: list[dict] = []
    interrupt: InterruptInfo | None = None
    account_opening_stage: str | None = None
    requires_document_upload: bool = False


class DocumentUploadResponse(BaseModel):
    message: str
    thread_id: str
    verified: bool
    account_opening_stage: str
    requires_document_upload: bool


class ChatResumeRequest(BaseModel):
    thread_id: str
    approved: bool
