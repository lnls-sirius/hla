"""Widget to control a pulsed magnet.

Exposes basic controls like:
    setpoint/readbacks tension
    setpoint/readbacks kick
    turning on/off
"""
from pydm.PyQt.QtGui import QWidget, QHBoxLayout, QVBoxLayout, QLabel, \
    QPushButton, QStyleOption, QStyle, QPainter
from pydm.widgets.led import PyDMLed
from pydm.widgets.state_button import PyDMStateButton
from pydm.widgets.label import PyDMLabel

from siriuspy.envars import vaca_prefix as _VACA_PREFIX
from siriuspy.pulsedps import properties as pu_props
from siriuspy.pulsedma import properties as pm_props
from siriushla.FloatSetPointWidget import FloatSetPointWidget
# from siriushla.as_pm_control.PMTensionWidget import PMTensionWidget
# from siriushla.as_pm_control.PMKickWidget import PMKickWidget


class PulsedMagnetWidget(QWidget):
    """Widget to control pulsed magnets properties."""

    StyleSheet = """
        #maname_header,
        #state_header,
        #tension_sp_header,
        #tension_mon_header,
        #kick_sp_header,
        #kick_mon_header,
        #button_header {
            font-weight: bold;
        }
        #state_header,
        #state_widget {
            min-width: 150px;
            max-width: 150px;
        }
        #maname_header,
        #maname_button {
            min-width: 300px;
            max-width: 300px;
            margin-right: 20px;
        }
        #tension_sp_header,
        #kick_sp_header,
        #tension_widget,
        #kick_widget {
            min-width: 250px;
            max-width: 250px;
        }
        #tension_mon_header,
        #kick_mon_header,
        #tension_label,
        #kick_label {
            min-width: 250px;
            max-width: 250px;
        }
    """

    def __init__(self, maname, header=False, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._maname = maname
        self._prefixed_maname = _VACA_PREFIX + self._maname + ":"
        self._header = header

        self._create_pvs()

        self._setup_ui()
        self.setStyleSheet(self.StyleSheet)

        self.setObjectName(self._maname)

    def _create_pvs(self):
        self._pwrstate_sp_pv = self._prefixed_maname + pu_props.PwrStateSel
        self._pwrstate_rb_pv = self._prefixed_maname + pu_props.PwrStateSts
        self._tension_sp_pv = self._prefixed_maname + pu_props.TensionSP
        self._tension_mon_pv = self._prefixed_maname + pu_props.TensionMon
        self._kick_sp_pv = self._prefixed_maname + pm_props.StrengthSP
        self._kick_mon_pv = self._prefixed_maname + pm_props.StrengthMon

    def _setup_ui(self):
        # Optional header layout
        if self._header:
            self.header_layout = QHBoxLayout()
            self.layout_with_header = QVBoxLayout()

            self.state_header = QLabel("State", self)
            self.state_header.setObjectName("state_header")
            self.maname_header = QLabel("Magnet", self)
            self.maname_header.setObjectName("maname_header")
            self.tension_sp_header = QLabel("Tension-SP", self)
            self.tension_sp_header.setObjectName("tension_sp_header")
            self.tension_mon_header = QLabel("Tension-Mon", self)
            self.tension_mon_header.setObjectName("tension_mon_header")
            self.kick_sp_header = QLabel("Kick-SP", self)
            self.kick_sp_header.setObjectName("kick_sp_header")
            self.kick_mon_header = QLabel("Kick-Mon", self)
            self.kick_mon_header.setObjectName("kick_mon_header")

            self.header_layout.addWidget(self.state_header)
            self.header_layout.addWidget(self.maname_header)
            self.header_layout.addWidget(self.tension_sp_header)
            self.header_layout.addWidget(self.tension_mon_header)
            self.header_layout.addWidget(self.kick_sp_header)
            self.header_layout.addWidget(self.kick_mon_header)
            self.header_layout.addStretch()

        self.layout = QHBoxLayout()

        # Widgets
        self.pwrstate_button = PyDMStateButton(
            parent=self, init_channel="ca://" + self._pwrstate_sp_pv)
        self.pwrstate_button.setObjectName("pwrstate_button")
        self.state_led = LedWidget(self._pwrstate_sp_pv, self)
        self.state_led.setObjectName("state_led")
        self.state_widget = QWidget(self)
        self.state_widget.setObjectName("state_widget")
        self.state_widget.layout = QHBoxLayout()
        self.state_widget.setLayout(self.state_widget.layout)
        self.state_widget.layout.addWidget(self.pwrstate_button)
        self.state_widget.layout.addWidget(self.state_led)
        self.maname_label = QPushButton(self._maname, self)
        self.maname_label.setObjectName("maname_button")
        # self.pwrstate_button = PyDMLed(
        #     parent=self, init_channel="ca://" + self._pwrstate_sp_pv)
        self.tension_widget = FloatSetPointWidget(
            parent=self, channel="ca://" + self._tension_sp_pv,)
        self.tension_widget.setObjectName("tension_widget")
        self.tension_mon_label = PyDMLabel(
            parent=self, init_channel="ca://" + self._tension_mon_pv)
        self.tension_mon_label.setObjectName("tension_label")
        self.kick_widget = FloatSetPointWidget(
            parent=self, channel="ca://" + self._kick_sp_pv)
        self.kick_widget.setObjectName("kick_widget")
        self.kick_mon_label = PyDMLabel(
            parent=self, init_channel="ca://" + self._kick_mon_pv)
        self.kick_mon_label.setObjectName("kick_label")

        # Configuration
        self.tension_mon_label.setPrecFromPV(True)
        self.tension_widget.set_limits_from_pv(True)
        self.kick_mon_label.setPrecFromPV(True)
        self.kick_widget.set_limits_from_pv(True)

        self.layout.addWidget(self.state_widget)
        self.layout.addWidget(self.maname_label)
        self.layout.addWidget(self.tension_widget)
        self.layout.addWidget(self.tension_mon_label)
        self.layout.addWidget(self.kick_widget)
        self.layout.addWidget(self.kick_mon_label)
        self.layout.addStretch()

        if self._header:
            self.layout_with_header.addLayout(self.header_layout)
            self.layout_with_header.addLayout(self.layout)
            self.setLayout(self.layout_with_header)
        else:
            self.setLayout(self.layout)

    def paintEvent(self, event):
        """Need to override paintEvent in order to apply CSS."""
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    def get_magnet_button(self):
        """Return the push button."""
        return self.maname_label

    def get_magnet_name(self):
        """Return magnet name."""
        return self._maname


class LedWidget(QWidget):
    """Led class."""

    def __init__(self, channel, parent=None):
        """Constructor."""
        super().__init__(parent)
        layout = QVBoxLayout()
        self.led = PyDMLed(
            parent=self, init_channel="ca://" + channel)
        layout.addWidget(self.led)
        self.setLayout(layout)


if __name__ == "__main__":
    import sys
    from pydm import PyDMApplication
    app = PyDMApplication(None, sys.argv)
    app.setStyleSheet("""""")
    w = PulsedMagnetWidget(maname="SI-01SA:PM-InjDpK")
    w.show()
    sys.exit(app.exec_())
