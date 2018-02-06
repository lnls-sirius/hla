"""Widget to control a pulsed magnet.

Exposes basic controls like:
    setpoint/readbacks tension
    setpoint/readbacks kick
    turning on/off
"""
import re

from pydm.PyQt.QtGui import QWidget, QHBoxLayout, QVBoxLayout, QLabel, \
    QPushButton, QStyleOption, QStyle, QPainter
from pydm.PyQt.QtCore import QSize
from pydm.widgets.label import PyDMLabel

from siriuspy.envars import vaca_prefix as _VACA_PREFIX
from siriushla.widgets import PyDMLinEditScrollbar
from siriushla.widgets.state_button import PyDMStateButton
from siriushla.widgets.led import PyDMLed

StorageRingFam = re.compile("^SI-Fam:.*$")
Dipole = re.compile("^.*:MA-B.*$")
Quadrupole = re.compile("^.*:MA-Q.*$")
QuadrupoleSkew = re.compile("^.*:MA-QS.*$")
Sextupole = re.compile("^.*:MA-S.*$")
Corrector = re.compile("^.*:MA-(CH|CV|FCH|FCV).*$")


class BaseMagnetWidget(QWidget):
    """Base widget with basic controls to control a magnet."""

    StyleSheet = """
        #maname_header,
        #state_header,
        #analog_sp_header,
        #analog_mon_header,
        #strength_sp_header,
        #strength_mon_header,
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
        #maname_header,
        #maname_button {
            min-width: 300px;
            max-width: 300px;
            margin-right: 20px;
        }
        #analog_sp_header,
        #strength_sp_header,
        #analog_widget,
        #strength_widget {
            min-width: 250px;
            max-width: 250px;
        }
        #analog_mon_header,
        #strength_mon_header,
        #analog_label,
        #strength_label {
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

    def __init__(self, maname, header=True, parent=None):
        """Init widget UI."""
        super().__init__(parent)
        self._maname = maname
        self._prefixed_maname = _VACA_PREFIX + self._maname + ":"
        self._header = header
        self._has_trim = False

        self._detail_window = None
        self._trim_window = None

        self._create_pvs()

        self._setup_ui()
        # self.maname_label.clicked.connect(self._open_detail_window)
        # if self._has_trim:
        #     self.trim_button.clicked.connect(self._open_trim_window)
        self.setStyleSheet(self.StyleSheet)

        self.setObjectName(self._maname)

    @property
    def maname(self):
        """Magnet name."""
        return self._maname

    def _create_pvs(self):
        raise NotImplementedError()

    def _setup_ui(self):
        # Optional header layout
        if self._header:
            self.header_layout = QHBoxLayout()
            self.layout_with_header = QVBoxLayout()

            self.state_header = QLabel("State", self)
            self.state_header.setObjectName("state_header")
            self.maname_header = QLabel("Magnet", self)
            self.maname_header.setObjectName("maname_header")
            self.analog_sp_header = QLabel(self._analog_name + "-SP", self)
            self.analog_sp_header.setObjectName("analog_sp_header")
            self.analog_mon_header = QLabel(self._analog_name + "-Mon", self)
            self.analog_mon_header.setObjectName("analog_mon_header")
            self.strength_sp_header = QLabel(self._strength_name + "-SP", self)
            self.strength_sp_header.setObjectName("strength_sp_header")
            self.strength_mon_header = QLabel(
                self._strength_name + "-Mon", self)
            self.strength_mon_header.setObjectName("strength_mon_header")

            self.header_layout.addWidget(self.state_header)
            self.header_layout.addWidget(self.maname_header)
            self.header_layout.addWidget(self.analog_sp_header)
            self.header_layout.addWidget(self.analog_mon_header)
            self.header_layout.addWidget(self.strength_sp_header)
            self.header_layout.addWidget(self.strength_mon_header)
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
        self.state_led = PyDMLed(
            self, "ca://" + self._pwrstate_rb_pv)
            # enum_map={'On': PyDMLed.Green, 'Off': PyDMLed.Red})
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
        self.analog_widget = PyDMLinEditScrollbar(
            parent=self, channel="ca://" + self._analog_sp_pv,)
        self.analog_widget.sp_scrollbar.setTracking(False)
        self.analog_widget.setObjectName("analog_widget")
        self.analog_mon_label = PyDMLabel(
            parent=self, init_channel="ca://" + self._analog_mon_pv)
        self.analog_mon_label.setObjectName("analog_label")
        self.strength_widget = PyDMLinEditScrollbar(
            parent=self, channel="ca://" + self._strength_sp_pv)
        self.strength_widget.setObjectName("strength_widget")
        self.strength_widget.sp_scrollbar.setTracking(False)
        self.strength_mon_label = PyDMLabel(
            parent=self, init_channel="ca://" + self._strength_mon_pv)
        self.strength_mon_label.setObjectName("strength_label")

        self.layout.addWidget(self.state_widget)
        self.layout.addWidget(self.maname_label)
        self.layout.addWidget(self.analog_widget)
        self.layout.addWidget(self.analog_mon_label)
        self.layout.addWidget(self.strength_widget)
        self.layout.addWidget(self.strength_mon_label)
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
    #             maname=self._maname, parent=self)
    #     self._detail_window.show()
    #     self._detail_window.activateWindow()

    # def _open_trim_window(self):
    #     if self._trim_window is None:
    #         self._trim_window = MagnetTrimWindow(
    #             maname=self._maname, parent=self)
    #     self._trim_window.show()

    def paintEvent(self, event):
        """Need to override paintEvent in order to apply CSS."""
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    def get_detail_button(self):
        """Return maname button."""
        return self.maname_label

    def get_trim_button(self):
        """Return trim button."""
        if self._has_trim:
            return self.trim_button
        return None

    def turn_on(self):
        if not self.pwrstate_button._bit_val:
            self.pwrstate_button.send_value()

    def turn_off(self):
        if self.pwrstate_button._bit_val:
            self.pwrstate_button.send_value()

    def sizeHint(self):
        return QSize(1600, 60)

class PulsedMagnetWidget(BaseMagnetWidget):
    """Widget to control a pulsed magnet."""

    def _create_pvs(self):
        self._analog_name = "Voltage"
        self._strength_name = "Kick"

        self._pwrstate_sp_pv = self._prefixed_maname + 'PwrState-Sel'
        self._pwrstate_rb_pv = self._prefixed_maname + 'PwrState-Sts'
        self._analog_sp_pv = self._prefixed_maname + 'Voltage-SP'
        self._analog_mon_pv = self._prefixed_maname + 'Voltage-Mon'
        self._strength_sp_pv = self._prefixed_maname + 'Kick-SP'
        self._strength_mon_pv = self._prefixed_maname + 'Kick-Mon'


class MagnetWidget(BaseMagnetWidget):
    """Widget to control a magnet."""

    def _create_pvs(self):
        self._analog_name = "Current"
        # Move to static variables
        if Dipole.match(self._maname):
            self._strength_name = "Energy"
        elif Quadrupole.match(self._maname):
            self._strength_name = "KL"
            # Fam Quads from SI have trims
            if not QuadrupoleSkew.match(self._maname) and \
                    StorageRingFam.match(self._maname):
                self._has_trim = True
        elif Sextupole.match(self._maname):
            self._strength_name = "SL"
        elif Corrector.match(self._maname):
            self._strength_name = "Kick"
        else:
            raise AttributeError("Magnet name is not defined.")
        # PVs
        self._pwrstate_sp_pv = self._prefixed_maname + "PwrState-Sel"
        self._pwrstate_rb_pv = self._prefixed_maname + "PwrState-Sts"
        self._analog_sp_pv = self._prefixed_maname + "Current-SP"
        self._analog_mon_pv = self._prefixed_maname + "Current-Mon"
        self._strength_sp_pv = \
            self._prefixed_maname + self._strength_name + "-SP"
        self._strength_mon_pv = \
            self._prefixed_maname + self._strength_name + "-Mon"


# class LedWidget(QWidget):
#     """Led class."""
#
#     def __init__(self, channel, parent=None):
#         """Constructor."""
#         super().__init__(parent)
#         layout = QVBoxLayout()
#         self.led = PyDMLed(
#             parent=self, init_channel="ca://" + channel)
#         layout.addWidget(self.led)
#         self.setLayout(layout)
