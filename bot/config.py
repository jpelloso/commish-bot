import logging
from dynaconf import Dynaconf

# When environments=true, default will be used unless settings.env('ENVIRONMENT') is set (e.g. dev, prod)
# Groups within the toml file will need to be prefixed with the environment name (e.g. dev,channels, prod.channels)
# If we set environments=false, groups do not need the prefix and can be accessed directly
# However, any settings that are in [default] will need to be updated to config.settings.default.log_level
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
