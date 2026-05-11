import os
from dotenv import load_dotenv

load_dotenv()


def _require(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise RuntimeError(f"Missing required env var: {key}")
    return val


DEYE_APP_ID = _require("DEYE_APP_ID")
DEYE_APP_SECRET = _require("DEYE_APP_SECRET")
DEYE_EMAIL = _require("DEYE_EMAIL")
DEYE_PASSWORD = _require("DEYE_PASSWORD")
DEYE_DEVICE_SN = _require("DEYE_DEVICE_SN")
DEYE_HOST = os.getenv("DEYE_HOST", "https://eu1-developer.deyecloud.com")

LATITUDE = float(_require("LATITUDE"))
LONGITUDE = float(_require("LONGITUDE"))

ANTHROPIC_API_KEY = _require("ANTHROPIC_API_KEY")
