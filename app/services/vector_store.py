import chromadb
from chromadb.utils import embedding_functions

from app.core.config import Settings
from app.models.schemas import SearchResult
from app.services.chunking import TextChunk, make_snippet
from app.sources.base import SourceDocument


class VectorStore:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.settings.chroma_path.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.settings.chroma_path))
        self.collection = self._open_collection()

    def _open_collection(self):
        # chroma handles embeddings for stored text and search queries
        return self.client.get_or_create_collection(
            name=self.settings.collection_name,
            metadata={"hnsw:space": "cosine"},
            embedding_function=embedding_functions.DefaultEmbeddingFunction(),
        )

    def upsert_document_chunks(self, document: SourceDocument, chunks: list[TextChunk]) -> int:
        # keep only the data used later by search and stats
        ids = [f"{document.document_id}:chunk:{chunk.index}" for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = [
            {
                "document_id": document.document_id,
                "source_name": document.source_name,
                "title": document.title,
                "source_url": document.source_url or "",
            }
            for chunk in chunks
        ]

        self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        return len(ids)

    def search(self, query: str, limit: int, source: str | None = None) -> list[SearchResult]:
        # source filtering is optional in the ui
        where = {"source_name": source} if source else None
        result = self.collection.query(
            query_texts=[query],
            n_results=min(limit, self.settings.max_search_results),
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        search_results: list[SearchResult] = []
        for chunk_text, metadata, distance in zip(documents, metadatas, distances):
            search_results.append(
                SearchResult(
                    title=metadata["title"],
                    source=metadata["source_name"],
                    snippet=make_snippet(chunk_text),
                    similarity=round(max(0.0, 1.0 - float(distance)), 4),
                    source_url=metadata.get("source_url") or None,
                )
            )

        return search_results

    def _get_all_metadatas(self) -> list[dict[str, str]]:
        # stats are based only on metadata already stored in chroma
        data = self.collection.get(include=["metadatas"])
        return [metadata for metadata in data.get("metadatas", []) if metadata is not None]

    def get_stats(self) -> dict:
        metadatas = self._get_all_metadatas()
        source_documents: dict[str, set[str]] = {}
        for metadata in metadatas:
            source_name = metadata["source_name"]
            source_documents.setdefault(source_name, set()).add(metadata["document_id"])

        document_ids = {metadata["document_id"] for metadata in metadatas}
        return {
            "total_documents": len(document_ids),
            "total_chunks": self.collection.count(),
            "sources": {
                source_name: len(document_ids_for_source)
                for source_name, document_ids_for_source in source_documents.items()
            },
        }

    def clear(self) -> None:
        try:
            self.client.delete_collection(self.settings.collection_name)
        except Exception:
            pass
        self.collection = self._open_collection()
