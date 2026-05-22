import pytest

from app.ai import build_context, sanitize_citations
from app.models import SearchResult
from app.search import normalize_tavily_payload
from app.sse import sse_event


def test_normalize_tavily_payload_numbers_results():
    payload = {
        "results": [
            {"title": "Alpha", "url": "https://example.com/a", "content": "A", "score": 0.9},
            {"title": "Beta", "url": "https://example.com/b", "content": "B", "score": 0.8},
        ]
    }

    results = normalize_tavily_payload(payload)

    assert [item.id for item in results] == [1, 2]
    assert results[0].title == "Alpha"


def test_build_context_contains_citation_ids():
    results = [
        SearchResult(id=1, title="Doc", url="https://example.com", content="Useful content"),
    ]

    context = build_context(results)

    assert "[1] Doc" in context
    assert "Useful content" in context


def test_sse_event_encodes_json():
    event = sse_event("token", {"text": "你好"})

    assert event.startswith("event: token\n")
    assert 'data: {"text": "你好"}' in event
    assert event.endswith("\n\n")


def test_sanitize_citations_removes_invalid_ids():
    results = [
        SearchResult(id=1, title="Doc", url="https://example.com/1", content="One"),
        SearchResult(id=2, title="Doc 2", url="https://example.com/2", content="Two"),
    ]

    answer = "有效事实 [1]，无效事实 [0] 和 [9]，组合 [1][2]。"

    sanitized = sanitize_citations(answer, results)

    assert "[1]" in sanitized
    assert "[2]" in sanitized
    assert "[0]" not in sanitized
    assert "[9]" not in sanitized


@pytest.mark.asyncio
async def test_health_endpoint():
    from httpx import ASGITransport, AsyncClient
    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
