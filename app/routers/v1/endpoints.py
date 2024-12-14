import os
import httpx
import json
from fastapi import APIRouter, Query
from app.models import SearchResponse
from fastapi.responses import JSONResponse

ROUTE_NAME = "v1"

router = APIRouter(
    prefix=f"/{ROUTE_NAME}",
    tags=[ROUTE_NAME],
)

URL = "https://google.serper.dev/news"

SERPER_API_KEY = os.environ["SERPER_API_KEY"]


async def search_news(query, gl="us", hl="en", num=10, tbs="qdr:d"):

    payload = json.dumps({
        "q": query,
        "gl": gl,
        "hl": hl,
        "num": num,
        "tbs": tbs
    })
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(URL, headers=headers, data=payload)

    return response.json()


@router.get("/news-search", response_model=SearchResponse)
async def search(
    query: str = Query(..., description="Search query"),
    gl: str = Query("us", description="Geographical location"),
    hl: str = Query("en", description="Language"),
    num: int = Query(10, description="Number of results"),
    tbs: str = Query("qdr:d", description="Time-based search")
):
    result = await search_news(query, gl, hl, num, tbs)
    return JSONResponse(content=result)
