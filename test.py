import asyncio
import logging

import aiohttp
import coloredlogs
import cv2

coloredlogs.install(level="DEBUG")

TEST_URLS = [
    "http://122.150.121.190:8888/out.jpg",
    "http://212.251.197.23:8081/video.mjpg",
    "http://73.102.200.134:8080/cam_1.cgi",
    "http://90.226.117.29:8080/video",
    "http://80.32.125.254:8080/cgi-bin/faststream.jpg",
    "http://202.245.13.81:80/cgi-bin/camera",
    "http://94.124.210.59:8083/mjpg/video.mjpg",
]


async def main() -> None:
    async def make_request(url: str) -> None:

        logging.info(f"Making request to: {url}")

        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=None, sock_connect=5, sock_read=5)
            ) as ses:
                async with ses.get(url) as res:
                    logging.debug(f"Content-Type: {res.content_type}")

                    video = cv2.VideoCapture(url, apiPreference=cv2.CAP_FFMPEG)
                    if video is None or not video.isOpened():
                        logging.error(f"{url} cannot be opened using OpenCV.")

        except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
            logging.error(f"Failed to connect to {url}.")

    tasks = []
    for url in TEST_URLS:
        tasks.append(make_request(url))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
