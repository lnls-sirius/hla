"""Widget to control a power supply.

Exposes basic controls like:
    setpoint/readbacks tension
    setpoint/readbacks kick
    turning on/off
"""
import re

from qtpy.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, \
    QPushButton, QStyleOption, QStyle, QSizePolicy
from qtpy.QtGui import QPainter
from qtpy.QtCore import QSize
from pydm.widgets.label import PyDMLabel

from siriuspy.envars import vaca_prefix as _VACA_PREFIX
from siriushla.widgets import PyDMLinEditScrollbar
from siriushla.widgets.state_button import PyDMStateButton
from siriushla.widgets.led import PyDMLed, SiriusLedAlert

StorageRingFam = re.compile("^SI-Fam:.*$")
Dipole = re.compile("^.*:MA-B.*$")
Quadrupole = re.compile("^.*:MA-Q.*$")
QuadrupoleSkew = re.compile("^.*:MA-QS.*$")
Sextupole = re.compile("^.*:MA-S.*$")
Corrector = re.compile("^.*:MA-(CH|CV|FCH|FCV).*$")

HasTrim = re.compile("^.*SI-Fam:(PS|MA)-Q.*$")
HasSoftHardIntlk = re.compile("^.*:(PS|MA)-.*$")


class BasePSWidget(QWidget):
    """Base widget with basic controls to control a magnet."""

    StyleSheet = """
        #state_header,
        #psname_header,
        #intlk_header,
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
            min-width: 8em;
            max-width: 8em;
        }
        #psname_header,
        #psname_button {
            min-width: 10em;
            max-width: 10em;
            margin-right: 0.5em;
        }
        #intlk_header,
        #intlk_widget {
            min-width: 5em;
            max-width: 5em;
        }
        #analog_sp_header,
        #strength_sp_header,
        #analog_widget,
        #strength_widget {
            min-width: 10em;
            max-width: 10em;
        }
        #analog_mon_header,
        #strength_mon_header,
        #analog_label,
        #strength_label {
            min-width: 10em;
            max-width: 10em;
            qproperty-alignment: AlignCenter;
        }
        #trim_header,
        #trim_button {
            min-width: 5em;
            max-width: 5em;
        }
        PyDMStateButton {
            min-width: 2.5em;
            max-width: 2.5em;
            min-height: 1.5em;
            max-height: 1.5em;
        }
        PyDMLed {
            min-width: 1.5em;
            max-width: 1.5em;
            min-height: 1.5em;
            max-height: 1.5em;
        }
    """

    def __init__(self, psname, header=True, parent=None):
        """Init widget UI."""
        super().__init__(parent)
        if ':MA-' in psname:
            self._is_magnet = True
        else:
            self._is_magnet = False
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

    def _build_header(self):
        self.header_layout = QHBoxLayout()
        self.layout_with_header = QVBoxLayout()

        self.psname_header = QLabel("Power Supply", self)
        self.psname_header.setObjectName("psname_header")
        self.state_header = QLabel("State", self)
        self.state_header.setObjectName("state_header")

        self.header_layout.addWidget(self.psname_header)
        self.header_layout.addWidget(self.state_header)

        if HasSoftHardIntlk.match(self._psname):
            self.intlk_header = QLabel("Interlocks", self)
            self.intlk_header.setObjectName("intlk_header")
            self.header_layout.addWidget(self.intlk_header)

        self.analog_sp_header = QLabel(self._analog_name + "-SP", self)
        self.analog_sp_header.setObjectName("analog_sp_header")
        self.analog_mon_header = QLabel(self._analog_name + "-Mon", self)
        self.analog_mon_header.setObjectName("analog_mon_header")

        self.header_layout.addWidget(self.analog_sp_header)
        self.header_layout.addWidget(self.analog_mon_header)
        # Add magnet strength related widgets
        if self._is_magnet:
            self.strength_sp_header = QLabel(
                self._strength_name + "-SP", self)
            self.strength_sp_header.setObjectName("strength_sp_header")
            self.strength_mon_header = QLabel(
                self._strength_name + "-Mon", self)
            self.strength_mon_header.setObjectName("strength_mon_header")

            self.header_layout.addWidget(self.strength_sp_header)
            self.header_layout.addWidget(self.strength_mon_header)
        # Add trim button
        if self._has_trim:
            self.trim_header = QLabel("Trims", self)
            self.trim_header.setObjectName("trim_header")
            self.header_layout.addWidget(self.trim_header)
        self.header_layout.addStretch()

    def _build_widget(self):
        # Widgets

        # Power Supply button to access detailed window
        self.psname_label = QPushButton(self._psname, self)
        self.psname_label.setObjectName("psname_button")
        # PwrState widgets
        self.pwrstate_button = PyDMStateButton(
            parent=self, init_channel=self._pwrstate_sp_pv)
        self.pwrstate_button.setObjectName("pwrstate_button")
        self.state_led = PyDMLed(self, self._pwrstate_rb_pv)
        self.state_led.setObjectName("state_led")
        self.state_widget = QWidget(self)
        self.state_widget.setObjectName("state_widget")
        self.state_widget.layout = QHBoxLayout()
        self.state_widget.setLayout(self.state_widget.layout)
        self.state_widget.layout.addWidget(self.pwrstate_button)
        self.state_widget.layout.addWidget(self.state_led)

        self.layout.addWidget(self.psname_label)
        self.layout.addWidget(self.state_widget)
        # Interlock leds
        if HasSoftHardIntlk.match(self._psname):
            self.intlksoft_led = \
                SiriusLedAlert(self, self._intlksoft_mon_pv)
            self.intlkhard_led = \
                SiriusLedAlert(self, self._intlkhard_mon_pv)
            self.intlk_widget = QWidget(self)
            self.intlk_widget.setObjectName("intlk_widget")
            self.intlk_widget.layout = QHBoxLayout()
            self.intlk_widget.setLayout(self.intlk_widget.layout)
            self.intlk_widget.layout.addWidget(self.intlksoft_led)
            self.intlk_widget.layout.addWidget(self.intlkhard_led)

            self.layout.addWidget(self.intlk_widget)
        # Analog setpoint widget
        self.analog_widget = PyDMLinEditScrollbar(
            parent=self, channel=self._analog_sp_pv,)
        self.analog_widget.sp_scrollbar.setTracking(False)
        self.analog_widget.setObjectName("analog_widget")
        # Analog mon widget
        self.analog_mon_label = PyDMLabel(
            parent=self, init_channel=self._analog_mon_pv)
        self.analog_mon_label.showUnits = True
        self.analog_mon_label.setObjectName("analog_label")

        self.layout.addWidget(self.analog_widget)
        self.layout.addWidget(self.analog_mon_label)
        # Add strength related widgets
        if self._is_magnet:
            self.strength_widget = PyDMLinEditScrollbar(
                parent=self, channel=self._strength_sp_pv)
            self.strength_widget.setObjectName("strength_widget")
            self.strength_widget.sp_scrollbar.setTracking(False)
            self.strength_mon_label = PyDMLabel(
                parent=self, init_channel=self._strength_mon_pv)
            self.strength_mon_label.showUnits = True
            self.strength_mon_label.setObjectName("strength_label")

            self.layout.addWidget(self.strength_widget)
            self.layout.addWidget(self.strength_mon_label)
        # Add trim button
        if self._has_trim:
            self.trim_button = QPushButton(">", self)
            self.trim_button.setObjectName("trim_button")
            self.layout.addWidget(self.trim_button)
        self.layout.addStretch()

    def _setup_ui(self):
        self.setWindowTitle(self._psname)
        # Widget layout
        self.layout = QHBoxLayout()
        # Optional header layout
        if self._header:
            self._build_header()
        # Builds widget
        self._build_widget()
        # Set widget layout
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

    # def sizePolicy(self):
    #     return QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

    # def sizeHint(self):
    #     """Return sizeHint."""
    #     return QSize(1600, 100)


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
        if HasTrim.match(self._psname):
            self._has_trim = True
        self._analog_name = "Current"
        # PVs
        self._pwrstate_sp_pv = self._prefixed_psname + "PwrState-Sel"
        self._pwrstate_rb_pv = self._prefixed_psname + "PwrState-Sts"
        self._analog_sp_pv = self._prefixed_psname + "Current-SP"
        self._analog_mon_pv = self._prefixed_psname + "Current-Mon"
        self._intlksoft_mon_pv = self._prefixed_psname + "IntlkSoft-Mon"
        self._intlkhard_mon_pv = self._prefixed_psname + "IntlkHard-Mon"


class PulsedMAWidget(BasePSWidget):
    """Widget to control a pulsed magnet."""

    def _create_pvs(self):
        self._analog_name = "Voltage"
        self._strength_name = "Kick"

        self._pwrstate_sp_pv = self._prefixed_psname + 'PwrState-Sel'
        self._pwrstate_rb_pv = self._prefixed_psname + 'PwrState-Sts'
        self._analog_sp_pv = self._prefixed_psname + 'Voltage-SP'
        self._analog_mon_pv = self._prefixed_psname + 'Voltage-Mon'
        self._strength_sp_pv = self._prefixed_psname + 'Kick-SP'
        self._strength_mon_pv = self._prefixed_psname + 'Kick-Mon'


class MAWidget(BasePSWidget):
    """Widget to control a magnet."""

    def _create_pvs(self):
        self._analog_name = "Current"
        # Move to static variables
        if Dipole.match(self._psname):
            self._strength_name = "Energy"
        elif Quadrupole.match(self._psname):
            self._strength_name = "KL"
            # Fam Quads from SI have trims
            if not QuadrupoleSkew.match(self._psname) and \
                    StorageRingFam.match(self._psname):
                self._has_trim = True
        elif Sextupole.match(self._psname):
            self._strength_name = "SL"
        elif Corrector.match(self._psname):
            self._strength_name = "Kick"
        else:
            raise AttributeError("Magnet name is not defined.")
        # PVs
        self._pwrstate_sp_pv = self._prefixed_psname + "PwrState-Sel"
        self._pwrstate_rb_pv = self._prefixed_psname + "PwrState-Sts"
        self._analog_sp_pv = self._prefixed_psname + "Current-SP"
        self._analog_mon_pv = self._prefixed_psname + "Current-Mon"
        self._intlksoft_mon_pv = self._prefixed_psname + "IntlkSoft-Mon"
        self._intlkhard_mon_pv = self._prefixed_psname + "IntlkHard-Mon"
        self._strength_sp_pv = \
            self._prefixed_psname + self._strength_name + "-SP"
        self._strength_mon_pv = \
            self._prefixed_psname + self._strength_name + "-Mon"


class PSWidgetFactory:
    """Return widget."""

    @staticmethod
    def factory(psname, header=False, parent=None):
        """Return apropriate widget."""
        if ':MA-' in psname:
            return MAWidget(psname, header, parent)
        elif ':PM-' in psname:
            return PulsedMAWidget(psname, header, parent)
        elif ':PS-' in psname:
            return PSWidget(psname, header, parent)
        elif ':PM-' in psname:
            return PulsedPSWidget(psname, header, parent)
        else:
            raise ValueError('Unknow device {}'.format(psname))


def run_test(psname=None):
    """Run test application."""
    import sys
    from siriushla.sirius_application import SiriusApplication

    psname = 'SI-Fam:PS-B1B2-1' if psname is None else psname
    app = SiriusApplication()
    window = PSWidget(psname=psname)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_test()
