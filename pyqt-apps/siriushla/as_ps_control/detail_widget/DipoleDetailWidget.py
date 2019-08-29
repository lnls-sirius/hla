"""Widget for controlling a dipole."""
import re

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QLabel, QSizePolicy, \
    QFrame, QHBoxLayout, QPushButton, QVBoxLayout

from pydm.widgets import PyDMLabel, PyDMEnumComboBox, PyDMLineEdit
from siriuspy.envars import vaca_prefix
from siriushla import util as _util
from siriushla.widgets import SiriusMainWindow, PyDMStateButton, \
    PyDMLinEditScrollbar, SiriusLedState, SiriusLedAlert
from .PSDetailWidget import PSDetailWidget
from .MagnetInterlockWidget import MagnetInterlockWindow


class DipoleDetailWidget(PSDetailWidget):
    """Widget that allows controlling a dipole magnet."""

    def __init__(self, magnet_name, parent=None):
        """Class constructor."""
        self._vaca_prefix = vaca_prefix
        if re.match("(SI|BO)-Fam:MA-B.*", magnet_name):
            self._magnet_name = magnet_name
            self._prefixed_magnet = self._vaca_prefix + self._magnet_name
        else:
            raise ValueError("Magnet not supported by this class!")
        ps_name = re.sub(":MA", ":PS", self._prefixed_magnet)
        self._ps_list = [ps_name + "-1", ps_name + "-2"]

        super(DipoleDetailWidget, self).__init__(self._magnet_name, parent)

    def _setWidgetLayout(self):
        layout = QVBoxLayout()
        boxes_layout = QHBoxLayout()
        controls = QVBoxLayout()
        analogs = QVBoxLayout()
        cycle = QVBoxLayout()
        waveform = QVBoxLayout()
        boxes_layout.addLayout(controls)
        boxes_layout.addLayout(analogs)
        boxes_layout.addLayout(cycle)
        boxes_layout.addLayout(waveform)

        layout.addWidget(QLabel("<h2>" + self._psname + "</h2>"))
        layout.addLayout(boxes_layout)
        dclink_layout = QHBoxLayout()
        dclink1_button = QPushButton(
            '{}\'s DCLinks'.format(self._ps_list[0]), self)
        dclink1_button.setObjectName('dclink1_button')
        dclink2_button = QPushButton(
            '{}\'s DCLinks'.format(self._ps_list[1]), self)
        dclink2_button.setObjectName('dclink2_button')
        dclink_layout.addWidget(dclink1_button)
        dclink_layout.addWidget(dclink2_button)
        layout.addLayout(dclink_layout)

        controls.addWidget(self.version_box)
        controls.addWidget(self.interlock_box)
        controls.addWidget(self.opmode_box)
        controls.addWidget(self.pwrstate_box)
        controls.addWidget(self.command_box)

        analogs.addWidget(self.current_box)
        if self._is_magnet:
            analogs.addWidget(self.metric_box)
        analogs.addWidget(self.pru_box)

        cycle.addWidget(self.cycle_box)

        waveform.addWidget(self.wfm_box)

        return layout

    def _interlockLayout(self):
        layout = QGridLayout()
        soft_intlk_button = QPushButton('Soft Interlock', self)
        hard_intlk_button = QPushButton('Hard Interlock', self)
        layout.addWidget(soft_intlk_button, 0, 0)
        layout.addWidget(SiriusLedAlert(
            self, self._prefixed_magnet + ':IntlkSoft-Mon'), 0, 1)
        layout.addWidget(SiriusLedAlert(
            self, self._ps_list[0] + ":IntlkSoft-Mon"), 0, 2)
        layout.addWidget(SiriusLedAlert(
            self, self._ps_list[1] + ":IntlkSoft-Mon"), 0, 3)
        layout.addWidget(hard_intlk_button, 1, 0)
        layout.addWidget(SiriusLedAlert(
            self, self._prefixed_magnet + ':IntlkHard-Mon'), 1, 1)
        layout.addWidget(SiriusLedAlert(
            self, self._ps_list[0] + ":IntlkHard-Mon"), 1, 2)
        layout.addWidget(SiriusLedAlert(
            self, self._ps_list[1] + ":IntlkHard-Mon"), 1, 3)
        # Connect buttons to open magnet interlock windows
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
            self, init_channel=self._prefixed_magnet + ":OpMode-Sel")
        self.opmode_rb = PyDMLabel(
            self, self._prefixed_magnet + ':OpMode-Sts')
        self.opmode_rb.setObjectName('opmode_rb_label')
        self.opmode1_rb = PyDMLabel(
            self, self._ps_list[0] + ":OpMode-Sts")
        self.opmode1_rb.setObjectName("opmode1_rb_label")
        self.opmode2_rb = PyDMLabel(
            self, self._ps_list[1] + ":OpMode-Sts")
        self.opmode2_rb.setObjectName("opmode2_rb_label")

        self.ctrlmode1_led = SiriusLedAlert(
            self, self._ps_list[0] + ":CtrlMode-Mon")
        self.ctrlmode1_label = PyDMLabel(
            self, self._ps_list[0] + ":CtrlMode-Mon")
        self.ctrlmode1_label.setObjectName("ctrlmode1_label")
        self.ctrlmode2_led = SiriusLedAlert(
            self, self._ps_list[1] + ":CtrlMode-Mon")
        self.ctrlmode2_label = PyDMLabel(
            self, self._ps_list[1] + ":CtrlMode-Mon")
        self.ctrlmode2_label.setObjectName("ctrlmode2_label")

        self.ctrlmode1_led.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.ctrlmode2_led.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Fixed)

        ps1_layout = QGridLayout()
        ps1_layout.addWidget(self.ctrlmode1_led, 1, 0)
        ps1_layout.addWidget(self.ctrlmode1_label, 1, 1)

        ps2_layout = QGridLayout()
        ps2_layout.addWidget(self.ctrlmode2_led, 1, 0)
        ps2_layout.addWidget(self.ctrlmode2_label, 1, 1)

        layout.addWidget(self.opmode_sp, 0, 0)
        layout.addWidget(self.opmode_rb, 1, 0, Qt.AlignCenter)
        layout.addWidget(self.opmode1_rb, 2, 0, Qt.AlignCenter)
        layout.addWidget(self.opmode2_rb, 3, 0, Qt.AlignCenter)
        layout.addLayout(ps1_layout, 0, 1, 2, 1, Qt.AlignCenter)
        layout.addLayout(ps2_layout, 2, 1, 2, 1, Qt.AlignCenter)

        return layout

    def _powerStateLayout(self):
        layout = QGridLayout()

        self.state_button = PyDMStateButton(
            parent=self,
            init_channel=self._prefixed_magnet + ":PwrState-Sel")

        self.pwrstate_led = SiriusLedState(
            self, self._prefixed_magnet + ":PwrState-Sts")
        self.pwrstate_label = PyDMLabel(
            self, self._prefixed_magnet + ":PwrState-Sts")
        self.pwrstate1_led = SiriusLedState(
            self, self._ps_list[0] + ":PwrState-Sts")
        self.pwrstate1_label = PyDMLabel(
            self, self._ps_list[0] + ":PwrState-Sts")
        self.pwrstate1_label.setObjectName("pwrstate1_label")
        self.pwrstate2_led = SiriusLedState(
            self, self._ps_list[1] + ":PwrState-Sts")
        self.pwrstate2_label = PyDMLabel(
            self, self._ps_list[1] + ":PwrState-Sts")
        self.pwrstate2_label.setObjectName("pwrstate2_label")

        self.state_button.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.pwrstate1_led.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.pwrstate2_led.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Fixed)

        pwrstatus_layout = QHBoxLayout()
        pwrstatus_layout1 = QHBoxLayout()
        pwrstatus_layout2 = QHBoxLayout()
        pwrstatus_layout.addWidget(self.pwrstate_led)
        pwrstatus_layout.addWidget(self.pwrstate_label)
        pwrstatus_layout1.addWidget(self.pwrstate1_led)
        pwrstatus_layout1.addWidget(self.pwrstate1_label)
        pwrstatus_layout2.addWidget(self.pwrstate2_led)
        pwrstatus_layout2.addWidget(self.pwrstate2_label)

        layout.addWidget(self.state_button, 0, 0, Qt.AlignCenter)
        layout.addLayout(pwrstatus_layout, 1, 0, Qt.AlignCenter)
        layout.addLayout(pwrstatus_layout1, 0, 1, Qt.AlignCenter)
        layout.addLayout(pwrstatus_layout2, 1, 1, Qt.AlignCenter)

        return layout

    def _currentLayout(self):
        layout = QGridLayout()

        self.current_sp_label = QLabel("Setpoint")
        self.current_rb_label = QLabel("Readback")
        self.current_ref_label = QLabel("Ref Mon")
        self.current_mon_label = QLabel("Mon")

        self.current_sp_widget = PyDMLinEditScrollbar(
            parent=self,
            channel=self._prefixed_magnet + ":Current-SP")
        self.current_sp_widget.sp_scrollbar.setTracking(False)
        # Current RB
        self.current_rb_val = PyDMLabel(
            self, self._prefixed_magnet + ":Current-RB")
        self.current_rb_val.precFromPV = True
        self.ps1_current_rb = PyDMLabel(
            self, self._ps_list[0] + ":Current-RB")
        self.ps1_current_rb.precFromPV = True
        self.ps2_current_rb = PyDMLabel(
            self, self._ps_list[1] + ":Current-RB")
        self.ps2_current_rb.precFromPV = True
        # Current Ref
        self.current_ref_val = PyDMLabel(
            self, self._prefixed_magnet + ":CurrentRef-Mon")
        self.current_ref_val.precFromPV = True
        self.ps1_current_ref = PyDMLabel(
            self, self._ps_list[0] + ":CurrentRef-Mon")
        self.ps1_current_ref.precFromPV = True
        self.ps2_current_ref = PyDMLabel(
            self, self._ps_list[1] + ":CurrentRef-Mon")
        self.ps2_current_ref.precFromPV = True
        # Current Mon
        self.current_mon_val = PyDMLabel(
            self, self._prefixed_magnet + ":Current-Mon")
        self.current_mon_val.precFromPV = True
        self.ps1_current_mon = PyDMLabel(
            self, self._ps_list[0] + ":Current-Mon")
        self.ps1_current_mon.precFromPV = True
        self.ps2_current_mon = PyDMLabel(
            self, self._ps_list[1] + ":Current-Mon")
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

        layout.addWidget(self.current_sp_label, 0, 0, Qt.AlignRight)
        layout.addWidget(self.current_sp_widget, 0, 1, 1, 2)
        layout.addWidget(hr3, 1, 0, 1, 3)
        layout.addWidget(self.current_rb_label, 2, 0, Qt.AlignRight)
        layout.addWidget(self.current_rb_val, 2, 1)
        layout.addWidget(self.ps1_current_rb, 2, 2)
        layout.addWidget(self.ps2_current_rb, 3, 2)
        layout.addWidget(hr1, 4, 0, 1, 3)
        layout.addWidget(self.current_ref_label, 5, 0, Qt.AlignRight)
        layout.addWidget(self.current_ref_val, 5, 1)
        layout.addWidget(self.ps1_current_ref, 5, 2)
        layout.addWidget(self.ps2_current_ref, 6, 2)
        layout.addWidget(hr2, 7, 0, 1, 3)
        layout.addWidget(self.current_mon_label, 8, 0, Qt.AlignRight)
        layout.addWidget(self.current_mon_val, 8, 1)
        layout.addWidget(self.ps1_current_mon, 8, 2)
        layout.addWidget(self.ps2_current_mon, 9, 2)
        layout.setColumnStretch(3, 1)

        return layout

    def _cycleLayout(self):
        layout = QGridLayout()
        # 15 cycle pvs
        enbl_rb_ca1 = self._ps_list[0] + ':CycleEnbl-Mon'
        enbl_rb_ca2 = self._ps_list[1] + ':CycleEnbl-Mon'
        type_sp_ca = self._prefixed_magnet + ':CycleType-Sel'
        type_rb_ca1 = self._ps_list[0] + ':CycleType-Sts'
        type_rb_ca2 = self._ps_list[1] + ':CycleType-Sts'
        nrcycles_sp_ca = self._prefixed_magnet + ':CycleNrCycles-SP'
        nrcycles_rb_ca1 = self._ps_list[0] + ':CycleNrCycles-RB'
        nrcycles_rb_ca2 = self._ps_list[1] + ':CycleNrCycles-RB'
        index_ca1 = self._ps_list[0] + ':CycleIndex-Mon'
        index_ca2 = self._ps_list[1] + ':CycleIndex-Mon'
        freq_sp_ca = self._prefixed_magnet + ':CycleFreq-SP'
        freq_rb_ca1 = self._ps_list[0] + ':CycleFreq-RB'
        freq_rb_ca2 = self._ps_list[1] + ':CycleFreq-RB'
        ampl_sp_ca = self._prefixed_magnet + ':CycleAmpl-SP'
        ampl_rb_ca1 = self._ps_list[0] + ':CycleAmpl-RB'
        ampl_rb_ca2 = self._ps_list[1] + ':CycleAmpl-RB'
        offset_sp_ca = self._prefixed_magnet + ':CycleOffset-SP'
        offset_rb_ca1 = self._ps_list[0] + ':CycleOffset-RB'
        offset_rb_ca2 = self._ps_list[1] + ':CycleOffset-RB'
        auxparam_sp_ca = self._prefixed_magnet + ':CycleAuxParam-SP'
        auxparam_rb_ca1 = self._ps_list[0] + ':CycleAuxParam-RB'
        auxparam_rb_ca2 = self._ps_list[1] + ':CycleAuxParam-RB'
        # 8 labels
        self.cycle_enbl_label = QLabel('Enabled', self)
        self.cycle_type_label = QLabel('Type', self)
        self.cycle_nr_label = QLabel('Nr. Cycles', self)
        self.cycle_index_label = QLabel('Index', self)
        self.cycle_freq_label = QLabel('Frequency', self)
        self.cycle_ampl_label = QLabel('Amplitude', self)
        self.cycle_offset_label = QLabel('Offset', self)
        self.cycle_auxparam_label = QLabel('AuxParams', self)
        # 15 widgets
        self.cycle_enbl_rb_led1 = SiriusLedState(self, enbl_rb_ca1)
        self.cycle_enbl_rb_led2 = SiriusLedState(self, enbl_rb_ca2)
        enbl_rb_layout = QHBoxLayout()
        enbl_rb_layout.addWidget(self.cycle_enbl_rb_led1)
        enbl_rb_layout.addWidget(self.cycle_enbl_rb_led2)
        self.cycle_type_sp_cb = PyDMEnumComboBox(self, type_sp_ca)
        self.cycle_type_rb_label1 = PyDMLabel(self, type_rb_ca1)
        self.cycle_type_rb_label2 = PyDMLabel(self, type_rb_ca2)
        type_rb_layout = QVBoxLayout()
        type_rb_layout.addWidget(self.cycle_type_rb_label1)
        type_rb_layout.addWidget(self.cycle_type_rb_label2)
        self.cycle_nr_sp_sb = PyDMLineEdit(self, nrcycles_sp_ca)
        self.cycle_nr_rb_label1 = PyDMLabel(self, nrcycles_rb_ca1)
        self.cycle_nr_rb_label2 = PyDMLabel(self, nrcycles_rb_ca2)
        nrcycles_rb_layout = QVBoxLayout()
        nrcycles_rb_layout.addWidget(self.cycle_nr_rb_label1)
        nrcycles_rb_layout.addWidget(self.cycle_nr_rb_label2)
        self.cycle_index_mon_label1 = PyDMLabel(self, index_ca1)
        self.cycle_index_mon_label2 = PyDMLabel(self, index_ca2)
        index_mon_layout = QVBoxLayout()
        index_mon_layout.addWidget(self.cycle_index_mon_label1)
        index_mon_layout.addWidget(self.cycle_index_mon_label2)
        self.cycle_freq_sp_sb = PyDMLineEdit(self, freq_sp_ca)
        self.cycle_freq_rb_label1 = PyDMLabel(self, freq_rb_ca1)
        self.cycle_freq_rb_label2 = PyDMLabel(self, freq_rb_ca2)
        freq_rb_layout = QVBoxLayout()
        freq_rb_layout.addWidget(self.cycle_freq_rb_label1)
        freq_rb_layout.addWidget(self.cycle_freq_rb_label2)
        self.cycle_ampl_sp_sb = PyDMLineEdit(self, ampl_sp_ca)
        self.cycle_ampl_rb_label1 = PyDMLabel(self, ampl_rb_ca1)
        self.cycle_ampl_rb_label2 = PyDMLabel(self, ampl_rb_ca2)
        ampl_rb_layout = QVBoxLayout()
        ampl_rb_layout.addWidget(self.cycle_ampl_rb_label1)
        ampl_rb_layout.addWidget(self.cycle_ampl_rb_label2)
        self.cycle_offset_sp_sb = PyDMLineEdit(self, offset_sp_ca)
        self.cycle_offset_rb_label1 = PyDMLabel(self, offset_rb_ca1)
        self.cycle_offset_rb_label2 = PyDMLabel(self, offset_rb_ca2)
        offset_rb_layout = QVBoxLayout()
        offset_rb_layout.addWidget(self.cycle_offset_rb_label1)
        offset_rb_layout.addWidget(self.cycle_offset_rb_label2)
        self.cycle_auxparam_sp_le = PyDMLineEdit(self, auxparam_sp_ca)
        self.cycle_auxparam_rb_label1 = PyDMLabel(self, auxparam_rb_ca1)
        self.cycle_auxparam_rb_label2 = PyDMLabel(self, auxparam_rb_ca2)
        auxparam_rb_layout = QVBoxLayout()
        auxparam_rb_layout.addWidget(self.cycle_auxparam_rb_label1)
        auxparam_rb_layout.addWidget(self.cycle_auxparam_rb_label2)

        layout.addWidget(self.cycle_enbl_label, 0, 0, Qt.AlignRight)
        layout.addLayout(enbl_rb_layout, 0, 1)
        layout.addWidget(self.cycle_type_label, 1, 0, Qt.AlignRight)
        layout.addWidget(self.cycle_type_sp_cb, 1, 1)
        layout.addLayout(type_rb_layout, 1, 2)
        layout.addWidget(self.cycle_nr_label, 2, 0, Qt.AlignRight)
        layout.addWidget(self.cycle_nr_sp_sb, 2, 1)
        layout.addLayout(nrcycles_rb_layout, 2, 2)
        layout.addWidget(self.cycle_index_label, 3, 0, Qt.AlignRight)
        layout.addLayout(index_mon_layout, 3, 2)
        layout.addWidget(self.cycle_freq_label, 4, 0, Qt.AlignRight)
        layout.addWidget(self.cycle_freq_sp_sb, 4, 1)
        layout.addLayout(freq_rb_layout, 4, 2)
        layout.addWidget(self.cycle_ampl_label, 5, 0, Qt.AlignRight)
        layout.addWidget(self.cycle_ampl_sp_sb, 5, 1)
        layout.addLayout(ampl_rb_layout, 5, 2)
        layout.addWidget(self.cycle_offset_label, 6, 0, Qt.AlignRight)
        layout.addWidget(self.cycle_offset_sp_sb, 6, 1)
        layout.addLayout(offset_rb_layout, 6, 2)
        layout.addWidget(self.cycle_auxparam_label, 7, 0, Qt.AlignRight)
        layout.addWidget(self.cycle_auxparam_sp_le, 7, 1)
        layout.addLayout(auxparam_rb_layout, 7, 2)
        layout.setRowStretch(8, 1)

        return layout


if __name__ == "__main__":
    import sys
    from sirius_application import SiriusApplication

    app = SiriusApplication()
    w = SiriusMainWindow()
    w.setCentralWidget(DipoleDetailWidget("SI-Fam:MA-B1B2", w))
    w.show()
    sys.exit(app.exec_())
