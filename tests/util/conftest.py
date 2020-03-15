
import pytest


class _StringableErr:
    """
    Class intended to fail when converted to string, or printed.
    """

    def __str__(self):
        raise Exception("intended")

    def __repr__(self):
        raise Exception("intended")


@pytest.fixture()
def stringable_err():
    """
    Return an object which throws an exception when converted to string.
    """
    return _StringableErr()
