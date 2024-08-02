import logging
from dynaconf import Dynaconf

settings = Dynaconf(settings_files=['settings.toml'], environments=True)

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(settings.log_level)
    if not logger.handlers:
        # prevent logging from propagating to root logger
        logger.propagate = 0
        ch = logging.StreamHandler()
        ch.setLevel(settings.log_level)
        formatter = logging.Formatter('[%(asctime)s %(levelname)s] [%(name)s.%(funcName)s] %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger
