from __future__ import annotations

import logging
import sys


def setup_logger(name: str = "zabbix_user_manager") -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
    )

    logger.addHandler(handler)
    logger.propagate = False

    return logger
