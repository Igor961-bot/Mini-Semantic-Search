from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status

from app.models.schemas import IngestRequest, IngestResponse, SearchRequest, SearchResponse, StatsResponse
from app.services.ingestion_service import IngestionError, IngestionService, UnknownSourceError
from app.services.search_service import SearchService

router = APIRouter(prefix="/api")


def get_ingestion_service(request: Request) -> IngestionService:
    return request.app.state.ingestion_service


def get_search_service(request: Request) -> SearchService:
    return request.app.state.search_service


@router.get("/health", tags=["system"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/sources", tags=["system"])
def list_sources(
    ingestion_service: IngestionService = Depends(get_ingestion_service),
) -> dict[str, list[dict[str, str]]]:
    return {"sources": ingestion_service.list_sources()}


@router.post("/ingestion/upload", response_model=IngestResponse, tags=["ingestion"])
async def ingest_uploaded_text(
    file: UploadFile = File(...),
    ingestion_service: IngestionService = Depends(get_ingestion_service),
) -> IngestResponse:
    try:
        file_bytes = await file.read()
        return await ingestion_service.ingest_uploaded_text(
            filename=file.filename or "uploaded.txt",
            file_bytes=file_bytes,
        )
    except IngestionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/ingestion/{source_name}", response_model=IngestResponse, tags=["ingestion"])
async def ingest_from_source(
    source_name: str,
    payload: IngestRequest,
    ingestion_service: IngestionService = Depends(get_ingestion_service),
) -> IngestResponse:
    try:
        return await ingestion_service.ingest_from_source(
            source_name=source_name,
            limit=payload.limit,
        )
    except UnknownSourceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except IngestionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/search", response_model=SearchResponse, tags=["search"])
def search(
    payload: SearchRequest,
    search_service: SearchService = Depends(get_search_service),
) -> SearchResponse:
    return search_service.search(
        query=payload.query,
        limit=payload.limit,
        source=payload.source,
    )


@router.get("/stats", response_model=StatsResponse, tags=["search"])
def get_stats(search_service: SearchService = Depends(get_search_service)) -> StatsResponse:
    return search_service.get_stats()


@router.get("/documents", include_in_schema=False)
def legacy_documents() -> dict[str, object]:
    return {"total": 0, "documents": []}


@router.delete("/documents", tags=["search"])
def clear_documents(search_service: SearchService = Depends(get_search_service)) -> dict[str, str]:
    search_service.clear_documents()
    return {"message": "Database cleared successfully."}
