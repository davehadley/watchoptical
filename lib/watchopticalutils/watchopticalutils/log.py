import inspect
import logging
import os


def getlog() -> logging.Logger:
    _configlog()
    caller_module_name = inspect.getmodule(inspect.stack()[1]).__name__
    return logging.getLogger(caller_module_name)


def _configlog():
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
