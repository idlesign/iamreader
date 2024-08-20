import logging
from datetime import datetime
from pathlib import Path
from typing import List

from ..annotations import Annotations
from ..utils import LOG, list_files, PATH_FILE_INDEX

logger = logging.getLogger('eyed3')
logger.setLevel(logging.ERROR)


def annotate_single(
    *,
    filepath: Path,
    artist: str,
    album: str,
    title: str,
    idx: int = 0,
    cover: Path = None,
):
    from eyed3 import load as load_audio
    from eyed3.id3 import ID3_V2_3, Tag, frames

    audio = load_audio(filepath)

    tag: Tag = audio.tag
    if tag is None:
        tag = audio.initTag()

    tag.artist = artist
    tag.album = album
    tag.title = title

    if idx:
        tag.track_num = idx

    tag.genre = 'Audiobook'
    tag.release_date = datetime.now().year

    if cover.exists():
        tag.images.set(frames.ImageFrame.FRONT_COVER, cover.read_bytes(), f'image/{cover.suffix}')

    tag.save(version=ID3_V2_3)


def annotate_media(
    *,
    audio_files: List[Path],
    annotations: Annotations,
    cover: Path,
):

    for idx, (filename, filepath, candidate_annotation) in enumerate(annotations.iter_for_files(audio_files), 1):

        if not candidate_annotation:
            LOG.warning(f'No annotation for "{filename}". Skipped.')
            continue

        title = candidate_annotation.title
        LOG.info(f'Annotating "{filename}" -> {title} ...')

        annotate_single(
            filepath=filepath,
            artist=candidate_annotation.get_author_first(),
            album=candidate_annotation.get_title_first(),
            title=title,
            idx=idx,
            cover=cover,
        )


def annotate(
    *,
    path_resources: Path,
    path_audio_in: Path,
):
    LOG.debug(f'{path_resources=}')
    LOG.debug(f'{path_audio_in=}')

    annotate_media(
        audio_files=list_files(path_audio_in, ext='mp3'),
        annotations=Annotations(index_fpath=PATH_FILE_INDEX),
        cover=path_resources / 'cover.jpg',
    )
