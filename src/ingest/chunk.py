"""Page-bounded chunks with exact character overlap and stable provenance IDs."""
from hashlib import sha256
import re


def chunk_pages(pages, size=500, overlap=80):
    if size < 30 or not 0 <= overlap < size:
        raise ValueError("Chunk size must be >=30 with 0 <= overlap < size.")
    chunks = []
    indices = {}
    for page in pages:
        text = page["text"].strip()
        identity_key = (page['source_file'], page['page'])
        index = indices.get(identity_key, 0)
        start = 0
        while start < len(text):
            end = min(start + size, len(text))
            if end < len(text):
                window = text[start:end]
                paragraphs = [m.end() for m in re.finditer(r"\n\s*\n", window)]
                sentences = [m.end() for m in re.finditer(r"[.!?]\s+", window)]
                lower = max(size // 2, overlap + 1)
                usable = [n for n in paragraphs if n >= lower] or [n for n in sentences if n >= lower]
                if usable:
                    end = start + usable[-1]
            content = text[start:end]
            if len(content.strip()) >= 30:
                identity = f"{page['source_file']}:{page['page']}:{index}"
                metadata = {k: page[k] for k in ("source_file", "page", "published_at", "effective_from") if k in page}
                chunks.append({**metadata, "text": content, "chunk_id": sha256(identity.encode()).hexdigest(),
                               "doc_type": page["source_file"].rsplit(".", 1)[-1].lower()})
                index += 1
            if end == len(text):
                break
            start = end - overlap
        indices[identity_key] = index
    return chunks
