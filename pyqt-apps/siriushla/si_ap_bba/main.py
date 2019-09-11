"""Main module."""

from copy import deepcopy as _dcopy
import numpy as np

from qtpy.QtCore import QObject, QThread

from siriuspy.csdevice.orbitcorr import SOFBFactory
from siriuspy.namesys import SiriusPVName as _PVName
from .models import BPM, Corr, Quad, Orbit


class DoBBA(QObject):
    ORBIT = 0
    TRAJ = 1

    def __init__(self, bpms_dict=dict(), method=None):
        super().__init__()
        self.bpms_dict = bpms_dict
        self.method = method if method is not None else 0

    @property
    def bpms_dict(self):
        return _dcopy(self.bpms_dict)

    @bpms_dict.setter
    def bpms_dict(self, value):
        value = self._check_consistency(value)
        if value:
            self.bpms_dict = value
            self.bpms_order = sorted(value.keys())

    def _check_consistency(self, value):
        val = dict()
        for name, data in value.items():
            name = _PVName(name)
            dta = _dcopy(data)
            if {'quad', 'corr'} - data.keys():
                return False
            dta['quad'] = _PVName(dta['quad'])
            dta['corr'] = _PVName(dta['corr'])
            val[name] = dta
        return val

    def start(self):
        self.connect_to_objects()
        self.do_bba()

    def connect_to_objects(self):
        self._bpms = dict()
        self._quads = dict()
        self._corrs = dict()
        for bpm, data in self.bpms_dict.items():
            self._bpms[bpm] = BPM(bpm)
            self._quads[data['quad']] = Quad(data['quad'])
            self._corrs[data['corr']] = Corr(data['corr'])
        self._orbit = Orbit()

    def do_bba(self):
        for bpm, data in self.bpms_dict.items():
            quad = data['quad']
            corr = data['corr']
            plane = data['plane']
            self._dobba_single_bpm(bpm, quad, corr, plane)

    def _dobba_single_bpm(self, bpm, quad, corr, plane):
        quad = self._quads[quad]
        bpm = self._bpms[bpm]
        corr = self._corrs[corr]
