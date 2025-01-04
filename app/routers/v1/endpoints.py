import traceback
from typing import List
from fastapi import APIRouter, Depends, Query, Security, status
from app.auth import get_api_key
from app.dependencies import get_db, get_openai_client
from app.models import DeliverToMail, SearchResponse
from fastapi.responses import JSONResponse
from app.routers.v1.deliver_to_the_mail import deliver_to_the_mail
from app.routers.v1.markdown_to_pdf import generate_pdf
from app.routers.v1.scrape import Scraper
from app.routers.v1.search_news import search_news
from app.routers.v1.task import execute_subscription_task
from loguru import logger
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


@router.post("/scrape", response_model=List[str])
async def scrape_content(urls: List[str], api_key: str = Security(get_api_key)):
    content = await scraper.multi_run(urls=urls)
    return content


@router.get("/get-pdf-url", response_model=str)
async def get_pdf_url(markdown: str, title: str, api_key: str = Security(get_api_key)):
    url = await generate_pdf(markdown, title)
    return url


@router.get("/execute-task")
async def execute(subscription_id: str, db=Depends(get_db), openai_client=Depends(get_openai_client), api_key: str = Security(get_api_key)):
    try:
        status_with_message = await execute_subscription_task(subscription_id, db=db, openai_client=openai_client)
        if status_with_message['status'] == 'error':
            return JSONResponse(content={"message": status_with_message['detail']},
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return JSONResponse(content={"message": status_with_message['detail']},
                                status_code=status.HTTP_200_OK)

    except Exception as e:
        error_details = traceback.format_exc()  # Get the traceback details
        return JSONResponse(content={"message": str(e), "trace": error_details},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/deliver-mail")
async def deliver_mail(payload: DeliverToMail, db=Depends(get_db), openai_client=Depends(get_openai_client), api_key: str = Security(get_api_key)):
    try:
        result = await deliver_to_the_mail(subscription_id=payload.subscriptionId,
                                           search_result=payload.searchResult,
                                           ai_insight=payload.aiInsight,
                                           pdfUrl=payload.pdfUrl,
                                           db=db, openai_client=openai_client)
        return result
    except Exception as e:
        error_details = traceback.format_exc()  # Get the traceback details
        logger.error(f"{e}: {error_details}")
        return JSONResponse(content={"detail": str(e), "trace": error_details, "status": "error"},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
