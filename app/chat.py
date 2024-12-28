from typing import Dict, List
from openai import OpenAI


async def get_chat_response(client: OpenAI, messages: List[Dict]):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=False
    )
    return response.choices[0].message.content
