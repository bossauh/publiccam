from mongoclass import MongoClassClient

from library.config import config

mongoclass = MongoClassClient(**config.value["database"])
if mongoclass._engine_used == "pymongo":
    mongoclass.server_info()
