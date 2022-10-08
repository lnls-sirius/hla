"""Custom widgets."""

import numpy as _np

from qtpy.QtCore import Qt, Slot
from qtpy.QtWidgets import QComboBox, QSizePolicy as QSzPlcy, \
    QLabel, QGridLayout, QWidget, QHBoxLayout, QPushButton, \
    QVBoxLayout, QGroupBox

import qtawesome as qta

from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.clientconfigdb import ConfigDBClient
from siriuspy.devices import Device
from siriuspy.diagbeam.bpm.csdev import Const as _csbpm

from pydm.widgets import PyDMPushButton

from siriushla.widgets.label import SiriusLabel
from siriushla.widgets.spinbox import SiriusSpinbox

from ..widgets import SiriusConnectionSignal as _ConnSignal, SiriusLedAlert, \
    SiriusDialog, PyDMLedMultiChannel
from ..as_ap_configdb import LoadConfigDialog
from .base import BaseObject
from .graphics import RefOrbViewWidget


class RefOrbWidget(BaseObject, QWidget):
    """Reference Orbit widget."""

    def __init__(self, parent, device, prefix=''):
        BaseObject.__init__(self, device, prefix)
        QWidget.__init__(self, parent)

        self._config_type = 'si_orbit'
        self._client = ConfigDBClient(config_type=self._config_type)

        self._refzero = dict()
        self._refzero['x'] = _np.zeros(self._csorb.nr_bpms, dtype=float)
        self._refzero['y'] = _np.zeros(self._csorb.nr_bpms, dtype=float)
        self._refx = _np.zeros(self._csorb.nr_bpms, dtype=float)
        self._refy = _np.zeros(self._csorb.nr_bpms, dtype=float)

        self._ch_refx = _ConnSignal(
            self.devpref.substitute(propty='RefOrbX-SP'))
        self._ch_refy = _ConnSignal(
            self.devpref.substitute(propty='RefOrbY-SP'))
        sofb_prefix = _PVName('SI-Glob:AP-SOFB').substitute(prefix=self.prefix)
        self._ch_sofb_orbx = _ConnSignal(
            sofb_prefix.substitute(propty='SlowOrbX-Mon'))
        self._ch_sofb_orby = _ConnSignal(
            sofb_prefix.substitute(propty='SlowOrbY-Mon'))
        self._ch_sofb_refx = _ConnSignal(
            sofb_prefix.substitute(propty='RefOrbX-RB'))
        self._ch_sofb_refy = _ConnSignal(
            sofb_prefix.substitute(propty='RefOrbY-RB'))

        self._setupUi()

    def _setupUi(self):
        lbl_read = QLabel(
            'Get from: ', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.read = QComboBox()
        self.read.setSizePolicy(QSzPlcy.Expanding, QSzPlcy.Preferred)
        self.read.setMaxVisibleItems(10)
        self._choose_reforb = [
            'Zero', 'SOFB SlowOrb', 'SOFB RefOrb',
            'ref_orb', 'bba_orb', 'other...',
            'Out of Date']
        for item in self._choose_reforb:
            self.read.addItem(item)
        self.read.setCurrentText('Out of Date')
        self.read.activated.connect(self._add_reforb_entry)

        self.graph = RefOrbViewWidget(self, self.device, self.prefix)
        self.viewgraph = QPushButton(self)
        self.viewgraph.setIcon(qta.icon('mdi.chart-line'))
        self.viewgraph.setObjectName('btn')
        self.viewgraph.setStyleSheet('#btn{max-width:25px; icon-size:25px;}')
        self.viewgraph.clicked.connect(self.graph.show)

        self.write = QPushButton('Send', self)
        self.write.clicked.connect(self._send_new_value)

        lay = QGridLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(lbl_read, 0, 0)
        lay.addWidget(self.read, 0, 1)
        lay.addWidget(self.viewgraph, 0, 2)
        lay.addWidget(self.write, 1, 1)

    @Slot(int)
    def _add_reforb_entry(self, index):
        text = self.read.itemText(index)
        if text == 'Out of Date':
            return
        if not text.startswith('other'):
            self._update_new_value(text)
            return
        win = LoadConfigDialog(self._config_type, self)
        confname, status = win.exec_()
        if not status:
            self.read.setCurrentText('Out of Date')
            return
        self.read.insertItem(index, confname)
        self.read.setCurrentIndex(index)
        self._update_new_value(confname)

    def _update_new_value(self, text):
        if text == 'Zero':
            refx, refy = self._refzero['x'], self._refzero['y']
        elif text == 'SOFB SlowOrb':
            refx = self._ch_sofb_orbx.value
            refy = self._ch_sofb_orby.value
        elif text == 'SOFB RefOrb':
            refx = self._ch_sofb_refx.value
            refy = self._ch_sofb_refy.value
        else:
            data = self._client.get_config_value(text)
            refx, refy = data['x'], data['y']
        if refx is None or refy is None or \
                _np.asarray(refx).size != self._csorb.nr_bpms or \
                _np.asarray(refy).size != self._csorb.nr_bpms:
            self.read.setCurrentText('Out of Date')
            return

        self._refx = _np.asarray(refx)
        self._refy = _np.asarray(refy)
        self.graph.update_new_value_curves(self._refx, self._refy)

    def _send_new_value(self):
        self._ch_refx.send_value_signal[_np.ndarray].emit(self._refx)
        self._ch_refy.send_value_signal[_np.ndarray].emit(self._refy)


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
                btn.setDefault(False)
                btn.setAutoDefault(False)
                btn.setObjectName('btn')
                btn.setStyleSheet(
                    '#btn{min-width:25px; max-width:25px; icon-size:20px;}')
                lay.addWidget(btn, idx+1, 2)


class BPMSwModeWidget(BaseObject, QWidget):
    """Auxiliary BPM switching control widget."""

    def __init__(self, parent, device, prefix=''):
        BaseObject.__init__(self, device, prefix)
        QWidget.__init__(self, parent)
        bnames = self._csorb.bpm_names
        props = ['SwMode-Sel', ]
        self._bpm_devs = [Device(b, props, auto_mon=True) for b in bnames]
        self._setupUi()
        self._init = False
        self._pv_init = self._bpm_devs[0].pv_object('SwMode-Sel')
        self._pv_init.connection_callbacks.append(self._set_initial_value)

    def _setupUi(self):
        lbl = QLabel(
            'SwMode: ', self, alignment=Qt.AlignRight | Qt.AlignVCenter)

        self.sel = QComboBox(self)
        self.sel.addItems(['switching', 'direct'])

        self.sts = PyDMLedMultiChannel(self)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(lbl)
        lay.addWidget(self.sel)
        lay.addWidget(self.sts)

    def _set_swithing_mode(self, text):
        mode = _csbpm.SwModes._fields.index(text)
        for dev in self._bpm_devs:
            dev['SwMode-Sel'] = mode
        ch2vals = {
            bpm+':SwMode-Sts': mode for bpm in self._csorb.bpm_names}
        self.sts.set_channels2values(ch2vals)

    def _set_initial_value(self, conn, **kws):
        if conn and not self._init:
            self._init = True

            if self._pv_init.wait_for_connection(1):
                value = self._pv_init.value
                mode = _csbpm.SwModes._fields[value]
            else:
                mode = 'switching'
                value = _csbpm.SwModes._fields.index(mode)

            ch2vals = {
                bpm+':SwMode-Sts': value for bpm in self._csorb.bpm_names}
            self.sts.set_channels2values(ch2vals)

            self.sel.setCurrentText(mode)
            self.sel.currentTextChanged.connect(self._set_swithing_mode)


class AuxCommDialog(BaseObject, SiriusDialog):
    """Auxiliary command dialog."""

    def __init__(self, parent, device, prefix=''):
        BaseObject.__init__(self, device, prefix)
        SiriusDialog.__init__(self, parent)
        self.setObjectName('SIApp')
        self.setWindowTitle('SI - FOFB - Auxiliary Commands')
        self._setupUi()
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        group2cmd = {
            'Correctors': {
                'Set all current to zero': 'CorrSetCurrZero-Cmd',
                'Clear all Acc': 'CorrSetAccClear-Cmd',
                # 'Set all OpMode to Manual': 'CorrSetOpModeManual-Cmd',
                # 'Set all AccFreeze to Enbl': 'CorrSetAccFreezeEnbl-Cmd',
                # 'Set all AccFreeze to Dsbl': 'CorrSetAccFreezeDsbl-Cmd',
            },
            'Controllers': {
                'Sync Net': 'FOFBCtrlSyncNet-Cmd',
                'Sync RefOrb': 'FOFBCtrlSyncRefOrb-Cmd',
                'Configure TimeFrameLength': 'FOFBCtrlConfTFrameLen-Cmd',
            },
            'BPMs': {
                'Configure BPM Log.Trigs.': 'FOFBCtrlConfBPMLogTrg-Cmd',
            },
        }
        lay = QVBoxLayout(self)
        for group, commands in group2cmd.items():
            gbox = QGroupBox(group)
            glay = QVBoxLayout(gbox)

            if 'Corr' in group:
                lbl = QLabel(
                    'Sat. Limit (A): ', self,
                    alignment=Qt.AlignRight | Qt.AlignVCenter)
                pref = self.devpref
                spw = SiriusSpinbox(
                    self, pref.substitute(propty='CorrAccSatMax-SP'))
                spw.showStepExponent = False
                rbw = SiriusLabel(
                    self, pref.substitute(propty='CorrAccSatMax-RB'))
                hlay = QHBoxLayout()
                hlay.setContentsMargins(0, 0, 0, 0)
                hlay.addWidget(lbl)
                hlay.addWidget(spw)
                hlay.addWidget(rbw)
                glay.addLayout(hlay)
            elif 'BPM' in group:
                swbpm = BPMSwModeWidget(self, self.device, self.prefix)
                glay.addWidget(swbpm)

            for desc, cmd in commands.items():
                btn = PyDMPushButton(
                    self, label=desc, pressValue=1,
                    init_channel=self.devpref.substitute(propty=cmd))
                btn.setDefault(False)
                btn.setAutoDefault(False)
                glay.addWidget(btn)
            lay.addWidget(gbox)
