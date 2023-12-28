import logging
import importlib
import os
import sys
import threading
from logging import config as log_config
from .helpers import GCPLogger
from aiohttp_boilerplate.config import get_config

def skipHealtcheck(record) -> bool:
    return record.getMessage().find("/healtcheck") == -1

def get_logger(
        name:str,
        level:str = None,
        format:str = None,
        stack_info:bool = None,
        stacklevel:int = None,
        extra_labels:map = {},
    ):

    if None in (level, format, stack_info, stacklevel):
        cfg = get_config('log')

        if level is None:
            level = cfg['level'].upper()
        if format is None:
            format = cfg['format']
        if stacklevel is None:
            stacklevel = cfg['stacklevel']
        if stack_info is None:
            stack_info = cfg['stackinfo']

    logging.root.setLevel(level)

    logger = GCPLogger(name, format=format, stack_info=stack_info, stacklevel=stacklevel, extra_labels=extra_labels)
    logger.setLevel(level)

    return logger

def _resolve(name):
    """Resolve a dotted name to a global object."""
    name = name.split('.')
    used = name.pop(0)
    found = importlib.import_module(used)
    for n in name:
        used = used + '.' + n
        try:
            found = getattr(found, n)
        except AttributeError:
            found = importlib.import_module(used)
    return found
log_config._resolve = _resolve


def except_logging(exc_type, exc_value, exc_traceback):
    """
    Log uncaught exceptions using the root logger. This is a function meant to
    be set as `sys.excepthook` to provide unified logging for regular logs and
    uncaught exceptions.
    """
    logging.error("Uncaught exception",
                  exc_info=(exc_type, exc_value, exc_traceback))
sys.excepthook = except_logging

def unraisable_logging(args):
    """
    Log unraisable exceptions using the root logger. This is a function meant
    to be set as `sys.unraisablehook` to provide unified logging for regular
    logs and unraisable exceptions.
    """
    exc_type, exc_value, exc_traceback, err_msg, _ = args
    default_msg = "Unraisable exception"

    logging.error(err_msg or default_msg,
                  exc_info=(exc_type, exc_value, exc_traceback))

sys.unraisablehook = unraisable_logging


def threading_except_logging(args):
    """
    Log uncaught exceptions from different threads using the root logger. This
    is a function meant to be set as `threading.excepthook` to provide unified
    logging for regular logs and uncaught exceptions from different threads.
    """
    exc_type, exc_value, exc_traceback, _ = args
    logging.error("Uncaught threading exception",
                  exc_info=(exc_type, exc_value, exc_traceback))

threading.excepthook = threading_except_logging
