from __future__ import annotations

import json
import re
from collections.abc import AsyncIterator

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import Settings
from app.models import SearchResult


ANSWER_SYSTEM_PROMPT = """你是 naki-ai-search 的 AI 搜索分析助手。
你会收到用户问题和一组已经联网搜索得到的网页资料。

要求：
1. 只基于给定搜索资料回答；资料不足时明确说明不确定。
2. 用中文给出结构清晰、信息密度高的回答。
3. 每个关键事实后使用来源编号标注，例如 [1] 或 [2][4]。
4. 不要编造来源编号，不要引用没有给出的资料。
5. 可以综合多个来源，但必须让用户能追溯信息。
"""


RELATED_SYSTEM_PROMPT = """你是搜索引擎的相关问题生成器。
基于用户问题、搜索结果和最终回答，生成 3 到 5 个中文相关问题。
只输出 JSON 数组字符串，例如 ["问题1","问题2","问题3"]。
不要输出 Markdown，不要输出解释。
"""


def build_context(results: list[SearchResult], per_source_limit: int = 1800) -> str:
    chunks: list[str] = []
    for item in results:
        source_text = item.raw_content or item.content or ""
        source_text = " ".join(source_text.split())
        if len(source_text) > per_source_limit:
            source_text = source_text[:per_source_limit] + "..."
        chunks.append(
            f"[{item.id}] {item.title}\nURL: {item.url}\n摘要/正文: {source_text}"
        )
    return "\n\n".join(chunks)


def sanitize_citations(answer: str, results: list[SearchResult]) -> str:
    valid_ids = {item.id for item in results}

    def replace(match: re.Match[str]) -> str:
        citation_id = int(match.group(1))
        return match.group(0) if citation_id in valid_ids else ""

    sanitized = re.sub(r"\[(\d+)\]", replace, answer)
    sanitized = re.sub(r" {2,}", " ", sanitized)
    sanitized = re.sub(r" +([。！？；，、])", r"\1", sanitized)
    return sanitized.strip()


def get_llm(settings: Settings, streaming: bool) -> ChatOpenAI:
    if not settings.deepseek_api_key:
        raise RuntimeError("Missing DEEPSEEK_API_KEY. Add it to backend/.env or the process environment.")

    return ChatOpenAI(
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        model=settings.deepseek_model,
        temperature=settings.deepseek_temperature,
        max_completion_tokens=settings.deepseek_max_tokens,
        timeout=settings.request_timeout_seconds,
        streaming=streaming,
        reasoning_effort=settings.deepseek_reasoning_effort,
        extra_body={
            "thinking": {
                "type": settings.deepseek_thinking,
            }
        },
    )


def build_answer_messages(query: str, results: list[SearchResult]) -> list[SystemMessage | HumanMessage]:
    context = build_context(results)
    user_prompt = f"""用户问题：
{query}

搜索资料：
{context}

请生成带来源编号引用的综合回答。"""
    return [SystemMessage(content=ANSWER_SYSTEM_PROMPT), HumanMessage(content=user_prompt)]


async def stream_answer(query: str, results: list[SearchResult], settings: Settings) -> AsyncIterator[str]:
    llm = get_llm(settings, streaming=True)
    async for chunk in llm.astream(build_answer_messages(query, results)):
        token = chunk.content
        if isinstance(token, str) and token:
            yield token


async def generate_related_questions(
    query: str,
    results: list[SearchResult],
    answer: str,
    settings: Settings,
) -> list[str]:
    llm = get_llm(settings, streaming=False)
    context = build_context(results, per_source_limit=500)
    prompt = f"""用户问题：{query}

AI 回答：
{answer}

搜索资料：
{context}

请生成 3 到 5 个适合继续搜索的相关问题。"""
    response = await llm.ainvoke([SystemMessage(content=RELATED_SYSTEM_PROMPT), HumanMessage(content=prompt)])
    content = response.content if isinstance(response.content, str) else json.dumps(response.content, ensure_ascii=False)

    try:
        parsed = json.loads(content)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()][:5]
    except json.JSONDecodeError:
        pass

    lines = [line.strip(" -0123456789.、") for line in content.splitlines()]
    return [line for line in lines if line][:5]
