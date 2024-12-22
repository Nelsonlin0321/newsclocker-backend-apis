import os
import json
from async_lru import alru_cache
import httpx


SERPER_API_KEY = os.environ["SERPER_API_KEY"]
URL = "https://google.serper.dev/news"


@alru_cache(maxsize=1024, ttl=60*60*12)
async def search_news(q, gl="us", hl="en", num=10, tbs="qdr:d"):
    payload = json.dumps({
        "q": q,
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
