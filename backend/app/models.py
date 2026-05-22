from pydantic import BaseModel, Field, HttpUrl


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)
    max_results: int | None = Field(default=None, ge=3, le=20)


class SearchResult(BaseModel):
    id: int
    title: str
    url: HttpUrl | str
    content: str = ""
    raw_content: str | None = None
    score: float | None = None


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
