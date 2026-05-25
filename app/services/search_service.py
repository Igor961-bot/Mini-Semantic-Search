from app.models.schemas import SearchResponse, StatsResponse
from app.services.vector_store import VectorStore


class SearchService:
    def __init__(self, vector_store: VectorStore) -> None:
        self.vector_store = vector_store

    def search(self, query: str, limit: int, source: str | None = None) -> SearchResponse:
        results = self.vector_store.search(query=query, limit=limit, source=source)
        return SearchResponse(results=results)

    def get_stats(self) -> StatsResponse:
        stats = self.vector_store.get_stats()
        return StatsResponse(**stats)

    def clear_documents(self) -> None:
        self.vector_store.clear()
