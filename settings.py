import os
from enum import Enum
from dotenv import load_dotenv

load_dotenv()


class StorageType(Enum):
    JSON = "json"
    SQLITE = "sqlite"


class Settings:
    storage: StorageType = StorageType(os.getenv("STORAGE", "json"))