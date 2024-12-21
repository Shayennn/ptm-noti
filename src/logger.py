import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter(
        '{"timestamp":"%(asctime)s","level":"%(levelname)s","message":%(message)s}',
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
)
logger.addHandler(handler)


def log_json(level, msg, **kwargs):
    record = {"msg": msg}
    record.update(kwargs)
    logger.log(level, json.dumps(record))
