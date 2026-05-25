from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    limit: int = Field(default=20, ge=1, le=50)


class IngestResponse(BaseModel):
    source: str
    imported_documents: int
    imported_chunks: int
    skipped_documents: int
    message: str


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=200)
    limit: int = Field(default=5, ge=1, le=10)
    source: str | None = None


class SearchResult(BaseModel):
    title: str
    source: str
    snippet: str
    similarity: float | None = None
    source_url: str | None = None


class SearchResponse(BaseModel):
    results: list[SearchResult]


class StatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    sources: dict[str, int]
