import logging
import os

import deye
from deye import set_zero_export_ct

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)

if os.getenv("DRY_RUN", "").lower() in ("1", "true"):
    deye.DRY_RUN = True
    logger.info("DRY RUN mode — no inverter changes will be made")

logger.info("Resetting inverter to Zero Export CT mode")
set_zero_export_ct()
