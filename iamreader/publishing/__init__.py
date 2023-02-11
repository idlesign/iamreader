from pathlib import Path

from .config import ProjectConfig
from .services import Service
from ..annotations import Annotations


def media_publish(*, service: str, path_resources: Path):

    cfg = ProjectConfig(path_resources / 'iamreader.json')

    try:
        Service.registry[service](
            config=cfg,
            annotations=Annotations(index_fpath=path_resources / 'index.txt'),
            path_resources=path_resources,
        ).publish()

    finally:
        cfg.save()
