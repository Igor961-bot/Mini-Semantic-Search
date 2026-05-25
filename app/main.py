from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router
from app.core.config import BASE_DIR, Settings, get_settings
from app.core.logging_config import setup_logging
from app.services.ingestion_service import IngestionService
from app.services.search_service import SearchService
from app.services.vector_store import VectorStore
from app.sources.europepmc_source import EuropePmcSource
from app.sources.openalex_source import OpenAlexSource


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    setup_logging(resolved_settings)

    vector_store = VectorStore(settings=resolved_settings)
    sources = {
        OpenAlexSource.name: OpenAlexSource(resolved_settings),
        EuropePmcSource.name: EuropePmcSource(resolved_settings),
    }

    ingestion_service = IngestionService(
        vector_store=vector_store,
        sources=sources,
        settings=resolved_settings,
    )
    search_service = SearchService(vector_store=vector_store)

    app = FastAPI(
        title=resolved_settings.project_name,
        version="0.1.0",
        description=(
            "Semantic search over scientific documents from open APIs "
            "and uploaded text files."
        ),
    )

    app.state.settings = resolved_settings
    app.state.ingestion_service = ingestion_service
    app.state.search_service = search_service

    app.include_router(api_router)

    static_dir = Path(BASE_DIR) / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index() -> FileResponse:
        return FileResponse(static_dir / "index.html")

    return app


app = create_app()
