import asyncio

from app.main import create_app


async def main() -> None:
    app = create_app()
    ingestion_service = app.state.ingestion_service

    result_one = await ingestion_service.ingest_from_source(
        source_name="openalex",
        limit=20,
    )
    result_two = await ingestion_service.ingest_from_source(
        source_name="europe_pmc",
        limit=20,
    )

    print(result_one.message)
    print(result_two.message)


if __name__ == "__main__":
    asyncio.run(main())
