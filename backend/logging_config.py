import logging
import sys
import uuid
from contextvars import ContextVar

# 修复：确保 site-packages 在 sys.path 中
import site
site.main()

# Context variable to store request ID
request_id_var = ContextVar("request_id", default=None)


class RequestIdFormatter(logging.Formatter):
    def format(self, record):
        record.request_id = request_id_var.get()
        return super().format(record)


def setup_logging():
    """
    Set up structured logging.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Use a handler that outputs to stdout
    handler = logging.StreamHandler(sys.stdout)

    # Use our custom formatter
    formatter = RequestIdFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(request_id)s - %(message)s"
    )

    handler.setFormatter(formatter)

    # Clear existing handlers and add the new one
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(handler)
