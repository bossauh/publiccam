import asyncio
from typing import Optional

import aiohttp
import cv2

from .config import config


def validate_cv2(url: str) -> bool:
    """
    Check if OpenCV can connect to the provided URL camera.

    Notes
    -----
    The provided `url` must already contain the output path.

    Parameters
    ----------
    `url` : str
        The camera's output url.

    Returns
    -------
    `bool` :
        Indicates whether OpenCV was able to connect to it successfully.
    """

    try:
        video = cv2.VideoCapture(url, apiPreference=cv2.CAP_FFMPEG)
        if video is None or not video.isOpened():
            return False
        video.read()
    except cv2.error:
        return False

    return True


async def validate_aiohttp(
    url: str, *, timeout: Optional[aiohttp.ClientTimeout] = None
) -> bool:
    """
    Check if aiohttp can connect to the provided URL and if the mimetype matches
    the supported mimetypes.

    Notes
    -----
    The provided `url` must already contain the output path.

    Parameters
    ----------
    `url` : str
        The camera's output url.
    `timeout` : Optional[aiohttp.ClientTimeout]
        The `aiohttp.ClientTimeout` instance to pass onto `aiohttp.ClientSession`.
        Defaults to `aiohttp.ClientTimeout(total=None, sock_connect=5, sock_read=5)`

    Returns
    -------
    `Tuple[bool, Optional[str]]` :
        The first value indicates whether it is valid and the second being
        the content type.
    """

    content_type = None
    try:
        async with aiohttp.ClientSession(
            timeout=timeout
            or aiohttp.ClientTimeout(
                total=None, connect=60, sock_connect=60, sock_read=10
            ),
        ) as ses:
            async with ses.get(url) as res:

                content_type = res.content_type
                if res.content_type not in config.value["bruteforcer"]["content_types"]:
                    return (False, content_type)

    except (
        aiohttp.ClientConnectionError,
        asyncio.TimeoutError,
        aiohttp.TooManyRedirects,
        aiohttp.ClientResponseError,
        aiohttp.InvalidURL,
    ):
        return (False, content_type)

    return (True, content_type)
