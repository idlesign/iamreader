from typing import TypeVar


class ActionBase:

    ident: str = ''

    def serialize(self, params: dict = None) -> dict:
        data = {
            'a': f'{self.ident}',
            'p': {**(params or {})},
        }
        return data


TypeAction = TypeVar('TypeAction', bound=ActionBase)


class UserAction(ActionBase):

    ident: str = 'u'

    def __init__(self, *, slot: int):
        self.slot = slot

    def serialize(self, params: dict = None) -> dict:
        return super().serialize({
            's': self.slot,
        })


class CheckpointAction(ActionBase):
    """Allows identification of places where some event has happened (e.g. utterance is ended)."""

    ident: str = 'p'


class ChapterAction(ActionBase):
    """Allows identification of places where a new chapter begins."""

    ident: str = 'c'
