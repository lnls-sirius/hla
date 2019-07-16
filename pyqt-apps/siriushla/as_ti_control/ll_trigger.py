import sys
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QPushButton
from pydm.widgets import PyDMLabel
from siriuspy.search import LLTimeSearch
from siriushla.widgets import PyDMLed, PyDMStateButton
from siriushla.util import connect_window
from siriushla.widgets.windows import create_window_from_widget
from siriushla import as_ti_control as _ti_ctrl
from .base import BaseList, \
    MySpinBox as _MySpinBox, MyComboBox as _MyComboBox


class LLTriggerList(BaseList):
    """Template for control of High Level Triggers."""

    _MIN_WIDs = {
        'name': 3.2,
        'device': 12,
        'state': 5.8,
        'event': 4.8,
        'widthraw': 4.8,
        'width': 4.8,
        'polarity': 5,
        'pulses': 4.8,
        'delayraw': 4.8,
        'delay': 4.8,
        'timestamp': 3.2,
        'source': 6.5,
        'trigger': 4,
        'rf_delayraw': 4.8,
        'rf_delay': 4.8,
        'fine_delayraw': 4.8,
        'fine_delay': 4.8,
        'rf_delay_type': 6.5,
        }
    _LABELS = {
        'name': 'Name',
        'device': 'Device',
        'state': 'State',
        'event': 'Event',
        'widthraw': 'Width',
        'width': 'Width [us]',
        'polarity': 'Polarity',
        'pulses': 'Nr Pulses',
        'delayraw': 'Delay',
        'delay': 'Delay [us]',
        'timestamp': 'Log',
        'source': 'Source',
        'trigger': 'Trigger',
        'rf_delayraw': 'RF Delay',
        'rf_delay': 'RF Delay [ns]',
        'fine_delayraw': 'Fine Delay',
        'fine_delay': 'Fine Delay [ps]',
        'rf_delay_type': 'RF Delay Type',
        }
    _ALL_PROPS = (
        'device', 'name', 'state', 'event', 'widthraw', 'width',
        'polarity', 'pulses', 'delayraw', 'delay', 'timestamp', 'source',
        'trigger', 'rf_delayraw', 'rf_delay', 'rf_delay_type', 'fine_delayraw',
        'fine_delay')

    def __init__(self, **kwargs):
        srch = set(('device', 'name', 'polarity', 'source'))
        kwargs['props2search'] = srch
        super().__init__(**kwargs)

    def _createObjs(self, prefix, prop):
        intlb = LLTimeSearch.get_channel_internal_trigger_pvname(prefix)
        outlb = LLTimeSearch.get_channel_output_port_pvname(prefix)
        sp = rb = None
        if prop == 'device':
            devt = outlb.dev
            if devt == 'EVR':
                devt = _ti_ctrl.EVR
            elif devt == 'EVE':
                devt = _ti_ctrl.EVE
            else:
                devt = _ti_ctrl.AFC
            sp = QPushButton(outlb.device_name, self)
            sp.setAutoDefault(False)
            sp.setDefault(False)
            Win = create_window_from_widget(devt, title=outlb.device_name)
            connect_window(sp, Win, None, prefix=outlb.device_name + ':')
        elif prop == 'name':
            sp = QLabel(outlb.propty, self)
            sp.setAlignment(Qt.AlignCenter)
        elif prop == 'state':
            pvname = intlb.substitute(propty=intlb.propty+"State-Sel")
            sp = PyDMStateButton(self, init_channel=pvname)
            pvname = intlb.substitute(propty=intlb.propty+"State-Sts")
            rb = PyDMLed(self, init_channel=pvname)
        elif prop == 'event':
            pvname = intlb.substitute(propty=intlb.propty+'Evt-SP')
            sp = _MySpinBox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = intlb.substitute(propty=intlb.propty+'Evt-RB')
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'widthraw':
            pvname = intlb.substitute(propty=intlb.propty+"WidthRaw-SP")
            sp = _MySpinBox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = intlb.substitute(propty=intlb.propty+"WidthRaw-RB")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'width':
            pvname = intlb.substitute(propty=intlb.propty+"Width-SP")
            sp = _MySpinBox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = intlb.substitute(propty=intlb.propty+"Width-RB")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'polarity':
            pvname = intlb.substitute(propty=intlb.propty+"Polarity-Sel")
            sp = _MyComboBox(self, init_channel=pvname)
            pvname = intlb.substitute(propty=intlb.propty+"Polarity-Sts")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'pulses':
            pvname = intlb.substitute(propty=intlb.propty+"NrPulses-SP")
            sp = _MySpinBox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = intlb.substitute(propty=intlb.propty+"NrPulses-RB")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'delayraw':
            pvname = intlb.substitute(propty=intlb.propty+"DelayRaw-SP")
            sp = _MySpinBox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = intlb.substitute(propty=intlb.propty+"DelayRaw-RB")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'delay':
            pvname = intlb.substitute(propty=intlb.propty+"Delay-SP")
            sp = _MySpinBox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = intlb.substitute(propty=intlb.propty+"Delay-RB")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'timestamp':
            pvname = intlb.substitute(propty=intlb.propty+"Log-Sel")
            sp = PyDMStateButton(self, init_channel=pvname)
            pvname = intlb.substitute(propty=intlb.propty+"Log-Sts")
            rb = PyDMLed(self, init_channel=pvname)
        elif prop == 'source':
            pvname = outlb.substitute(propty=outlb.propty+"Src-Sel")
            sp = _MyComboBox(self, init_channel=pvname)
            pvname = outlb.substitute(propty=outlb.propty+"Src-Sts")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'trigger':
            pvname = outlb.substitute(propty=outlb.propty+"SrcTrig-SP")
            sp = _MySpinBox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = outlb.substitute(propty=outlb.propty+"SrcTrig-RB")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'rf_delayraw':
            pvname = outlb.substitute(propty=outlb.propty+"RFDelayRaw-SP")
            sp = _MySpinBox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = outlb.substitute(propty=outlb.propty+"RFDelayRaw-RB")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'rf_delay':
            pvname = outlb.substitute(propty=outlb.propty+"RFDelay-SP")
            sp = _MySpinBox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = outlb.substitute(propty=outlb.propty+"RFDelay-RB")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'rf_delay_type':
            pvname = outlb.substitute(propty=outlb.propty+"RFDelayType-Sel")
            sp = _MyComboBox(self, init_channel=pvname)
            pvname = outlb.substitute(propty=outlb.propty+"RFDelayType-Sts")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'fine_delayraw':
            pvname = outlb.substitute(propty=outlb.propty+"FineDelayRaw-SP")
            sp = _MySpinBox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = outlb.substitute(propty=outlb.propty+"FineDelayRaw-RB")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        elif prop == 'fine_delay':
            pvname = outlb.substitute(propty=outlb.propty+"FineDelay-SP")
            sp = _MySpinBox(self, init_channel=pvname)
            sp.showStepExponent = False
            pvname = outlb.substitute(propty=outlb.propty+"FineDelay-RB")
            rb = PyDMLabel(self, init_channel=pvname)
            rb.setAlignment(Qt.AlignCenter)
        if rb is None:
            return (sp, )
        return sp, rb


class OTPList(LLTriggerList):
    """Template for control of Timing devices Internal Triggers."""

    _ALL_PROPS = (
        'name', 'state', 'event', 'widthraw', 'polarity', 'pulses', 'delayraw',
        'timestamp')


class OUTList(LLTriggerList):
    """Template for control of Timing Devices Output Channels."""

    _ALL_PROPS = (
        'name', 'source', 'trigger', 'rf_delayraw', 'rf_delay_type',
        'fine_delayraw')


class AFCOUTList(LLTriggerList):
    """Template for control of Timing devices Internal Triggers."""

    _ALL_PROPS = (
        'name', 'state', 'event', 'source', 'width', 'polarity', 'pulses',
        'delay', 'timestamp')


if __name__ == '__main__':
    """Run Example."""
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets.windows import SiriusMainWindow

    props = {'device', 'name', 'state', 'pulses', 'width'}
    app = SiriusApplication()
    win = SiriusMainWindow()
    list_ctrl = LLTriggerList(
        name="Triggers", props=props,
        obj_names=['TEST-FAC:TI-EVR:OTP00', 'TEST-FAC:TI-EVE:OTP00'])
    win.setCentralWidget(list_ctrl)
    win.show()
    sys.exit(app.exec_())
