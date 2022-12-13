import json
import os
import time


class DynamicConfig:
    def __init__(self, path: str = os.path.join(os.getcwd(), "config.json")) -> None:
        self.path = path
        self.cached = {"data": None, "timestamp": time.time()}

    @property
    def value(self) -> dict:

        if self.cached["data"] is None or (time.time() - self.cached["timestamp"] > 10):
            with open(self.path, encoding="utf-8", mode="r") as f:
                self.cached["data"] = json.load(f)

            self.cached["timestamp"] = time.time()

        return self.cached["data"]

    @value.setter
    def value(self, new_value: dict) -> None:
        with open(self.path, encoding="utf-8", mode="w") as f:
            json.dump(new_value, f, indent=2)


config = DynamicConfig()
