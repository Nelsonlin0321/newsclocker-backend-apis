
import cuid
from copy import deepcopy
from datetime import datetime
import json
import os
from pymongo import MongoClient
from app.routers.v1.search_news import search_news
from app.utils import process_keywords
from app.routers.v1.scrape import Scraper
from openai import OpenAI
from app.routers.v1.markdown_to_pdf import generate_pdf
mongodb_url = os.getenv("MONGODB_URL")
mongodb_client = MongoClient(mongodb_url)
db = mongodb_client['default']


deep_seek_api_key = os.getenv("DEEPSEEK_API_KEY")

client = OpenAI(api_key=deep_seek_api_key,
                base_url="https://api.deepseek.com")

date_range_map = {
    "any_time": None,
    "past_hour": "qdr:h",
    "past_24_hours": "qdr:d",
    "past_week": "qdr:w",
    "past_month": "qdr:m",
    "past_year": "qdr:y",
}


async def execute_subscription_task(subscription_id):

    subscription = db['NewsSubscription'].find_one({"_id": subscription_id})
    if subscription:
        return {"status": "error", "detail": f"Subscription {subscription_id} not found"}

    query = process_keywords(
        subscription["keywords"], subscription["newsSources"])

    q = query
    gl = subscription['country']
    hl = subscription['language']
    num = 20
    tbs = date_range_map[subscription['dateRange']]

    search_result = await search_news(q=q, gl=gl, hl=hl, num=num, tbs=tbs)

    scraper = Scraper()

    urls = [new['link']for new in search_result['news']]

    contents = await scraper.multi_run(urls=urls)

    relevant_articles = deepcopy(search_result['news'])
    for article, content in zip(relevant_articles, contents):
        article.pop("imageUrl")
        article['content'] = content

    news_reference = [{"link": news['link']} for news in search_result['news']]

    user_prompt = subscription['newsPrompt']
    new_articles = json.dumps(relevant_articles, indent=4)
    news_reference = json.dumps(news_reference, indent=4)

    prompt = get_prompt(user_prompt, new_articles, news_reference)

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )

    ai_insight = response.choices[0].message.content

    title_prompt = """
    Extract title from this article, the title not more than 8 words.
    Directly return title only without any introducing.
    """

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "assistant", "content": ai_insight},
            {"role": "user", "content": title_prompt},
        ],
        stream=False
    )

    title = response.choices[0].message.content

    # Updated to use timezone-aware UTC now
    createdAt = datetime.datetime.now(datetime.timezone.utc).isoformat()
    newsSubscriptionId = subscription_id
    scrapeContent = contents
    searchResult = search_result
    content = ai_insight
    pdfUrl = await generate_pdf(content, title)

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

    return {"status": "success", "detail": f"The mail f{mail_id} has been generated."}


def get_prompt(user_prompt: str, new_articles: str, news_reference: str):

    return f"""
    ## User Request:
    "{user_prompt}"

    Cite the reference links from {news_reference} only with link without their titles at the end of your response.

    ## Instructions:
    Based on the user's request and the provided news articles, generate a comprehensive and insightful response with title.

    **Specifically, your response should:**

    * **Address the key aspects** of the user's prompt.
    * **Highlight key aspects and important information in different color.**
    * **Synthesize information** from the provided articles, avoiding direct quotes unless necessary for emphasis or context.
    * **Present a neutral and objective perspective**, acknowledging different viewpoints presented in the articles.
    * **Maintain a clear and concise writing style**, suitable for a general audience.
    * **Avoid making subjective statements or drawing unsupported conclusions.**

    ## Relevant News Articles in JSON format:
    {new_articles}
    """.strip()


system_prompt = """
You are a helpful and informative AI assistant designed to provide insightful summaries and analyses of news articles. You receive user requests for information and a set of relevant news articles as context. Your goal is to process this information and generate a comprehensive and objective response that satisfies the user's request.

Here's how you should operate:

- Understand the User Request: Carefully analyze the user's prompt to identify the key information they are seeking. Pay attention to keywords, context, and any specific instructions regarding format or length.
- Process the News Articles: Thoroughly read and analyze the provided news articles. Extract key facts, events, perspectives, and any other relevant information that can help address the user's request.
- Synthesize and Summarize: Combine the information from different articles to create a cohesive and comprehensive response. Avoid simply summarizing each article individually. Instead, synthesize the information to provide a holistic view of the topic.
- Maintain Objectivity: Present information neutrally and objectively, acknowledging different viewpoints presented in the articles without expressing personal opinions or biases.
- Focus on Clarity and Conciseness: Use clear and concise language to make your response easily understandable for a general audience. Avoid jargon or technical terms unless necessary and clearly defined.
- Follow Instructions: Adhere to any specific instructions provided in the prompt, such as desired format (summary, comparison, timeline) or length limitations.
- Cite Sources When Necessary: If directly quoting from an article or presenting a specific fact, provide appropriate attribution to the source.
Remember: Your primary goal is to provide users with accurate, informative, and objective insights based on the provided news articles. Avoid making subjective statements, drawing unsupported conclusions, or presenting information not found within the provided context.
""".strip()
