import asyncio
import json
import logging
import os

import coloredlogs
import faker

from library.config import config
from models import Camera

logging.getLogger("faker.factory").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)
coloredlogs.install(level="INFO")

logger = logging.getLogger(__name__)


class PublicCam:
    def __init__(self) -> None:

        # Load the configuration
        with open(os.path.join(os.getcwd(), "config.json"), encoding="utf-8") as f:
            self.config = json.load(f)

        self.faker = faker.Faker()
        self.local_statistics = {
            "scanned": 0,
            "valid": 0,
            "invalid": 0,
            "loop_iterations": 0,
            "batches_processed": 0,
        }

    async def start(self) -> None:
        """
        Start generating random URLs and validating if they are IP cameras.
        """

        async def validate(camera: Camera) -> None:

            logger.debug(f"Validating {camera.url}...")
            valid = await camera.is_valid()
            self.local_statistics["scanned"] += 1

            if valid:
                self.local_statistics["valid"] += 1
                logger.info(f"{camera.url} is a valid IP camera.")
                camera.save()
                return

            self.local_statistics["invalid"] += 1

        coroutines = []

        while True:

            host = self.faker.ipv4()

            # Retrieve the possible ports and output paths
            port_range: list[int] = config.value["bruteforcer"]["port_range"]
            ports = [80, 88, *list(range(*port_range))]
            output_paths: list[str] = config.value["bruteforcer"]["output_paths"]
            for path in output_paths.copy():
                if "{index}" in path:
                    for i in range(20):
                        output_paths.append(path.replace("{index}", str(i)))
                    output_paths.remove(path)

            # Create the validate coroutines for every possible port and output path combination
            # Once it has accumulated enough coroutines, it will start running all of them
            # together through the use of asyncio.gather
            for port in ports:
                for output_path in output_paths:
                    coroutines.append(
                        validate(Camera(host=host, port=port, output_path=output_path))
                    )

            if len(coroutines) > config.value["bruteforcer"]["batch-size"]:
                await asyncio.gather(*coroutines)
                coroutines.clear()
                logger.info(
                    f"Scanned: {self.local_statistics['scanned']} | Valid: {self.local_statistics['valid']} | Invalid: {self.local_statistics['invalid']} | Unique Hosts: {self.local_statistics['loop_iterations']}"
                )

                self.local_statistics["batches_processed"] += 1
            self.local_statistics["loop_iterations"] += 1


if __name__ == "__main__":
    asyncio.run(PublicCam().start())
