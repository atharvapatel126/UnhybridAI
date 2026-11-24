from pathlib import Path

import pymupdf
import pytest
from scripts.create_demo_docs import create_documents
from src.ingest.chunk import chunk_pages
from src.ingest.extract import extract_document, validate_filename


def test_demo_documents_and_provenance(tmp_path):
    names = create_documents(tmp_path)
    assert len(names) == 4
    for name in names:
        result = extract_document(tmp_path / name)
        assert not result["errors"]
        assert all("SYNTHETIC" in p["text"] and p["source_file"] == name for p in result["pages"])
    result = extract_document(tmp_path / "Academic_Regulations.pdf")
    assert "75 percent" in result["pages"][3]["text"]
    assert result["pages"][3]["page"] == 4


@pytest.mark.parametrize("filename,content", [("empty.txt", b""), ("broken.pdf", b"bad pdf"),
    ("wrong.csv", b"a,b"), ("bad.txt", b"\xff\xfe"), ("image.pdf", b"GIF89a")])
def test_invalid_extraction(tmp_path, filename, content):
    path = tmp_path / filename
    path.write_bytes(content)
    result = extract_document(path)
    assert result["errors"] and not result["pages"]


def test_empty_scanned_encrypted_and_oversized(tmp_path):
    for name, encrypted in [("empty.pdf", False), ("encrypted.pdf", True)]:
        with pymupdf.open() as doc:
            page = doc.new_page()
            if encrypted:
                page.insert_text((50, 50), "private content")
            doc.save(tmp_path / name, encryption=pymupdf.PDF_ENCRYPT_AES_256 if encrypted else 0,
                     owner_pw="owner", user_pw="password")
        assert extract_document(tmp_path / name)["errors"]
    with pymupdf.open() as doc:
        page = doc.new_page()
        image = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 10, 10))
        image.clear_with(255)
        page.insert_image(page.rect, pixmap=image)
        doc.save(tmp_path / "scanned.pdf")
    assert "No extractable text" in extract_document(tmp_path / "scanned.pdf")["errors"][0]
    large = tmp_path / "large.txt"
    with large.open("wb") as file:
        file.truncate(20 * 1024 * 1024 + 1)
    assert "20 MB" in extract_document(large)["errors"][0]


@pytest.mark.parametrize("name", ["../policy.txt", "..\\policy.pdf", ".hidden.pdf", "a.exe", "a:bad.txt", ""])
def test_unsafe_upload_names(name):
    assert not validate_filename(name)


def test_text_markdown_and_blank_pdf_pages(tmp_path):
    path = tmp_path / "rules.md"
    path.write_text("Synthetic policy " * 10, encoding="utf-8")
    assert extract_document(path)["pages"][0]["page"] == 1
    with pymupdf.open() as doc:
        doc.new_page()
        page = doc.new_page()
        page.insert_text((50, 50), "SYNTHETIC - DEMO ONLY valid second page")
        doc.save(tmp_path / "blank.pdf")
    assert extract_document(tmp_path / "blank.pdf")["pages"][0]["page"] == 2


def test_chunk_overlap_ids_metadata_and_bounds():
    pages = [{"text": "".join(chr(0x4e00 + i) for i in range(1234)), "source_file": "a.txt", "page": 1}]
    chunks = chunk_pages(pages)
    assert len(chunks) > 1 and chunks == chunk_pages(pages)
    assert chunks[0]["text"][-80:] == chunks[1]["text"][:80]
    assert chunks[0]["text"] + "".join(c["text"][80:] for c in chunks[1:]) == pages[0]["text"]
    assert all(30 <= len(c["text"].strip()) <= 500 and c["doc_type"] == "txt" for c in chunks)
    assert len({c["chunk_id"] for c in chunks}) == len(chunks)
    assert chunk_pages([]) == []
    assert chunk_pages([dict(pages[0], text="short")]) == []
    with pytest.raises(ValueError):
        chunk_pages(pages, overlap=500)


def test_paragraph_boundary_and_repeated_page_indices():
    text = "Policy sentence. " * 20 + "\n\n" + "Another paragraph. " * 20
    pages = [{"text": text, "source_file": "a.txt", "page": 1},
             {"text": "Dated notice. " * 10, "source_file": "a.txt", "page": 1, "published_at": "2026-11-15"},
             {"text": "Second page. " * 10, "source_file": "a.txt", "page": 2}]
    chunks = chunk_pages(pages)
    assert len({c["chunk_id"] for c in chunks}) == len(chunks)
    assert chunks[-1]["page"] == 2 and chunks[-2]["published_at"] == "2026-11-15"
    assert chunks[0]["text"].endswith("\n\n")
