"""Custom widgets."""

import numpy as _np

from qtpy.QtCore import Qt, Slot
from qtpy.QtWidgets import QComboBox, QSizePolicy as QSzPlcy, \
    QLabel, QGridLayout

import qtawesome as qta

from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.clientconfigdb import ConfigDBClient

from pydm.widgets import PyDMPushButton

from ..widgets import SiriusConnectionSignal as _ConnSignal, SiriusLedAlert, \
    SiriusDialog
from ..as_ap_configdb import LoadConfigDialog
from .base import BaseObject


class RefOrbComboBox(BaseObject, QComboBox):
    """Reference Orbit ComboBox."""

    def __init__(self, parent, device, prefix=''):
        BaseObject.__init__(self, device, prefix)
        QComboBox.__init__(self, parent)

        self._config_type = 'si_orbit'
        self._client = ConfigDBClient(config_type=self._config_type)

        self._ch_refx = _ConnSignal(
            self.devpref.substitute(propty='RefOrbX-SP'))
        self._ch_refy = _ConnSignal(
            self.devpref.substitute(propty='RefOrbY-SP'))
        self._refzero = dict()
        self._refzero['x'] = _np.zeros(self._csorb.nr_bpms, dtype=float)
        self._refzero['y'] = _np.zeros(self._csorb.nr_bpms, dtype=float)

        self.setSizePolicy(QSzPlcy.Expanding, QSzPlcy.Preferred)
        self.setMaxVisibleItems(10)
        self._choose_reforb = [
            'Zero', 'ref_orb', 'bba_orb', 'other...', 'Out of Date']
        for item in self._choose_reforb:
            self.addItem(item)
        self.setCurrentText('Out of Date')
        self.activated.connect(self._add_reforb_entry)

    @Slot(int)
    def _add_reforb_entry(self, index):
        text = self.itemText(index)
        if text == 'Out of Date':
            return
        if not text.startswith('other'):
            self._set_reforb(text)
            return
        win = LoadConfigDialog(self._config_type, self)
        confname, status = win.exec_()
        if not status:
            self.setCurrentIndex(0)
            return
        self.insertItem(index, confname)
        self.setCurrentIndex(index)
        self._set_reforb(confname)

    def _set_reforb(self, confname):
        if confname == 'Zero':
            data = self._refzero
        else:
            data = self._client.get_config_value(confname)
        self._ch_refx.send_value_signal[_np.ndarray].emit(_np.array(data['x']))
        self._ch_refy.send_value_signal[_np.ndarray].emit(_np.array(data['y']))


class StatusDialog(SiriusDialog):
    """Status Detail Dialog."""

    def __init__(self, parent, pvname, labels, cmds, title=''):
        super().__init__(parent)
        self.setObjectName('SIApp')
        self.pvname = _PVName(pvname)
        self.labels = labels
        self.cmds = cmds
        self.title = title

        lay = QGridLayout(self)

        label = QLabel(
            '<h4>'+self.title+'</h4>', self, alignment=Qt.AlignCenter)
        lay.addWidget(label, 0, 0, 1, 3)

        for idx, desc in enumerate(self.labels):
            led = SiriusLedAlert(self, self.pvname, bit=idx)
            lbl = QLabel(desc, self)
            lay.addWidget(led, idx+1, 0)
            lay.addWidget(lbl, idx+1, 1)

            if self.cmds[idx]:
                btn = PyDMPushButton(
                    self, icon=qta.icon('fa5s.sync'), pressValue=1,
                    init_channel=self.cmds[idx])
                btn.setObjectName('btn')
                btn.setStyleSheet(
                    '#btn{min-width:25px; max-width:25px; icon-size:20px;}')
                lay.addWidget(btn, idx+1, 2)
