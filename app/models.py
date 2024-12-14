from pydantic import BaseModel
from typing import List


class NewsItem(BaseModel):
    title: str
    link: str
    snippet: str
    date: str
    source: str
    imageUrl: str
    position: int


class SearchParameters(BaseModel):
    q: str
    gl: str
    hl: str
    type: str
    tbs: str
    engine: str


class SearchResponse(BaseModel):
    searchParameters: SearchParameters
    news: List[NewsItem]
    credits: int
