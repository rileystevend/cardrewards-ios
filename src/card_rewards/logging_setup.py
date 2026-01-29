import logging
import sys

def setup_logging() -> logging.Logger:
    logger = logging.getLogger("card_rewards")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s"))
    if not logger.handlers:
        logger.addHandler(handler)
    return logger
