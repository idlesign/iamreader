#!/usr/bin/env python
import logging

import click

from . import VERSION_STR
from .exceptions import IamreaderException
from .rc import RemoteControl, RemoteControlUi
from .utils import configure_logging, PATH_RESOURCES_OUT, PATH_OUT_AUDIO, PATH_RESOURCES, PATH_PROJECT_CFG
from .video import generate as video_generate
from .video.services import YoutubeService

PATH_CURRENT = Path.cwd()


@click.group()
@click.version_option(version=VERSION_STR)
@click.option('--debug', help='Show debug messages', is_flag=True)
def entry_point(debug):
    """iamreader command line utilities."""
    configure_logging(logging.DEBUG if debug else None)


@entry_point.command()
def rc():
    """Launches a Remote Control UI for Audacity"""
    window = RemoteControlUi(remote_control=RemoteControl())
    window.bind_shortcuts()
    window.loop()

@entry_point.group()
def video():
    """Video related commands."""

@video.command()
def generate():
    """Generates video from audio and text index file."""
    video_generate(
        path_resources=PATH_RESOURCES,
        path_audio_in=PATH_OUT_AUDIO,
        path_out=PATH_RESOURCES_OUT,
    )


@video.command()
@click.argument('service')
def publish(service):
    """Publish videos at a remote service."""
    YoutubeService.publish()


def main():
    try:
        entry_point(obj={})
    except IamreaderException as e:
        click.secho(f'{e}', fg='red', err=True)


if __name__ == '__main__':
    main()
