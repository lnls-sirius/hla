import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets import QSizePolicy as QSzPol
from PyQt5.QtWidgets import QPushButton
from pydm import PyDMApplication
from pydm.widgets.checkbox import PyDMCheckbox as PyDMCb
from pydm.widgets.enum_combo_box import PyDMEnumComboBox as PyDMECB
from pydm.widgets.label import PyDMLabel
from pydm.widgets.spinbox import PyDMSpinbox
from pydm.widgets.pushbutton import PyDMPushButton
from siriushla.widgets.led import PyDMLed, SiriusLedAlert
from siriushla.widgets.state_button import PyDMStateButton
from siriuspy.namesys import SiriusPVName as _PVName


class _BaseList(QGroupBox):
    """Template for control of High Level Triggers."""

    _MIN_WIDs = {}
    _LABELS = {}
    _ALL_PROPS = tuple()

    def __init__(self, name=None, parent=None, prefix='',
                 props=set(), obj_names=list()):
        """Initialize object."""
        super().__init__(name, parent)
        self.prefix = prefix
        self.props = props or set(self._ALL_PROPS)
        self.obj_names = obj_names
        self.setupUi()

    def setupUi(self):
        self.my_layout = QGridLayout(self)
        self.my_layout.setVerticalSpacing(30)
        self.my_layout.setHorizontalSpacing(30)

        objs = self.getLine(header=True)
        for j, obj in enumerate(objs):
            self.my_layout.addItem(obj, 0, j)
        for i, obj_name in enumerate(self.obj_names, 1):
            pref = _PVName(self.prefix + obj_name)
            objs = self.getLine(pref)
            for j, obj in enumerate(objs):
                self.my_layout.addItem(obj, i, j)

    def getLine(self, prefix=None, header=False):
        objects = list()
        for prop in self._ALL_PROPS:
            item = self.getColumn(prefix, prop, header)
            if item is not None:
                objects.append(item)
        return objects

    def getColumn(self, prefix, prop, header):
        if prop not in self.props:
            return
        lv = QVBoxLayout()
        lv.setAlignment(Qt.AlignHCenter)
        fun = self._createObjs if not header else self._headerLabel
        objs = fun(prefix, prop)
        for ob in objs:
            lv.addWidget(ob)
            ob.setMinimumWidth(self._MIN_WIDs[prop])
            ob.setSizePolicy(QSzPol.Minimum, QSzPol.Maximum)
        return lv

    def _headerLabel(self, prefix, prop):
        lb = QLabel(self._LABELS[prop], self)
        lb.setAlignment(Qt.AlignHCenter)
        return (lb, )

    def _createObjs(self, prefix, prop):
        return tuple()  # return tuple of widgets


class EventList(_BaseList):
    """Template for control of Events."""

    _MIN_WIDs = {'ext_trig': 150, 'mode': 205, 'delay_type': 130, 'delay': 150}
    _LABELS = {'ext_trig': 'Ext. Trig.', 'mode': 'Mode',
               'delay_type': 'Type', 'delay': 'Delay [us]'}
    _ALL_PROPS = ('ext_trig', 'mode', 'delay_type', 'delay')

    def _createObjs(self, prefix, prop):
        if 'ext_trig' == prop:
            sp = PyDMPushButton(self, init_channel=prefix+'ExtTrig-Cmd',
                                pressValue=1)
            sp.setText(prefix.propty)
            return (sp, )
        elif 'mode' == prop:
            sp = PyDMECB(self, init_channel=prefix + "Mode-Sel")
            # rb = PyDMLabel(self, init_channel=prefix + "Mode-Sts")
            return (sp, )
        elif 'delay_type' == prop:
            sp = PyDMECB(self, init_channel=prefix+"DelayType-Sel")
            # rb = PyDMLabel(self, init_channel=prefix+"DelayType-Sts")
            return (sp, )
        elif 'delay' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "Delay-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "Delay-RB")
        return sp, rb


class ClockList(_BaseList):
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

    def _createObjs(self, prefix, prop):
        if 'state' == prop:
            sp = PyDMCb(self, init_channel=prefix + "State-Sel")
            sp.setText(prefix.propty)
            # rb = PyDMLed(self, init_channel=prefix + "State-Sts")
            return (sp, )
        elif 'frequency' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "Freq-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "Freq-RB")
        return sp, rb


class HLTriggerList(_BaseList):
    """Template for control of High Level Triggers."""

    _MIN_WIDs = {
        'detailed': 280,
        'status': 150,
        'state': 120,
        'interlock': 200,
        'source': 150,
        'pulses': 100,
        'duration': 190,
        'polarity': 150,
        'delay_type': 130,
        'delay': 170,
        }
    _LABELS = {
        'detailed': 'Detailed View',
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
        'detailed', 'state', 'interlock', 'source', 'polarity', 'pulses',
        'duration', 'delay_type', 'delay', 'status',
        )

    def _createObjs(self, prefix, prop):
        if 'detailed' == prop:
            but = (QPushButton(prefix.device_name, self), )
        elif 'status' == prop:
            rb = SiriusLedAlert(self, init_channel=prefix + "Status-Mon")
            rb.setShape(rb.shapeMap.Square)
            but = (rb, )
        elif 'state' == prop:
            sp = PyDMStateButton(self, init_channel=prefix + "State-Sel")
            # rb = PyDMLed(self, init_channel=prefix + "State-Sts")
            but = (sp, )
        elif 'interlock' == prop:
            but = (PyDMCb(self, init_channel=prefix + "Intlk-Sel"),
                   PyDMLed(self, init_channel=prefix + "Intlk-Sts"))
        elif 'source' == prop:
            sp = PyDMECB(self, init_channel=prefix + "Src-Sel")
            # rb = PyDMLabel(self, init_channel=prefix+"Src-Sts")
            but = (sp, )
        elif 'pulses' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "Pulses-SP")
            sp.showStepExponent = False
            # rb = PyDMLabel(self, init_channel=prefix + "Pulses-RB")
            but = (sp, )
        elif 'duration' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "Duration-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "Duration-RB")
            but = (sp, rb)
        elif 'polarity' == prop:
            sp = PyDMECB(self, init_channel=prefix + "Polarity-Sel")
            # rb = PyDMLabel(self, init_channel=prefix+"Polarity-Sts")
            but = (sp, )
        elif 'delay_type' == prop:
            but = (PyDMECB(self, init_channel=prefix+"DelayType-Sel"),
                   PyDMLabel(self, init_channel=prefix+"DelayType-Sts"))
        elif 'delay' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "Delay-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "Delay-RB")
            but = (sp, rb)
        else:
            raise Exception('Property unknown')
        return but


class AFCOUTList(_BaseList):
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

    def _createObjs(self, prefix, prop):
        if 'state' == prop:
            sp = PyDMCb(self, init_channel=prefix + "State-Sel")
            rb = PyDMLed(self, init_channel=prefix + "State-Sts")
        elif 'event' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + 'Evt-SP')
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + 'Evt-RB')
        elif 'source' == prop:
            sp = PyDMECB(self, init_channel=prefix + 'Src-SP')
            rb = PyDMLabel(self, init_channel=prefix + 'Src-RB')
        elif 'width' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix+"Width-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix+"Width-RB")
        elif 'polarity' == prop:
            sp = PyDMECB(self, init_channel=prefix + "Polarity-Sel")
            rb = PyDMLabel(self, init_channel=prefix+"Polarity-Sts")
        elif 'pulses' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "Pulses-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "Pulses-RB")
        elif 'delay' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "Delay-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "Delay-RB")
        return sp, rb


class OTPList(_BaseList):
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

    def _createObjs(self, prefix, prop):
        if 'state' == prop:
            sp = PyDMCb(self, init_channel=prefix + "State-Sel")
            rb = PyDMLed(self, init_channel=prefix + "State-Sts")
        elif 'event' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + 'Evt-SP')
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + 'Evt-RB')
        elif 'width' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix+"Width-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix+"Width-RB")
        elif 'polarity' == prop:
            sp = PyDMECB(self, init_channel=prefix + "Polarity-Sel")
            rb = PyDMLabel(self, init_channel=prefix+"Polarity-Sts")
        elif 'pulses' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "Pulses-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "Pulses-RB")
        elif 'delay' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "Delay-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "Delay-RB")
        return sp, rb


class OUTList(_BaseList):
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

    def _createObjs(self, prefix, prop):
        if 'interlock' == prop:
            sp = PyDMCb(self, init_channel=prefix + "Intlk-Sel")
            rb = PyDMLed(self, init_channel=prefix + "Intlk-Sts")
        elif 'source' == prop:
            sp = PyDMECB(self, init_channel=prefix+"Src-Sel")
            rb = PyDMLabel(self, init_channel=prefix + "Src-Sts")
        elif 'trigger' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "SrcTrig-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "SrcTrig-RB")
        elif 'rf_delay' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "RFDelay-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "RFDelay-RB")
        elif 'fine_delay' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "FineDelay-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "FineDelay-RB")
        return rb, sp


if __name__ == '__main__':
    """Run Example."""
    app = PyDMApplication()
    ev_ctrl = EventList(prefix='AS-Glob:TI-EVG:Linac')
    ev_ctrl.show()
    props = {'evg_param', 'state', 'pulses', 'duration'}
    cl_ctrl = HLTriggerList(prefix='SI-Glob:TI-Corrs:', props=props)
    cl_ctrl.show()
    sys.exit(app.exec_())
