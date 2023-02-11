from json import loads, dumps
from pathlib import Path
from typing import List, Any


class ProjectConfig:

    def __init__(self, fpath: Path):
        self.fpath = fpath
        self._raw = {}
        self.load()

    def __str__(self):
        return f'{self.fpath}'

    def get_pub_template(self, service_alias: str) -> dict:
        return self._get_pub(service_alias=service_alias, key='template', default={})

    def get_pub_items(self, service_alias: str) -> List[dict]:
        return self._get_pub(service_alias=service_alias, key='items', default=[])

    def _get_pub(self, *, service_alias: str, key: str, default: Any) -> Any:
        service_data = self._raw['publish'].setdefault(service_alias, {
            'template': {},
            'items': [],
        })
        data = service_data.setdefault(key, default)
        return data

    def normalize(self):
        raw = self._raw
        raw.setdefault('publish', {})

    def load(self):
        with open(f'{self.fpath}') as f:
            self._raw = loads(f.read())

        self.normalize()

    def save(self):
        with open(f'{self.fpath}', 'w') as f:
            f.write(dumps(self._raw, indent=2, ensure_ascii=False))
