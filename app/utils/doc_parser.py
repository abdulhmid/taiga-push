import csv
from pathlib import Path
from typing import Dict, List, Tuple

from PyPDF2 import PdfReader


class DocumentParseError(ValueError):
    pass


def _extract_pdf_text(path: Path) -> str:
    reader = PdfReader(path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def _detect_delimiter(header_line: str) -> str:
    for delimiter in [",", "\t", ";", "|"]:
        if delimiter in header_line:
            return delimiter
    return ","


def _normalize_header(header: str) -> str:
    return header.strip().lower().replace(" ", "_")


def parse_document(path: str, fmt: str) -> List[Dict[str, str]]:
    file_path = Path(path)
    if not file_path.exists():
        raise DocumentParseError(f"Input document not found: {file_path}")

    if fmt == "pdf":
        text = _extract_pdf_text(file_path)
    elif fmt == "txt":
        text = file_path.read_text(encoding="utf-8", errors="ignore")
    else:
        raise DocumentParseError(f"Unsupported document format: {fmt}")

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise DocumentParseError("Document is empty or contains no parseable rows.")

    header_line = lines[0]
    delimiter = _detect_delimiter(header_line)
    headers = [_normalize_header(column) for column in next(csv.reader([header_line], delimiter=delimiter))]

    expected_columns = {"talent", "note", "estimation"}
    if not expected_columns.issubset(set(headers)):
        raise DocumentParseError(
            "Document header must include Talent, Note, and Estimation columns."
        )

    rows: List[Dict[str, str]] = []
    reader = csv.DictReader(lines[1:], fieldnames=headers, delimiter=delimiter)
    for index, raw_row in enumerate(reader, start=2):
        row = {key: (value or "").strip() for key, value in raw_row.items()}
        if not row.get("talent") or not row.get("note") or not row.get("estimation"):
            continue
        rows.append({
            "talent": row.get("talent", ""),
            "note": row.get("note", ""),
            "estimation": row.get("estimation", ""),
            "row_number": index,
        })

    if not rows:
        raise DocumentParseError("No valid task rows were found in the document.")

    return rows
