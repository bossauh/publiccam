import dataclasses
import logging
from typing import Optional

from database import mongoclass
from library import utils

logger = logging.getLogger(__name__)


@mongoclass.mongoclass
@dataclasses.dataclass
class Metadata:
    title: Optional[str] = None
    description: Optional[str] = None
    geolocation: Optional[dict] = None
    tags: Optional[list[str]] = dataclasses.field(default_factory=lambda: [])


@mongoclass.mongoclass()
@dataclasses.dataclass
class Camera:
    host: str
    port: int
    output_path: str
    content_type: Optional[str] = None

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}{self.output_path}"

    async def is_valid(self) -> bool:
        """
        Checks if this `Camera` is valid and connectable.
        This can also modify the `content_type` but it won't save unless you
        save it manually yourself.
        """

        valid, content_type = await utils.validate_aiohttp(self.url)
        self.content_type = content_type
        if valid:
            valid = utils.validate_cv2(self.url)

        return valid
