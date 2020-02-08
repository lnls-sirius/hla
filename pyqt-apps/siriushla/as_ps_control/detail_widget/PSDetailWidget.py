"""MagnetDetailWidget definition."""
import re
import numpy as _np
from datetime import datetime as _datetime

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGroupBox, QPushButton, QLabel, \
    QGridLayout, QVBoxLayout, QHBoxLayout, QFormLayout, QTabWidget, \
    QSizePolicy as QSzPlcy, QCheckBox
from qtpy.QtGui import QColor
import qtawesome as qta

from siriuspy.envars import VACA_PREFIX
from pydm.widgets import PyDMLabel, PyDMEnumComboBox, PyDMPushButton, \
    PyDMLineEdit, PyDMWaveformPlot
from siriushla import util
from siriushla.widgets import PyDMStateButton, PyDMLinEditScrollbar, \
    SiriusConnectionSignal, SiriusLedState, SiriusLedAlert
from .InterlockWindow import InterlockWindow, LIInterlockWindow


class PSDetailWidget(QWidget):
    """Widget with control interface for a given magnet."""

    StyleSheet = """
        #opmode1_rb_label,
        #opmode2_rb_label {
            min-width: 7em;
            max-width: 7em;
            qproperty-alignment: AlignCenter;
        }
        #ctrlloop_label,
        #ctrlmode1_label,
        #ctrlmode2_label {
            min-width: 4em;
            max-width: 4em;
            qproperty-alignment: AlignCenter;
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
        #ctrlmode1_psconn_label {
            min-width: 7em;
            max-width: 7em;
            qproperty-alignment: AlignCenter;
        }
        QLed,
        SiriusLedAlert,
        SiriusLedState {
            min-width: 1.5em;
            max-width: 1.5em;
            min-height: 1.5em;
            max-height: 1.5em;
        }
        PyDMStateButton {
            min-width: 2.5em;
            max-width: 2.5em;
            min-height: 1.5em;
            max-height: 1.5em;
        }
        PyDMWaveformPlot {
            min-width: 18em;
            max-width: 18em;
            min-height: 14.4em;
            max-height: 14.4em;
        }
        QTabWidget::pane {
            border-left: 2px solid gray;
            border-bottom: 2px solid gray;
            border-right: 2px solid gray;
        }
    """

    def __init__(self, psname, parent=None):
        """Class constructor."""
        super(PSDetailWidget, self).__init__(parent)
        self._VACA_PREFIX = VACA_PREFIX
        self._psname = psname
        self._prefixed_psname = self._VACA_PREFIX + self._psname

        self._metric = self._getElementMetric()

        self._setup_ui()
        self.setFocus(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setStyleSheet(self.StyleSheet)
        self.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Maximum)

    def _setup_ui(self):
        # Group boxes that compose the widget
        self.frmwr_box = QGroupBox("Firmware && IOC")
        self.frmwr_box.setObjectName("version")
        self.frmwr_box.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Maximum)
        self.interlock_box = QGroupBox("Interlock")
        self.interlock_box.setObjectName("interlock")
        self.pwrstate_box = QGroupBox("PwrState")
        self.pwrstate_box.setObjectName("power_state")
        self.opmode_box = QGroupBox("OpMode")
        self.opmode_box.setObjectName("operation_mode")
        self.ctrlloop_box = QGroupBox('Control Loop')
        self.ctrlloop_box.setObjectName('ctrlloop_box')
        self.params_box = QGroupBox('Params')
        self.params_box.setObjectName('params_box')
        self.current_box = QGroupBox("Current")
        self.current_box.setObjectName("current")
        self.wfm_tab = QWidget()
        self.wfm_tab.setObjectName("wfm_tab")
        self.siggen_tab = QWidget()
        self.siggen_tab.setObjectName('cycle_tab')
        self.cycle_tabs = QTabWidget()
        self.cycle_tabs.addTab(self.siggen_tab, 'SigGen')
        self.cycle_tabs.addTab(self.wfm_tab, 'Wfm')
        if self._psname.sec == 'BO':
            self.cycle_tabs.setCurrentIndex(1)
        if self._metric:
            self.metric_box = QGroupBox(self._metric)
            self.metric_box.setObjectName("metric")

        # Set group boxes layouts
        self.frmwr_box.setLayout(self._frmwrLayout())
        self.interlock_box.setLayout(self._interlockLayout())
        self.pwrstate_box.setLayout(self._powerStateLayout())
        self.opmode_box.setLayout(self._opModeLayout())
        self.ctrlloop_box.setLayout(self._ctrlLoopLayout())
        self.params_box.setLayout(self._paramsLayout())
        self.current_box.setLayout(self._currentLayout())
        self.wfm_tab.setLayout(self._wfmLayout())
        self.siggen_tab.setLayout(self._siggenLayout())
        if self._metric:
            self.metric_box.setLayout(self._metricLayout())

        # Add group boxes to laytout
        self.layout = self._setWidgetLayout()

        # Set widget layout
        self.setLayout(self.layout)

    def _setWidgetLayout(self):
        controls = QGridLayout()
        controls.addWidget(self.frmwr_box, 0, 0, 1, 2)
        controls.addWidget(self.opmode_box, 2, 0)
        controls.addWidget(self.pwrstate_box, 2, 1)
        controls.addWidget(self.ctrlloop_box, 3, 0)
        controls.addWidget(self.interlock_box, 3, 1)
        controls.addWidget(self.params_box, 4, 0, 1, 2)

        analogs = QVBoxLayout()
        analogs.addWidget(self.current_box, Qt.AlignCenter)
        analogs.addWidget(self.metric_box, Qt.AlignCenter)
        analogs.addWidget(self.cycle_tabs, Qt.AlignCenter)

        boxes_layout = QHBoxLayout()
        boxes_layout.addLayout(controls)
        boxes_layout.addLayout(analogs)
        boxes_layout.setStretch(0, 1)
        boxes_layout.setStretch(1, 1)

        dclink_button = QPushButton('DCLink', self)
        dclink_button.setObjectName('dclink_button')

        layout = QVBoxLayout()
        layout.addWidget(QLabel("<h2>" + self._psname + "</h2>"))
        layout.addLayout(boxes_layout)
        layout.addWidget(dclink_button)
        return layout

    def _frmwrLayout(self):
        self.version_label = QLabel('ARM & DSP')
        self.version_label.setObjectName("version_label")
        self.version_label.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Maximum)

        self.version_cte = PyDMLabel(
            self, self._prefixed_psname + ":Version-Cte")
        self.version_cte.setObjectName("version_cte_label")
        self.version_cte.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Maximum)

        self.tstamp_boot_label = QLabel('IOC Boot')
        self.tstamp_boot_label.setObjectName("tstamp_label")
        self.tstamp_boot_label.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Maximum)

        self.tstamp_boot = QLabel('', self)
        self.tstamp_boot_ch = SiriusConnectionSignal(
            self._prefixed_psname + ":TimestampBoot-Cte")
        self.tstamp_boot_ch.new_value_signal[float].connect(
            self._tstamp_boot_met)
        self.tstamp_boot.setObjectName("tstamp_boot_label")
        self.tstamp_boot.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Maximum)

        self.tstamp_update_label = QLabel('IOC Update')
        self.tstamp_update_label.setObjectName("tstamp_label")
        self.tstamp_update_label.setSizePolicy(
            QSzPlcy.Minimum, QSzPlcy.Maximum)

        self.tstamp_update = QLabel('', self)
        self.tstamp_update_ch = SiriusConnectionSignal(
            self._prefixed_psname + ":TimestampUpdate-Mon")
        self.tstamp_update_ch.new_value_signal[float].connect(
            self._tstamp_update_met)
        self.tstamp_update.setObjectName("tstamp_update_label")
        self.tstamp_update.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Maximum)

        layout = QGridLayout()
        layout.addWidget(self.version_label, 0, 0, Qt.AlignHCenter)
        layout.addWidget(self.version_cte, 0, 1, Qt.AlignHCenter)
        layout.addWidget(self.tstamp_boot_label, 1, 0, Qt.AlignHCenter)
        layout.addWidget(self.tstamp_boot, 1, 1, Qt.AlignHCenter)
        layout.addWidget(self.tstamp_update_label, 2, 0, Qt.AlignHCenter)
        layout.addWidget(self.tstamp_update, 2, 1, Qt.AlignHCenter)
        return layout

    @staticmethod
    def conv_time_string(value):
        time_str = _datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')
        time_str += '.{:03d}'.format(int(1e3*(value % 1)))
        return time_str

    def _tstamp_update_met(self, value):
        time_str = self.conv_time_string(value)
        self.tstamp_update.setText(time_str)

    def _tstamp_boot_met(self, value):
        time_str = self.conv_time_string(value)
        self.tstamp_boot.setText(time_str)

    def _psConnLayout(self):
        self.psconnsts_led = SiriusLedState(
            self, self._prefixed_psname + ":PSConnStatus-Mon")
        self.psconnsts_led.setOffColor(SiriusLedState.Red)
        self.psconnsts_led.setObjectName("ctrlmode1_psconn_led")
        self.psconnsts_label = PyDMLabel(
            self, self._prefixed_psname + ":PSConnStatus-Mon")
        self.psconnsts_label.setObjectName("ctrlmode1_psconn_label")

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.psconnsts_led)
        layout.addWidget(self.psconnsts_label)
        return layout

    def _interlockLayout(self):
        # Widgets
        self.soft_intlk_bt = QPushButton(qta.icon('fa5s.list-ul'), '', self)
        self.soft_intlk_bt.setObjectName('soft_intlk_bt')
        self.soft_intlk_bt.setStyleSheet(
            '#soft_intlk_bt{min-width:25px; max-width:25px; icon-size:20px;}')
        util.connect_window(self.soft_intlk_bt, InterlockWindow, self,
                            **{'devname': self._psname, 'interlock': 'Soft'})
        self.soft_intlk_led = SiriusLedAlert(
            parent=self, init_channel=self._prefixed_psname + ":IntlkSoft-Mon")

        self.hard_intlk_bt = QPushButton(qta.icon('fa5s.list-ul'), '', self)
        self.hard_intlk_bt.setObjectName('hard_intlk_bt')
        self.hard_intlk_bt.setStyleSheet(
            '#hard_intlk_bt{min-width:25px; max-width:25px; icon-size:20px;}')
        util.connect_window(self.hard_intlk_bt, InterlockWindow, self,
                            **{'devname': self._psname, 'interlock': 'Hard'})
        self.hard_intlk_led = SiriusLedAlert(
            parent=self, init_channel=self._prefixed_psname + ":IntlkHard-Mon")

        self.reset_bt = PyDMPushButton(
            parent=self, icon=qta.icon('fa5s.sync'), pressValue=1,
            init_channel=self._prefixed_psname + ":Reset-Cmd")
        self.reset_bt.setObjectName('reset_bt')
        self.reset_bt.setStyleSheet(
            '#reset_bt{min-width:25px; max-width:25px; icon-size:20px;}')

        # Build layout
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.soft_intlk_bt, 0, 0)
        layout.addWidget(QLabel('Soft', self, alignment=Qt.AlignCenter), 0, 1)
        layout.addWidget(self.soft_intlk_led, 0, 2)
        layout.addWidget(self.hard_intlk_bt, 1, 0)
        layout.addWidget(QLabel('Hard', self, alignment=Qt.AlignCenter), 1, 1)
        layout.addWidget(self.hard_intlk_led, 1, 2)
        layout.addWidget(self.reset_bt, 2, 2)
        return layout

    def _powerStateLayout(self):
        self.state_button = PyDMStateButton(
            parent=self, init_channel=self._prefixed_psname + ":PwrState-Sel")
        self.pwrstate_led = SiriusLedState(
            parent=self, init_channel=self._prefixed_psname + ":PwrState-Sts")
        self.pwrstate_label = PyDMLabel(
            parent=self, init_channel=self._prefixed_psname + ":PwrState-Sts")
        self.pwrstate_label.setObjectName("pwrstate_label")

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setHorizontalSpacing(4)
        layout.addWidget(self.state_button, 0, 0, 1, 2, Qt.AlignHCenter)
        layout.addWidget(self.pwrstate_led, 1, 0, Qt.AlignRight)
        layout.addWidget(self.pwrstate_label, 1, 1, Qt.AlignLeft)
        return layout

    def _opModeLayout(self):
        self.opmode_sp = PyDMEnumComboBox(
            self, self._prefixed_psname + ":OpMode-Sel")
        self.opmode_rb = PyDMLabel(
            self, self._prefixed_psname + ":OpMode-Sts")
        self.opmode_rb.setObjectName("opmode1_rb_label")
        self.ctrlmode_led = SiriusLedAlert(
            self, self._prefixed_psname + ":CtrlMode-Mon")
        self.ctrlmode_label = PyDMLabel(
            self, self._prefixed_psname + ":CtrlMode-Mon")
        self.ctrlmode_label.setObjectName("ctrlmode1_label")

        ctrlmode_layout = QHBoxLayout()
        ctrlmode_layout.addWidget(self.ctrlmode_led)
        ctrlmode_layout.addWidget(self.ctrlmode_label)

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.opmode_sp, 0, 0, Qt.AlignHCenter)
        layout.addWidget(self.opmode_rb, 1, 0, Qt.AlignHCenter)
        layout.addLayout(ctrlmode_layout, 2, 0, Qt.AlignHCenter)
        return layout

    def _ctrlLoopLayout(self):
        self.ctrlloop_btn = PyDMStateButton(
            parent=self, init_channel=self._prefixed_psname + ":CtrlLoop-Sel",
            invert=True)
        self.ctrlloop_label = PyDMLabel(
            parent=self, init_channel=self._prefixed_psname + ":CtrlLoop-Sts")
        self.ctrlloop_label.setObjectName('ctrlloop_label')
        self.ctrlloop_led = SiriusLedState(
            parent=self, init_channel=self._prefixed_psname + ":CtrlLoop-Sts")
        self.ctrlloop_led.setOffColor(SiriusLedState.LightGreen)
        self.ctrlloop_led.setOnColor(SiriusLedState.DarkGreen)

        lay_sts = QHBoxLayout()
        lay_sts.addWidget(self.ctrlloop_led)
        lay_sts.addWidget(self.ctrlloop_label)

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.ctrlloop_btn, 0, 0, Qt.AlignHCenter)
        layout.addLayout(lay_sts, 1, 0)
        return layout

    def _currentLayout(self):
        self.current_sp_label = QLabel("Setpoint")
        self.current_rb_label = QLabel("Readback")
        self.current_ref_label = QLabel("Ref Mon")
        self.current_mon_label = QLabel("Mon")

        self.current_sp_widget = PyDMLinEditScrollbar(
            parent=self, channel=self._prefixed_psname + ":Current-SP")
        self.current_sp_widget.layout.setContentsMargins(0, 0, 0, 0)
        self.current_sp_widget.sp_scrollbar.setTracking(False)
        self.current_rb_val = PyDMLabel(
            parent=self, init_channel=self._prefixed_psname+":Current-RB")
        self.current_rb_val.showUnits = True
        self.current_rb_val.precFromPV = True
        self.current_ref_val = PyDMLabel(
            parent=self, init_channel=self._prefixed_psname+":CurrentRef-Mon")
        self.current_ref_val.showUnits = True
        self.current_ref_val.precFromPV = True
        self.current_mon_val = PyDMLabel(
            parent=self, init_channel=self._prefixed_psname+":Current-Mon")
        self.current_mon_val.showUnits = True
        self.current_mon_val.precFromPV = True

        layout = QGridLayout()
        layout.addWidget(self.current_sp_label, 0, 0, Qt.AlignRight)
        layout.addWidget(self.current_sp_widget, 0, 1)
        layout.addWidget(self.current_rb_label, 1, 0, Qt.AlignRight)
        layout.addWidget(self.current_rb_val, 1, 1)
        layout.addWidget(self.current_ref_label, 2, 0, Qt.AlignRight)
        layout.addWidget(self.current_ref_val, 2, 1)
        layout.addWidget(self.current_mon_label, 3, 0, Qt.AlignRight)
        layout.addWidget(self.current_mon_val, 3, 1)
        layout.setColumnStretch(2, 1)
        return layout

    def _metricLayout(self):
        metric_sp_ch = self._prefixed_psname+":"+self._metric+"-SP"
        metric_rb_ch = self._prefixed_psname+":"+self._metric+"-RB"
        metric_ref_ch = self._prefixed_psname+":"+self._metric+"Ref-Mon"
        metric_mon_ch = self._prefixed_psname+":"+self._metric+"-Mon"

        self.metric_sp_label = QLabel("Setpoint")
        self.metric_rb_label = QLabel("Readback")
        self.metric_ref_label = QLabel("Ref Mon")
        self.metric_mon_label = QLabel("Mon")

        self.metric_sp_widget = PyDMLinEditScrollbar(
            parent=self, channel=metric_sp_ch)
        self.metric_sp_widget.layout.setContentsMargins(0, 0, 0, 0)
        self.metric_sp_widget.sp_scrollbar.setTracking(False)
        self.metric_rb_val = PyDMLabel(
            parent=self, init_channel=metric_rb_ch)
        self.metric_rb_val.showUnits = True
        self.metric_rb_val.precFromPV = True
        self.metric_ref_val = PyDMLabel(
            parent=self, init_channel=metric_ref_ch)
        self.metric_ref_val.showUnits = True
        self.metric_ref_val.precFromPV = True
        self.metric_mon_val = PyDMLabel(
            parent=self, init_channel=metric_mon_ch)
        self.metric_mon_val.showUnits = True
        self.metric_mon_val.precFromPV = True

        layout = QGridLayout()
        layout.addWidget(self.metric_sp_label, 0, 0, Qt.AlignRight)
        layout.addWidget(self.metric_sp_widget, 0, 1)
        layout.addWidget(self.metric_rb_label, 1, 0, Qt.AlignRight)
        layout.addWidget(self.metric_rb_val, 1, 1)
        layout.addWidget(self.metric_ref_label, 2, 0, Qt.AlignRight)
        layout.addWidget(self.metric_ref_val, 2, 1)
        layout.addWidget(self.metric_mon_label, 3, 0, Qt.AlignRight)
        layout.addWidget(self.metric_mon_val, 3, 1)
        layout.setColumnStretch(3, 1)
        return layout

    def _siggenLayout(self):
        enbl_mon_ca = self._prefixed_psname + ':CycleEnbl-Mon'
        type_sp_ca = self._prefixed_psname + ':CycleType-Sel'
        type_rb_ca = self._prefixed_psname + ':CycleType-Sts'
        nrcycles_sp_ca = self._prefixed_psname + ':CycleNrCycles-SP'
        nrcycles_rb_ca = self._prefixed_psname + ':CycleNrCycles-RB'
        index_ca = self._prefixed_psname + ':CycleIndex-Mon'
        freq_sp_ca = self._prefixed_psname + ':CycleFreq-SP'
        freq_rb_ca = self._prefixed_psname + ':CycleFreq-RB'
        ampl_sp_ca = self._prefixed_psname + ':CycleAmpl-SP'
        ampl_rb_ca = self._prefixed_psname + ':CycleAmpl-RB'
        offset_sp_ca = self._prefixed_psname + ':CycleOffset-SP'
        offset_rb_ca = self._prefixed_psname + ':CycleOffset-RB'
        auxparam_sp_ca = self._prefixed_psname + ':CycleAuxParam-SP'
        auxparam_rb_ca = self._prefixed_psname + ':CycleAuxParam-RB'
        # Labels
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
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self.cycle_enbl_label, 0, 0, Qt.AlignRight)
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

    def _paramsLayout(self):
        queue_size_ca = self._prefixed_psname + ':PRUCtrlQueueSize-Mon'
        queue_size_label = QLabel('IOC Queue Size', self)
        queue_size_rb_label = PyDMLabel(self, queue_size_ca)

        layout = QGridLayout()
        layout.setColumnStretch(3, 1)
        layout.addWidget(queue_size_label, 0, 0, Qt.AlignRight)
        layout.addWidget(queue_size_rb_label, 0, 1)

        if 'DCLink' not in self._prefixed_psname:
            wfm_index_ca = self._prefixed_psname + ':WfmIndex-Mon'
            wfm_count_ca = self._prefixed_psname + ':WfmSyncPulseCount-Mon'
            wfm_updateauto_ca = self._prefixed_psname + ':WfmUpdateAuto-Sts'
            wfm_updateauto_sel = self._prefixed_psname + ':WfmUpdateAuto-Sel'
            syncpulse_cmd_ca = self._prefixed_psname + ':SyncPulse-Cmd'

            wfm_index_label = QLabel('Wfm Index', self)
            wfm_index_rb_label = PyDMLabel(self, wfm_index_ca)

            wfm_count_label = QLabel('Wfm Pulse Count', self)
            wfm_count_rb_label = PyDMLabel(self, wfm_count_ca)

            wfm_updateauto_label = QLabel('Wfm UpdateAuto', self)
            wfm_updateauto_sts_led = SiriusLedState(self, wfm_updateauto_ca)
            wfm_updateauto_btn = PyDMStateButton(self, wfm_updateauto_sel)

            syncpulse_cmd_lb = QLabel('Sync Pulse Cmd', self)
            syncpulse_cmd_btn = PyDMPushButton(
                parent=self, icon=qta.icon('fa5s.step-forward'), pressValue=1,
                init_channel=syncpulse_cmd_ca)
            syncpulse_cmd_btn.setObjectName('syncpulse')
            syncpulse_cmd_btn.setStyleSheet(
                '#syncpulse{min-width:25px; max-width:32px; icon-size:20px;}')

            layout.addWidget(wfm_index_label, 1, 0, Qt.AlignRight)
            layout.addWidget(wfm_index_rb_label, 1, 1)
            layout.addWidget(wfm_count_label, 2, 0, Qt.AlignRight)
            layout.addWidget(wfm_count_rb_label, 2, 1)
            layout.addWidget(wfm_updateauto_label, 3, 0, Qt.AlignRight)
            layout.addWidget(wfm_updateauto_btn, 3, 1, Qt.AlignHCenter)
            layout.addWidget(wfm_updateauto_sts_led, 3, 2)
            layout.addWidget(syncpulse_cmd_lb, 4, 0, Qt.AlignRight)
            layout.addWidget(syncpulse_cmd_btn, 4, 1)
        return layout

    def _wfmLayout(self):
        # Channels
        wfm_data_sp_ch = self._prefixed_psname + ":Wfm-SP"
        wfm_data_rb_ch = self._prefixed_psname + ":Wfm-RB"
        wfm_data_rm_ch = self._prefixed_psname + ":WfmRef-Mon"
        wfm_data_mo_ch = self._prefixed_psname + ":Wfm-Mon"

        # Constants
        self._wfm_data_rm = _np.array([])
        self._wfm_data_mo = _np.array([])
        self._wfm_nrpts_sp = 0
        self._wfm_nrpts_rb = 0
        self._wfm_nrpts_rm = 0
        self._wfm_nrpts_mo = 0

        # NrPoints
        self.wfm_nrpts = QLabel('Nrpts (SP|RB|Ref-Mon|Mon):', self)
        self.wfm_nrpts.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Maximum)
        self.wfm_nrpts_ch_rb = SiriusConnectionSignal(wfm_data_rb_ch)
        self.wfm_nrpts_ch_rb.new_value_signal[_np.ndarray].connect(
            self._wfm_update_rb)
        self.wfm_nrpts_ch_sp = SiriusConnectionSignal(wfm_data_sp_ch)
        self.wfm_nrpts_ch_sp.new_value_signal[_np.ndarray].connect(
            self._wfm_update_sp)
        self.wfm_nrpts_ch_rm = SiriusConnectionSignal(wfm_data_rm_ch)
        self.wfm_nrpts_ch_rm.new_value_signal[_np.ndarray].connect(
            self._wfm_update_rm)
        self.wfm_nrpts_ch_mo = SiriusConnectionSignal(wfm_data_mo_ch)
        self.wfm_nrpts_ch_mo.new_value_signal[_np.ndarray].connect(
            self._wfm_update_mo)

        # Plot
        self.wfm = PyDMWaveformPlot()
        self.wfm.setObjectName('graph')
        self.wfm.setStyleSheet('#graph{max-height:15em; max-width:16.5em;}')
        self.wfm.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Maximum)
        self.wfm.autoRangeX = True
        self.wfm.autoRangeY = True
        self.wfm.setBackgroundColor(QColor(255, 255, 255))
        # self.wfm.setShowLegend(True)
        self.wfm.addChannel(y_channel=wfm_data_sp_ch, name='Wfm-SP',
                            color='red', lineWidth=2)
        self.wfm.addChannel(y_channel=wfm_data_rb_ch, name='Wfm-RB',
                            color='blue', lineWidth=2)
        self.wfm.addChannel(y_channel=wfm_data_rm_ch, name='WfmRef-Mon',
                            color='green', lineWidth=2)
        self.wfm.addChannel(y_channel=wfm_data_mo_ch, name='Wfm-Mon',
                            color='black', lineWidth=2)
        self.wfm.addChannel(y_channel='FAKE:DiffMon2Ref', name='Mon - Ref',
                            color='magenta', lineWidth=2)
        self._wfm_curves = {'Wfm-SP': self.wfm.curveAtIndex(0),
                            'Wfm-RB': self.wfm.curveAtIndex(1),
                            'WfmRef-Mon': self.wfm.curveAtIndex(2),
                            'Wfm-Mon': self.wfm.curveAtIndex(3),
                            'Mon - Ref': self.wfm.curveAtIndex(4)}

        # Show
        self.show_wfm_sp = QCheckBox('SP')
        self.show_wfm_sp.setChecked(True)
        self.show_wfm_sp.setStyleSheet('color: red;')
        self.show_wfm_sp.stateChanged.connect(
            self._wfm_curves['Wfm-SP'].setVisible)
        self.show_wfm_rb = QCheckBox('RB')
        self.show_wfm_rb.setChecked(True)
        self.show_wfm_rb.setStyleSheet('color: blue;')
        self.show_wfm_rb.stateChanged.connect(
            self._wfm_curves['Wfm-RB'].setVisible)
        self.show_wfm_rm = QCheckBox('Ref-Mon')
        self.show_wfm_rm.setChecked(True)
        self.show_wfm_rm.setStyleSheet('color: green;')
        self.show_wfm_rm.stateChanged.connect(
            self._wfm_curves['WfmRef-Mon'].setVisible)
        self.show_wfm_mo = QCheckBox('Mon')
        self.show_wfm_mo.setChecked(True)
        self.show_wfm_mo.setStyleSheet('color: black;')
        self.show_wfm_mo.stateChanged.connect(
            self._wfm_curves['Wfm-Mon'].setVisible)
        self.show_wfm_diff = QCheckBox('Mon - Ref')
        self.show_wfm_diff.setChecked(True)
        self.show_wfm_diff.setStyleSheet('color: magenta;')
        self.show_wfm_diff.stateChanged.connect(
            self._wfm_curves['Mon - Ref'].setVisible)
        hbox_show = QHBoxLayout()
        hbox_show.setSpacing(9)
        hbox_show.addWidget(self.show_wfm_sp)
        hbox_show.addWidget(self.show_wfm_rb)
        hbox_show.addWidget(self.show_wfm_rm)
        hbox_show.addWidget(self.show_wfm_mo)
        hbox_show.addWidget(self.show_wfm_diff)

        # Add widgets
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self.wfm)
        layout.addWidget(self.wfm_nrpts)
        layout.addLayout(hbox_show)
        return layout

    def _set_wfm_nrpts_label(self):
        self.wfm_nrpts.setText(
            "Nrpts (SP|RB|Ref-Mon|Mon): {}|{}|{}|{}".format(
                self._wfm_nrpts_sp,
                self._wfm_nrpts_rb,
                self._wfm_nrpts_rm,
                self._wfm_nrpts_mo))

    def _update_wfm_diff(self):
        if self._wfm_nrpts_rm != self._wfm_nrpts_mo:
            self._wfm_curves['Mon - Ref'].receiveYWaveform(_np.array([]))
        else:
            self._wfm_curves['Mon - Ref'].receiveYWaveform(
                self._wfm_data_rm - self._wfm_data_mo)
        self._wfm_curves['Mon - Ref'].redrawCurve()

    def _wfm_update_rb(self, value):
        self._wfm_nrpts_rb = len(value)
        self._set_wfm_nrpts_label()

    def _wfm_update_sp(self, value):
        self._wfm_nrpts_sp = len(value)
        self._set_wfm_nrpts_label()

    def _wfm_update_rm(self, value):
        self._wfm_data_rm = value
        self._wfm_nrpts_rm = len(value)
        self._set_wfm_nrpts_label()
        self._update_wfm_diff()

    def _wfm_update_mo(self, value):
        self._wfm_data_mo = value
        self._wfm_nrpts_mo = len(value)
        self._set_wfm_nrpts_label()
        self._update_wfm_diff()

    def _getElementMetric(self):
        dipole = re.compile("(SI|BO|LI|TS|TB)-(Fam|\w{2,4}):PS-(B.*|Spect)$")
        quadrupole = re.compile("(SI|BO|TS|TB)-(Fam|\w{2,4}):PS-Q\w+")
        liquad = re.compile("LI-(Fam|\w{2,4}):PS-Q(?!(F|D)1)")
        sextupole = re.compile("(SI|BO|TS|TB)-(Fam|\w{2,4}):PS-S(?!lnd)\w+$")
        slow_corrector = re.compile(
            "(SI|BO|TS|TB)-(Fam|\w{2,4}):PS-(CH|CV)(-|\w)*")
        fast_corrector = re.compile(
            "(SI|BO|TS|TB)-(Fam|\w{2,4}):PS-(FCH|FCV)(-|\w)*")
        skew_quad = re.compile("(SI|BO|TS|TB)-(Fam|\w{2,4}):PS-QS")

        if dipole.match(self._psname):
            return "Energy"
        elif quadrupole.match(self._psname) or \
                skew_quad.match(self._psname) or \
                liquad.match(self._psname):
            return "KL"
        elif sextupole.match(self._psname):
            return "SL"
        elif slow_corrector.match(self._psname) or \
                fast_corrector.match(self._psname):
            return "Kick"
        else:
            return


class LIPSDetailWidget(PSDetailWidget):

    def _setup_ui(self):
        # Group boxes that compose the widget
        self.frmwr_box = QGroupBox("IOC && Net")
        self.frmwr_box.setObjectName("version")
        self.frmwr_box.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Maximum)
        self.pwrstate_box = QGroupBox("PwrState")
        self.pwrstate_box.setObjectName("power_state")
        self.interlock_box = QGroupBox("Interlock")
        self.interlock_box.setObjectName("interlock")
        self.params_box = QGroupBox('Params')
        self.params_box.setObjectName('params_box')
        self.current_box = QGroupBox("Current")
        self.current_box.setObjectName("current")
        if self._metric:
            self.metric_box = QGroupBox(self._metric)
            self.metric_box.setObjectName("metric")

        # Set group boxes layouts
        self.frmwr_box.setLayout(self._frmwrLayout())
        self.pwrstate_box.setLayout(self._powerStateLayout())
        self.interlock_box.setLayout(self._interlockLayout())
        self.params_box.setLayout(self._paramsLayout())
        self.current_box.setLayout(self._currentLayout())
        if self._metric:
            self.metric_box.setLayout(self._metricLayout())

        # Add group boxes to laytout
        self.layout = self._setWidgetLayout()

        # Set widget layout
        self.setLayout(self.layout)

    def _setWidgetLayout(self):
        controls = QGridLayout()
        controls.addWidget(self.frmwr_box, 0, 0, 1, 2)
        controls.addWidget(self.pwrstate_box, 1, 0)
        controls.addWidget(self.interlock_box, 1, 1)

        analogs = QVBoxLayout()
        analogs.addWidget(self.current_box, Qt.AlignCenter)

        if self._metric:
            analogs.addWidget(self.metric_box, Qt.AlignCenter)
            controls.addWidget(self.params_box, 2, 0, 1, 2)
        else:
            analogs.addWidget(self.params_box, Qt.AlignCenter)

        boxes_layout = QHBoxLayout()
        boxes_layout.addLayout(controls)
        boxes_layout.addLayout(analogs)
        boxes_layout.setStretch(0, 1)
        boxes_layout.setStretch(1, 1)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("<h2>" + self._psname + "</h2>"))
        layout.addLayout(boxes_layout)
        return layout

    def _frmwrLayout(self):
        self.version_label = QLabel('Version')
        self.version_label.setObjectName("version_label")
        self.version_label.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Maximum)
        self.version_cte = PyDMLabel(
            self, self._prefixed_psname + ":Version-Cte")
        self.version_cte.setObjectName("version_cte_label")
        self.version_cte.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Maximum)

        self.tstamp_boot_label = QLabel('IOC Boot')
        self.tstamp_boot_label.setObjectName("tstamp_label")
        self.tstamp_boot_label.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Maximum)
        self.tstamp_boot_cte = PyDMLabel(
            self, self._prefixed_psname + ":TimestampBoot-Cte")
        self.tstamp_boot_cte.setObjectName("tstamp_cte_label")
        self.tstamp_boot_cte.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Maximum)

        self.conn_label = QLabel('Net Status')
        self.conn_label.setObjectName("net_label")
        self.conn_label.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Maximum)
        self.conn_sts = PyDMLabel(
            self, self._prefixed_psname + ":Connected-Mon")
        self.conn_sts.setObjectName("net_cte_label")
        self.conn_sts.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Maximum)

        layout = QGridLayout()
        layout.addWidget(self.version_label, 0, 0, Qt.AlignHCenter)
        layout.addWidget(self.version_cte, 0, 1, Qt.AlignHCenter)
        layout.addWidget(self.tstamp_boot_label, 1, 0, Qt.AlignHCenter)
        layout.addWidget(self.tstamp_boot_cte, 1, 1, Qt.AlignHCenter)
        layout.addWidget(self.conn_label, 2, 0, Qt.AlignHCenter)
        layout.addWidget(self.conn_sts, 2, 1, Qt.AlignHCenter)
        return layout

    def _currentLayout(self):
        self.current_sp_label = QLabel("Setpoint")
        self.current_rb_label = QLabel("Readback")
        self.current_mon_label = QLabel("Mon")

        self.current_sp_widget = PyDMLinEditScrollbar(
            parent=self, channel=self._prefixed_psname + ":Current-SP")
        self.current_sp_widget.layout.setContentsMargins(0, 0, 0, 0)
        self.current_sp_widget.sp_scrollbar.setTracking(False)
        self.current_rb_val = PyDMLabel(
            parent=self, init_channel=self._prefixed_psname+":Current-RB")
        self.current_rb_val.showUnits = True
        self.current_rb_val.precFromPV = True
        self.current_mon_val = PyDMLabel(
            parent=self, init_channel=self._prefixed_psname+":Current-Mon")
        self.current_mon_val.showUnits = True
        self.current_mon_val.precFromPV = True

        layout = QGridLayout()
        layout.addWidget(self.current_sp_label, 0, 0, Qt.AlignRight)
        layout.addWidget(self.current_sp_widget, 0, 1)
        layout.addWidget(self.current_rb_label, 1, 0, Qt.AlignRight)
        layout.addWidget(self.current_rb_val, 1, 1)
        layout.addWidget(self.current_mon_label, 3, 0, Qt.AlignRight)
        layout.addWidget(self.current_mon_val, 3, 1)
        layout.setColumnStretch(2, 1)
        return layout

    def _metricLayout(self):
        metric_sp_ch = self._prefixed_psname+":"+self._metric+"-SP"
        metric_rb_ch = self._prefixed_psname+":"+self._metric+"-RB"
        metric_mon_ch = self._prefixed_psname+":"+self._metric+"-Mon"

        self.metric_sp_label = QLabel("Setpoint")
        self.metric_rb_label = QLabel("Readback")
        self.metric_mon_label = QLabel("Mon")

        self.metric_sp_widget = PyDMLinEditScrollbar(
            parent=self, channel=metric_sp_ch)
        self.metric_sp_widget.layout.setContentsMargins(0, 0, 0, 0)
        self.metric_sp_widget.sp_scrollbar.setTracking(False)
        self.metric_rb_val = PyDMLabel(
            parent=self, init_channel=metric_rb_ch)
        self.metric_rb_val.showUnits = True
        self.metric_rb_val.precFromPV = True
        self.metric_mon_val = PyDMLabel(
            parent=self, init_channel=metric_mon_ch)
        self.metric_mon_val.showUnits = True
        self.metric_mon_val.precFromPV = True

        layout = QGridLayout()
        layout.addWidget(self.metric_sp_label, 0, 0, Qt.AlignRight)
        layout.addWidget(self.metric_sp_widget, 0, 1)
        layout.addWidget(self.metric_rb_label, 1, 0, Qt.AlignRight)
        layout.addWidget(self.metric_rb_val, 1, 1)
        layout.addWidget(self.metric_mon_label, 3, 0, Qt.AlignRight)
        layout.addWidget(self.metric_mon_val, 3, 1)
        layout.setColumnStretch(3, 1)
        return layout

    def _interlockLayout(self):
        self.intlk_bt = QPushButton(qta.icon('fa5s.list-ul'), '', self)
        self.intlk_bt.setObjectName('intlk_bt')
        self.intlk_bt.setStyleSheet(
            '#intlk_bt{min-width:25px; max-width:25px; icon-size:20px;}')
        util.connect_window(self.intlk_bt, LIInterlockWindow, self,
                            **{'devname': self._psname})
        self.intlk_led = SiriusLedAlert(
            parent=self, init_channel=self._prefixed_psname+":StatusIntlk-Mon")

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.intlk_bt, 0, 0)
        layout.addWidget(QLabel('Intlk', self, alignment=Qt.AlignCenter), 0, 1)
        layout.addWidget(self.intlk_led, 0, 2)
        return layout

    def _paramsLayout(self):
        temp_label = QLabel('Temperature', self)
        self.temp_mon_label = PyDMLabel(
            self, self._prefixed_psname + ':Temperature-Mon')

        loadv_label = QLabel('Load Voltage', self)
        self.loadv_mon_label = PyDMLabel(
            self, self._prefixed_psname + ':LoadVoltage-Mon')

        busv_label = QLabel('Bus Voltage', self)
        self.busv_mon_label = PyDMLabel(
            self, self._prefixed_psname + ':BusVoltage-Mon')

        layout = QGridLayout()
        layout.addWidget(temp_label, 0, 0, Qt.AlignRight)
        layout.addWidget(self.temp_mon_label, 0, 1)
        layout.addWidget(loadv_label, 1, 0, Qt.AlignRight)
        layout.addWidget(self.loadv_mon_label, 1, 1)
        layout.addWidget(busv_label, 2, 0, Qt.AlignRight)
        layout.addWidget(self.busv_mon_label, 2, 1)
        return layout


class DCLinkDetailWidget(PSDetailWidget):

    def _setup_ui(self):
        # Group boxes that compose the widget
        self.frmwr_box = QGroupBox('Firmware && IOC')
        self.frmwr_box.setObjectName("Firmware")
        self.interlock_box = QGroupBox('Interlock')
        self.interlock_box.setObjectName('interlock')
        self.pwrstate_box = QGroupBox('PwrState')
        self.pwrstate_box.setObjectName('power_state')
        self.opmode_box = QGroupBox('OpMode')
        self.opmode_box.setObjectName('operation_mode')
        self.ctrlloop_box = QGroupBox('Control Loop')
        self.ctrlloop_box.setObjectName('ctrlloop_box')
        self.params_box = QGroupBox('Params')
        self.params_box.setObjectName('params_box')
        self.analog_box = QGroupBox(self._analog_varname)
        self.analog_box.setObjectName('current')
        self.aux_box = QGroupBox('Other Params')
        self.aux_box.setObjectName('aux_box')

        # Set group boxes layouts
        self.frmwr_box.setLayout(self._frmwrLayout())
        self.interlock_box.setLayout(self._interlockLayout())
        self.pwrstate_box.setLayout(self._powerStateLayout())
        self.opmode_box.setLayout(self._opModeLayout())
        self.ctrlloop_box.setLayout(self._ctrlLoopLayout())
        self.params_box.setLayout(self._paramsLayout())
        self.analog_box.setLayout(self._analogLayout())
        self.aux_box.setLayout(self._auxLayout())

        # Add group boxes to laytout
        self.layout = self._setWidgetLayout()

        # Set widget layout
        self.setLayout(self.layout)

    def _setWidgetLayout(self):
        controls = QGridLayout()
        controls.addWidget(self.frmwr_box, 0, 0, 1, 2)
        controls.addWidget(self.interlock_box, 1, 0)
        controls.addWidget(self.opmode_box, 1, 1)
        controls.addWidget(self.pwrstate_box, 2, 0)
        controls.addWidget(self.ctrlloop_box, 2, 1)
        controls.addWidget(self.params_box, 3, 0, 1, 2)

        analogs = QVBoxLayout()
        analogs.addWidget(self.analog_box)
        analogs.addWidget(self.aux_box)

        boxes_layout = QHBoxLayout()
        boxes_layout.addLayout(controls)
        boxes_layout.addLayout(analogs)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("<h2>" + self._psname + "</h2>"))
        layout.addLayout(boxes_layout)
        return layout

    def _analogLayout(self):
        raise NotImplementedError

    def _auxLayout(self):
        raise NotImplementedError

    def _opModeLayout(self):
        self.opmode_rb = PyDMLabel(
            self, self._prefixed_psname + ":OpMode-Sts")
        self.opmode_rb.setObjectName("opmode1_rb_label")
        self.ctrlmode_led = SiriusLedAlert(
            self, self._prefixed_psname + ":CtrlMode-Mon")
        self.ctrlmode_label = PyDMLabel(
            self, self._prefixed_psname + ":CtrlMode-Mon")
        self.ctrlmode_label.setObjectName("ctrlmode1_label")

        ctrlmode_layout = QHBoxLayout()
        ctrlmode_layout.addWidget(self.ctrlmode_led)
        ctrlmode_layout.addWidget(self.ctrlmode_label)

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.opmode_rb, 0, 0, Qt.AlignHCenter)
        layout.addLayout(ctrlmode_layout, 1, 0, Qt.AlignHCenter)
        return layout


class FBPDCLinkDetailWidget(DCLinkDetailWidget):

    def __init__(self, psname, parent=None):
        self._analog_varname = 'Current'
        super().__init__(psname, parent)

    def _analogLayout(self):
        self.current_sp_label = QLabel("Setpoint")
        self.current_rb_label = QLabel("Readback")
        self.current_ref_label = QLabel("Ref Mon")
        self.current_mon_label = QLabel("Mon")

        self.current_sp_widget = PyDMLinEditScrollbar(
            parent=self, channel=self._prefixed_psname + ":Voltage-SP")
        self.current_sp_widget.layout.setContentsMargins(0, 0, 0, 0)
        self.current_sp_widget.sp_lineedit.showUnits = False
        self.current_sp_widget.sp_scrollbar.setTracking(False)
        self.current_rb_val = PyDMLabel(
            parent=self, init_channel=self._prefixed_psname+":Voltage-RB")
        self.current_rb_val.precFromPV = True
        self.current_ref_val = PyDMLabel(
            parent=self, init_channel=self._prefixed_psname+":VoltageRef-Mon")
        self.current_ref_val.precFromPV = True
        self.current_mon_val = PyDMLabel(
            parent=self, init_channel=self._prefixed_psname+":Voltage-Mon")
        self.current_mon_val.precFromPV = True

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self.current_sp_label, 0, 0, Qt.AlignRight)
        layout.addWidget(self.current_sp_widget, 0, 1)
        layout.addWidget(self.current_rb_label, 1, 0, Qt.AlignRight)
        layout.addWidget(self.current_rb_val, 1, 1)
        layout.addWidget(self.current_ref_label, 2, 0, Qt.AlignRight)
        layout.addWidget(self.current_ref_val, 2, 1)
        layout.addWidget(self.current_mon_label, 3, 0, Qt.AlignRight)
        layout.addWidget(self.current_mon_val, 3, 1)
        layout.setColumnStretch(2, 1)
        return layout

    def _auxLayout(self):
        self._out_1_mon = PyDMLabel(
            self, self._prefixed_psname + ':Voltage1-Mon')
        self._out_2_mon = PyDMLabel(
            self, self._prefixed_psname + ':Voltage2-Mon')
        self._out_3_mon = PyDMLabel(
            self, self._prefixed_psname + ':Voltage3-Mon')
        self._out_dig_mon = PyDMLabel(
            self, self._prefixed_psname + ':VoltageDig-Mon')
        self._mod_status_mon = PyDMLabel(
            self, self._prefixed_psname + ':ModulesStatus-Mon')

        layout = QFormLayout()
        layout.addRow('Voltage 1', self._out_1_mon)
        layout.addRow('Voltage 2', self._out_2_mon)
        layout.addRow('Voltage 3', self._out_3_mon)
        layout.addRow('Voltage dig', self._out_dig_mon)
        layout.addRow('Module Status', self._mod_status_mon)
        return layout


class FACDCLinkDetailWidget(DCLinkDetailWidget):

    def __init__(self, psname, parent=None):
        self._analog_varname = 'Capacitor Bank Voltage'
        super().__init__(psname, parent)

    def _analogLayout(self):
        self.cap_bank_sp_label = QLabel("Setpoint")
        self.cap_bank_rb_label = QLabel("Readback")
        self.cap_bank_ref_label = QLabel("Ref Mon")
        self.cap_bank_mon_label = QLabel("Mon")

        self.cap_bank_sp_widget = PyDMLinEditScrollbar(
            self._prefixed_psname + ":CapacitorBankVoltage-SP", self)
        self.cap_bank_sp_widget.sp_lineedit.showUnits = False
        self.cap_bank_sp_widget.sp_scrollbar.setTracking(False)
        self.cap_bank_rb_val = PyDMLabel(
            self,
            self._prefixed_psname + ":CapacitorBankVoltage-RB")
        self.cap_bank_rb_val.precFromPV = True
        self.cap_bank_ref_val = PyDMLabel(
            self,
            self._prefixed_psname + ":CapacitorBankVoltageRef-Mon")
        self.cap_bank_ref_val.precFromPV = True
        self.cap_bank_mon_val = PyDMLabel(
            self,
            self._prefixed_psname + ":CapacitorBankVoltage-Mon")
        self.cap_bank_mon_val.precFromPV = True

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)
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
        self.rectifier_voltage_mon = PyDMLabel(
            self, self._prefixed_psname + ':RectifierVoltage-Mon')
        self.rectifier_current_mon = PyDMLabel(
            self, self._prefixed_psname + ':RectifierCurrent-Mon')
        self.heatsink_temperature = PyDMLabel(
            self, self._prefixed_psname + ':HeatSinkTemperature-Mon')
        self.inductors_temperature = PyDMLabel(
            self,
            self._prefixed_psname + ':InductorsTemperature-Mon')
        self.duty_cycle = PyDMLabel(
            self, self._prefixed_psname + ':PWMDutyCycle-Mon')

        layout = QFormLayout()
        layout.addRow('Rectifier Voltage', self.rectifier_voltage_mon)
        layout.addRow('Rectifier Current', self.rectifier_current_mon)
        layout.addRow('Heatsink Temperatue', self.heatsink_temperature)
        layout.addRow('Inductors Temperature', self.inductors_temperature)
        layout.addRow('PWM Duty Cycle', self.duty_cycle)
        return layout
