"""PS Detail Widget."""

import re
from datetime import datetime as _datetime
from functools import partial as _part
import numpy as _np

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGroupBox, QPushButton, QLabel, \
    QGridLayout, QVBoxLayout, QHBoxLayout, QFormLayout, QTabWidget, \
    QSizePolicy as QSzPlcy, QCheckBox, QHeaderView, QAbstractItemView, \
    QScrollArea, QFrame, QComboBox
from qtpy.QtGui import QColor

import qtawesome as qta

from pydm.widgets import PyDMEnumComboBox, PyDMPushButton, PyDMLineEdit
from pydm.widgets.display_format import parse_value_for_display

from siriuspy.util import get_strength_label
from siriuspy.namesys import SiriusPVName
from siriuspy.envars import VACA_PREFIX
from siriuspy.search import PSSearch
from siriuspy.pwrsupply.csdev import get_ps_propty_database, get_ps_modules, \
    DEF_WFMSIZE_FBP, DEF_WFMSIZE_OTHERS, PS_LI_INTLK_THRS as _PS_LI_INTLK, \
    ETypes as _PSet, get_ps_scopesourcemap
from siriuspy.devices import PowerSupply

from ... import util
from ...widgets import PyDMStateButton, PyDMSpinboxScrollbar, SiriusTimePlot, \
    SiriusConnectionSignal, SiriusLedState, SiriusLedAlert, SiriusLabel, \
    PyDMLedMultiChannel, SiriusDialog, SiriusWaveformTable, SiriusSpinbox, \
    SiriusHexaSpinbox, SiriusWaveformPlot, PyDMLed, SiriusStringComboBox, \
    PyDMLinEditScrollbar
from .InterlockWindow import InterlockWindow, LIInterlockWindow
from .custom_widgets import LISpectIntlkLed


class _BaseDetailWidget(QWidget):
    """Widget with some common layouts."""

    StyleSheet = """
        #opmode_sp_cbox{
            min-width: 7em;
            max-width: 7em;
        }
        #opmode_rb_label,
        #psstatus_mon{
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
        #current > SiriusLabel,
        #metric > SiriusLabel {
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
        #auxmeaslabel {
            min-width: 7.5em;
            qproperty-alignment: AlignCenter;
        }
    """

    def __init__(self, psname, parent=None):
        """Class constructor."""
        super(_BaseDetailWidget, self).__init__(parent)
        self._prefix = VACA_PREFIX
        self._psname = SiriusPVName(psname)

        try:
            self._metric = get_strength_label(
                PSSearch.conv_psname_2_magfunc(self._psname))
        except (ValueError, KeyError):
            self._metric = ''

        self._prefixed_psname = self._psname.substitute(prefix=self._prefix)

        self.setObjectName(parent.objectName())

        self.setFocus(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Maximum)

    @staticmethod
    def conv_time_string(value):
        time_str = _datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')
        time_str += '.{:03d}'.format(int(1e3*(value % 1)))
        return time_str

    def _powerStateLayout(self):
        self.state_button = PyDMStateButton(
            parent=self, init_channel=self._prefixed_psname + ":PwrState-Sel")
        self.pwrstate_led = SiriusLedState(
            parent=self, init_channel=self._prefixed_psname + ":PwrState-Sts")
        self.pwrstate_label = SiriusLabel(
            parent=self, init_channel=self._prefixed_psname + ":PwrState-Sts")
        self.pwrstate_label.setObjectName("pwrstate_label")

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setHorizontalSpacing(4)
        layout.addWidget(self.state_button, 0, 0, 1, 2, Qt.AlignHCenter)
        layout.addWidget(self.pwrstate_led, 1, 0, Qt.AlignRight)
        layout.addWidget(self.pwrstate_label, 1, 1, Qt.AlignLeft)
        return layout

    def _currentLayout(self, prec=None, has_refmon=True):
        current_sp_label = QLabel("Setpoint")
        current_rb_label = QLabel("Readback")
        current_mon_label = QLabel("Mon")

        self.current_sp_wid = PyDMSpinboxScrollbar(
            self, self._prefixed_psname + ":Current-SP")
        self.current_rb_val = SiriusLabel(
            self, self._prefixed_psname+":Current-RB", keep_unit=True)
        self.current_rb_val.showUnits = True
        self.current_mon_val = SiriusLabel(
            self, self._prefixed_psname+":Current-Mon", keep_unit=True)
        self.current_mon_val.showUnits = True

        if has_refmon:
            current_ref_label = QLabel("Ref Mon")
            self.current_ref_val = SiriusLabel(
                self, self._prefixed_psname+":CurrentRef-Mon", keep_unit=True)
            self.current_ref_val.showUnits = True

        if prec is not None:
            self.current_sp_wid.spinbox.precisionFromPV = False
            self.current_sp_wid.spinbox.precision = prec
            self.current_rb_val.precisionFromPV = False
            self.current_rb_val.precision = prec
            self.current_mon_val.precisionFromPV = False
            self.current_mon_val.precision = prec
            if has_refmon:
                self.current_ref_val.precisionFromPV = False
                self.current_ref_val.precision = prec
        else:
            self.current_rb_val.precisionFromPV = True
            self.current_mon_val.precisionFromPV = True
            if has_refmon:
                self.current_ref_val.precisionFromPV = True

        layout = QGridLayout()
        layout.addWidget(current_sp_label, 0, 0, Qt.AlignRight)
        layout.addWidget(self.current_sp_wid, 0, 1)
        layout.addWidget(current_rb_label, 1, 0, Qt.AlignRight)
        layout.addWidget(self.current_rb_val, 1, 1)
        if has_refmon:
            layout.addWidget(current_ref_label, 2, 0, Qt.AlignRight)
            layout.addWidget(self.current_ref_val, 2, 1)
            layout.addWidget(current_mon_label, 3, 0, Qt.AlignRight)
            layout.addWidget(self.current_mon_val, 3, 1)
        else:
            layout.addWidget(current_mon_label, 2, 0, Qt.AlignRight)
            layout.addWidget(self.current_mon_val, 2, 1)
        layout.setColumnStretch(2, 1)
        return layout

    def _metricLayout(self, prec=None, has_refmon=True):
        metric_sp_ch = self._prefixed_psname+":"+self._metric+"-SP"
        metric_rb_ch = self._prefixed_psname+":"+self._metric+"-RB"
        metric_mon_ch = self._prefixed_psname+":"+self._metric+"-Mon"

        metric_sp_label = QLabel("Setpoint")
        metric_rb_label = QLabel("Readback")
        metric_mon_label = QLabel("Mon")

        self.metric_sp_wid = PyDMSpinboxScrollbar(self, metric_sp_ch)
        self.metric_rb_val = SiriusLabel(
            parent=self, init_channel=metric_rb_ch, keep_unit=True)
        self.metric_rb_val.showUnits = True
        self.metric_mon_val = SiriusLabel(
            parent=self, init_channel=metric_mon_ch, keep_unit=True)
        self.metric_mon_val.showUnits = True

        if has_refmon:
            metric_ref_ch = self._prefixed_psname+":"+self._metric+"Ref-Mon"
            metric_ref_label = QLabel("Ref Mon")
            self.metric_ref_val = SiriusLabel(
                parent=self, init_channel=metric_ref_ch, keep_unit=True)
            self.metric_ref_val.showUnits = True

        if prec is not None:
            self.metric_sp_wid.spinbox.precisionFromPV = False
            self.metric_sp_wid.spinbox.precision = prec
            self.metric_rb_val.precisionFromPV = False
            self.metric_rb_val.precision = prec
            self.metric_mon_val.precisionFromPV = False
            self.metric_mon_val.precision = prec
            if has_refmon:
                self.metric_ref_val.precisionFromPV = False
                self.metric_ref_val.precision = prec
        else:
            self.metric_rb_val.precFromPV = True
            self.metric_mon_val.precFromPV = True
            if has_refmon:
                self.metric_ref_val.precFromPV = True

        layout = QGridLayout()
        layout.addWidget(metric_sp_label, 0, 0, Qt.AlignRight)
        layout.addWidget(self.metric_sp_wid, 0, 1)
        layout.addWidget(metric_rb_label, 1, 0, Qt.AlignRight)
        layout.addWidget(self.metric_rb_val, 1, 1)
        if has_refmon:
            layout.addWidget(metric_ref_label, 2, 0, Qt.AlignRight)
            layout.addWidget(self.metric_ref_val, 2, 1)
            layout.addWidget(metric_mon_label, 3, 0, Qt.AlignRight)
            layout.addWidget(self.metric_mon_val, 3, 1)
        else:
            layout.addWidget(metric_mon_label, 2, 0, Qt.AlignRight)
            layout.addWidget(self.metric_mon_val, 2, 1)
        layout.setColumnStretch(3, 1)
        return layout


class PSDetailWidget(_BaseDetailWidget):
    """Widget with control interface for a given magnet."""

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
        'IDFFMode-Sel', 'IDFFMode-Sts',
        'PRUCtrlQueueSize-Mon', 'SyncPulse-Cmd',
        'Wfm-SP', 'Wfm-RB', 'WfmRef-Mon', 'Wfm-Mon',
        'Voltage-SP', 'Voltage-RB', 'VoltageRef-Mon', 'Voltage-Mon',
        'CapacitorBankVoltage-SP', 'CapacitorBankVoltage-RB',
        'CapacitorBankVoltageRef-Mon', 'CapacitorBankVoltage-Mon',
        'ScopeSrcAddr-SP', 'ScopeSrcAddr-RB',
        'ScopeFreq-SP', 'ScopeFreq-RB',
        'ScopeDuration-SP', 'ScopeDuration-RB',
        'WfmSyncMode-Sel', 'WfmSyncMode-Sts',
        'WfmFreq-SP', 'WfmFreq-RB',
        'WfmGain-SP', 'WfmGain-RB',
        'WfmOffset-SP', 'WfmOffset-RB',
    ]

    def __init__(self, psname, parent=None, psmodel=None, pstype=None):
        """Class constructor."""
        super(PSDetailWidget, self).__init__(psname, parent=parent)
        self._psmodel = psmodel or PSSearch.conv_psname_2_psmodel(psname)
        self._pstype = pstype or PSSearch.conv_psname_2_pstype(psname)

        self._db = get_ps_propty_database(self._psmodel, self._pstype)
        self._mods = get_ps_modules(psmodel=self._psmodel)

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
        if psname in self._auxdev2mod:
            self._auxdev = ['', 'a', 'b', 'c']

        self._setup_ui()
        self.setStyleSheet(self.StyleSheet)

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
        if self._psmodel == 'FBP':
            self.iocmode_box = QGroupBox('IOC Mode')
            self.iocmode_box.setObjectName('iocmode_box')
        self.genparams_box = QGroupBox('General Params')
        self.genparams_box.setObjectName('genparams_box')
        self.current_box = QGroupBox("Current")
        self.current_box.setObjectName("current")
        self.siggen_tab = QWidget()
        self.siggen_tab.setObjectName('cycle_tab')
        self.wfmplot_tab = QWidget()
        self.wfmplot_tab.setObjectName("wfm_tab")
        self.wfmparams_tab = QWidget()
        self.wfmparams_tab.setObjectName('wfmparams_tab')
        self.curve_tabs = QTabWidget()
        self.curve_tabs.setObjectName(self._psname.sec+'Tab')
        self.curve_tabs.setStyleSheet(
            '#'+self._psname.sec+'Tab::pane {'
            '    border-left: 2px solid gray;'
            '    border-bottom: 2px solid gray;'
            '    border-right: 2px solid gray;}')
        self.curve_tabs.addTab(self.siggen_tab, 'SigGen')
        self.curve_tabs.addTab(self.wfmplot_tab, 'WfmPlot')
        self.curve_tabs.addTab(self.wfmparams_tab, 'WfmParams')
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
        if self._psmodel == 'FBP':
            self.iocmode_box.setLayout(self._iocModeLayout())
        self.genparams_box.setLayout(self._genParamsLayout())
        self.current_box.setLayout(self._currentLayout())
        self.siggen_tab.setLayout(self._siggenLayout())
        self.wfmplot_tab.setLayout(self._wfmplotLayout())
        self.wfmparams_tab.setLayout(self._wfmparamsLayout())
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
            controls.addWidget(self.iocmode_box, 4, 1)
        else:
            controls.addWidget(self.genparams_box, 4, 0, 1, 2)

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

        self.version_cte = SiriusLabel(
            self, self._prefixed_psname + ":Version-Cte")
        self.version_cte.displayFormat = \
            SiriusLabel.DisplayFormat.BSMPUDCVersion
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
            devname=self._psname, database=self._db, interlock='IntlkSoft',
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
            devname=self._psname, database=self._db, interlock='IntlkHard',
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
                devname=self._psname, database=self._db, interlock=iib_intlks,
                auxdev=self._auxdev, auxdev2mod=self._auxdev2mod)

            chs2vals = dict()
            for aux in self._auxdev:
                chs2vals.update({self._prefixed_psname+aux+":"+intlk+"-Mon": 0
                                 for intlk in iib_intlks})
            self.iib_intlk_led = PyDMLedMultiChannel(self, chs2vals)

        alarms = ['Alarms', ] if 'Alarms-Mon' in self._db else []
        alarms.extend([k.replace('Labels-Cte', '') for k in self._db
                       if re.match('AlarmsIIB.*Labels-Cte', k)])
        if alarms:
            self.alarm_label = QLabel(
                'Alarms', self, alignment=Qt.AlignCenter)
            self.alarm_bt = QPushButton(qta.icon('fa5s.list-ul'), '', self)
            self.alarm_bt.setObjectName('alarm_bt')
            self.alarm_bt.setStyleSheet(
                '#alarm_bt{min-width:25px;max-width:25px;icon-size:20px;}')
            util.connect_window(
                self.alarm_bt, InterlockWindow, self,
                devname=self._psname, database=self._db, interlock=alarms,
                auxdev=self._auxdev, auxdev2mod=self._auxdev2mod)

            chs2vals = dict()
            for aux in self._auxdev:
                chs2vals.update({self._prefixed_psname+aux+":"+alarm+"-Mon": 0
                                 for alarm in alarms})
            self.alarm_led = PyDMLedMultiChannel(
                self, chs2vals,
                color_list=[PyDMLed.Yellow, PyDMLed.LightGreen, PyDMLed.Gray])

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
        if alarms:
            layout.addWidget(self.alarm_bt, 3, 0)
            layout.addWidget(self.alarm_label, 3, 1)
            layout.addWidget(self.alarm_led, 3, 2)
        layout.addWidget(self.reset_bt, 4, 2)
        return layout

    def _opModeLayout(self):
        self.opmode_sp = PyDMEnumComboBox(
            self, self._prefixed_psname + ":OpMode-Sel")
        self.opmode_sp.setObjectName("opmode_sp_cbox")
        self.opmode_rb = SiriusLabel(
            self, self._prefixed_psname + ":OpMode-Sts")
        self.opmode_rb.setObjectName("opmode_rb_label")
        self.ctrlmode_led = SiriusLedAlert(
            self, self._prefixed_psname + ":CtrlMode-Mon")
        self.ctrlmode_label = SiriusLabel(
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
        self.ctrlloop_label = SiriusLabel(
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

    def _siggenLayout(self):
        # Tab
        self.tab_siggen = QTabWidget(self)
        self.tab_siggen.setObjectName(self._psname.sec+'Tab')

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
        self.cycle_type_rb_label = SiriusLabel(self, type_rb_ca)

        self.cycle_nr_label = QLabel('Nr. Cycles', self)
        self.cycle_nr_sp_sb = PyDMLineEdit(self, nrcycles_sp_ca)
        self.cycle_nr_rb_label = SiriusLabel(self, nrcycles_rb_ca)

        self.cycle_index_label = QLabel('Index', self)
        self.cycle_index_mon_label = SiriusLabel(self, index_ca)

        self.cycle_freq_label = QLabel('Frequency', self)
        self.cycle_freq_sp_sb = PyDMLineEdit(self, freq_sp_ca)
        self.cycle_freq_rb_label = SiriusLabel(self, freq_rb_ca)

        self.cycle_ampl_label = QLabel('Amplitude', self)
        self.cycle_ampl_sp_sb = PyDMLineEdit(self, ampl_sp_ca)
        self.cycle_ampl_rb_label = SiriusLabel(self, ampl_rb_ca)

        self.cycle_offset_label = QLabel('Offset', self)
        self.cycle_offset_sp_sb = PyDMLineEdit(self, offset_sp_ca)
        self.cycle_offset_rb_label = SiriusLabel(self, offset_rb_ca)

        self.cycle_auxparam_label = QLabel('AuxParams', self)
        self.cycle_auxparam_sp_le = PyDMLineEdit(self, auxparam_sp_ca)
        self.cycle_auxparam_rb_label = SiriusLabel(self, auxparam_rb_ca)

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

        self.tab_siggen.addTab(parms, 'Params')

        # Default Curve
        try:
            self._siggen = PSSearch.conv_psname_2_siggenconf(self._psname)
        except KeyError:
            self._siggen = None

        if self._siggen is not None:
            self._siggen_nrpts = DEF_WFMSIZE_FBP if self._psmodel == 'FBP' \
                else DEF_WFMSIZE_OTHERS
            self._siggen_w = self._siggen.get_waveform(self._siggen_nrpts)

            self.curve_siggen = SiriusWaveformPlot()
            self.curve_siggen.setObjectName('graph')
            self.curve_siggen.setStyleSheet(
                '#graph{max-height:15em; max-width:16.5em;}')
            self.curve_siggen.setLabel('left', text='Current [A]', color='gray')
            self.curve_siggen.setLabel('bottom', text='Time [s]', color='gray')
            self.curve_siggen.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Maximum)
            self.curve_siggen.autoRangeX = True
            self.curve_siggen.autoRangeY = True
            self.curve_siggen.showXGrid = True
            self.curve_siggen.showYGrid = True
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

            self.tab_siggen.addTab(defcurve, 'Default Curve')

        layout = QGridLayout()
        layout.setContentsMargins(0, 6, 0, 0)
        layout.addWidget(self.tab_siggen, 0, 0)
        return layout

    def _iocModeLayout(self):
        idff_mode_sel = self._prefixed_psname + ':IDFFMode-Sel'
        idff_mode_sts = self._prefixed_psname + ':IDFFMode-Sts'

        idff_mode_label = QLabel('IDFF', self)
        idff_mode_btn = PyDMStateButton(self, idff_mode_sel)
        idff_mode_led = SiriusLedState(self, idff_mode_sts)

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setColumnStretch(2, 1)
        layout.addWidget(idff_mode_label, 0, 0, Qt.AlignRight)
        layout.addWidget(idff_mode_btn, 0, 1, Qt.AlignHCenter)
        layout.addWidget(idff_mode_led, 0, 2)
        return layout

    def _genParamsLayout(self):
        queue_size_ca = self._prefixed_psname + ':PRUCtrlQueueSize-Mon'
        queue_size_label = QLabel('IOC Queue Size', self)
        queue_size_rb_label = SiriusLabel(self, queue_size_ca)

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

    def _wfmplotLayout(self):
        # graph
        self.wfm_graph = SiriusWaveformPlot()
        self.wfm_graph.setObjectName('graph')
        self.wfm_graph.setStyleSheet(
            '#graph{max-height:15em; max-width:16.5em;}')
        self.wfm_graph.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Maximum)
        self.wfm_graph.autoRangeX = True
        self.wfm_graph.autoRangeY = True
        self.wfm_graph.showXGrid = True
        self.wfm_graph.showYGrid = True
        self.wfm_graph.setLabel('left', text='Current [A]', color='gray')
        self.wfm_graph.setLabel('bottom', text='Time [s]')
        self.wfm_graph.plotItem.ctrl.fftCheck.toggled.connect(
            self._wfmUpdAxisLabel)
        self.wfm_graph.setBackgroundColor(QColor(255, 255, 255))

        # nrpts label
        self.wfm_nrpts_lb = QLabel('Nrpts (SP|RB|Ref-Mon|Mon):', self)
        self.wfm_nrpts_lb.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Maximum)

        # checkbox layout
        hbox_show = QHBoxLayout()
        hbox_show.setSpacing(9)

        # create auxiliary channels
        self._scopedur_ch_rb = SiriusConnectionSignal(
            self._prefixed_psname + ':ScopeDuration-RB')
        self._scopefreq_ch_rb = SiriusConnectionSignal(
            self._prefixed_psname + ':ScopeFreq-RB')
        self._wfmfreq_ch_rb = SiriusConnectionSignal(
            self._prefixed_psname + ':ParamWfmRefFreq-Cte')

        # fill graph, label and show layout
        self._wfm_chs, self._wfm_nrpts = dict(), dict()
        self._wfm_curves, self._wfm_show_cbs = dict(), dict()
        suf2color = {
            '-SP': 'red',
            '-RB': 'blue',
            'Ref-Mon': 'green',
            '-Mon': 'black',
        }
        for idx, suf in enumerate(suf2color):
            propty = 'Wfm' + suf
            color = suf2color[suf]
            channel = self._prefixed_psname + ':' + propty

            # initialize nrpts
            self._wfm_nrpts[suf] = 0

            # create channel to listen curve updates
            self._wfm_chs[suf] = SiriusConnectionSignal(channel)

            # listen to curve channel to update NrPts label
            self._wfm_chs[suf].new_value_signal[_np.ndarray].connect(
                self._update_wfm_nrpts_label)

            # add curve to wfm_graph
            self.wfm_graph.addChannel(
                y_channel=channel, name=propty, color=color, lineWidth=2)
            curve = self.wfm_graph.curveAtIndex(idx)

            # change xdata to show time indices according to ScopeDuration-RB
            curvetype = 'scope' if propty == 'Wfm-Mon' else 'wfm'
            self._scopedur_ch_rb.new_value_signal[float].connect(
                _part(self._wfmTimeData, propty))
            self._wfm_chs[suf].new_value_signal[_np.ndarray].connect(
                _part(self._wfmTimeData, propty))
            # reimplement fourier transform to use ScopeFreq-RB
            curve._fourierTransform = _part(self._wfmFourierData, curvetype)
            self._wfm_curves[propty] = curve

            # fill checkbox layout
            cbx = QCheckBox(suf.strip('-'))
            cbx.setChecked(True)
            cbx.setStyleSheet('color: '+color+';')
            cbx.stateChanged.connect(self._wfm_curves[propty].setVisible)
            self._wfm_show_cbs[propty] = cbx
            hbox_show.addWidget(cbx)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.wfm_graph)
        layout.addWidget(self.wfm_nrpts_lb)
        layout.addLayout(hbox_show)
        return layout

    def _wfmparamsLayout(self):
        # --- scope groupbox ----

        src_sp = self._prefixed_psname + ':ScopeSrcAddr-SP'
        src_rb = self._prefixed_psname + ':ScopeSrcAddr-RB'
        freq_sp = self._prefixed_psname + ':ScopeFreq-SP'
        freq_rb = self._prefixed_psname + ':ScopeFreq-RB'
        dur_sp = self._prefixed_psname + ':ScopeDuration-SP'
        dur_rb = self._prefixed_psname + ':ScopeDuration-RB'

        self.scope_src_label = QLabel('Source', self)
        self.scope_src_sp_sb = SiriusHexaSpinbox(self, src_sp)
        self.scope_src_rb_lb = SiriusLabel(self, src_rb)
        self.scope_src_rb_lb.displayFormat = SiriusLabel.DisplayFormat.Hex

        self.scope_freq_label = QLabel('Frequency [Hz]', self)
        self.scope_freq_sp_sb = SiriusSpinbox(self, freq_sp)
        self.scope_freq_rb_lb = SiriusLabel(self, freq_rb, keep_unit=True)
        self.scope_freq_rb_lb.showUnits = True

        self.scope_dur_label = QLabel('Duration [s]', self)
        self.scope_dur_sp_sb = SiriusSpinbox(self, dur_sp)
        self.scope_dur_rb_lb = SiriusLabel(self, dur_rb)
        self.scope_dur_rb_lb.showUnits = True

        layout_scope = QGridLayout()
        layout_scope.setAlignment(Qt.AlignTop)
        layout_scope.setContentsMargins(6, 6, 3, 3)
        layout_scope.addWidget(self.scope_src_label, 0, 0, Qt.AlignRight)
        layout_scope.addWidget(self.scope_src_rb_lb, 0, 3)
        layout_scope.addWidget(
            self.scope_freq_label, 1, 0, 1, 2, Qt.AlignRight)
        layout_scope.addWidget(self.scope_freq_sp_sb, 1, 2)
        layout_scope.addWidget(self.scope_freq_rb_lb, 1, 3)
        layout_scope.addWidget(self.scope_dur_label, 2, 0, 1, 2, Qt.AlignRight)
        layout_scope.addWidget(self.scope_dur_sp_sb, 2, 2)
        layout_scope.addWidget(self.scope_dur_rb_lb, 2, 3)

        try:
            self.scope_src_sp_cb = SiriusStringComboBox(
                self, src_sp, items=get_ps_scopesourcemap(self._psname))
            self.scope_src_sp_opt = QComboBox(self)
            self.scope_src_sp_opt.addItems(['[list]', '[0x]'])
            self.scope_src_sp_opt.currentIndexChanged.connect(
                self.scope_src_sp_cb.setHidden)
            self.scope_src_sp_opt.currentIndexChanged.connect(
                self.scope_src_sp_sb.setVisible)

            self.scope_src_sp_sb.setVisible(False)
            layout_scope.addWidget(self.scope_src_label, 0, 0, Qt.AlignRight)
            layout_scope.addWidget(self.scope_src_sp_opt, 0, 1)
            layout_scope.addWidget(self.scope_src_sp_cb, 0, 2)
            layout_scope.addWidget(self.scope_src_sp_sb, 0, 2)
        except KeyError:
            layout_scope.addWidget(
                self.scope_src_label, 0, 0, 1, 2, Qt.AlignRight)
            layout_scope.addWidget(self.scope_src_sp_sb, 0, 2)

        self.scope_box = QGroupBox("Scope")
        self.scope_box.setObjectName("Scope")
        self.scope_box.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Maximum)
        self.scope_box.setLayout(layout_scope)

        # --- wfm groupbox ---

        wfm_selected_mon = self._prefixed_psname + ':WfmSelected-Mon'
        wfm_syncmode_sel = self._prefixed_psname + ':WfmSyncMode-Sel'
        wfm_syncmode_sts = self._prefixed_psname + ':WfmSyncMode-Sts'
        wfm_freq_sp = self._prefixed_psname + ':WfmFreq-SP'
        wfm_freq_rb = self._prefixed_psname + ':WfmFreq-RB'
        wfm_gain_sp = self._prefixed_psname + ':WfmGain-SP'
        wfm_gain_rb = self._prefixed_psname + ':WfmGain-RB'
        wfm_offset_sp = self._prefixed_psname + ':WfmOffset-SP'
        wfm_offset_rb = self._prefixed_psname + ':WfmOffset-RB'

        wfm_index_ca = self._prefixed_psname + ':WfmIndex-Mon'
        wfm_count_ca = self._prefixed_psname + ':WfmSyncPulseCount-Mon'
        wfm_updateauto_ca = self._prefixed_psname + ':WfmUpdateAuto-Sts'
        wfm_updateauto_sel = self._prefixed_psname + ':WfmUpdateAuto-Sel'

        self.wfm_selected_label = QLabel('Wfm Selected', self)
        self.wfm_selected_mon = SiriusLabel(self, wfm_selected_mon)

        self.wfm_syncmode_label = QLabel('Wfm SyncMode', self)
        self.wfm_syncmode_sel_cb = PyDMEnumComboBox(self, wfm_syncmode_sel)
        self.wfm_syncmode_sts_lb = SiriusLabel(self, wfm_syncmode_sts)
        self.wfm_syncmode_sts_lb.showUnits = True

        self.wfm_freq_label = QLabel('Wfm Frequency [Hz]', self)
        self.wfm_freq_sp_sb = SiriusSpinbox(self, wfm_freq_sp)
        self.wfm_freq_rb_lb = SiriusLabel(self, wfm_freq_rb, keep_unit=True)
        self.wfm_freq_rb_lb.showUnits = True

        self.wfm_gain_label = QLabel('Wfm Gain', self)
        self.wfm_gain_sp_sb = SiriusSpinbox(self, wfm_gain_sp)
        self.wfm_gain_rb_lb = SiriusLabel(self, wfm_gain_rb)
        self.wfm_gain_rb_lb.showUnits = True

        self.wfm_offset_label = QLabel('Wfm Offset [A]', self)
        self.wfm_offset_sp_sb = SiriusSpinbox(self, wfm_offset_sp)
        self.wfm_offset_rb_lb = SiriusLabel(self, wfm_offset_rb)
        self.wfm_offset_rb_lb.showUnits = True

        wfm_index_label = QLabel('Wfm Index', self)
        wfm_index_rb_label = SiriusLabel(self, wfm_index_ca)
        wfm_count_label = QLabel('Wfm Pulse Count', self)
        wfm_count_rb_label = SiriusLabel(self, wfm_count_ca)
        wfm_updateauto_label = QLabel('Wfm UpdateAuto', self)
        wfm_updateauto_sts_led = SiriusLedState(self, wfm_updateauto_ca)
        wfm_updateauto_btn = PyDMStateButton(self, wfm_updateauto_sel)

        layout_wfm = QGridLayout()
        layout_wfm.setAlignment(Qt.AlignTop)
        layout_wfm.setContentsMargins(6, 6, 3, 3)

        layout_wfm.addWidget(
            self.wfm_selected_label, 0, 0, Qt.AlignRight)
        layout_wfm.addWidget(self.wfm_selected_mon, 0, 1, 1, 2)
        layout_wfm.addWidget(
            self.wfm_syncmode_label, 1, 0, Qt.AlignRight)
        layout_wfm.addWidget(self.wfm_syncmode_sel_cb, 1, 1)
        layout_wfm.addWidget(self.wfm_syncmode_sts_lb, 1, 2)
        layout_wfm.addWidget(self.wfm_freq_label, 2, 0, Qt.AlignRight)
        layout_wfm.addWidget(self.wfm_freq_sp_sb, 2, 1)
        layout_wfm.addWidget(self.wfm_freq_rb_lb, 2, 2)
        layout_wfm.addWidget(self.wfm_gain_label, 3, 0, Qt.AlignRight)
        layout_wfm.addWidget(self.wfm_gain_sp_sb, 3, 1)
        layout_wfm.addWidget(self.wfm_gain_rb_lb, 3, 2)
        layout_wfm.addWidget(self.wfm_offset_label, 4, 0, Qt.AlignRight)
        layout_wfm.addWidget(self.wfm_offset_sp_sb, 4, 1)
        layout_wfm.addWidget(self.wfm_offset_rb_lb, 4, 2)

        layout_wfm.addWidget(wfm_index_label, 5, 0, Qt.AlignRight)
        layout_wfm.addWidget(wfm_index_rb_label, 5, 1)
        layout_wfm.addWidget(wfm_count_label, 6, 0, Qt.AlignRight)
        layout_wfm.addWidget(wfm_count_rb_label, 6, 1)
        layout_wfm.addWidget(wfm_updateauto_label, 7, 0, Qt.AlignRight)
        layout_wfm.addWidget(wfm_updateauto_btn, 7, 1, Qt.AlignHCenter)
        layout_wfm.addWidget(wfm_updateauto_sts_led, 7, 2)

        self.wfm_box = QGroupBox("Wfm")
        self.wfm_box.setObjectName("Wfm")
        self.wfm_box.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Maximum)
        self.wfm_box.setLayout(layout_wfm)

        # --- wfmlayout ---

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(6, 6, 3, 3)
        layout.addWidget(self.scope_box, 1, 1)
        layout.addWidget(self.wfm_box, 2, 1)
        return layout

    def _update_wfm_nrpts_label(self, value):
        pvtype = self.sender().address.split('Wfm')[-1]
        self._wfm_nrpts[pvtype] = len(value)
        self.wfm_nrpts_lb.setText(
            "Nrpts (SP|RB|Ref-Mon|Mon): {}|{}|{}|{}".format(
                self._wfm_nrpts['-SP'],
                self._wfm_nrpts['-RB'],
                self._wfm_nrpts['Ref-Mon'],
                self._wfm_nrpts['-Mon']))

    def _wfmUpdAxisLabel(self, state):
        xlabel = 'Frequency [Hz]' if state else 'Time [s]'
        self.wfm_graph.setLabel('bottom', text=xlabel)

    def _wfmTimeData(self, propty, value):
        if value is None:
            return
        channel = self.sender().address
        curve = self._wfm_curves[propty]
        if 'Duration' in channel:
            duration = value
            latest_y = curve.latest_y
        else:
            duration = self._scopedur_ch_rb.value
            latest_y = value
        if latest_y is None:
            return
        curve.receiveXWaveform(_np.linspace(0, duration, len(latest_y)))
        curve.redrawCurve()

    def _wfmFourierData(self, curvetype, x, y):
        """Perform Fourier transform.

        This code is a copy of pyqtgraph.graphicsItems.PlotDataItem, just
        changing the sampling frequency to the ScopeFreq-RB value.
        """
        # If x values are not sampled uniformly,
        # then use np.interp to resample before taking fft.
        dx = _np.diff(x)
        uniform = not _np.any(_np.abs(dx-dx[0]) > (abs(dx[0]) / 1000.))
        if not uniform:
            x2 = _np.linspace(x[0], x[-1], len(x))
            y = _np.interp(x2, x, y)
            x = x2

        n = y.size
        f = _np.fft.rfft(y) / n
        # Diff: use scope frequency
        chfreq = self._scopefreq_ch_rb if curvetype else self._wfmfreq_ch_rb
        freq = chfreq.value
        if isinstance(freq, _np.ndarray):
            freq = freq[0]
        d = 1./freq if freq is not None else 1
        x = _np.fft.rfftfreq(n, d)
        y = _np.abs(f)
        return x, y


class LIPSDetailWidget(_BaseDetailWidget):
    """."""

    def __init__(self, psname, parent=None):
        """Class constructor."""
        super(LIPSDetailWidget, self).__init__(psname, parent=parent)
        self._setup_ui()
        self.setStyleSheet(self.StyleSheet)

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
        self.current_box.setLayout(self._currentLayout(has_refmon=False))
        if self._metric:
            self.metric_box.setLayout(self._metricLayout(has_refmon=False))

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
        self.version_cte = SiriusLabel(
            self, self._prefixed_psname + ":Version-Cte")
        self.version_cte.setObjectName("version_cte_label")
        self.version_cte.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Maximum)

        self.tstamp_boot_label = QLabel('IOC Boot')
        self.tstamp_boot_label.setObjectName("tstamp_label")
        self.tstamp_boot_label.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Maximum)
        self.tstamp_boot_cte = SiriusLabel(
            self, self._prefixed_psname + ":TimestampBoot-Cte")
        self.tstamp_boot_cte.setObjectName("tstamp_cte_label")
        self.tstamp_boot_cte.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Maximum)
        self.tstamp_boot_cte_ch = SiriusConnectionSignal(
            self._prefixed_psname + ":TimestampBoot-Cte")
        self.tstamp_boot_cte_ch.new_value_signal[float].connect(
            self._tstamp_boot_cte_met)

        self.tstamp_update_label = QLabel('IOC Update')
        self.tstamp_update_label.setObjectName("tstampupdate_label")
        self.tstamp_update_label.setSizePolicy(
            QSzPlcy.Minimum, QSzPlcy.Maximum)
        self.tstamp_update_mon = SiriusLabel(
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
        self.conn_sts = SiriusLabel(
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
        layout.setContentsMargins(6, 6, 3, 3)
        layout.addWidget(self.intlk_bt, 0, 0)
        layout.addWidget(QLabel('Intlk', self, alignment=Qt.AlignCenter), 0, 1)
        layout.addWidget(self.intlk_led, 0, 2)
        return layout

    def _paramsLayout(self):
        temp_label = QLabel('Temperature', self)
        self.temp_mon_label = SiriusLabel(
            self, self._prefixed_psname + ':Temperature-Mon')

        loadv_label = QLabel('Load Voltage', self)
        self.loadv_mon_label = SiriusLabel(
            self, self._prefixed_psname + ':LoadVoltage-Mon')

        busv_label = QLabel('Bus Voltage', self)
        self.busv_mon_label = SiriusLabel(
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
        self.opmode_rb = SiriusLabel(
            self, self._prefixed_psname + ":OpMode-Sts")
        self.opmode_rb.setObjectName("opmode1_rb_label")
        self.ctrlmode_led = SiriusLedAlert(
            self, self._prefixed_psname + ":CtrlMode-Mon")
        self.ctrlmode_label = SiriusLabel(
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

        self.current_sp_widget = PyDMSpinboxScrollbar(
            self, self._prefixed_psname + ":Voltage-SP")
        self.current_rb_val = SiriusLabel(
            self, self._prefixed_psname+":Voltage-RB", keep_unit=True)
        self.current_rb_val.showUnits = True
        self.current_rb_val.precFromPV = True
        self.current_ref_val = SiriusLabel(
            self, self._prefixed_psname+":VoltageRef-Mon", keep_unit=True)
        self.current_ref_val.showUnits = True
        self.current_ref_val.precFromPV = True
        self.current_mon_val = SiriusLabel(
            self, self._prefixed_psname+":Voltage-Mon", keep_unit=True)
        self.current_mon_val.showUnits = True
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
        layout = QFormLayout()
        for auxmeas in self._auxmeasures:
            text = auxmeas.split('-')[0]
            label = SiriusLabel(
                self, self._prefixed_psname + ':' + auxmeas)
            label.showUnits = True
            layout.addRow(text, label)

        pbprm = QPushButton(qta.icon('mdi.open-in-new'),
                            'Parameters', self)
        util.connect_window(
            pbprm, PSParamsWidget, self, psname=self._psname,
            params=self._params)
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

        self.cap_bank_sp_widget = PyDMSpinboxScrollbar(
            self, self._prefixed_psname + ":CapacitorBankVoltage-SP")
        self.cap_bank_rb_val = SiriusLabel(
            self, self._prefixed_psname + ":CapacitorBankVoltage-RB",
            keep_unit=True)
        self.cap_bank_rb_val.showUnits = True
        self.cap_bank_ref_val = SiriusLabel(
            self, self._prefixed_psname + ":CapacitorBankVoltageRef-Mon",
            keep_unit=True)
        self.cap_bank_ref_val.showUnits = True
        self.cap_bank_mon_val = SiriusLabel(
            self, self._prefixed_psname + ":CapacitorBankVoltage-Mon",
            keep_unit=True)
        self.cap_bank_mon_val.showUnits = True

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
            pydmlbl = SiriusLabel(
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


class FastCorrPSDetailWidget(_BaseDetailWidget):
    def __init__(self, psname, parent=None):
        """Class constructor."""
        super(FastCorrPSDetailWidget, self).__init__(psname, parent=parent)
        self._psmodel = 'FOFB_PS'
        self._pstype = 'si-corrector-fc1-ch'
        self._db = get_ps_propty_database(self._psmodel, self._pstype)
        self._setup_ui()

    def _setup_ui(self):
        # Group boxes that compose the widget
        self.opmode_box = QGroupBox('OpMode')
        self.opmode_box.setObjectName('operation_mode')
        self.pwrstate_box = QGroupBox('PwrState')
        self.pwrstate_box.setObjectName('power_state')
        self.interlock_box = QGroupBox('Interlock')
        self.interlock_box.setObjectName('interlock')
        self.analogtab = QTabWidget()
        self.analogtab.setObjectName(self._psname.sec+'Tab')
        self.current_box = QWidget()
        self.current_box.setObjectName('current')
        self.analogtab.addTab(self.current_box, 'Current [A]')
        self.current_raw_box = QWidget()
        self.current_raw_box.setObjectName('current')
        self.analogtab.addTab(self.current_raw_box, 'Curr.[Raw]')
        self.voltage_box = QWidget()
        self.voltage_box.setObjectName('voltage')
        self.analogtab.addTab(self.voltage_box, 'Volt.[V]')
        self.voltage_raw_box = QWidget()
        self.voltage_raw_box.setObjectName('voltage')
        self.analogtab.addTab(self.voltage_raw_box, 'Volt.[Raw]')
        if self._metric:
            self.metric_box = QGroupBox(self._metric)
            self.metric_box.setObjectName('metric')
        self.paramstab = QTabWidget()
        self.paramstab.setObjectName(self._psname.sec+'Tab')
        self.currloop_box = QWidget()
        self.currloop_box.setObjectName('currloop_box')
        self.paramstab.addTab(self.currloop_box, 'Current Loop Controls')
        self.fofbctrl_box = QWidget()
        self.fofbctrl_box.setObjectName('fofbctrl_box')
        self.paramstab.addTab(self.fofbctrl_box, 'FOFB Parameters')

        # Set group boxes layouts
        self.opmode_box.setLayout(self._opModeLayout())
        self.pwrstate_box.setLayout(self._powerStateLayout())
        self.interlock_box.setLayout(self._interlockLayout())
        self.current_box.setLayout(self._currentLayout(prec=6))
        self.current_raw_box.setLayout(self._currentRawLayout())
        self.voltage_box.setLayout(self._voltageLayout())
        self.voltage_raw_box.setLayout(self._voltageRawLayout())
        if self._metric:
            self.metric_box.setLayout(self._metricLayout())
        self.currloop_box.setLayout(self._currLoopLayout())
        self.fofbctrl_box.setLayout(self._fofbctrlLayout())

        self.setStyleSheet(
            '#'+self._psname.sec+'Tab::pane {'
            ' border-left: 2px solid gray;'
            ' border-bottom: 2px solid gray;'
            ' border-right: 2px solid gray;}')

        # Add group boxes to laytout
        self.layout = self._setWidgetLayout()

        # Set widget layout
        self.setLayout(self.layout)

    def _setWidgetLayout(self):
        lay1 = QGridLayout()
        lay1.setContentsMargins(0, 0, 0, 0)
        lay1.addWidget(self.opmode_box, 0, 0)
        lay1.addWidget(self.pwrstate_box, 0, 1)
        lay1.addWidget(self.interlock_box, 1, 0, 1, 2)

        lay2 = QVBoxLayout()
        lay2.setContentsMargins(0, 0, 0, 0)
        lay2.addWidget(self.analogtab)
        if self._metric:
            lay2.addWidget(self.metric_box)

        boxes_layout = QGridLayout()
        boxes_layout.addLayout(lay1, 0, 0)
        boxes_layout.addLayout(lay2, 0, 1)
        boxes_layout.addWidget(self.paramstab, 2, 0, 1, 2)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("<h2>" + self._psname + "</h2>", self))
        layout.addLayout(boxes_layout)
        return layout

    def _opModeLayout(self):
        self.opmode_sp = PyDMEnumComboBox(
            self, self._prefixed_psname + ":OpMode-Sel")
        self.opmode_sp.setObjectName("opmode_sp_cbox")
        self.opmode_rb = SiriusLabel(
            self, self._prefixed_psname + ":OpMode-Sts")
        self.opmode_rb.setObjectName("opmode_rb_label")

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.opmode_sp, 0, 0, Qt.AlignHCenter)
        layout.addWidget(self.opmode_rb, 1, 0, Qt.AlignHCenter)
        return layout

    def _currentRawLayout(self):
        current_sp_label = QLabel("Setpoint")
        current_rb_label = QLabel("Readback")
        current_ref_label = QLabel("Ref Mon")
        current_mon_label = QLabel("Mon")

        self.current_raw_sp = PyDMSpinboxScrollbar(
            self, self._prefixed_psname + ":CurrentRaw-SP")
        self.current_raw_rb = SiriusLabel(
            self, self._prefixed_psname+":CurrentRaw-RB")
        self.current_raw_ref = SiriusLabel(
            self, self._prefixed_psname+":CurrentRawRef-Mon")
        self.current_raw_mon = SiriusLabel(
            self, self._prefixed_psname+":CurrentRaw-Mon")

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(current_sp_label, 0, 0, Qt.AlignRight)
        layout.addWidget(self.current_raw_sp, 0, 1)
        layout.addWidget(current_rb_label, 1, 0, Qt.AlignRight)
        layout.addWidget(self.current_raw_rb, 1, 1)
        layout.addWidget(current_ref_label, 2, 0, Qt.AlignRight)
        layout.addWidget(self.current_raw_ref, 2, 1)
        layout.addWidget(current_mon_label, 3, 0, Qt.AlignRight)
        layout.addWidget(self.current_raw_mon, 3, 1)
        layout.setColumnStretch(2, 1)
        return layout

    def _voltageLayout(self):
        voltage_sp_label = QLabel("Setpoint")
        voltage_rb_label = QLabel("Readback")
        voltage_mn_label = QLabel("Mon")

        self.voltage_sp = PyDMLinEditScrollbar(
            self, self._prefixed_psname + ":Voltage-SP")
        self.voltage_sp.lineedit.precisionFromPV = False
        self.voltage_sp.lineedit.precision = 6
        self.voltage_rb = SiriusLabel(
            self, self._prefixed_psname+":Voltage-RB", keep_unit=True)
        self.voltage_rb.precisionFromPV = False
        self.voltage_rb.precision = 6
        self.voltage_rb.showUnits = True
        self.voltage_mn = SiriusLabel(
            self, self._prefixed_psname+":Voltage-Mon", keep_unit=True)
        self.voltage_mn.precisionFromPV = False
        self.voltage_mn.precision = 6
        self.voltage_mn.showUnits = True

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(voltage_sp_label, 0, 0, Qt.AlignRight)
        layout.addWidget(self.voltage_sp, 0, 1)
        layout.addWidget(voltage_rb_label, 1, 0, Qt.AlignRight)
        layout.addWidget(self.voltage_rb, 1, 1)
        layout.addWidget(voltage_mn_label, 2, 0, Qt.AlignRight)
        layout.addWidget(self.voltage_mn, 2, 1)
        layout.setColumnStretch(2, 1)
        return layout

    def _voltageRawLayout(self):
        voltage_sp_label = QLabel("Setpoint")
        voltage_rb_label = QLabel("Readback")
        voltage_mn_label = QLabel("Mon")

        self.voltage_raw_sp = PyDMLinEditScrollbar(
            self, self._prefixed_psname + ":VoltageRaw-SP")
        self.voltage_raw_rb = SiriusLabel(
            self, self._prefixed_psname+":VoltageRaw-RB", keep_unit=True)
        self.voltage_rb.showUnits = True
        self.voltage_raw_mn = SiriusLabel(
            self, self._prefixed_psname+":VoltageRaw-Mon", keep_unit=True)
        self.voltage_raw_mn.showUnits = True

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(voltage_sp_label, 0, 0, Qt.AlignRight)
        layout.addWidget(self.voltage_raw_sp, 0, 1)
        layout.addWidget(voltage_rb_label, 1, 0, Qt.AlignRight)
        layout.addWidget(self.voltage_raw_rb, 1, 1)
        layout.addWidget(voltage_mn_label, 2, 0, Qt.AlignRight)
        layout.addWidget(self.voltage_raw_mn, 2, 1)
        layout.setColumnStretch(2, 1)
        return layout

    def _interlockLayout(self):
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignCenter)

        row = 0
        for pvn in ['AlarmsAmp', 'AlarmsAmpLtc']:
            alarm_label = QLabel(pvn, self, alignment=Qt.AlignCenter)
            alarm_bt = QPushButton(qta.icon('fa5s.list-ul'), '', self)
            alarm_bt.setObjectName('alarm_bt')
            alarm_bt.setStyleSheet(
                '#alarm_bt{min-width:25px; max-width:25px; icon-size:20px;}')

            util.connect_window(
                alarm_bt, InterlockWindow, self,
                devname=self._psname, database=self._db, interlock=pvn)
            alarm_led = SiriusLedAlert(
                parent=self, init_channel=self._prefixed_psname+':'+pvn+'-Mon')
            alarm_led.onColor = alarm_led.Yellow

            layout.addWidget(alarm_bt, row, 0)
            layout.addWidget(alarm_label, row, 1)
            layout.addWidget(alarm_led, row, 2)
            row += 1

        self.reset_bt = PyDMPushButton(
            parent=self, icon=qta.icon('fa5s.sync'), pressValue=1,
            init_channel=self._prefixed_psname + ":AlarmsAmpLtcRst-Cmd")
        self.reset_bt.setObjectName('reset_bt')
        self.reset_bt.setStyleSheet(
            '#reset_bt{min-width:25px; max-width:25px; icon-size:20px;}')
        layout.addWidget(self.reset_bt, row, 2)

        return layout

    def _currLoopLayout(self):
        # controls
        tabctrl = QTabWidget()
        tabctrl.setObjectName(self._psname.sec+'Tab')

        # # loop parameters
        ctlmode_lb = QLabel(
            'CurrLoopMode', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.ctlmode_cb = PyDMEnumComboBox(
            self, self._prefixed_psname + ':CurrLoopMode-Sel')
        self.ctlmode_lb = SiriusLabel(
            self, self._prefixed_psname + ':CurrLoopMode-Sts')

        ctlkp_lb = QLabel(
            'CurrLoopKp', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.ctlkp_sp = SiriusSpinbox(
            self, self._prefixed_psname + ':CurrLoopKp-SP')
        self.ctlkp_sp.limitsFromChannel = False
        self.ctlkp_sp.setMinimum(0.0)
        self.ctlkp_sp.setMaximum(2**31 - 1)
        self.ctlkp_rb = SiriusLabel(
            self, self._prefixed_psname + ':CurrLoopKp-RB')

        ctlti_lb = QLabel(
            'CurrLoopKi', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.ctlti_sp = SiriusSpinbox(
            self, self._prefixed_psname + ':CurrLoopKi-SP')
        self.ctlti_sp.limitsFromChannel = False
        self.ctlti_sp.setMinimum(0.0)
        self.ctlti_sp.setMaximum(2**31 - 1)
        self.ctlti_rb = SiriusLabel(
            self, self._prefixed_psname + ':CurrLoopKi-RB')

        cgain_lb = QLabel(
            'CurrGain', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.cgain_sp = SiriusSpinbox(
            self, self._prefixed_psname + ':CurrGain-SP')
        self.cgain_sp.precisionFromPV = False
        self.cgain_sp.precision = 8
        self.cgain_sp.limitsFromChannel = False
        self.cgain_sp.setMinimum(-1)
        self.cgain_sp.setMaximum(+1)
        self.cgain_rb = SiriusLabel(
            self, self._prefixed_psname + ':CurrGain-RB')
        self.cgain_rb.precisionFromPV = False
        self.cgain_rb.precision = 8

        coffs_lb = QLabel(
            'CurrOffset', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.coffs_sp = SiriusSpinbox(
            self, self._prefixed_psname + ':CurrOffset-SP')
        self.coffs_sp.limitsFromChannel = False
        self.coffs_sp.setMinimum(-100)
        self.coffs_sp.setMaximum(+100)
        self.coffs_rb = SiriusLabel(
            self, self._prefixed_psname + ':CurrOffset-RB')

        vgain_lb = QLabel(
            'VoltGain', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.vgain_sp = SiriusSpinbox(
            self, self._prefixed_psname + ':VoltGain-SP')
        self.vgain_sp.precisionFromPV = False
        self.vgain_sp.precision = 8
        self.vgain_sp.limitsFromChannel = False
        self.vgain_sp.setMinimum(-1)
        self.vgain_sp.setMaximum(+1)
        self.vgain_rb = SiriusLabel(
            self, self._prefixed_psname + ':VoltGain-RB')
        self.vgain_rb.precisionFromPV = False
        self.vgain_rb.precision = 8

        voffs_lb = QLabel(
            'VoltOffset', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.voffs_sp = SiriusSpinbox(
            self, self._prefixed_psname + ':VoltOffset-SP')
        self.voffs_sp.limitsFromChannel = False
        self.voffs_sp.setMinimum(-100)
        self.voffs_sp.setMaximum(+100)
        self.voffs_rb = SiriusLabel(
            self, self._prefixed_psname + ':VoltOffset-RB')

        widgetparms = QWidget()
        lay = QGridLayout(widgetparms)
        lay.setAlignment(Qt.AlignTop)
        lay.addWidget(ctlmode_lb, 0, 0, Qt.AlignRight)
        lay.addWidget(self.ctlmode_cb, 0, 1)
        lay.addWidget(self.ctlmode_lb, 0, 2)
        lay.addWidget(ctlkp_lb, 1, 0, Qt.AlignRight)
        lay.addWidget(self.ctlkp_sp, 1, 1)
        lay.addWidget(self.ctlkp_rb, 1, 2)
        lay.addWidget(ctlti_lb, 2, 0, Qt.AlignRight)
        lay.addWidget(self.ctlti_sp, 2, 1)
        lay.addWidget(self.ctlti_rb, 2, 2)
        lay.addWidget(cgain_lb, 3, 0, Qt.AlignRight)
        lay.addWidget(self.cgain_sp, 3, 1)
        lay.addWidget(self.cgain_rb, 3, 2)
        lay.addWidget(coffs_lb, 4, 0, Qt.AlignRight)
        lay.addWidget(self.coffs_sp, 4, 1)
        lay.addWidget(self.coffs_rb, 4, 2)
        lay.addWidget(vgain_lb, 5, 0, Qt.AlignRight)
        lay.addWidget(self.vgain_sp, 5, 1)
        lay.addWidget(self.vgain_rb, 5, 2)
        lay.addWidget(voffs_lb, 6, 0, Qt.AlignRight)
        lay.addWidget(self.voffs_sp, 6, 1)
        lay.addWidget(self.voffs_rb, 6, 2)
        tabctrl.addTab(widgetparms, 'Parameters')

        # # tests
        testlima_lb = QLabel(
            'Limit A', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.testlima_sp = SiriusSpinbox(
            self, self._prefixed_psname + ':TestLimA-SP')
        self.testlima_rb = SiriusLabel(
            self, self._prefixed_psname + ':TestLimA-RB')

        testlimb_lb = QLabel(
            'Limit B', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.testlimb_sp = SiriusSpinbox(
            self, self._prefixed_psname + ':TestLimB-SP')
        self.testlimb_rb = SiriusLabel(
            self, self._prefixed_psname + ':TestLimB-RB')

        testwaveper_lb = QLabel(
            'Wave Period', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.testwaveper_sp = SiriusSpinbox(
            self, self._prefixed_psname + ':TestWavePeriod-SP')
        self.testwaveper_rb = SiriusLabel(
            self, self._prefixed_psname + ':TestWavePeriod-RB')

        widgettest = QWidget()
        lay = QGridLayout(widgettest)
        lay.setAlignment(Qt.AlignTop)
        lay.addWidget(testlima_lb, 0, 0, Qt.AlignRight)
        lay.addWidget(self.testlima_sp, 0, 1)
        lay.addWidget(self.testlima_rb, 0, 2)
        lay.addWidget(testlimb_lb, 1, 0, Qt.AlignRight)
        lay.addWidget(self.testlimb_sp, 1, 1)
        lay.addWidget(self.testlimb_rb, 1, 2)
        lay.addWidget(testwaveper_lb, 2, 0, Qt.AlignRight)
        lay.addWidget(self.testwaveper_sp, 2, 1)
        lay.addWidget(self.testwaveper_rb, 2, 2)
        tabctrl.addTab(widgettest, 'Tests')

        # monitoring
        tabmon = QTabWidget(self)
        tabmon.setObjectName(self._psname.sec+'Tab')

        # # current waveform
        self.graph_curr = SiriusWaveformPlot()
        self.graph_curr.addChannel(
            y_channel=self._prefixed_psname + ':LAMPCurrentData',
            name='Current', color='blue', lineWidth=1)
        self.graph_curr.addChannel(
            y_channel=self._prefixed_psname + ':LAMPCurrentRefData',
            name='CurrentRef', color='green', lineWidth=1)
        # self.graph_curr.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Maximum)
        self.graph_curr.autoRangeX = True
        self.graph_curr.autoRangeY = True
        self.graph_curr.showXGrid = True
        self.graph_curr.showYGrid = True
        self.graph_curr.title = 'Current'
        self.graph_curr.setLabel('left', text='Current [A]', color='gray')
        self.graph_curr.setLabel('bottom', text='Index')
        self.graph_curr.setBackgroundColor(QColor(255, 255, 255))
        tabmon.addTab(self.graph_curr, 'Current Acq.')

        # # voltage waveform
        self.graph_volt = SiriusWaveformPlot()
        self.graph_volt.addChannel(
            y_channel=self._prefixed_psname + ':LAMPVoltageData',
            name='Voltage', color='blue', lineWidth=1)
        # self.graph_volt.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Maximum)
        self.graph_volt.autoRangeX = True
        self.graph_volt.autoRangeY = True
        self.graph_volt.showXGrid = True
        self.graph_volt.showYGrid = True
        self.graph_volt.title = 'Voltage'
        self.graph_volt.setLabel('left', text='Voltage [V]', color='gray')
        self.graph_volt.setLabel('bottom', text='Index')
        self.graph_volt.setBackgroundColor(QColor(255, 255, 255))
        tabmon.addTab(self.graph_volt, 'Voltage Acq.')

        # # current history
        self.graph_chist = SiriusTimePlot()
        timespan = 5*60  # 5min
        self.graph_chist.timeSpan = timespan  # [s]
        self.graph_chist.bufferSize = 5*timespan  # [max 5 samples/s]
        pvsuf2color = {
            '-SP': 'red',
            '-RB': 'blue',
            'Ref-Mon': 'green',
            '-Mon': 'black',
        }
        hbox_show = QHBoxLayout()
        hbox_show.setSpacing(9)
        for pvs, color in pvsuf2color.items():
            pvname = self._prefixed_psname.substitute(propty='Current'+pvs)
            legtxt = pvs.replace('-', '')
            self.graph_chist.addYChannel(
                y_channel=pvname, name=legtxt, color=color, lineWidth=1)
            curve = self.graph_chist.curveAtIndex(-1)
            cb_show = QCheckBox(legtxt)
            cb_show.setChecked(True)
            cb_show.setStyleSheet('color: '+color+';')
            cb_show.stateChanged.connect(curve.setVisible)
            hbox_show.addWidget(cb_show)
        self.graph_chist.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Maximum)
        self.graph_chist.autoRangeX = True
        self.graph_chist.autoRangeY = True
        self.graph_chist.showXGrid = True
        self.graph_chist.showYGrid = True
        self.graph_chist.timeSpan = 30  # [s]
        self.graph_chist.title = 'Current Mean History'
        self.graph_chist.setLabel('left', text='Current [A]', color='gray')
        self.graph_chist.showLegend = True
        self.graph_chist.setBackgroundColor(QColor(255, 255, 255))
        wid_currhist = QWidget()
        lay_currhist = QVBoxLayout(wid_currhist)
        lay_currhist.setContentsMargins(0, 0, 0, 0)
        lay_currhist.addWidget(self.graph_chist)
        lay_currhist.addLayout(hbox_show)
        tabmon.addTab(wid_currhist, 'Current Hist.')
        tabmon.setCurrentIndex(2)

        layout = QHBoxLayout()
        layout.addWidget(tabctrl)
        layout.addWidget(tabmon)
        return layout

    def _fofbctrlLayout(self):
        # controls
        fofbacc_lb = QLabel(
            'Accumulator', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.fofbacc_mon = SiriusLabel(
            self, self._prefixed_psname + ':FOFBAcc-Mon')
        self.fofbacc_mon.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Maximum)

        fofbaccgain_lb = QLabel(
            'Acc. Gain', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.fofbaccgain_sp = PyDMLineEdit(
            self, self._prefixed_psname + ':FOFBAccGain-SP')
        self.fofbaccgain_sp.precisionFromPV = False
        self.fofbaccgain_sp.precision = 8
        self.fofbaccgain_rb = SiriusLabel(
            self, self._prefixed_psname + ':FOFBAccGain-RB')
        self.fofbaccgain_rb.precisionFromPV = False
        self.fofbaccgain_rb.precision = 8

        fofbaccfreeze_lb = QLabel(
            'Acc. Freeze', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.fofbaccfreeze_sp = PyDMEnumComboBox(
            self, self._prefixed_psname + ':FOFBAccFreeze-Sel')
        self.fofbaccfreeze_rb = SiriusLabel(
            self, self._prefixed_psname + ':FOFBAccFreeze-Sts')

        fofbaccclear_lb = QLabel(
            'Acc. Clear', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.fofbaccclear_bt = PyDMPushButton(
            parent=self, icon=qta.icon('mdi.sync'), pressValue=1,
            init_channel=self._prefixed_psname + ":FOFBAccClear-Cmd")
        self.fofbaccclear_bt.setObjectName('accclear_bt')
        self.fofbaccclear_bt.setStyleSheet(
            '#accclear_bt{min-width:25px; max-width:25px; icon-size:20px;}')

        fofbaccmaxsat_lb = QLabel(
            'Max. Sat. Current', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.fofbaccmaxsat_sp = SiriusSpinbox(
            self, self._prefixed_psname + ':FOFBAccSatMax-SP')
        self.fofbaccmaxsat_sp.precisionFromPV = False
        self.fofbaccmaxsat_sp.precision = 8
        self.fofbaccmaxsat_rb = SiriusLabel(
            self, self._prefixed_psname + ':FOFBAccSatMax-RB')
        self.fofbaccmaxsat_rb.precisionFromPV = False
        self.fofbaccmaxsat_rb.precision = 8

        fofbaccminsat_lb = QLabel(
            'Min. Sat. Current', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.fofbaccminsat_sp = SiriusSpinbox(
            self, self._prefixed_psname + ':FOFBAccSatMin-SP')
        self.fofbaccminsat_sp.precisionFromPV = False
        self.fofbaccminsat_sp.precision = 8
        self.fofbaccminsat_rb = SiriusLabel(
            self, self._prefixed_psname + ':FOFBAccSatMin-RB')
        self.fofbaccminsat_rb.precisionFromPV = False
        self.fofbaccminsat_rb.precision = 8

        fofbaccfiltgain_lb = QLabel(
            'Filter Gain', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.fofbaccfiltgain_sp = PyDMLineEdit(
            self, self._prefixed_psname + ':FOFBAccFilterGain-SP')
        self.fofbaccfiltgain_rb = SiriusLabel(
            self, self._prefixed_psname + ':FOFBAccFilterGain-RB')

        widctrl = QWidget()
        lay = QGridLayout(widctrl)
        lay.addWidget(fofbacc_lb, 0, 0, Qt.AlignRight)
        lay.addWidget(self.fofbacc_mon, 0, 1)
        lay.addWidget(fofbaccgain_lb, 1, 0, Qt.AlignRight)
        lay.addWidget(self.fofbaccgain_sp, 1, 1)
        lay.addWidget(self.fofbaccgain_rb, 1, 2)
        lay.addWidget(fofbaccfreeze_lb, 2, 0, Qt.AlignRight)
        lay.addWidget(self.fofbaccfreeze_sp, 2, 1)
        lay.addWidget(self.fofbaccfreeze_rb, 2, 2)
        lay.addWidget(fofbaccclear_lb, 3, 0, Qt.AlignRight)
        lay.addWidget(self.fofbaccclear_bt, 3, 1)
        lay.addWidget(fofbaccmaxsat_lb, 4, 0, Qt.AlignRight)
        lay.addWidget(self.fofbaccmaxsat_sp, 4, 1)
        lay.addWidget(self.fofbaccmaxsat_rb, 4, 2)
        lay.addWidget(fofbaccminsat_lb, 5, 0, Qt.AlignRight)
        lay.addWidget(self.fofbaccminsat_sp, 5, 1)
        lay.addWidget(self.fofbaccminsat_rb, 5, 2)
        lay.addWidget(fofbaccfiltgain_lb, 6, 0, Qt.AlignRight)
        lay.addWidget(self.fofbaccfiltgain_sp, 6, 1)
        lay.addWidget(self.fofbaccfiltgain_rb, 6, 2)

        # coefficients
        gph_fofbcoeffs = dict()
        for plane in ['X', 'Y']:
            colorsp = 'darkBlue' if plane == 'X' else 'darkRed'
            colorrb = 'blue' if plane == 'X' else 'red'
            gph_fofbcoeffs[plane] = SiriusWaveformPlot()
            gph_fofbcoeffs[plane].setSizePolicy(
                QSzPlcy.Maximum, QSzPlcy.Maximum)
            gph_fofbcoeffs[plane].showLegend = True
            gph_fofbcoeffs[plane].autoRangeX = True
            gph_fofbcoeffs[plane].autoRangeY = True
            gph_fofbcoeffs[plane].showXGrid = True
            gph_fofbcoeffs[plane].showYGrid = True
            gph_fofbcoeffs[plane].title = 'InvRespMatRow'+plane+' Coefficients'
            gph_fofbcoeffs[plane].setBackgroundColor(QColor(255, 255, 255))
            gph_fofbcoeffs[plane].addChannel(
                y_channel=self._prefixed_psname+':InvRespMatRow'+plane+'-SP',
                name='SP', color=colorsp, lineWidth=2, symbol='o')
            gph_fofbcoeffs[plane].addChannel(
                y_channel=self._prefixed_psname+':InvRespMatRow'+plane+'-RB',
                name='RB', color=colorrb, lineWidth=2, symbol='o')

        self.show_coeff_sp = QCheckBox('SP')
        self.show_coeff_sp.setChecked(True)
        self.show_coeff_rb = QCheckBox('RB')
        self.show_coeff_rb.setChecked(True)
        for plane in ['X', 'Y']:
            self.show_coeff_sp.stateChanged.connect(
                gph_fofbcoeffs[plane].curveAtIndex(0).setVisible)
            self.show_coeff_rb.stateChanged.connect(
                gph_fofbcoeffs[plane].curveAtIndex(1).setVisible)
        hbox_coeffshow = QHBoxLayout()
        hbox_coeffshow.setAlignment(Qt.AlignCenter)
        hbox_coeffshow.addWidget(self.show_coeff_sp)
        hbox_coeffshow.addWidget(self.show_coeff_rb)

        widcoeff = QWidget()
        lay = QVBoxLayout(widcoeff)
        lay.setAlignment(Qt.AlignTop)
        for plane in ['X', 'Y']:
            lay.addWidget(gph_fofbcoeffs[plane])
        lay.addLayout(hbox_coeffshow)

        # filters
        gph_filt = SiriusWaveformPlot()
        gph_filt.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Maximum)
        gph_filt.showLegend = True
        gph_filt.autoRangeX = True
        gph_filt.autoRangeY = True
        gph_filt.showXGrid = True
        gph_filt.showYGrid = True
        gph_filt.title = 'Filter Coefficients'
        gph_filt.setBackgroundColor(QColor(255, 255, 255))
        gph_filt.addChannel(
            y_channel=self._prefixed_psname+':FOFBAccFilter-SP',
            name='SP', color='darkBlue', lineWidth=2, symbol='o')
        gph_filt.addChannel(
            y_channel=self._prefixed_psname+':FOFBAccFilter-RB',
            name='RB', color='blue', lineWidth=2, symbol='o')

        self.show_filt_sp = QCheckBox('SP')
        self.show_filt_sp.setChecked(True)
        self.show_filt_rb = QCheckBox('RB')
        self.show_filt_rb.setChecked(True)
        self.show_filt_sp.stateChanged.connect(
            gph_filt.curveAtIndex(0).setVisible)
        self.show_filt_rb.stateChanged.connect(
            gph_filt.curveAtIndex(1).setVisible)
        hbox_filtshow = QHBoxLayout()
        hbox_filtshow.setAlignment(Qt.AlignCenter)
        hbox_filtshow.addWidget(self.show_filt_sp)
        hbox_filtshow.addWidget(self.show_filt_rb)

        widfilt = QWidget()
        lay = QVBoxLayout(widfilt)
        lay.setAlignment(Qt.AlignTop)
        lay.addWidget(gph_filt)
        lay.addLayout(hbox_filtshow)

        widmon = QTabWidget()
        widmon.setObjectName(self._psname.sec+'Tab')
        widmon.addTab(widcoeff, 'InvRespMat')
        widmon.addTab(widfilt, 'Filter')

        layout = QHBoxLayout()
        layout.addWidget(widctrl)
        layout.addWidget(widmon)
        return layout


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
        self.setStyleSheet('SiriusLabel{qproperty-alignment: AlignCenter;}')

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
                lbl = SiriusLabel(
                    self, self._prefixed_psname.substitute(propty=pv),
                    keep_unit=True)
                lbl.showUnits = True
                flay1.addRow(text, lbl)

            half2 = self.auxmeas[20:]
            flay2 = QFormLayout()
            flay2.setVerticalSpacing(9)
            for pv in half2:
                text = pv.split('-')[0]
                lbl = SiriusLabel(
                    self, self._prefixed_psname.substitute(propty=pv),
                    keep_unit=True)
                lbl.showUnits = True
                flay2.addRow(text, lbl)

            lay.addLayout(flay1)
            lay.addLayout(flay2)
        else:
            flay = QFormLayout(wid)
            for pv in self.auxmeas:
                text = pv.split('-')[0] if 'SOFB' not in pv else pv
                lbl = SiriusLabel(
                    self, self._prefixed_psname.substitute(propty=pv),
                    keep_unit=True)
                lbl.showUnits = True
                lbl.setObjectName('auxmeaslabel')
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
            lbl = SiriusLabel(self, psname + ':' + pv, keep_unit=True)
            lbl.showUnits = True
            lbl.setObjectName('auxmeaslabel')
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
            'SiriusLabel{qproperty-alignment: AlignVCenter;}')

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
        lbl = CustomLabel(self, keep_unit=True)
        if 'PSName' in pvname:
            lbl.displayFormat = SiriusLabel.DisplayFormat.String
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


class CustomLabel(SiriusLabel):

    def value_changed(self, new_value):
        super().value_changed(new_value)
        new_value = parse_value_for_display(
            value=new_value, precision=self.precision,
            display_format_type=self._display_format_type,
            string_encoding=self._string_encoding, widget=self)
        if isinstance(new_value, str):
            if self._show_units and self._unit != "":
                new_value = "{} {}".format(new_value, self._unit)
            self.setText(new_value)
            return
        if self.enum_strings and isinstance(new_value, (int, float)):
            try:
                self.setText(self.enum_strings[int(new_value)])
            except IndexError:
                self.setText(f'Index Overflow [{new_value}]')
            return
        if self.enum_strings and isinstance(new_value, _np.ndarray):
            text = '['+', '.join([self.enum_strings[int(idx)]
                                  if idx < len(self.enum_strings) else 'UNDEF'
                                  for idx in new_value])+']'
            self.setText(text)
            return
        if isinstance(new_value, (int, float)):
            self.setText(self.format_string.format(new_value))
            return
        self.setText(str(new_value))
