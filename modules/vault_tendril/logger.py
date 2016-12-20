"""All details about logging are in here"""

import logging

LOG_LEVEL_MAP = {
    'debug':logging.DEBUG,
    'info':logging.INFO,
    'warning':logging.WARNING,
    'error':logging.ERROR,
    'critical':logging.CRITICAL
    }

def configure_logging(filename=None, level='info'):
    """Configure the appropriate level of logging"""

    # Remove all existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(filename=filename,
                        level=LOG_LEVEL_MAP[level],
                        format='[%(asctime)s] [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
