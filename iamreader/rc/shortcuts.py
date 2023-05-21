from functools import partial
from tkinter import Event
from typing import NamedTuple, List, Callable

from .actions import TypeAction, CheckpointAction, ChapterAction

if False:  # pragma: nocover
    from .ui import RemoteControlUi  # noqa


class Shortcut(NamedTuple):

    keys: List[str]
    hint: str
    func: Callable


def label_action(event: Event, *, action: TypeAction, ui: 'RemoteControlUi'):
    ui.label_action(action)


def record(event: Event, *, ui: 'RemoteControlUi'):
    ui.rc.cmd_record()


def rerecord(event: Event, *, ui: 'RemoteControlUi'):
    ui.rc.cmd_stop()
    ui.rc.cmd_to_label_prev()
    ui.rc.cmd_record()


def stop(event: Event, *, ui: 'RemoteControlUi'):
    ui.rc.cmd_stop()


def play(event: Event, *, ui: 'RemoteControlUi'):
    ui.rc.cmd_play()


def save(event: Event, *, ui: 'RemoteControlUi'):
    ui.rc.cmd_save()


def speed_inc(event: Event, *, ui: 'RemoteControlUi'):
    ui.rc.cmd_speed_inc()


def speed_dec(event: Event, *, ui: 'RemoteControlUi'):
    ui.rc.cmd_speed_dec()


def label_prev(event: Event, *, ui: 'RemoteControlUi'):
    ui.rc.cmd_to_label_prev()
    play(event, ui=ui)


def label_next(event: Event, *, ui: 'RemoteControlUi'):
    ui.rc.cmd_to_label_next()
    play(event, ui=ui)


SHORTCUTS: List[Shortcut] = [
    Shortcut(
        keys=['e'],
        hint='Add a checkpoint',
        func=partial(label_action, action=CheckpointAction())
    ),
    Shortcut(
        keys=['t'],
        hint='Record from previous label',
        func=rerecord
    ),
    Shortcut(
        keys=['a'],
        hint='Record',
        func=record
    ),
    Shortcut(
        keys=['s'],
        hint='Go to previous label',
        func=label_prev
    ),
    Shortcut(
        keys=['d'],
        hint='Stop',
        func=stop
    ),
    Shortcut(
        keys=['f'],
        hint='Go to next label',
        func=label_next
    ),
    Shortcut(
        keys=['w'],
        hint='Mark a new chapter',
        func=partial(label_action, action=ChapterAction())
    ),
    Shortcut(
        keys=['Insert'],
        hint='Save project',
        func=save
    ),
    Shortcut(
        keys=['minus'],
        hint='Decrement playback speed',
        func=speed_dec
    ),
    Shortcut(
        keys=['equal'],
        hint='Increment playback speed',
        func=speed_inc
    ),
]
"""
Key names: https://docs.huihoo.com/tkinter/tkinter-reference-a-gui-for-python/key-names.html
"""
