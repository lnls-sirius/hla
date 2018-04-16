"""Detailed widget for controlling a pulsed mangnet."""
from pydm.PyQt.QtGui import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, \
    QLabel, QGroupBox
from pydm.widgets.label import PyDMLabel

from siriuspy.envars import vaca_prefix as _VACA_PREFIX
from siriushla.widgets.led import SiriusLedState, SiriusLedAlert
from siriushla.widgets.state_button import PyDMStateButton
from siriushla.widgets import PyDMLinEditScrollbar


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
                max-width: 150px;
            }
        """)

    def _create_pvs(self):
        """Create variables with pvs that'll be used."""
        self._voltage_sp_pv = self._prefixed_maname + ":Voltage-SP"
        self._voltage_mon_pv = \
            self._prefixed_maname + ":Voltage-Mon"
        self._kick_sp_pv = \
            self._prefixed_maname + ":Kick-SP"
        self._kick_mon_pv = \
            self._prefixed_maname + ":Kick-Mon"
        self._pwrstate_sel_pv = \
            self._prefixed_maname + ":PwrState-Sel"
        self._pwrstate_sts_pv = \
            self._prefixed_maname + ":PwrState-Sts"
        self._enablepulses_sel_pv = \
            self._prefixed_maname + ":Pulsed-Sel"
        self._enablepulses_sts_pv = \
            self._prefixed_maname + ":Pulsed-Sts"
        self._intlk_mon_pv = \
            self._prefixed_maname + ":Intlk-Mon"
        self._ctrlmode_pv = self._prefixed_maname + ":CtrlMode-Mon"

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
        voltage_box = QGroupBox(parent=self, title="Tension")
        voltage_box.setObjectName("voltage_box")
        voltage_box.setLayout(self._voltage_layout())
        kick_box = QGroupBox(parent=self, title="Kick")
        kick_box.setObjectName("kick_box")
        kick_box.setLayout(self._kick_layout())

        self.layout.addWidget(self.header_label, 0, 0, 1, 3)
        self.layout.addWidget(interlock_box, 1, 0, 2, 1)
        self.layout.addWidget(pwrstate_box, 1, 1)
        self.layout.addWidget(pulses_box, 2, 1)
        self.layout.addWidget(voltage_box, 1, 2)
        self.layout.addWidget(kick_box, 2, 2)
        self.layout.addLayout(self._ctrlmode_layout(), 3, 1, 1, 3)

        self.setLayout(self.layout)

    def _interlock_layout(self):
        interlock_layout = QGridLayout()
        interlock_labels = ["Bit0", "Bit1", "Bit2", "Bit3", "Bit4", "Bit5",
                            "Bit6", "Bit7"]
        for i in range(8):
            label_widget = QLabel(interlock_labels[i])
            led = SiriusLedAlert(
                self, "ca://" + self._intlk_mon_pv, i)
            interlock_layout.addWidget(led, i, 0)
            interlock_layout.addWidget(label_widget, i, 1)

        interlock_layout.setRowStretch(8, 1)

        return interlock_layout

    def _pwrstate_layout(self):
        pwrstate_layout = QHBoxLayout()

        self.state_button = PyDMStateButton(
            parent=self, init_channel="ca://" + self._pwrstate_sel_pv)
        self.state_led = SiriusLedState(self, "ca://" + self._pwrstate_sts_pv)

        pwrstate_layout.addStretch()
        pwrstate_layout.addWidget(self.state_button)
        pwrstate_layout.addWidget(self.state_led)
        pwrstate_layout.addStretch()

        return pwrstate_layout

    def _pulses_layout(self):
        pulses_layout = QHBoxLayout()

        self.pulses_state_button = PyDMStateButton(
            parent=self, init_channel="ca://" + self._enablepulses_sel_pv)
        self.pulses_state_led = SiriusLedState(
            parent=self, init_channel="ca://" + self._enablepulses_sts_pv)

        pulses_layout.addStretch()
        pulses_layout.addWidget(self.pulses_state_button)
        pulses_layout.addWidget(self.pulses_state_led)
        pulses_layout.addStretch()

        return pulses_layout

    def _voltage_layout(self):
        voltage_layout = QVBoxLayout()

        self.voltage_sp_widget = PyDMLinEditScrollbar(
            parent=self, channel="ca://" + self._voltage_sp_pv)
        self.voltage_rb_label = PyDMLabel(
            parent=self, init_channel="ca://" + self._voltage_mon_pv)

        # self.voltage_sp_widget.set_limits_from_pv(True)
        # self.voltage_rb_label.precFromPV = True

        voltage_layout.addWidget(self.voltage_sp_widget)
        voltage_layout.addWidget(self.voltage_rb_label)

        return voltage_layout

    def _kick_layout(self):
        kick_layout = QVBoxLayout()

        self.kick_sp_widget = PyDMLinEditScrollbar(
            parent=self, channel="ca://" + self._kick_sp_pv)
        self.kick_rb_label = PyDMLabel(
            parent=self, init_channel="ca://" + self._kick_mon_pv)

        # self.kick_sp_widget.set_limits_from_pv(True)
        # self.kick_rb_label.precFromPV = True

        kick_layout.addWidget(self.kick_sp_widget)
        kick_layout.addWidget(self.kick_rb_label)

        return kick_layout

    def _ctrlmode_layout(self):
        ctrlmode_layout = QHBoxLayout()

        self.ctrlmode_led = SiriusLedAlert(
            parent=self, init_channel="ca://" + self._ctrlmode_pv)
        self.ctrlmode_label = PyDMLabel(
            parent=self, init_channel="ca://" + self._ctrlmode_pv)

        ctrlmode_layout.addStretch()
        ctrlmode_layout.addWidget(self.ctrlmode_led)
        ctrlmode_layout.addWidget(self.ctrlmode_label)

        return ctrlmode_layout


if __name__ == "__main__":
    import sys
    from pydm import PyDMApplication

    app = PyDMApplication(None, sys.argv)
    w = PulsedMagnetDetailWidget(maname="SI-01SA:PM-InjDpKckr")
    w.show()
    sys.exit(app.exec_())
