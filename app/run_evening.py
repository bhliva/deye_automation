import logging

import deye
from deye import set_zero_export_ct
from notify import send

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    if deye.DRY_RUN:
        logger.info("DRY RUN mode — no inverter changes will be made")

    logger.info("Resetting inverter to Zero Export CT mode")
    set_zero_export_ct()

    prefix = "[DRY RUN] " if deye.DRY_RUN else ""
    send(f"{prefix}Reset to Zero Export CT mode")


if __name__ == "__main__":
    main()