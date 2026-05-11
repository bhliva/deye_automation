import logging
import os

import deye
from deye import set_zero_export_ct
from notify import send

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)

dry_run = os.getenv("DRY_RUN", "").lower() in ("1", "true")
if dry_run:
    deye.DRY_RUN = True
    logger.info("DRY RUN mode — no inverter changes will be made")

logger.info("Resetting inverter to Zero Export CT mode")
set_zero_export_ct()

prefix = "[DRY RUN] " if dry_run else ""
send(f"{prefix}Reset to Zero Export CT mode")
