from json import dumps
from os import getuid
from pathlib import Path
from subprocess import check_output, CalledProcessError
from typing import Tuple, IO, List, Callable

from .actions import TypeAction
from ..exceptions import RemoteControlException
from ..utils import LOG


class RemoteControl:

    _uid = getuid()
    _fpath_outgoing = Path(f'/tmp/audacity_script_pipe.to.{_uid}')
    _fpath_incoming = Path(f'/tmp/audacity_script_pipe.from.{_uid}')

    def __init__(self):
        self._pipe_out, self._pipe_in = self._get_pipes()
        self._speed: int = 100
        self._speed_delta: int = 25

    def pack_action_data(self, action: TypeAction) -> str:
        return dumps(action.serialize())

    def _get_pipes(self) -> Tuple[IO, IO]:

        try:
            check_output('ps -xc | grep audacity', shell=True)

        except CalledProcessError:
            raise RemoteControlException('Please run Audacity before iamreader RC is started.')

        f_out = self._fpath_outgoing
        f_in = self._fpath_incoming

        LOG.debug(f'Audacity pipe files: {f_out}, {f_in}')

        if not all([f_out.exists(), f_in.exists()]):
            raise RemoteControlException(
                'Unable to find Audacity pipe files. '
                'Please ensure Audacity is running and "mod-script-pipe"'
                'is enabled in Preferences -> Modules.')

        p_out = open(f_out, 'w')
        p_in = open(f_in, 'r')

        return p_out, p_in

    def cmd_record(self, *, rewrite: bool = True):
        self.cmd_stop(select=False)  # do not select to record just from the chosen label

        write = self.write

        if rewrite:
            write('CursorRight')  # to preserve a label
            write('SelAllTracks')  # select audio + labels track
            write('SelEnd')  # select everything to the right
            write('Delete')  # delete audio + labels
            write('CursorLeft')

        write('Record1stChoice')

    def cmd_pause(self):
        self.write('Pause')

    def cmd_stop(self, *, select: bool = True):
        write = self.write
        select and write('SetLeftSelection')
        write('Stop')

    def cmd_play(self):
        self.write('PlayAtSpeed')

    def cmd_speed_inc(self):
        self.cmd_speed_set(self._speed_delta)

    def cmd_speed_dec(self):
        self.cmd_speed_set(-self._speed_delta)

    def cmd_speed_set(self, delta: int):
        # SetPlaySpeed accepts no params, emulate
        cmd = 'PlaySpeedInc' if delta > 0 else 'PlaySpeedDec'
        write = self.write

        self.cmd_stop()
        for _ in range(int(abs(delta) / 3)):
            write(cmd)

        self._speed += delta
        LOG.debug(f'Audacity speed: {self._speed}')

        self.cmd_play()

    def cmd_save(self):
        self.write('Save')

    def cmd_to_label_prev(self):
        self.write('MoveToPrevLabel')

    def cmd_to_label_next(self):
        self.write('MoveToNextLabel')

    def cmd_add_action_label(self, *, action: TypeAction, callback: Callable = None):
        text = self.pack_action_data(action)
        callback = callback or (lambda val: val)
        callback(text)
        self.cmd_add_label(text)

    def cmd_add_label(self, text: str = ''):
        write = self.write
        # use clipboard (ui.copy_to_clipboard(text))
        # to workaround Audacity inability to set text
        # right from AddLabelPlaying
        write('AddLabelPlaying')
        write('Paste')

    def write(self, cmd: str):
        LOG.debug(f'Audacity command: "{cmd}"')

        p_out = self._pipe_out
        p_out.write(f'{cmd}\n')
        p_out.flush()

    def read(self) -> List[str]:
        # todo maybe?

        result = []
        p_in = self._pipe_in

        while True:
            line = p_in.readline()  # this will fail for raw bytes
            if line == '\n' and result:
                break

        LOG.debug(f'Audacity response: "{result}"')

        return result
