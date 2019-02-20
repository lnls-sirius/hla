import time
import epics
from math import isclose
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

    def check(self, value, wait=5):
        """Do timed get."""
        if not self.connected(self._pv):
            return False

        t = 0
        init = time.time()
        while t < wait:
            if isinstance(value, float):
                pv_value = self._pv.get(use_monitor=False)
                if (pv_value is not None and
                        isclose(pv_value, value, rel_tol=1e-06, abs_tol=0.0)):
                    return True
            else:
                if self._pv.get() == value:
                    return True
            t = time.time() - init
            time.sleep(5e-3)

        return False

    def get(self):
        """Return PV value."""
        if self.connected(self._pv, wait=10e-3):
            return self._pv.get(timeout=10e-3)
