"""Base Object."""

import math as _math
import numpy as _np

from epics.ca import ChannelAccessException

from siriuspy.epics import PV as _PV
from siriuspy.envars import VACA_PREFIX
from siriuspy.namesys import SiriusPVName
from siriuspy.clientconfigdb import ConfigDBClient
from siriuspy.devices.orbit_interlock import BaseOrbitIntlk


class BaseObject(BaseOrbitIntlk):
    """Base SI BPM info object."""

    CONV_NM2M = 1e-9  # [nm] --> [m]
    CONV_UM2NM = 1e+3  # [um] --> [nm]
    MINSUM_RESO = 2**24

    _pvs = dict()

    def __init__(self, prefix=VACA_PREFIX):
        super().__init__()
        self._client = ConfigDBClient(config_type='si_orbit')
        self._prefix = prefix

        self._pv_facqrate_value = None
        self._pv_monitrate_value = None
        self._monitsum2intlksum_factor = 1

        pvname = SiriusPVName(
            self.BPM_NAMES[0]).substitute(
                propty='INFOMONITRate-RB', prefix=prefix)
        self._pv_monitrate = _PV(pvname, callback=self._callback_get_rate)
        pvname = SiriusPVName(
            self.BPM_NAMES[0]).substitute(
                propty='INFOFAcqRate-RB', prefix=prefix)
        self._pv_facqrate = _PV(pvname, callback=self._callback_get_rate)

    @property
    def monitsum2intlksum_factor(self):
        """Return factor between BPM Monit Sum and interlock Sum."""
        return self._monitsum2intlksum_factor

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
        except Exception:
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
            new_pvs[pvname] = _PV(
                pvname, auto_monitor=False, connection_timeout=0.01)
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
            try:
                val = self._pvs[pvname].get()
            except ChannelAccessException:
                val = None
            if val is None:
                val = 0
            elif propty in ['Intlk-Mon', 'IntlkLtc-Mon'] or \
                    'Lower' in propty or 'Upper' in propty:
                val = 1 if val == 0 else 0
            values.append(val)
        return values

    def _callback_get_rate(self, pvname, value, **kws):
        if value is None:
            return
        if 'MONIT' in pvname:
            self._pv_monitrate_value = value
        elif 'FAcq' in pvname:
            self._pv_facqrate_value = value
        monit = self._pv_monitrate_value
        facq = self._pv_facqrate_value
        if None in [monit, facq]:
            return
        frac = monit/facq
        factor = 2**_math.ceil(_math.log2(frac)) / frac
        self._monitsum2intlksum_factor = factor
