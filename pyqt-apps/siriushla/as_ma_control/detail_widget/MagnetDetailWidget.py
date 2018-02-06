"""MagnetDetailWidget definition."""
import re

from pydm.PyQt.QtCore import Qt
from pydm.PyQt.QtGui import QWidget, QGroupBox, QGridLayout, \
    QLabel, QSizePolicy, QPushButton, QVBoxLayout, QHBoxLayout
# from epics import get_pv

from siriuspy.envars import vaca_prefix
from pydm.widgets.label import PyDMLabel
# from pydm.widgets.pushbutton import PyDMPushButton
from siriushla.widgets.state_button import PyDMStateButton
from pydm.widgets.enum_combo_box import PyDMEnumComboBox
from pydm.widgets.pushbutton import PyDMPushButton
from siriushla.widgets import PyDMLinEditScrollbar
from siriushla.widgets.led import SiriusLedState, SiriusLedAlert
from siriushla import util as _util
from .MagnetInterlockWidget import MagnetInterlockWindow


class MagnetDetailWidget(QWidget):
    """Widget with control interface for a given magnet."""

    StyleSheet = """
        #opmode1_rb_label,
        #opmode2_rb_label {
            min-width: 7em;
            max-width: 7em;
            qproperty-alignment: AlignCenter;
        }
        #ctrlmode1_label,
        #ctrlmode2_label {
            min-width: 4em;
            max-width: 4em;
        }
        #pwrstate_label,
        #pwrstate1_label,
        #pwrstate2_label {
            min-width: 2em;
            max-width: 2em;
        }
        #current > PyDMLabel,
        #metric > PyDMLabel {
            min-width: 7em;
            max-width: 7em;
            qproperty-alignment: AlignCenter;
        }
    """

    def __init__(self, magnet_name, parent=None):
        """Class constructor."""
        super(MagnetDetailWidget, self).__init__(parent)
        self._vaca_prefix = vaca_prefix
        self._magnet_name = magnet_name
        self._prefixed_magnet = self._vaca_prefix + self._magnet_name
        self._ps_name = re.sub(":MA-", ":PS-", self._magnet_name)

        self._magnet_type = self._getElementType()
        if self._magnet_type == "b":
            self._metric = "Energy"
            self._metric_text = "Energy [GeV]"
        elif self._magnet_type == "q":
            self._metric = "KL"
            self._metric_text = "KL [1/m]"
        elif self._magnet_type == "s":
            self._metric = "SL"
            self._metric_text = "SL [1/m^2]"
        elif self._magnet_type in ["sc", "fc"]:
            self._metric = "Kick"
            unit = _util.get_kick_unit(self._magnet_name)
            self._metric_text = "Kick [{}]".format(unit)

        self._setup_ui()
        self.setStyleSheet(self.StyleSheet)
        self.setFocus(True)

    def _setup_ui(self):
        # Group boxes that compose the widget
        self.interlock_box = QGroupBox("Interlock")
        self.interlock_box.setObjectName("interlock")
        self.opmode_box = QGroupBox("OpMode")
        self.opmode_box.setObjectName("operation_mode")
        self.pwrstate_box = QGroupBox("PwrState")
        self.pwrstate_box.setObjectName("power_state")
        self.current_box = QGroupBox("Current [A]")
        self.current_box.setObjectName("current")
        self.metric_box = QGroupBox(self._metric_text)
        self.metric_box.setObjectName("metric")
        self.command_box = QGroupBox("Commands")
        self.command_box.setObjectName("command_box")

        # Set group boxes layouts
        self.interlock_box.setLayout(self._interlockLayout())
        self.opmode_box.setLayout(self._opModeLayout())
        self.pwrstate_box.setLayout(self._powerStateLayout())
        self.current_box.setLayout(self._currentLayout())
        self.metric_box.setLayout(self._metricLayout())
        self.command_box.setLayout(self._commandLayout())

        # Add group boxes to laytout
        self.layout = self._setWidgetLayout()

        # Set widget layout
        self.setLayout(self.layout)

    def _setWidgetLayout(self):
        layout = QVBoxLayout()
        boxes_layout = QHBoxLayout()
        controls = QVBoxLayout()
        analogs = QVBoxLayout()
        boxes_layout.addLayout(controls)
        boxes_layout.addLayout(analogs)

        layout.addWidget(QLabel("<h1>" + self._magnet_name + "</h1>"))
        layout.addLayout(boxes_layout)

        controls.addWidget(self.interlock_box)
        controls.addWidget(self.opmode_box)
        controls.addWidget(self.pwrstate_box)
        controls.addWidget(self.command_box)

        analogs.addWidget(self.current_box)
        analogs.addWidget(self.metric_box)

        return layout

    def _interlockLayout(self):
        # layout = QVBoxLayout()
        layout = QGridLayout()
        soft_intlk_button = QPushButton('Soft Interlock', self)
        hard_intlk_button = QPushButton('Hard Interlock', self)
        # _util.connect_window(soft_intlk_button, )
        layout.addWidget(soft_intlk_button, 0, 0)
        layout.addWidget(SiriusLedAlert(
            self, "ca://" + self._prefixed_magnet + ":IntlkSoft-Mon"), 0, 1)
        layout.addWidget(hard_intlk_button, 1, 0)
        layout.addWidget(SiriusLedAlert(
            self, "ca://" + self._prefixed_magnet + ":IntlkHard-Mon"), 1, 1)

        _util.connect_window(soft_intlk_button, MagnetInterlockWindow, self,
                             **{'magnet': self._magnet_name,
                                'interlock': 0})
        _util.connect_window(hard_intlk_button, MagnetInterlockWindow, self,
                             **{'magnet': self._magnet_name,
                                'interlock': 1})

        return layout

    def _opModeLayout(self):
        layout = QGridLayout()

        self.opmode_sp = PyDMEnumComboBox(
            self, "ca://" + self._prefixed_magnet + ":OpMode-Sel")
        self.opmode_rb = PyDMLabel(
            self, "ca://" + self._prefixed_magnet + ":OpMode-Sts")
        self.opmode_rb.setObjectName("opmode1_rb_label")
        self.ctrlmode_led = SiriusLedAlert(
            self, "ca://" + self._prefixed_magnet + ":CtrlMode-Mon")
        self.ctrlmode_label = PyDMLabel(
            self, "ca://" + self._prefixed_magnet + ":CtrlMode-Mon")
        self.ctrlmode_label.setObjectName("ctrlmode1_label")

        self.ctrlmode_led.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        ctrlmode_layout = QHBoxLayout()
        ctrlmode_layout.addWidget(self.ctrlmode_led)
        ctrlmode_layout.addWidget(self.ctrlmode_label)

        layout.addWidget(self.opmode_sp, 0, 0, Qt.AlignHCenter)
        layout.addWidget(self.opmode_rb, 1, 0, Qt.AlignHCenter)
        layout.addLayout(ctrlmode_layout, 2, 0, Qt.AlignHCenter)
        # layout.setRowStretch(3, 1)
        # layout.setColumnStretch(1, 1)

        return layout

    def _powerStateLayout(self):
        layout = QGridLayout()

        # self.on_btn = PyDMPushButton(
        #     self, label="On", pressValue=1,
        #     init_channel="ca://" + self._prefixed_magnet + ":PwrState-Sel")
        # self.off_btn = PyDMPushButton(
        #     self, label="Off", pressValue=0,
        #     init_channel="ca://" + self._prefixed_magnet + ":PwrState-Sel")
        self.state_button = PyDMStateButton(
            parent=self,
            init_channel="ca://" + self._prefixed_magnet + ":PwrState-Sel")
        self.pwrstate_led = SiriusLedState(
            self, "ca://" + self._prefixed_magnet + ":PwrState-Sts")
        # enum_map={'On': PyDMLed.Green, 'Off': PyDMLed.Red})
        self.pwrstate_label = PyDMLabel(
            self, "ca://" + self._prefixed_magnet + ":PwrState-Sts")
        self.pwrstate_label.setObjectName("pwrstate_label")

        self.pwrstate_led.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        # buttons_layout = QHBoxLayout()
        # buttons_layout.addWidget(self.on_btn)
        # buttons_layout.addWidget(self.off_btn)
        pwrstatus_layout = QHBoxLayout()
        pwrstatus_layout.addWidget(self.pwrstate_led)
        pwrstatus_layout.addWidget(self.pwrstate_label)

        # layout.addStretch(1)
        layout.addWidget(self.state_button, 0, 0, Qt.AlignHCenter)
        layout.addLayout(pwrstatus_layout, 1, 0, Qt.AlignHCenter)
        # layout.addWidget(self.pwrstate_led)
        # layout.addWidget(self.pwrstate_label)
        # layout.addStretch(1)

        return layout

    def _currentLayout(self):
        layout = QGridLayout()

        self.current_sp_label = QLabel("Setpoint")
        self.current_rb_label = QLabel("Readback")
        self.current_ref_label = QLabel("Ref Mon")
        self.current_mon_label = QLabel("Mon")

        self.current_sp_widget = PyDMLinEditScrollbar(
            parent=self,
            channel="ca://" + self._prefixed_magnet + ":Current-SP")
        # self.current_sp_widget.set_limits_from_pv(True)
        # if self._magnet_type == "b":
        self.current_sp_widget.sp_scrollbar.setTracking(False)
        self.current_rb_val = PyDMLabel(
            self, "ca://" + self._prefixed_magnet + ":Current-RB")
        self.current_rb_val.precFromPV = True
        self.current_ref_val = PyDMLabel(
            self, "ca://" + self._prefixed_magnet + ":CurrentRef-Mon")
        self.current_ref_val.precFromPV = True
        self.current_mon_val = PyDMLabel(
            self, "ca://" + self._prefixed_magnet + ":Current-Mon")
        self.current_mon_val.precFromPV = True

        layout.addWidget(self.current_sp_label, 0, 0)
        layout.addWidget(self.current_sp_widget, 0, 1)
        layout.addWidget(self.current_rb_label, 1, 0)
        layout.addWidget(self.current_rb_val, 1, 1)
        layout.addWidget(self.current_ref_label, 2, 0)
        layout.addWidget(self.current_ref_val, 2, 1)
        layout.addWidget(self.current_mon_label, 3, 0)
        layout.addWidget(self.current_mon_val, 3, 1)
        # layout.addWidget(self.current_sp_slider, 2, 1)
        # layout.setRowStretch(4, 1)
        layout.setColumnStretch(2, 1)
        # layout.setRowStretch(2, 1)

        return layout

    def _metricLayout(self):
        layout = QGridLayout()

        self.metric_sp_label = QLabel("Setpoint")
        self.metric_rb_label = QLabel("Readback")
        self.metric_ref_label = QLabel("Ref Mon")
        self.metric_mon_label = QLabel("Mon")

        self.metric_sp_widget = PyDMLinEditScrollbar(
            "ca://" + self._prefixed_magnet + ":" + self._metric + "-SP",
            self)
        # self.metric_sp_widget.set_limits_from_pv(True)
        # if self._magnet_type == "b":
        self.metric_sp_widget.sp_scrollbar.setTracking(False)
        self.metric_rb_val = PyDMLabel(
            self, "ca://" + self._prefixed_magnet + ":" + self._metric + "-RB")
        self.metric_rb_val.precFromPV = True
        self.metric_ref_val = PyDMLabel(
            self,
            "ca://" + self._prefixed_magnet + ":" + self._metric + "Ref-Mon")
        self.metric_ref_val.precFromPV = True
        self.metric_mon_val = PyDMLabel(
            self,
            "ca://" + self._prefixed_magnet + ":" + self._metric + "-Mon")
        self.metric_mon_val.precFromPV = True

        layout.addWidget(self.metric_sp_label, 0, 0)
        layout.addWidget(self.metric_sp_widget, 0, 1)
        layout.addWidget(self.metric_rb_label, 1, 0)
        layout.addWidget(self.metric_rb_val, 1, 1)
        layout.addWidget(self.metric_ref_label, 2, 0)
        layout.addWidget(self.metric_ref_val, 2, 1)
        layout.addWidget(self.metric_mon_label, 3, 0)
        layout.addWidget(self.metric_mon_val, 3, 1)
        # layout.addWidget(self.metric_sp_slider, 2, 1)
        # layout.setRowStretch(4, 1)
        layout.setColumnStretch(3, 1)

        return layout

    def _commandLayout(self):
        layout = QHBoxLayout()

        reset_pv = "ca://" + self._prefixed_magnet + ":Reset-Cmd"
        abort_pv = "ca://" + self._prefixed_magnet + ":Abort-Cmd"

        self.abort_btn = PyDMPushButton(
            parent=self, label="Abort", pressValue=1, init_channel=abort_pv)
        self.reset_btn = PyDMPushButton(
            parent=self, label="Reset", pressValue=1, init_channel=reset_pv)

        layout.addWidget(self.abort_btn)
        layout.addWidget(self.reset_btn)

        return layout

    def _getElementType(self):
        dipole = re.compile("(SI|BO|LI|TS|TB)-(Fam|\w{2,4}):MA-B")
        quadrupole = re.compile("(SI|BO|LI|TS|TB)-(Fam|\w{2,4}):MA-Q\w+")
        sextupole = re.compile("(SI|BO|LI|TS|TB)-(Fam|\w{2,4}):MA-S\w+$")
        slow_corrector = re.compile(
            "(SI|BO|LI|TS|TB)-(Fam|\w{2,4}):MA-(CH|CV)(-|\w)*")
        fast_corrector = re.compile(
            "(SI|BO|LI|TS|TB)-(Fam|\w{2,4}):MA-(FCH|FCV)(-|\w)*")
        skew_quad = re.compile("(SI|BO|LI|TS|TB)-(Fam|\w{2,4}):MA-QS")

        if dipole.match(self._magnet_name):
            return "b"
        elif quadrupole.match(self._magnet_name) or \
                skew_quad.match(self._magnet_name):
            return "q"
        elif sextupole.match(self._magnet_name):
            return "s"
        elif slow_corrector.match(self._magnet_name):
            return "sc"
        elif fast_corrector.match(self._magnet_name):
            return "fc"
        else:
            raise ValueError("Element not defined")
