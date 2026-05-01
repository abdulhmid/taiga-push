import csv
import io
import re
from pathlib import Path
from typing import Dict, List

from PyPDF2 import PdfReader
from pdfminer.high_level import extract_text


class DocumentParseError(ValueError):
    pass


def _extract_pdf_text(path: Path) -> str:
    try:
        return extract_text(str(path))
    except Exception:
        reader = PdfReader(path)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)


def _extract_pdf_text_from_bytes(content: bytes) -> str:
    try:
        return extract_text(io.BytesIO(content))
    except Exception:
        reader = PdfReader(io.BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)


def _detect_delimiter(header_line: str) -> str:
    for delimiter in [",", "\t", ";", "|"]:
        if delimiter in header_line:
            return delimiter
    return ","


def _normalize_header(header: str) -> str:
    return header.strip().lower().replace(" ", "_")


def _parse_table_document(lines: List[str]) -> List[Dict[str, str]]:
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


def _parse_kv_blocks(text: str) -> List[Dict[str, str]]:
    expected_columns = {"talent", "note", "estimation"}
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    rows: List[Dict[str, str]] = []

    for block_index, block in enumerate(blocks, start=1):
        row_data: Dict[str, str] = {}
        for line in block.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
            elif "=" in line:
                key, value = line.split("=", 1)
            else:
                continue

            normalized_key = _normalize_header(key)
            row_data[normalized_key] = value.strip()

        if expected_columns.issubset(set(row_data.keys())):
            rows.append({
                "talent": row_data.get("talent", ""),
                "note": row_data.get("note", ""),
                "estimation": row_data.get("estimation", ""),
                "row_number": block_index,
            })

    if not rows:
        raise DocumentParseError(
            "Document must contain tasks with Talent, Note, and Estimation values."
        )

    return rows


def _split_talent_sections(text: str) -> List[tuple[str, str]]:
    pattern = re.compile(r"(?P<talent>[A-Za-z][A-Za-z ]+?)\s*->\s*[0-9\.]+(?:md)?", re.I)
    matches = list(pattern.finditer(text))
    sections: List[tuple[str, str]] = []
    for index, match in enumerate(matches):
        begin = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append((match.group("talent").strip(), text[begin:end].strip()))
    return sections


def _parse_note_est_pairs(text: str) -> List[Dict[str, str]]:
    pattern = re.compile(
        r"Note\s*:?\s*(?P<note>.+?)\s+Est\s*:?\s*(?P<est>[0-9\.]+(?:d|md)?)",
        re.I | re.S,
    )
    rows: List[Dict[str, str]] = []
    for match in pattern.finditer(text):
        note = re.sub(r"\s+", " ", match.group("note")).strip()
        estimation = match.group("est").strip()
        rows.append({
            "talent": "",
            "note": note,
            "estimation": estimation,
            "row_number": 0,
        })
    return rows


def _parse_meeting_notes_document(text: str) -> List[Dict[str, str]]:
    sections = _split_talent_sections(text)
    rows: List[Dict[str, str]] = []
    row_number = 1
    for talent, section_text in sections:
        note_pairs = _parse_note_est_pairs(section_text)
        for pair in note_pairs:
            rows.append({
                "talent": talent,
                "note": pair["note"],
                "estimation": pair["estimation"],
                "row_number": row_number,
            })
            row_number += 1

    if not rows:
        raise DocumentParseError(
            "Document must contain tasks with Talent, Note, and Estimation values."
        )

    return rows


def _is_table_document(lines: List[str]) -> bool:
    header_line = lines[0]
    if any(delimiter in header_line for delimiter in [",", "\t", ";", "|"]):
        return True
    normalized = _normalize_header(header_line)
    return all(column in normalized for column in ["talent", "note", "estimation"])


def _parse_text_document(text: str) -> List[Dict[str, str]]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise DocumentParseError("Document is empty or contains no parseable rows.")

    if _is_table_document(lines):
        return _parse_table_document(lines)

    try:
        return _parse_kv_blocks(text)
    except DocumentParseError:
        return _parse_meeting_notes_document(text)


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

    return _parse_text_document(text)


def parse_document_from_bytes(content: bytes, filename: str) -> List[Dict[str, str]]:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        text = _extract_pdf_text_from_bytes(content)
    elif suffix in {".txt", ".csv"}:
        text = content.decode("utf-8", errors="ignore")
    else:
        raise DocumentParseError(
            f"Unsupported document format: {suffix or 'unknown'}"
        )

    return _parse_text_document(text)
