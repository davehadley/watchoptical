import logging
import os


def getlog(name) -> logging.Logger:
    _configlog()
    return logging.getLogger(name)


def _configlog():
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
