import datetime
import cuid
from openai import OpenAI
from pymongo.database import Database
from app.chat import get_chat_response
from app.models import SearchResponse
from app.routers.v1.scrape import Scraper


async def deliver_to_the_mail(subscription_id: str, search_result: SearchResponse, ai_insight: str,
                              pdfUrl: str, db: Database, openai_client: OpenAI):

    search_result = search_result.model_dump()

    scraper = Scraper()

    urls = [new['link']for new in search_result['news']]
    contents = await scraper.multi_run(urls=urls)

    title_prompt = """
        Extract title from this article, the title not more than 8 words.
        Directly return title only without any introducing.
        """

    messages = [
        {"role": "assistant", "content": ai_insight},
        {"role": "user", "content": title_prompt},
    ]

    title = await get_chat_response(openai_client, messages)
    createdAt = datetime.datetime.now(datetime.timezone.utc)
    newsSubscriptionId = subscription_id
    scrapeContent = contents
    searchResult = search_result
    content = ai_insight

    payload_to_insert = {
        "_id": cuid.cuid(),
        "createdAt": createdAt,
        "newsSubscriptionId": newsSubscriptionId,
        "scrapeContent": scrapeContent,
        "searchResult": searchResult,
        "content": content,
        "title": title,
        "pdfUrl": pdfUrl,
        "isRead": False,
        "isStarred": False,
        "isTrashed": False,
    }

    mail = db['Mail'].insert_one(payload_to_insert)
    mail_id = mail.inserted_id

    return {"status": "success", "detail": f"The mail f{mail_id} has been delivered.", "mailId": mail_id}
