from functools import partial
from tkinter import Event
from typing import NamedTuple, List, Callable

from .actions import TypeAction, UserAction, CheckpointAction, RollbackAction, ChapterAction

if False:  # pragma: nocover
    from .ui import RemoteControlUi  # noqa


class Shortcut(NamedTuple):

    keys: List[str]
    hint: str
    func: Callable


def label_action(event: Event, *, action: TypeAction, ui: 'RemoteControlUi'):
    ui.label_action(action)


def record_toggle(event: Event, *, ui: 'RemoteControlUi'):
    ui.rc.cmd_record_toggle()


def pause(event: Event, *, ui: 'RemoteControlUi'):
    ui.rc.cmd_pause()


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
        keys=['Tab'],
        hint='Start/stop recording',
        func=record_toggle
    ),
    Shortcut(
        keys=['space'],
        hint='Pause recording',
        func=pause
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
    Shortcut(
        keys=['a'],
        hint='Playback at speed',
        func=play
    ),
    Shortcut(
        keys=['Prior'],
        hint='Go to previous label',
        func=label_prev
    ),
    Shortcut(
        keys=['Next'],
        hint='Go to next label',
        func=label_next
    ),
    Shortcut(
        keys=['e'],
        hint='Add a checkpoint',
        func=partial(label_action, action=CheckpointAction())
    ),
    Shortcut(
        keys=['g', 'Return'],
        hint='Mark a new chapter',
        func=partial(label_action, action=ChapterAction())
    ),
    Shortcut(
        keys=['r', 'BackSpace'],
        hint='Rollback to the previous checkpoint',
        func=partial(label_action, action=RollbackAction())
    ),
    Shortcut(
        keys=['t'],
        hint='Rollback to the previous but one checkpoint',
        func=partial(label_action, action=RollbackAction(depth=2))
    ),
]
"""
Key names: https://docs.huihoo.com/tkinter/tkinter-reference-a-gui-for-python/key-names.html
"""

for slot in range(10):
    SHORTCUTS.append(
        Shortcut(
            keys=[f'{slot}'],
            hint=f'Add user action {slot}',
            func=partial(label_action, action=UserAction(slot=slot))
        ),
    )
