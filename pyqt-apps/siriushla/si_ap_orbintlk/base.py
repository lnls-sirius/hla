"""Base Object."""

import numpy as _np
from siriuspy.epics import PV as _PV
from siriuspy.envars import VACA_PREFIX
from siriuspy.namesys import SiriusPVName
from siriuspy.clientconfigdb import ConfigDBClient
from siriuspy.devices.orbit_interlock import BaseOrbitIntlk, OrbitInterlock


class BaseObject(BaseOrbitIntlk):
    """Base SI BPM info object."""

    CONV_NM2M = 1e-9  # [nm] --> [m]
    CONV_UM2NM = 1e+3  # [um] --> [nm]

    CONV_POLY_MONIT1_2_MONIT = OrbitInterlock.CONV_POLY_MONIT1_2_MONIT

    _pvs = dict()

    def __init__(self, prefix=VACA_PREFIX):
        super().__init__()
        self._client = ConfigDBClient(config_type='si_orbit')
        self._prefix = prefix

    def get_ref_orb(self, configname):
        """Get reference orbit from config [um].

        Args:
            configname (str): si orbit configuration name.

        Returns:
            si_orbit: si orbit configuration value from ConfigDB
        """
        try:
            configvalue = self._client.get_config_value(configname)
            value = dict()
            value['x'] = _np.array(configvalue['x']) * self.CONV_UM2NM
            value['y'] = _np.array(configvalue['y']) * self.CONV_UM2NM
        except:
            value = dict()
            value['x'] = _np.zeros(len(self.BPM_NAMES), dtype=float)
            value['y'] = _np.zeros(len(self.BPM_NAMES), dtype=float)
        return value

    # --- pv handler methods ---

    def _create_pvs(self, propty):
        new_pvs = dict()
        for psn in self.BPM_NAMES:
            pvname = SiriusPVName(psn).substitute(
                prefix=self._prefix, propty=propty)
            if pvname in self._pvs:
                continue
            new_pvs[pvname] = _PV(pvname, connection_timeout=0.01)
        self._pvs.update(new_pvs)

    def _get_values(self, propty):
        for psn in self.BPM_NAMES:
            pvname = SiriusPVName(psn).substitute(
                prefix=self._prefix, propty=propty)
            self._pvs[pvname].wait_for_connection()

        values = list()
        for psn in self.BPM_NAMES:
            pvname = SiriusPVName(psn).substitute(
                prefix=self._prefix, propty=propty)
            val = self._pvs[pvname].get()
            if val is None:
                val = 0
            elif propty.startswith('Intlk') and propty.endswith('-Mon'):
                val = 1 if val == 0 else 0
            values.append(val)
        return values
