"""Widget to control a power supply.

Exposes basic controls like:
    setpoint/readbacks tension
    setpoint/readbacks kick
    turning on/off
"""
from pydm.PyQt.QtGui import QWidget, QHBoxLayout, QVBoxLayout, QLabel, \
    QPushButton, QStyleOption, QStyle, QPainter
from pydm.PyQt.QtCore import QSize
from pydm.widgets.label import PyDMLabel

from siriuspy.envars import vaca_prefix as _VACA_PREFIX
from siriushla.widgets import PyDMLinEditScrollbar
from siriushla.widgets.state_button import PyDMStateButton
from siriushla.widgets.led import PyDMLed


class BasePSWidget(QWidget):
    """Base widget with basic controls to control a magnet."""

    StyleSheet = """
        #psname_header,
        #state_header,
        #analog_sp_header,
        #analog_mon_header,
        #button_header,
        #trim_header {
            font-weight: bold;
            qproperty-alignment: AlignCenter;
        }
        #state_header,
        #state_widget {
            min-width: 150px;
            max-width: 150px;
        }
        #psname_header,
        #psname_button {
            min-width: 300px;
            max-width: 300px;
            margin-right: 20px;
        }
        #analog_sp_header,
        #analog_widget {
            min-width: 250px;
            max-width: 250px;
        }
        #analog_mon_header,
        #analog_label {
            min-width: 200px;
            max-width: 200px;
            qproperty-alignment: AlignCenter;
        }
        #trim_header,
        #trim_button {
            min-width: 85px;
            max-width: 85px;
        }
    """

    def __init__(self, psname, header=True, parent=None):
        """Init widget UI."""
        super().__init__(parent)
        self._psname = psname
        self._prefixed_psname = _VACA_PREFIX + self._psname + ":"
        self._header = header
        self._has_trim = False

        self._detail_window = None
        self._trim_window = None

        self._create_pvs()

        self._setup_ui()
        # self.psname_label.clicked.connect(self._open_detail_window)
        # if self._has_trim:
        #     self.trim_button.clicked.connect(self._open_trim_window)
        self.setStyleSheet(self.StyleSheet)

        self.setObjectName(self._psname)

    @property
    def psname(self):
        """PS name."""
        return self._psname

    def _create_pvs(self):
        raise NotImplementedError()

    def _setup_ui(self):
        # Optional header layout
        if self._header:
            self.header_layout = QHBoxLayout()
            self.layout_with_header = QVBoxLayout()

            self.state_header = QLabel("State", self)
            self.state_header.setObjectName("state_header")
            self.psname_header = QLabel("Power Supply", self)
            self.psname_header.setObjectName("psname_header")
            self.analog_sp_header = QLabel(self._analog_name + "-SP", self)
            self.analog_sp_header.setObjectName("analog_sp_header")
            self.analog_mon_header = QLabel(self._analog_name + "-Mon", self)
            self.analog_mon_header.setObjectName("analog_mon_header")

            self.header_layout.addWidget(self.state_header)
            self.header_layout.addWidget(self.psname_header)
            self.header_layout.addWidget(self.analog_sp_header)
            self.header_layout.addWidget(self.analog_mon_header)
            if self._has_trim:
                self.trim_header = QLabel("Trims", self)
                self.trim_header.setObjectName("trim_header")
                self.header_layout.addWidget(self.trim_header)
            self.header_layout.addStretch()

        self.layout = QHBoxLayout()

        # Widgets
        self.pwrstate_button = PyDMStateButton(
            parent=self, init_channel="ca://" + self._pwrstate_sp_pv)
        self.pwrstate_button.setObjectName("pwrstate_button")
        self.state_led = PyDMLed(self, "ca://" + self._pwrstate_rb_pv)
        self.state_led.setObjectName("state_led")
        self.state_widget = QWidget(self)
        self.state_widget.setObjectName("state_widget")
        self.state_widget.layout = QHBoxLayout()
        self.state_widget.setLayout(self.state_widget.layout)
        self.state_widget.layout.addWidget(self.pwrstate_button)
        self.state_widget.layout.addWidget(self.state_led)
        self.psname_label = QPushButton(self._psname, self)
        self.psname_label.setObjectName("psname_button")
        # self.pwrstate_button = PyDMLed(
        #     parent=self, init_channel="ca://" + self._pwrstate_sp_pv)
        self.analog_widget = PyDMLinEditScrollbar(
            parent=self, channel="ca://" + self._analog_sp_pv,)
        self.analog_widget.sp_scrollbar.setTracking(False)
        self.analog_widget.setObjectName("analog_widget")
        self.analog_mon_label = PyDMLabel(
            parent=self, init_channel="ca://" + self._analog_mon_pv)
        self.analog_mon_label.setObjectName("analog_label")

        self.layout.addWidget(self.state_widget)
        self.layout.addWidget(self.psname_label)
        self.layout.addWidget(self.analog_widget)
        self.layout.addWidget(self.analog_mon_label)
        if self._has_trim:
            self.trim_button = QPushButton(">", self)
            self.trim_button.setObjectName("trim_button")
            self.layout.addWidget(self.trim_button)
        self.layout.addStretch()

        if self._header:
            self.layout_with_header.addLayout(self.header_layout)
            self.layout_with_header.addLayout(self.layout)
            self.setLayout(self.layout_with_header)
        else:
            self.setLayout(self.layout)

    # def _open_detail_window(self):
    #     if self._detail_window is None:
    #         self._detail_window = MagnetDetailWindow(
    #             psname=self._psname, parent=self)
    #     self._detail_window.show()
    #     self._detail_window.activateWindow()

    # def _open_trim_window(self):
    #     if self._trim_window is None:
    #         self._trim_window = MagnetTrimWindow(
    #             psname=self._psname, parent=self)
    #     self._trim_window.show()

    def paintEvent(self, event):
        """Need to override paintEvent in order to apply CSS."""
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    def get_detail_button(self):
        """Return psname button."""
        return self.psname_label

    def get_trim_button(self):
        """Return trim button."""
        if self._has_trim:
            return self.trim_button
        return None

    def turn_on(self):
        """Turn power supply on."""
        if not self.pwrstate_button._bit_val:
            self.pwrstate_button.send_value()

    def turn_off(self):
        """Turn power supply off."""
        if self.pwrstate_button._bit_val:
            self.pwrstate_button.send_value()

    def sizeHint(self):
        """Return sizeHint."""
        return QSize(1600, 60)


class PulsedPSWidget(BasePSWidget):
    """Widget to control a pulsed magnet."""

    def _create_pvs(self):
        self._analog_name = "Voltage"

        self._pwrstate_sp_pv = self._prefixed_psname + 'PwrState-Sel'
        self._pwrstate_rb_pv = self._prefixed_psname + 'PwrState-Sts'
        self._analog_sp_pv = self._prefixed_psname + 'Voltage-SP'
        self._analog_mon_pv = self._prefixed_psname + 'Voltage-Mon'


class PSWidget(BasePSWidget):
    """Widget to control a magnet."""

    def _create_pvs(self):
        self._analog_name = "Current"
        # PVs
        self._pwrstate_sp_pv = self._prefixed_psname + "PwrState-Sel"
        self._pwrstate_rb_pv = self._prefixed_psname + "PwrState-Sts"
        self._analog_sp_pv = self._prefixed_psname + "Current-SP"
        self._analog_mon_pv = self._prefixed_psname + "Current-Mon"


def run_test(psname=None):
    """Run test application."""
    import sys
    from siriushla.sirius_application import SiriusApplication
    from siriushla import util

    psname = 'SI-Fam:PS-B1B2-1' if psname is None else psname
    app = SiriusApplication()
    util.set_style(app)
    window = PSWidget(psname=psname)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_test()
