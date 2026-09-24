from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    thread_id: str


class InterruptInfo(BaseModel):
    action: str
    card_id: int | None = None
    last_four: str | None = None
    message: str


class ChatResponse(BaseModel):
    message: str | None = None
    thread_id: str
    sources: list[dict] = []
    interrupt: InterruptInfo | None = None


class ChatResumeRequest(BaseModel):
    thread_id: str
    approved: bool