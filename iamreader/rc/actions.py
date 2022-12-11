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

    ident: str = 'p'


class ChapterAction(ActionBase):

    ident: str = 'c'


class RollbackAction(ActionBase):

    ident: str = 'r'

    def __init__(self, *, depth: int = 1):
        self.depth = depth

    def serialize(self, params: dict = None) -> dict:
        return super().serialize({
            'd': self.depth,
        })
