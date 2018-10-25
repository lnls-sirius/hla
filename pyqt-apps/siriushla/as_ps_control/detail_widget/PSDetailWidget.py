"""MagnetDetailWidget definition."""
import re

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGroupBox, QGridLayout, QLabel, \
    QSizePolicy, QPushButton, QVBoxLayout, QHBoxLayout, QApplication, \
    QFormLayout
from qtpy.QtGui import QColor
# from epics import get_pv

from siriuspy.envars import vaca_prefix
from pydm.widgets import PyDMLabel, PyDMEnumComboBox, PyDMPushButton, \
    PyDMLineEdit, PyDMWaveformPlot
from siriushla.widgets.state_button import PyDMStateButton
from siriushla.widgets import PyDMLinEditScrollbar
from siriushla.widgets.led import SiriusLedState, SiriusLedAlert
from siriushla import util as _util
from .MagnetInterlockWidget import MagnetInterlockWindow


class PSDetailWidget(QWidget):
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
        QLed {
            min-width: 1em;
            max-width: 1em;
            min-height: 1em;
            max-height: 1em;
        }
        PyDMStateButton {
            min-width: 2em;
            max-width: 2em;
        }
    """

    def __init__(self, psname, parent=None):
        """Class constructor."""
        super(PSDetailWidget, self).__init__(parent)
        self._vaca_prefix = vaca_prefix
        self._psname = psname
        self._prefixed_psname = self._vaca_prefix + self._psname
        # self._ps_name = re.sub(":MA-", ":PS-", self._magnet_name)

        if ':MA-' in self._psname:
            self._is_magnet = True
        else:
            self._is_magnet = False

        if self._is_magnet:
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
                unit = _util.get_kick_unit(self._psname)
                self._metric_text = "Kick [{}]".format(unit)

        self._setup_ui()
        self.setFocus(True)
        # Get screen height
        screen_height = QApplication.desktop().screenGeometry().height()
        layout_height = self.layout.sizeHint().height()
        if layout_height > screen_height:
            # Decrease font size
            self.setStyleSheet(self.StyleSheet + '* {font-size: 14px;}')
        else:
            self.setStyleSheet(self.StyleSheet)
        self.layout.setSizeConstraint(QGridLayout.SetFixedSize)

    def _setup_ui(self):
        # Group boxes that compose the widget
        self.version_box = QGroupBox("Version")
        self.version_box.setObjectName("version")
        self.interlock_box = QGroupBox("Interlock")
        self.interlock_box.setObjectName("interlock")
        self.opmode_box = QGroupBox("OpMode")
        self.opmode_box.setObjectName("operation_mode")
        self.pwrstate_box = QGroupBox("PwrState")
        self.pwrstate_box.setObjectName("power_state")
        self.current_box = QGroupBox("Current [A]")
        self.current_box.setObjectName("current")
        if self._is_magnet:
            self.metric_box = QGroupBox(self._metric_text)
            self.metric_box.setObjectName("metric")
        self.command_box = QGroupBox("Commands")
        self.command_box.setObjectName("command_box")
        self.wfm_box = QGroupBox("Waveforms")
        self.wfm_box.setObjectName("wfm_box")
        self.cycle_box = QGroupBox('Cycle')
        self.cycle_box.setObjectName('cycle_box')
        self.pru_box = QGroupBox('PRU')
        self.pru_box.setObjectName('pru_box')

        # Set group boxes layouts
        self.version_box.setLayout(self._versionLayout())
        self.interlock_box.setLayout(self._interlockLayout())
        self.opmode_box.setLayout(self._opModeLayout())
        self.pwrstate_box.setLayout(self._powerStateLayout())
        self.current_box.setLayout(self._currentLayout())
        if self._is_magnet:
            self.metric_box.setLayout(self._metricLayout())
        self.command_box.setLayout(self._commandLayout())
        self.wfm_box.setLayout(self._waveformLayout())
        self.cycle_box.setLayout(self._cycleLayout())
        self.pru_box.setLayout(self._pruLayout())

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

        layout.addWidget(QLabel("<h1>" + self._psname + "</h1>"))
        layout.addLayout(boxes_layout)
        if not self._is_magnet:
            dclink_button = QPushButton('DCLink', self)
            dclink_button.setObjectName('dclink_button')
            layout.addWidget(dclink_button)

        controls.addWidget(self.version_box)
        controls.addWidget(self.interlock_box)
        controls.addWidget(self.opmode_box)
        controls.addWidget(self.pwrstate_box)
        controls.addWidget(self.wfm_box)
        controls.addWidget(self.command_box)

        analogs.addWidget(self.current_box)
        if self._is_magnet:
            analogs.addWidget(self.metric_box)
        analogs.addWidget(self.cycle_box)
        analogs.addWidget(self.pru_box)

        return layout

    def _versionLayout(self):
        layout = QGridLayout()

        self.version_cte = PyDMLabel(
            self, "ca://" + self._prefixed_psname + ":Version-Cte")
        self.version_cte.setObjectName("version_cte_label")

        self.version_cte.setSizePolicy(QSizePolicy.Minimum,
                                       QSizePolicy.Maximum)
        layout.addWidget(self.version_cte, 0, 0, Qt.AlignHCenter)

        return layout

    def _interlockLayout(self):
        # layout = QVBoxLayout()
        layout = QGridLayout()
        soft_intlk_button = QPushButton('Soft Interlock', self)
        hard_intlk_button = QPushButton('Hard Interlock', self)
        openloop_label = QLabel('ControlLoop', self)
        # _util.connect_window(soft_intlk_button, )
        layout.addWidget(soft_intlk_button, 0, 0)
        layout.addWidget(SiriusLedAlert(
            self, "ca://" + self._prefixed_psname + ":IntlkSoft-Mon"), 0, 1)
        layout.addWidget(hard_intlk_button, 1, 0)
        layout.addWidget(SiriusLedAlert(
            self, "ca://" + self._prefixed_psname + ":IntlkHard-Mon"), 1, 1)
        layout.addWidget(openloop_label, 2, 0, Qt.AlignCenter)
        layout.addWidget(SiriusLedAlert(
            self, "ca://" + self._prefixed_psname + ":CtrlLoop-Sts"), 2, 1)

        _util.connect_window(soft_intlk_button, MagnetInterlockWindow, self,
                             **{'magnet': self._psname,
                                'interlock': 0})
        _util.connect_window(hard_intlk_button, MagnetInterlockWindow, self,
                             **{'magnet': self._psname,
                                'interlock': 1})
        return layout

    def _opModeLayout(self):
        layout = QGridLayout()

        self.opmode_sp = PyDMEnumComboBox(
            self, "ca://" + self._prefixed_psname + ":OpMode-Sel")
        self.opmode_rb = PyDMLabel(
            self, "ca://" + self._prefixed_psname + ":OpMode-Sts")
        self.opmode_rb.setObjectName("opmode1_rb_label")
        self.ctrlmode_led = SiriusLedAlert(
            self, "ca://" + self._prefixed_psname + ":CtrlMode-Mon")
        self.ctrlmode_label = PyDMLabel(
            self, "ca://" + self._prefixed_psname + ":CtrlMode-Mon")
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
            init_channel="ca://" + self._prefixed_psname + ":PwrState-Sel")
        self.pwrstate_led = SiriusLedState(
            self, "ca://" + self._prefixed_psname + ":PwrState-Sts")
        # enum_map={'On': PyDMLed.Green, 'Off': PyDMLed.Red})
        self.pwrstate_label = PyDMLabel(
            self, "ca://" + self._prefixed_psname + ":PwrState-Sts")
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
            channel="ca://" + self._prefixed_psname + ":Current-SP")
        # self.current_sp_widget.set_limits_from_pv(True)
        # if self._magnet_type == "b":
        self.current_sp_widget.sp_scrollbar.setTracking(False)
        self.current_rb_val = PyDMLabel(
            self, "ca://" + self._prefixed_psname + ":Current-RB")
        self.current_rb_val.precFromPV = True
        self.current_ref_val = PyDMLabel(
            self, "ca://" + self._prefixed_psname + ":CurrentRef-Mon")
        self.current_ref_val.precFromPV = True
        self.current_mon_val = PyDMLabel(
            self, "ca://" + self._prefixed_psname + ":Current-Mon")
        self.current_mon_val.precFromPV = True

        layout.addWidget(self.current_sp_label, 0, 0, Qt.AlignRight)
        layout.addWidget(self.current_sp_widget, 0, 1)
        layout.addWidget(self.current_rb_label, 1, 0, Qt.AlignRight)
        layout.addWidget(self.current_rb_val, 1, 1)
        layout.addWidget(self.current_ref_label, 2, 0, Qt.AlignRight)
        layout.addWidget(self.current_ref_val, 2, 1)
        layout.addWidget(self.current_mon_label, 3, 0, Qt.AlignRight)
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
            "ca://" + self._prefixed_psname + ":" + self._metric + "-SP",
            self)
        # self.metric_sp_widget.set_limits_from_pv(True)
        # if self._magnet_type == "b":
        self.metric_sp_widget.sp_scrollbar.setTracking(False)
        self.metric_rb_val = PyDMLabel(
            self, "ca://" + self._prefixed_psname + ":" + self._metric + "-RB")
        self.metric_rb_val.precFromPV = True
        self.metric_ref_val = PyDMLabel(
            self,
            "ca://" + self._prefixed_psname + ":" + self._metric + "Ref-Mon")
        self.metric_ref_val.precFromPV = True
        self.metric_mon_val = PyDMLabel(
            self,
            "ca://" + self._prefixed_psname + ":" + self._metric + "-Mon")
        self.metric_mon_val.precFromPV = True

        layout.addWidget(self.metric_sp_label, 0, 0, Qt.AlignRight)
        layout.addWidget(self.metric_sp_widget, 0, 1)
        layout.addWidget(self.metric_rb_label, 1, 0, Qt.AlignRight)
        layout.addWidget(self.metric_rb_val, 1, 1)
        layout.addWidget(self.metric_ref_label, 2, 0, Qt.AlignRight)
        layout.addWidget(self.metric_ref_val, 2, 1)
        layout.addWidget(self.metric_mon_label, 3, 0, Qt.AlignRight)
        layout.addWidget(self.metric_mon_val, 3, 1)
        # layout.addWidget(self.metric_sp_slider, 2, 1)
        # layout.setRowStretch(4, 1)
        layout.setColumnStretch(3, 1)

        return layout

    def _cycleLayout(self):
        layout = QGridLayout()
        enbl_mon_ca = 'ca://' + self._prefixed_psname + ':CycleEnbl-Mon'
        type_sp_ca = 'ca://' + self._prefixed_psname + ':CycleType-Sel'
        type_rb_ca = 'ca://' + self._prefixed_psname + ':CycleType-Sts'
        nrcycles_sp_ca = 'ca://' + self._prefixed_psname + ':CycleNrCycles-SP'
        nrcycles_rb_ca = 'ca://' + self._prefixed_psname + ':CycleNrCycles-RB'
        index_ca = 'ca://' + self._prefixed_psname + ':CycleIndex-Mon'
        freq_sp_ca = 'ca://' + self._prefixed_psname + ':CycleFreq-SP'
        freq_rb_ca = 'ca://' + self._prefixed_psname + ':CycleFreq-RB'
        ampl_sp_ca = 'ca://' + self._prefixed_psname + ':CycleAmpl-SP'
        ampl_rb_ca = 'ca://' + self._prefixed_psname + ':CycleAmpl-RB'
        offset_sp_ca = 'ca://' + self._prefixed_psname + ':CycleOffset-SP'
        offset_rb_ca = 'ca://' + self._prefixed_psname + ':CycleOffset-RB'
        auxparam_sp_ca = 'ca://' + self._prefixed_psname + ':CycleAuxParam-SP'
        auxparam_rb_ca = 'ca://' + self._prefixed_psname + ':CycleAuxParam-RB'
        # 8 labels
        self.cycle_enbl_label = QLabel('Enabled', self)
        self.cycle_type_label = QLabel('Type', self)
        self.cycle_nr_label = QLabel('Nr. Cycles', self)
        self.cycle_index_label = QLabel('Index', self)
        self.cycle_freq_label = QLabel('Frequency', self)
        self.cycle_ampl_label = QLabel('Amplitude', self)
        self.cycle_offset_label = QLabel('Offset', self)
        self.cycle_auxparam_label = QLabel('AuxParams', self)
        # Widgets
        self.cycle_enbl_mon_led = SiriusLedState(self, enbl_mon_ca)
        self.cycle_type_sp_cb = PyDMEnumComboBox(self, type_sp_ca)
        self.cycle_type_rb_label = PyDMLabel(self, type_rb_ca)
        self.cycle_nr_sp_sb = PyDMLineEdit(self, nrcycles_sp_ca)
        self.cycle_nr_rb_label = PyDMLabel(self, nrcycles_rb_ca)
        self.cycle_index_mon_label = PyDMLabel(self, index_ca)
        self.cycle_freq_sp_sb = PyDMLineEdit(self, freq_sp_ca)
        self.cycle_freq_rb_label = PyDMLabel(self, freq_rb_ca)
        self.cycle_ampl_sp_sb = PyDMLineEdit(self, ampl_sp_ca)
        self.cycle_ampl_rb_label = PyDMLabel(self, ampl_rb_ca)
        self.cycle_offset_sp_sb = PyDMLineEdit(self, offset_sp_ca)
        self.cycle_offset_rb_label = PyDMLabel(self, offset_rb_ca)
        self.cycle_auxparam_sp_le = PyDMLineEdit(self, auxparam_sp_ca)
        self.cycle_auxparam_rb_label = PyDMLabel(self, auxparam_rb_ca)
        # Layout
        layout.addWidget(self.cycle_enbl_label, 0, 0, Qt.AlignRight)
        # layout.addWidget(self.cycle_enbl_sp_button, 0, 1)
        # layout.addWidget(self.cycle_dsbl_sp_button, 0, 2)
        layout.addWidget(self.cycle_enbl_mon_led, 0, 1, Qt.AlignCenter)
        layout.addWidget(self.cycle_type_label, 1, 0, Qt.AlignRight)
        layout.addWidget(self.cycle_type_sp_cb, 1, 1)
        layout.addWidget(self.cycle_type_rb_label, 1, 2)
        layout.addWidget(self.cycle_nr_label, 2, 0, Qt.AlignRight)
        layout.addWidget(self.cycle_nr_sp_sb, 2, 1)
        layout.addWidget(self.cycle_nr_rb_label, 2, 2)
        layout.addWidget(self.cycle_index_label, 3, 0, Qt.AlignRight)
        layout.addWidget(self.cycle_index_mon_label, 3, 2)
        layout.addWidget(self.cycle_freq_label, 4, 0, Qt.AlignRight)
        layout.addWidget(self.cycle_freq_sp_sb, 4, 1)
        layout.addWidget(self.cycle_freq_rb_label, 4, 2)
        layout.addWidget(self.cycle_ampl_label, 5, 0, Qt.AlignRight)
        layout.addWidget(self.cycle_ampl_sp_sb, 5, 1)
        layout.addWidget(self.cycle_ampl_rb_label, 5, 2)
        layout.addWidget(self.cycle_offset_label, 6, 0, Qt.AlignRight)
        layout.addWidget(self.cycle_offset_sp_sb, 6, 1)
        layout.addWidget(self.cycle_offset_rb_label, 6, 2)
        layout.addWidget(self.cycle_auxparam_label, 7, 0, Qt.AlignRight)
        layout.addWidget(self.cycle_auxparam_sp_le, 7, 1)
        layout.addWidget(self.cycle_auxparam_rb_label, 7, 2)

        return layout

    def _pruLayout(self):
        layout = QGridLayout()

        sync_mode_ca = 'ca://' + self._prefixed_psname + ':PRUSyncMode-Mon'
        block_index_ca = 'ca://' + self._prefixed_psname + ':PRUBlockIndex-Mon'
        sync_count_ca = \
            'ca://' + self._prefixed_psname + ':PRUSyncPulseCount-Mon'
        queue_size_ca = \
            'ca://' + self._prefixed_psname + ':PRUCtrlQueueSize-Mon'

        sync_mode_label = QLabel('Sync Mode', self)
        block_index_label = QLabel('Block Index', self)
        sync_count_label = QLabel('Pulse Count', self)
        queue_size_label = QLabel('Queue Size', self)

        sync_mode_rb_label = PyDMLabel(self, sync_mode_ca)
        block_index_rb_label = PyDMLabel(self, block_index_ca)
        sync_count_rb_label = PyDMLabel(self, sync_count_ca)
        queue_size_rb_label = PyDMLabel(self, queue_size_ca)

        layout.addWidget(sync_mode_label, 0, 0, Qt.AlignRight)
        layout.addWidget(sync_mode_rb_label, 0, 1)
        layout.addWidget(block_index_label, 1, 0, Qt.AlignRight)
        layout.addWidget(block_index_rb_label, 1, 1)
        layout.addWidget(sync_count_label, 2, 0, Qt.AlignRight)
        layout.addWidget(sync_count_rb_label, 2, 1)
        layout.addWidget(queue_size_label, 3, 0, Qt.AlignRight)
        layout.addWidget(queue_size_rb_label, 3, 1)

        layout.setColumnStretch(2, 1)

        return layout

    def _commandLayout(self):
        layout = QHBoxLayout()

        reset_pv = "ca://" + self._prefixed_psname + ":Reset-Cmd"
        abort_pv = "ca://" + self._prefixed_psname + ":Abort-Cmd"

        self.abort_btn = PyDMPushButton(
            parent=self, label="Abort", pressValue=1, init_channel=abort_pv)
        self.reset_btn = PyDMPushButton(
            parent=self, label="Reset", pressValue=1, init_channel=reset_pv)

        layout.addWidget(self.abort_btn)
        layout.addWidget(self.reset_btn)

        return layout

    def _waveformLayout(self):
        layout = QVBoxLayout()

        wfm_data_sp_ch = "ca://" + self._prefixed_psname + ":WfmData-SP"
        wfm_data_rb_ch = "ca://" + self._prefixed_psname + ":WfmData-RB"

        self.wfmdata = PyDMWaveformPlot()
        self.wfmdata.setMaximumSize(400, 300)
        self.wfmdata.autoRangeX = True
        self.wfmdata.autoRangeY = True
        self.wfmdata.setBackgroundColor(QColor(255, 255, 255))
        self.wfmdata.setShowLegend(True)
        self.wfmdata.addChannel(y_channel=wfm_data_sp_ch, name='WfmData-SP',
                                color='red', lineWidth=2)
        self.wfmdata.addChannel(y_channel=wfm_data_rb_ch, name='WfmData-RB',
                                color='blue', lineWidth=2)
        layout.addWidget(self.wfmdata)

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

        if dipole.match(self._psname):
            return "b"
        elif quadrupole.match(self._psname) or \
                skew_quad.match(self._psname):
            return "q"
        elif sextupole.match(self._psname):
            return "s"
        elif slow_corrector.match(self._psname):
            return "sc"
        elif fast_corrector.match(self._psname):
            return "fc"
        else:
            raise ValueError("Element not defined")


class DCLinkDetailWidget(PSDetailWidget):

    def _setup_ui(self):
        # Group boxes that compose the widget
        self.version_box = QGroupBox("Version")
        self.version_box.setObjectName("version")
        self.interlock_box = QGroupBox("Interlock")
        self.interlock_box.setObjectName("interlock")
        self.pwrstate_box = QGroupBox("PwrState")
        self.pwrstate_box.setObjectName("power_state")
        self.analog_box = QGroupBox("Current [A]")
        self.analog_box.setObjectName("current")
        self.command_box = QGroupBox("Commands")
        self.command_box.setObjectName("command_box")
        self.aux_box = QGroupBox("Other Params")
        self.aux_box.setObjectName("aux_box")

        # Set group boxes layouts
        self.version_box.setLayout(self._versionLayout())
        self.interlock_box.setLayout(self._interlockLayout())
        self.pwrstate_box.setLayout(self._powerStateLayout())
        self.analog_box.setLayout(self._analogLayout())
        self.command_box.setLayout(self._commandLayout())
        self.aux_box.setLayout(self._auxLayout())

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

        layout.addWidget(QLabel("<h1>" + self._psname + "</h1>"))
        layout.addLayout(boxes_layout)

        controls.addWidget(self.version_box)
        controls.addWidget(self.interlock_box)
        controls.addWidget(self.pwrstate_box)
        controls.addWidget(self.command_box)

        analogs.addWidget(self.analog_box)
        analogs.addWidget(self.aux_box)

        return layout

    def _analogLayout(self):
        raise NotImplementedError

    def _auxLayout(self):
        raise NotImplementedError


class FBPDCLinkDetailWidget(DCLinkDetailWidget):

    def _analogLayout(self):
        layout = QGridLayout()

        self.current_sp_label = QLabel("Setpoint")
        self.current_rb_label = QLabel("Readback")
        self.current_ref_label = QLabel("Ref Mon")
        self.current_mon_label = QLabel("Mon")

        self.current_sp_widget = PyDMLinEditScrollbar(
            parent=self,
            channel="ca://" + self._prefixed_psname + ":Voltage-SP")
        # self.current_sp_widget.set_limits_from_pv(True)
        # if self._magnet_type == "b":
        self.current_sp_widget.sp_lineedit.showUnits = False
        self.current_sp_widget.sp_scrollbar.setTracking(False)
        self.current_rb_val = PyDMLabel(
            self, "ca://" + self._prefixed_psname + ":Voltage-RB")
        self.current_rb_val.precFromPV = True
        self.current_ref_val = PyDMLabel(
            self, "ca://" + self._prefixed_psname + ":VoltageRef-Mon")
        self.current_ref_val.precFromPV = True
        self.current_mon_val = PyDMLabel(
            self, "ca://" + self._prefixed_psname + ":Voltage-Mon")
        self.current_mon_val.precFromPV = True

        layout.addWidget(self.current_sp_label, 0, 0, Qt.AlignRight)
        layout.addWidget(self.current_sp_widget, 0, 1)
        layout.addWidget(self.current_rb_label, 1, 0, Qt.AlignRight)
        layout.addWidget(self.current_rb_val, 1, 1)
        layout.addWidget(self.current_ref_label, 2, 0, Qt.AlignRight)
        layout.addWidget(self.current_ref_val, 2, 1)
        layout.addWidget(self.current_mon_label, 3, 0, Qt.AlignRight)
        layout.addWidget(self.current_mon_val, 3, 1)
        # layout.addWidget(self.current_sp_slider, 2, 1)
        # layout.setRowStretch(4, 1)
        layout.setColumnStretch(2, 1)
        # layout.setRowStretch(2, 1)

        return layout

    def _auxLayout(self):
        layout = QFormLayout()

        self._out_1_mon = PyDMLabel(
            self, 'ca://' + self._prefixed_psname + ':Voltage1-Mon')
        self._out_2_mon = PyDMLabel(
            self, 'ca://' + self._prefixed_psname + ':Voltage2-Mon')
        self._out_3_mon = PyDMLabel(
            self, 'ca://' + self._prefixed_psname + ':Voltage3-Mon')
        self._out_dig_mon = PyDMLabel(
            self, 'ca://' + self._prefixed_psname + ':VoltageDig-Mon')
        self._mod_status_mon = PyDMLabel(
            self, 'ca://' + self._prefixed_psname + ':ModulesStatus-Mon')

        layout.addRow('Voltage 1', self._out_1_mon)
        layout.addRow('Voltage 2', self._out_2_mon)
        layout.addRow('Voltage 3', self._out_3_mon)
        layout.addRow('Voltage dig', self._out_dig_mon)
        layout.addRow('Module Status', self._mod_status_mon)

        return layout


class FACDCLinkDetailWidget(DCLinkDetailWidget):

    def _analogLayout(self):
        layout = QGridLayout()

        self.cap_bank_sp_label = QLabel("Setpoint")
        self.cap_bank_rb_label = QLabel("Readback")
        self.cap_bank_ref_label = QLabel("Ref Mon")
        self.cap_bank_mon_label = QLabel("Mon")

        self.cap_bank_sp_widget = PyDMLinEditScrollbar(
            "ca://" + self._prefixed_psname + ":CapacitorBankVoltage-SP", self)
        self.cap_bank_sp_widget.sp_lineedit.showUnits = False
        self.cap_bank_sp_widget.sp_scrollbar.setTracking(False)
        self.cap_bank_rb_val = PyDMLabel(
            self,
            "ca://" + self._prefixed_psname + ":CapacitorBankVoltage-RB")
        self.cap_bank_rb_val.precFromPV = True
        self.cap_bank_ref_val = PyDMLabel(
            self,
            "ca://" + self._prefixed_psname + ":CapacitorBankVoltageRef-Mon")
        self.cap_bank_ref_val.precFromPV = True
        self.cap_bank_mon_val = PyDMLabel(
            self,
            "ca://" + self._prefixed_psname + ":CapacitorBankVoltage-Mon")
        self.cap_bank_mon_val.precFromPV = True

        layout.addWidget(self.cap_bank_sp_label, 0, 0, Qt.AlignRight)
        layout.addWidget(self.cap_bank_sp_widget, 0, 1)
        layout.addWidget(self.cap_bank_rb_label, 1, 0, Qt.AlignRight)
        layout.addWidget(self.cap_bank_rb_val, 1, 1)
        layout.addWidget(self.cap_bank_ref_label, 2, 0, Qt.AlignRight)
        layout.addWidget(self.cap_bank_ref_val, 2, 1)
        layout.addWidget(self.cap_bank_mon_label, 3, 0, Qt.AlignRight)
        layout.addWidget(self.cap_bank_mon_val, 3, 1)

        layout.setColumnStretch(2, 1)

        return layout

    def _auxLayout(self):
        layout = QFormLayout()

        self.rectifier_voltage_mon = PyDMLabel(
            self, 'ca://' + self._prefixed_psname + ':RectifierVoltage-Mon')
        self.rectifier_current_mon = PyDMLabel(
            self, 'ca://' + self._prefixed_psname + ':RectifierCurrent-Mon')
        self.heatsink_temperature = PyDMLabel(
            self, 'ca://' + self._prefixed_psname + ':HeatSinkTemperature-Mon')
        self.inductors_temperature = PyDMLabel(
            self,
            'ca://' + self._prefixed_psname + ':InductorsTemperature-Mon')
        self.duty_cycle = PyDMLabel(
            self, 'ca://' + self._prefixed_psname + ':PWMDutyCycle-Mon')

        layout.addRow('Rectifier Voltage', self.rectifier_voltage_mon)
        layout.addRow('Rectifier Current', self.rectifier_current_mon)
        layout.addRow('Heatsink Temperatue', self.heatsink_temperature)
        layout.addRow('Inductors Temperature', self.inductors_temperature)
        layout.addRow('PWM Duty Cycle', self.duty_cycle)

        return layout
