from pydantic import BaseModel
from typing import List, Optional


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
    gl: Optional[str] = None
    hl: Optional[str] = None
    type: Optional[str] = None
    num: Optional[int] = None
    tbs: Optional[str] = None
    engine: Optional[str] = None


class SearchResponse(BaseModel):
    searchParameters: SearchParameters
    news: List[NewsItem]
    credits: int


class DeliverToMail(BaseModel):
    subscriptionId: str
    aiInsight: str
    pdfUrl: str
    searchResult: SearchResponse
