import datetime
import os
import random
from async_lru import alru_cache
from fastapi import FastAPI, Query, Request, status, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from pymongo import MongoClient
import uvicorn
from app.auth import get_api_key
from app.routers import v1
# from mangum import Mangum

mongodb_url = os.getenv("MONGODB_URL")

origins = [
    "*",
]

PREFIX = "/api"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1.endpoints.router, prefix=PREFIX)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
start_time = now_hk = datetime.datetime.now(
    datetime.timezone(datetime.timedelta(hours=8)))
start_time = start_time.strftime(DATE_FORMAT)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Get client IP address (handling potential proxies)
    client_ip = request.client.host

    # Log the request details
    logger.info(
        f"Request: IP={client_ip}, Method={request.method}, URL={
            request.url}, Headers={request.headers}"
    )

    # Process the request and get the response
    response = await call_next(request)

    # Log the response details
    logger.info(
        f"Response: IP={client_ip}, Status={response.status_code}"
    )

    return response


@app.get(f"{PREFIX}/health_check")
async def health_check(api_key: str = Security(get_api_key)):
    """
    Endpoint to check the server's uptime.

    Returns:
        dict: A dictionary containing a message indicating the server's uptime and the time it started.
              Returns 500 status code if the connection to MongoDB fails.
    """
    try:
        client = MongoClient(mongodb_url)
        db = client["search"]
        db.command("ping")
        response = "Connected to the MongoDB Database!"
        status_code = status.HTTP_200_OK  # Successful connection
    except Exception as e:
        response = f"Error connecting to MongoDB: {str(e)}"
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    finally:
        if 'client' in locals():  # Only close if the connection was established
            client.close()

    return JSONResponse(content={"message": response, "start_hk_time": start_time},
                        status_code=status_code)


@alru_cache(maxsize=1024, ttl=60*60*12)
async def get_random_number(query):
    return random.randint(0, 255)


@app.get(f"{PREFIX}/get-random")
async def get_random(query: str = Query(..., description="random query")):
    random_number = await get_random_number(query)
    return random_number


# handler = Mangum(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
