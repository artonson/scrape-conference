import logging


def setup_custom_logger(name, filename=None):
    formatter = logging.Formatter(fmt='%(levelname)s %(asctime)s %(process)d/%(thread)d: %(message)s')
    if None is filename:
        handler = logging.StreamHandler()
    else:
        handler = logging.FileHandler(filename)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if logger.handlers:
        existing_handler = logger.handlers[0]
        logger.removeHandler(existing_handler)
    logger.addHandler(handler)
    return logger


def loggable(message):
    logger = logging.getLogger('root')
    logger.debug(message)

    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator




