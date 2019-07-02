import sys
from copy import deepcopy as _dcopy
import numpy as _np
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGroupBox, QLabel, QPushButton, QFormLayout, \
    QVBoxLayout, QGridLayout, QSizePolicy as QSzPol, QWidget, QDoubleSpinBox, \
    QFrame, QScrollArea
from pydm.widgets import PyDMLabel
from pydm.widgets.base import PyDMWritableWidget
from siriuspy.search import HLTimeSearch
from siriuspy.csdevice import timesys
from siriushla.widgets import PyDMLed, SiriusLedAlert, PyDMStateButton, \
    SiriusLabel, SiriusSpinbox
from siriushla.util import connect_window
from siriushla.widgets.windows import create_window_from_widget
from .base import BaseList, BaseWidget, MySpinBox as _MySpinBox, \
    MyComboBox as _MyComboBox
from .ll_trigger import LLTriggerList, OTPList, OUTList, AFCOUTList


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
        Window = create_window_from_widget(
            LLTriggers, title=self.prefix.device_name+': LL Triggers')
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

        if HLTimeSearch.has_delay_type(prefix.device_name):
            init_channel = prefix.substitute(propty="RFDelayType-Sel")
            sp = _MyComboBox(self, init_channel=init_channel)
            init_channel = prefix.substitute(propty="RFDelayType-Sts")
            rb = PyDMLabel(self, init_channel=init_channel)
            gb = self._create_small_GB(
                        'Delay Type', self.ll_list_wid, (sp, rb))
            ll_list_layout.addWidget(gb, 4, 0)
            ll_list_layout.addWidget(gbdel, 4, 1)
        else:
            ll_list_layout.addWidget(gbdel, 4, 0, 1, 2)

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
        self.valueBeingSet = False
        PyDMWritableWidget.value_changed(self, value)

    def send_value(self):
        """
        Method invoked to send the current value on the QDoubleSpinBox to
        the channel using the `send_value_signal`.
        """
        value = QDoubleSpinBox.value(self)
        val = _dcopy(self.value)
        val[self._index] = value
        if not self.valueBeingSet:
            self.send_value_signal[_np.ndarray].emit(val)


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
            props.add('device')
            amc_wid = LLTriggerList(name='AMCs', parent=self, props=props,
                                    prefix=prefix, obj_names=amc_list)
            amc_wid.setObjectName('amc_wid')
            amc_wid.setStyleSheet("""#amc_wid{min-width:90em;}""")
            vl.addWidget(amc_wid)
        if otp_list:
            props = set(OTPList()._ALL_PROPS)
            props.add('device')
            otp_wid = LLTriggerList(name='OTPs', parent=self, props=props,
                                    prefix=prefix, obj_names=otp_list)
            otp_wid.setObjectName('otp_wid')
            otp_wid.setStyleSheet("""#otp_wid{min-width:56em;}""")
            vl.addWidget(otp_wid)
        if out_list:
            props = set(OTPList()._ALL_PROPS)
            for prop in OUTList()._ALL_PROPS:
                props.add(prop)
            props.add('device')
            out_wid = LLTriggerList(name='OUTs', parent=self, props=props,
                                    prefix=prefix, obj_names=out_list)
            out_wid.setObjectName('out_wid')
            out_wid.setStyleSheet("""#out_wid{min-width:110em;}""")
            vl.addWidget(out_wid)


class HLTriggerList(BaseList):
    """Template for control of High Level Triggers."""

    _MIN_WIDs = {
        'detailed': 10,
        'status': 4.8,
        'state': 3.8,
        'source': 4.8,
        'pulses': 4.8,
        'duration': 8,
        'polarity': 6,
        'delay_type': 4.2,
        'delay': 5.5,
        }
    _LABELS = {
        'detailed': 'Detailed View',
        'status': 'Status',
        'state': 'Enabled',
        'source': 'Source',
        'pulses': 'Nr Pulses',
        'duration': 'Duration [us]',
        'polarity': 'Polarity',
        'delay_type': 'Type',
        'delay': 'Delay [us]',
        }
    _ALL_PROPS = (
        'detailed', 'state', 'source', 'polarity', 'pulses',
        'duration', 'delay_type', 'delay', 'status',
        )

    def __init__(self, **kwargs):
        srch = set(('source', 'detailed', 'polarity', 'state'))
        kwargs['props2search'] = srch
        super().__init__(**kwargs)
        self.setObjectName('ASApp')

    def _createObjs(self, prefix, prop):
        sp = rb = None
        if prop == 'detailed':
            sp = QPushButton(prefix.device_name, self)
            Window = create_window_from_widget(
                HLTriggerDetailed,
                title=prefix.device_name+': HL Trigger Detailed')
            connect_window(sp, Window, self, prefix=prefix)
        elif prop == 'status':
            init_channel = prefix.substitute(propty="Status-Mon")
            sp = SiriusLedAlert(self, init_channel=init_channel)
            sp.setShape(sp.ShapeMap.Square)
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
        obj_names=['BO-Fam:TI-Corrs-1', 'BO-Fam:TI-Corrs-2'])
    win.setCentralWidget(list_ctrl)
    win.show()
    sys.exit(app.exec_())
