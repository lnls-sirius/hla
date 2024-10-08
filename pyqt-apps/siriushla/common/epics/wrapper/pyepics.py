"""PyEpicsWrapper."""

from math import isclose
import epics
from epics.ca import ChannelAccessGetFailure, CASeverityException
import numpy as _np
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX

_TIMEOUT = 0.5


class PyEpicsWrapper:
    """Wraps a PV object.

    Implements:
    pvname
    put
    check
    get
    """

    TIMEOUT = _TIMEOUT

    def __init__(self, pv):
        """Create PV object."""
        pvn = _VACA_PREFIX + ('-' if _VACA_PREFIX else '') + pv
        self._pv = epics.get_pv(pvn)

    @property
    def pvname(self):
        """PV Name."""
        return self._pv.pvname

    def put(self, value, wait=_TIMEOUT):
        """Put if connected."""
        if not self._pv.wait_for_connection(wait):
            return False
        return self._pv.put(value)

    def check(self, value, wait=_TIMEOUT):
        """Do timed get."""
        pvv = self.get(wait=wait)
        if pvv is None:
            return False
        elif self._isarray(pvv) or self._isarray(value):
            try:
                if len(pvv) != len(value):
                    return False
                return _np.allclose(pvv, value, rtol=1e-06, atol=0.0)
            except TypeError:
                # one of them is not an array or the array type is not numeric
                return False
        elif isinstance(pvv, float) or isinstance(value, float):
            return isclose(pvv, value, rel_tol=1e-06, abs_tol=0.0)
        elif pvv == value:
            return True
        return False

    def get(self, wait=_TIMEOUT):
        """Return PV value."""
        if not self._pv.wait_for_connection(wait):
            return None
        try:
            value = self._pv.get(timeout=wait)
        except (ChannelAccessGetFailure, CASeverityException):
            # exceptions raised in a Virtual Circuit Disconnect (192)
            # event. If the PV IOC goes down, for example.
            print('Could not get value of {}'.format(self._pv.pvname))
            value = None
        return value

    def _isarray(self, value):
        return isinstance(value, (_np.ndarray, list, tuple))
