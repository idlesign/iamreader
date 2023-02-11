
class IamreaderException(Exception):
    """Base iamreader exeption."""


class RemoteControlException(IamreaderException):
    """Base remote control exception."""


class ServiceException(IamreaderException):
    """Base exception for interaction with services."""
