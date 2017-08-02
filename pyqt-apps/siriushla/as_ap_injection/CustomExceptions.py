"""Module that defines custom exceptions."""


class PVConnectionError(ConnectionError):
    """Failed to communicate with a PV."""

    pass
