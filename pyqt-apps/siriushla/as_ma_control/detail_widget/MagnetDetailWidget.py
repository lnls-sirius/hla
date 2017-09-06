"""MagnetDetailWidget definition."""
import re

from pydm.PyQt.QtGui import QWidget, QGroupBox, QGridLayout, QVBoxLayout, \
    QHBoxLayout, QLabel, QSizePolicy

from siriuspy.envars import vaca_prefix
from pydm.widgets.label import PyDMLabel
# from pydm.widgets.pushbutton import PyDMPushButton
from pydm.widgets.state_button import PyDMStateButton
from pydm.widgets.enum_combo_box import PyDMEnumComboBox
from pydm.widgets.led import PyDMLed
from pydm.widgets.pushbutton import PyDMPushButton
from siriushla.FloatSetPointWidget import FloatSetPointWidget


class MagnetDetailWidget(QWidget):
    """Widget with control interface for a given magnet."""

    StyleSheet = """
        #current > PyDMLabel,
        #metric > PyDMLabel {
            min-width: 7em;
            max-width: 7em;
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
            self._metric_text = "Kick [mrad]"

        self._setup_ui()
        self.setStyleSheet(self.StyleSheet)

    def _setup_ui(self):
        # Group boxes that compose the widget
        self.interlock_box = QGroupBox("Interlock")
        self.interlock_box.setObjectName("interlock")
        self.opmode_box = QGroupBox("Op Mode")
        self.opmode_box.setObjectName("operation_mode")
        self.pwrstate_box = QGroupBox("Pwr State")
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
        layout = QGridLayout()

        layout.addWidget(
            QLabel("<h1>" + self._magnet_name + "</h1>"), 0, 0, 1, 3)
        layout.addWidget(self.interlock_box, 1, 0, 3, 1)
        layout.addWidget(self.opmode_box, 1, 1)
        layout.addWidget(self.pwrstate_box, 1, 2)
        layout.addWidget(self.current_box, 2, 1, 1, 2)
        layout.addWidget(self.metric_box, 3, 1, 1, 2)
        layout.addWidget(self.command_box, 4, 0, 1, 3)
        layout.setColumnStretch(4, 1)
        layout.setRowStretch(5, 1)

        return layout

    def _interlockLayout(self):
        # layout = QVBoxLayout()
        layout = QGridLayout()
        for i in range(16):
            led = PyDMLed(
                self, "ca://" + self._prefixed_magnet + ":Intlk-Mon", i)
            led.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            led.setOnColour(0)
            led.setOffColour(1)

            layout.addWidget(led, i, 0)
            layout.addWidget(QLabel("Bit " + str(i)), i, 1)
        layout.setRowStretch(17, 1)

        return layout

    def _opModeLayout(self):
        layout = QVBoxLayout()

        self.opmode_sp = PyDMEnumComboBox(
            self, "ca://" + self._prefixed_magnet + ":OpMode-Sel")
        self.opmode_rb = PyDMLabel(
            self, "ca://" + self._prefixed_magnet + ":OpMode-Sts")
        self.ctrlmode_led = PyDMLed(
            self, "ca://" + self._prefixed_magnet + ":CtrlMode-Mon",
            enum_map={'Remote': 1, 'Local': 0})
        self.ctrlmode_label = PyDMLabel(
            self, "ca://" + self._prefixed_magnet + ":CtrlMode-Mon")

        self.ctrlmode_led.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        ctrlmode_layout = QHBoxLayout()
        ctrlmode_layout.addWidget(self.ctrlmode_led)
        ctrlmode_layout.addWidget(self.ctrlmode_label)

        layout.addWidget(self.opmode_sp)
        layout.addWidget(self.opmode_rb)
        layout.addLayout(ctrlmode_layout)

        return layout

    def _powerStateLayout(self):
        layout = QVBoxLayout()

        # self.on_btn = PyDMPushButton(
        #     self, label="On", pressValue=1,
        #     init_channel="ca://" + self._prefixed_magnet + ":PwrState-Sel")
        # self.off_btn = PyDMPushButton(
        #     self, label="Off", pressValue=0,
        #     init_channel="ca://" + self._prefixed_magnet + ":PwrState-Sel")
        self.state_button = PyDMStateButton(
            parent=self,
            init_channel="ca://" + self._prefixed_magnet + ":PwrState-Sel")
        self.pwrstate_led = PyDMLed(
            self, "ca://" + self._prefixed_magnet + ":PwrState-Sts")
        self.pwrstate_label = PyDMLabel(
            self, "ca://" + self._prefixed_magnet + ":PwrState-Sts")

        self.pwrstate_led.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        # buttons_layout = QHBoxLayout()
        # buttons_layout.addWidget(self.on_btn)
        # buttons_layout.addWidget(self.off_btn)
        pwrstatus_layout = QHBoxLayout()
        pwrstatus_layout.addWidget(self.pwrstate_led)
        pwrstatus_layout.addWidget(self.pwrstate_label)

        layout.addWidget(self.state_button)
        layout.addLayout(pwrstatus_layout)

        return layout

    def _currentLayout(self):
        layout = QGridLayout()

        self.current_sp_label = QLabel("Setpoint")
        self.current_rb_label = QLabel("Readback")
        self.current_ref_label = QLabel("Ref Mon")
        self.current_mon_label = QLabel("Mon")

        self.current_sp_widget = FloatSetPointWidget(
            parent=self,
            channel="ca://" + self._prefixed_magnet + ":Current-SP")
        self.current_sp_widget.set_limits_from_pv(True)
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
        layout.setRowStretch(4, 1)
        layout.setColumnStretch(3, 1)
        # layout.setRowStretch(2, 1)

        return layout

    def _metricLayout(self):
        layout = QGridLayout()

        self.metric_sp_label = QLabel("Setpoint")
        self.metric_rb_label = QLabel("Readback")
        self.metric_ref_label = QLabel("Ref Mon")
        self.metric_mon_label = QLabel("Mon")

        self.metric_sp_widget = FloatSetPointWidget(
            "ca://" + self._prefixed_magnet + ":" + self._metric + "-SP",
            self)
        self.metric_sp_widget.set_limits_from_pv(True)
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
        layout.setRowStretch(4, 1)
        # layout.setColumnStretch(3, 1)

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
