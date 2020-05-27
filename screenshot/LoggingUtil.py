import logging.config
import os

import yaml

with open('logging.yaml') as f:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    logging.config.dictConfig(yaml.safe_load(f.read()))


def get_logging(name=None):
    if name:
        return logging.getLogger(name)
    return logging
