from functools import partial
from tkinter import Tk, Frame, Label, Event, Text, END
from typing import Callable

from .audacity import RemoteControl, TypeAction
from .shortcuts import SHORTCUTS
from ..utils import LOG


class RemoteControlUi:

    def __init__(self, *, remote_control: 'RemoteControl'):

        LOG.debug('Creating RC UI ...')

        app = Tk()
        app.title('iamreader Audacity Remote Control')

        self.app = app
        self.rc = remote_control

        frame = Frame(
            app,
            width=600,
            height=100,
            name='iamreader-rc'
        )
        self.frame = frame

        statusbar = Label(app, text='', anchor='w', background='#ccc', foreground='white')
        statusbar.pack(side='bottom', fill='x')
        self.statusbar = statusbar

        hint_area = Text(
            app, width=40, height=16,
            takefocus=False,
            font=('Arial', 10),
        )
        hint_area.pack(side='top', fill='both', expand=True)
        self.hint_area = hint_area

        frame.pack(side='top', fill='both', expand=True)

        self.bind_event(event='FocusIn', func=self.on_focus_in)
        self.bind_event(event='FocusOut', func=self.on_focus_out)

        frame.focus_set()
        
    def on_focus_in(self, event: Event):
        self.statusbar['bg'] = '#ccc'
        self.statusbar['text'] = ''

    def on_focus_out(self, event: Event):
        self.statusbar['bg'] = 'red'
        self.statusbar['text'] = 'This window is out of focus. The remote control for Audacity will not work.'

    def bind_event(self, *, event: str, func: Callable):

        if not event.isnumeric():
            event = f'<{event}>'

        LOG.debug(f'Binding {event}: {func} ...')

        self.frame.bind(event, func)

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
