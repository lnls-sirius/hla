"""Define Controllers for the orbits displayed in the graphic."""

from functools import partial as _part
import numpy as _np
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QHBoxLayout, QSizePolicy, QComboBox
from pydm.widgets import PyDMLabel, PyDMEnumComboBox
from pydm.widgets.base import PyDMPrimitiveWidget
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.csdevice.orbitcorr import SOFBFactory
from siriushla.widgets import SiriusSpinbox


class BaseWidget(QWidget):

    def __init__(self, parent, prefix, acc='SI'):
        super().__init__(parent)
        self.setObjectName(acc.upper()+'App')
        self.prefix = _PVName(prefix)
        self._csorb = SOFBFactory.create(acc)

    @property
    def acc(self):
        return self._csorb.acc

    @property
    def acc_idx(self):
        return self._csorb.acc_idx

    @property
    def isring(self):
        return self._csorb.isring

    def create_pair(self, parent, pvname, prefix=None):
        prefix = prefix or self.prefix
        wid = QWidget(parent)
        hbl = QHBoxLayout(wid)
        hbl.setContentsMargins(0, 0, 0, 0)
        pdm_spbx = SiriusSpinbox(wid, init_channel=prefix+pvname+'-SP')
        pdm_spbx.showStepExponent = False
        pdm_lbl = PyDMLabel(wid, init_channel=prefix+pvname+'-RB')
        pdm_lbl.setAlignment(Qt.AlignCenter)
        hbl.addWidget(pdm_spbx)
        hbl.addWidget(pdm_lbl)
        return wid

    def create_pair_sel(self, parent, pvname, prefix=None):
        prefix = prefix or self.prefix
        wid = QWidget(parent)
        hbl = QHBoxLayout(wid)
        hbl.setContentsMargins(0, 0, 0, 0)
        pdm_cbbx = PyDMEnumComboBox(
            wid, init_channel=prefix+pvname+'-Sel')
        pdm_lbl = PyDMLabel(wid, init_channel=prefix+pvname+'-Sts')
        pdm_lbl.setAlignment(Qt.AlignCenter)
        hbl.addWidget(pdm_cbbx)
        hbl.addWidget(pdm_lbl)
        return wid


class BaseCombo(QComboBox, PyDMPrimitiveWidget):

    def __init__(self, parent, ctrls, setpoint=dict(),
                 readback=dict(), acc='SI'):
        QComboBox.__init__(self, parent)
        PyDMPrimitiveWidget.__init__(self)
        self.setpoint = setpoint
        self.readback = readback
        self.ctrls = ctrls
        self._csorb = SOFBFactory.create(acc)
        self.orbits = {
            'x': _np.zeros(self._csorb.NR_BPMS, dtype=float),
            'y': _np.zeros(self._csorb.NR_BPMS, dtype=float)}
        self.signals_to_watch = dict()
        self.slots = {
            'x': _part(self._watch_if_changed, 'x'),
            'y': _part(self._watch_if_changed, 'y')}

        self.setup_ui()
        self.connect_signals()

    @property
    def acc(self):
        return self._csorb.acc

    @property
    def acc_idx(self):
        return self._csorb.acc_idx

    @property
    def isring(self):
        return self._csorb.isring

    def channels(self):
        chans = list(self.readback.values())
        chans += list(self.setpoint.values())
        return chans

    def connect_signals(self):
        for pln in ('x', 'y'):
            self.readback[pln].new_value_signal[_np.ndarray].connect(
                _part(self.ioc_orbit_changed, pln))

    def setup_ui(self, add_items=[]):
        sz_pol = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setSizePolicy(sz_pol)
        self.setEditable(True)
        for item in add_items:
            self.addItem(item)
        for reg in sorted(self.ctrls.keys()):
            self.addItem(reg)
        self.addItem('Out of Date')
        self.setCurrentIndex(self.count()-1)
        self.activated.connect(self._item_selected)

    def _item_selected(self, index):
        text = self.itemText(index)
        self._selection_changed(text)

    def _selection_changed(self, text, sigs=None):
        sigs = sigs or dict()
        if text in self.ctrls:
            for pln in ('x', 'y'):
                orb = self.ctrls[text][pln]['getvalue']()
                if orb is None:
                    return
                self.orbits[pln] = orb
                sigs[pln] = self.ctrls[text][pln]['signal']
                self.setpoint[pln].send_value_signal[_np.ndarray].emit(
                    self.orbits[pln])
        for pln in ('x', 'y'):
            if self.signals_to_watch:
                self.signals_to_watch[pln].disconnect(self.slots[pln])
            if sigs:
                sigs[pln].connect(self.slots[pln])
        self.signals_to_watch = sigs

    def ioc_orbit_changed(self, pln, orb):
        self._orbit_changed(pln, orb)

    def _watch_if_changed(self, pln, orb):
        self._orbit_changed(pln, orb)

    def _orbit_changed(self, pln, orb):
        myorb = self.orbits[pln]
        if myorb is not None and _np.allclose(orb, myorb, rtol=1e-7):
            return
        self.setCurrentIndex(self.count()-1)
