import logging

import httpx

from app.core.config import Settings
from app.sources.base import DataSource, SourceDocument
from app.utils.pdf import extract_text_from_pdf_bytes
from app.utils.text import reconstruct_abstract

logger = logging.getLogger(__name__)


class OpenAlexSource(DataSource):
    name = "openalex"
    description = "OpenAlex API with academic papers, metadata and open-access PDFs."

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def fetch_documents(self, limit: int) -> list[SourceDocument]:
        async with httpx.AsyncClient(
            timeout=self.settings.request_timeout_seconds,
            follow_redirects=True,
            headers={"User-Agent": "ASI-mini-project/1.0"},
        ) as client:
            response = await client.get(
                "https://api.openalex.org/works",
                params={
                    "filter": "has_abstract:true,is_oa:true",
                    "per-page": limit,
                    "sort": "cited_by_count:desc",
                },
            )
            response.raise_for_status()
            payload = response.json()

            documents: list[SourceDocument] = []
            for item in payload.get("results", []):
                document = await self._build_document(client, item)
                if document is not None:
                    documents.append(document)

            return documents

    async def _build_document(
        self,
        client: httpx.AsyncClient,
        item: dict,
    ) -> SourceDocument | None:
        title = item.get("display_name") or item.get("title") or "Untitled work"
        external_id = item.get("id") or title

        location = item.get("best_oa_location") or item.get("primary_location") or {}
        pdf_url = location.get("pdf_url")
        source_url = location.get("landing_page_url") or item.get("doi") or item.get("id")

        text: str | None = None

        if pdf_url:
            text = await self._download_pdf_text(client, pdf_url)

        if not text:
            abstract = reconstruct_abstract(item.get("abstract_inverted_index") or {})
            if abstract:
                text = f"{title}\n\n{abstract}"

        if not text:
            logger.warning("OpenAlex work %s does not have PDF text or abstract", external_id)
            return None

        return SourceDocument(
            source_name=self.name,
            external_id=external_id,
            title=title,
            text=text,
            source_url=source_url or pdf_url,
        )

    async def _download_pdf_text(self, client: httpx.AsyncClient, pdf_url: str) -> str | None:
        try:
            response = await client.get(pdf_url)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Could not download OpenAlex PDF %s: %s", pdf_url, exc)
            return None

        content_type = response.headers.get("content-type", "")
        if "pdf" not in content_type.lower() and not pdf_url.lower().endswith(".pdf"):
            return None
        if len(response.content) > self.settings.max_pdf_bytes:
            logger.warning("Skipping large PDF %s", pdf_url)
            return None

        text = extract_text_from_pdf_bytes(response.content)
        return text if len(text.strip()) >= 50 else None
