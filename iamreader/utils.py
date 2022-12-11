import logging

LOG = logging.getLogger('iamreader')


def configure_logging(log_level=None):
    """Performs basic logging configuration.

    :param log_level: logging level, e.g. logging.DEBUG
        Default: logging.INFO

    """
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level or logging.INFO)
