import sys
from datetime import datetime, timedelta
from functools import partial
from tkinter import Tk, Frame, Label, Event, Button, font, messagebox
from typing import Callable, List, Union

from .audacity import RemoteControl, TypeAction
from .shortcuts import (
    Shortcut, SC_MARK, SC_RERECORD, SC_INCR, SC_DECR, SC_SAVE, SC_RECORD, SC_FOOT, SC_CHAPT, SC_PREV, SC_STOP, SC_NEXT
)
from .state import RemoteState
from ..utils import LOG


class Timer:

    def __init__(self, *, cumulative: bool = False):
        self.enabled = True
        self.started = None
        self.delta = timedelta()
        self.delta_cumulative = timedelta()
        self.cumulate = cumulative

    def __str__(self) -> str:
        return f'{self.delta_cumulative + self.delta}'.partition('.')[0]

    def update(self):
        started = self.started

        if not started:
            self.enabled = True
            started = datetime.now()
            self.started = started

        if self.enabled:
            self.delta = datetime.now() - started

    def stop(self):

        if not self.enabled:
            return

        self.enabled = False
        self.started = None

        if self.cumulate:
            self.delta_cumulative += self.delta
            self.delta = timedelta()


class RemoteControlUi:

    def __init__(self, *, remote_control: 'RemoteControl', remote_state: 'RemoteState'):

        LOG.debug('Creating RC UI ...')

        self._focused = True

        self._time_session = Timer()
        self._time_record_current = Timer()
        self._time_record_total = Timer(cumulative=True)

        app = Tk()
        app.title('iamreader Audacity Remote Control')
        app.geometry('250x170')

        try:
            remote_control.bootstrap()

        except Exception as e:
            if messagebox.showerror(title='RC Failure', message=f'{e}'):
                sys.exit()

        app.attributes('-topmost', True)
        app.resizable(False, False)

        font_small = font.Font(size=8)
        font_main = font.Font(size=12)

        self.app = app
        self.rc = remote_control
        self.rs = remote_state

        frame = Frame(app, name='iamreader-rc')

        statusbar = Label(app, text='', anchor='w', background='#ccc', foreground='white', font=font_small)
        statusbar.pack(side='bottom', fill='x')
        self.statusbar = statusbar

        statusbar.after(1000, self.on_statusbar_refresh)

        def place_sample_buttons(shortcuts: List[List[Union[Shortcut, None]]]):
            for row_idx, row_items in enumerate(shortcuts):
                for column_idx, shortcut in enumerate(row_items):
                    text = ' ' if shortcut is None else f'{shortcut.keys[0].upper()} {shortcut.label}'
                    Button(
                        frame,
                        text=text,
                        font=font_main,
                        state='disabled',
                    ).grid(row=row_idx, column=column_idx, sticky='nesw')

        place_sample_buttons(
            [
                [None, SC_MARK, SC_RERECORD],
                [SC_PREV, SC_STOP, SC_NEXT],
                [None, None, None],
                [SC_DECR, SC_INCR, SC_SAVE],
            ]
        )

        frame.pack(side='top', fill='both', expand=True)

        self.bind_event(event='FocusIn', func=self.on_focus_in)
        self.bind_event(event='FocusOut', func=self.on_focus_out)

        frame.focus_set()

    def on_statusbar_refresh(self):
        bar = self.statusbar

        time_session = self._time_session
        time_record_total = self._time_record_total
        time_record_current = self._time_record_current
        time_session.update()

        state = self.rs

        if state.is_recording:
            time_record_current.update()
            time_record_total.update()

        else:
            time_record_current.stop()
            time_record_total.stop()

        if self._focused:
            state_items = []

            if state.is_recording:
                state_items.append('⚫')

            elif state.is_stopped:
                state_items.append('◾')

            elif state.is_playing:
                state_items.append('▸')

            if state.is_in_footnote:
                state_items.append('※')

            bar['text'] = (
                f'session: {time_session} | '
                f'rec: total {time_record_total} / current {time_record_current} | '
                f"state: {' '.join(state_items)}"
            )

        bar.after(1000, self.on_statusbar_refresh)
        
    def on_focus_in(self, event: Event):
        self.statusbar.configure(
            bg='#aaa',
            text='',
        )
        self._focused = True

    def on_focus_out(self, event: Event):
        self.statusbar.configure(
            bg='red',
            text="The RC won't work since the window is out of focus.",
        )
        self._focused = False

    def bind_event(self, *, event: str, func: Callable):

        if not event.isnumeric():
            event = f'<{event}>'

        LOG.debug(f'Binding {event}: {func} ...')

        self.app.bind(event, func)

    def bind_shortcuts(self):
        LOG.debug('Binding shortcuts ...')

        keymap = {
            '+': 'equal',
            '-': 'minus',
        }

        for shortcut in Shortcut.obj_registry:
            if not shortcut.enabled:
                continue
            for key in shortcut.keys:
                self.bind_event(
                    event=keymap.get(key, key),
                    func=partial(shortcut.func, ui=self),
                )

    def label_action(self, action: TypeAction):
        self.rc.cmd_add_action_label(
            action=action,
            callback=self.copy_to_clipboard,
        )

    def copy_to_clipboard(self, text: str):
        engine = self.app
        engine.clipboard_clear()
        engine.clipboard_append(text)

    def loop(self):
        LOG.debug('Starting the UI loop ...')

        self.app.mainloop()
