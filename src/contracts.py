"""Shared result contracts. Dates are ISO 8601; PDF pages are 1-based."""
from typing import Any, Literal, NotRequired, TypedDict

Route = Literal["STRUCTURED", "UNSTRUCTURED", "HYBRID", "OUT_OF_SCOPE"]


class Page(TypedDict):
    text: str
    page: int
    source_file: str


class ExtractionResult(TypedDict):
    pages: list[Page]
    errors: list[str]


class DocumentMatch(Page):
    chunk_id: str
    score: float
    published_at: NotRequired[str]
    effective_from: NotRequired[str]
    tag: NotRequired[str]


class RetrievalResult(TypedDict):
    matches: list[DocumentMatch]
    state: Literal["ok", "empty", "no_match", "error"]
    errors: list[str]


class SQLResult(TypedDict):
    found: bool
    rows: list[dict[str, Any]]
    source: str
    error: str | None
    tag: NotRequired[str]


class RouteResult(TypedDict):
    route: Route
    sql_tools: list[str]
    doc_query: str
    reason: str
    method: Literal["llm", "fallback"]


class Evidence(TypedDict):
    sql: list[SQLResult]
    docs: list[DocumentMatch]


class AnswerResult(TypedDict):
    route: Route
    reason: str
    method: Literal["llm", "fallback"]
    sql_tools: list[str]
    evidence: Evidence
    answer: str
    sources: list[dict[str, Any]]
    errors: list[str]
    timings: dict[str, float]
    request_id: str
