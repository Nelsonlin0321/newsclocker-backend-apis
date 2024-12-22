from typing import List
from fastapi import APIRouter, Query, Security
from app.auth import get_api_key
from app.models import SearchResponse
from fastapi.responses import JSONResponse
from app.routers.v1.markdown_to_pdf import generate_pdf
from app.routers.v1.scrape import Scraper
from app.routers.v1.search_news import search_news

ROUTE_NAME = "v1"

router = APIRouter(
    prefix=f"/{ROUTE_NAME}",
    tags=[ROUTE_NAME],
)


@router.get("/news-search", response_model=SearchResponse)
async def search(
    q: str = Query(..., description="Search query"),
    gl: str = Query("us", description="Geographical location"),
    hl: str = Query("en", description="Language"),
    num: int = Query(10, description="Number of results"),
    tbs: str = Query("qdr:d", description="Time-based search"),
    api_key: str = Security(get_api_key)
):
    result = await search_news(q, gl, hl, num, tbs)
    return JSONResponse(content=result)


scraper = Scraper()


@router.post("/scrape/", response_model=List[str])
async def scrape_content(urls: List[str], api_key: str = Security(get_api_key)):
    content = await scraper.multi_run(urls=urls)
    return content


@router.post("/get_pdf_url/", response_model=str)
async def get_pdf_url(markdown: str, keywords: str, api_key: str = Security(get_api_key)):
    url = await generate_pdf(markdown, keywords)
    return url
