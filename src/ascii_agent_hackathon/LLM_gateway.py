import base64
import hashlib
import json
import os
from io import BytesIO
from pathlib import Path
from typing import Optional, Union

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


def get_cache_key(prompt: str, model: str) -> str:
    """Generate a unique cache key based on prompt and model."""
    content = f"{prompt}:{model}"
    return hashlib.md5(content.encode()).hexdigest()


def get_cache_path(cache_key: str) -> Path:
    """Get the cache file path for a given cache key."""
    cache_dir = Path(".img_cache")
    cache_dir.mkdir(exist_ok=True)
    return cache_dir / f"{cache_key}.png"


def get_cache_metadata_path(cache_key: str) -> Path:
    """Get the metadata file path for a given cache key."""
    cache_dir = Path(".img_cache")
    return cache_dir / f"{cache_key}.json"


def generate_image(
    prompt: str,
    model: str = "gemini-2.5-flash-image-preview",
    save_path: Optional[str] = None,
    use_cache: bool = True,
) -> Optional[Image.Image]:
    """
    Generate an image using LLM Gateway API with caching support.

    Args:
        prompt: The prompt to generate an image from
        model: The model to use for generation
        save_path: Optional path to save the generated image
        use_cache: Whether to use caching (default: True)

    Returns:
        PIL Image object or None if generation failed
    """
    # Generate cache key
    cache_key = get_cache_key(prompt, model)
    cache_path = get_cache_path(cache_key)
    metadata_path = get_cache_metadata_path(cache_key)

    # Check cache if enabled
    if use_cache and cache_path.exists():
        print(f"Using cached image for prompt: '{prompt[:50]}...'")
        image = Image.open(cache_path)

        # Save to specified path if requested
        if save_path:
            image.save(save_path)

        return image

    # Generate new image
    print(f"Generating new image for prompt: '{prompt[:50]}...'")
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

    # Save to cache
    if use_cache:
        cache_path.parent.mkdir(exist_ok=True)
        image.save(cache_path)

        # Save metadata
        metadata = {"prompt": prompt, "model": model, "cache_key": cache_key}
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

    # Save to specified path if requested
    if save_path:
        image.save(save_path)

    return image


def image_to_base64(image: Union[Image.Image, str]) -> str:
    """
    Convert an image to base64 string.

    Args:
        image: Either a PIL Image object or a path to an image file

    Returns:
        Base64 encoded image string with data URI prefix
    """
    if isinstance(image, str):
        # Load from file path
        img = Image.open(image)
    else:
        # Already a PIL Image
        img = image

    # Convert to PNG bytes
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # Encode to base64
    img_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    return f"data:image/png;base64,{img_base64}"


def generate_character_pose(
    input_image: Union[Image.Image, str],
    pose_description: str,
    model: str = "gemini-2.5-flash-image-preview",
    save_path: Optional[str] = None,
    use_cache: bool = True,
) -> Optional[Image.Image]:
    """
    Generate a different pose of the same character from an input image.

    Args:
        input_image: Either a PIL Image object or path to an image file
        pose_description: Description of the desired pose
        model: The model to use for generation
        save_path: Optional path to save the generated image
        use_cache: Whether to use caching (default: True)

    Returns:
        PIL Image object of the character in new pose, or None if generation failed
    """
    # Convert image to base64
    img_base64 = image_to_base64(input_image)

    # Create prompt for pose generation
    prompt = f"""Generate the EXACT same character from this image in a different pose: {pose_description}.
    IMPORTANT:
    - Keep the same character, clothing, colors, and art style
    - Keep the same background
    - Only change the pose as described
    - Maintain consistent lighting and perspective
    - The character should be clearly recognizable as the same one"""

    # Create cache key that includes the image and pose
    if isinstance(input_image, str):
        with open(input_image, "rb") as f:
            img_identifier = hashlib.md5(f.read()).hexdigest()[:8]
    elif isinstance(input_image, Image.Image):
        buffer = BytesIO()
        input_image.save(buffer, format="PNG")
        img_identifier = hashlib.md5(buffer.getvalue()).hexdigest()[:8]
    else:
        img_identifier = "unknown"

    cache_key = get_cache_key(f"{prompt}_{img_identifier}_{pose_description}", model)
    cache_path = get_cache_path(cache_key)
    metadata_path = get_cache_metadata_path(cache_key)

    # Check cache if enabled
    if use_cache and cache_path.exists():
        print(f"Using cached pose: {pose_description[:30]}...")
        image = Image.open(cache_path)

        if save_path:
            image.save(save_path)

        return image

    # Generate new pose
    print(f"Generating pose: {pose_description[:50]}...")

    # Prepare the message with both text and image
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": img_base64}},
            ],
        }
    ]

    response: requests.Response = requests.post(
        "https://api.llmgateway.io/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('LLM_GATEWAY_API_KEY')}",
        },
        json={
            "model": model,
            "messages": messages,
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

    # Save to cache
    if use_cache:
        cache_path.parent.mkdir(exist_ok=True)
        image.save(cache_path)

        # Save metadata
        metadata = {
            "operation": "character_pose",
            "pose_description": pose_description,
            "model": model,
            "cache_key": cache_key,
        }
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

    # Save to specified path if requested
    if save_path:
        image.save(save_path)

    return image
