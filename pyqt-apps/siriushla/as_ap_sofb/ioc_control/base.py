"""Define Controllers for the orbits displayed in the graphic."""

from functools import partial as _part
import numpy as _np
from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QWidget, QHBoxLayout, QSizePolicy, QComboBox, \
    QLabel, QVBoxLayout
from pydm.widgets import PyDMLabel, PyDMEnumComboBox
from pydm.widgets.base import PyDMPrimitiveWidget
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.sofb.csdev import SOFBFactory
from siriuspy.clientconfigdb import ConfigDBClient
from siriushla.widgets import SiriusSpinbox, PyDMStateButton, SiriusLedState
from siriushla.as_ap_configdb import LoadConfigDialog


class BaseWidget(QWidget):
    """."""

    def __init__(self, parent, prefix, acc='SI'):
        """."""
        super().__init__(parent)
        self.setObjectName(acc.upper()+'App')
        self.prefix = _PVName(prefix)
        self._csorb = SOFBFactory.create(acc)

    @property
    def acc(self):
        """."""
        return self._csorb.acc

    @property
    def acc_idx(self):
        """."""
        return self._csorb.acc_idx

    @property
    def isring(self):
        """."""
        return self._csorb.isring

    def create_pair(self, parent, pvname, prefix=None, is_vert=False):
        """."""
        prefix = prefix or self.prefix
        wid = QWidget(parent)
        if is_vert:
            lay = QVBoxLayout(wid)
        else:
            lay = QHBoxLayout(wid)
        lay.setContentsMargins(0, 0, 0, 0)
        pdm_spbx = SiriusSpinbox(wid, init_channel=prefix+pvname+'-SP')
        pdm_spbx.showStepExponent = False
        pdm_lbl = PyDMLabel(wid, init_channel=prefix+pvname+'-RB')
        pdm_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(pdm_spbx)
        lay.addWidget(pdm_lbl)
        wid.sp_wid = pdm_spbx
        wid.rb_wid = pdm_lbl
        return wid

    def create_pair_sel(self, parent, pvname, prefix=None, is_vert=False):
        """."""
        prefix = prefix or self.prefix
        wid = QWidget(parent)
        if is_vert:
            lay = QVBoxLayout(wid)
        else:
            lay = QHBoxLayout(wid)
        lay.setContentsMargins(0, 0, 0, 0)
        pdm_cbbx = PyDMEnumComboBox(
            wid, init_channel=prefix+pvname+'-Sel')
        pdm_lbl = PyDMLabel(wid, init_channel=prefix+pvname+'-Sts')
        pdm_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(pdm_cbbx)
        lay.addWidget(pdm_lbl)
        wid.sp_wid = pdm_cbbx
        wid.rb_wid = pdm_lbl
        return wid

    def create_pair_butled(self, parent, pvname, prefix=None, is_vert=False):
        """."""
        prefix = prefix or self.prefix
        wid = QWidget(parent)
        if is_vert:
            lay = QVBoxLayout(wid)
        else:
            lay = QHBoxLayout(wid)
        lay.setContentsMargins(0, 0, 0, 0)
        spnt = PyDMStateButton(
            wid, init_channel=prefix+pvname+'-Sel')
        rdb = SiriusLedState(wid, init_channel=prefix+pvname+'-Sts')
        lay.addWidget(spnt)
        lay.addWidget(rdb)
        wid.sp_wid = spnt
        wid.rb_wid = spnt
        return wid


class BaseCombo(QComboBox, PyDMPrimitiveWidget):
    """."""

    configname = Signal(str)

    def __init__(
            self, parent, ctrls, setpoint=None, readback=None, acc='SI'):
        """."""
        QComboBox.__init__(self, parent)
        PyDMPrimitiveWidget.__init__(self)
        self.setpoint = setpoint or dict()
        self.readback = readback or dict()
        self.ctrls = ctrls
        self._csorb = SOFBFactory.create(acc)
        self._config_type = acc.lower() + '_orbit'
        self._client = ConfigDBClient(config_type=self._config_type)
        self.orbits = {
            'x': _np.zeros(self._csorb.nr_bpms, dtype=float),
            'y': _np.zeros(self._csorb.nr_bpms, dtype=float)}
        self.signals_to_watch = dict()
        self.slots = {
            'x': _part(self._watch_if_changed, 'x'),
            'y': _part(self._watch_if_changed, 'y')}

        self.setup_ui()
        self.connect_signals()

    @property
    def acc(self):
        """."""
        return self._csorb.acc

    @property
    def acc_idx(self):
        """."""
        return self._csorb.acc_idx

    @property
    def isring(self):
        """."""
        return self._csorb.isring

    def channels(self):
        """."""
        chans = list(self.readback.values())
        chans += list(self.setpoint.values())
        return chans

    def connect_signals(self):
        """."""
        for pln in ('x', 'y'):
            self.readback[pln].new_value_signal[_np.ndarray].connect(
                _part(self.ioc_orbit_changed, pln))

    def setup_ui(self, add_items=None):
        """."""
        sz_pol = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setSizePolicy(sz_pol)
        add_items = add_items or []
        add_items.extend(['Zero', 'ServConf'])
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
        if not text.lower().startswith('servconf'):
            self.configname.emit('')
        if text.lower().startswith('zero'):
            for pln in ('x', 'y'):
                if self.orbits[pln] is not None:
                    self.orbits[pln] *= 0
                    self.setpoint[pln].send_value_signal[_np.ndarray].emit(
                        self.orbits[pln])
        elif text.lower().startswith('servconf'):
            win = LoadConfigDialog(self._config_type, self)
            confname, status = win.exec_()
            if not status:
                return
            data = self._client.get_config_value(confname)
            self.configname.emit(confname)
            for pln in ('x', 'y'):
                self.orbits[pln] = _np.array(data[pln])
                self.setpoint[pln].send_value_signal[_np.ndarray].emit(
                    self.orbits[pln])
        elif text in self.ctrls:
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
        """."""
        self._orbit_changed(pln, orb)

    def _watch_if_changed(self, pln, orb):
        self._orbit_changed(pln, orb)

    def _orbit_changed(self, pln, orb):
        myorb = self.orbits[pln]
        if myorb is not None and myorb.size == orb.size and \
                _np.allclose(orb, myorb, rtol=1e-7):
            return
        self.setCurrentIndex(self.count()-1)
        self.configname.emit('')


class CALabel(QLabel, PyDMPrimitiveWidget):
    """."""
