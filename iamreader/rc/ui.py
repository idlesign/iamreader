from datetime import datetime, timedelta
from functools import partial
from tkinter import Tk, Frame, Label, Event, Text, END, DISABLED
from typing import Callable

from .audacity import RemoteControl, TypeAction
from .shortcuts import SHORTCUTS
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
        app.geometry('400x170')
        app.attributes('-topmost', True)
        app.resizable(False, False)

        self.app = app
        self.rc = remote_control
        self.rs = remote_state

        frame = Frame(app, name='iamreader-rc')

        statusbar = Label(app, text='', anchor='w', background='#ccc', foreground='white', font=('Arial', 9))
        statusbar.pack(side='bottom', fill='x')
        self.statusbar = statusbar

        statusbar.after(1000, self.on_statusbar_refresh)

        hint_area = Text(
            app,
            takefocus=False,
            font=('Arial', 8),
        )
        hint_area.pack(side='top', fill='both', expand=True)
        self.hint_area = hint_area

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
                state_items.append('REC')

            if state.is_in_footnote:
                state_items.append('FN')

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

        hint_area = self.hint_area

        for shortcut in SHORTCUTS:
            hint_area.insert(END, f'{shortcut.keys} - {shortcut.hint}\n')

            for key in shortcut.keys:
                self.bind_event(
                    event=key,
                    func=partial(shortcut.func, ui=self),
                )

        hint_area.config(state=DISABLED)

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
