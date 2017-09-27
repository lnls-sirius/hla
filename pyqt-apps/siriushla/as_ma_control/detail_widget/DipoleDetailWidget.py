"""Widget for controlling a dipole."""
import re

from pydm.PyQt.QtCore import Qt
from pydm.PyQt.QtGui import QGridLayout, QVBoxLayout, QLabel, QSizePolicy, \
    QFrame, QHBoxLayout

from siriuspy.envars import vaca_prefix
from pydm.widgets.label import PyDMLabel
# from pydm.widgets.pushbutton import PyDMPushButton
from pydm.widgets.state_button import PyDMStateButton
from pydm.widgets.enum_combo_box import PyDMEnumComboBox
from pydm.widgets.led import PyDMLed
from siriushla.as_ma_control.detail_widget.MagnetDetailWidget \
    import MagnetDetailWidget
from siriushla.FloatSetPointWidget import FloatSetPointWidget


class DipoleDetailWidget(MagnetDetailWidget):
    """Widget that allows controlling a dipole magnet."""

    def __init__(self, magnet_name, parent=None):
        """Class constructor."""
        self._vaca_prefix = vaca_prefix
        if re.match("(SI|BO)-Fam:MA-B\w*", magnet_name):
            self._magnet_name = magnet_name
            self._prefixed_magnet = self._vaca_prefix + self._magnet_name
        else:
            raise ValueError("Magnet not supported by this class!")

        ps_name = re.sub(":MA", ":PS", self._prefixed_magnet)
        self._ps_list = [ps_name + "-1",
                         ps_name + "-2"]

        super(DipoleDetailWidget, self).__init__(self._magnet_name, parent)

    def _interlockLayout(self):
        layout = QGridLayout()
        # layout.addWidget(QLabel("PS1"), 0, 0)
        # layout.addWidget(QLabel("PS2"), 0, 1)
        for i in range(16):
            for col, ps in enumerate(self._ps_list):
                led = PyDMLed(self, "ca://" + ps + ":Intlk-Mon", i)
                led.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
                led.setOnColour(0)
                led.setOffColour(1)
                layout.addWidget(led, i, col)
            layout.addWidget(QLabel("Bit " + str(i)), i, 2)
        # layout.setRowStretch(17, 1)
        layout.setColumnStretch(3, 1)

        return layout

    def _opModeLayout(self):
        layout = QGridLayout()

        self.opmode_sp = PyDMEnumComboBox(
            self, init_channel="ca://" + self._prefixed_magnet + ":OpMode-Sel")
        self.opmode1_rb = PyDMLabel(
            self, "ca://" + self._ps_list[0] + ":OpMode-Sts")
        self.opmode1_rb.setObjectName("opmode1_rb_label")
        self.ctrlmode1_led = PyDMLed(
            self, "ca://" + self._ps_list[0] + ":CtrlMode-Mon",
            enum_map={'Remote': 1, 'Local': 0})
        self.ctrlmode1_label = PyDMLabel(
            self, "ca://" + self._ps_list[0] + ":CtrlMode-Mon")
        self.ctrlmode1_label.setObjectName("ctrlmode1_label")
        self.opmode2_rb = PyDMLabel(
            self, "ca://" + self._ps_list[1] + ":OpMode-Sts")
        self.opmode2_rb.setObjectName("opmode2_rb_label")
        self.ctrlmode2_led = PyDMLed(
            self, "ca://" + self._ps_list[1] + ":CtrlMode-Mon",
            enum_map={'Remote': 1, 'Local': 0})
        self.ctrlmode2_label = PyDMLabel(
            self, "ca://" + self._ps_list[1] + ":CtrlMode-Mon")
        self.ctrlmode2_label.setObjectName("ctrlmode2_label")

        self.ctrlmode1_led.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.ctrlmode2_led.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Fixed)

        ps1_layout = QGridLayout()
        # ps1_layout.addWidget(QLabel("PS1"), 0, 0, 1, 2)
        # ps1_layout.addWidget(self.opmode1_rb, 0, 0, 1, 2)
        ps1_layout.addWidget(self.ctrlmode1_led, 1, 0)
        ps1_layout.addWidget(self.ctrlmode1_label, 1, 1)

        ps2_layout = QGridLayout()
        # ps2_layout.addWidget(QLabel("PS2"), 0, 0, 1, 2)
        # ps2_layout.addWidget(self.opmode2_rb, 0, 0, 1, 2)
        ps2_layout.addWidget(self.ctrlmode2_led, 1, 0)
        ps2_layout.addWidget(self.ctrlmode2_label, 1, 1)

        layout.addWidget(self.opmode_sp, 0, 0, 1, 2, Qt.AlignCenter)
        layout.addWidget(self.opmode1_rb, 1, 0)
        layout.addWidget(self.opmode2_rb, 1, 1)
        layout.addLayout(ps1_layout, 2, 0)
        layout.addLayout(ps2_layout, 2, 1)
        # layout.setColumnStretch(2, 1)

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

        self.pwrstate1_led = PyDMLed(
            self, "ca://" + self._ps_list[0] + ":PwrState-Sts")
        self.pwrstate1_label = PyDMLabel(
            self, "ca://" + self._ps_list[0] + ":PwrState-Sts")
        self.pwrstate1_label.setObjectName("pwrstate1_label")
        self.pwrstate2_led = PyDMLed(
            self, "ca://" + self._ps_list[1] + ":PwrState-Sts")
        self.pwrstate2_label = PyDMLabel(
            self, "ca://" + self._ps_list[1] + ":PwrState-Sts")
        self.pwrstate2_label.setObjectName("pwrstate2_label")

        self.pwrstate1_led.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.pwrstate2_led.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Fixed)

        # buttons_layout = QHBoxLayout()
        # buttons_layout.addWidget(self.on_btn)
        # buttons_layout.addWidget(self.off_btn)
        pwrstatus_layout1 = QHBoxLayout()
        pwrstatus_layout2 = QHBoxLayout()
        # pwrstatus_layout.addWidget(QLabel("PS1"), 0, 0, 1, 2)
        # pwrstatus_layout.addWidget(QLabel("PS2"), 0, 2, 1, 2)
        pwrstatus_layout1.addWidget(self.pwrstate1_led)
        pwrstatus_layout1.addWidget(self.pwrstate1_label)
        pwrstatus_layout2.addWidget(self.pwrstate2_led)
        pwrstatus_layout2.addWidget(self.pwrstate2_label)

        layout.addWidget(self.state_button, 0, 0, 1, 2)
        layout.addLayout(pwrstatus_layout1, 1, 0, Qt.AlignCenter)
        layout.addLayout(pwrstatus_layout2, 1, 1, Qt.AlignCenter)
        # layout.addStretch(1)

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
        self.current_sp_widget.sp_scrollbar.setTracking(False)
        # Current RB
        self.current_rb_val = PyDMLabel(
            self, "ca://" + self._prefixed_magnet + ":Current-RB")
        self.current_rb_val.precFromPV = True
        self.ps1_current_rb = PyDMLabel(
            self, "ca://" + self._ps_list[0] + ":Current-RB")
        self.ps1_current_rb.precFromPV = True
        self.ps2_current_rb = PyDMLabel(
            self, "ca://" + self._ps_list[1] + ":Current-RB")
        self.ps2_current_rb.precFromPV = True
        # Current Ref
        self.current_ref_val = PyDMLabel(
            self, "ca://" + self._prefixed_magnet + ":CurrentRef-Mon")
        self.current_ref_val.precFromPV = True
        self.ps1_current_ref = PyDMLabel(
            self, "ca://" + self._ps_list[0] + ":CurrentRef-Mon")
        self.ps1_current_ref.precFromPV = True
        self.ps2_current_ref = PyDMLabel(
            self, "ca://" + self._ps_list[1] + ":CurrentRef-Mon")
        self.ps2_current_ref.precFromPV = True
        # Current Mon
        self.current_mon_val = PyDMLabel(
            self, "ca://" + self._prefixed_magnet + ":Current-Mon")
        self.current_mon_val.precFromPV = True
        self.ps1_current_mon = PyDMLabel(
            self, "ca://" + self._ps_list[0] + ":Current-Mon")
        self.ps1_current_mon.precFromPV = True
        self.ps2_current_mon = PyDMLabel(
            self, "ca://" + self._ps_list[1] + ":Current-Mon")
        self.ps2_current_mon.precFromPV = True

        # Horizontal rulers
        hr1 = QFrame(self)
        hr1.setFrameShape(QFrame.HLine)
        hr1.setFrameShadow(QFrame.Sunken)
        hr2 = QFrame(self)
        hr2.setFrameShape(QFrame.HLine)
        hr2.setFrameShadow(QFrame.Sunken)
        hr3 = QFrame(self)
        hr3.setFrameShape(QFrame.HLine)
        hr3.setFrameShadow(QFrame.Sunken)

        layout.addWidget(self.current_sp_label, 0, 0)
        layout.addWidget(self.current_sp_widget, 0, 1, 1, 2)
        layout.addWidget(hr3, 1, 0, 1, 3)
        layout.addWidget(self.current_rb_label, 2, 0)
        layout.addWidget(self.current_rb_val, 2, 1)
        # layout.addWidget(QLabel("PS1"), 1, 2)
        layout.addWidget(self.ps1_current_rb, 2, 2)
        # layout.addWidget(QLabel("PS2"), 2, 2)
        layout.addWidget(self.ps2_current_rb, 3, 2)
        layout.addWidget(hr1, 4, 0, 1, 3)
        layout.addWidget(self.current_ref_label, 5, 0)
        layout.addWidget(self.current_ref_val, 5, 1)
        # layout.addWidget(QLabel("PS1"), 3, 2)
        layout.addWidget(self.ps1_current_ref, 5, 2)
        # layout.addWidget(QLabel("PS2"), 4, 2)
        layout.addWidget(self.ps2_current_ref, 6, 2)
        layout.addWidget(hr2, 7, 0, 1, 3)
        layout.addWidget(self.current_mon_label, 8, 0)
        layout.addWidget(self.current_mon_val, 8, 1)
        # layout.addWidget(QLabel("PS1"), 5, 2)
        layout.addWidget(self.ps1_current_mon, 8, 2)
        # layout.addWidget(QLabel("PS2"), 6, 2)
        layout.addWidget(self.ps2_current_mon, 9, 2)
        # layout.addWidget(self.current_sp_slider, 3, 1)
        # layout.setRowStretch(10, 1)
        layout.setColumnStretch(3, 1)

        return layout


if __name__ == "__main__":
    import sys
    from pydm import PyDMApplication
    from PyQt5.QtWidgets import QMainWindow
    app = PyDMApplication(None, [])

    w = QMainWindow()
    w.setCentralWidget(DipoleDetailWidget("SI-Fam:MA-B1B2", w))
    w.setStyleSheet("""
    """)
    w.show()

    sys.exit(app.exec_())
