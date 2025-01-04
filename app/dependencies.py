import os
from openai import OpenAI

from pymongo import MongoClient
mongodb_url = os.getenv("MONGODB_URL")
deep_seek_api_key = os.getenv("DEEPSEEK_API_KEY")


def get_db():
    mongodb_client = MongoClient(mongodb_url)
    db = mongodb_client['newsclocker']
    return db


def get_openai_client():
    client = OpenAI(api_key=deep_seek_api_key,
                    base_url="https://api.deepseek.com")
    return client
