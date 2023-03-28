"""InjCtrl MainWindow."""

from qtpy.QtCore import Qt, Slot, Signal, QEvent
from qtpy.QtWidgets import QWidget, QLabel, QGridLayout, QGroupBox, \
    QHBoxLayout, QVBoxLayout, QSizePolicy as QSzPlcy, QPushButton

import qtawesome as qta

from siriuspy.namesys import SiriusPVName
from siriuspy.injctrl.csdev import Const as _Const

from ..util import get_appropriate_color, connect_newprocess, connect_window
from ..widgets import SiriusMainWindow, SiriusEnumComboBox, \
    PyDMLogLabel, PyDMStateButton, SiriusSpinbox, \
    SiriusConnectionSignal, SiriusLedState, SiriusLabel
from ..as_ti_control import BucketList, EVGInjectionLed, EVGInjectionButton
from ..as_ap_machshift import MachShiftLabel
from .widgets import InjDiagLed, MonitorSummaryWidget, \
    InjSysStbyControlWidget, ClockLabel, TaskStatusLabel
from .auxiliary_dialogs import BiasFBDetailDialog


class InjCtrlWindow(SiriusMainWindow):
    """InjCtrl Main Window."""

    showMonitor = Signal()
    showStatus = Signal()
    showEgun = Signal()

    def __init__(self, parent=None, prefix=''):
        """Init."""
        super().__init__(parent)
        self._prefix = prefix
        self._inj_dev = SiriusPVName('AS-Glob:AP-InjCtrl')
        self._inj_prefix = self._inj_dev.substitute(prefix=prefix)
        self.setWindowTitle('Injection Controls')
        self.setObjectName('ASApp')
        self.setWindowIcon(
            qta.icon('fa5s.syringe', color=get_appropriate_color('AS')))

        self._setupUi()

        self.setFocus(True)
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        self.title = QLabel(
            '<h3>Injection Control<h3>', self, alignment=Qt.AlignCenter)
        self.title.setStyleSheet('QLabel{max-height:1.6em;}')

        self.wid_comm = self._setupMainBarWidget()
        self.wid_comm.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Fixed)

        self.wid_sett = self._setupSettingsWidget()
        self.wid_sett.setSizePolicy(
            QSzPlcy.Preferred, QSzPlcy.MinimumExpanding)

        self.wid_mon = self._setupMonitorWidget()
        self.wid_log = self._setupLogWidget()
        wid_row = QWidget()
        wid_row.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Fixed)
        hbox_row = QHBoxLayout(wid_row)
        hbox_row.setContentsMargins(0, 0, 0, 0)
        hbox_row.setStretch(0, 3)
        hbox_row.setStretch(1, 5)
        hbox_row.addWidget(self.wid_mon)
        hbox_row.addWidget(self.wid_log)

        wid = QWidget(self)
        lay = QVBoxLayout(wid)
        lay.addWidget(self.title)
        lay.addWidget(self.wid_comm)
        lay.addWidget(self.wid_comm)
        lay.addWidget(self.wid_sett)
        lay.addWidget(wid_row)
        lay.setStretch(1, 1)
        lay.setStretch(2, 3)
        lay.setStretch(3, 2)
        self.setCentralWidget(wid)

        self._ch_injmode = SiriusConnectionSignal(
            self._inj_prefix.substitute(propty='Mode-Sel'))
        self._ch_injmode.new_value_signal[int].connect(
            self._handle_injmode_settings_vis)

        # connect window signals
        connect_newprocess(
            self, 'sirius-hla-as-ap-monitor.py',
            parent=self, signal=self.showMonitor)
        connect_newprocess(
            self, 'sirius-hla-si-ap-genstatus.py',
            parent=self, signal=self.showStatus)
        connect_newprocess(
            self, 'sirius-hla-li-eg-control.py',
            parent=self, signal=self.showEgun)

    def _setupMainBarWidget(self):
        # Shift
        machshift_pvname = SiriusPVName(
            'AS-Glob:AP-MachShift:Mode-Sel').substitute(prefix=self._prefix)
        self._cb_shift = SiriusEnumComboBox(self, machshift_pvname)
        self._lb_shift = MachShiftLabel(self, prefix=self._prefix)
        self._lb_shift.setStyleSheet(
            'QLabel{max-height: 2em; min-width: 7em;}')
        self.wid_shift = QGroupBox('Mach.Shift', self)
        lay_shift = QVBoxLayout(self.wid_shift)
        lay_shift.addWidget(self._cb_shift)
        lay_shift.addWidget(self._lb_shift)

        # Injection System
        self.wid_is_summ = InjSysStbyControlWidget(self, is_summary=True)
        self.wid_injsys = QGroupBox('Inj.System', self)
        lay_injsys = QGridLayout(self.wid_injsys)
        lay_injsys.setContentsMargins(0, 0, 0, 0)
        lay_injsys.addWidget(self.wid_is_summ, 0, 0)
        # self.wid_is_full = InjSysStbyControlWidget(self, is_summary=False)
        # self.wid_is_full.setVisible(False)
        # lay_injsys.addWidget(self.wid_is_full, 0, 0)
        # self._icon_expd = qta.icon('fa5s.plus')
        # self._icon_comp = qta.icon('fa5s.minus')
        # self.bt_is_tgl = QPushButton(self._icon_expd, '', self)
        # self.bt_is_tgl.clicked.connect(self._handle_injsys_details_vis)
        # self.bt_is_tgl.setObjectName('bt')
        # self.bt_is_tgl.setStyleSheet("""
        #     #bt{
        #         min-width: 0.8em; max-width: 0.8em;
        #         min-height: 0.8em; max-height: 0.8em;
        #         icon-size:12px;}
        # """)
        # lay_injsys.addWidget(
        #     self.bt_is_tgl, 0, 1, alignment=Qt.AlignRight | Qt.AlignBottom)

        # EGun
        egun_dev = SiriusPVName(
            'LI-01:EG-TriggerPS').substitute(prefix=self._prefix)
        self._sb_eguntrg = PyDMStateButton(
            self, egun_dev.substitute(propty_name='enable'))
        self._led_eguntrg = SiriusLedState(
            self, egun_dev.substitute(propty_name='enablereal'))
        self._led_eguntrg.setStyleSheet(
            'QLed{min-width: 1.29em; max-width: 1.29em;}')
        self.wid_egun = self._create_groupwidget(
            'EGun Trig.', [self._sb_eguntrg, ], [self._led_eguntrg, ])

        # Injection
        self._pb_tiinj = EVGInjectionButton(self, self._prefix)
        self._pb_topup = PyDMStateButton(
            self, init_channel=self._inj_prefix.substitute(
                propty='TopUpState-Sel'))
        self._pb_topup.setVisible(False)
        self._led_injti = EVGInjectionLed(self, self._prefix)
        self._lb_injcnt = SiriusLabel(self)
        self._lb_injcnt.setToolTip(
            'Count injection pulses when Egun Trigger is enabled.')
        ch_injcnt = SiriusPVName(
            'AS-Glob:AP-CurrInfo:InjCount-Mon').substitute(prefix=self._prefix)
        self._lb_injcnt.channel = ch_injcnt
        self._lb_injcnt.setStyleSheet('QLabel{max-width: 3.5em;}')
        hbox_injsts = QHBoxLayout()
        hbox_injsts.setContentsMargins(0, 0, 0, 0)
        hbox_injsts.addWidget(self._led_injti)
        hbox_injsts.addWidget(self._lb_injcnt)
        self.wid_inj = QGroupBox('Injection', self)
        lay_inj = QGridLayout(self.wid_inj)
        lay_inj.setAlignment(Qt.AlignCenter)
        lay_inj.addWidget(self._pb_tiinj, 0, 0)
        lay_inj.addWidget(self._pb_topup, 0, 0)
        lay_inj.addLayout(hbox_injsts, 1, 0)

        # Current
        curr_pvname = SiriusPVName(
            'SI-Glob:AP-CurrInfo:Current-Mon').substitute(prefix=self._prefix)
        self._lb_curr = SiriusLabel(self, curr_pvname)
        self._lb_curr.showUnits = True
        self._lb_curr.setStyleSheet("""
            QLabel{
                font-size: 18pt; qproperty-alignment: AlignCenter;
                min-width: 5.5em; max-width: 5.5em;
        }""")
        self.wid_curr = QGroupBox('Current', self)
        lay_curr = QHBoxLayout(self.wid_curr)
        lay_curr.addWidget(self._lb_curr)

        # TopUp status
        self._lb_tusts = SiriusLabel(
            self, self._inj_prefix.substitute(propty='TopUpState-Sts'))
        self._lb_tusts.setAlignment(Qt.AlignCenter)
        self._lb_tusts.setStyleSheet('QLabel{max-height:2em;}')
        self._ld_tunow = QLabel(
            'Now:', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self._lb_tunow = ClockLabel(self)
        self._lb_tunow.setStyleSheet('QLabel{max-height:2em;}')
        self._ld_tunxt = QLabel(
            'Next:', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self._lb_tunxt = SiriusLabel(
            self, self._inj_prefix.substitute(propty='TopUpNextInj-Mon'))
        self._lb_tunxt.displayFormat = SiriusLabel.DisplayFormat.Time
        self._lb_tunxt.setAlignment(Qt.AlignCenter)
        self._lb_tunxt.setStyleSheet('QLabel{max-height:2em;}')
        self.wid_tusts = QGroupBox('Top-up status')
        self.wid_tusts.setVisible(False)
        lay_tusts = QGridLayout(self.wid_tusts)
        lay_tusts.addWidget(self._lb_tusts, 0, 0, 1, 2)
        lay_tusts.addWidget(self._ld_tunow, 1, 0)
        lay_tusts.addWidget(self._lb_tunow, 1, 1)
        lay_tusts.addWidget(self._ld_tunxt, 2, 0)
        lay_tusts.addWidget(self._lb_tunxt, 2, 1)

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.wid_shift, 0, 0)
        lay.addWidget(self.wid_injsys, 0, 1)
        lay.addWidget(self.wid_egun, 0, 2)
        lay.addWidget(self.wid_inj, 0, 3)
        lay.addWidget(self.wid_tusts, 0, 4)
        lay.addWidget(self.wid_curr, 0, 5)
        lay.setColumnStretch(0, 3)
        lay.setColumnStretch(1, 2)
        lay.setColumnStretch(2, 2)
        lay.setColumnStretch(3, 2)
        lay.setColumnStretch(4, 4)
        lay.setColumnStretch(5, 3)
        wid.setStyleSheet('.QLabel{min-height: 1em; max-height: 1em;}')
        return wid

    def _setupSettingsWidget(self):
        # group of labels to set the same stylesheet
        labelsdesc, labelsmon = list(), list()

        # Mode
        self._ld_injmode = QLabel('Mode', self)
        labelsdesc.append(self._ld_injmode)
        self._cb_injmode = SiriusEnumComboBox(
            self, self._inj_prefix.substitute(propty='Mode-Sel'))
        self._lb_injmode = SiriusLabel(
            self, self._inj_prefix.substitute(propty='Mode-Sts'))
        self._lb_injmode.showUnits = True
        labelsmon.append(self._lb_injmode)

        # Target current
        self._ld_currtgt = QLabel('Target Curr.', self)
        self._sb_currtgt = SiriusSpinbox(
            self, self._inj_prefix.substitute(propty='TargetCurrent-SP'))
        self._lb_currtgt = SiriusLabel(
            self, self._inj_prefix.substitute(propty='TargetCurrent-RB'),
            keep_unit=True)
        self._lb_currtgt.showUnits = True
        labelsmon.append(self._lb_currtgt)

        self._pb_show_topup = QPushButton('v', self)
        self._pb_show_topup.setToolTip('Show TopUp Configurations.')
        self._pb_show_topup.clicked.connect(self._handle_topup_details_vis)
        self._pb_show_topup.setStyleSheet('QPushButton{max-width: 0.8em;}')
        self._wid_currtgt = QWidget(self)
        self._wid_currtgt.setLayout(QHBoxLayout())
        self._wid_currtgt.layout().setContentsMargins(0, 0, 0, 0)
        self._wid_currtgt.layout().addWidget(
            self._pb_show_topup, alignment=Qt.AlignLeft)
        self._wid_currtgt.layout().addWidget(self._ld_currtgt)

        # mode specific configurations
        self.wid_tudtls = self._setupTopUpModeWidget()
        self.wid_tudtls.setVisible(False)

        # Mon
        self._ld_injset = QLabel('Setup ok', self)
        labelsdesc.append(self._ld_injset)
        self._led_injset = InjDiagLed(self)

        # Type
        self._ld_injtype = QLabel('Type', self)
        labelsdesc.append(self._ld_injtype)
        self._cb_injtype = SiriusEnumComboBox(
            self, self._inj_prefix.substitute(propty='Type-Sel'))
        self._lb_injtype = SiriusLabel(
            self, self._inj_prefix.substitute(propty='Type-Sts'))
        labelsmon.append(self._lb_injtype)
        self._lb_injtype_mon = SiriusLabel(
            self, self._inj_prefix.substitute(propty='Type-Mon'))
        labelsmon.append(self._lb_injtype_mon)
        self._ch_injtype = SiriusConnectionSignal(
            self._inj_prefix.substitute(propty='Type-Sel'))
        self._ch_injtype.new_value_signal[int].connect(
            self._handle_injtype_settings_vis)
        self._ind_injtype_mon = TaskStatusLabel(
            self, self._inj_prefix.substitute(propty='TypeCmdSts-Mon'))

        # PUMode
        self._ld_pumode = QLabel('PU Mode', self)
        labelsdesc.append(self._ld_pumode)
        self._cb_pumode = SiriusEnumComboBox(
            self, self._inj_prefix.substitute(propty='PUMode-Sel'))
        self._lb_pumode = SiriusLabel(
            self, self._inj_prefix.substitute(propty='PUMode-Sts'))
        labelsmon.append(self._lb_pumode)
        self._lb_pumode_mon = SiriusLabel(
            self, self._inj_prefix.substitute(propty='PUMode-Mon'))
        labelsmon.append(self._lb_pumode_mon)
        self._ch_pumode = SiriusConnectionSignal(
            self._inj_prefix.substitute(propty='PUMode-Sel'))
        self._ind_pumode_mon = TaskStatusLabel(
            self, self._inj_prefix.substitute(propty='PUModeCmdSts-Mon'))

        # Single bunch bias voltage
        self._ld_sbbias = QLabel('SB Bias Voltage', self)
        labelsdesc.append(self._ld_sbbias)
        self._sb_sbbias = SiriusSpinbox(
            self, self._inj_prefix.substitute(propty='SglBunBiasVolt-SP'))
        self._lb_sbbias = SiriusLabel(
            self, self._inj_prefix.substitute(propty='SglBunBiasVolt-RB'),
            keep_unit=True)
        self._lb_sbbias.showUnits = True
        labelsmon.append(self._lb_sbbias)
        self._ld_sbbias.setVisible(False)
        self._sb_sbbias.setVisible(False)
        self._lb_sbbias.setVisible(False)

        # Multi bunch bias voltage
        self._ld_mbbias = QLabel('MB Bias Volt.', self)
        labelsdesc.append(self._ld_mbbias)
        self._sb_mbbias = SiriusSpinbox(
            self, self._inj_prefix.substitute(propty='MultBunBiasVolt-SP'))
        self._lb_mbbias = SiriusLabel(
            self, self._inj_prefix.substitute(propty='MultBunBiasVolt-RB'),
            keep_unit=True)
        self._lb_mbbias.showUnits = True
        labelsmon.append(self._lb_mbbias)

        # bias voltage mon
        ch_bias_mon = SiriusPVName('LI-01:EG-BiasPS').substitute(
            prefix=self._prefix, propty_name='voltinsoft')
        self._lb_bias_mon = SiriusLabel(
            self, ch_bias_mon, keep_unit=True)
        self._lb_bias_mon.showUnits = True
        labelsmon.append(self._lb_bias_mon)
        self._ind_bias_mon = TaskStatusLabel(
            self, self._inj_prefix.substitute(propty='BiasVoltCmdSts-Mon'))

        # Filament current op value
        self._ld_filaopcurr = QLabel('Fila.Op. Curr.', self)
        labelsdesc.append(self._ld_filaopcurr)
        self._sb_filaopcurr = SiriusSpinbox(
            self, self._inj_prefix.substitute(propty='FilaOpCurr-SP'))
        self._lb_filaopcurr = SiriusLabel(
            self, self._inj_prefix.substitute(propty='FilaOpCurr-RB'),
            keep_unit=True)
        self._lb_filaopcurr.showUnits = True
        labelsmon.append(self._lb_filaopcurr)
        ch_filacurr_mon = SiriusPVName('LI-01:EG-FilaPS').substitute(
            prefix=self._prefix, propty_name='currentinsoft')
        self._lb_filaopcurr_mon = SiriusLabel(
            self, ch_filacurr_mon, keep_unit=True)
        self._lb_filaopcurr_mon.showUnits = True
        labelsmon.append(self._lb_filaopcurr_mon)
        self._ind_filaopcurr_mon = TaskStatusLabel(
            self, self._inj_prefix.substitute(propty='FilaOpCurrCmdSts-Mon'))

        # High voltage op value
        self._ld_hvopvolt = QLabel('HV.Op. Volt.', self)
        labelsdesc.append(self._ld_hvopvolt)
        self._sb_hvopvolt = SiriusSpinbox(
            self, self._inj_prefix.substitute(propty='HVOpVolt-SP'))
        self._lb_hvopvolt = SiriusLabel(
            self, self._inj_prefix.substitute(propty='HVOpVolt-RB'),
            keep_unit=True)
        self._lb_hvopvolt.showUnits = True
        labelsmon.append(self._lb_hvopvolt)
        ch_hvvolt_mon = SiriusPVName('LI-01:EG-HVPS').substitute(
            prefix=self._prefix, propty_name='voltinsoft')
        self._lb_hvopvolt_mon = SiriusLabel(
            self, ch_hvvolt_mon, keep_unit=True)
        self._lb_hvopvolt_mon.showUnits = True
        labelsmon.append(self._lb_hvopvolt_mon)
        self._ind_hvopvolt_mon = TaskStatusLabel(
            self, self._inj_prefix.substitute(propty='HVOpVoltCmdSts-Mon'))

        # header
        ld_sp = QLabel('<h4>SP</h4>', self, alignment=Qt.AlignCenter)
        ld_rb = QLabel('<h4>RB</h4>', self, alignment=Qt.AlignCenter)
        ld_mon = QLabel('<h4>Mon</h4>', self, alignment=Qt.AlignCenter)

        # Bucket list
        self._wid_bl = BucketList(
            self, prefix=self._prefix, min_size=15, show_graph=True)
        self._wid_bl.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.MinimumExpanding)

        wid1 = QWidget()
        wid1.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Fixed)
        glay1 = QGridLayout(wid1)
        glay1.setAlignment(Qt.AlignTop)
        glay1.addWidget(self._ld_injset, 0, 0)
        glay1.addWidget(self._led_injset, 0, 1)
        glay1.addWidget(self._ld_injmode, 1, 0)
        glay1.addWidget(self._cb_injmode, 1, 1)
        glay1.addWidget(self._lb_injmode, 1, 2)
        glay1.addWidget(self._wid_currtgt, 2, 0)
        glay1.addWidget(self._sb_currtgt, 2, 1)
        glay1.addWidget(self._lb_currtgt, 2, 2)
        glay1.addWidget(self.wid_tudtls, 3, 0, 2, 4)
        glay1.setColumnStretch(0, 3)
        glay1.setColumnStretch(1, 2)
        glay1.setColumnStretch(2, 2)

        wid2 = QWidget()
        wid2.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Fixed)
        glay2 = QGridLayout(wid2)
        glay2.setAlignment(Qt.AlignTop)
        glay2.addWidget(ld_sp, 0, 1)
        glay2.addWidget(ld_rb, 0, 2)
        glay2.addWidget(ld_mon, 0, 3)
        glay2.addWidget(self._ld_injtype, 1, 0)
        glay2.addWidget(self._cb_injtype, 1, 1)
        glay2.addWidget(self._lb_injtype, 1, 2)
        glay2.addWidget(self._lb_injtype_mon, 1, 3)
        glay2.addWidget(self._ind_injtype_mon, 1, 4)
        glay2.addWidget(self._ld_pumode, 2, 0)
        glay2.addWidget(self._cb_pumode, 2, 1)
        glay2.addWidget(self._lb_pumode, 2, 2)
        glay2.addWidget(self._lb_pumode_mon, 2, 3)
        glay2.addWidget(self._ind_pumode_mon, 2, 4)
        glay2.addWidget(self._ld_sbbias, 3, 0)
        glay2.addWidget(self._sb_sbbias, 3, 1)
        glay2.addWidget(self._lb_sbbias, 3, 2)
        glay2.addWidget(self._ld_mbbias, 3, 0)
        glay2.addWidget(self._sb_mbbias, 3, 1)
        glay2.addWidget(self._lb_mbbias, 3, 2)
        glay2.addWidget(self._lb_bias_mon, 3, 3)
        glay2.addWidget(self._ind_bias_mon, 3, 4)
        glay2.addWidget(self._ld_filaopcurr, 4, 0)
        glay2.addWidget(self._sb_filaopcurr, 4, 1)
        glay2.addWidget(self._lb_filaopcurr, 4, 2)
        glay2.addWidget(self._lb_filaopcurr_mon, 4, 3)
        glay2.addWidget(self._ind_filaopcurr_mon, 4, 4)
        glay2.addWidget(self._ld_hvopvolt, 5, 0)
        glay2.addWidget(self._sb_hvopvolt, 5, 1)
        glay2.addWidget(self._lb_hvopvolt, 5, 2)
        glay2.addWidget(self._lb_hvopvolt_mon, 5, 3)
        glay2.addWidget(self._ind_hvopvolt_mon, 5, 4)
        glay2.setColumnStretch(0, 5)
        glay2.setColumnStretch(1, 3)
        glay2.setColumnStretch(2, 3)
        glay2.setColumnStretch(3, 3)
        glay2.setColumnStretch(3, 1)

        wid = QGroupBox('Settings')
        lay = QGridLayout(wid)
        lay.addWidget(wid1, 0, 0, alignment=Qt.AlignTop)
        lay.addWidget(wid2, 0, 1, alignment=Qt.AlignTop)
        lay.addWidget(self._wid_bl, 1, 0, 1, 2)
        lay.setColumnStretch(0, 3)
        lay.setColumnStretch(1, 4)

        for lbl in labelsdesc:
            lbl.setStyleSheet("""
                QLabel{
                    min-width: 7em; max-width: 7em; min-height: 1.5em;
                    qproperty-alignment: 'AlignRight | AlignVCenter';
                }""")
        for lbl in labelsmon:
            lbl.setStyleSheet("SiriusLabel{qproperty-alignment: AlignCenter;}")

        return wid

    def _setupTopUpModeWidget(self):
        self._ld_tuperd = QLabel('Period', self)
        self._sb_tuperd = SiriusSpinbox(
            self, self._inj_prefix.substitute(propty='TopUpPeriod-SP'))
        self._lb_tuperd = SiriusLabel(
            self, self._inj_prefix.substitute(propty='TopUpPeriod-RB'),
            keep_unit=True)
        self._lb_tuperd.showUnits = True

        self._ld_tuoffs = QLabel('Head Start Time', self)
        pvname = self._inj_prefix.substitute(propty='TopUpHeadStartTime-SP')
        self._sb_tuoffs = SiriusSpinbox(self, pvname)
        self._lb_tuoffs = SiriusLabel(
            self, pvname.substitute(propty_suffix='RB'), keep_unit=True)
        self._lb_tuoffs.showUnits = True

        self._ld_tunrpu = QLabel('Nr.Pulses', self)
        self._sb_tunrpu = SiriusSpinbox(
            self, self._inj_prefix.substitute(propty='TopUpNrPulses-SP'))
        self._lb_tunrpu = SiriusLabel(
            self, self._inj_prefix.substitute(propty='TopUpNrPulses-RB'))
        self._lb_tunrpu.showUnits = True

        self._ld_tupustd = QLabel('PU Standby', self)
        pvname = self._inj_prefix.substitute(propty='TopUpPUStandbyEnbl-Sel')
        self._sb_tupustd = PyDMStateButton(self, pvname)
        self._lb_tupustd = SiriusLedState(
            self, pvname.substitute(propty_suffix='Sts'))

        self._ld_tulistd = QLabel('LI Standby', self)
        pvname = self._inj_prefix.substitute(propty='TopUpLIStandbyEnbl-Sel')
        self._sb_tulistd = PyDMStateButton(self, pvname)
        self._lb_tulistd = SiriusLedState(
            self, pvname.substitute(propty_suffix='Sts'))

        self._ld_tubiasfb = QLabel('Bias FB', self)
        pvname = self._inj_prefix.substitute(propty='BiasFBLoopState-Sel')
        self._sb_tubiasfb = PyDMStateButton(self, pvname)
        self._lb_tubiasfb = SiriusLedState(
            self, pvname.substitute(propty_suffix='Sts'))
        self._pb_biasfb = QPushButton(qta.icon('fa5s.ellipsis-v'), '', self)
        self._pb_biasfb.setObjectName('btn')
        self._pb_biasfb.setStyleSheet(
            '#btn{min-width:18px;max-width:18px;icon-size:20px;}')
        connect_window(
            self._pb_biasfb, BiasFBDetailDialog, self,
            device=self._inj_dev, prefix=self._prefix)

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setContentsMargins(0, 6, 0, 0)
        lay.setAlignment(Qt.AlignTop)
        lay.addWidget(self._ld_tuperd, 0, 0)
        lay.addWidget(self._sb_tuperd, 0, 1)
        lay.addWidget(self._lb_tuperd, 0, 2)
        lay.addWidget(self._ld_tuoffs, 1, 0)
        lay.addWidget(self._sb_tuoffs, 1, 1)
        lay.addWidget(self._lb_tuoffs, 1, 2)
        lay.addWidget(self._ld_tunrpu, 2, 0)
        lay.addWidget(self._sb_tunrpu, 2, 1)
        lay.addWidget(self._lb_tunrpu, 2, 2)
        lay.addWidget(self._ld_tupustd, 3, 0)
        lay.addWidget(self._sb_tupustd, 3, 1)
        lay.addWidget(self._lb_tupustd, 3, 2)
        lay.addWidget(self._ld_tulistd, 4, 0)
        lay.addWidget(self._sb_tulistd, 4, 1)
        lay.addWidget(self._lb_tulistd, 4, 2)
        lay.addWidget(self._ld_tubiasfb, 5, 0)
        lay.addWidget(self._sb_tubiasfb, 5, 1)
        lay.addWidget(self._lb_tubiasfb, 5, 2)
        lay.addWidget(self._pb_biasfb, 5, 3)
        lay.setColumnStretch(0, 3)
        lay.setColumnStretch(1, 2)
        lay.setColumnStretch(2, 2)

        wid.setStyleSheet("""
            .QLabel{
                min-width: 7em; max-width: 7em; min-height: 1.5em;
                qproperty-alignment: 'AlignRight | AlignVCenter';
            }
            SiriusLabel{
                qproperty-alignment: AlignCenter;
            }""")
        return wid

    def _setupLogWidget(self):
        self._log = PyDMLogLabel(
            self, self._inj_prefix.substitute(propty='Log-Mon'),
            ['Remaining time', ])

        wid = QGroupBox('Log')
        lay = QHBoxLayout(wid)
        lay.addWidget(self._log)
        return wid

    def _setupMonitorWidget(self):
        self.wid_mon = MonitorSummaryWidget(self)

        wid = QWidget(self)
        lay = QGridLayout(wid)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.wid_mon, 0, 0)
        return wid

    # ---- auxiliary commands ----

    @Slot(int)
    def _handle_injtype_settings_vis(self, new_type):
        is_sb = new_type == _Const.InjType.SingleBunch
        self._ld_sbbias.setVisible(is_sb)
        self._sb_sbbias.setVisible(is_sb)
        self._lb_sbbias.setVisible(is_sb)
        self._ld_mbbias.setVisible(not is_sb)
        self._sb_mbbias.setVisible(not is_sb)
        self._lb_mbbias.setVisible(not is_sb)
        self.centralWidget().adjustSize()
        self.adjustSize()

    @Slot(int)
    def _handle_injmode_settings_vis(self, new_mode):
        is_topup = new_mode == _Const.InjMode.TopUp
        self._handle_topup_details_vis(False, is_topup=is_topup)
        self._pb_topup.setVisible(is_topup)
        self._pb_tiinj.setVisible(not is_topup)
        self.wid_tusts.setVisible(is_topup)

    def _handle_topup_details_vis(self, val, is_topup=None):
        _ = val
        if is_topup is None:
            show = self.wid_tudtls.isHidden()
        else:
            show = is_topup
        self.wid_tudtls.setVisible(show)
        text = '^' if show else 'v'
        tooltip = ('Hide' if show else 'Show')+' TopUp Configurations.'
        self._pb_show_topup.setText(text)
        self._pb_show_topup.setToolTip(tooltip)

    def _handle_injsys_details_vis(self):
        exp = self.wid_is_summ.isVisible()
        icon = self._icon_comp if exp else self._icon_expd
        self.sender().setIcon(icon)
        self.wid_is_summ.setVisible(not exp)
        self.wid_is_full.setVisible(exp)
        self.centralWidget().adjustSize()
        self.adjustSize()

    def _create_groupwidget(self, title, sp_wids, rb_wids, aux_wids=None):
        hbox_sp = QHBoxLayout()
        hbox_sp.setAlignment(Qt.AlignCenter)
        hbox_sp.setContentsMargins(0, 0, 0, 0)
        for wid in sp_wids:
            hbox_sp.addWidget(wid)

        hbox_rb = QHBoxLayout()
        hbox_rb.setAlignment(Qt.AlignCenter)
        hbox_rb.setContentsMargins(0, 0, 0, 0)
        for wid in rb_wids:
            hbox_rb.addWidget(wid)

        box = QGroupBox(title, self) if title else QWidget(self)
        lay = QVBoxLayout(box)
        lay.setAlignment(Qt.AlignCenter)
        if not isinstance(box, QGroupBox):
            lay.setContentsMargins(0, 0, 0, 0)
        lay.addLayout(hbox_sp)
        lay.addLayout(hbox_rb)

        if aux_wids:
            hbox_aux = QHBoxLayout()
            hbox_aux.setAlignment(Qt.AlignCenter)
            hbox_aux.setContentsMargins(0, 0, 0, 0)
            for wid in aux_wids:
                hbox_aux.addWidget(wid)
            lay.addLayout(hbox_aux)
        return box

    # ---- events ----

    def mouseDoubleClickEvent(self, event):
        """Implement mouseDoubleClickEvent."""
        if event.button() == Qt.LeftButton:
            if self.wid_curr.underMouse():
                self.showStatus.emit()
            elif self.wid_shift.underMouse():
                self.showStatus.emit()
            elif self.wid_egun.underMouse():
                self.showEgun.emit()
            elif self.wid_mon.underMouse():
                self.showMonitor.emit()
        super().mouseDoubleClickEvent(event)

    def changeEvent(self, event):
        """Implement changeEvent."""
        if event.type() == QEvent.FontChange:
            fontsize = self.app.font().pointSize()
            self._lb_curr.setStyleSheet(
                'QLabel{'
                '    font-size: '+str(fontsize+8)+'pt;'
                '    qproperty-alignment: AlignCenter;'
                '    min-width: 6em; max-width: 6em;'
                '}')
            self.ensurePolished()
