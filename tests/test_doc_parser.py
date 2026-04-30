from app.utils.doc_parser import parse_document, DocumentParseError


def test_parse_text_document(tmp_path):
    content = "Talent,Note,Estimation\nAlice,Fix login bug,3\nBob,Review specs,2"
    file_path = tmp_path / "tasks.txt"
    file_path.write_text(content, encoding="utf-8")

    rows = parse_document(str(file_path), "txt")
    assert len(rows) == 2
    assert rows[0]["talent"] == "Alice"
    assert rows[1]["estimation"] == "2"


def test_parse_document_missing_columns(tmp_path):
    content = "Owner,Task,Hours\nAlice,Fix login bug,3"
    file_path = tmp_path / "bad.txt"
    file_path.write_text(content, encoding="utf-8")

    try:
        parse_document(str(file_path), "txt")
        assert False, "Expected DocumentParseError"
    except DocumentParseError as exc:
        assert "Talent, Note, and Estimation" in str(exc)
