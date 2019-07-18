import time
import epics
from math import isclose
import numpy as _np
from siriuspy.envars import vaca_prefix as _VACA_PREFIX


class PyEpicsWrapper:
    """Wraps a PV object.

    Implements:
    pvname
    connected
    put
    check
    get
    """

    def __init__(self, pv):
        """Create PV object."""
        self._pv = epics.get_pv(_VACA_PREFIX + pv)

    @property
    def pvname(self):
        """PV Name."""
        return self._pv.pvname

    def connected(self, pv, wait=50e-3):
        """Wait pv connection."""
        t = 0
        init = time.time()
        while not pv.connected:
            t = time.time() - init
            if t > wait:
                return False
            time.sleep(5e-3)
        return True

    def put(self, value):
        """Put if connected."""
        if not self.connected(self._pv):
            return False
        return self._pv.put(value)

    def check(self, value, wait=10):
        """Do timed get."""
        if not self.connected(self._pv):
            return False

        dt = 5e-3
        for _ in range(int(wait/dt)):
            pvv = self._pv.get(use_monitor=False)
            if pvv is not None:
                break
            time.sleep(dt)

        if pvv is None:
            return False
        elif isinstance(pvv, _np.ndarray) or isinstance(value, _np.ndarray):
            if len(pvv) != len(value):
                return False
            return _np.allclose(pvv, value, rtol=1e-06, atol=0.0)
        elif isinstance(pvv, float) or isinstance(value, float):
            return isclose(pvv, value, rel_tol=1e-06, abs_tol=0.0)
        elif pvv == value:
            return True
        return False

    def get(self):
        """Return PV value."""
        if self.connected(self._pv):
            return self._pv.get(timeout=50e-3)
