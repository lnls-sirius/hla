"""Defines window class to show trims of a magnet."""
# from pydm.PyQt.QtGui import QDialog, QVBoxLayout, QApplication
# from siriushla.as_ma_control.MagnetWidget import MagnetTrimWidget
import re

from pydm.PyQt.QtCore import QSize
from pydm.PyQt.QtGui import QWidget, QHBoxLayout, QVBoxLayout, \
    QLabel, QPushButton, QStyleOption, QStyle, QPainter, \
    QGridLayout, QGroupBox, QDialog, QApplication, QScrollArea
from pydm.widgets.led import PyDMLed
from pydm.widgets.state_button import PyDMStateButton
from pydm.widgets.label import PyDMLabel

from siriuspy.search import MASearch
from siriuspy.envars import vaca_prefix as _VACA_PREFIX
from siriuspy.pulsedps import properties as pu_props
from siriuspy.pulsedma import properties as pm_props
from siriushla.FloatSetPointWidget import FloatSetPointWidget
from siriushla.as_ma_control.MagnetDetailWindow import MagnetDetailWindow
from siriushla.as_ma_control.MagnetWidget import MagnetWidget
# from siriushla.as_ma_control.MagnetTrimWindow import MagnetTrimWindow


class MagnetTrimWindow(QDialog):
    """Allow controlling the trims of a given magnet."""

    def __init__(self, maname, parent=None):
        """Class constructor."""
        super(MagnetTrimWindow, self).__init__(parent)

        self._maname = maname
        # self._ps = re.sub(":MA-", ":PS-", self._maname)

        self._setupUi()
        # self.setStyleSheet(self.STYLESHEET)

        self.app = QApplication.instance()
        self.app.establish_widget_connections(self)

    def _setupUi(self):
        self.setWindowTitle(self._maname + ' Trims')
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.trim_widget = MagnetTrimWidget(maname=self._maname, parent=self)
        self.layout.addWidget(self.trim_widget)

    def closeEvent(self, event):
        """Reimplement close event to close widget connections."""
        self.app.close_widget_connections(self)
        super().closeEvent(event)


# class BaseMagnetWidget(QWidget):
#     """Base widget with basic controls to control a magnet."""
#
#     StyleSheet = """
#         #maname_header,
#         #state_header,
#         #analog_sp_header,
#         #analog_mon_header,
#         #strength_sp_header,
#         #strength_mon_header,
#         #button_header,
#         #trim_header {
#             font-weight: bold;
#         }
#         #state_header,
#         #state_widget {
#             min-width: 150px;
#             max-width: 150px;
#         }
#         #maname_header,
#         #maname_button {
#             min-width: 300px;
#             max-width: 300px;
#             margin-right: 20px;
#         }
#         #analog_sp_header,
#         #strength_sp_header,
#         #analog_widget,
#         #strength_widget {
#             min-width: 250px;
#             max-width: 250px;
#         }
#         #analog_mon_header,
#         #strength_mon_header,
#         #analog_label,
#         #strength_label {
#             min-width: 250px;
#             max-width: 250px;
#         }
#         #trim_header,
#         #trim_button {
#             min-width: 85px;
#             max-width: 85px;
#         }
#     """
#
#     def __init__(self, maname, header=True, parent=None):
#         """Init widget UI."""
#         super().__init__(parent)
#         self._maname = maname
#         self._prefixed_maname = _VACA_PREFIX + self._maname + ":"
#         self._header = header
#         self._has_trim = False
#
#         self._detail_window = None
#         self._trim_window = None
#
#         self._create_pvs()
#
#         self._setup_ui()
#         self.maname_label.clicked.connect(self._open_detail_window)
#         if self._has_trim:
#             self.trim_button.clicked.connect(self._open_trim_window)
#         self.setStyleSheet(self.StyleSheet)
#
#         self.setObjectName(self._maname)
#
#     def _create_pvs(self):
#         raise NotImplementedError()
#
#     def _setup_ui(self):
#         # Optional header layout
#         if self._header:
#             self.header_layout = QHBoxLayout()
#             self.layout_with_header = QVBoxLayout()
#
#             self.state_header = QLabel("State", self)
#             self.state_header.setObjectName("state_header")
#             self.maname_header = QLabel("Magnet", self)
#             self.maname_header.setObjectName("maname_header")
#             self.analog_sp_header = QLabel(self._analog_name + "-SP", self)
#             self.analog_sp_header.setObjectName("analog_sp_header")
#             self.analog_mon_header = QLabel(self._analog_name + "-Mon", self)
#             self.analog_mon_header.setObjectName("analog_mon_header")
#             self.strength_sp_header = QLabel(self._strength_name + "-SP", self)
#             self.strength_sp_header.setObjectName("strength_sp_header")
#             self.strength_mon_header = QLabel(
#                 self._strength_name + "-Mon", self)
#             self.strength_mon_header.setObjectName("strength_mon_header")
#
#             self.header_layout.addWidget(self.state_header)
#             self.header_layout.addWidget(self.maname_header)
#             self.header_layout.addWidget(self.analog_sp_header)
#             self.header_layout.addWidget(self.analog_mon_header)
#             self.header_layout.addWidget(self.strength_sp_header)
#             self.header_layout.addWidget(self.strength_mon_header)
#             if self._has_trim:
#                 self.trim_header = QLabel("Trims", self)
#                 self.trim_header.setObjectName("trim_header")
#                 self.header_layout.addWidget(self.trim_header)
#             self.header_layout.addStretch()
#
#         self.layout = QHBoxLayout()
#
#         # Widgets
#         self.pwrstate_button = PyDMStateButton(
#             parent=self, init_channel="ca://" + self._pwrstate_sp_pv)
#         self.pwrstate_button.setObjectName("pwrstate_button")
#         self.state_led = LedWidget(self._pwrstate_sp_pv, self)
#         self.state_led.setObjectName("state_led")
#         self.state_widget = QWidget(self)
#         self.state_widget.setObjectName("state_widget")
#         self.state_widget.layout = QHBoxLayout()
#         self.state_widget.setLayout(self.state_widget.layout)
#         self.state_widget.layout.addWidget(self.pwrstate_button)
#         self.state_widget.layout.addWidget(self.state_led)
#         self.maname_label = QPushButton(self._maname, self)
#         self.maname_label.setObjectName("maname_button")
#         # self.pwrstate_button = PyDMLed(
#         #     parent=self, init_channel="ca://" + self._pwrstate_sp_pv)
#         self.analog_widget = FloatSetPointWidget(
#             parent=self, channel="ca://" + self._analog_sp_pv,)
#         self.analog_widget.setObjectName("analog_widget")
#         self.analog_mon_label = PyDMLabel(
#             parent=self, init_channel="ca://" + self._analog_mon_pv)
#         self.analog_mon_label.setObjectName("analog_label")
#         self.strength_widget = FloatSetPointWidget(
#             parent=self, channel="ca://" + self._strength_sp_pv)
#         self.strength_widget.setObjectName("strength_widget")
#         self.strength_mon_label = PyDMLabel(
#             parent=self, init_channel="ca://" + self._strength_mon_pv)
#         self.strength_mon_label.setObjectName("strength_label")
#
#         # Configuration
#         self.analog_mon_label.setPrecFromPV(True)
#         self.analog_widget.set_limits_from_pv(True)
#         self.strength_mon_label.setPrecFromPV(True)
#         self.strength_widget.set_limits_from_pv(True)
#
#         self.layout.addWidget(self.state_widget)
#         self.layout.addWidget(self.maname_label)
#         self.layout.addWidget(self.analog_widget)
#         self.layout.addWidget(self.analog_mon_label)
#         self.layout.addWidget(self.strength_widget)
#         self.layout.addWidget(self.strength_mon_label)
#         if self._has_trim:
#             self.trim_button = QPushButton(">", self)
#             self.trim_button.setObjectName("trim_button")
#             self.layout.addWidget(self.trim_button)
#         self.layout.addStretch()
#
#         if self._header:
#             self.layout_with_header.addLayout(self.header_layout)
#             self.layout_with_header.addLayout(self.layout)
#             self.setLayout(self.layout_with_header)
#         else:
#             self.setLayout(self.layout)
#
#     def _open_detail_window(self):
#         if self._detail_window is None:
#             self._detail_window = MagnetDetailWindow(
#                 maname=self._maname, parent=self)
#         self._detail_window.show()
#
#     def _open_trim_window(self):
#         print("func: open_trim_window")
#         if self._trim_window is None:
#             self._trim_window = MagnetTrimWindow(
#                 maname=self._maname, parent=self)
#         self._trim_window.show()
#
#     def paintEvent(self, event):
#         """Need to override paintEvent in order to apply CSS."""
#         opt = QStyleOption()
#         opt.initFrom(self)
#         p = QPainter(self)
#         self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)
#
#
# class PulsedMagnetWidget(BaseMagnetWidget):
#     """Widget to control a pulsed magnet."""
#
#     def _create_pvs(self):
#         self._analog_name = "Tension"
#         self._strength_name = "Kick"
#
#         self._pwrstate_sp_pv = self._prefixed_maname + pu_props.PwrStateSel
#         self._pwrstate_rb_pv = self._prefixed_maname + pu_props.PwrStateSts
#         self._analog_sp_pv = self._prefixed_maname + pu_props.TensionSP
#         self._analog_mon_pv = self._prefixed_maname + pu_props.TensionMon
#         self._strength_sp_pv = self._prefixed_maname + pm_props.StrengthSP
#         self._strength_mon_pv = self._prefixed_maname + pm_props.StrengthMon
#
#
# class MagnetWidget(BaseMagnetWidget):
#     """Widget to control a magnet."""
#
#     StorageRingFam = re.compile("^SI-Fam:.*$")
#     Dipole = re.compile("^.*:MA-B.*$")
#     Quadrupole = re.compile("^.*:MA-Q.*$")
#     QuadrupoleSkew = re.compile("^.*:MA-QS.*$")
#     Sextupole = re.compile("^.*:MA-S.*$")
#     Corrector = re.compile("^.*:MA-(CH|CV|FCH|FCV).*$")
#
#     def _create_pvs(self):
#         self._analog_name = "Current"
#         # Move to static variables
#         if self.Dipole.match(self._maname):
#             self._strength_name = "Energy"
#         elif self.Quadrupole.match(self._maname):
#             self._strength_name = "KL"
#             # Fam Quads from SI have trims
#             if not self.QuadrupoleSkew.match(self._maname) and \
#                     self.StorageRingFam.match(self._maname):
#                 print("Has Trim")
#                 self._has_trim = True
#         elif self.Sextupole.match(self._maname):
#             self._strength_name = "SL"
#         elif self.Corrector.match(self._maname):
#             self._strength_name = "Kick"
#         else:
#             raise AttributeError("Magnet name is not defined.")
#         # PVs
#         self._pwrstate_sp_pv = self._prefixed_maname + "PwrState-Sel"
#         self._pwrstate_rb_pv = self._prefixed_maname + "PwrState-Sts"
#         self._analog_sp_pv = self._prefixed_maname + "Current-SP"
#         self._analog_mon_pv = self._prefixed_maname + "Current-Mon"
#         self._strength_sp_pv = \
#             self._prefixed_maname + self._strength_name + "-SP"
#         self._strength_mon_pv = \
#             self._prefixed_maname + self._strength_name + "-Mon"
#
#
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


class MagnetTrimWidget(QWidget):
    """Widget that show trim of family mangnet."""

    def __init__(self, maname, parent=None):
        """Init UI."""
        super().__init__(parent)
        self._maname = maname
        self._setup_ui()
        # self.setStyleSheet("""""")

    def _setup_ui(self):
        self.layout = QGridLayout()

        self.fam_magnet = MagnetWidget(self._maname, self)
        self.fam_magnet.trim_button.setEnabled(False)
        # Fam Magnet
        self.fam_box = QGroupBox(self._maname)
        fam_box_layout = QHBoxLayout()
        fam_box_layout.addWidget(self.fam_magnet)
        self.fam_box.setLayout(fam_box_layout)
        # Trims
        trims = self._getTrims()

        self.trims_group_1 = QGroupBox()
        self.scroll_area_1 = QScrollArea()
        self.trims_group_2 = QGroupBox()
        self.scroll_area_2 = QScrollArea()
        self.trims_group_1.setLayout(self._createGroupBoxLayout(trims[::2]))
        self.trims_group_2.setLayout(self._createGroupBoxLayout(trims[1::2]))
        self.scroll_area_1.setWidget(self.trims_group_1)
        self.scroll_area_1.setMinimumSize(1550, 600)
        self.scroll_area_2.setWidget(self.trims_group_2)
        self.scroll_area_2.setMinimumSize(1550, 600)
        # Set layout
        self.layout.addWidget(self.fam_box, 0, 0, 1, 2)
        self.layout.addWidget(self.scroll_area_1, 1, 0)
        self.layout.addWidget(self.scroll_area_2, 1, 1)
        # Set widget layout
        self.setLayout(self.layout)

    def _createGroupBoxLayout(self, magnets):
        layout = QVBoxLayout()

        for i, magnet in enumerate(magnets):
            layout.addWidget(MagnetWidget(magnet, self))

        return layout

    def _getTrims(self):
        trims = list()
        ma_pattern = re.compile(re.sub("Fam", "\d{2}[A-Z]\d", self._maname))
        for magnet in MASearch.get_manames():
            if ma_pattern.match(magnet):
                trims.append(magnet)

        trims.sort()

        return trims
