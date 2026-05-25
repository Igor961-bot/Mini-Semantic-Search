import hashlib
import re
import xml.etree.ElementTree as ET


def make_document_id(source_name: str, external_id: str) -> str:
    digest = hashlib.sha1(external_id.encode("utf-8")).hexdigest()[:16]
    return f"{source_name}-{digest}"


def reconstruct_abstract(inverted_index: dict[str, list[int]]) -> str:
    if not inverted_index:
        return ""

    max_position = max((max(positions) for positions in inverted_index.values() if positions), default=-1)
    if max_position < 0:
        return ""

    ordered_words = [""] * (max_position + 1)
    for word, positions in inverted_index.items():
        for position in positions:
            ordered_words[position] = word

    return " ".join(word for word in ordered_words if word).strip()


def extract_text_from_xml(xml_text: str) -> str:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return ""

    fragments: list[str] = []
    relevant_tags = {
        "article-title",
        "title",
        "abstract",
        "p",
        "sec",
        "label",
    }

    for element in root.iter():
        tag_name = element.tag.split("}")[-1]
        if tag_name not in relevant_tags:
            continue

        text = " ".join(" ".join(element.itertext()).split())
        if text and text not in fragments:
            fragments.append(text)

    combined = "\n\n".join(fragments)
    combined = re.sub(r"\n{3,}", "\n\n", combined)
    return combined.strip()
