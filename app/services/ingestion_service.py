import hashlib
import logging

from app.core.config import Settings
from app.models.schemas import IngestResponse
from app.services.chunking import split_into_chunks
from app.services.vector_store import VectorStore
from app.sources.base import DataSource, SourceDocument

logger = logging.getLogger(__name__)


class IngestionError(Exception):
    """raised when a document cannot be ingested."""


class UnknownSourceError(IngestionError):
    """raised when the source name is not registered."""


class IngestionService:
    def __init__(
        self,
        vector_store: VectorStore,
        sources: dict[str, DataSource],
        settings: Settings,
    ) -> None:
        self.vector_store = vector_store
        self.sources = sources
        self.settings = settings

    def list_sources(self) -> list[dict[str, str]]:
        sources = [
            {"name": source.name, "description": source.description}
            for source in self.sources.values()
        ]
        sources.append({"name": "upload", "description": "Uploaded TXT files."})
        return sources

    async def ingest_from_source(self, source_name: str, limit: int) -> IngestResponse:
        source = self.sources.get(source_name)
        if source is None:
            raise UnknownSourceError(f"Unknown source: {source_name}")

        logger.info("Starting ingestion from source=%s limit=%s", source_name, limit)
        documents = await source.fetch_documents(limit=limit)

        imported_documents = 0
        imported_chunks = 0
        skipped_documents = 0

        for document in documents:
            chunk_count = self._store_document(document)
            if chunk_count == 0:
                skipped_documents += 1
                continue

            imported_documents += 1
            imported_chunks += chunk_count

        message = (
            f"Imported {imported_documents} document(s) and {imported_chunks} chunk(s) "
            f"from source '{source_name}'."
        )
        logger.info(message)

        return IngestResponse(
            source=source_name,
            imported_documents=imported_documents,
            imported_chunks=imported_chunks,
            skipped_documents=skipped_documents,
            message=message,
        )

    async def ingest_uploaded_text(self, filename: str, file_bytes: bytes) -> IngestResponse:
        if not filename.lower().endswith(".txt"):
            raise IngestionError("Only TXT files are supported.")
        if not file_bytes:
            raise IngestionError("Uploaded file is empty.")
        if len(file_bytes) > self.settings.max_pdf_bytes:
            raise IngestionError(
                f"Uploaded file is too large. Maximum size is {self.settings.max_pdf_bytes // 1_000_000} MB."
            )

        text = file_bytes.decode("utf-8-sig", errors="ignore").strip()
        if len(text.strip()) < 50:
            raise IngestionError("The uploaded TXT did not contain enough readable text.")

        document = SourceDocument(
            source_name="upload",
            external_id=hashlib.sha1(file_bytes).hexdigest()[:16],
            title=filename,
            text=text,
            source_url=None,
        )

        imported_chunks = self._store_document(document)
        if imported_chunks == 0:
            raise IngestionError("The uploaded TXT could not be split into valid chunks.")

        return IngestResponse(
            source="upload",
            imported_documents=1,
            imported_chunks=imported_chunks,
            skipped_documents=0,
            message=f"Imported 1 uploaded TXT file and {imported_chunks} chunk(s).",
        )

    def _store_document(self, document: SourceDocument) -> int:
        chunks = split_into_chunks(
            text=document.text,
            chunk_size_words=self.settings.chunk_size_words,
            chunk_overlap_words=self.settings.chunk_overlap_words,
        )
        if not chunks:
            logger.warning("Skipping empty document %s", document.document_id)
            return 0

        return self.vector_store.upsert_document_chunks(document=document, chunks=chunks)
