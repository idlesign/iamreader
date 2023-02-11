import logging
from pathlib import Path

LOG = logging.getLogger('iamreader')

PATH_ASSETS = Path(__file__).parent / 'assets'


def configure_logging(log_level=None):
    """Performs basic logging configuration.

    :param log_level: logging level, e.g. logging.DEBUG
        Default: logging.INFO

    """
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level or logging.INFO)
