from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, TypeVar
from typing import List

from ..config import ProjectConfig
from ...annotations import Annotations
from ...utils import PATH_OUT_AUDIO, list_files, LOG

TypeService = TypeVar('TypeService', bound='Service')


class Service:

    alias: str = ''
    registry: Dict[str, TypeService] = {}

    file_ext: str = ''

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        alias = cls.alias
        existing = cls.registry.get(alias)
        assert alias not in cls.registry, f'Service "{alias}" is already registered (exists "{existing}"; new "{cls}").'

        cls.registry[alias] = cls

    def __init__(self, *, config: ProjectConfig, annotations: Annotations, path_resources: Path):
        self._cfg = config
        self._ann = annotations
        self._path_resources = path_resources

    def __str__(self) -> str:
        return self.alias

    def materialize_template(self, path_sources: Path = None) -> List[dict]:

        path_sources = path_sources or PATH_OUT_AUDIO
        source_files = list_files(path_sources, ext=self.file_ext)
        alias = self.alias
        processed = self._cfg.get_pub_items(alias)
        template = self._cfg.get_pub_template(alias)

        items = []

        for filename, filepath, annotation in self._ann.iter_for_files(source_files):
            if not annotation:
                LOG.warning(f'No annotation for "{filename}". Skipped.')
            items.append((filepath, annotation))

        counter_width = len(f'{len(items)}')
        counter = len(processed)
        date_pub_latest = datetime.now().date()

        if processed:
            if dt_pub := processed[-1].get('dt_pub'):
                date_pub_latest = datetime.fromisoformat(dt_pub).date()

        config = []

        for idx, (filepath, annotation) in enumerate(items, 0):

            if idx < counter:
                continue

            ident = annotation.filename
            conf = {
                'ident': '{{ ident }}',
                'title': '{{ counter }}. {{ title_first }}. {{ title_last }}',
                'description': '{{ author_first }}\n{{ title_full_n }}',
                'tags': [],
                'playlists': [],
                'dt_pub': '+1d 12:30:00+00:00',
                'fpath': f'{filepath}',
            }

            full_title = annotation.get_full_title(root_title=True)

            context = {
                'counter': f'{counter + 1}'.zfill(counter_width),
                'ident': f'{ident}',
                'author_first': annotation.get_author_first(),
                'title_first': full_title[0],
                'title_last': full_title[-1],
                'title_full': '. '.join(full_title),
                'title_full_n': '\n'.join(full_title),
            }

            for key, val in conf.items():

                value = template.get(key, val)

                if isinstance(value, str):
                    for context_key, contex_val in context.items():
                        value = value.replace('{{ %s }}' % context_key, contex_val)

                conf[key] = value

            dt_pub_val = conf['dt_pub']

            if dt_pub_val.startswith('+'):
                shift, _, timechunk = dt_pub_val.partition(' ')

                dt_pub_current = (
                    datetime.fromisoformat(f'{date_pub_latest} {timechunk}') +
                    timedelta(days=int(shift.strip('+d')))
                )

                date_pub_latest = dt_pub_current.date()
                conf['dt_pub'] = f'{dt_pub_current}'

            counter += 1
            config.append(conf)

        return config

    def _contribute_item(self, *, ident_remote: str, item: dict):
        item.update({
            'ident_remote': ident_remote,
            'dt_prc': f'{datetime.now()}',
        })
        self._cfg.get_pub_items(self.alias).append(item)

    def publish(self):  # pragma: nocover
        items = self.materialize_template()
        for item in items:
            LOG.info(f"{self}: publishing {item['ident']} ...")
            self._publish_item(item)

    def _publish_item(self, item: dict) -> bool:  # pragma: nocover
        raise NotImplementedError
