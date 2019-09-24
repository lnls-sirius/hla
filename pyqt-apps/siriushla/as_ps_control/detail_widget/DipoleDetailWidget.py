"""Widget for controlling a dipole."""
import re

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QLabel, QSizePolicy, \
    QFrame, QHBoxLayout, QPushButton, QVBoxLayout
import qtawesome as qta

from pydm.widgets import PyDMLabel, PyDMEnumComboBox, PyDMLineEdit, \
    PyDMPushButton
from siriuspy.envars import vaca_prefix
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.search import MASearch
from siriushla import util as _util
from siriushla.widgets import SiriusMainWindow, PyDMStateButton, \
    PyDMLinEditScrollbar, SiriusLedState, SiriusLedAlert
from .PSDetailWidget import PSDetailWidget
from .InterlockWindow import InterlockWindow


class DipoleDetailWidget(PSDetailWidget):
    """Widget that allows controlling a dipole magnet."""

    def __init__(self, magnet_name, parent=None):
        """Class constructor."""
        if re.match("(SI|BO)-Fam:MA-B.*", magnet_name):
            self._magnet_name = _PVName(magnet_name)
            self._prefixed_magnet = vaca_prefix + self._magnet_name
        else:
            raise ValueError("Magnet not supported by this class!")
        self._ps_list = MASearch.conv_maname_2_psnames(self._magnet_name)
        self._ps_list = [vaca_prefix+ps for ps in self._ps_list]
        super(DipoleDetailWidget, self).__init__(self._magnet_name, parent)

    def _setWidgetLayout(self):
        layout = QVBoxLayout()

        # Basic controls
        controls = QGridLayout()
        controls.addWidget(self.version_box, 0, 0, 1, 2)
        controls.addWidget(self.psconn_box, 1, 0, 1, 2)
        controls.addWidget(self.opmode_box, 2, 0)
        controls.addWidget(self.pwrstate_box, 2, 1)
        controls.addWidget(self.ctrlloop_box, 3, 0)
        controls.addWidget(self.interlock_box, 3, 1)
        controls.addWidget(self.pru_box, 4, 0, 1, 2)

        # Analogs
        analogs = QVBoxLayout()
        analogs.addWidget(self.current_box)
        if self._is_magnet:
            analogs.addWidget(self.metric_box)

        # Setup layout
        boxes_layout = QHBoxLayout()
        boxes_layout.addLayout(controls)
        boxes_layout.addLayout(analogs)
        boxes_layout.addWidget(self.cycle_tabs)

        layout.addWidget(QLabel("<h2>" + self._psname + "</h2>"))
        layout.addLayout(boxes_layout)
        if self._magnet_name.sec == 'BO':
            dclink_layout = QHBoxLayout()
            dclink1_button = QPushButton(self._ps_list[0]+'\'s DCLinks', self)
            dclink1_button.setObjectName('dclink1_button')
            dclink2_button = QPushButton(self._ps_list[1]+'\'s DCLinks', self)
            dclink2_button.setObjectName('dclink2_button')
            dclink_layout.addWidget(dclink1_button)
            dclink_layout.addWidget(dclink2_button)
            layout.addLayout(dclink_layout)
        return layout

    def _interlockLayout(self):
        self.soft_intlk_bt = QPushButton(qta.icon('fa5s.list-ul'), '', self)
        self.soft_intlk_bt.setObjectName('soft_intlk_bt')
        self.soft_intlk_bt.setStyleSheet(
            '#soft_intlk_bt{min-width:25px; max-width:25px; icon-size:20px;}')
        _util.connect_window(self.soft_intlk_bt, InterlockWindow, self,
                             **{'devname': self._magnet_name, 'interlock': 0})
        self.led_soft_ma = SiriusLedAlert(
            parent=self, init_channel=self._prefixed_magnet + ':IntlkSoft-Mon')
        self.led_soft_ps0 = SiriusLedAlert(
            parent=self, init_channel=self._ps_list[0] + ':IntlkSoft-Mon')
        self.led_soft_ps1 = SiriusLedAlert(
            parent=self, init_channel=self._ps_list[1] + ':IntlkSoft-Mon')

        self.hard_intlk_bt = QPushButton(qta.icon('fa5s.list-ul'), '', self)
        self.hard_intlk_bt.setObjectName('hard_intlk_bt')
        self.hard_intlk_bt.setStyleSheet(
            '#hard_intlk_bt{min-width:25px; max-width:25px; icon-size:20px;}')
        _util.connect_window(self.hard_intlk_bt, InterlockWindow, self,
                             **{'devname': self._magnet_name, 'interlock': 1})
        self.led_hard_ma = SiriusLedAlert(
            parent=self, init_channel=self._prefixed_magnet + ':IntlkHard-Mon')
        self.led_hard_ps0 = SiriusLedAlert(
            parent=self, init_channel=self._ps_list[0] + ':IntlkHard-Mon')
        self.led_hard_ps1 = SiriusLedAlert(
            parent=self, init_channel=self._ps_list[1] + ':IntlkHard-Mon')

        self.reset_bt = PyDMPushButton(
            parent=self, icon=qta.icon('fa5s.sync'), pressValue=1,
            init_channel=self._prefixed_psname + ":Reset-Cmd")
        self.reset_bt.setObjectName('reset_bt')
        self.reset_bt.setStyleSheet(
            '#reset_bt{min-width:25px; icon-size:20px;}')

        layout = QGridLayout()
        layout.addWidget(self.soft_intlk_bt, 0, 0)
        layout.addWidget(QLabel('Soft', self), 0, 1)
        layout.addWidget(self.led_soft_ma, 0, 2)
        layout.addWidget(self.led_soft_ps0, 0, 3)
        layout.addWidget(self.led_soft_ps1, 0, 4)
        layout.addWidget(self.hard_intlk_bt, 1, 0)
        layout.addWidget(QLabel('Hard', self), 1, 1)
        layout.addWidget(self.led_hard_ma, 1, 2)
        layout.addWidget(self.led_hard_ps0, 1, 3)
        layout.addWidget(self.led_hard_ps1, 1, 4)
        layout.addWidget(self.reset_bt, 2, 2, 1, 3)
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

    def _ctrlLoopLayout(self):
        self.ctrlloop_bt = PyDMStateButton(
            parent=self, init_channel=self._prefixed_magnet + ":CtrlLoop-Sel",
            invert=True)
        self.ctrlloop_label = PyDMLabel(
            parent=self, init_channel=self._prefixed_magnet + ":CtrlLoop-Sts")
        self.ctrlloop_label.setObjectName('ctrlloop_label')
        self.ctrlloop_led = SiriusLedState(
            parent=self, init_channel=self._prefixed_magnet + ":CtrlLoop-Sts")
        self.ctrlloop_led.setOffColor(SiriusLedState.LightGreen)
        self.ctrlloop_led.setOnColor(SiriusLedState.DarkGreen)

        lay_sts = QHBoxLayout()
        lay_sts.addWidget(self.ctrlloop_led)
        lay_sts.addWidget(self.ctrlloop_label)

        self.ctrlloop1_led = SiriusLedState(
            self, self._ps_list[0] + ":CtrlLoop-Sts")
        self.ctrlloop1_led.setOffColor(SiriusLedState.LightGreen)
        self.ctrlloop1_led.setOnColor(SiriusLedState.DarkGreen)
        self.ctrlloop1_label = PyDMLabel(
            self, self._ps_list[0] + ":CtrlLoop-Sts")
        self.ctrlloop1_label.setObjectName("ctrlloop1_label")
        self.ctrlloop2_led = SiriusLedState(
            self, self._ps_list[1] + ":CtrlLoop-Sts")
        self.ctrlloop2_led.setOffColor(SiriusLedState.LightGreen)
        self.ctrlloop2_led.setOnColor(SiriusLedState.DarkGreen)
        self.ctrlloop2_label = PyDMLabel(
            self, self._ps_list[1] + ":CtrlLoop-Sts")
        self.ctrlloop2_label.setObjectName("ctrlloop2_label")

        lay_sts = QHBoxLayout()
        lay_sts.setAlignment(Qt.AlignCenter)
        lay_sts.addWidget(self.ctrlloop_led)
        lay_sts.addWidget(self.ctrlloop_label)
        lay_sts1 = QHBoxLayout()
        lay_sts1.setAlignment(Qt.AlignCenter)
        lay_sts1.addWidget(self.ctrlloop1_led)
        lay_sts1.addWidget(self.ctrlloop1_label)
        lay_sts2 = QHBoxLayout()
        lay_sts2.setAlignment(Qt.AlignCenter)
        lay_sts2.addWidget(self.ctrlloop2_led)
        lay_sts2.addWidget(self.ctrlloop2_label)

        layout = QGridLayout()
        layout.addWidget(self.ctrlloop_bt, 0, 0, Qt.AlignCenter)
        layout.addLayout(lay_sts, 1, 0, Qt.AlignCenter)
        layout.addLayout(lay_sts1, 0, 1, Qt.AlignCenter)
        layout.addLayout(lay_sts2, 1, 1, Qt.AlignCenter)
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

    def _siggenLayout(self):
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
