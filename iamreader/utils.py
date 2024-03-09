import logging
from os import walk
from pathlib import Path
from typing import List

LOG = logging.getLogger('iamreader')

PATH_ASSETS = Path(__file__).parent / 'assets'

PATH_CURRENT = Path.cwd()
PATH_RESOURCES = PATH_CURRENT / 'res'
PATH_RESOURCES_OUT = PATH_RESOURCES / 'out'
PATH_OUT_AUDIO = PATH_RESOURCES_OUT / 'aud'
PATH_OUT_VIDEO = PATH_RESOURCES_OUT / 'vid'
PATH_OUT_IMAGES = PATH_RESOURCES_OUT / 'img'

FILENAME_INDEX = 'titles.txt'
PATH_FILE_INDEX = PATH_RESOURCES / FILENAME_INDEX


def configure_logging(log_level=None):
    """Performs basic logging configuration.

    :param log_level: logging level, e.g. logging.DEBUG
        Default: logging.INFO

    """
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level or logging.INFO)


def list_files(src_path: Path, *, ext: str) -> List[Path]:
    candidates = []

    for path, subs, files in walk(src_path):
        for file in files:
            fullpath = Path(path) / file
            if fullpath.suffix == f'.{ext}':
                candidates.append(fullpath)

    return candidates
