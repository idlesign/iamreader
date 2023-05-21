

class RemoteState:

    def __init__(self):
        self.is_recording = False
        """Currently in recoding."""

        self.is_in_footnote = False
        """Currently in a footnote region."""

    def toggle_footnote(self):

        value = self.is_in_footnote
        value_new = not value

        self.is_in_footnote = value_new

        return value
