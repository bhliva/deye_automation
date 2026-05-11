import logging
import os
import httpx
from config import DEYE_APP_ID, DEYE_APP_SECRET, DEYE_EMAIL, DEYE_PASSWORD, DEYE_DEVICE_SN, DEYE_HOST

logger = logging.getLogger(__name__)

WORK_MODE_SELLING_FIRST = 0
WORK_MODE_ZERO_EXPORT_CT = 2

_MODE_NAMES = {
    WORK_MODE_SELLING_FIRST: "SELLING_FIRST",
    WORK_MODE_ZERO_EXPORT_CT: "ZERO_EXPORT_CT",
}

DRY_RUN = os.getenv("DRY_RUN", "").lower() in ("1", "true")


def get_token() -> str:
    url = f"{DEYE_HOST}/v1.0/account/token?appId={DEYE_APP_ID}"
    response = httpx.post(url, json={
        "appSecret": DEYE_APP_SECRET,
        "email": DEYE_EMAIL,
        "password": DEYE_PASSWORD,
    }, timeout=15)
    response.raise_for_status()
    data = response.json()
    return data["data"]["accessToken"]


def set_mode(mode: int) -> None:
    mode_name = _MODE_NAMES.get(mode, str(mode))
    if DRY_RUN:
        logger.info("[DRY RUN] Would set inverter to %s (WORK_MODE=%s)", mode_name, mode)
        return
    token = get_token()
    url = f"{DEYE_HOST}/v1.0/order/sys/power/update"
    response = httpx.post(
        url,
        json={
            "deviceSn": DEYE_DEVICE_SN,
            "powerType": "WORK_MODE",
            "value": mode,
        },
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    response.raise_for_status()
    logger.info("Inverter mode set to %s", mode_name)


def set_selling_first() -> None:
    set_mode(WORK_MODE_SELLING_FIRST)


def set_zero_export_ct() -> None:
    set_mode(WORK_MODE_ZERO_EXPORT_CT)
