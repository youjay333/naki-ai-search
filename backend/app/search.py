from __future__ import annotations

from typing import Any

from langchain_tavily import TavilySearch

from app.config import Settings
from app.models import SearchResult


def _to_result(index: int, item: dict[str, Any]) -> SearchResult:
    return SearchResult(
        id=index,
        title=item.get("title") or "Untitled result",
        url=item.get("url") or "",
        content=item.get("content") or "",
        raw_content=item.get("raw_content"),
        score=item.get("score"),
    )


def normalize_tavily_payload(payload: Any) -> list[SearchResult]:
    if isinstance(payload, dict):
        items = payload.get("results", [])
    elif isinstance(payload, list):
        items = payload
    else:
        items = []

    return [_to_result(index, item) for index, item in enumerate(items, start=1) if isinstance(item, dict)]


async def search_web(query: str, settings: Settings, max_results: int | None = None) -> list[SearchResult]:
    if not settings.tavily_api_key:
        raise RuntimeError("Missing TAVILY_API_KEY. Add it to backend/.env or the process environment.")

    tool = TavilySearch(
        tavily_api_key=settings.tavily_api_key,
        max_results=max_results or settings.tavily_max_results,
        topic="general",
        search_depth=settings.tavily_search_depth,
        include_answer=False,
        include_raw_content=settings.tavily_include_raw_content,
        include_images=False,
    )

    payload = await tool.ainvoke({"query": query})
    return normalize_tavily_payload(payload)
