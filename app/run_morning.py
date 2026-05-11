import logging

import deye
from ai_decision import decide
from deye import set_selling_first
from notify import send
from weather import get_forecast

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    if deye.DRY_RUN:
        logger.info("DRY RUN mode — no inverter changes will be made")

    forecast = get_forecast()
    decision = decide(forecast)

    logger.info("Claude reasoning: %s", decision["reasoning"])
    logger.info(
        "Decision: sell_today=%s  sell_from=%s  sell_until=%s (informational — reset handled by evening job)",
        decision["sell_today"], decision["sell_from"], decision["sell_until"],
    )

    prefix = "[DRY RUN] " if deye.DRY_RUN else ""

    if decision["sell_today"]:
        set_selling_first()
        send(
            f"{prefix}Switched to Selling First mode\n"
            f"Sell window: {decision['sell_from']} - {decision['sell_until']}\n\n"
            f"{decision['reasoning']}"
        )
    else:
        logger.info("Staying in Zero Export mode, no changes made")
        send(
            f"{prefix}Staying in Zero Export mode\n\n"
            f"{decision['reasoning']}"
        )


if __name__ == "__main__":
    main()