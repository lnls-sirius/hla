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
from siriushla.widgets.led import PyDMLed
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.timesys.time_data import Events as _Events
from siriuspy.timesys.time_data import Clocks as _Clocks


class PseudoPyDMECB(PyDMECB):

    def value_changed(self, new_val):
        if isinstance(new_val, str) and self.combo_box.findText(new_val) >= 0:
            new_val = self.combo_box.findText(new_val)
        super(PseudoPyDMECB, self).value_changed(new_val)

    def internal_combo_box_activated_int(self, index):
        self.activated[int].emit(index)

    def internal_combo_box_activated_str(self, text):
        self.send_value_signal[str].emit(text)
        self.activated[str].emit(text)


class _BaseCntrler(QGroupBox):
    """Template for control of High Level Triggers."""

    _MIN_WIDs = {}
    _LABELS = {}
    _ALL_PROPS = tuple()

    def __init__(self, parent=None, prefix='', props=set(), header=False):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self.props = props
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
        if not self.header:
            lv = QVBoxLayout()
            lv.setAlignment(Qt.AlignHCenter)
            objs = self._createObjs(prop)
            for ob in objs:
                lv.addWidget(ob)
            self.lh.addItem(lv)
        else:
            ob = self._headerLabel(prop)
            self.lh.addWidget(ob)
            objs = (ob, )
        for ob in objs:
            ob.setMinimumWidth(self._MIN_WIDs[prop])
            ob.setSizePolicy(QSzPol.Minimum, QSzPol.Maximum)
        spc = QSpIt(5, 5, QSzPol.Expanding, QSzPol.Minimum)
        self.lh.addItem(spc)

    def _headerLabel(self, prop):
        lb = QLabel(self._LABELS[prop], self)
        lb.setAlignment(Qt.AlignHCenter)
        return lb

    def _createObjs(self, prop):
        return tuple()  # return tuple of objects


class EventCntrler(_BaseCntrler):
    """Template for control of Events."""

    _MIN_WIDs = {'ext_trig': 120, 'mode': 190, 'delay_type': 90, 'delay': 100}
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
            rb = PyDMLabel(self, init_channel=pv_pref + "Mode-Sts")
        elif 'delay_type' == prop:
            sp = PyDMECB(self, init_channel=pv_pref+"DelayType-Sel")
            rb = PyDMLabel(self, init_channel=pv_pref+"DelayType-Sts")
        elif 'duration' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref + "Delay-SP")

            rb = PyDMLabel(self, init_channel=pv_pref + "Delay-RB")
        elif 'polarity' == prop:
            sp = PyDMECB(self, init_channel=pv_pref + "Polrty-Sel")
            rb = PyDMLabel(self, init_channel=pv_pref+"Polrty-Sts")
        elif 'delay' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref + "Delay-SP")
            rb = PyDMLabel(self, init_channel=pv_pref + "Delay-RB")
        return sp, rb


class HLTrigCntrler(_BaseCntrler):
    """Template for control of High Level Triggers."""

    _MIN_WIDs = {'state': 300, 'evg_param': 120, 'pulses': 100,
                 'duration': 230, 'polarity': 130, 'delay': 260,
                 'delay_type': 130}
    _LABELS = {'state': 'Enabled', 'evg_param': 'Param', 'pulses': 'Pulses',
               'duration': 'Duration [ms]', 'polarity': 'Polarity',
               'delay': 'Delay [us]', 'delay_type': 'Type'}
    _ALL_PROPS = ('state', 'evg_param', 'pulses', 'duration', 'polarity',
                  'delay_type', 'delay')

    def _createObjs(self, prop):
        pv_pref = self.prefix
        if 'state' == prop:
            sp = PyDMCb(self, init_channel=pv_pref + "State-Sel")
            sp.setText(self.prefix.dev_name)
            rb = PyDMLed(self, init_channel=pv_pref + "State-Sts")
        elif 'evg_param' == prop:
            sp = PyDMECB(self, init_channel=pv_pref + "EVGParam-Sel")
            rb = PyDMLabel(self, init_channel=pv_pref+"EVGParam-Sts")
        elif 'pulses' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref + "Pulses-SP")
            rb = PyDMLabel(self, init_channel=pv_pref + "Pulses-RB")
        elif 'duration' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref + "Duration-SP")
            rb = PyDMLabel(self, init_channel=pv_pref + "Duration-RB")
        elif 'polarity' == prop:
            sp = PyDMECB(self, init_channel=pv_pref + "Polrty-Sel")
            rb = PyDMLabel(self, init_channel=pv_pref+"Polrty-Sts")
        elif 'delay_type' == prop:
            sp = PyDMECB(self, init_channel=pv_pref+"DelayType-Sel")
            rb = PyDMLabel(self, init_channel=pv_pref+"DelayType-Sts")
        elif 'delay' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref + "Delay-SP")
            rb = PyDMLabel(self, init_channel=pv_pref + "Delay-RB")
        return sp, rb


class ClockCntrler(_BaseCntrler):
    """Template for control of High and Low Level Clocks."""

    _MIN_WIDs = {'state': 150, 'frequency': 150}
    _LABELS = {'state': 'Enabled', 'frequency': 'Freq. [kHz]'}
    _ALL_PROPS = ('state', 'frequency')

    def _createObjs(self, prop):
        pv_pref = self.prefix
        if 'state' == prop:
            sp = PyDMCb(self, init_channel=pv_pref + "State-Sel")
            sp.setText(self.prefix.propty)
            rb = PyDMLed(self, init_channel=pv_pref + "State-Sts")
        elif 'frequency' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref + "Freq-SP")
            rb = PyDMLabel(self, init_channel=pv_pref + "Freq-RB")
        return sp, rb


class IntTrigCntrler(_BaseCntrler):
    """Template for control of Timing devices Internal Triggers."""

    _MIN_WIDs = {'state': 200, 'evg_param': 100, 'pulses': 70, 'width': 150,
                 'polarity': 70, 'delay': 150}
    _LABELS = {'state': 'State', 'evg_param': 'EVG Params',
               'pulses': 'Nr Pulses', 'width': 'Width',
               'polarity': 'Polarity', 'delay': 'Delay'}
    _ALL_PROPS = ('state', 'evg_param', 'pulses', 'width', 'polarity',
                  'delay')

    def __init__(self, parent=None, prefix='', props=set(), header=False,
                 device='evr'):
        """Initialize object."""
        self.device = device
        super().__init__(parent, prefix, props, header)

    def _createObjs(self, prop):
        pv_pref = self.prefix
        if 'state' == prop:
            sp = PyDMCb(self, init_channel=pv_pref + "State-Sel")
            rb = PyDMLed(self, init_channel=pv_pref + "State-Sts")
        elif 'evg_param' == prop:
            name = pv_pref + 'Event'
            enum_strings = _Events.LL_EVENTS
            if self.device.lower() == 'afc':
                name = pv_pref + 'EVGParam'
                enum_strings += sorted(_Clocks.LL2HL_MAP.keys())
            sp = PseudoPyDMECB(self, init_channel=name + "-Sel")
            sp.enum_strings_changed(enum_strings)
            sp.combo_box.setEditable(True)
            rb = PyDMLabel(self, init_channel=name + "-Sts")
        elif 'pulses' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref + "Pulses-SP")
            rb = PyDMLabel(self, init_channel=pv_pref + "Pulses-RB")
        elif 'width' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref+"Width-SP")
            rb = PyDMLabel(self, init_channel=pv_pref+"Width-RB")
        elif 'polarity' == prop:
            sp = PyDMECB(self, init_channel=pv_pref + "Polrty-Sel")
            rb = PyDMLabel(self, init_channel=pv_pref+"Polrty-Sts")
        elif 'delay' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref + "Delay-SP")
            rb = PyDMLabel(self, init_channel=pv_pref + "Delay-RB")
        return sp, rb


class OutChanCntrler(QGroupBox):
    """Template for control of Timing Devices Output Channels."""

    _MIN_WIDs = {'int_chan': 200, 'delay': 150, 'fine_delay': 150}
    _LABELS = {'int_chan': 'Inter. Trig.', 'delay': 'RFDelay',
               'fine_delay': 'Fine Delay'}
    _ALL_PROPS = ('int_chan', 'delay', 'fine_delay')

    def __init__(self, parent=None, prefix='', props=set(), header=False,
                 device='evr'):
        """Initialize object."""
        self.device = device
        super().__init__(parent, prefix, props, header)

    def _createObjs(self, prop):
        pv_pref = self.prefix
        if 'int_chan' == prop:
            num = 24 if self.device.lower() == 'evr' else 16
            enum_strings = (['IntTrig{0:02d}'.format(i) for i in range(num)] +
                            sorted(_Clocks.LL2HL_MAP.keys()))
            sp = PseudoPyDMECB(self, init_channel=pv_pref+"IntChan-Sel")
            sp.enum_strings_changed(enum_strings)
            sp.combo_box.setEditable(True)
            # sp.setMaxVisibleItems(6)
            rb = PyDMLabel(self, init_channel=pv_pref + "IntChan-Sts")
        elif 'delay' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref + "RFDelay-SP")
            rb = PyDMLabel(self, init_channel=pv_pref + "RFDelay-RB")
        elif 'fine_delay' == prop:
            sp = PyDMSpinbox(self, init_channel=pv_pref + "FineDelay-SP")
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
