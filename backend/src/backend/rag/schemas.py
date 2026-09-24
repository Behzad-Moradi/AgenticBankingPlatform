from pydantic import BaseModel


class KnowledgeSource(BaseModel):
    source: str
    page: int | None = None
    