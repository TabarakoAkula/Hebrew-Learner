from django.conf import settings
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def chat(prompt: str) -> str:
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Ты помощник для изучения иврита. "
                    "Отвечай на русском языке, если пользователь не просит иначе."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content or ""
