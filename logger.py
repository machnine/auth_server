import logging
from logging.config import fileConfig

fileConfig("logging.conf")
logger = logging.getLogger("simpleLogger")
