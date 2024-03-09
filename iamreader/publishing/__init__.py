from pathlib import Path

from .config import ProjectConfig
from .services import Service
from ..annotations import Annotations
from ..utils import PATH_FILE_INDEX


def media_publish(*, service: str, path_resources: Path):

    cfg = ProjectConfig(path_resources / 'iamreader.json')

    try:
        Service.registry[service](
            config=cfg,
            annotations=Annotations(index_fpath=PATH_FILE_INDEX),
            path_resources=path_resources,
        ).publish()

    finally:
        cfg.save()
