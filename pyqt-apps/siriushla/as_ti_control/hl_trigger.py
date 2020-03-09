import sys
from copy import deepcopy as _dcopy
import numpy as _np
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGroupBox, QLabel, QPushButton, QFormLayout, \
    QVBoxLayout, QGridLayout, QWidget, QDoubleSpinBox, QHBoxLayout, \
    QFrame, QScrollArea, QTabWidget
import qtawesome as qta

from pydm.widgets import PyDMLabel
from pydm.widgets.base import PyDMWritableWidget
from siriuspy.search import HLTimeSearch
from siriuspy.csdevice import timesys

from siriushla.util import connect_window, get_appropriate_color
from siriushla.widgets import PyDMLed, SiriusLedAlert, PyDMStateButton, \
    SiriusLabel, SiriusSpinbox, PyDMLedMultiChannel
from siriushla.widgets.windows import create_window_from_widget
from .base import BaseList, BaseWidget, MySpinBox as _MySpinBox, \
    MyComboBox as _MyComboBox
from .ll_trigger import LLTriggerList, OTPList, OUTList, AFCOUTList


class HLTriggerSimple(BaseWidget):

    def __init__(self, parent, prefix, delay=True, duration=False,
                 nrpulses=False, src=False):
        super().__init__(parent=parent, prefix=prefix)
        flay = QFormLayout(self)
        flay.setLabelAlignment(Qt.AlignRight)
        flay.setFormAlignment(Qt.AlignCenter)

        l_TIstatus = QLabel('Status: ', self)
        ledmulti_TIStatus = PyDMLedMultiChannel(
            parent=self,
            channels2values={prefix+':State-Sts': 1, prefix+':Status-Mon': 0})
        ledmulti_TIStatus.setStyleSheet(
            "min-width:1.29em; max-width:1.29em;"
            "min-height:1.29em; max-height:1.29em;")
        pb_trgdetails = QPushButton(qta.icon('fa5s.ellipsis-h'), '', self)
        pb_trgdetails.setToolTip('Open details')
        pb_trgdetails.setObjectName('detail')
        pb_trgdetails.setStyleSheet(
            "#detail{min-width:25px; max-width:25px; icon-size:20px;}")
        trg_w = create_window_from_widget(
            HLTriggerDetailed, title=prefix+' Detailed Settings',
            is_main=True)
        connect_window(pb_trgdetails, trg_w, parent=None, prefix=prefix)
        hlay_TIstatus = QHBoxLayout()
        hlay_TIstatus.addWidget(ledmulti_TIStatus)
        hlay_TIstatus.addWidget(pb_trgdetails)
        flay.addRow(l_TIstatus, hlay_TIstatus)

        if delay:
            l_delay = QLabel('Delay [us]: ', self)
            l_delay.setStyleSheet("min-width:5em;")
            hlay_delay = self._create_propty_layout(propty='Delay-SP')
            flay.addRow(l_delay, hlay_delay)

        if duration:
            l_duration = QLabel('Duration [us]: ', self)
            l_duration.setStyleSheet("min-width:5em;")
            hlay_duration = self._create_propty_layout(propty='Duration-SP')
            flay.addRow(l_duration, hlay_duration)

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

    def create_propty_layout(self, propty, width=6.0):
        """Return layout that handles a property according to 'propty_type'."""
        layout = QHBoxLayout()
        style = """
        min-width:wvalem; max-width:wvalem; min-height:1.29em;
        max-height:1.29em;""".replace('wval', str(width))

        sp = _MySpinBox(
            parent=self, init_channel=self.prefix+':'+propty+'-SP')
        sp.showStepExponent = False
        sp.setStyleSheet(style)
        sp.setAlignment(Qt.AlignCenter)
        layout.addWidget(sp)
        label = PyDMLabel(
            parent=self, init_channel=self.prefix+':'+propty+'-RB')
        label.setStyleSheet(style)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        layout.setAlignment(Qt.AlignVCenter)
        return layout


class HLTriggerDetailed(BaseWidget):
    """Template for control of High Level Triggers."""

    def __init__(self, parent=None, prefix=''):
        """Initialize object."""
        super().__init__(parent, prefix)
        name = self.prefix.sec + 'App'
        self.setObjectName(name)
        self._setupUi()

    def _setupUi(self):
        self.my_layout = QGridLayout(self)
        self.my_layout.setHorizontalSpacing(20)
        self.my_layout.setVerticalSpacing(20)
        lab = QLabel('<h1>' + self.prefix.device_name + '</h1>', self)
        self.my_layout.addWidget(lab, 0, 0, 1, 2)
        self.my_layout.setAlignment(lab, Qt.AlignCenter)
        self.status_wid = QGroupBox('Status', self)
        self.my_layout.addWidget(self.status_wid, 1, 0)
        self._setup_status_wid()
        self.ll_list_wid = QGroupBox('Configs', self)
        self.my_layout.addWidget(self.ll_list_wid, 1, 1)
        self._setup_ll_list_wid()

    def _setup_status_wid(self):
        status_layout = QFormLayout(self.status_wid)
        status_layout.setHorizontalSpacing(20)
        status_layout.setVerticalSpacing(20)
        for bit, label in enumerate(timesys.Const.HLTrigStatusLabels):
            led = SiriusLedAlert(
                    self, self.prefix.substitute(propty='Status-Mon'), bit)
            lab = QLabel(label, self)
            status_layout.addRow(led, lab)

    def _setup_ll_list_wid(self):
        prefix = self.prefix
        ll_list_layout = QGridLayout(self.ll_list_wid)
        ll_list_layout.setHorizontalSpacing(20)
        ll_list_layout.setVerticalSpacing(20)

        but = QPushButton('Open LL Triggers', self)
        but.setAutoDefault(False)
        but.setDefault(False)
        obj_names = HLTimeSearch.get_ll_trigger_names(self.prefix.device_name)
        icon = qta.icon(
            'mdi.timer', color=get_appropriate_color(self.prefix.sec))
        Window = create_window_from_widget(
            LLTriggers, title=self.prefix.device_name+': LL Triggers',
            icon=icon)
        connect_window(
            but, Window, self, prefix=self.prefix.prefix + '-',
            hltrigger=self.prefix.device_name, obj_names=obj_names)
        ll_list_layout.addWidget(but, 0, 0, 1, 2)

        init_channel = prefix.substitute(propty="LowLvlLock-Sel")
        sp = PyDMStateButton(self, init_channel=init_channel)
        init_channel = prefix.substitute(propty="LowLvlLock-Sts")
        rb = PyDMLed(self, init_channel=init_channel)
        gb = self._create_small_GB(
            'Lock Low Level', self.ll_list_wid, (sp, rb))
        ll_list_layout.addWidget(gb, 1, 0)

        init_channel = prefix.substitute(propty="State-Sel")
        sp = PyDMStateButton(self, init_channel=init_channel)
        init_channel = prefix.substitute(propty="State-Sts")
        rb = PyDMLed(self, init_channel=init_channel)
        gb = self._create_small_GB('Enabled', self.ll_list_wid, (sp, rb))
        ll_list_layout.addWidget(gb, 1, 1)

        init_channel = prefix.substitute(propty="Polarity-Sel")
        sp = _MyComboBox(self, init_channel=init_channel)
        init_channel = prefix.substitute(propty="Polarity-Sts")
        rb = PyDMLabel(self, init_channel=init_channel)
        gb = self._create_small_GB('Polarity', self.ll_list_wid, (sp, rb))
        ll_list_layout.addWidget(gb, 2, 0)

        init_channel = prefix.substitute(propty="Src-Sel")
        sp = _MyComboBox(self, init_channel=init_channel)
        init_channel = prefix.substitute(propty="Src-Sts")
        rb = PyDMLabel(self, init_channel=init_channel)
        gb = self._create_small_GB('Source', self.ll_list_wid, (sp, rb))
        ll_list_layout.addWidget(gb, 2, 1)

        init_channel = prefix.substitute(propty="NrPulses-SP")
        sp = _MySpinBox(self, init_channel=init_channel)
        sp.showStepExponent = False
        init_channel = prefix.substitute(propty="NrPulses-RB")
        rb = PyDMLabel(self, init_channel=init_channel)
        gb = self._create_small_GB('Nr Pulses', self.ll_list_wid, (sp, rb))
        ll_list_layout.addWidget(gb, 3, 0)

        init_channel = prefix.substitute(propty="Duration-SP")
        sp = _MySpinBox(self, init_channel=init_channel)
        sp.showStepExponent = False
        init_channel = prefix.substitute(propty="Duration-RB")
        rb = PyDMLabel(self, init_channel=init_channel)
        gb = self._create_small_GB('Duration [us]', self.ll_list_wid, (sp, rb))
        ll_list_layout.addWidget(gb, 3, 1)

        init_channel = prefix.substitute(propty="Delay-SP")
        sp = _MySpinBox(self, init_channel=init_channel)
        sp.showStepExponent = False
        init_channel = prefix.substitute(propty="Delay-RB")
        rb = PyDMLabel(self, init_channel=init_channel)
        gbdel = self._create_small_GB('Delay [us]', self.ll_list_wid, (sp, rb))

        init_channel = prefix.substitute(propty="DelayRaw-SP")
        sp = _MySpinBox(self, init_channel=init_channel)
        sp.showStepExponent = False
        init_channel = prefix.substitute(propty="DelayRaw-RB")
        rb = PyDMLabel(self, init_channel=init_channel)
        gbdelr = self._create_small_GB('Raw Delay', self.ll_list_wid, (sp, rb))

        tabdel = QTabWidget(self)
        tabdel.addTab(gbdel, '[us]')
        tabdel.addTab(gbdelr, 'Raw')

        if HLTimeSearch.has_delay_type(prefix.device_name):
            init_channel = prefix.substitute(propty="RFDelayType-Sel")
            sp = _MyComboBox(self, init_channel=init_channel)
            init_channel = prefix.substitute(propty="RFDelayType-Sts")
            rb = PyDMLabel(self, init_channel=init_channel)
            gb = self._create_small_GB(
                'Delay Type', self.ll_list_wid, (sp, rb))
            ll_list_layout.addWidget(gb, 4, 0)
            ll_list_layout.addWidget(tabdel, 4, 1)
        else:
            ll_list_layout.addWidget(tabdel, 4, 0, 1, 2)

        gbdelta = self._create_deltadelay()
        ll_list_layout.addWidget(gbdelta, 0, 2, 5, 1)

    def _create_deltadelay(self):
        gb = QGroupBox('Delta Delay')
        lay = QVBoxLayout(gb)
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
        lay.addWidget(QLabel('<h4>SP [us]</h4>'), 0, 1, Qt.AlignCenter)
        lay.addWidget(QLabel('<h4>RB [us]</h4>'), 0, 2, Qt.AlignCenter)
        pref = self.prefix
        devname = pref.device_name
        ll_obj_names = HLTimeSearch.get_ll_trigger_names(devname)
        for idx, obj in enumerate(ll_obj_names, 1):
            nam = QLabel(obj, wid)
            spin = _SpinBox(
                wid, init_channel=pref.substitute(propty='DeltaDelay-SP'),
                index=idx-1)
            spin.setStyleSheet('min-width:7em;')
            lbl = _Label(
                wid, init_channel=pref.substitute(propty='DeltaDelay-SP'),
                index=idx-1)
            lbl.setStyleSheet('min-width:6em;')
            lay.addWidget(nam, idx, 0)
            lay.addWidget(spin, idx, 1)
            lay.addWidget(lbl, idx, 2)
        sc_area.setSizeAdjustPolicy(QScrollArea.AdjustToContentsOnFirstShow)
        sc_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        return gb

    def _create_small_GB(self, name, parent, wids):
        gb = QGroupBox(name, parent)
        lv = QVBoxLayout(gb)
        for wid in wids:
            lv.addWidget(wid)
        return gb


class _SpinBox(SiriusSpinbox):

    def __init__(self, parent=None, init_channel=None, index=0):
        self._index = index
        super().__init__(parent=parent, init_channel=init_channel)
        self.showStepExponent = False

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
            props = set(AFCOUTList()._ALL_PROPS)
            props.discard('widthraw')
            props.discard('delayraw')
            props.add('device')
            amc_wid = LLTriggerList(name='AMCs', parent=self, props=props,
                                    prefix=prefix, obj_names=amc_list)
            amc_wid.setObjectName('amc_wid')
            amc_wid.setStyleSheet("""#amc_wid{min-width:90em;}""")
            vl.addWidget(amc_wid)
        if otp_list:
            props = set(OTPList()._ALL_PROPS)
            props.discard('width')
            props.discard('delay')
            props.add('device')
            otp_wid = LLTriggerList(name='OTPs', parent=self, props=props,
                                    prefix=prefix, obj_names=otp_list)
            otp_wid.setObjectName('otp_wid')
            otp_wid.setStyleSheet("""#otp_wid{min-width:56em;}""")
            vl.addWidget(otp_wid)
        if out_list:
            props = set(OTPList()._ALL_PROPS)
            props.update(OUTList()._ALL_PROPS)
            props.discard('width')
            props.discard('delay')
            props.discard('fine_delay')
            props.discard('rf_delay')
            props.add('device')
            out_wid = LLTriggerList(name='OUTs', parent=self, props=props,
                                    prefix=prefix, obj_names=out_list)
            out_wid.setObjectName('out_wid')
            out_wid.setStyleSheet("""#out_wid{min-width:110em;}""")
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
        'polarity': 6,
        'delay_type': 4.2,
        'delay': 5.5,
        'delayraw': 5.5,
        }
    _LABELS = {
        'detailed': '',
        'name': 'Name',
        'status': 'Status',
        'state': 'Enabled',
        'source': 'Source',
        'pulses': 'Nr Pulses',
        'duration': 'Duration [us]',
        'polarity': 'Polarity',
        'delay_type': 'Type',
        'delay': 'Delay [us]',
        'delayraw': 'Raw Delay',
        }
    _ALL_PROPS = (
        'detailed', 'status', 'name', 'state', 'source', 'polarity', 'pulses',
        'duration', 'delay_type', 'delay', 'delayraw')

    def __init__(self, **kwargs):
        srch = set(('source', 'name', 'polarity', 'state'))
        kwargs['props2search'] = srch
        super().__init__(**kwargs)
        self.setObjectName('ASApp')

    def _createObjs(self, prefix, prop):
        sp = rb = None
        if prop == 'name':
            sp = QLabel(prefix.device_name, self, alignment=Qt.AlignCenter)
        elif prop == 'status':
            init_channel = prefix.substitute(propty="Status-Mon")
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
                'mdi.timer', color=get_appropriate_color(prefix.sec))
            Window = create_window_from_widget(
                HLTriggerDetailed,
                title=prefix.device_name+': HL Trigger Detailed',
                icon=icon)
            connect_window(but, Window, None, prefix=prefix)
            QHBoxLayout(sp).addWidget(but)
        elif prop == 'state':
            init_channel = prefix.substitute(propty="State-Sel")
            sp = PyDMStateButton(self, init_channel=init_channel)
            init_channel = prefix.substitute(propty="State-Sts")
            rb = PyDMLed(self, init_channel=init_channel)
        elif prop == 'source':
            init_channel = prefix.substitute(propty="Src-Sel")
            sp = _MyComboBox(self, init_channel=init_channel)
            init_channel = prefix.substitute(propty="Src-Sts")
            rb = PyDMLabel(self, init_channel=init_channel)
        elif prop == 'pulses':
            init_channel = prefix.substitute(propty="NrPulses-SP")
            sp = _MySpinBox(self, init_channel=init_channel)
            sp.showStepExponent = False
            init_channel = prefix.substitute(propty="NrPulses-RB")
            rb = PyDMLabel(self, init_channel=init_channel)
        elif prop == 'duration':
            init_channel = prefix.substitute(propty="Duration-SP")
            sp = _MySpinBox(self, init_channel=init_channel)
            sp.showStepExponent = False
            init_channel = prefix.substitute(propty="Duration-RB")
            rb = PyDMLabel(self, init_channel=init_channel)
        elif prop == 'polarity':
            init_channel = prefix.substitute(propty="Polarity-Sel")
            sp = _MyComboBox(self, init_channel=init_channel)
            init_channel = prefix.substitute(propty="Polarity-Sts")
            rb = PyDMLabel(self, init_channel=init_channel)
        elif prop == 'delay_type':
            init_channel = prefix.substitute(propty="RFDelayType-Sel")
            sp = _MyComboBox(self, init_channel=init_channel)
            init_channel = prefix.substitute(propty="RFDelayType-Sts")
            rb = PyDMLabel(self, init_channel=init_channel)
        elif prop == 'delay':
            init_channel = prefix.substitute(propty="Delay-SP")
            sp = _MySpinBox(self, init_channel=init_channel)
            sp.showStepExponent = False
            init_channel = prefix.substitute(propty="Delay-RB")
            rb = PyDMLabel(self, init_channel=init_channel)
        elif prop == 'delayraw':
            init_channel = prefix.substitute(propty="DelayRaw-SP")
            sp = _MySpinBox(self, init_channel=init_channel)
            sp.showStepExponent = False
            init_channel = prefix.substitute(propty="DelayRaw-RB")
            rb = PyDMLabel(self, init_channel=init_channel)
        else:
            raise Exception('Property unknown')
        if rb is None:
            return (sp, )
        return sp, rb


if __name__ == '__main__':
    """Run Example."""
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets.windows import SiriusMainWindow

    props = {'detailed', 'state', 'pulses', 'duration'}
    app = SiriusApplication()
    win = SiriusMainWindow()
    list_ctrl = HLTriggerList(
        name="Triggers", props=props,
        obj_names=['BO-Glob:TI-Mags-Corrs', 'SI-Glob:TI-Mags-Corrs'])
    win.setCentralWidget(list_ctrl)
    win.show()
    sys.exit(app.exec_())
