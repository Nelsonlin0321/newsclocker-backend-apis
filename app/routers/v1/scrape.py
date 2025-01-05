import asyncio
import re
from async_lru import alru_cache
from bs4 import BeautifulSoup
import httpx


class Scraper():
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    @alru_cache(maxsize=1024, ttl=60*60*12)
    async def run(self, url):
        try:
            async with httpx.AsyncClient() as client:  # Use httpx.AsyncClient
                page = await client.get(  # Await the get request
                    url,
                    timeout=5,
                    headers=self.headers
                )

                # page.encoding = page.apparent_encoding
                parsed = BeautifulSoup(page.text, "html.parser")

                text = parsed.get_text(" ")
                text = re.sub('[ \t]+', ' ', text)
                text = re.sub('\\s+\n\\s+', '\n', text)
                return text
        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"Error scraping {url}: {str(e)} with error: {error_details}")
            return ""

    async def multi_run(self, urls):
        tasks = [self.run(url) for url in urls]  # Create a list of tasks
        results = await asyncio.gather(*tasks)  # Await all tasks concurrently
        return results
