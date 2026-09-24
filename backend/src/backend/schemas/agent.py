from pydantic import BaseModel, Field


class AccountAgentResponse(BaseModel):
    answer: str = Field(
        description="Natural-language answer for the customer."
    )
    data_found: bool = Field(
        description="Whether relevant banking data was found."
    )
    

class KnowledgeSource(BaseModel):
    source: str = Field(
        description="Source filename used to support the answer."
    )
    page: int | None = Field(
        default=None,
        description=(
            "Page number of the supporting content when the source "
            "is a PDF. None for non-page-based sources."
        ),
    )
    chunk_index: int = Field(
        description="Index of the supporting chunk."
    )


class KnowledgeAgentResponse(BaseModel):
    answer: str = Field(
        description="Grounded answer to the user's question."
    )
    sources: list[KnowledgeSource] = Field(
        description="Sources that support the answer."
    )