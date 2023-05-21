from functools import partial
from tkinter import Event
from typing import List, Callable

from .actions import TypeAction, CheckpointAction, ChapterAction, FootnoteAction

if False:  # pragma: nocover
    from .ui import RemoteControlUi  # noqa


ACTION_FOOTNOTE_BEGIN = FootnoteAction(begin=True)
ACTION_FOOTNOTE_END = FootnoteAction(begin=False)


class Shortcut:

    obj_registry: List['Shortcut'] = []

    def __init__(self, *, keys: List[str], label: str, hint: str, func: Callable):
        self.keys = keys
        """Key names: https://docs.huihoo.com/tkinter/tkinter-reference-a-gui-for-python/key-names.html"""
        self.label = label
        self.hint = hint
        self.func = func

        self.__class__.obj_registry.append(self)


def label_action(event: Event, *, action: TypeAction, ui: 'RemoteControlUi'):
    ui.label_action(action)


def mark_footnote(event: Event, *, ui: 'RemoteControlUi'):
    label_action(
        event,
        action=(
            ACTION_FOOTNOTE_END
            if ui.rs.toggle_footnote() else
            ACTION_FOOTNOTE_BEGIN
        ),
        ui=ui
    )


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


SC_MARK = Shortcut(
    label='✓',
    keys=['e'],
    hint='Add a checkpoint mark',
    func=partial(label_action, action=CheckpointAction())
)

SC_RERECORD = Shortcut(
    label='←⚫',
    keys=['t'],
    hint='Record from previous label',
    func=rerecord
)

SC_RECORD = Shortcut(
    label='⚫',
    keys=['a'],
    hint='Record',
    func=record
)


SC_PREV = Shortcut(
    label='←',
    keys=['s'],
    hint='Go to previous label',
    func=label_prev
)

SC_STOP = Shortcut(
    label='⏹',
    keys=['d'],
    hint='Stop',
    func=stop
)

SC_NEXT = Shortcut(
    label='→',
    keys=['f'],
    hint='Go to next label',
    func=label_next
)

SC_CHAPT = Shortcut(
    label='§',
    keys=['w'],
    hint='Mark a new chapter start',
    func=partial(label_action, action=ChapterAction())
)

SC_FOOT = Shortcut(
    label='※',
    keys=['q'],
    hint='Mark a footnote region start/end',
    func=mark_footnote
)

SC_SAVE = Shortcut(
    label='🖫',
    keys=['F2'],
    hint='Save project',
    func=save
)

SC_DECR = Shortcut(
    label='⯯',
    keys=['-'],
    hint='Decrement playback speed',
    func=speed_dec
)

SC_INCR = Shortcut(
    label='⯭',
    keys=['+'],
    hint='Increment playback speed',
    func=speed_inc
)
