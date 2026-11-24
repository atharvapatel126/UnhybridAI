"""Semantic search with explicit empty/no-match/error states and cosine scores."""
from config import settings
import math
from src.ingest.embed_store import embed_texts
from src.ingest.vector_store import DocumentStore


def retrieve(query, k=None, threshold=None, *, store=None):
    result = {"matches": [], "state": "no_match", "errors": []}
    if not isinstance(query, str) or not query.strip():
        return result
    k = settings.top_k if k is None else k
    threshold = settings.sim_threshold if threshold is None else threshold
    if (not isinstance(k, int) or not 1 <= k <= 50
            or not isinstance(threshold, (int, float))
            or not math.isfinite(threshold) or not -1 <= threshold <= 1):
        return {**result, "state": "error", "errors": ["Invalid retrieval limit or threshold."]}
    try:
        store = store or DocumentStore()
        if not store.list_documents():
            return {**result, "state": "empty"}
        response = store.search(embed_texts([query])[0], k)
        for text, metadata, distance in zip(response["documents"][0], response["metadatas"][0], response["distances"][0]):
            score = min(1., max(-1., 1. - distance))
            if score >= threshold:
                result["matches"].append({**metadata, "text": text, "score": score, "distance": distance})
        result["matches"].sort(key=lambda item: item["score"], reverse=True)
        result["state"] = "ok" if result["matches"] else "no_match"
    except Exception:
        result.update(state="error", errors=["Document retrieval unavailable. Check the model cache and vector store."])
    return result
