import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QLabel, QWidget, QScrollArea
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtWidgets import QSizePolicy as QSzPol
from pydm.widgets.label import PyDMLabel
from pydm.widgets.line_edit import PyDMLineEdit
from pydm.widgets.spinbox import PyDMSpinbox
from pydm.widgets.pushbutton import PyDMPushButton
from pydm.widgets.enum_combo_box import PyDMEnumComboBox as PyDMECB
from pydm.widgets.checkbox import PyDMCheckbox as PyDMCb
from siriuspy.timesys.time_data.hl_types_data import Events as _Events
from siriuspy.timesys.time_data.hl_types_data import Clocks as _Clocks
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets.led import PyDMLed, SiriusLedAlert
from siriushla.widgets.state_button import PyDMStateButton
from siriushla.widgets.windows import SiriusMainWindow
from siriuspy.namesys import SiriusPVName as _PVName
from siriushla import util as _util
from base_list import BaseList


class EVG(SiriusMainWindow):
    """Template for control of High Level Triggers."""

    def __init__(self, parent=None, prefix=''):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self._setupUi()

    def _setupUi(self):
        # self.resize(2000, 2000)
        cw = QWidget(self)
        self.setCentralWidget(cw)
        self.my_layout = QGridLayout(cw)
        self.my_layout.setHorizontalSpacing(20)
        self.my_layout.setVerticalSpacing(20)
        lab = QLabel('<h1>' + self.prefix.device_name + '</h1>', cw)
        self.my_layout.addWidget(lab, 0, 0, 1, 2)
        self.my_layout.setAlignment(lab, Qt.AlignCenter)

        scr_ar = QScrollArea(cw)
        # scr_ar.setSizePolicy(QSzPol.)
        self.events_wid = EventList(
            name='Events', parent=scr_ar, prefix=self.prefix,
            obj_names=sorted(_Events.LL_EVENTS)
            )
        scr_ar.setWidget(self.events_wid)
        scr_ar.setMinimumWidth(1150)
        scr_ar.setSizePolicy(QSzPol.Minimum, QSzPol.Preferred)
        self.my_layout.addWidget(scr_ar, 2, 0)

        self.clocks_wid = ClockList(
            name='Clocks', parent=self, prefix=self.prefix,
            props={'mux_div', 'mux_enbl'},
            obj_names=sorted(_Clocks.LL2HL_MAP.keys())
            )
        self.my_layout.addWidget(self.clocks_wid, 2, 1)

        self.configs_wid = QGroupBox('Configurations', self)
        self.my_layout.addWidget(self.configs_wid, 1, 0)
        self._setup_configs_wid()

        self.status_wid = QGroupBox('Status', self)
        self.my_layout.addWidget(self.status_wid, 1, 1)
        self._setup_status_wid()

    def _setup_configs_wid(self):
        prefix = self.prefix
        configs_layout = QGridLayout(self.configs_wid)
        configs_layout.setHorizontalSpacing(30)
        configs_layout.setVerticalSpacing(30)

        sp = PyDMStateButton(self, init_channel=prefix + "DevEnbl-Sel")
        rb = PyDMLed(self, init_channel=prefix + "DevEnbl-Sts")
        rb.setMinimumHeight(40)
        rb.setSizePolicy(QSzPol.Preferred, QSzPol.Minimum)
        gb = self._create_small_GB(
            'Enabled', self.configs_wid, (sp, rb), align_ver=False
            )
        configs_layout.addWidget(gb, 0, 0)

        sp = PyDMStateButton(self, init_channel=prefix + "ContinuousEvt-Sel")
        rb = PyDMLed(self, init_channel=prefix + "ContinuousEvt-Sts")
        gb = self._create_small_GB(
            'Continuous', self.configs_wid, (sp, rb), align_ver=False
            )
        configs_layout.addWidget(gb, 0, 1)

        sp = PyDMStateButton(self, init_channel=prefix + "InjectionEvt-Sel")
        rb = PyDMLed(self, init_channel=prefix + "InjectionEvt-Sts")
        gb = self._create_small_GB(
            'Injection', self.configs_wid, (sp, rb), align_ver=False
            )
        configs_layout.addWidget(gb, 0, 2)

        sp = PyDMSpinbox(self, init_channel=prefix + "ACDiv-SP")
        sp.showStepExponent = False
        rb = PyDMLabel(self, init_channel=prefix + "ACDiv-RB")
        gb = self._create_small_GB(
            'AC Divisor', self.configs_wid, (sp, rb), align_ver=False)
        configs_layout.addWidget(gb, 1, 0)

        sp = PyDMSpinbox(self, init_channel=prefix + "RFDiv-SP")
        sp.showStepExponent = False
        rb = PyDMLabel(self, init_channel=prefix + "RFDiv-RB")
        gb = self._create_small_GB(
            'RF Divisor', self.configs_wid, (sp, rb), align_ver=False)
        configs_layout.addWidget(gb, 1, 1)

        sp = PyDMSpinbox(self, init_channel=prefix + "RepeatBucketList-SP")
        sp.showStepExponent = False
        rb = PyDMLabel(self, init_channel=prefix + "RepeatBucketList-RB")
        gb = self._create_small_GB(
            'Repeat BL', self.configs_wid, (sp, rb), align_ver=False)
        configs_layout.addWidget(gb, 1, 2)

        sp = PyDMLineEdit(self, init_channel=prefix + "BucketList-SP")
        sp.setMaximumHeight(35)
        # sp.setMinimumWidth(300)
        sp.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
        rb = PyDMLabel(self, init_channel=prefix + "BucketList-RB")
        rb.setMaximumSize(500, 35)
        # rb.setMinimumWidth(300)
        rb.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
        gb = self._create_small_GB('Bucket List', self.configs_wid, (sp, rb))
        configs_layout.addWidget(gb, 2, 0, 1, 2)

        rb = PyDMLabel(self, init_channel=prefix + "BucketListLen-Mon")
        gb = self._create_small_GB('BL Length', self.configs_wid, (rb, ))
        configs_layout.addWidget(gb, 2, 2)

    def _setup_status_wid(self):
        prefix = self.prefix
        status_layout = QGridLayout(self.status_wid)
        status_layout.setHorizontalSpacing(30)
        status_layout.setVerticalSpacing(30)

        rb = PyDMLabel(self, init_channel=prefix + "StateMachine-Mon")
        status_layout.addWidget(rb, 0, 0, 1, 3)
        status_layout.setAlignment(rb, Qt.AlignCenter)

        lb = QLabel("<b>Alive</b>")
        rb = PyDMLabel(self, init_channel=prefix + "Alive-Mon")
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 1, 0)

        lb = QLabel("<b>Network</b>")
        rb = SiriusLedAlert(self, init_channel=prefix + "Network-Mon")
        on_c, off_c = rb.onColor, rb.offColor
        rb.offColor = on_c
        rb.onColor = off_c
        rb.setMaximumSize(40, 40)
        rb.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 1, 1)

        lb = QLabel("<b>RF Sts</b>")
        rb = SiriusLedAlert(self, init_channel=prefix + "RFStatus-Mon")
        on_c, off_c = rb.onColor, rb.offColor
        rb.offColor = on_c
        rb.onColor = off_c
        rb.setMaximumSize(40, 40)
        rb.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
        gb = self._create_small_GB('', self.status_wid, (lb, rb))
        gb.setStyleSheet('border: 2px solid transparent;')
        status_layout.addWidget(gb, 1, 2)

        wids = list()
        for i in range(8):
            rb = SiriusLedAlert(self, init_channel=prefix + "Los-Mon", bit=i)
            rb.setMaximumSize(40, 40)
            rb.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
            wids.append(rb)
        gb = self._create_small_GB(
                'Down Connection', self.status_wid, wids, align_ver=False
                )
        status_layout.addWidget(gb, 2, 0, 1, 3)

    def _create_small_GB(self, name, parent, wids, align_ver=True):
        gb = QGroupBox(name, parent)
        lv = QVBoxLayout(gb) if align_ver else QHBoxLayout(gb)
        for wid in wids:
            lv.addWidget(wid)
            lv.setAlignment(wid, Qt.AlignCenter)
        return gb


class EventList(BaseList):
    """Template for control of Events."""

    _MIN_WIDs = {
        'ext_trig': 150, 'mode': 205, 'delay_type': 130, 'delay': 150,
        'description': 300,
        }
    _LABELS = {
        'ext_trig': 'Ext. Trig.', 'mode': 'Mode', 'description': 'Description',
        'delay_type': 'Type', 'delay': 'Delay [us]'
        }
    _ALL_PROPS = ('ext_trig', 'mode', 'delay_type', 'delay', 'description')

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
        elif 'description' == prop:
            sp = PyDMLineEdit(self, init_channel=prefix + 'Desc-SP')
            rb = PyDMLabel(self, init_channel=prefix + 'Desc-RB')
        return (sp, rb)


class ClockList(BaseList):
    """Template for control of High and Low Level Clocks."""

    _MIN_WIDs = {
        'state': 150,
        'frequency': 150,
        'mux_div': 150,
        'mux_enbl': 150,
        }
    _LABELS = {
        'state': 'Enabled',
        'frequency': 'Freq. [kHz]',
        'mux_div': 'Mux Divisor',
        'mux_enbl': 'Mux Enabled',
        }
    _ALL_PROPS = ('state', 'frequency', 'mux_div', 'mux_enbl')

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
        if 'mux_enbl' == prop:
            sp = PyDMCb(self, init_channel=prefix + "MuxEnbl-Sel")
            sp.setText(prefix.propty)
            rb = PyDMLed(self, init_channel=prefix + "MuxEnbl-Sts")
            return (sp, rb)
        elif 'mux_div' == prop:
            sp = PyDMSpinbox(self, init_channel=prefix + "MuxDiv-SP")
            sp.showStepExponent = False
            rb = PyDMLabel(self, init_channel=prefix + "MuxDiv-RB")
        return sp, rb


if __name__ == '__main__':
    """Run Example."""
    app = SiriusApplication()
    _util.set_style(app)
    evg_ctrl = EVG(
        prefix='ca://fernando-lnls452-linux-AS-Glob:TI-EVG:')
    evg_ctrl.show()
    sys.exit(app.exec_())
