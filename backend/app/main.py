from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.ai import generate_related_questions, sanitize_citations, stream_answer
from app.config import Settings, get_settings
from app.models import SearchRequest, SearchResponse
from app.search import search_web
from app.sse import sse_event

app = FastAPI(title="naki-ai-search API", version="0.1.0")

_settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/search", response_model=SearchResponse)
async def search(request: SearchRequest, settings: Settings = Depends(get_settings)) -> SearchResponse:
    try:
        results = await search_web(request.query, settings, request.max_results)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return SearchResponse(query=request.query, results=results)


@app.post("/api/search/stream")
async def search_stream(
    request: SearchRequest,
    settings: Settings = Depends(get_settings),
) -> StreamingResponse:
    async def event_generator() -> AsyncIterator[str]:
        answer_parts: list[str] = []
        try:
            yield sse_event("status", {"message": "正在联网搜索"})
            results = await search_web(request.query, settings, request.max_results)
            yield sse_event("results", {"query": request.query, "results": [item.model_dump(mode="json") for item in results]})

            yield sse_event("status", {"message": "正在综合分析"})
            async for token in stream_answer(request.query, results, settings):
                answer_parts.append(token)
                yield sse_event("token", {"text": token})

            answer = sanitize_citations("".join(answer_parts), results)
            yield sse_event("status", {"message": "正在生成相关问题"})
            related = await generate_related_questions(request.query, results, answer, settings)
            yield sse_event("related", {"questions": related})
            yield sse_event("done", {"answer": answer})
        except Exception as exc:
            yield sse_event("error", {"message": str(exc)})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
