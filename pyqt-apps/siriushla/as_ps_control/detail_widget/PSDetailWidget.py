"""PS Detail Widget."""

import re
from datetime import datetime as _datetime
import numpy as _np

from qtpy.QtCore import Qt, QRegExp
from qtpy.QtGui import QRegExpValidator
from qtpy.QtWidgets import QWidget, QGroupBox, QPushButton, QLabel, \
    QGridLayout, QVBoxLayout, QHBoxLayout, QFormLayout, QTabWidget, \
    QSizePolicy as QSzPlcy, QCheckBox, QHeaderView, QAbstractItemView, \
    QScrollArea, QFrame
from qtpy.QtGui import QColor

import qtawesome as qta

from pydm.widgets import PyDMLabel, PyDMEnumComboBox, PyDMPushButton, \
    PyDMLineEdit, PyDMWaveformPlot
from pydm.widgets.display_format import parse_value_for_display

from siriuspy.util import get_strength_label
from siriuspy.namesys import SiriusPVName
from siriuspy.envars import VACA_PREFIX
from siriuspy.search import PSSearch
from siriuspy.pwrsupply.csdev import get_ps_propty_database, get_ps_modules, \
    DEF_WFMSIZE_FBP, DEF_WFMSIZE_OTHERS, PS_LI_INTLK_THRS as _PS_LI_INTLK, \
    ETypes as _PSet
from siriuspy.devices import PowerSupply

from ... import util
from ...widgets import PyDMStateButton, PyDMLinEditScrollbar, SiriusTimePlot, \
    SiriusConnectionSignal, SiriusLedState, SiriusLedAlert, PyDMLed, \
    PyDMLedMultiChannel, SiriusDialog, SiriusWaveformTable, SiriusSpinbox
from .InterlockWindow import InterlockWindow, LIInterlockWindow
from .custom_widgets import LISpectIntlkLed


class PSDetailWidget(QWidget):
    """Widget with control interface for a given magnet."""

    StyleSheet = """
        #opmode_sp_cbox{
            min-width: 7em;
            max-width: 7em;
        }
        #opmode_rb_label{
            min-width: 7em;
            max-width: 7em;
            qproperty-alignment: AlignCenter;
        }
        #ctrlloop_label,
        #ctrlmode_label {
            min-width: 4em;
            max-width: 4em;
            qproperty-alignment: AlignCenter;
        }
        #pwrstate_label {
            min-width: 2em;
            max-width: 2em;
        }
        #current > PyDMLabel,
        #metric > PyDMLabel {
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
    """

    AuxDev2ModDict = {
        'BO-Fam:PS-B-1': {'A': '1', 'B': '2'},
        'BO-Fam:PS-B-1a': {'A': '3', 'B': '4'},
        'BO-Fam:PS-B-1b': {'A': '5', 'B': '6'},
        'BO-Fam:PS-B-1c': {'A': '7', 'B': '8'},
        'BO-Fam:PS-B-2': {'A': '1', 'B': '2'},
        'BO-Fam:PS-B-2a': {'A': '3', 'B': '4'},
        'BO-Fam:PS-B-2b': {'A': '5', 'B': '6'},
        'BO-Fam:PS-B-2c': {'A': '7', 'B': '8'},
    }

    BasicParams = [
        'Version-Cte', 'Properties-Cte',
        'Reset-Cmd', 'Abort-Cmd', 'WfmUpdate-Cmd',
        'TimestampBoot-Cte', 'TimestampUpdate-Mon',
        'PwrState-Sel', 'PwrState-Sts',
        'OpMode-Sel', 'OpMode-Sts', 'CtrlMode-Mon',
        'CtrlLoop-Sel', 'CtrlLoop-Sts',
        'Current-SP', 'Current-RB', 'CurrentRef-Mon', 'Current-Mon',
        'CycleEnbl-Mon', 'CycleIndex-Mon',
        'CycleType-Sel', 'CycleType-Sts',
        'CycleNrCycles-SP', 'CycleNrCycles-RB',
        'CycleFreq-SP', 'CycleFreq-RB',
        'CycleAmpl-SP', 'CycleAmpl-RB',
        'CycleOffset-SP', 'CycleOffset-RB',
        'CycleAuxParam-SP', 'CycleAuxParam-RB',
        'WfmIndex-Mon', 'WfmSyncPulseCount-Mon',
        'WfmUpdateAuto-Sel', 'WfmUpdateAuto-Sts',
        'SOFBMode-Sel', 'SOFBMode-Sts',
        'PRUCtrlQueueSize-Mon', 'SyncPulse-Cmd',
        'Wfm-SP', 'Wfm-RB', 'WfmRef-Mon', 'Wfm-Mon',
        'Voltage-SP', 'Voltage-RB', 'VoltageRef-Mon', 'Voltage-Mon',
        'CapacitorBankVoltage-SP', 'CapacitorBankVoltage-RB',
        'CapacitorBankVoltageRef-Mon', 'CapacitorBankVoltage-Mon',
        'ScopeSrcAddr-SP', 'ScopeSrcAddr-RB',
        'ScopeFreq-SP', 'ScopeFreq-RB',
        'ScopeDuration-SP', 'ScopeDuration-RB',
    ]

    def __init__(self, psname, parent=None):
        """Class constructor."""
        super(PSDetailWidget, self).__init__(parent)
        self._prefix = VACA_PREFIX
        self._psname = SiriusPVName(psname)
        self._psmodel = PSSearch.conv_psname_2_psmodel(psname)
        self._pstype = PSSearch.conv_psname_2_pstype(self._psname)
        try:
            self._metric = get_strength_label(
                PSSearch.conv_psname_2_magfunc(self._psname))
        except ValueError:
            self._metric = ''

        try:
            self._db = get_ps_propty_database(self._psmodel, self._pstype)
            self._mods = get_ps_modules(psmodel=self._psmodel)
        except ValueError:
            self._db = dict()
            self._mods = set()
        if self._mods:
            self._mod2db = {
                mod: [
                    pv for pv in self._db
                    if 'Mod'+mod in pv and 'IIB' in pv and
                    'Intlk' not in pv and 'Alarm' not in pv
                ] for mod in self._mods
            }
        else:
            self._mod2db = {
                'main': [
                    pv for pv in self._db if 'IIB' in pv and
                    'Intlk' not in pv and 'Alarm' not in pv
                ]
            }
        self._auxmeasures = [
            pv for pv in self._db if pv not in self.BasicParams and
            'Intlk' not in pv and 'Alarm' not in pv and
            (self._metric not in pv if self._metric else True) and
            'IIB' not in pv and 'Param' not in pv
        ]
        self._params = [
            prm for prm in self._db if 'Param' in prm and '-Cte' in prm]

        self._auxdev = ['', ]
        self._auxdev2mod = self.AuxDev2ModDict
        if self._psname in self._auxdev2mod:
            self._auxdev = ['', 'a', 'b', 'c']

        self._prefixed_psname = self._psname.substitute(prefix=self._prefix)

        self.setObjectName(parent.objectName())

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
        self.wfmparams_box = QGroupBox('Wfm Params')
        self.wfmparams_box.setObjectName('wfmparams_box')
        if self._psmodel == 'FBP':
            self.sofbparams_box = QGroupBox('SOFB Params')
            self.sofbparams_box.setObjectName('sofbparams_box')
        self.genparams_box = QGroupBox('General Params')
        self.genparams_box.setObjectName('genparams_box')
        self.current_box = QGroupBox("Current")
        self.current_box.setObjectName("current")
        self.siggen_tab = QWidget()
        self.siggen_tab.setObjectName('cycle_tab')
        self.wfm_tab = QWidget()
        self.wfm_tab.setObjectName("wfm_tab")
        self.scope_tab = QWidget()
        self.scope_tab.setObjectName('scope_tab')
        self.curve_tabs = QTabWidget()
        self.curve_tabs.setObjectName('curve_tabs')
        self.curve_tabs.setStyleSheet("""
            #curve_tabs::pane {
                border-left: 2px solid gray;
                border-bottom: 2px solid gray;
                border-right: 2px solid gray;
        }""")
        self.curve_tabs.addTab(self.siggen_tab, 'SigGen')
        self.curve_tabs.addTab(self.wfm_tab, 'Wfm')
        self.curve_tabs.addTab(self.scope_tab, 'Scope')
        if self._psname.sec == 'BO':
            self.curve_tabs.setCurrentIndex(1)
        if self._metric:
            self.metric_box = QGroupBox(self._metric)
            self.metric_box.setObjectName("metric")

        # Set group boxes layouts
        self.frmwr_box.setLayout(self._frmwrLayout())
        self.interlock_box.setLayout(self._interlockLayout())
        self.pwrstate_box.setLayout(self._powerStateLayout())
        self.opmode_box.setLayout(self._opModeLayout())
        self.ctrlloop_box.setLayout(self._ctrlLoopLayout())
        self.wfmparams_box.setLayout(self._wfmParamsLayout())
        if self._psmodel == 'FBP':
            self.sofbparams_box.setLayout(self._sofbParamsLayout())
        self.genparams_box.setLayout(self._genParamsLayout())
        self.current_box.setLayout(self._currentLayout())
        self.siggen_tab.setLayout(self._siggenLayout())
        self.wfm_tab.setLayout(self._wfmLayout())
        self.scope_tab.setLayout(self._scopeLayout())
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
        if self._psmodel == 'FBP':
            controls.addWidget(self.genparams_box, 4, 0)
            controls.addWidget(self.sofbparams_box, 4, 1)
        else:
            controls.addWidget(self.genparams_box, 4, 0, 1, 2)
        controls.addWidget(self.wfmparams_box, 5, 0, 1, 2)

        analogs = QVBoxLayout()
        analogs.addWidget(self.current_box, Qt.AlignCenter)
        if self._metric:
            analogs.addWidget(self.metric_box, Qt.AlignCenter)
        analogs.addWidget(self.curve_tabs, Qt.AlignCenter)

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

    def _interlockLayout(self):
        # Widgets
        self.soft_label = QLabel('Soft', self, alignment=Qt.AlignCenter)
        self.soft_intlk_bt = QPushButton(qta.icon('fa5s.list-ul'), '', self)
        self.soft_intlk_bt.setObjectName('soft_intlk_bt')
        self.soft_intlk_bt.setStyleSheet(
            '#soft_intlk_bt{min-width:25px; max-width:25px; icon-size:20px;}')
        util.connect_window(
            self.soft_intlk_bt, InterlockWindow, self,
            devname=self._psname, interlock='IntlkSoft',
            auxdev=self._auxdev, auxdev2mod=self._auxdev2mod)
        self.soft_intlk_led = SiriusLedAlert(
            parent=self, init_channel=self._prefixed_psname + ":IntlkSoft-Mon")

        self.hard_label = QLabel('Hard', self, alignment=Qt.AlignCenter)
        self.hard_intlk_bt = QPushButton(qta.icon('fa5s.list-ul'), '', self)
        self.hard_intlk_bt.setObjectName('hard_intlk_bt')
        self.hard_intlk_bt.setStyleSheet(
            '#hard_intlk_bt{min-width:25px; max-width:25px; icon-size:20px;}')
        util.connect_window(
            self.hard_intlk_bt, InterlockWindow, self,
            devname=self._psname, interlock='IntlkHard',
            auxdev=self._auxdev, auxdev2mod=self._auxdev2mod)
        self.hard_intlk_led = SiriusLedAlert(
            parent=self, init_channel=self._prefixed_psname + ":IntlkHard-Mon")

        iib_intlks = [k.replace('Labels-Cte', '') for k in self._db
                      if re.match('IntlkIIB.*Labels-Cte', k)]
        if iib_intlks:
            self.iib_label = QLabel('IIB', self, alignment=Qt.AlignCenter)
            self.iib_intlk_bt = QPushButton(
                qta.icon('fa5s.list-ul'), '', self)
            self.iib_intlk_bt.setObjectName('iib_intlk_bt')
            self.iib_intlk_bt.setStyleSheet(
                "#iib_intlk_bt{min-width:25px;max-width:25px;icon-size:20px;}")
            util.connect_window(
                self.iib_intlk_bt, InterlockWindow, self,
                devname=self._psname, interlock=iib_intlks,
                auxdev=self._auxdev, auxdev2mod=self._auxdev2mod)

            chs2vals = dict()
            for aux in self._auxdev:
                chs2vals.update({self._prefixed_psname+aux+":"+intlk+"-Mon": 0
                                 for intlk in iib_intlks})
            self.iib_intlk_led = PyDMLedMultiChannel(self, chs2vals)

        iib_alarms = [k.replace('Labels-Cte', '') for k in self._db
                      if re.match('AlarmsIIB.*Labels-Cte', k)]
        if iib_alarms:
            self.alarm_label = QLabel(
                'Alarms', self, alignment=Qt.AlignCenter)
            self.alarm_bt = QPushButton(qta.icon('fa5s.list-ul'), '', self)
            self.alarm_bt.setObjectName('alarm_bt')
            self.alarm_bt.setStyleSheet(
                '#alarm_bt{min-width:25px;max-width:25px;icon-size:20px;}')
            util.connect_window(
                self.alarm_bt, InterlockWindow, self,
                devname=self._psname, interlock=iib_alarms,
                auxdev=self._auxdev, auxdev2mod=self._auxdev2mod)

            chs2vals = dict()
            for aux in self._auxdev:
                chs2vals.update({self._prefixed_psname+aux+":"+alarm+"-Mon": 0
                                 for alarm in iib_alarms})
            self.alarm_led = PyDMLedMultiChannel(self, chs2vals)

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
        layout.addWidget(self.soft_label, 0, 1)
        layout.addWidget(self.soft_intlk_led, 0, 2)
        layout.addWidget(self.hard_intlk_bt, 1, 0)
        layout.addWidget(self.hard_label, 1, 1)
        layout.addWidget(self.hard_intlk_led, 1, 2)
        if iib_intlks:
            layout.addWidget(self.iib_intlk_bt, 2, 0)
            layout.addWidget(self.iib_label, 2, 1)
            layout.addWidget(self.iib_intlk_led, 2, 2)
        if iib_alarms:
            layout.addWidget(self.alarm_bt, 3, 0)
            layout.addWidget(self.alarm_label, 3, 1)
            layout.addWidget(self.alarm_led, 3, 2)
        layout.addWidget(self.reset_bt, 4, 2)
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
        self.opmode_sp.setObjectName("opmode_sp_cbox")
        self.opmode_rb = PyDMLabel(
            self, self._prefixed_psname + ":OpMode-Sts")
        self.opmode_rb.setObjectName("opmode_rb_label")
        self.ctrlmode_led = SiriusLedAlert(
            self, self._prefixed_psname + ":CtrlMode-Mon")
        self.ctrlmode_label = PyDMLabel(
            self, self._prefixed_psname + ":CtrlMode-Mon")
        self.ctrlmode_label.setObjectName("ctrlmode_label")

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

        # Params
        self.cycle_enbl_label = QLabel('Enabled', self)
        self.cycle_enbl_mon_led = SiriusLedState(self, enbl_mon_ca)

        self.cycle_type_label = QLabel('Type', self)
        self.cycle_type_sp_cb = PyDMEnumComboBox(self, type_sp_ca)
        self.cycle_type_rb_label = PyDMLabel(self, type_rb_ca)

        self.cycle_nr_label = QLabel('Nr. Cycles', self)
        self.cycle_nr_sp_sb = PyDMLineEdit(self, nrcycles_sp_ca)
        self.cycle_nr_rb_label = PyDMLabel(self, nrcycles_rb_ca)

        self.cycle_index_label = QLabel('Index', self)
        self.cycle_index_mon_label = PyDMLabel(self, index_ca)

        self.cycle_freq_label = QLabel('Frequency', self)
        self.cycle_freq_sp_sb = PyDMLineEdit(self, freq_sp_ca)
        self.cycle_freq_rb_label = PyDMLabel(self, freq_rb_ca)

        self.cycle_ampl_label = QLabel('Amplitude', self)
        self.cycle_ampl_sp_sb = PyDMLineEdit(self, ampl_sp_ca)
        self.cycle_ampl_rb_label = PyDMLabel(self, ampl_rb_ca)

        self.cycle_offset_label = QLabel('Offset', self)
        self.cycle_offset_sp_sb = PyDMLineEdit(self, offset_sp_ca)
        self.cycle_offset_rb_label = PyDMLabel(self, offset_rb_ca)

        self.cycle_auxparam_label = QLabel('AuxParams', self)
        self.cycle_auxparam_sp_le = PyDMLineEdit(self, auxparam_sp_ca)
        self.cycle_auxparam_rb_label = PyDMLabel(self, auxparam_rb_ca)

        self.cycle_auxparam_helpbut = QPushButton(
            qta.icon('mdi.help'), '', self)
        self.cycle_auxparam_helpbut.setToolTip(
            'Show AuxParam help message')
        self.cycle_auxparam_helpbut.setObjectName('help_bt')
        self.cycle_auxparam_helpbut.setStyleSheet(
            '#help_bt{min-width:20px;max-width:20px;icon-size:16px;}')
        self.cycle_auxparam_helpwid = QWidget()
        self.cycle_auxparam_helpwid.setObjectName(self.parent().objectName())
        self.cycle_auxparam_helpwid.setWindowTitle('AuxParam Help Message')
        self.cycle_auxparam_helpbut.clicked.connect(
            self.cycle_auxparam_helpwid.show)
        text = getattr(PowerSupply, 'cycle_aux_param').__doc__
        self.cycle_auxparam_helplab = QLabel(text, self)
        lay_help = QHBoxLayout(self.cycle_auxparam_helpwid)
        lay_help.addWidget(self.cycle_auxparam_helplab)

        parms = QWidget()
        lay_parms = QGridLayout(parms)
        lay_parms.setAlignment(Qt.AlignTop)
        lay_parms.addWidget(self.cycle_enbl_label, 0, 0, Qt.AlignRight)
        lay_parms.addWidget(self.cycle_enbl_mon_led, 0, 1, Qt.AlignCenter)
        lay_parms.addWidget(self.cycle_type_label, 1, 0, Qt.AlignRight)
        lay_parms.addWidget(self.cycle_type_sp_cb, 1, 1)
        lay_parms.addWidget(self.cycle_type_rb_label, 1, 2, 1, 2)
        lay_parms.addWidget(self.cycle_nr_label, 2, 0, Qt.AlignRight)
        lay_parms.addWidget(self.cycle_nr_sp_sb, 2, 1)
        lay_parms.addWidget(self.cycle_nr_rb_label, 2, 2, 1, 2)
        lay_parms.addWidget(self.cycle_index_label, 3, 0, Qt.AlignRight)
        lay_parms.addWidget(self.cycle_index_mon_label, 3, 2, 1, 2)
        lay_parms.addWidget(self.cycle_freq_label, 4, 0, Qt.AlignRight)
        lay_parms.addWidget(self.cycle_freq_sp_sb, 4, 1)
        lay_parms.addWidget(self.cycle_freq_rb_label, 4, 2, 1, 2)
        lay_parms.addWidget(self.cycle_ampl_label, 5, 0, Qt.AlignRight)
        lay_parms.addWidget(self.cycle_ampl_sp_sb, 5, 1)
        lay_parms.addWidget(self.cycle_ampl_rb_label, 5, 2, 1, 2)
        lay_parms.addWidget(self.cycle_offset_label, 6, 0, Qt.AlignRight)
        lay_parms.addWidget(self.cycle_offset_sp_sb, 6, 1)
        lay_parms.addWidget(self.cycle_offset_rb_label, 6, 2, 1, 2)
        lay_parms.addWidget(self.cycle_auxparam_label, 7, 0, Qt.AlignRight)
        lay_parms.addWidget(self.cycle_auxparam_sp_le, 7, 1)
        lay_parms.addWidget(self.cycle_auxparam_rb_label, 7, 2)
        lay_parms.addWidget(self.cycle_auxparam_helpbut, 7, 3)

        # Default Curve
        self._siggen = PSSearch.conv_psname_2_siggenconf(self._psname)
        self._siggen_nrpts = DEF_WFMSIZE_FBP if self._psmodel == 'FBP' \
            else DEF_WFMSIZE_OTHERS
        self._siggen_w = self._siggen.get_waveform(self._siggen_nrpts)

        self.curve_siggen = PyDMWaveformPlot()
        self.curve_siggen.setObjectName('graph')
        self.curve_siggen.setStyleSheet(
            '#graph{max-height:15em; max-width:16.5em;}')
        self.curve_siggen.setLabels(left='Current [A]', bottom='T [s]')
        self.curve_siggen.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Maximum)
        self.curve_siggen.autoRangeX = True
        self.curve_siggen.autoRangeY = True
        self.curve_siggen.plotItem.showButtons()
        self.curve_siggen.setBackgroundColor(QColor(255, 255, 255))
        self.curve_siggen.addChannel(
            y_channel='SigGen', x_channel='T [s]',
            color='black', lineWidth=2)
        self.curve_siggen.curve = self.curve_siggen.curveAtIndex(0)
        self.curve_siggen.curve.receiveXWaveform(_np.array(self._siggen_w[1]))
        self.curve_siggen.curve.receiveYWaveform(_np.array(self._siggen_w[0]))
        self.curve_siggen.curve.redrawCurve()

        defcurve = QWidget()
        lay_defcurve = QGridLayout(defcurve)
        lay_defcurve.addWidget(self.curve_siggen)

        # Tab
        self.tab_siggen = QTabWidget(self)
        self.tab_siggen.addTab(parms, 'Params')
        self.tab_siggen.addTab(defcurve, 'Default Curve')

        layout = QGridLayout()
        layout.setContentsMargins(0, 6, 0, 0)
        layout.addWidget(self.tab_siggen, 0, 0)
        return layout

    def _wfmParamsLayout(self):
        wfm_index_ca = self._prefixed_psname + ':WfmIndex-Mon'
        wfm_count_ca = self._prefixed_psname + ':WfmSyncPulseCount-Mon'
        wfm_updateauto_ca = self._prefixed_psname + ':WfmUpdateAuto-Sts'
        wfm_updateauto_sel = self._prefixed_psname + ':WfmUpdateAuto-Sel'

        wfm_index_label = QLabel('Wfm Index', self)
        wfm_index_rb_label = PyDMLabel(self, wfm_index_ca)

        wfm_count_label = QLabel('Wfm Pulse Count', self)
        wfm_count_rb_label = PyDMLabel(self, wfm_count_ca)

        wfm_updateauto_label = QLabel('Wfm UpdateAuto', self)
        wfm_updateauto_sts_led = SiriusLedState(self, wfm_updateauto_ca)
        wfm_updateauto_btn = PyDMStateButton(self, wfm_updateauto_sel)

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setColumnStretch(3, 1)
        layout.addWidget(wfm_index_label, 0, 0, Qt.AlignRight)
        layout.addWidget(wfm_index_rb_label, 0, 1)
        layout.addWidget(wfm_count_label, 1, 0, Qt.AlignRight)
        layout.addWidget(wfm_count_rb_label, 1, 1)
        layout.addWidget(wfm_updateauto_label, 2, 0, Qt.AlignRight)
        layout.addWidget(wfm_updateauto_btn, 2, 1, Qt.AlignHCenter)
        layout.addWidget(wfm_updateauto_sts_led, 2, 2)
        return layout

    def _sofbParamsLayout(self):
        sofb_mode_ca = self._prefixed_psname + ':SOFBMode-Sts'
        sofb_mode_sel = self._prefixed_psname + ':SOFBMode-Sel'

        sofb_mode_label = QLabel('SOFB Mode', self)
        sofb_mode_btn = PyDMStateButton(self, sofb_mode_sel)
        sofb_mode_sts_led = SiriusLedState(self, sofb_mode_ca)

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setColumnStretch(3, 1)
        layout.addWidget(sofb_mode_label, 0, 0, Qt.AlignRight)
        layout.addWidget(sofb_mode_btn, 0, 1, Qt.AlignHCenter)
        layout.addWidget(sofb_mode_sts_led, 0, 2)
        return layout

    def _genParamsLayout(self):
        queue_size_ca = self._prefixed_psname + ':PRUCtrlQueueSize-Mon'
        queue_size_label = QLabel('IOC Queue Size', self)
        queue_size_rb_label = PyDMLabel(self, queue_size_ca)

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setColumnStretch(3, 1)
        layout.addWidget(queue_size_label, 0, 0, Qt.AlignRight)
        layout.addWidget(queue_size_rb_label, 0, 1)

        if 'DCLink' not in self._prefixed_psname:
            syncpulse_cmd_ca = self._prefixed_psname + ':SyncPulse-Cmd'
            syncpulse_cmd_lb = QLabel('Sync Pulse Cmd', self)
            syncpulse_cmd_btn = PyDMPushButton(
                parent=self, icon=qta.icon('fa5s.step-forward'), pressValue=1,
                init_channel=syncpulse_cmd_ca)
            syncpulse_cmd_btn.setObjectName('syncpulse')
            syncpulse_cmd_btn.setStyleSheet(
                '#syncpulse{min-width:25px; max-width:32px; icon-size:20px;}')

            layout.addWidget(syncpulse_cmd_lb, 1, 0, Qt.AlignRight)
            layout.addWidget(syncpulse_cmd_btn, 1, 1)

            pbaux = QPushButton(
                qta.icon('mdi.open-in-new'), 'Aux. Measures', self)
            util.connect_window(
                pbaux, PSAuxMeasWidget, self, psname=self._psname,
                auxmeas=self._auxmeasures, mod2dbase=self._mod2db,
                auxdev=self._auxdev, auxdev2mod=self._auxdev2mod)
            layout.addWidget(pbaux, 2, 0, 1, 2)

            pbprm = QPushButton(qta.icon('mdi.open-in-new'),
                                'Parameters', self)
            util.connect_window(
                pbprm, PSParamsWidget, self, psname=self._psname,
                params=self._params)
            layout.addWidget(pbprm, 3, 0, 1, 2)

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
        self.wfm.plotItem.showButtons()
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
        self._wfm_curves = {'Wfm-SP': self.wfm.curveAtIndex(0),
                            'Wfm-RB': self.wfm.curveAtIndex(1),
                            'WfmRef-Mon': self.wfm.curveAtIndex(2),
                            'Wfm-Mon': self.wfm.curveAtIndex(3)}

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
        monlabel = 'Mon' + (' (Error)' if self._psname.sec == 'BO' else '')
        self.show_wfm_mo = QCheckBox(monlabel)
        self.show_wfm_mo.setChecked(True)
        self.show_wfm_mo.setStyleSheet('color: black;')
        self.show_wfm_mo.stateChanged.connect(
            self._wfm_curves['Wfm-Mon'].setVisible)
        hbox_show = QHBoxLayout()
        hbox_show.setSpacing(9)
        hbox_show.addWidget(self.show_wfm_sp)
        hbox_show.addWidget(self.show_wfm_rb)
        hbox_show.addWidget(self.show_wfm_rm)
        hbox_show.addWidget(self.show_wfm_mo)

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

    def _wfm_update_mo(self, value):
        self._wfm_data_mo = value
        self._wfm_nrpts_mo = len(value)
        self._set_wfm_nrpts_label()

    def _scopeLayout(self):
        src_sp = self._prefixed_psname + ':ScopeSrcAddr-SP'
        src_rb = self._prefixed_psname + ':ScopeSrcAddr-RB'
        freq_sp = self._prefixed_psname + ':ScopeFreq-SP'
        freq_rb = self._prefixed_psname + ':ScopeFreq-RB'
        dur_sp = self._prefixed_psname + ':ScopeDuration-SP'
        dur_rb = self._prefixed_psname + ':ScopeDuration-RB'

        self.scope_src_label = QLabel('Source', self)
        self.scope_src_sp_sb = CustomSpinBox(self, src_sp)
        self.scope_src_sp_sb.showStepExponent = False
        self.scope_src_rb_lb = PyDMLabel(self, src_rb)
        self.scope_src_rb_lb.displayFormat = PyDMLabel.DisplayFormat.Hex

        self.scope_freq_label = QLabel('Frequency', self)
        self.scope_freq_sp_sb = SiriusSpinbox(self, freq_sp)
        self.scope_freq_sp_sb.showStepExponent = False
        self.scope_freq_rb_label = PyDMLabel(self, freq_rb)
        self.scope_freq_rb_label.showUnits = True

        self.scope_dur_label = QLabel('Duration', self)
        self.scope_dur_sp_sb = SiriusSpinbox(self, dur_sp)
        self.scope_dur_sp_sb.showStepExponent = False
        self.scope_dur_rb_label = PyDMLabel(self, dur_rb)
        self.scope_dur_rb_label.showUnits = True

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(0, 6, 0, 0)
        layout.addWidget(self.scope_src_label, 0, 0, Qt.AlignRight)
        layout.addWidget(self.scope_src_sp_sb, 0, 1)
        layout.addWidget(self.scope_src_rb_lb, 0, 2)
        layout.addWidget(self.scope_freq_label, 1, 0, Qt.AlignRight)
        layout.addWidget(self.scope_freq_sp_sb, 1, 1)
        layout.addWidget(self.scope_freq_rb_label, 1, 2)
        layout.addWidget(self.scope_dur_label, 2, 0, Qt.AlignRight)
        layout.addWidget(self.scope_dur_sp_sb, 2, 1)
        layout.addWidget(self.scope_dur_rb_label, 2, 2)
        return layout


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
        self.tstamp_boot_cte_ch = SiriusConnectionSignal(
            self._prefixed_psname + ":TimestampBoot-Cte")
        self.tstamp_boot_cte_ch.new_value_signal[float].connect(
            self._tstamp_boot_cte_met)

        self.tstamp_update_label = QLabel('IOC Update')
        self.tstamp_update_label.setObjectName("tstampupdate_label")
        self.tstamp_update_label.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Maximum)
        self.tstamp_update_mon = PyDMLabel(
            self, self._prefixed_psname + ":TimestampUpdate-Mon")
        self.tstamp_update_mon.setObjectName("tstampupdate_mon_label")
        self.tstamp_update_mon.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Maximum)
        self.tstamp_update_mon_ch = SiriusConnectionSignal(
            self._prefixed_psname + ":TimestampUpdate-Mon")
        self.tstamp_update_mon_ch.new_value_signal[float].connect(
            self._tstamp_update_mon_met)

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
        layout.addWidget(self.tstamp_update_label, 2, 0, Qt.AlignHCenter)
        layout.addWidget(self.tstamp_update_mon, 2, 1, Qt.AlignHCenter)
        layout.addWidget(self.conn_label, 3, 0, Qt.AlignHCenter)
        layout.addWidget(self.conn_sts, 3, 1, Qt.AlignHCenter)
        return layout

    def _tstamp_update_mon_met(self, value):
        time_str = self.conv_time_string(value)
        self.tstamp_update_mon.setText(time_str)

    def _tstamp_boot_cte_met(self, value):
        time_str = self.conv_time_string(value)
        self.tstamp_boot_cte.setText(time_str)

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
                            **{'devname': self._prefixed_psname})
        if self._psname.dev == 'Spect':
            self.intlk_led = LISpectIntlkLed(self)
        else:
            ch2vals = {self._prefixed_psname+':StatusIntlk-Mon': {
                'value': _PS_LI_INTLK, 'comp': 'lt'}}
            self.intlk_led = PyDMLedMultiChannel(self, channels2values=ch2vals)

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
        self.params_box = QGroupBox('General Params')
        self.params_box.setObjectName('genparams_box')
        self.analog_box = QGroupBox(self._analog_varname)
        self.analog_box.setObjectName('current')
        self.aux_box = QGroupBox('DCLink Auxiliar Params')
        self.aux_box.setObjectName('aux_box')

        # Set group boxes layouts
        self.frmwr_box.setLayout(self._frmwrLayout())
        self.interlock_box.setLayout(self._interlockLayout())
        self.pwrstate_box.setLayout(self._powerStateLayout())
        self.opmode_box.setLayout(self._opModeLayout())
        self.ctrlloop_box.setLayout(self._ctrlLoopLayout())
        self.params_box.setLayout(self._genParamsLayout())
        self.analog_box.setLayout(self._analogLayout())
        self.aux_box.setLayout(self._auxLayout())

        # Add group boxes to laytout
        self.layout = self._setWidgetLayout()

        # Set widget layout
        self.setLayout(self.layout)

    def _setWidgetLayout(self):
        controls = QGridLayout()
        controls.addWidget(self.frmwr_box, 0, 0, 1, 2)
        controls.addWidget(self.opmode_box, 1, 0)
        controls.addWidget(self.pwrstate_box, 1, 1)
        controls.addWidget(self.ctrlloop_box, 2, 0)
        controls.addWidget(self.interlock_box, 2, 1)
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

        pbprm = QPushButton(qta.icon('mdi.open-in-new'),
                            'Parameters', self)
        util.connect_window(
            pbprm, PSParamsWidget, self, psname=self._psname,
            params=self._params)

        layout = QFormLayout()
        layout.addRow('Voltage 1', self._out_1_mon)
        layout.addRow('Voltage 2', self._out_2_mon)
        layout.addRow('Voltage 3', self._out_3_mon)
        layout.addRow('Voltage dig', self._out_dig_mon)
        layout.addRow('Module Status', self._mod_status_mon)
        layout.addRow(pbprm)
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
        layout = QFormLayout()

        for auxmeas in self._auxmeasures:
            pydmlbl = PyDMLabel(
                self, self._prefixed_psname + ':' + auxmeas)
            layout.addRow(auxmeas.split('-')[0], pydmlbl)

        pbaux = QPushButton(
            qta.icon('mdi.open-in-new'), 'Aux. Measures', self)
        util.connect_window(
            pbaux, PSAuxMeasWidget, self, psname=self._psname,
            auxmeas=list(), mod2dbase=self._mod2db,
            auxdev=self._auxdev, auxdev2mod=self._auxdev2mod)
        layout.addRow(pbaux)

        pbprm = QPushButton(qta.icon('mdi.open-in-new'),
                            'Parameters', self)
        util.connect_window(
            pbprm, PSParamsWidget, self, psname=self._psname,
            params=self._params)
        layout.addRow(pbprm)

        return layout


class FastCorrPSDetailWidget(PSDetailWidget):

    CONV_CORR2CHANNEL = {
        'M1-FCH': 0,
        'M1-FCV': 1,
        'M2-FCH': 2,
        'M2-FCV': 3,
        'C2-FCH': 4,
        'C2-FCV': 5,
        'C3-FCH': 6,
        'C3-FCV': 7,
    }

    def _setup_ui(self):
        # Group boxes that compose the widget
        self.opmode_box = QGroupBox('OpMode')
        self.opmode_box.setObjectName('operation_mode')
        self.pwrstate_box = QGroupBox("PwrState")
        self.pwrstate_box.setObjectName("power_state")
        self.ctrlloop_box = QGroupBox('Control Loop')
        self.ctrlloop_box.setObjectName('ctrlloop_box')
        self.interlock_box = QGroupBox("Interlock")
        self.interlock_box.setObjectName("interlock")
        self.params_box = QGroupBox('Params')
        self.params_box.setObjectName('params_box')
        self.current_a_box = QGroupBox("Current [A]")
        self.current_a_box.setObjectName("current")
        self.current_raw_box = QGroupBox("Current [Raw]")
        self.current_raw_box.setObjectName("current")
        self.waveform_box = self._wfmWidget()

        # Set group boxes layouts
        self.opmode_box.setLayout(self._opModeLayout())
        self.pwrstate_box.setLayout(self._powerStateLayout())
        self.ctrlloop_box.setLayout(self._ctrlLoopLayout())
        self.interlock_box.setLayout(self._interlockLayout())
        self.params_box.setLayout(self._paramsLayout())
        self.current_a_box.setLayout(self._currentALayout())
        self.current_raw_box.setLayout(self._currentRawLayout())

        # Add group boxes to laytout
        self.layout = self._setWidgetLayout()

        # Set widget layout
        self.setLayout(self.layout)

    def _setWidgetLayout(self):
        boxes_layout = QGridLayout()
        boxes_layout.addWidget(self.opmode_box, 0, 0)
        boxes_layout.addWidget(self.pwrstate_box, 0, 1)
        boxes_layout.addWidget(self.ctrlloop_box, 1, 0)
        boxes_layout.addWidget(self.interlock_box, 1, 1)
        boxes_layout.addWidget(self.params_box, 2, 0, 1, 2)
        boxes_layout.addWidget(self.current_a_box, 0, 2)
        boxes_layout.addWidget(self.current_raw_box, 1, 2)
        boxes_layout.addWidget(self.waveform_box, 2, 2)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("<h2>" + self._psname + "</h2>", self))
        layout.addLayout(boxes_layout)
        return layout

    def _powerStateLayout(self):
        self.state_button = PyDMStateButton(
            parent=self, init_channel=self._prefixed_psname + ':PwrState-Sel')
        self.pwrstate_led = SiriusLedState(
            parent=self, init_channel=self._prefixed_psname + ':PwrState-Sts')

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.state_button)
        layout.addWidget(self.pwrstate_led)
        return layout

    def _opModeLayout(self):
        test_lb = QLabel('Tests', self)

        oltriang_lb = QLabel('Open/Triang', self)
        self.oltriang_sb = PyDMStateButton(
            self, self._prefixed_psname + ':TestOpenLoopTriang-Sel')
        self.oltriang_rb = SiriusLedState(
            self, self._prefixed_psname + ':TestOpenLoopTriang-Sts')

        olsquare_lb = QLabel('Open/Square', self)
        self.olsquare_sb = PyDMStateButton(
            self, self._prefixed_psname + ':TestOpenLoopSquare-Sel')
        self.olsquare_rb = SiriusLedState(
            self, self._prefixed_psname + ':TestOpenLoopSquare-Sts')

        clsquare_lb = QLabel('Closed/Square', self)
        self.clsquare_sb = PyDMStateButton(
            self, self._prefixed_psname + ':TestClosedLoopSquare-Sel')
        self.clsquare_rb = SiriusLedState(
            self, self._prefixed_psname + ':TestClosedLoopSquare-Sts')

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setHorizontalSpacing(4)
        layout.addWidget(test_lb, 0, 0, 1, 3, Qt.AlignHCenter)
        layout.addWidget(oltriang_lb, 1, 0, Qt.AlignHCenter)
        layout.addWidget(self.oltriang_sb, 1, 1, Qt.AlignRight)
        layout.addWidget(self.oltriang_rb, 1, 2, Qt.AlignLeft)
        layout.addWidget(olsquare_lb, 2, 0, Qt.AlignHCenter)
        layout.addWidget(self.olsquare_sb, 2, 1, Qt.AlignRight)
        layout.addWidget(self.olsquare_rb, 2, 2, Qt.AlignLeft)
        layout.addWidget(clsquare_lb, 3, 0, Qt.AlignHCenter)
        layout.addWidget(self.clsquare_sb, 3, 1, Qt.AlignRight)
        layout.addWidget(self.clsquare_rb, 3, 2, Qt.AlignLeft)
        return layout

    def _ctrlLoopLayout(self):
        self.ctrlloop_btn = PyDMStateButton(
            parent=self, init_channel=self._prefixed_psname + ":CtrlLoop-Sel")
        self.ctrlloop_label = PyDMLabel(
            parent=self, init_channel=self._prefixed_psname + ":CtrlLoop-Sts")
        self.ctrlloop_label.setObjectName('ctrlloop_label')
        self.ctrlloop_led = SiriusLedState(
            parent=self, init_channel=self._prefixed_psname + ":CtrlLoop-Sts")

        lay_sts = QHBoxLayout()
        lay_sts.addWidget(self.ctrlloop_led)
        lay_sts.addWidget(self.ctrlloop_label)

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.ctrlloop_btn, 0, 0, Qt.AlignHCenter)
        layout.addLayout(lay_sts, 1, 0)
        return layout

    def _currentALayout(self):
        current_sp_label = QLabel("Setpoint")
        current_rb_label = QLabel("Readback")

        self.current_sp = SiriusSpinbox(
            self, self._prefixed_psname + ":Current-SP")
        self.current_sp.precisionFromPV = False
        self.current_sp.precision = 8
        self.current_sp.limitsFromChannel = False
        self.current_sp.setMinimum(-1.0)
        self.current_sp.setMaximum(+1.0)
        self.current_sp.showStepExponent = False
        self.current_rb = PyDMLabel(
            self, self._prefixed_psname+":Current-RB")
        self.current_rb.precisionFromPV = False
        self.current_rb.precision = 8
        self.current_rb.showUnits = True

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(current_sp_label, 0, 0, Qt.AlignRight)
        layout.addWidget(self.current_sp, 0, 1)
        layout.addWidget(current_rb_label, 1, 0, Qt.AlignRight)
        layout.addWidget(self.current_rb, 1, 1)
        layout.setColumnStretch(2, 1)
        return layout

    def _currentRawLayout(self):
        current_sp_label = QLabel("Setpoint")
        current_rb_label = QLabel("Readback")

        self.current_sp = PyDMLineEdit(
            self, self._prefixed_psname + ":CurrentRaw-SP")
        self.current_rb = PyDMLabel(
            self, self._prefixed_psname+":CurrentRaw-RB")

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(current_sp_label, 0, 0, Qt.AlignRight)
        layout.addWidget(self.current_sp, 0, 1)
        layout.addWidget(current_rb_label, 1, 0, Qt.AlignRight)
        layout.addWidget(self.current_rb, 1, 1)
        layout.setColumnStretch(2, 1)
        return layout

    def _interlockLayout(self):
        alarms = [
            'PSAmpOverCurrFlagL-Sts',
            'PSAmpOverCurrFlagR-Sts',
            'PSAmpOverTempFlagL-Sts',
            'PSAmpOverTempFlagR-Sts',
        ]
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignCenter)
        for i, alm in enumerate(alarms):
            led = PyDMLed(self, self._prefixed_psname + ':' + alm)
            led.onColor = led.LightGreen
            led.offColor = led.Red
            label = QLabel(alm.split('-')[0].split('PSAmp')[1], self)
            layout.addWidget(led, i, 0)
            layout.addWidget(label, i, 1)
        return layout

    def _paramsLayout(self):
        ctlkp_lb = QLabel('CtrlLoopKp', self, alignment=Qt.AlignRight)
        self.ctlkp_sp = PyDMLineEdit(
            self, self._prefixed_psname + ':CtrlLoopKp-SP')
        self.ctlkp_rb = PyDMLabel(
            self, self._prefixed_psname + ':CtrlLoopKp-RB')

        ctlti_lb = QLabel('CtrlLoopTi', self, alignment=Qt.AlignRight)
        self.ctlti_sp = PyDMLineEdit(
            self, self._prefixed_psname + ':CtrlLoopTi-SP')
        self.ctlti_rb = PyDMLabel(
            self, self._prefixed_psname + ':CtrlLoopTi-RB')

        cgain_lb = QLabel('CurrGain', self, alignment=Qt.AlignRight)
        self.cgain_sp = PyDMLineEdit(
            self, self._prefixed_psname + ':CurrGain-SP')
        self.cgain_sp.precisionFromPV = False
        self.cgain_sp.precision = 8
        self.cgain_rb = PyDMLabel(
            self, self._prefixed_psname + ':CurrGain-RB')
        self.cgain_rb.precisionFromPV = False
        self.cgain_rb.precision = 8

        coffs_lb = QLabel('CurrOffset', self, alignment=Qt.AlignRight)
        self.coffs_sp = PyDMLineEdit(
            self, self._prefixed_psname + ':CurrOffset-SP')
        self.coffs_sp.precisionFromPV = False
        self.coffs_sp.precision = 8
        self.coffs_rb = PyDMLabel(
            self, self._prefixed_psname + ':CurrOffset-RB')
        self.coffs_rb.precisionFromPV = False
        self.coffs_rb.precision = 8

        vgain_lb = QLabel('VoltGain', self, alignment=Qt.AlignRight)
        self.vgain_sp = PyDMLineEdit(
            self, self._prefixed_psname + ':VoltGain-SP')
        self.vgain_sp.precisionFromPV = False
        self.vgain_sp.precision = 8
        self.vgain_rb = PyDMLabel(
            self, self._prefixed_psname + ':VoltGain-RB')
        self.vgain_rb.precisionFromPV = False
        self.vgain_rb.precision = 8

        voffs_lb = QLabel('VoltOffset', self, alignment=Qt.AlignRight)
        self.voffs_sp = PyDMLineEdit(
            self, self._prefixed_psname + ':VoltOffset-SP')
        self.voffs_sp.precisionFromPV = False
        self.voffs_sp.precision = 8
        self.voffs_rb = PyDMLabel(
            self, self._prefixed_psname + ':VoltOffset-RB')
        self.voffs_rb.precisionFromPV = False
        self.voffs_rb.precision = 8

        layout = QGridLayout()
        layout.addWidget(ctlkp_lb, 0, 0, Qt.AlignRight)
        layout.addWidget(self.ctlkp_sp, 0, 1)
        layout.addWidget(self.ctlkp_rb, 0, 2)
        layout.addWidget(ctlti_lb, 1, 0, Qt.AlignRight)
        layout.addWidget(self.ctlti_sp, 1, 1)
        layout.addWidget(self.ctlti_rb, 1, 2)
        layout.addWidget(cgain_lb, 2, 0, Qt.AlignRight)
        layout.addWidget(self.cgain_sp, 2, 1)
        layout.addWidget(self.cgain_rb, 2, 2)
        layout.addWidget(coffs_lb, 3, 0, Qt.AlignRight)
        layout.addWidget(self.coffs_sp, 3, 1)
        layout.addWidget(self.coffs_rb, 3, 2)
        layout.addWidget(vgain_lb, 4, 0, Qt.AlignRight)
        layout.addWidget(self.vgain_sp, 4, 1)
        layout.addWidget(self.vgain_rb, 4, 2)
        layout.addWidget(voffs_lb, 5, 0, Qt.AlignRight)
        layout.addWidget(self.voffs_sp, 5, 1)
        layout.addWidget(self.voffs_rb, 5, 2)
        return layout

    def _wfmWidget(self):
        fofbctrl = SiriusPVName('IA-99RaBPM:BS-FOFBCtrl')
        subnum = self._prefixed_psname.sub[:2]
        subnam = self._prefixed_psname.sub[2:]
        dev = self._prefixed_psname.dev
        fofbctrl = fofbctrl.replace('99', subnum)
        # fofbctrl = fofbctrl.replace('IA-'+subnum, 'XX-99SL01')  # comment
        chn = FastCorrPSDetailWidget.CONV_CORR2CHANNEL[subnam+'-'+dev]

        self.graph_curr = PyDMWaveformPlot()
        # self.graph_curr.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Maximum)
        self.graph_curr.autoRangeX = True
        self.graph_curr.autoRangeY = True
        self.graph_curr.showXGrid = True
        self.graph_curr.showYGrid = True
        self.graph_curr.title = 'Current'
        self.graph_curr.setLabel("left", text='Current [A]')
        self.graph_curr.setLabel("bottom", text='Index')
        self.graph_curr.plotItem.showButtons()
        self.graph_curr.setBackgroundColor(QColor(255, 255, 255))
        self.graph_curr.addChannel(
            y_channel=fofbctrl.substitute(
                propty='GENConvArrayDataCH'+str(chn)),
            name='Current', color='blue', lineWidth=2)

        self.graph_volt = PyDMWaveformPlot()
        # self.graph_volt.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Maximum)
        self.graph_volt.autoRangeX = True
        self.graph_volt.autoRangeY = True
        self.graph_volt.showXGrid = True
        self.graph_volt.showYGrid = True
        self.graph_volt.title = 'Voltage'
        self.graph_volt.setLabel("left", text='Voltage [V]')
        self.graph_volt.setLabel("bottom", text='Index')
        self.graph_volt.plotItem.showButtons()
        self.graph_volt.setBackgroundColor(QColor(255, 255, 255))
        self.graph_volt.addChannel(
            y_channel=fofbctrl.substitute(
                propty='GENConvArrayDataCH'+str(chn+12)),
            name='Voltage', color='blue', lineWidth=2)

        self.graph_chist = SiriusTimePlot()
        self.graph_chist.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Maximum)
        self.graph_chist.autoRangeX = True
        self.graph_chist.autoRangeY = True
        self.graph_chist.showXGrid = True
        self.graph_chist.showYGrid = True
        self.graph_chist.title = 'Current Mean History'
        self.graph_chist.setLabel("left", text='Current [A]')
        self.graph_chist.showLegend = True
        timespan = 5*60  # 5min
        self.graph_chist.timeSpan = timespan  # [s]
        self.graph_chist.bufferSize = 5*timespan  # [max 5 samples/s]
        self.graph_chist.plotItem.showButtons()
        self.graph_chist.setBackgroundColor(QColor(255, 255, 255))
        self.graph_chist.addYChannel(
            y_channel=self._prefixed_psname.substitute(propty='Current-SP'),
            name='SP', color='red', lineWidth=2)
        self.graph_chist.addYChannel(
            y_channel=self._prefixed_psname.substitute(propty='Current-RB'),
            name='RB', color='blue', lineWidth=2)
        self.chn_chist = SiriusConnectionSignal(fofbctrl.substitute(
            propty='GENConvArrayDataCH'+str(chn)))
        self.chn_chist.new_value_signal[_np.ndarray].connect(
            self._plot_currhist)
        self.graph_chist.addYChannel(
            y_channel='FAKE:CurrentHistory',
            name='Mon', color='black', lineWidth=2)
        self.curve_chist = self.graph_chist.curveAtIndex(2)

        tab = QTabWidget(self)
        tab.setObjectName('SITab')
        tab.addTab(self.graph_curr, 'Curr.')
        tab.addTab(self.graph_volt, 'Volt.')
        tab.addTab(self.graph_chist, 'Curr.Hist.')
        tab.setCurrentIndex(2)
        tab.setStyleSheet("""
            #SITab::pane {
                border-left: 2px solid gray;
                border-bottom: 2px solid gray;
                border-right: 2px solid gray;
            }""")
        return tab

    def _plot_currhist(self, new_array):
        mean = _np.mean(new_array)
        self.curve_chist.receiveNewValue(mean)


class PSAuxMeasWidget(SiriusDialog):
    """PS Modules Detail Widget."""

    def __init__(self, parent, psname, auxmeas, mod2dbase,
                 auxdev, auxdev2mod):
        """Init."""
        super().__init__(parent)
        self._psname = [psname, ]
        if auxdev:
            self._psname = list()
            for aux in auxdev:
                self._psname.append(psname+aux)
        self._prefixed_psname = SiriusPVName(psname).substitute(
            prefix=VACA_PREFIX)

        self.auxmeas = auxmeas
        self.mod2dbase = mod2dbase
        self.auxdev2mod = auxdev2mod

        self.title_text = psname + ' - Auxiliary Measures'
        self.setWindowTitle(self.title_text)

        self.setObjectName(parent.objectName())

        self._setupUi()
        self.setStyleSheet('PyDMLabel{qproperty-alignment: AlignCenter;}')

    def _setupUi(self):
        text_psname = QLabel('<h3>' + self._psname[0] + '</h3>', self,
                             alignment=Qt.AlignCenter)

        pswid = None
        if self.auxmeas:
            title_main = QLabel('<h3>Main Measures</h3>', self,
                                alignment=Qt.AlignCenter)
            pswid = self._setupPSWidget()

        if len(self.mod2dbase) > 1:
            title_iib = QLabel('<h3>IIB Measures</h3>', self,
                               alignment=Qt.AlignCenter)
            lay_mod = QGridLayout()
            ncols = 4 if len(self.mod2dbase)*len(self._psname) > 4 else 2
            idx = 0
            for psn in self._psname:
                for mod, dbase in self.mod2dbase.items():
                    modwid = self._setupModWidget(psn, mod, dbase)
                    lay_mod.addWidget(modwid, idx//ncols, idx % ncols)
                    idx += 1

            lay = QGridLayout(self)
            lay.setHorizontalSpacing(20)
            lay.setVerticalSpacing(20)
            if pswid:
                lay.addWidget(text_psname, 0, 0, 1, 2)
                lay.addWidget(title_main, 1, 0)
                lay.addWidget(pswid, 2, 0)
                lay.addWidget(title_iib, 1, 1)
                lay.addLayout(lay_mod, 2, 1)
            else:
                lay.addWidget(text_psname, 0, 0)
                lay.addWidget(title_iib, 1, 0)
                lay.addLayout(lay_mod, 2, 0)
        else:
            lay = QVBoxLayout(self)
            lay.setSpacing(15)
            lay.addWidget(text_psname)

            if pswid:
                lay.addWidget(title_main)
                lay.addWidget(pswid)

            dbase = self.mod2dbase['main']
            if dbase:
                title_iib = QLabel('<h3>IIB Measures</h3>', self,
                                   alignment=Qt.AlignCenter)
                modwid = self._setupModWidget(self._psname[0], 'main', dbase)
                lay.addWidget(title_iib)
                lay.addWidget(modwid)

    def _setupPSWidget(self):
        wid = QWidget()
        if len(self.auxmeas) > 32:
            lay = QHBoxLayout(wid)
            lay.setSpacing(20)

            half1 = self.auxmeas[:20]
            flay1 = QFormLayout()
            flay1.setVerticalSpacing(9)
            for pv in half1:
                text = pv.split('-')[0]
                lbl = PyDMLabel(
                    self, self._prefixed_psname.substitute(propty=pv))
                lbl.showUnits = True
                flay1.addRow(text, lbl)

            half2 = self.auxmeas[20:]
            flay2 = QFormLayout()
            flay2.setVerticalSpacing(9)
            for pv in half2:
                text = pv.split('-')[0]
                lbl = PyDMLabel(
                    self, self._prefixed_psname.substitute(propty=pv))
                lbl.showUnits = True
                flay2.addRow(text, lbl)

            lay.addLayout(flay1)
            lay.addLayout(flay2)
        else:
            flay = QFormLayout(wid)
            for pv in self.auxmeas:
                text = pv.split('-')[0]
                lbl = PyDMLabel(
                    self, self._prefixed_psname.substitute(propty=pv))
                lbl.showUnits = True
                flay.addRow(text, lbl)
        return wid

    def _setupModWidget(self, psname, mod, dbase):
        wid = QWidget()
        lay = QVBoxLayout(wid)
        lay.setAlignment(Qt.AlignTop)

        modname = mod
        if psname in self.auxdev2mod:
            modname = self.auxdev2mod[psname][mod]

        if mod != 'main':
            self.title = QLabel('<h3>Mod'+modname+'</h3>', self,
                                alignment=Qt.AlignCenter)
            lay.addWidget(self.title)

        flay = QFormLayout()
        for pv in dbase:
            text = pv.split('Mod'+mod)[0].split('IIB')[0]
            lbl = PyDMLabel(self, psname + ':' + pv)
            lbl.showUnits = True
            flay.addRow(text, lbl)
        lay.addLayout(flay)

        return wid


class PSParamsWidget(SiriusDialog):
    """PS Parameters Widget."""

    def __init__(self, parent, psname, params):
        """Init."""
        super().__init__(parent)
        self._psname = SiriusPVName(psname)
        self._prefix = VACA_PREFIX
        self._prefixed_psname = self._psname.substitute(prefix=self._prefix)

        self.params = params

        self.title_text = psname + ' - Parameters'
        self.setWindowTitle(self.title_text)

        self.setObjectName(parent.objectName())

        self._setupUi()
        self.setStyleSheet(
            'PyDMLabel{qproperty-alignment: AlignVCenter;}')

    def _setupUi(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(15)

        text_psname = QLabel('<h3>' + self._psname + '</h3>', self,
                             alignment=Qt.AlignCenter)
        lay.addWidget(text_psname)

        scr_area = QScrollArea(self)
        scr_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scr_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scr_area.setWidgetResizable(True)
        scr_area.setFrameShape(QFrame.NoFrame)
        scr_area_wid = QWidget()
        scr_area_wid.setObjectName('scr_ar_wid')
        scr_area_wid.setStyleSheet(
            '#scr_ar_wid {background-color: transparent;}')
        scr_area.setWidget(scr_area_wid)
        flay = QFormLayout(scr_area_wid)
        flay.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Update
        text = 'Update Command'
        wid = PyDMPushButton(
            parent=self, icon=qta.icon('fa5s.redo-alt'), pressValue=1,
            init_channel=self._prefixed_psname + ":ParamUpdate-Cmd")
        wid.setObjectName('updt_bt')
        wid.setStyleSheet(
            '#updt_bt{min-width:25px; max-width:25px; icon-size:20px;}')
        flay.addRow(text, wid)

        # Params
        for param in self.params:
            pvname = self._prefixed_psname + ':' + param
            text = param.split('-')[0].split('Param')[1]
            if 'Intlk' in pvname or 'Analog' in pvname:
                wid = self._create_table_wid(pvname)
                text += ' [us]'
            else:
                wid = self._create_label_wid(pvname)
            flay.addRow(text, wid)
        lay.addWidget(scr_area)

    def _create_label_wid(self, pvname):
        lbl = CustomLabel(self)
        if 'PSName' in pvname:
            lbl.displayFormat = PyDMLabel.DisplayFormat.String
        elif 'PSModel' in pvname:
            lbl.enum_strings = _PSet.MODELS
        elif 'SigGenType' in pvname:
            lbl.enum_strings = _PSet.CYCLE_TYPES
        elif 'WfmRefSyncMode' in pvname:
            lbl.enum_strings = _PSet.WFMREF_SYNCMODE
        else:
            lbl.showUnits = True
        lbl.channel = pvname
        return lbl

    def _create_table_wid(self, pvname):
        table = SiriusWaveformTable(self, pvname)
        table.showUnits = True
        col_count = 32 if 'Intlk' in pvname else 64
        table.setColumnCount(col_count)
        table.setObjectName('table')
        table.setStyleSheet('#table{max-width:24em; max-height: 3em;}')
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.horizontalHeader().setStyleSheet(
            "min-height:1em; max-height:1em;")
        table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.columnHeaderLabels = [str(i) for i in range(col_count)]
        table.rowHeaderLabels = []
        return table


class CustomLabel(PyDMLabel):

    def value_changed(self, new_value):
        super(PyDMLabel, self).value_changed(new_value)
        new_value = parse_value_for_display(
            value=new_value, precision=self.precision,
            display_format_type=self._display_format_type,
            string_encoding=self._string_encoding, widget=self)
        if isinstance(new_value, str):
            if self._show_units and self._unit != "":
                new_value = "{} {}".format(new_value, self._unit)
            self.setText(new_value)
            return
        if self.enum_strings is not None and \
                isinstance(new_value, (int, float)):
            try:
                self.setText(self.enum_strings[int(new_value)])
            except IndexError:
                self.setText("**INVALID**")
            return
        elif self.enum_strings is not None and \
                isinstance(new_value, _np.ndarray):
            text = '['+', '.join([self.enum_strings[int(idx)]
                                  if idx < len(self.enum_strings) else 'UNDEF'
                                  for idx in new_value])+']'
            self.setText(text)
            return
        if isinstance(new_value, (int, float)):
            self.setText(self.format_string.format(new_value))
            return
        self.setText(str(new_value))


class CustomSpinBox(SiriusSpinbox):

    def valueFromText(self, text):
        return int(str(text), 16)

    def textFromValue(self, value):
        return hex(int(value))

    def validate(self, text, pos):
        regex = QRegExp("0x[0-9A-Fa-f]{1,8}")
        regex.setCaseSensitivity(Qt.CaseInsensitive)
        return QRegExpValidator(regex, self).validate(text, pos)

    def update_step_size(self):
        """Reimplement to use hexa base."""
        self.setSingleStep(16 ** self.step_exponent)
        self.update_format_string()

    def update_format_string(self):
        """Reimplement to use hexa base."""
        if self._show_units:
            units = " {}".format(self._unit)
        else:
            units = ""

        if self._show_step_exponent:
            self.setSuffix(
                '{0} Step: 16**{1}'.format(units, self.step_exponent))
            self.lineEdit().setToolTip("")
        else:
            self.setSuffix(units)
            self.lineEdit().setToolTip(
                'Step: 16**{0:+d}'.format(self.step_exponent))
