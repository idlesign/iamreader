from json import dumps
from os import getuid
from pathlib import Path
from shutil import which
from subprocess import check_output, CalledProcessError, Popen, DEVNULL
from time import sleep
from typing import Tuple, IO, List, Callable, Optional

from .actions import TypeAction
from .state import RemoteState
from ..exceptions import RemoteControlException
from ..utils import LOG


class RemoteControl:

    _uid = getuid()
    _fpath_outgoing = Path(f'/tmp/audacity_script_pipe.to.{_uid}')
    _fpath_incoming = Path(f'/tmp/audacity_script_pipe.from.{_uid}')

    def __init__(self, *, remote_state: 'RemoteState'):
        self._pipe_out: Optional[IO] = None
        self._pipe_in: Optional[IO] = None
        self._speed: int = 100
        self._speed_delta: int = 25
        self.rs = remote_state

    def bootstrap(self):
        self._check_process(allow_spawn=True)
        self.reset_pipes()

    def reset_pipes(self):
        for pipe in (self._pipe_in, self._pipe_out):
            pipe and pipe.close()
        self._pipe_out, self._pipe_in = self._get_pipes()

    def _check_process(self, *, allow_spawn: bool, rase_exc: bool = True) -> bool:

        result = False

        try:
            check_output('ps -xc | grep audacity', shell=True)
            result = True

        except CalledProcessError:

            if allow_spawn:
                # gtk-launch allows using .desktop shortcuts (e.g. for appImage files)
                # see also https://gist.github.com/idlesign/9a625a53219eeb42474c16282b7a33e9
                cmd = 'audacity' if which('audacity') else 'gtk-launch audacity'
                Popen(cmd, shell=True, close_fds=True, stdout=DEVNULL, stderr=DEVNULL, stdin=DEVNULL)

                wait = 2
                wait_max = 15
                waited = 0

                while True:
                    sleep(wait)
                    waited += wait

                    if self._check_process(allow_spawn=False, rase_exc=False):
                        result = True

                    if result or (waited >= wait_max):
                        break

            elif rase_exc:
                raise RemoteControlException('Please run Audacity before iamreader RC is started.')

        return result

    def pack_action_data(self, action: TypeAction) -> str:
        return dumps(action.serialize())

    def _get_pipes(self) -> Tuple[IO, IO]:

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
        self.cmd_stop(select=False)  # do not select: to record just from the chosen label

        write = self.write

        if rewrite:
            write('CursorRight')  # to preserve a label
            write('SelAllTracks')  # select audio + labels track
            write('SelEnd')  # select everything to the right
            write('Delete')  # delete audio + labels
            write('CursorLeft')

        write('Record1stChoice')

        self.rs.mark_recording()

    def cmd_stop(self, *, select: bool = True):
        """

        :param select: Set the selection starting pointer on stop.

        """
        state = self.rs
        write = self.write
        select and (not state.is_stopped) and write('SetLeftSelection')
        write('Stop')
        state.mark_stopped()

    def cmd_play(self):
        self.write('PlayAtSpeed')
        self.rs.mark_playing()

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
        self.cmd_stop()
        self.write('Save')

    def cmd_strip_silence(self):
        # PinnedHead - sticky cursor
        self.write('CursProjectStart')
        self.write('SelEnd')
        self.write('SelAllTracks')
        # Threshold -20 dB and -80 dB
        self.write('TruncateSilence: Threshold=-20 Minimum=0.5 Compress=80 Action="Compress Excess Silence"')

    def cmd_to_label_prev(self):
        self.write('MoveToPrevLabel')
        self.rs.mark_stopped()

    def cmd_to_label_next(self):
        self.write('MoveToNextLabel')
        self.rs.mark_stopped()

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
