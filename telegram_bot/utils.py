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
        headers={"x-api-key": API_KEY},
    )


async def get_or_create_user(telegram_id: int, data: dict) -> None:
    response = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + f"users/{telegram_id}",
        headers={"x-api-key": API_KEY},
        params=data,
    )
    return response.json()


async def get_or_add_word(data: dict) -> None:
    response = await asyncio.to_thread(
        requests.get,
        url=DOCKER_URL + "storage/words",
        headers={"x-api-key": API_KEY},
        params=data,
    )
    return response.json()
