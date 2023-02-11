from os import makedirs
from pathlib import Path
from subprocess import run
from typing import List

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from ..annotations import Annotations
from ..utils import LOG, PATH_ASSETS, list_files


def generate_cover(*, fpath: Path, text: str, template: Path):

    LOG.debug(f'Generating "{fpath}" ...')

    img = Image.open(f'{template}')
    img = img.convert('RGB')

    # /usr/local/share/fonts
    # ~/.local/share/fonts
    font = ImageFont.truetype(
        f"{ PATH_ASSETS / 'fonts' / 'Ubuntu-R.ttf' }",
        size=20
    )

    draw = ImageDraw.Draw(img)
    draw.text(xy=(450, 250), text=text, fill=(255, 255, 255), font=font)

    img.save(f'{fpath}')


def generate_media(
    *,
    audio_files: List[Path],
    annotations: Annotations,
    cover_template: Path,
    dest_vid: Path,
    dest_img: Path,
):

    makedirs(dest_vid, exist_ok=True)
    makedirs(dest_img, exist_ok=True)

    for candidate in sorted(audio_files):
        out_video = dest_vid / candidate.with_suffix('.avi').name
        filename = out_video.stem

        text = ''
        if candidate_annotation := annotations.by_filename.get(filename):
            text = '\n\n'.join(candidate_annotation.get_full_title())

        if not text.strip():
            LOG.warning(f'No annotation for "{filename}". Skipped.')
            continue

        LOG.info(f'Generating media for "{filename}" ...')

        image = dest_img / f'{filename}.png'

        generate_cover(
            fpath=image,
            text=text,
            template=cover_template,
        )

        LOG.debug(f'Generating "{out_video}" ...')

        run(
            # f'ffmpeg -loop 1 -i {image} -i {candidate} -c:v libx264 -tune stillimage -c:a copy -shortest {out_video}'
            f'ffmpeg -r 1 -loop 1 -y -i {image} -i {candidate} -c:a copy -r 1 -vcodec libx264 -shortest {out_video}',
            shell=True
        )


def generate(
    *,
    path_resources: Path,
    path_audio_in: Path,
    path_out_vid: Path,
    path_out_img: Path,
):
    generate_media(
        audio_files=list_files(path_audio_in, ext='mp3'),
        annotations=Annotations(fpath=path_resources / 'index.txt'),
        cover_template=path_resources / 'bg.png',
        dest_vid=path_out_vid,
        dest_img=path_out_img,
    )
