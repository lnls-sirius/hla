"""Custom widgets."""

import time as _time
from functools import partial as _part
import numpy as _np

from qtpy.QtCore import Qt, Slot
from qtpy.QtGui import QColor, QPalette
from qtpy.QtWidgets import QComboBox, QSizePolicy as QSzPlcy, \
    QLabel, QGridLayout, QWidget, QHBoxLayout, QPushButton, \
    QVBoxLayout, QTabWidget, QCheckBox, QScrollArea

import qtawesome as qta
from matplotlib import cm

from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.clientconfigdb import ConfigDBClient
from siriuspy.devices import Device, FOFBCtrlDCC, FamFOFBControllers
from siriuspy.diagbeam.bpm.csdev import Const as _csbpm

from pydm.widgets import PyDMPushButton

from ..util import connect_window
from ..widgets import SiriusConnectionSignal as _ConnSignal, SiriusLedAlert, \
    SiriusDialog, PyDMLedMultiChannel, SiriusLabel, PyDMLed, SiriusLedState
from ..widgets.windows import create_window_from_widget
from ..as_ap_configdb import LoadConfigDialog
from ..as_di_bpms.triggers import LogicalTriggers
from ..as_ap_sofb.graphics.base import Graph
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
        self._ch_syncref = _ConnSignal(
            self.devpref.substitute(propty='CtrlrSyncRefOrb-Cmd'))

        sofb_prefix = _PVName('SI-Glob:AP-SOFB').substitute(prefix=self.prefix)
        self._ch_sofb_orbx = _ConnSignal(
            sofb_prefix.substitute(propty='SlowOrbX-Mon'))
        self._ch_sofb_orbx.new_value_signal[_np.ndarray].connect(
            _part(self._watch_if_changed, 'x', 'SOFB SlowOrb'))
        self._ch_sofb_orbx.new_value_signal[float].connect(
            _part(self._watch_if_changed, 'x', 'SOFB SlowOrb'))
        self._ch_sofb_orby = _ConnSignal(
            sofb_prefix.substitute(propty='SlowOrbY-Mon'))
        self._ch_sofb_orby.new_value_signal[_np.ndarray].connect(
            _part(self._watch_if_changed, 'y', 'SOFB SlowOrb'))
        self._ch_sofb_orby.new_value_signal[float].connect(
            _part(self._watch_if_changed, 'y', 'SOFB SlowOrb'))
        self._ch_sofb_refx = _ConnSignal(
            sofb_prefix.substitute(propty='RefOrbX-RB'))
        self._ch_sofb_refx.new_value_signal[_np.ndarray].connect(
            _part(self._watch_if_changed, 'x', 'SOFB RefOrb'))
        self._ch_sofb_refy = _ConnSignal(
            sofb_prefix.substitute(propty='RefOrbY-RB'))
        self._ch_sofb_refy.new_value_signal[_np.ndarray].connect(
            _part(self._watch_if_changed, 'y', 'SOFB RefOrb'))

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
        _time.sleep(0.05)
        self._ch_syncref.send_value_signal[int].emit(1)

    def _watch_if_changed(self, plane, orb, value):
        myvalue = getattr(self, '_ref' + plane)
        if orb != self.read.currentText():
            return
        if myvalue is not None and myvalue.size == value.size and \
                _np.allclose(value, myvalue, rtol=1e-7):
            return
        self.read.setCurrentIndex(self.read.count()-1)


class StatusDialog(SiriusDialog):
    """Status Detail Dialog."""

    def __init__(
            self, parent, pvname, labels, cmds, title='', detail_button=None):
        super().__init__(parent)
        self.setObjectName('SIApp')
        self.pvname = _PVName(pvname)
        self.labels = labels
        self.cmds = cmds
        self.title = title
        self.detail_button = detail_button

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

        if self.detail_button is not None:
            lay.addWidget(
                self.detail_button, len(self.labels)+1, 1,
                alignment=Qt.AlignCenter)


class BPMSwModeWidget(BaseObject, QWidget):
    """Auxiliary BPM switching control widget."""

    def __init__(self, parent, device, prefix=''):
        BaseObject.__init__(self, device, prefix)
        QWidget.__init__(self, parent)
        props = ['SwMode-Sel', ]
        self._bpm_devs = [
            Device(b, props, auto_mon=True) for b in self._csorb.bpm_names]
        self._setupUi()
        self._init_dict = {}
        self._init = False
        self._pv_objs = list()
        for dev in self._bpm_devs:
            pvo = dev.pv_object('SwMode-Sel')
            pvo.add_callback(self._set_initial_value)
            pvo.add_callback(self._update_current_value)
            if pvo.connected:
                self._set_initial_value(pvo.pvname, pvo.value)
            self._pv_objs.append(pvo)

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

    def _set_swithing_mode(self, text, do_sp=True):
        mode = _csbpm.SwModes._fields.index(text)
        if do_sp:
            for dev in self._bpm_devs:
                dev['SwMode-Sel'] = mode
        else:
            self.blockSignals(True)
            self.sel.setCurrentText(text)
            self.blockSignals(False)

        ch2vals = dict()
        for bpm in self._csorb.bpm_names:
            pvn = _PVName(bpm).substitute(
                prefix=self.prefix, propty='SwMode-Sts')
            ch2vals[pvn] = mode
        self.sts.set_channels2values(ch2vals)

    def _set_initial_value(self, pvname, value, **kws):
        if value is not None:
            self._init_dict[pvname] = value

        if self._init or len(self._init_dict) < len(self._bpm_devs):
            return

        self._init = True

        vals, cnts = _np.unique(
            list(self._init_dict.values()), return_counts=True)
        value = vals[_np.argmax(cnts)]
        mode = _csbpm.SwModes._fields[value]

        ch2vals = dict()
        for bpm in self._csorb.bpm_names:
            pvn = _PVName(bpm).substitute(
                prefix=self.prefix, propty='SwMode-Sts')
            ch2vals[pvn] = value
        self.sts.set_channels2values(ch2vals)

        self.sel.setCurrentText(mode)
        self.sel.currentTextChanged.connect(self._set_swithing_mode)

    def _update_current_value(self, value, **kws):
        if not self._init:
            return
        if not _np.all([pvo.value == value for pvo in self._pv_objs]):
            return
        mode = _csbpm.SwModes._fields[value]
        self._set_swithing_mode(mode, do_sp=False)


class ControllersDetailDialog(BaseObject, SiriusDialog):
    """Controllers detail dialog."""

    def __init__(self, parent, device, prefix=''):
        BaseObject.__init__(self, device, prefix)
        SiriusDialog.__init__(self, parent)
        self.setObjectName('SIApp')
        self.setWindowTitle('SI - FOFB - Controllers Details Dialog')

        self.ctrlrs = FOFBCtrlDCC.DEVICES
        ctrlr_offset = FamFOFBControllers.FOFBCTRL_BPMID_OFFSET
        self.dccnames, self.dccids = list(), list()
        for dcc in FOFBCtrlDCC.PROPDEVICES.ALL:
            for ctrl in self.ctrlrs:
                bid = ctrlr_offset - 1 + int(ctrl[3:5])
                self.dccnames.append(ctrl+':'+dcc)
                self.dccids.append(bid)
        for idx, bpm in enumerate(self._csorb.bpm_names):
            self.dccnames.append(bpm+':DCCP2P')
            bid = ((idx + 1) // 2) * 2 % 160
            self.dccids.append(bid)

        self._setupUi()

        self._ch_synenls = _ConnSignal(
            self.devpref.substitute(propty='CtrlrSyncEnblList-Mon'))
        self._ch_synenls.new_value_signal[_np.ndarray].connect(
            self._update_dcc_enbllist)
        self._ch_synenls.new_value_signal[_np.ndarray].connect(
            self._update_refpacketloss)

        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        tab = QTabWidget(self)
        tab.setObjectName('SITab')
        tab.addTab(self._setupBPMIdsTab(), 'DCC BPM Ids')
        tab.addTab(self._setupNetSyncTab(), 'Net Sync Status')
        tab.addTab(self._setupLinkPartnerTab(), 'DCC Linked Partners')
        tab.addTab(self._setupRefOrbTab(), 'RefOrb Sync Status')
        tab.addTab(self._setupTimeFrameLenTab(), 'DCC TimeFrameLen')
        tab.addTab(self._setupBPMLogTrigTab(), 'BPM Logical Trigger Configs')
        tab.addTab(self._setupOrbDistTab(), 'Orbit Distortion Detection')
        tab.addTab(self._setupPacketLossTab(), 'Packet Loss Detection')
        tab.addTab(self._setupIntlkTab(), 'Loop Interlock')

        lay = QVBoxLayout(self)
        lay.addWidget(tab)

        self.setStyleSheet('SiriusLabel{qproperty-alignment: AlignCenter;}')

    def _setupBPMIdsTab(self):
        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setSpacing(1)
        lay.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # header
        lay.addWidget(
            QLabel('<h4>Device</h4>', self, alignment=Qt.AlignCenter), 0, 0)
        lay.addWidget(
            QLabel('<h4>BPMId</h4>', self, alignment=Qt.AlignCenter), 0, 1)

        # table
        for idx, dcc in enumerate(self.dccnames):
            row = idx + 1
            lbl = QLabel(dcc, self, alignment=Qt.AlignCenter)
            pvn = _PVName(dcc).substitute(prefix=self.prefix) + 'BPMId-RB'
            plb = SiriusLabel(self, pvn)
            led = PyDMLedMultiChannel(self, {pvn: self.dccids[idx]})
            lay.addWidget(lbl, row, 0)
            lay.addWidget(plb, row, 1)
            lay.addWidget(led, row, 2)

        return self._build_scroll_area(wid)

    def _setupNetSyncTab(self):
        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setSpacing(1)
        lay.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # header
        lay.addWidget(
            QLabel('<h4>Device</h4>', self, alignment=Qt.AlignCenter), 0, 0)
        lay.addWidget(
            QLabel('<h4>BPM Count</h4>', self, alignment=Qt.AlignCenter), 0, 1)
        lay.addWidget(
            QLabel('<h4>Enable</h4>', self, alignment=Qt.AlignCenter), 0, 2)

        # table
        self.leds_sync, self.leds_dccsts = dict(), dict()
        for idx, dcc in enumerate(self.dccnames):
            row = idx + 1
            lbl = QLabel(dcc, self, alignment=Qt.AlignCenter)
            pvn = _PVName(dcc).substitute(prefix=self.prefix) + 'BPMCnt-Mon'
            plb = SiriusLabel(self, pvn)
            lay.addWidget(lbl, row, 0)
            lay.addWidget(plb, row, 1)

            pvn = _PVName(dcc).substitute(prefix=self.prefix) + 'CCEnable-RB'
            led = PyDMLed(self, pvn)
            led.setObjectName('led_status')
            led.shape = led.ShapeMap.Square
            if 'FOFBCtrl' in dcc:
                led.offColor = led.Red
            self.leds_dccsts[dcc] = led
            lay.addWidget(led, row, 2, alignment=Qt.AlignTop)

            if 'FMC' in dcc:
                c2v = {pvn: FOFBCtrlDCC.DEF_FMC_BPMCNT}
                led = PyDMLedMultiChannel(self, c2v)
                self.leds_sync[dcc] = led
                lay.addWidget(led, row, 3)

        return self._build_scroll_area(wid)

    def _update_dcc_enbllist(self, value):
        for dcc, led in self.leds_sync.items():
            pvn = _PVName(dcc).substitute(prefix=self.prefix) + 'BPMCnt-Mon'
            c2v = {pvn: int(_np.sum(value))}
            led.set_channels2values(c2v)
        for idx, bpm in enumerate(self._csorb.bpm_names):
            led = self.leds_dccsts[bpm+':DCCP2P']
            if value[idx]:
                led.offColor = led.Red
                led.onColor = led.LightGreen
            else:
                led.offColor = led.DarkGreen
                led.onColor = led.Red

    def _setupLinkPartnerTab(self):
        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setSpacing(1)
        lay.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        lpart_pvs = [
            'BPMId-RB', 'LinkPartnerCH0-Mon', 'LinkPartnerCH1-Mon',
            'LinkPartnerCH2-Mon', 'LinkPartnerCH3-Mon']

        # header
        lay.addWidget(
            QLabel('<h4>Device</h4>', self, alignment=Qt.AlignCenter), 0, 0)
        for idx, link in enumerate(lpart_pvs):
            col = idx + 1
            text = '<h4>' + link.split('-')[0] + '</h4>'
            lbl = QLabel(text, self, alignment=Qt.AlignCenter)
            lay.addWidget(lbl, 0, col)

        # table
        row = 1
        for dcc in self.dccnames:
            if 'FMC' not in dcc:
                continue
            lbl = QLabel(dcc, self, alignment=Qt.AlignCenter)
            lay.addWidget(lbl, row, 0)
            for idx, link in enumerate(lpart_pvs):
                col = idx + 1
                pvn = _PVName(dcc).substitute(prefix=self.prefix) + link
                plb = SiriusLabel(self, pvn)
                lay.addWidget(plb, row, col)
            row += 1

        return self._build_scroll_area(wid)

    def _setupRefOrbTab(self):
        self._refimpl = _np.zeros(2*self._csorb.nr_bpms)
        self._ch_refx = _ConnSignal(
            self.devpref.substitute(propty='RefOrbHwX-Mon'))
        self._ch_refx.new_value_signal[_np.ndarray].connect(
            _part(self._update_reforb, 'x'))
        self._ch_refy = _ConnSignal(
            self.devpref.substitute(propty='RefOrbHwY-Mon'))
        self._ch_refy.new_value_signal[_np.ndarray].connect(
            _part(self._update_reforb, 'y'))

        # title
        title = QLabel(
            '<h4>Reference Orbit [X, Y] in Hardware Units [nm]</h4>', self,
            alignment=Qt.AlignCenter)

        # graph
        self.graph_ref = Graph(self)
        self.graph_ref.showLegend = False

        opts = dict(
            y_channel='', name='HL RefOrb',
            color='black', redraw_mode=2,
            lineStyle=1, lineWidth=2,
            symbol='o', symbolSize=10)
        self.graph_ref.addChannel(**opts)
        self.curve_hlref = self.graph_ref.curveAtIndex(0)

        c2v = dict()
        visisel = list()
        colors = cm.jet(_np.linspace(0, 1, len(self.ctrlrs)))*255
        for ctrl, color in zip(self.ctrlrs, colors):
            pvn = _PVName(ctrl).substitute(
                prefix=self.prefix, propty='RefOrb-RB')
            coloro = QColor(*color)

            c2v[pvn] = self._refimpl

            opts = dict(
                y_channel=pvn, name='',
                color=coloro, redraw_mode=2,
                lineStyle=1, lineWidth=2,
                symbol='o', symbolSize=10)
            self.graph_ref.addChannel(**opts)
            curve = self.graph_ref.curveAtIndex(-1)

            cbx = QCheckBox(ctrl[3:5], self)
            cbx.setChecked(True)
            cbx.stateChanged.connect(curve.setVisible)
            cbx.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Maximum)
            pal = cbx.palette()
            pal.setColor(QPalette.Base, coloro)
            pal.setColor(QPalette.Text, Qt.white)
            cbx.setPalette(pal)
            visisel.append(cbx)

        # led
        self.led_ref = PyDMLedMultiChannel(self, c2v)

        # curves
        lay_sel = QGridLayout()
        lay_sel.setContentsMargins(0, 0, 0, 0)
        colsel = 2
        for idx, cbx in enumerate(visisel):
            lay_sel.addWidget(cbx, idx // colsel, idx % colsel)

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.addWidget(title, 0, 0)
        lay.addWidget(self.led_ref, 0, 1, alignment=Qt.AlignRight)
        lay.addWidget(self.graph_ref, 1, 0)
        lay.addLayout(lay_sel, 1, 1)
        return wid

    def _update_reforb(self, plane, value):
        if plane == 'x':
            self._refimpl[:self._csorb.nr_bpms] = value
        else:
            self._refimpl[self._csorb.nr_bpms:] = value
        self.curve_hlref.receiveYWaveform(self._refimpl)

        c2v = {
            _PVName(ctrl).substitute(
                prefix=self.prefix, propty='RefOrb-RB'): self._refimpl
            for ctrl in self.ctrlrs}
        self.led_ref.set_channels2values(c2v)

    def _setupTimeFrameLenTab(self):
        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setSpacing(1)
        lay.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # header
        lay.addWidget(
            QLabel('<h4>Device</h4>', self, alignment=Qt.AlignCenter), 0, 0)
        lay.addWidget(
            QLabel('<h4>TimeFrameLen</h4>', self, alignment=Qt.AlignCenter),
            0, 1)

        # table
        self._led_timeframelen = dict()
        for idx, dcc in enumerate(self.dccnames):
            row = idx + 1
            lbl = QLabel(dcc, self, alignment=Qt.AlignCenter)
            pvn = _PVName(dcc).substitute(prefix=self.prefix)
            pvn += 'TimeFrameLen-RB'
            plb = SiriusLabel(self, pvn)
            led = PyDMLedMultiChannel(self)
            self._led_timeframelen[pvn] = led
            lay.addWidget(lbl, row, 0)
            lay.addWidget(plb, row, 1)
            lay.addWidget(led, row, 2)

        self._ch_tfl = _ConnSignal(
            self.devpref.substitute(propty='TimeFrameLen-RB'))
        self._ch_tfl.new_value_signal[int].connect(
            self._update_reftimeframelen)

        return self._build_scroll_area(wid)

    def _update_reftimeframelen(self, value):
        for pvn, led in self._led_timeframelen.items():
            led.set_channels2values({pvn: value})

    def _setupOrbDistTab(self):
        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setSpacing(1)
        lay.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # header
        lay.addWidget(
            QLabel('<h4>Device</h4>', self, alignment=Qt.AlignCenter), 0, 0)
        lay.addWidget(
            QLabel('<h4>Threshold</h4>', self, alignment=Qt.AlignCenter), 0, 1)
        lay.addWidget(
            QLabel('<h4>Enable</h4>', self, alignment=Qt.AlignCenter), 0, 2)

        # table
        self.leds_odd = dict()
        for idx, ctl in enumerate(self.ctrlrs):
            row = idx + 1
            c2v = dict()

            lbl = QLabel(ctl, self, alignment=Qt.AlignCenter)
            pvn = _PVName(ctl).substitute(
                prefix=self.prefix, propty='MaxOrbDistortion-RB')
            c2v[pvn] = 0
            plb = SiriusLabel(self, pvn)
            lay.addWidget(lbl, row, 0)
            lay.addWidget(plb, row, 1)

            pvn = _PVName(ctl).substitute(
                prefix=self.prefix, propty='MaxOrbDistortionEnbl-Sts')
            c2v[pvn] = 0
            led = SiriusLedState(self, pvn)
            led.setObjectName('led_status')
            led.shape = led.ShapeMap.Square
            lay.addWidget(led, row, 2, alignment=Qt.AlignTop)

            led = PyDMLedMultiChannel(self, c2v)
            self.leds_odd[ctl] = led
            lay.addWidget(led, row, 3)

        self._ch_odt = _ConnSignal(
            self.devpref.substitute(propty='LoopMaxOrbDistortion-RB'))
        self._ch_odt.new_value_signal[float].connect(
            self._update_reforbdist)
        self._ch_odd = _ConnSignal(
            self.devpref.substitute(propty='LoopMaxOrbDistortionEnbl-Sts'))
        self._ch_odd.new_value_signal[int].connect(
            self._update_reforbdist)

        return self._build_scroll_area(wid)

    def _update_reforbdist(self, _):
        odt = self._ch_odt.value
        odd = self._ch_odd.value
        if odt is None or odd is None:
            return
        odt = int(odt*self.UM2NM)
        for ctl, led in self.leds_odd.items():
            pref = _PVName(ctl).substitute(prefix=self.prefix)
            c2v = {
                pref.substitute(propty='MaxOrbDistortion-RB'): odt,
                pref.substitute(propty='MaxOrbDistortionEnbl-Sts'): odd,
            }
            led.set_channels2values(c2v)

    def _setupPacketLossTab(self):
        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setSpacing(1)
        lay.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # header
        lay.addWidget(
            QLabel('<h4>Device</h4>', self, alignment=Qt.AlignCenter), 0, 0)
        lay.addWidget(
            QLabel('<h4>MinBPMCount</h4>', self, alignment=Qt.AlignCenter), 0, 1)
        lay.addWidget(
            QLabel('<h4>Enable</h4>', self, alignment=Qt.AlignCenter), 0, 2)

        # table
        self.leds_pld = dict()
        for idx, ctl in enumerate(self.ctrlrs):
            row = idx + 1
            c2v = dict()

            lbl = QLabel(ctl, self, alignment=Qt.AlignCenter)
            pvn = _PVName(ctl).substitute(
                prefix=self.prefix, propty='MinBPMCnt-RB')
            c2v[pvn] = 0
            plb = SiriusLabel(self, pvn)
            lay.addWidget(lbl, row, 0)
            lay.addWidget(plb, row, 1)

            pvn = _PVName(ctl).substitute(
                prefix=self.prefix, propty='MinBPMCntEnbl-Sts')
            c2v[pvn] = 0
            led = SiriusLedState(self, pvn)
            led.setObjectName('led_status')
            led.shape = led.ShapeMap.Square
            lay.addWidget(led, row, 2, alignment=Qt.AlignTop)

            led = PyDMLedMultiChannel(self, c2v)
            self.leds_pld[ctl] = led
            lay.addWidget(led, row, 3)

        self._ch_ple = _ConnSignal(
            self.devpref.substitute(propty='LoopPacketLossDetecEnbl-Sts'))
        self._ch_ple.new_value_signal[int].connect(
            self._update_refpacketloss)

        return self._build_scroll_area(wid)

    def _update_refpacketloss(self, _):
        plc = self._ch_synenls.value
        ple = self._ch_ple.value
        if plc is None or ple is None:
            return
        plc = int(_np.sum(plc))
        for ctl, led in self.leds_pld.items():
            pref = _PVName(ctl).substitute(prefix=self.prefix)
            c2v = {
                pref.substitute(propty='MinBPMCnt-RB'): plc,
                pref.substitute(propty='MinBPMCntEnbl-Sts'): ple,
            }
            led.set_channels2values(c2v)

    def _setupIntlkTab(self):
        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setSpacing(1)
        lay.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # header
        lay.addWidget(
            QLabel('<h4>Device</h4>', self, alignment=Qt.AlignCenter), 0, 0)
        lay.addWidget(
            QLabel('<h4>Interlock</h4>', self, alignment=Qt.AlignCenter), 0, 1)

        # table
        for idx, dcc in enumerate(self.ctrlrs):
            row = idx + 1
            lbl = QLabel(dcc, self, alignment=Qt.AlignCenter)
            lay.addWidget(lbl, row, 0)
            pvn = _PVName(dcc).substitute(
                prefix=self.prefix, propty='LoopIntlk-Mon')
            led = SiriusLedAlert(self, pvn)
            led.setObjectName('led_status')
            lay.addWidget(led, row, 1, alignment=Qt.AlignTop)

        return self._build_scroll_area(wid)

    def _setupBPMLogTrigTab(self):
        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setSpacing(1)
        lay.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        triggers = FamFOFBControllers.BPM_TRIGS_IDS
        propties = ['RcvSrc-Sts', 'RcvInSel-RB']

        # header
        devlbl = QLabel('<h4>BPM</h4>', self, alignment=Qt.AlignCenter)
        lay.addWidget(devlbl, 0, 0, 2, 1)
        for idx1, trigid in enumerate(triggers):
            text = f'<h4>TRIGGER {trigid}</h4>'
            lbl = QLabel(text, self, alignment=Qt.AlignCenter)
            lay.addWidget(lbl, 0, idx1*2+1, 1, 2)
            for idx2, prop in enumerate(propties):
                text = prop.split('-')[0]
                lbl = QLabel(text, self, alignment=Qt.AlignCenter)
                lay.addWidget(lbl, 1, idx1*2+1+idx2)

        # table
        for idxr, bpm in enumerate(self._csorb.bpm_names):
            row = idxr + 2
            btn = QPushButton(qta.icon('fa5s.ellipsis-h'), '', self)
            btn.setObjectName('btn')
            btn.setStyleSheet(
                '#btn{min-width:25px; max-width:25px; icon-size:20px;}')
            btn.setDefault(False)
            btn.setAutoDefault(False)
            win = create_window_from_widget(
                LogicalTriggers, title=bpm+': ACQ Logical Triggers')
            connect_window(btn, win, parent=self, prefix=self.prefix, bpm=bpm)
            lbl = QLabel(bpm, self, alignment=Qt.AlignCenter)
            lbl.setObjectName('lbl_bpmname')
            hwid = QWidget()
            hwid.setObjectName('wid')
            hwid.setStyleSheet('#wid{border: 1px solid gray;}')
            hlay = QHBoxLayout(hwid)
            hlay.setContentsMargins(2, 0, 2, 0)
            hlay.addWidget(btn)
            hlay.addWidget(lbl)
            lay.addWidget(hwid, row, 0)
            c2v = dict()
            for idx1, trigid in enumerate(triggers):
                for idx2, prop in enumerate(propties):
                    pvn = _PVName(bpm).substitute(
                        prefix=self.prefix, propty='TRIGGER'+str(trigid)+prop)
                    dval = FamFOFBControllers.DEF_BPMTRIG_RCVIN if 'RcvIn' \
                        in prop else FamFOFBControllers.DEF_BPMTRIG_RCVSRC
                    c2v[pvn] = dval
                    plb = SiriusLabel(self, pvn)
                    lay.addWidget(plb, row, idx1*2+1+idx2)
            led = PyDMLedMultiChannel(self, c2v)
            lay.addWidget(led, row, 7)

        return self._build_scroll_area(wid)

    def _build_scroll_area(self, widget):
        area = QScrollArea(self)
        area.setSizeAdjustPolicy(QScrollArea.AdjustToContentsOnFirstShow)
        area.setWidgetResizable(True)
        area.setWidget(widget)
        widget.setObjectName('widget')
        widget.setStyleSheet(
            '#widget{background-color: transparent;}'
            'QLabel{border: 1px solid gray; min-height: 1.5em;}'
            '#lbl_bpmname{border: 0px solid gray; min-height: 1.5em;}'
            '#led_status{border: 1px solid gray; min-height: 1.5em;}')
        return area
