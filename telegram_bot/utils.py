import asyncio
import os

import dotenv
import requests

dotenv.load_dotenv()

DOCKER_URL = os.getenv("DOCKER_URL")
API_KEY = os.getenv("API_KEY")


async def simple_post_request(data: dict) -> None:
    telegram_id = data["telegram_id"]
    await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + f"users/{telegram_id}",
        json=data,
        headers={"X-Api-Key": API_KEY},
    )


async def simple_get_request(telegram_id: int) -> None:
    response = await asyncio.to_thread(
        requests.get,
        url=DOCKER_URL + f"users/{telegram_id}",
        params={"api_key": API_KEY},
    )
    return response.json()
