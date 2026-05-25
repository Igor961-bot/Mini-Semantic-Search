import logging

import httpx

from app.core.config import Settings
from app.sources.base import DataSource, SourceDocument
from app.utils.text import extract_text_from_xml

logger = logging.getLogger(__name__)


class EuropePmcSource(DataSource):
    name = "europe_pmc"
    description = "Europe PMC API with open-access scientific articles."

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def fetch_documents(self, limit: int) -> list[SourceDocument]:
        async with httpx.AsyncClient(
            timeout=self.settings.request_timeout_seconds,
            follow_redirects=True,
            headers={"User-Agent": "ASI-mini-project/1.0"},
        ) as client:
            response = await client.get(
                "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                params={
                    "query": "OPEN_ACCESS:Y",
                    "format": "json",
                    "pageSize": limit,
                    "resultType": "lite",
                },
            )
            response.raise_for_status()
            payload = response.json()

            documents: list[SourceDocument] = []
            for item in payload.get("resultList", {}).get("result", []):
                document = await self._build_document(client, item)
                if document is not None:
                    documents.append(document)

            return documents

    async def _build_document(
        self,
        client: httpx.AsyncClient,
        item: dict,
    ) -> SourceDocument | None:
        pmcid = item.get("pmcid")
        if not pmcid:
            return None

        text = await self._fetch_full_text(client, pmcid)
        if not text:
            logger.warning("Europe PMC document %s has no readable full text", pmcid)
            return None

        return SourceDocument(
            source_name=self.name,
            external_id=pmcid,
            title=item.get("title") or pmcid,
            text=text,
            source_url=f"https://europepmc.org/article/PMC/{pmcid}",
        )

    async def _fetch_full_text(self, client: httpx.AsyncClient, pmcid: str) -> str | None:
        try:
            response = await client.get(
                f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Could not download Europe PMC XML for %s: %s", pmcid, exc)
            return None

        return extract_text_from_xml(response.text)
