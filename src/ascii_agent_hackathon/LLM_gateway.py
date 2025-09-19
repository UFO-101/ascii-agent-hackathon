import base64
import os
from io import BytesIO
from typing import Optional

import requests
from PIL import Image


def send_message(message: str, model: str = "gpt-5-nano") -> str:
    response: requests.Response = requests.post(
        "https://api.llmgateway.io/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('LLM_GATEWAY_API_KEY')}",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": message}],
        },
    )

    response.raise_for_status()
    reply: str = response.json()["choices"][0]["message"]["content"]
    return reply


def generate_image(prompt: str, model: str = "gemini-2.5-flash-image-preview", save_path: Optional[str] = None) -> Optional[Image.Image]:
    response: requests.Response = requests.post(
        "https://api.llmgateway.io/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('LLM_GATEWAY_API_KEY')}",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        },
    )

    response.raise_for_status()
    result: dict = response.json()

    images: list = result["choices"][0]["message"].get("images", [])

    if not images:
        return None

    base64_str: str = images[0]["image_url"]["url"].split("base64,")[1]
    image_data: bytes = base64.b64decode(base64_str)

    image: Image.Image = Image.open(BytesIO(image_data))

    if save_path:
        image.save(save_path)

    return image
