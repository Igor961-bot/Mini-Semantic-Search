from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.utils.text import make_document_id


@dataclass(slots=True)
class SourceDocument:
    source_name: str
    external_id: str
    title: str
    text: str
    source_url: str | None = None
    document_id: str = field(init=False)

    def __post_init__(self) -> None:
        self.document_id = make_document_id(
            source_name=self.source_name,
            external_id=self.external_id,
        )


class DataSource(ABC):
    name: str
    description: str

    @abstractmethod
    async def fetch_documents(self, limit: int) -> list[SourceDocument]:
        raise NotImplementedError
