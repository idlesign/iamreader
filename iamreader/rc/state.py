
STATE_STOPPED = 0
STATE_RECORDING = 1
STATE_PLAYING = 2


class RemoteState:

    def __init__(self):
        self._value: int = STATE_STOPPED
        """Current state value."""

        self.is_in_footnote = False
        """Currently in a footnote region."""

    @property
    def is_recording(self) -> bool:
        return self._value == STATE_RECORDING

    def mark_recording(self):
        self._value = STATE_RECORDING

    @property
    def is_playing(self) -> bool:
        return self._value == STATE_PLAYING

    def mark_playing(self):
        self._value = STATE_PLAYING

    @property
    def is_stopped(self) -> bool:
        return self._value == STATE_STOPPED

    def mark_stopped(self):
        self._value = STATE_STOPPED

    def toggle_footnote(self):

        value = self.is_in_footnote
        value_new = not value

        self.is_in_footnote = value_new

        return value
