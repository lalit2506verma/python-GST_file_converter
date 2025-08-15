import logging, logging.config


def setup_logging():
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "Formatters":{
            "plain": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"}
        },
        "handlers": {
            "console": {"class": "logging.StreamHandler", "fomatter": "plain"},
        },
        "root": {"level": "INFO", "handlers": ["console"]},
    })