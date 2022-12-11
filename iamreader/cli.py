#!/usr/bin/env python
import logging

import click

from iamreader import VERSION_STR
from iamreader.utils import configure_logging
from .exceptions import IamreaderException
from .rc import RemoteControl, RemoteControlUi


@click.group()
@click.version_option(version=VERSION_STR)
def entry_point():
    """iamreader command line utilities."""


@entry_point.command()
@click.option('--debug', help='Show debug messages', is_flag=True)
def rc(debug):
    """Launches a Remote Control UI for Audacity"""

    if debug:
        configure_logging(logging.DEBUG)

    window = RemoteControlUi(remote_control=RemoteControl())
    window.bind_shortcuts()
    window.loop()


def main():
    try:
        entry_point(obj={})
    except IamreaderException as e:
        click.secho(f'{e}', fg='red', err=True)


if __name__ == '__main__':
    main()

