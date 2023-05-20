from functools import partial
from tkinter import Tk, Frame, Label, Event, Text, END, DISABLED
from typing import Callable

from .audacity import RemoteControl, TypeAction
from .shortcuts import SHORTCUTS
from ..utils import LOG


class RemoteControlUi:

    def __init__(self, *, remote_control: 'RemoteControl'):

        LOG.debug('Creating RC UI ...')

        app = Tk()
        app.title('iamreader Audacity Remote Control')
        app.geometry('400x150')
        app.attributes('-topmost', True)
        app.resizable(False, False)

        self.app = app
        self.rc = remote_control

        frame = Frame(
            app,
            name='iamreader-rc'
        )

        statusbar = Label(app, text='', anchor='w', background='#ccc', foreground='white', font=('Arial', 9))
        statusbar.pack(side='bottom', fill='x')
        self.statusbar = statusbar

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
        
    def on_focus_in(self, event: Event):
        self.statusbar['bg'] = '#ccc'
        self.statusbar['text'] = ''

    def on_focus_out(self, event: Event):
        self.statusbar['bg'] = 'red'
        self.statusbar['text'] = "The RC won't work since the window is out of focus."

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
