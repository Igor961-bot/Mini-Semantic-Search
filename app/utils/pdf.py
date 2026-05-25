from io import BytesIO

from pypdf import PdfReader


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(pdf_bytes))
    pages: list[str] = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        cleaned = " ".join(page_text.split())
        if cleaned:
            pages.append(cleaned)

    return "\n\n".join(pages)
