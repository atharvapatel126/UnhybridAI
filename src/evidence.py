"""Shared evidence labels, source metadata, and transparent raw-evidence fallback."""
import json


def label_evidence(evidence):
    for kind, prefix in (("sql", "SQL"), ("docs", "DOC")):
        for index, item in enumerate(evidence[kind], 1):
            item["tag"] = f"[{prefix}-{index}]"
    return evidence


def sources(evidence):
    output = [{"tag": row["tag"], "source": row["source"]} for row in evidence["sql"]]
    output += [{key: item[key] for key in ("tag", "source_file", "page", "chunk_id", "score", "published_at", "effective_from") if key in item}
               for item in evidence["docs"]]
    return output


def raw_answer(evidence, notice="Showing retrieved evidence; generated interpretation is unavailable."):
    parts = [notice]
    for item in evidence["sql"]:
        parts.append(f"{item['tag']} {item['source']}: {json.dumps(item['rows'], ensure_ascii=True)}")
    for item in evidence["docs"]:
        parts.append(f"{item['tag']} {item['source_file']} page {item['page']}: {item['text']}")
    if not evidence["sql"] and not evidence["docs"]:
        parts.append("No supporting evidence is available. Missing information cannot be inferred.")
    return "\n\n".join(parts)
