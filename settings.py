import os
from enum import Enum
from dotenv import load_dotenv

load_dotenv()


class StorageType(Enum):
    JSON = "json"
    SQLITE = "sqlite"


class Settings:
    storage: StorageType = StorageType(os.getenv("STORAGE", "json"))

    @classmethod
    def get_cmc_api_key(cls) -> str:
        key = os.getenv("CMC_API_KEY", "")
        if not key:
            raise ValueError("CMC_API_KEY is not set in .env file")
        return key