import re
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Optional, Generator, Tuple

from .utils import LOG

RE_FILE_NAME = re.compile('^((?:\d{2}|xx)_[^\s.]+).?\s+([^\n]+)$')
RE_LINE_INDENT = re.compile('^(\s*)[^\n]+$')
RE_AUTHOR = re.compile(r'^\[([^]]+)](.+)')


class AnnotationNode:

    def __init__(self, *, title: str, depth: int, filename: str = ''):
        self.title_raw = title
        self.title = title
        self.author: str = ''

        if match := RE_AUTHOR.match(title):
            author, title = match.groups()
            self.author = author.strip()
            self.title = title.strip()

        self.depth = depth
        self.filename = filename
        self.parent: Optional['AnnotationNode'] = None
        self.children: List['AnnotationNode'] = []

    def __str__(self):
        filename = self.filename
        postfix = f' [{filename}]' if filename else ''
        return f'{self.title}{postfix}'

    def get_author_first(self) -> str:
        parent = self.parent
        author = ''

        while parent:
            author = parent.author
            parent = parent.parent

        return author

    def get_full_title(self, *, root_title: bool = False) -> List[str]:

        titles = [
            self.title,
        ]
        parent = self.parent

        while parent:
            titles.append(parent.title)
            parent = parent.parent

        titles = list(reversed(titles))

        if not root_title:
            titles.pop(0)

        return titles


class Annotations:

    def __init__(self, *, index_fpath: Path):
        self.fpath = index_fpath
        nodes = self.parse()
        self.nodes = nodes
        self.by_filename: Dict[str, AnnotationNode] = {
            node.filename: node
            for node in nodes if node.filename
        }

    def parse(self) -> List[AnnotationNode]:

        nodes_by_depth = defaultdict(list)
        all_nodes = []
        last_node = None

        with open(f'{self.fpath}') as f:

            for line in f:
                if indent_match := RE_LINE_INDENT.match(line):
                    depth = len(indent_match.group(1))

                    if (line := line.strip()) and not line.startswith('-'):

                        if match := RE_FILE_NAME.match(line):
                            filename = match.group(1)
                            title = match.group(2)

                            LOG.debug(f'Filename: "{filename}" | Title: "{title}"')
                            assert title, f'Empty title for line: {line}'

                        else:
                            title = line
                            filename = ''

                        node = AnnotationNode(title=title, depth=depth, filename=filename)

                        if last_node:
                            if last_node.depth == node.depth:
                                # sibling
                                parent = last_node.parent

                            elif last_node.depth < node.depth:
                                # current is child
                                parent = last_node

                            else:
                                # level up
                                parent = nodes_by_depth[node.depth][-1].parent

                            node.parent = parent
                            parent.children.append(node)

                        nodes_by_depth[depth].append(node)
                        all_nodes.append(node)
                        last_node = node

        return all_nodes

    def iter_for_files(
        self,
        files: List[Path]
    ) -> Generator[Tuple[str, Path, Optional[AnnotationNode]], None, None]:

        for filepath in sorted(files):
            filename = filepath.stem
            yield filename, filepath, self.by_filename.get(filename)
