import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout
from PyQt5.QtWidgets import QSpacerItem as QSpIt
from PyQt5.QtWidgets import QSizePolicy as QSzPol
from pydm import PyDMApplication
from pydm.widgets.checkbox import PyDMCheckbox as PyDMCb
from pydm.widgets.enum_combo_box import PyDMEnumComboBox as PyDMECB
from pydm.widgets.label import PyDMLabel
from pydm.widgets.spinbox import PyDMSpinbox
from pydm.widgets.pushbutton import PyDMPushButton
from siriushla.widgets.led import PyDMLed, SiriusLedAlert
from siriuspy.namesys import SiriusPVName as _PVName


class _BaseCntrler(QGroupBox):
    """Template for control of High Level Triggers."""

    _MIN_WIDs = {}
    _LABELS = {}
    _ALL_PROPS = tuple()

    def __init__(self, parent=None, prefix='', props=set(), header=False):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self.props = props or set(self._ALL_PROPS)
        self.header = header
        self.setupUi()

    def setupUi(self):
        self.lh = QHBoxLayout(self)
        self.setLayout(self.lh)
        self.setSizePolicy(QSzPol.Expanding, QSzPol.Maximum)
        # self.setContentsMargins(0, 0, 0, 0)
        spc = QSpIt(5, 5, QSzPol.Expanding, QSzPol.Minimum)
        self.lh.addItem(spc)
        for prop in self._ALL_PROPS:
            self.addColumn(prop)

    def addColumn(self, prop):
        if prop not in self.props:
            return
        lv = QVBoxLayout()
        lv.setAlignment(Qt.AlignHCenter)
        fun = self._createObjs if not self.header else self._headerLabel
        objs = fun(prop)
        for ob in objs:
            lv.addWidget(ob)
            # lv.setStretch(self._MIN_WIDs[prop], 1)
            ob.setMinimumWidth(self._MIN_WIDs[prop])
            ob.setSizePolicy(QSzPol.Minimum, QSzPol.Maximum)
        spc = QSpIt(5, 5, QSzPol.Expanding, QSzPol.Minimum)
        self.lh.addItem(lv)
        # self.lh.addItem(spc)

    def _headerLabel(self, prop):
        lb = QLabel(self._LABELS[prop], self)
        lb.setAlignment(Qt.AlignHCenter)
        return (lb, )

    def _createObjs(self, prop):
        return tuple()  # return tuple of objects


class EventCntrler(_BaseCntrler):
    """Template for control of Events."""

    _MIN_WIDs = {'ext_trig': 200, 'mode': 220, 'delay_type': 90, 'delay': 150}
    _LABELS = {'ext_trig': 'Ext. Trig.', 'mode': 'Mode',
               'delay_type': 'Type', 'delay': 'Delay [us]'}
    _ALL_PROPS = ('ext_trig', 'mode', 'delay_type', 'delay')

    def _createObjs(self, prop):
        pv_pref = self.prefix
        if 'ext_trig' == prop:
            sp = PyDMPushButton(self, init_channel=pv_pref+'ExtTrig-Cmd',
                                pressValue=1)
            sp.setText(self.prefix.propty)
            return (sp, )
        elif 'mode' == prop:
            sp = PyDMECB(self, init_channel=pv_pref + "Mode-Sel")
            # rb = PyDMLabel(self, init_channel=pv_pref + "Mode-Sts")
            return (sp, )
        elif 'delay_type' == prop:
            sp = PyDMECB(self, init_channel=pv_pref+"DelayType-Sel")
            # rb = PyDMLabel(self, init_channel=pv_pref+"DelayType-Sts")
            return (sp, )
        elif 'delay' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref + "Delay-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=pv_pref + "Delay-RB")
        return sp, rb


class ClockCntrler(_BaseCntrler):
    """Template for control of High and Low Level Clocks."""

    _MIN_WIDs = {
        'state': 150,
        'frequency': 150,
        }
    _LABELS = {
        'state': 'Enabled',
        'frequency': 'Freq. [kHz]',
        }
    _ALL_PROPS = ('state', 'frequency')

    def _createObjs(self, prop):
        pv_pref = self.prefix
        if 'state' == prop:
            sp = PyDMCb(self, init_channel=pv_pref + "State-Sel")
            sp.setText(self.prefix.propty)
            # rb = PyDMLed(self, init_channel=pv_pref + "State-Sts")
            return (sp, )
        elif 'frequency' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref + "Freq-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=pv_pref + "Freq-RB")
        return sp, rb


class HLTrigCntrler(_BaseCntrler):
    """Template for control of High Level Triggers."""

    _MIN_WIDs = {
        'status': 200,
        'state': 300,
        'interlock': 200,
        'source': 120,
        'pulses': 100,
        'duration': 230,
        'polarity': 130,
        'delay_type': 130,
        'delay': 200,
        }
    _LABELS = {
        'status': 'Status',
        'state': 'Enabled',
        'interlock': 'Interlock',
        'source': 'Source',
        'pulses': 'Pulses',
        'duration': 'Duration [ms]',
        'polarity': 'Polarity',
        'delay_type': 'Type',
        'delay': 'Delay [us]',
        }
    _ALL_PROPS = (
        'state', 'interlock', 'source', 'polarity', 'pulses',
        'duration', 'delay_type', 'delay', 'status',
        )

    def _createObjs(self, prop):
        pv_pref = self.prefix
        if 'status' == prop:
            rb = SiriusLedAlert(self, init_channel=pv_pref + "Status-Mon")
            rb.setShape(rb.shapeMap.Square)
            return (rb, )
        elif 'state' == prop:
            sp = PyDMCb(self, init_channel=pv_pref + "State-Sel")
            sp.setText(self.prefix.device_name)
            # rb = PyDMLed(self, init_channel=pv_pref + "State-Sts")
            return (sp, )
        elif 'interlock' == prop:
            sp = PyDMCb(self, init_channel=pv_pref + "Intlk-Sel")
            rb = PyDMLed(self, init_channel=pv_pref + "Intlk-Sts")
        elif 'source' == prop:
            sp = PyDMECB(self, init_channel=pv_pref + "Src-Sel")
            # rb = PyDMLabel(self, init_channel=pv_pref+"Src-Sts")
            return (sp, )
        elif 'pulses' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref + "Pulses-SP")
            sp.showStepExponent = False
            # rb = PyDMLabel(self, init_channel=pv_pref + "Pulses-RB")
            return (sp, )
        elif 'duration' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref + "Duration-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=pv_pref + "Duration-RB")
        elif 'polarity' == prop:
            sp = PyDMECB(self, init_channel=pv_pref + "Polarity-Sel")
            # rb = PyDMLabel(self, init_channel=pv_pref+"Polarity-Sts")
            return (sp, )
        elif 'delay_type' == prop:
            sp = PyDMECB(self, init_channel=pv_pref+"DelayType-Sel")
            rb = PyDMLabel(self, init_channel=pv_pref+"DelayType-Sts")
        elif 'delay' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref + "Delay-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=pv_pref + "Delay-RB")
        else:
            raise Exception('Property unknown')
        return sp, rb


class AFCOUTCntrler(_BaseCntrler):
    """Template for control of Timing devices Internal Triggers."""

    _MIN_WIDs = {
        'state': 200,
        'event': 100,
        'source': 100,
        'width': 150,
        'polarity': 70,
        'pulses': 70,
        'delay': 150,
        }
    _LABELS = {
        'state': 'State',
        'event': 'Event',
        'source': 'Source',
        'width': 'Width',
        'polarity': 'Polarity',
        'pulses': 'Nr Pulses',
        'delay': 'Delay',
        }
    _ALL_PROPS = (
        'state', 'event', 'source', 'width', 'polarity', 'pulses', 'delay',
        )

    def _createObjs(self, prop):
        pv_pref = self.prefix
        if 'state' == prop:
            sp = PyDMCb(self, init_channel=pv_pref + "State-Sel")
            rb = PyDMLed(self, init_channel=pv_pref + "State-Sts")
        elif 'event' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref + 'Evt-SP')
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=pv_pref + 'Evt-RB')
        elif 'source' == prop:
            sp = PyDMECB(self, init_channel=pv_pref + 'Src-SP')
            rb = PyDMLabel(self, init_channel=pv_pref + 'Src-RB')
        elif 'width' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref+"Width-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=pv_pref+"Width-RB")
        elif 'polarity' == prop:
            sp = PyDMECB(self, init_channel=pv_pref + "Polarity-Sel")
            rb = PyDMLabel(self, init_channel=pv_pref+"Polarity-Sts")
        elif 'pulses' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref + "Pulses-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=pv_pref + "Pulses-RB")
        elif 'delay' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref + "Delay-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=pv_pref + "Delay-RB")
        return sp, rb


class OTPCntrler(_BaseCntrler):
    """Template for control of Timing devices Internal Triggers."""

    _MIN_WIDs = {
        'state': 200,
        'event': 100,
        'width': 150,
        'polarity': 70,
        'pulses': 70,
        'delay': 150,
        }
    _LABELS = {
        'state': 'State',
        'event': 'Event',
        'width': 'Width',
        'polarity': 'Polarity',
        'pulses': 'Nr Pulses',
        'delay': 'Delay',
        }
    _ALL_PROPS = (
        'state', 'event', 'width', 'polarity', 'pulses', 'delay',
        )

    def _createObjs(self, prop):
        pv_pref = self.prefix
        if 'state' == prop:
            sp = PyDMCb(self, init_channel=pv_pref + "State-Sel")
            rb = PyDMLed(self, init_channel=pv_pref + "State-Sts")
        elif 'event' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref + 'Evt-SP')
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=pv_pref + 'Evt-RB')
        elif 'width' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref+"Width-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=pv_pref+"Width-RB")
        elif 'polarity' == prop:
            sp = PyDMECB(self, init_channel=pv_pref + "Polarity-Sel")
            rb = PyDMLabel(self, init_channel=pv_pref+"Polarity-Sts")
        elif 'pulses' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref + "Pulses-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=pv_pref + "Pulses-RB")
        elif 'delay' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref + "Delay-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=pv_pref + "Delay-RB")
        return sp, rb


class OUTCntrler(_BaseCntrler):
    """Template for control of Timing Devices Output Channels."""

    _MIN_WIDs = {
        'interlock': 200,
        'source': 200,
        'trigger': 200,
        'rf_delay': 150,
        'fine_delay': 150,
        }
    _LABELS = {
        'interlock': 'Interlock',
        'source': 'Source',
        'trigger': 'Trigger',
        'rf_delay': 'RF Delay',
        'fine_delay': 'Fine Delay',
        }
    _ALL_PROPS = (
        'interlock', 'source', 'trigger', 'rf_delay', 'fine_delay',
        )

    def _createObjs(self, prop):
        pv_pref = self.prefix
        if 'interlock' == prop:
            sp = PyDMCb(self, init_channel=pv_pref + "Intlk-Sel")
            rb = PyDMLed(self, init_channel=pv_pref + "Intlk-Sts")
        elif 'source' == prop:
            sp = PyDMECB(self, init_channel=pv_pref+"Src-Sel")
            rb = PyDMLabel(self, init_channel=pv_pref + "Src-Sts")
        elif 'trigger' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref + "SrcTrig-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=pv_pref + "SrcTrig-RB")
        elif 'rf_delay' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref + "RFDelay-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=pv_pref + "RFDelay-RB")
        elif 'fine_delay' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref + "FineDelay-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=pv_pref + "FineDelay-RB")
        return rb, sp


if __name__ == '__main__':
    """Run Example."""
    app = PyDMApplication()
    ev_ctrl = EventCntrler(prefix='AS-Glob:TI-EVG:Linac')
    ev_ctrl.show()
    props = {'evg_param', 'state', 'pulses', 'duration'}
    cl_ctrl = HLTrigCntrler(prefix='SI-Glob:TI-Corrs:', props=props)
    cl_ctrl.show()
    sys.exit(app.exec_())
