import logging
import os

import deye
from ai_decision import decide
from deye import set_selling_first
from weather import get_forecast

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)

if os.getenv("DRY_RUN", "").lower() in ("1", "true"):
    deye.DRY_RUN = True
    logger.info("DRY RUN mode — no inverter changes will be made")

forecast = get_forecast()
decision = decide(forecast)

logger.info("Claude reasoning: %s", decision["reasoning"])
logger.info(
    "Decision: sell_today=%s  sell_from=%s  sell_until=%s (informational — reset handled by evening job)",
    decision["sell_today"], decision["sell_from"], decision["sell_until"],
)

if decision["sell_today"]:
    set_selling_first()
else:
    logger.info("Staying in Zero Export mode, no changes made")
