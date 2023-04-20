"""."""
from copy import deepcopy as _dcopy
from functools import partial as _partial

import numpy as _np
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGroupBox, QLabel, QPushButton, QFormLayout, \
    QVBoxLayout, QGridLayout, QWidget, QDoubleSpinBox, QHBoxLayout, \
    QFrame, QScrollArea, QTabWidget
import qtawesome as qta
from pydm.widgets.base import PyDMWritableWidget

from siriuspy.search import HLTimeSearch
from siriuspy.timesys import csdev as _cstime

from ..util import connect_window, get_appropriate_color
from ..widgets import PyDMLed, SiriusLedAlert, PyDMStateButton, \
    SiriusLabel, SiriusSpinbox, PyDMLedMultiChannel, \
    SiriusEnumComboBox, SiriusLedState
from ..widgets.windows import create_window_from_widget

from .base import BaseList, BaseWidget
from .low_level_devices import LLTriggerList, \
    EVREVEOTPList, EVREVEOUTList, AFCOUTList


class HLTriggerSimple(BaseWidget):

    def __init__(
            self, parent, device='', prefix='', delay=True, delayraw=False,
            duration=False, widthraw=False, nrpulses=False, src=False,
            deltadelay=False, deltadelayraw=False):
        super().__init__(parent, device, prefix)
        flay = QFormLayout(self)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignCenter)

        l_TIstatus = QLabel('Status: ', self)
        ledmulti_TIStatus = PyDMLedMultiChannel(
            parent=self, channels2values={
                self.get_pvname('State-Sts'): 1,
                self.get_pvname('Status-Mon'): 0})
        ledmulti_TIStatus.setStyleSheet(
            "min-width:1.29em; max-width:1.29em;"
            "min-height:1.29em; max-height:1.29em;")
        pb_trgdetails = QPushButton(qta.icon('fa5s.ellipsis-h'), '', self)
        pb_trgdetails.setToolTip('Open details')
        pb_trgdetails.setObjectName('detail')
        pb_trgdetails.setStyleSheet(
            "#detail{min-width:25px; max-width:25px; icon-size:20px;}")
        trg_w = create_window_from_widget(
            HLTriggerDetailed, title=device+' Detailed Settings',
            is_main=True)
        connect_window(
            pb_trgdetails, trg_w, parent=None,
            device=self.device, prefix=self.prefix)
        hlay_TIstatus = QHBoxLayout()
        hlay_TIstatus.addWidget(ledmulti_TIStatus)
        hlay_TIstatus.addWidget(pb_trgdetails)
        flay.addRow(l_TIstatus, hlay_TIstatus)

        if delay:
            l_delay = QLabel('Delay [us]: ', self)
            l_delay.setStyleSheet("min-width:5em;")
            hlay_delay = self._create_propty_layout(propty='Delay-SP')
            flay.addRow(l_delay, hlay_delay)

        if delayraw:
            l_delay = QLabel('DelayRaw: ', self)
            l_delay.setStyleSheet("min-width:5em;")
            hlay_delay = self._create_propty_layout(
                propty='DelayRaw-SP', show_unit=False)
            flay.addRow(l_delay, hlay_delay)

        if duration:
            l_duration = QLabel('Duration [us]: ', self)
            l_duration.setStyleSheet("min-width:5em;")
            hlay_duration = self._create_propty_layout(propty='Duration-SP')
            flay.addRow(l_duration, hlay_duration)

        if widthraw:
            l_widthraw = QLabel('WidthRaw: ', self)
            l_widthraw.setStyleSheet("min-width:5em;")
            hlay_widthraw = self._create_propty_layout(
                propty='WidthRaw-SP')
            flay.addRow(l_widthraw, hlay_widthraw)

        if nrpulses:
            l_nrpulses = QLabel('Nr Pulses: ', self)
            l_nrpulses.setStyleSheet("min-width:5em;")
            hlay_nrpulses = self._create_propty_layout(propty='NrPulses-SP')
            flay.addRow(l_nrpulses, hlay_nrpulses)

        if src:
            l_src = QLabel('Source: ', self)
            l_src.setStyleSheet("min-width:5em;")
            hlay_src = self._create_propty_layout(propty='Src-Sel')
            flay.addRow(l_src, hlay_src)

        if deltadelay or deltadelayraw:
            tab_deltadelay = QTabWidget(self)
            tab_deltadelay.setObjectName(self.device.sec+'Tab')
            tab_deltadelay.setStyleSheet("""
                #{}Tab::pane {{
                    border-left: 2px solid gray;
                    border-bottom: 2px solid gray;
                    border-right: 2px solid gray;
                }}""".format(self.device.sec))
            for tab in ['DeltaDelay', 'DeltaDelayRaw']:
                if 'Raw' not in tab and not deltadelay:
                    continue
                if 'Raw' in tab and not deltadelayraw:
                    continue
                unit = '' if 'Raw' in tab else ' [us]'
                wid = QWidget(self)
                lay = QGridLayout(wid)
                lay.setAlignment(Qt.AlignTop)
                lay.addWidget(
                    QLabel('<h4>Low Level</h4>'), 0, 0, Qt.AlignCenter)
                lay.addWidget(
                    QLabel(f'<h4>SP{unit:s}</h4>'), 0, 1, Qt.AlignCenter)
                lay.addWidget(
                    QLabel(f'<h4>RB{unit:s}</h4>'), 0, 2, Qt.AlignCenter)
                devname = self.device.device_name
                ll_obj_names = HLTimeSearch.get_ll_trigger_names(devname)
                hl_obj_names = HLTimeSearch.get_hl_trigger_channels(devname)
                for idx, objs in enumerate(zip(ll_obj_names, hl_obj_names)):
                    nam = QLabel(
                        objs[0] + '\n(' + objs[1] + ')', wid,
                        alignment=Qt.AlignCenter)
                    spin = _SpinBox(
                        wid, init_channel=self.get_pvname(tab+'-SP'),
                        index=idx)
                    spin.setStyleSheet('min-width:7em;')
                    lbl = _Label(
                        wid, init_channel=self.get_pvname(tab+'-RB'),
                        index=idx)
                    lbl.setStyleSheet('min-width:6em;')
                    lay.addWidget(nam, idx+1, 0)
                    lay.addWidget(spin, idx+1, 1)
                    lay.addWidget(lbl, idx+1, 2)
                tab_deltadelay.addTab(wid, tab)
            flay.addRow(tab_deltadelay)


class HLTriggerDetailed(BaseWidget):
    """Template for control of High Level Triggers."""

    def __init__(self, parent=None, device='', prefix=''):
        """Initialize object."""
        super().__init__(parent, device, prefix)
        name = self.device.sec + 'App'
        self.setObjectName(name)
        self._setupUi()

    def _setupUi(self):
        self.my_layout = QGridLayout(self)
        self.my_layout.setHorizontalSpacing(20)
        self.my_layout.setVerticalSpacing(0)
        lab = QLabel('<h1>' + self.device.device_name + '</h1>', self)
        self.my_layout.addWidget(lab, 0, 0, 1, 2)
        self.my_layout.setAlignment(lab, Qt.AlignCenter)

        self.status_wid = QGroupBox('Status', self)
        self.my_layout.addWidget(self.status_wid, 1, 0)
        self._setup_status_wid()

        init_channel = self.get_pvname('InInjTable-Mon')
        rb = SiriusLedState(self, init_channel=init_channel)
        gbinjtab = self._create_small_group('In Injection Table?', self, (rb,))
        self.my_layout.addWidget(gbinjtab, 2, 0)

        self.ll_list_wid = QGroupBox('Configs', self)
        self.my_layout.addWidget(self.ll_list_wid, 1, 1, 2, 1)
        self._setup_ll_list_wid()

    def _setup_status_wid(self):
        status_layout = QFormLayout(self.status_wid)
        status_layout.setHorizontalSpacing(20)
        status_layout.setVerticalSpacing(20)
        for bit, label in enumerate(_cstime.Const.HLTrigStatusLabels):
            led = SiriusLedAlert(self, self.get_pvname('Status-Mon'), bit)
            lab = QLabel(label, self)
            status_layout.addRow(led, lab)

    def _setup_ll_list_wid(self):
        ll_list_layout = QGridLayout(self.ll_list_wid)
        ll_list_layout.setHorizontalSpacing(20)
        ll_list_layout.setVerticalSpacing(20)

        but = QPushButton('Open LL Triggers', self)
        but.setAutoDefault(False)
        but.setDefault(False)
        obj_names = HLTimeSearch.get_ll_trigger_names(self.device.device_name)
        icon = qta.icon(
            'mdi.timer', color=get_appropriate_color(self.device.sec))
        Window = create_window_from_widget(
            LLTriggers, title=self.device.device_name+': LL Triggers',
            icon=icon)
        connect_window(
            but, Window, self, prefix=self.prefix,
            hltrigger=self.device.device_name, obj_names=obj_names)
        lay = QHBoxLayout()
        ll_list_layout.addLayout(lay, 0, 0, 1, 3)
        lay.addWidget(but)
        lay.addStretch()

        pbt_bl = QPushButton('>', self)
        pbt_bl.setToolTip('Show Delta Delay information.')
        pbt_bl.setStyleSheet('QPushButton{max-width: 0.8em;}')
        lay.addWidget(pbt_bl)

        init_channel = self.get_pvname('LowLvlLock-Sel')
        sp = PyDMStateButton(self, init_channel=init_channel)
        init_channel = self.get_pvname('LowLvlLock-Sts')
        rb = PyDMLed(self, init_channel=init_channel)
        gb = self._create_small_group(
            'Lock Low Level', self.ll_list_wid, (sp, rb))
        ll_list_layout.addWidget(gb, 1, 0)

        init_channel = self.get_pvname('State-Sel')
        sp = PyDMStateButton(self, init_channel=init_channel)
        init_channel = self.get_pvname('State-Sts')
        rb = PyDMLed(self, init_channel=init_channel)
        gb = self._create_small_group('Enabled', self.ll_list_wid, (sp, rb))
        ll_list_layout.addWidget(gb, 1, 1)

        init_channel = self.get_pvname('Polarity-Sel')
        sp = SiriusEnumComboBox(self, init_channel=init_channel)
        init_channel = self.get_pvname('Polarity-Sts')
        rb = SiriusLabel(self, init_channel=init_channel)
        gb = self._create_small_group('Polarity', self.ll_list_wid, (sp, rb))
        ll_list_layout.addWidget(gb, 1, 2)

        init_channel = self.get_pvname('Src-Sel')
        sp = SiriusEnumComboBox(self, init_channel=init_channel)
        init_channel = self.get_pvname('Src-Sts')
        rb = SiriusLabel(self, init_channel=init_channel)
        gb = self._create_small_group('Source', self.ll_list_wid, (sp, rb))
        ll_list_layout.addWidget(gb, 2, 0)

        init_channel = self.get_pvname('NrPulses-SP')
        sp = SiriusSpinbox(self, init_channel=init_channel)
        init_channel = self.get_pvname('NrPulses-RB')
        rb = SiriusLabel(self, init_channel=init_channel)
        gb = self._create_small_group('Nr Pulses', self.ll_list_wid, (sp, rb))
        ll_list_layout.addWidget(gb, 2, 1)

        init_channel = self.get_pvname('Duration-SP')
        sp = SiriusSpinbox(self, init_channel=init_channel)
        init_channel = self.get_pvname('Duration-RB')
        rb = SiriusLabel(self, init_channel=init_channel)
        gbdur = self._create_small_group(
            'Duration [us]', self.ll_list_wid, (sp, rb))

        init_channel = self.get_pvname('WidthRaw-SP')
        sp = SiriusSpinbox(self, init_channel=init_channel)
        init_channel = self.get_pvname('WidthRaw-RB')
        rb = SiriusLabel(self, init_channel=init_channel)
        gbwid = self._create_small_group(
            'WidthRaw', self.ll_list_wid, (sp, rb))

        widd = QWidget(self.ll_list_wid)
        widd.setLayout(QHBoxLayout())
        widd.layout().addWidget(gbdur)
        widd.layout().addWidget(gbwid)
        ll_list_layout.addWidget(widd, 3, 0, 1, 3)

        init_channel = self.get_pvname('Delay-SP')
        sp = SiriusSpinbox(self, init_channel=init_channel)
        init_channel = self.get_pvname('Delay-RB')
        rb = SiriusLabel(self, init_channel=init_channel)
        gbdel = self._create_small_group('[us]', self.ll_list_wid, (sp, rb))

        init_channel = self.get_pvname('DelayRaw-SP')
        sp = SiriusSpinbox(self, init_channel=init_channel)
        init_channel = self.get_pvname('DelayRaw-RB')
        rb = SiriusLabel(self, init_channel=init_channel)
        gbdelr = self._create_small_group('Raw', self.ll_list_wid, (sp, rb))

        init_channel = self.get_pvname('TotalDelay-Mon')
        rb = SiriusLabel(self, init_channel=init_channel)
        gbtdel = self._create_small_group('[us]', self.ll_list_wid, (rb, ))

        init_channel = self.get_pvname('TotalDelayRaw-Mon')
        rb = SiriusLabel(self, init_channel=init_channel)
        gbtdelr = self._create_small_group('Raw', self.ll_list_wid, (rb, ))

        widd = QWidget(self.ll_list_wid)
        widd.setLayout(QHBoxLayout())
        widd.layout().addWidget(gbdel)
        widd.layout().addWidget(gbdelr)

        widt = QWidget(self.ll_list_wid)
        widt.setLayout(QHBoxLayout())
        widt.layout().addWidget(gbtdel)
        widt.layout().addWidget(gbtdelr)

        tabdel = QTabWidget(self)
        tabdel.setObjectName(self.device.sec + 'Tab')
        tabdel.addTab(widd, 'Delay')
        tabdel.addTab(widt, 'Total Delay')
        ll_list_layout.addWidget(tabdel, 4, 0, 1, 3)

        if HLTimeSearch.has_delay_type(self.device.device_name):
            init_channel = self.get_pvname('RFDelayType-Sel')
            sp = SiriusEnumComboBox(self, init_channel=init_channel)
            init_channel = self.get_pvname('RFDelayType-Sts')
            rb = SiriusLabel(self, init_channel=init_channel)
            gb = self._create_small_group(
                'Delay Type', self.ll_list_wid, (sp, rb))
            ll_list_layout.addWidget(gb, 2, 2)

        tabdelta = QTabWidget(self)
        tabdelta.setObjectName(self.device.sec + 'Tab')
        deltaus = self._create_deltadelay(israw=False)
        deltaraw = self._create_deltadelay(israw=True)
        tabdelta.addTab(deltaus, 'Delta Delay')
        tabdelta.addTab(deltaraw, 'Delta Delay Raw')

        tabdelta.setVisible(False)
        pbt_bl.clicked.connect(_partial(
            self._toggle_visibility, tabdelta, pbt_bl))
        ll_list_layout.addWidget(tabdelta, 0, 3, 5, 1)

    def _toggle_visibility(self, wid, but):
        show = wid.isHidden()
        wid.setVisible(show)
        text = '<' if show else '>'
        but.setText(text)
        tooltip = ('Hide' if show else 'Show') + but.toolTip()[4:]
        self.sender().setToolTip(tooltip)
        parent = but.parent()
        while parent is not None:
            parent.adjustSize()
            parent = parent.parent()

    def _create_deltadelay(self, israw=False):
        unit = '' if israw else ' [us]'
        pvn = 'DeltaDelay' + ('Raw' if israw else '')
        wid_ = QWidget()
        lay = QVBoxLayout(wid_)
        sc_area = QScrollArea()
        sc_area.setWidgetResizable(True)
        sc_area.setFrameShape(QFrame.NoFrame)
        lay.addWidget(sc_area)

        wid = QWidget(sc_area)
        wid.setObjectName('wid')
        wid.setStyleSheet('#wid {background-color: transparent;}')
        sc_area.setWidget(wid)

        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignTop)
        lay.addWidget(QLabel('<h4>Low Level</h4>'), 0, 0, Qt.AlignCenter)
        lay.addWidget(QLabel(f'<h4>SP{unit:s}</h4>'), 0, 1, Qt.AlignCenter)
        lay.addWidget(QLabel(f'<h4>RB{unit:s}</h4>'), 0, 2, Qt.AlignCenter)
        ll_obj_names = HLTimeSearch.get_ll_trigger_names(
            self.device.device_name)
        for idx, obj in enumerate(ll_obj_names, 1):
            nam = QLabel(obj, wid)
            spin = _SpinBox(
                wid, init_channel=self.get_pvname(pvn+'-SP'),
                index=idx-1)
            spin.setStyleSheet('min-width:7em;')
            lbl = _Label(
                wid, init_channel=self.get_pvname(pvn+'-RB'),
                index=idx-1)
            lbl.setStyleSheet('min-width:6em;')
            lay.addWidget(nam, idx, 0)
            lay.addWidget(spin, idx, 1)
            lay.addWidget(lbl, idx, 2)
        sc_area.setSizeAdjustPolicy(QScrollArea.AdjustToContentsOnFirstShow)
        sc_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        return wid_


class _SpinBox(SiriusSpinbox):

    def __init__(self, parent=None, init_channel=None, index=0):
        self._index = index
        super().__init__(parent=parent, init_channel=init_channel)

    def value_changed(self, value):
        self.valueBeingSet = True
        if isinstance(value, _np.ndarray):
            self.setValue(value[self._index])
        else:
            self.setValue(value)
        self.valueBeingSet = False
        PyDMWritableWidget.value_changed(self, value)

    def send_value(self):
        """
        Method invoked to send the current value on the QDoubleSpinBox to
        the channel using the `send_value_signal`.
        """
        value = QDoubleSpinBox.value(self)
        val = _dcopy(self.value)
        if isinstance(val, _np.ndarray):
            val[self._index] = value
            if not self.valueBeingSet:
                self.send_value_signal[_np.ndarray].emit(val)
        else:
            if not self.valueBeingSet:
                self.send_value_signal[float].emit(value)


class _Label(SiriusLabel):

    def __init__(self, parent=None, init_channel=None, index=0):
        self._index = index
        super().__init__(parent=parent, init_channel=init_channel)

    def value_changed(self, value):
        if isinstance(value, _np.ndarray):
            value = value[self._index]
        super().value_changed(value)


class LLTriggers(QWidget):

    def __init__(
            self, parent=None, prefix=None, hltrigger='', obj_names=list()):
        super().__init__(parent)
        vl = QVBoxLayout(self)
        vl.addWidget(QLabel(
            '<h1>Low Level Triggers of '+hltrigger+'</h1>',
            self, alignment=Qt.AlignCenter))
        self.setObjectName(hltrigger.sec+'App')

        amc_list = set()
        otp_list = set()
        out_list = set()
        for name in obj_names:
            if 'AMC' in name.dev:
                amc_list.add(name)
            elif 'OTP' in name.propty_name:
                otp_list.add(name)
            elif 'OUT' in name.propty_name:
                out_list.add(name)
        if amc_list:
            props = set(AFCOUTList._ALL_PROPS)
            props.discard('widthraw')
            props.discard('delayraw')
            props.add('device')
            amc_wid = LLTriggerList(
                name='AMCs', parent=self, props=props,
                prefix=prefix, obj_names=sorted(amc_list))
            amc_wid.setObjectName('amc_wid')
            vl.addWidget(amc_wid)
        if otp_list:
            props = set(EVREVEOTPList._ALL_PROPS)
            props.discard('width')
            props.discard('delay')
            props.add('device')
            otp_wid = LLTriggerList(
                name='OTPs', parent=self, props=props,
                prefix=prefix, obj_names=sorted(otp_list))
            otp_wid.setObjectName('otp_wid')
            vl.addWidget(otp_wid)
        if out_list:
            props = set(EVREVEOTPList._ALL_PROPS)
            props.update(EVREVEOUTList._ALL_PROPS)
            props.discard('width')
            props.discard('delay')
            props.discard('fine_delay')
            props.discard('rf_delay')
            props.add('device')
            out_wid = LLTriggerList(
                name='OUTs', parent=self, props=props,
                prefix=prefix, obj_names=sorted(out_list))
            out_wid.setObjectName('out_wid')
            vl.addWidget(out_wid)


class HLTriggerList(BaseList):
    """Template for control of High Level Triggers."""

    _MIN_WIDs = {
        'name': 10,
        'detailed': 3,
        'status': 4,
        'state': 3.8,
        'source': 4.8,
        'pulses': 4.8,
        'duration': 8,
        'widthraw': 8,
        'polarity': 6,
        'delay_type': 4.2,
        'delay': 5.5,
        'delayraw': 5.5,
        'total_delay': 6,
        'total_delayraw': 6,
        'ininjtable': 5,
        }
    _LABELS = {
        'detailed': '',
        'name': 'Name',
        'status': 'Status',
        'state': 'Enabled',
        'source': 'Source',
        'pulses': 'Nr Pulses',
        'duration': 'Duration [us]',
        'widthraw': 'WidthRaw',
        'polarity': 'Polarity',
        'delay_type': 'Type',
        'delay': 'Delay [us]',
        'delayraw': 'DelayRaw',
        'total_delay': 'Total Dly [us]',
        'total_delayraw': 'Total DlyRaw',
        'ininjtable': 'InInjTable',
        }
    _ALL_PROPS = (
        'detailed', 'status', 'name', 'state', 'source', 'polarity', 'pulses',
        'duration', 'widthraw', 'delay_type', 'delay', 'delayraw',
        'total_delay', 'total_delayraw', 'ininjtable')

    def __init__(self, **kwargs):
        srch = set(('source', 'name', 'polarity', 'state'))
        kwargs['props2search'] = srch
        super().__init__(**kwargs)
        self.setObjectName('ASApp')

    def _createObjs(self, device, prop):
        sp = rb = None
        if prop == 'name':
            sp = QLabel(device.device_name, self, alignment=Qt.AlignCenter)
        elif prop == 'status':
            init_channel = device.substitute(propty='Status-Mon')
            sp = SiriusLedAlert(self, init_channel=init_channel)
            sp.setShape(sp.ShapeMap.Square)
        elif prop == 'detailed':
            sp = QWidget(self)
            but = QPushButton('', sp)
            but.setToolTip('Open Detailed View Window')
            but.setIcon(qta.icon('fa5s.list-ul'))
            but.setObjectName('but')
            but.setStyleSheet(
                '#but{min-width:25px; max-width:25px;\
                min-height:25px; max-height:25px;\
                icon-size:20px;}')
            icon = qta.icon(
                'mdi.timer', color=get_appropriate_color(device.sec))
            Window = create_window_from_widget(
                HLTriggerDetailed,
                title=device.device_name+': HL Trigger Detailed',
                icon=icon)
            connect_window(
                but, Window, None, device=device, prefix=self.prefix)
            QHBoxLayout(sp).addWidget(but)
        elif prop == 'state':
            init_channel = device.substitute(propty='State-Sel')
            sp = PyDMStateButton(self, init_channel=init_channel)
            init_channel = device.substitute(propty='State-Sts')
            rb = PyDMLed(self, init_channel=init_channel)
        elif prop == 'source':
            init_channel = device.substitute(propty='Src-Sel')
            sp = SiriusEnumComboBox(self, init_channel=init_channel)
            init_channel = device.substitute(propty='Src-Sts')
            rb = SiriusLabel(self, init_channel=init_channel)
        elif prop == 'pulses':
            init_channel = device.substitute(propty='NrPulses-SP')
            sp = SiriusSpinbox(self, init_channel=init_channel)
            init_channel = device.substitute(propty='NrPulses-RB')
            rb = SiriusLabel(self, init_channel=init_channel)
        elif prop == 'duration':
            init_channel = device.substitute(propty='Duration-SP')
            sp = SiriusSpinbox(self, init_channel=init_channel)
            init_channel = device.substitute(propty='Duration-RB')
            rb = SiriusLabel(self, init_channel=init_channel)
        elif prop == 'widthraw':
            init_channel = device.substitute(propty='WidthRaw-SP')
            sp = SiriusSpinbox(self, init_channel=init_channel)
            init_channel = device.substitute(propty='WidthRaw-RB')
            rb = SiriusLabel(self, init_channel=init_channel)
        elif prop == 'polarity':
            init_channel = device.substitute(propty='Polarity-Sel')
            sp = SiriusEnumComboBox(self, init_channel=init_channel)
            init_channel = device.substitute(propty='Polarity-Sts')
            rb = SiriusLabel(self, init_channel=init_channel)
        elif prop == 'delay_type':
            init_channel = device.substitute(propty='RFDelayType-Sel')
            sp = SiriusEnumComboBox(self, init_channel=init_channel)
            init_channel = device.substitute(propty='RFDelayType-Sts')
            rb = SiriusLabel(self, init_channel=init_channel)
        elif prop == 'delay':
            init_channel = device.substitute(propty='Delay-SP')
            sp = SiriusSpinbox(self, init_channel=init_channel)
            init_channel = device.substitute(propty='Delay-RB')
            rb = SiriusLabel(self, init_channel=init_channel)
        elif prop == 'delayraw':
            init_channel = device.substitute(propty='DelayRaw-SP')
            sp = SiriusSpinbox(self, init_channel=init_channel)
            init_channel = device.substitute(propty='DelayRaw-RB')
            rb = SiriusLabel(self, init_channel=init_channel)
        elif prop == 'total_delay':
            init_channel = device.substitute(propty='TotalDelay-Mon')
            sp = SiriusLabel(self, init_channel=init_channel)
        elif prop == 'total_delayraw':
            init_channel = device.substitute(propty='TotalDelayRaw-Mon')
            sp = SiriusLabel(self, init_channel=init_channel)
        elif prop == 'ininjtable':
            init_channel = device.substitute(propty='InInjTable-Mon')
            sp = SiriusLedState(self, init_channel=init_channel)
        else:
            raise Exception('Property unknown')
        if rb is None:
            return (sp, )
        return sp, rb
