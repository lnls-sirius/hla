"""Detailed widget for controlling a pulsed mangnet."""
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, \
    QLabel, QGroupBox, QPushButton
from pydm.widgets import PyDMLabel, PyDMSpinbox

from siriuspy.envars import vaca_prefix as _VACA_PREFIX
from siriushla import util
from siriushla.widgets import SiriusLedState, SiriusLedAlert, PyDMLed, \
    PyDMStateButton, PyDMLinEditScrollbar, PyDMLedMultiChannel
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_ti_control.hl_trigger import HLTriggerDetailed


class PulsedMagnetDetailWidget(QWidget):
    """Detailed widget for controlling a pulsed magnet."""

    def __init__(self, maname, parent=None):
        """Receive a parent and a pulsed mangnet name."""
        super().__init__(parent)
        self._maname = maname
        self._prefixed_maname = _VACA_PREFIX + self._maname

        self._create_pvs()
        self._setup_ui()
        self.setStyleSheet("""
            #pulses_box,
            #pwrstate_box {
                max-width: 8em;
            }
        """)

    def _create_pvs(self):
        """Create variables with pvs that'll be used."""
        self._voltage_sp_pv = self._prefixed_maname + ":Voltage-SP"
        self._voltage_mon_pv = self._prefixed_maname + ":Voltage-Mon"
        self._kick_sp_pv = self._prefixed_maname + ":Kick-SP"
        self._kick_mon_pv = self._prefixed_maname + ":Kick-Mon"
        self._pwrstate_sel_pv = self._prefixed_maname + ":PwrState-Sel"
        self._pwrstate_sts_pv = self._prefixed_maname + ":PwrState-Sts"
        self._enablepulses_sel_pv = self._prefixed_maname + ":Pulse-Sel"
        self._enablepulses_sts_pv = self._prefixed_maname + ":Pulse-Sts"
        self._intlk1_mon_pv = self._prefixed_maname + ":Intlk1-Mon"
        self._intlk2_mon_pv = self._prefixed_maname + ":Intlk2-Mon"
        self._intlk3_mon_pv = self._prefixed_maname + ":Intlk3-Mon"
        self._intlk4_mon_pv = self._prefixed_maname + ":Intlk4-Mon"
        self._intlk5_mon_pv = self._prefixed_maname + ":Intlk5-Mon"
        self._intlk6_mon_pv = self._prefixed_maname + ":Intlk6-Mon"
        self._intlk7_mon_pv = self._prefixed_maname + ":Intlk7-Mon"
        self._intlk8_mon_pv = self._prefixed_maname + ":Intlk8-Mon"
        self._intlk1label_cte_pv = self._prefixed_maname + ":Intlk1Label-Cte"
        self._intlk2label_cte_pv = self._prefixed_maname + ":Intlk2Label-Cte"
        self._intlk3label_cte_pv = self._prefixed_maname + ":Intlk3Label-Cte"
        self._intlk4label_cte_pv = self._prefixed_maname + ":Intlk4Label-Cte"
        self._intlk5label_cte_pv = self._prefixed_maname + ":Intlk5Label-Cte"
        self._intlk6label_cte_pv = self._prefixed_maname + ":Intlk6Label-Cte"
        self._intlk7label_cte_pv = self._prefixed_maname + ":Intlk7Label-Cte"
        self._intlk8label_cte_pv = self._prefixed_maname + ":Intlk8Label-Cte"
        self._ctrlmode_pv = self._prefixed_maname + ":CtrlMode-Mon"
        self._prefixed_trigger_name = \
            self._prefixed_maname.replace('PM-', 'TI-')
        self._timing_delay_sp = self._prefixed_trigger_name + ":Delay-SP"
        self._timing_delay_rb = self._prefixed_trigger_name + ":Delay-RB"
        self._timing_status_pv = self._prefixed_trigger_name + ":Status-Mon"
        self._timing_state_pv = self._prefixed_trigger_name + ":State-Sts"

    def _setup_ui(self):
        self.layout = QGridLayout()

        self.header_label = QLabel("<h1>" + self._prefixed_maname + "</h1>")
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
        timing_box.setLayout(self._timing_layout())

        self.layout.addWidget(self.header_label, 0, 0, 1, 3)
        self.layout.addWidget(interlock_box, 1, 0, 2, 1)
        self.layout.addWidget(pwrstate_box, 1, 1)
        self.layout.addWidget(pulses_box, 2, 1)
        self.layout.addWidget(voltage_box, 1, 2)
        self.layout.addWidget(kick_box, 2, 2)
        self.layout.addWidget(timing_box, 3, 0, 1, 3)
        self.layout.addLayout(self._ctrlmode_layout(), 4, 1, 1, 3)

        self.setLayout(self.layout)

    def _interlock_layout(self):
        interlock_layout = QGridLayout()

        for i in range(8):
            label = PyDMLabel(
                self, getattr(self, '_intlk' + str(i+1) + 'label_cte_pv'))
            led = PyDMLed(
                self, getattr(self, '_intlk' + str(i+1) + '_mon_pv'))
            led.onColor = led.LightGreen
            led.offColor = led.Red
            interlock_layout.addWidget(led, i, 0)
            interlock_layout.addWidget(label, i, 1)

        interlock_layout.setRowStretch(8, 1)

        return interlock_layout

    def _pwrstate_layout(self):
        pwrstate_layout = QHBoxLayout()

        self.state_button = PyDMStateButton(
            parent=self, init_channel=self._pwrstate_sel_pv)
        self.state_led = SiriusLedState(self, self._pwrstate_sts_pv)

        pwrstate_layout.addStretch()
        pwrstate_layout.addWidget(self.state_button)
        pwrstate_layout.addWidget(self.state_led)
        pwrstate_layout.addStretch()

        return pwrstate_layout

    def _pulses_layout(self):
        pulses_layout = QHBoxLayout()

        self.pulses_state_button = PyDMStateButton(
            parent=self, init_channel=self._enablepulses_sel_pv)
        self.pulses_state_led = SiriusLedState(
            parent=self, init_channel=self._enablepulses_sts_pv)

        pulses_layout.addStretch()
        pulses_layout.addWidget(self.pulses_state_button)
        pulses_layout.addWidget(self.pulses_state_led)
        pulses_layout.addStretch()

        return pulses_layout

    def _voltage_layout(self):
        voltage_layout = QVBoxLayout()

        self.voltage_sp_widget = PyDMLinEditScrollbar(
            parent=self, channel=self._voltage_sp_pv)
        self.voltage_rb_label = PyDMLabel(
            parent=self, init_channel=self._voltage_mon_pv)

        voltage_layout.addWidget(self.voltage_sp_widget)
        voltage_layout.addWidget(self.voltage_rb_label)

        return voltage_layout

    def _kick_layout(self):
        kick_layout = QVBoxLayout()

        self.kick_sp_widget = PyDMLinEditScrollbar(
            parent=self, channel=self._kick_sp_pv)
        self.kick_rb_label = PyDMLabel(
            parent=self, init_channel=self._kick_mon_pv)

        kick_layout.addWidget(self.kick_sp_widget)
        kick_layout.addWidget(self.kick_rb_label)

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

    def _timing_layout(self):
        timing_layout = QGridLayout()

        # Led, Timing-SP/RB, trigger window
        self._trigger_delay_label = QLabel('Delay', self)
        self._trigger_delay_sp = PyDMSpinbox(
            parent=self, init_channel=self._timing_delay_sp)
        self._trigger_delay_sp.showStepExponent = False
        self._trigger_delay_rb = PyDMLabel(
            parent=self, init_channel=self._timing_delay_rb)
        self._trigger_status_label = QLabel('Status')
        self._trigger_status_led = PyDMLedMultiChannel(
            parent=self,
            channels2values={
                self._timing_status_pv: 0,
                self._timing_state_pv: 1})
        self._trigger_detail_btn = QPushButton('Open details', self)

        # Connect trigger window
        trg_w = create_window_from_widget(
            HLTriggerDetailed,
            title=self._prefixed_trigger_name+' Detailed Settings',
            is_main=True)
        util.connect_window(
            self._trigger_detail_btn, trg_w,
            parent=self, prefix=self._prefixed_maname.replace('PM-', 'TI-'))

        timing_layout.addWidget(self._trigger_delay_label, 0, 0,
                                alignment=Qt.AlignCenter)
        timing_layout.addWidget(self._trigger_delay_sp, 0, 1)
        timing_layout.addWidget(self._trigger_delay_rb, 0, 2)
        timing_layout.addWidget(self._trigger_status_label, 1, 0,
                                alignment=Qt.AlignCenter)
        timing_layout.addWidget(self._trigger_status_led, 1, 1)
        timing_layout.addWidget(self._trigger_detail_btn, 1, 2)

        return timing_layout


if __name__ == "__main__":
    import sys
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication(None, sys.argv)
    w = PulsedMagnetDetailWidget(maname="SI-01SA:PM-InjDpKckr")
    w.show()
    sys.exit(app.exec_())
