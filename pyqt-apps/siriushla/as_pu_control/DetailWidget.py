"""Detailed widget for controlling a pulsed mangnet."""
import qtawesome as qta
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, \
    QLabel, QGroupBox, QFormLayout
from pydm.widgets import PyDMLabel, PyDMPushButton

from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriushla import util
from siriushla.widgets import SiriusLedState, SiriusLedAlert, PyDMLed, \
    PyDMStateButton, PyDMLinEditScrollbar
from siriushla.as_ti_control.hl_trigger import HLTriggerSimple


class PUDetailWidget(QWidget):
    """Detailed widget for controlling a pulsed magnet."""

    def __init__(self, devname, parent=None):
        """Receive a parent and a pulsed mangnet name."""
        super().__init__(parent)
        self._devname = _PVName(devname)
        self._section = self._devname.sec
        self._prefix = _VACA_PREFIX
        self._prefdevname = self._devname.substitute(prefix=self._prefix)
        self.setObjectName(self._section+'App')
        self.setWindowIcon(qta.icon(
            'mdi.current-ac', color=util.get_appropriate_color(self._section)))

        self._create_pvs()
        self._setup_ui()
        self.setStyleSheet("""
            #pulses_box,
            #pwrstate_box {
                max-width: 8em;
            }
        """)
        self.setFocusPolicy(Qt.StrongFocus)

    def _create_pvs(self):
        """Create variables with pvs that'll be used."""
        self._voltage_sp_pv = self._prefdevname + ":Voltage-SP"
        self._voltage_rb_pv = self._prefdevname + ":Voltage-RB"
        self._voltage_mon_pv = self._prefdevname + ":Voltage-Mon"
        self._kick_sp_pv = self._prefdevname + ":Kick-SP"
        self._kick_rb_pv = self._prefdevname + ":Kick-RB"
        self._kick_mon_pv = self._prefdevname + ":Kick-Mon"
        self._pwrstate_sel_pv = self._prefdevname + ":PwrState-Sel"
        self._pwrstate_sts_pv = self._prefdevname + ":PwrState-Sts"
        self._enablepulses_sel_pv = self._prefdevname + ":Pulse-Sel"
        self._enablepulses_sts_pv = self._prefdevname + ":Pulse-Sts"
        self._reset_cmd_pv = self._prefdevname + ":Reset-Cmd"
        self._intlk1_mon_pv = self._prefdevname + ":Intlk1-Mon"
        self._intlk2_mon_pv = self._prefdevname + ":Intlk2-Mon"
        self._intlk3_mon_pv = self._prefdevname + ":Intlk3-Mon"
        self._intlk4_mon_pv = self._prefdevname + ":Intlk4-Mon"
        self._intlk5_mon_pv = self._prefdevname + ":Intlk5-Mon"
        self._intlk6_mon_pv = self._prefdevname + ":Intlk6-Mon"
        self._intlk7_mon_pv = self._prefdevname + ":Intlk7-Mon"
        self._intlk1label_cte_pv = self._prefdevname + ":Intlk1Label-Cte"
        self._intlk2label_cte_pv = self._prefdevname + ":Intlk2Label-Cte"
        self._intlk3label_cte_pv = self._prefdevname + ":Intlk3Label-Cte"
        self._intlk4label_cte_pv = self._prefdevname + ":Intlk4Label-Cte"
        self._intlk5label_cte_pv = self._prefdevname + ":Intlk5Label-Cte"
        self._intlk6label_cte_pv = self._prefdevname + ":Intlk6Label-Cte"
        self._intlk7label_cte_pv = self._prefdevname + ":Intlk7Label-Cte"
        if 'Sept' not in self._devname:
            self._intlk8_mon_pv = self._prefdevname + ":Intlk8-Mon"
            self._intlk8label_cte_pv = self._prefdevname+":Intlk8Label-Cte"
        self._ctrlmode_pv = self._prefdevname + ":CtrlMode-Mon"

        self._trigname = self._devname.substitute(dis='TI')

    def _setup_ui(self):
        self.header_label = QLabel("<h1>" + self._prefdevname + "</h1>")
        self.header_label.setObjectName("header_label")
        interlock_box = QGroupBox(parent=self, title="Interlock")
        interlock_box.setObjectName("interlock_box")
        interlock_box.setLayout(self._interlock_layout())
        pwrstate_box = QGroupBox(parent=self, title="Power")
        pwrstate_box.setObjectName("pwrstate_box")
        pwrstate_box.setLayout(self._pwrstate_layout())
        pulses_box = QGroupBox(parent=self, title="Pulses")
        pulses_box.setObjectName("pulses_box")
        pulses_box.setLayout(self._pulses_layout())
        voltage_box = QGroupBox(parent=self, title="Voltage")
        voltage_box.setObjectName("voltage_box")
        voltage_box.setLayout(self._voltage_layout())
        kick_box = QGroupBox(parent=self, title="Kick")
        kick_box.setObjectName("kick_box")
        kick_box.setLayout(self._kick_layout())
        timing_box = QGroupBox(parent=self, title='Trigger')
        timing_box.setObjectName('timing_box')
        hbl = QHBoxLayout(timing_box)
        hbl.addWidget(HLTriggerSimple(
            timing_box, self._trigname, self._prefix))

        self.layout = QGridLayout(self)
        self.layout.addWidget(self.header_label, 0, 0, 1, 3)
        self.layout.addWidget(interlock_box, 1, 0, 3, 1)
        vbl1 = QVBoxLayout()
        vbl1.addWidget(pwrstate_box)
        vbl1.addWidget(pulses_box)
        self.layout.addLayout(vbl1, 1, 1, 2, 1)
        vbl2 = QVBoxLayout()
        vbl2.addWidget(voltage_box)
        vbl2.addWidget(kick_box)
        self.layout.addLayout(vbl2, 1, 2, 2, 1)
        self.layout.addWidget(timing_box, 3, 1, 1, 3)
        self.layout.addLayout(self._ctrlmode_layout(), 4, 1, 1, 3)

    def _interlock_layout(self):
        interlock_layout = QGridLayout()

        intlk_cnt = 8 if 'Sept' not in self._devname else 7
        for i in range(intlk_cnt):
            label = PyDMLabel(
                self, getattr(self, '_intlk' + str(i+1) + 'label_cte_pv'))
            led = PyDMLed(
                self, getattr(self, '_intlk' + str(i+1) + '_mon_pv'))
            led.onColor = led.LightGreen
            led.offColor = led.Red
            interlock_layout.addWidget(led, i, 0)
            interlock_layout.addWidget(label, i, 1)

        self.reset_bt = PyDMPushButton(
            parent=self, init_channel=self._reset_cmd_pv, pressValue=1)
        self.reset_bt.setIcon(qta.icon('fa5s.sync'))
        self.reset_bt.setObjectName('reset_bt')
        self.reset_bt.setStyleSheet(
            '#reset_bt{min-width:25px; max-width:25px; icon-size:20px;}')
        interlock_layout.addWidget(
            self.reset_bt, i+1, 0, 1, 2, alignment=Qt.AlignHCenter)

        return interlock_layout

    def _pwrstate_layout(self):
        pwrstate_layout = QHBoxLayout()

        self.state_button = PyDMStateButton(
            parent=self, init_channel=self._pwrstate_sel_pv)
        self.state_led = SiriusLedState(self, self._pwrstate_sts_pv)

        pwrstate_layout.addWidget(self.state_button)
        pwrstate_layout.addWidget(self.state_led)

        return pwrstate_layout

    def _pulses_layout(self):
        pulses_layout = QHBoxLayout()

        self.pulses_state_button = PyDMStateButton(
            parent=self, init_channel=self._enablepulses_sel_pv)
        self.pulses_state_led = SiriusLedState(
            parent=self, init_channel=self._enablepulses_sts_pv)

        pulses_layout.addWidget(self.pulses_state_button)
        pulses_layout.addWidget(self.pulses_state_led)

        return pulses_layout

    def _voltage_layout(self):
        voltage_layout = QVBoxLayout()

        self.voltage_sp_widget = PyDMLinEditScrollbar(
            parent=self, channel=self._voltage_sp_pv)
        self.voltage_rb_label = PyDMLabel(
            parent=self, init_channel=self._voltage_rb_pv)
        self.voltage_rb_label .showUnits = True
        self.voltage_rb_label.precisionFromPV = True
        self.voltage_mon_label = PyDMLabel(
            parent=self, init_channel=self._voltage_mon_pv)
        self.voltage_mon_label.showUnits = True
        self.voltage_mon_label.precisionFromPV = True

        voltage_layout = QFormLayout()
        voltage_layout.setLabelAlignment(Qt.AlignRight)
        voltage_layout.setFormAlignment(Qt.AlignHCenter)
        voltage_layout.addRow('SP:', self.voltage_sp_widget)
        voltage_layout.addRow('RB:', self.voltage_rb_label)
        voltage_layout.addRow('Mon:', self.voltage_mon_label)

        return voltage_layout

    def _kick_layout(self):
        self.kick_sp_widget = PyDMLinEditScrollbar(
            parent=self, channel=self._kick_sp_pv)
        self.kick_rb_label = PyDMLabel(
            parent=self, init_channel=self._kick_rb_pv)
        self.kick_rb_label.showUnits = True
        self.kick_rb_label.precisionFromPV = True
        self.kick_mon_label = PyDMLabel(
            parent=self, init_channel=self._kick_mon_pv)
        self.kick_mon_label.showUnits = True
        self.kick_mon_label.precisionFromPV = True

        kick_layout = QFormLayout()
        kick_layout.setLabelAlignment(Qt.AlignRight)
        kick_layout.setFormAlignment(Qt.AlignHCenter)
        kick_layout.addRow('SP:', self.kick_sp_widget)
        kick_layout.addRow('RB:', self.kick_rb_label)
        kick_layout.addRow('Mon:', self.kick_mon_label)

        return kick_layout

    def _ctrlmode_layout(self):
        ctrlmode_layout = QHBoxLayout()

        self.ctrlmode_led = SiriusLedAlert(
            parent=self, init_channel=self._ctrlmode_pv)
        self.ctrlmode_label = PyDMLabel(
            parent=self, init_channel=self._ctrlmode_pv)

        ctrlmode_layout.addStretch()
        ctrlmode_layout.addWidget(self.ctrlmode_led)
        ctrlmode_layout.addWidget(self.ctrlmode_label)

        return ctrlmode_layout


if __name__ == "__main__":
    import sys
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication(None, sys.argv)
    w = PUDetailWidget(devname="SI-01SA:PM-InjDpKckr")
    w.show()
    sys.exit(app.exec_())
