"""Widget to control a pulsed magnet.

Exposes basic controls like:
    setpoint/readbacks tension
    setpoint/readbacks kick
    turning on/off
"""
from pydm.PyQt.QtGui import QWidget, QHBoxLayout, QVBoxLayout, QLabel, \
    QPushButton

# from pydm.widgets.led import PyDMLed
from pydm.widgets.state_button import PyDMStateButton
from pydm.widgets.line_edit import PyDMLineEdit
from pydm.widgets.scrollbar import PyDMScrollBar
from pydm.widgets.label import PyDMLabel
from siriuspy.envars import vaca_prefix as _VACA_PREFIX
from siriuspy.pulsedps import properties as pu_props
from siriuspy.pulsedma import properties as pm_props


class PulsedMagnetWidget(QWidget):
    """Widget to control pulsed magnets properties."""

    StyleSheet = """
        #maname_header,
        #state_header,
        #tension_sp_header,
        #tension_mon_header,
        #kick_sp_header,
        #kick_mon_header {
            font-weight: bold;
        }
        #maname_header,
        #maname_button {
            min-width: 300px;
            max-width: 300px;
            margin-right: 20px;
        }
        #state_header,
        #pwrstate_button {
            min-width: 100px;
            max-width: 100px;
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
            min-width: 200px;
            max-width: 200px;
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
        self._tension_sp_pv = self._prefixed_maname + pu_props.TensionSP
        self._tension_mon_pv = self._prefixed_maname + pu_props.TensionMon
        self._kick_sp_pv = self._prefixed_maname + pm_props.StrengthSP
        self._kick_mon_pv = self._prefixed_maname + pm_props.StrengthMon

    def _setup_ui(self):
        if self._header:
            self.header_layout = QHBoxLayout()
            self.layout_with_header = QVBoxLayout()

            self.maname_header = QLabel("Magnet", self)
            self.maname_header.setObjectName("maname_header")
            self.state_header = QLabel("State", self)
            self.state_header.setObjectName("state_header")
            self.tension_sp_header = QLabel("Tension-SP", self)
            self.tension_sp_header.setObjectName("tension_sp_header")
            self.tension_mon_header = QLabel("Tension-Mon", self)
            self.tension_mon_header.setObjectName("tension_mon_header")
            self.kick_sp_header = QLabel("Kick-SP", self)
            self.kick_sp_header.setObjectName("kick_sp_header")
            self.kick_mon_header = QLabel("Kick-Mon", self)
            self.kick_mon_header.setObjectName("kick_mon_header")

            self.header_layout.addWidget(self.maname_header)
            self.header_layout.addWidget(self.state_header)
            self.header_layout.addWidget(self.tension_sp_header)
            self.header_layout.addWidget(self.tension_mon_header)
            self.header_layout.addWidget(self.kick_sp_header)
            self.header_layout.addWidget(self.kick_mon_header)
            self.header_layout.addStretch()

        self.layout = QHBoxLayout()

        # Widgets
        self.maname_label = QPushButton(self._maname, self)
        self.maname_label.setObjectName("maname_button")
        # self.pwrstate_button = PyDMLed(
        #     parent=self, init_channel="ca://" + self._pwrstate_sp_pv)
        # self.pwrstate_button = LedWidget(self._pwrstate_sp_pv, self)
        self.pwrstate_button = PyDMStateButton(
            parent=self, init_channel="ca://" + self._pwrstate_sp_pv)
        self.pwrstate_button.setObjectName("pwrstate_button")
        self.tension_widget = PMTensionWidget(device=self._maname, parent=self)
        self.tension_widget.setObjectName("tension_widget")
        self.tension_mon_label = PyDMLabel(
            parent=self, init_channel="ca://" + self._tension_mon_pv)
        self.tension_mon_label.setObjectName("tension_label")
        self.kick_widget = PMKickWidget(device=self._maname, parent=self)
        self.kick_widget.setObjectName("kick_widget")
        self.kick_mon_label = PyDMLabel(
            parent=self, init_channel="ca://" + self._kick_mon_pv)
        self.kick_mon_label.setObjectName("kick_label")

        # Configuration
        self.tension_mon_label.setPrecFromPV(True)
        self.tension_widget.set_limits_from_pv(True)
        self.kick_mon_label.setPrecFromPV(True)
        self.kick_widget.set_limits_from_pv(True)

        self.layout.addWidget(self.maname_label)
        self.layout.addWidget(self.pwrstate_button)
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


class PMTensionWidget(QWidget):
    """Widget to set tension of a pulsed magnet."""

    def __init__(self, device, parent=None):
        """Constructor sets channel name."""
        super().__init__(parent)
        self._device = device
        self._channel = _VACA_PREFIX + self._device + ":" + pu_props.TensionSP
        self._setup_ui()

    def _setup_ui(self):
        self.layout = QVBoxLayout()
        self.tension_sp_lineedit = PyDMLineEdit(
            parent=self, init_channel="ca://" + self._channel)
        self.tension_sp_lineedit.setObjectName("tension_sp_lineedit")
        self.tension_sp_scrollbar = PyDMScrollBar(
            parent=self, init_channel="ca://" + self._channel)
        self.tension_sp_scrollbar.setObjectName("tension_sp_scrollbar")
        self.layout.addWidget(self.tension_sp_lineedit)
        self.layout.addWidget(self.tension_sp_scrollbar)
        self.setLayout(self.layout)

    def set_limits_from_pv(self, value):
        """Set wether to use limiits from the pv channel."""
        self.tension_sp_scrollbar.limitsFromPV = value


class PMKickWidget(QWidget):
    """Widget to set kick of a pulsed magnet."""

    def __init__(self, device, parent=None):
        """Constructor sets channel name."""
        super().__init__(parent)
        self._device = device
        self._channel = _VACA_PREFIX + self._device + ":" + pm_props.StrengthSP
        self._setup_ui()

    def _setup_ui(self):
        self.layout = QVBoxLayout()
        self.kick_sp_lineedit = PyDMLineEdit(
            parent=self, init_channel="ca://" + self._channel)
        self.kick_sp_scrollbar = PyDMScrollBar(
            parent=self, init_channel="ca://" + self._channel)
        self.layout.addWidget(self.kick_sp_lineedit)
        self.layout.addWidget(self.kick_sp_scrollbar)
        self.setLayout(self.layout)

    def set_limits_from_pv(self, value):
        """Set wether to use limiits from the pv channel."""
        self.kick_sp_scrollbar.limitsFromPV = value


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
