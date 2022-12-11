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

for slot in range(10):
    SHORTCUTS.append(
        Shortcut(
            keys=[f'{slot}'],
            hint=f'Add user action {slot}',
            func=partial(label_action, action=UserAction(slot=slot))
        ),
    )
