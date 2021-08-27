"""InjCtrl MainWindow."""

from qtpy.QtCore import Qt, Slot, Signal, QEvent
from qtpy.QtWidgets import QWidget, QLabel, QGridLayout, QGroupBox, \
    QHBoxLayout, QVBoxLayout

import qtawesome as qta

from pydm.widgets import PyDMPushButton, PyDMLabel

from siriuspy.search import LLTimeSearch
from siriuspy.injctrl.csdev import Const as _Const

from ..util import get_appropriate_color, connect_newprocess
from ..widgets import SiriusMainWindow, SiriusEnumComboBox, \
    PyDMLogLabel, PyDMStateButton, SiriusSpinbox, \
    SiriusConnectionSignal, SiriusLedState, SiriusLabel
from ..as_ti_control import BucketList, EVGInjectionLed, EVGInjectionButton
from ..as_ap_machshift import MachShiftLabel
from .widgets import InjDiagLed, MonitorSummaryWidget, \
    InjSysStbyControlWidget, ClockLabel


class InjCtrlWindow(SiriusMainWindow):
    """InjCtrl Main Window."""

    showMonitor = Signal()
    showStatus = Signal()
    showEgun = Signal()

    def __init__(self, prefix='', parent=None):
        """Init."""
        super().__init__(parent)
        self._prefix = prefix
        self._inj_prefix = prefix + 'AS-Glob:AP-InjCtrl'
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

        self.wid_sett = self._setupSettingsWidget()

        self.wid_mon = self._setupMonitorWidget()
        self.wid_log = self._setupLogWidget()

        wid = QWidget(self)
        lay = QGridLayout(wid)
        lay.addWidget(self.title, 0, 0, 1, 2)
        lay.addWidget(self.wid_comm, 1, 0, 1, 2)
        lay.addWidget(self.wid_comm, 1, 0, 1, 2)
        lay.addWidget(self.wid_sett, 2, 0, 1, 2)
        lay.addWidget(self.wid_mon, 3, 0)
        lay.addWidget(self.wid_log, 3, 1)
        lay.setColumnStretch(0, 3)
        lay.setColumnStretch(1, 5)
        lay.setRowStretch(1, 1)
        lay.setRowStretch(2, 3)
        lay.setRowStretch(3, 2)
        self.setCentralWidget(wid)

        self._ch_injmode = SiriusConnectionSignal(
            self._inj_prefix + ':Mode-Sel')
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
        self._cb_shift = SiriusEnumComboBox(
            self, self._prefix+'AS-Glob:AP-MachShift:Mode-Sel')
        self._lb_shift = MachShiftLabel()
        self._lb_shift.setStyleSheet(
            'QLabel{max-height: 2em; min-width: 7em;}')
        self.wid_shift = QGroupBox('Mach.Shift')
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
        self._sb_eguntrg = PyDMStateButton(
            self, self._prefix+'LI-01:EG-TriggerPS:enable')
        self._led_eguntrg = SiriusLedState(
            self, self._prefix+'LI-01:EG-TriggerPS:enablereal')
        self._led_eguntrg.setStyleSheet(
            'QLed{min-width: 1.29em; max-width: 1.29em;}')
        self.wid_egun = self._create_groupwidget(
            'EGun Trig.', [self._sb_eguntrg, ], [self._led_eguntrg, ])

        # Injection
        self._pb_tiinj = EVGInjectionButton(self, self._prefix)
        self._pb_topup = PyDMStateButton(
            self, init_channel=self._inj_prefix + ':TopUpState-Sel')
        self._pb_topup.setVisible(False)
        self._led_injti = EVGInjectionLed(self, self._prefix)
        self._lb_injcnt = PyDMLabel(self)
        self._lb_injcnt.setToolTip(
            'Count injection pulses when Egun Trigger is enabled.')
        self._lb_injcnt.channel = \
            'AS-Glob:AP-CurrInfo:InjCount-Mon'
        self._lb_injcnt.setStyleSheet('QLabel{max-width: 3.5em;}')
        hbox_injsts = QHBoxLayout()
        hbox_injsts.setContentsMargins(0, 0, 0, 0)
        hbox_injsts.addWidget(self._led_injti)
        hbox_injsts.addWidget(self._lb_injcnt)
        self.wid_inj = QGroupBox('Injection')
        lay_inj = QGridLayout(self.wid_inj)
        lay_inj.setAlignment(Qt.AlignCenter)
        lay_inj.addWidget(self._pb_tiinj, 0, 0)
        lay_inj.addWidget(self._pb_topup, 0, 0)
        lay_inj.addLayout(hbox_injsts, 1, 0)

        # Current
        self._lb_curr = PyDMLabel(self, 'SI-Glob:AP-CurrInfo:Current-Mon')
        self._lb_curr.showUnits = True
        self._lb_curr.setStyleSheet("""
            QLabel{
                font-size: 18pt; qproperty-alignment: AlignCenter;
                min-width: 5.5em; max-width: 5.5em;
        }""")
        self.wid_curr = QGroupBox('Current')
        lay_curr = QHBoxLayout(self.wid_curr)
        lay_curr.addWidget(self._lb_curr)

        # TopUp status
        self._lb_tusts = PyDMLabel(
            self, self._inj_prefix + ':TopUpState-Sts')
        self._lb_tusts.setAlignment(Qt.AlignCenter)
        self._lb_tusts.setStyleSheet('QLabel{max-height:2em;}')
        self._ld_tunow = QLabel(
            'Now:', self, alignment=Qt.AlignRight | Qt.AlignCenter)
        self._lb_tunow = ClockLabel(self)
        self._lb_tunow.setStyleSheet('QLabel{max-height:2em;}')
        self._ld_tunxt = QLabel(
            'Next:', self, alignment=Qt.AlignRight | Qt.AlignCenter)
        self._lb_tunxt = SiriusLabel(
            self, self._inj_prefix + ':TopUpNextInj-Mon')
        self._lb_tunxt.displayFormat = SiriusLabel.DisplayFormat.Time
        self._lb_tunxt.setAlignment(Qt.AlignCenter)
        self._lb_tunxt.setStyleSheet('QLabel{max-height:2em;}')
        self._pb_round = PyDMPushButton(
            self, label='', icon=qta.icon('mdi.tilde'), pressValue=1,
            init_channel=self._inj_prefix + ':TopUpNextInjRound-Cmd')
        self._pb_round.setObjectName('but')
        self._pb_round.setStyleSheet(
            '#but{min-width:18px; max-width:18px; icon-size:16px;}')
        self.wid_tusts = QGroupBox('Top-up status')
        self.wid_tusts.setVisible(False)
        lay_tusts = QGridLayout(self.wid_tusts)
        lay_tusts.addWidget(self._lb_tusts, 0, 0, 1, 2)
        lay_tusts.addWidget(self._ld_tunow, 1, 0)
        lay_tusts.addWidget(self._lb_tunow, 1, 1)
        lay_tusts.addWidget(self._ld_tunxt, 2, 0)
        lay_tusts.addWidget(self._lb_tunxt, 2, 1)
        lay_tusts.addWidget(self._pb_round, 2, 2)

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
        # Mode
        self._ld_injmode = QLabel(
            'Mode', self, alignment=Qt.AlignRight | Qt.AlignCenter)
        self._ld_injmode.setStyleSheet(
            'QLabel{min-width: 6.5em; max-width: 6.5em; min-height: 1em;}')
        self._cb_injmode = SiriusEnumComboBox(
            self, self._inj_prefix + ':Mode-Sel')
        self._lb_injmode = PyDMLabel(
            self, self._inj_prefix + ':Mode-Sts')
        self._lb_injmode.showUnits = True

        # Target current
        self._ld_currtgt = QLabel(
            'Target Curr.', self, alignment=Qt.AlignRight | Qt.AlignCenter)
        self._ld_currtgt.setStyleSheet(
            'QLabel{min-width: 6.5em; max-width: 6.5em; min-height: 1em;}')
        self._sb_currtgt = SiriusSpinbox(
            self, self._inj_prefix + ':TargetCurrent-SP')
        self._sb_currtgt.showStepExponent = False
        self._lb_currtgt = PyDMLabel(
            self, self._inj_prefix + ':TargetCurrent-RB')
        self._lb_currtgt.showUnits = True

        # mode specific configurations
        self.wid_dcdtls = self._setupDecayModeWidget()
        self.wid_tudtls = self._setupTopUpModeWidget()
        self.wid_tudtls.setVisible(False)

        # Mon
        self._ld_injset = QLabel(
            'Setup ok', self, alignment=Qt.AlignRight | Qt.AlignCenter)
        self._ld_injset.setStyleSheet(
            'QLabel{min-width: 6.5em; max-width: 6.5em; min-height: 1em;}')
        self._led_injset = InjDiagLed(self)

        # Type
        self._ld_injtype = QLabel(
            'Type', self, alignment=Qt.AlignRight | Qt.AlignCenter)
        self._ld_injtype.setStyleSheet(
            'QLabel{min-width: 6.5em; max-width: 6.5em; min-height: 1em;}')
        self._cb_injtype = SiriusEnumComboBox(
            self, self._inj_prefix + ':Type-Sel')
        self._lb_injtype = PyDMLabel(
            self, self._inj_prefix + ':Type-Sts')
        self._lb_injtype.showUnits = True
        self._ch_injtype = SiriusConnectionSignal(
            self._inj_prefix + ':Type-Sel')
        self._ch_injtype.new_value_signal[int].connect(
            self._handle_injtype_settings_vis)

        # Single bunch bias voltage
        self._ld_sbbias = QLabel(
            'SB Bias Voltage', self, alignment=Qt.AlignRight | Qt.AlignCenter)
        self._ld_sbbias.setStyleSheet(
            'QLabel{min-width: 6.5em; max-width: 6.5em; min-height: 1em;}')
        self._sb_sbbias = SiriusSpinbox(
            self, self._inj_prefix + ':SglBunBiasVolt-SP')
        self._sb_sbbias.showStepExponent = False
        self._lb_sbbias = PyDMLabel(
            self, self._inj_prefix + ':SglBunBiasVolt-RB')
        self._lb_sbbias.showUnits = True
        self._ld_sbbias.setVisible(False)
        self._sb_sbbias.setVisible(False)
        self._lb_sbbias.setVisible(False)

        # Multi bunch bias voltage
        self._ld_mbbias = QLabel(
            'MB Bias Volt.', self, alignment=Qt.AlignRight | Qt.AlignCenter)
        self._ld_mbbias.setStyleSheet(
            'QLabel{min-width: 6.5em; max-width: 6.5em; min-height: 1em;}')
        self._sb_mbbias = SiriusSpinbox(
            self, self._inj_prefix + ':MultBunBiasVolt-SP')
        self._sb_mbbias.showStepExponent = False
        self._lb_mbbias = PyDMLabel(
            self, self._inj_prefix + ':MultBunBiasVolt-RB')
        self._lb_mbbias.showUnits = True

        # Filament current op value
        self._ld_filaopcurr = QLabel(
            'Fila.Op. Curr.', self, alignment=Qt.AlignRight | Qt.AlignCenter)
        self._ld_filaopcurr.setStyleSheet(
            'QLabel{min-width: 6.5em; max-width: 6.5em; min-height: 1em;}')
        self._sb_filaopcurr = SiriusSpinbox(
            self, self._inj_prefix + ':FilaOpCurr-SP')
        self._sb_filaopcurr.showStepExponent = False
        self._lb_filaopcurr = PyDMLabel(
            self, self._inj_prefix + ':FilaOpCurr-RB')
        self._lb_filaopcurr.showUnits = True

        # High voltage op value
        self._ld_hvopvolt = QLabel(
            'HV.Op. Volt.', self, alignment=Qt.AlignRight | Qt.AlignCenter)
        self._ld_hvopvolt.setStyleSheet(
            'QLabel{min-width: 6.5em; max-width: 6.5em; min-height: 1em;}')
        self._sb_hvopvolt = SiriusSpinbox(
            self, self._inj_prefix + ':HVOpVolt-SP')
        self._sb_hvopvolt.showStepExponent = False
        self._lb_hvopvolt = PyDMLabel(
            self, self._inj_prefix + ':HVOpVolt-RB')
        self._lb_hvopvolt.showUnits = True

        # Bucket list
        evg_name = LLTimeSearch.get_evg_name()
        self._wid_bl = BucketList(
            self, prefix=self._prefix+evg_name+':', min_size=15,
            show_graph=True)

        wid1 = QWidget()
        glay1 = QGridLayout(wid1)
        glay1.setAlignment(Qt.AlignTop)
        glay1.addWidget(self._ld_injmode, 0, 0)
        glay1.addWidget(self._cb_injmode, 0, 1)
        glay1.addWidget(self._lb_injmode, 0, 2)
        glay1.addWidget(self._ld_currtgt, 1, 0)
        glay1.addWidget(self._sb_currtgt, 1, 1)
        glay1.addWidget(self._lb_currtgt, 1, 2)
        glay1.addWidget(self.wid_tudtls, 2, 0, 2, 3)
        glay1.addWidget(self.wid_dcdtls, 2, 0, 2, 3)
        glay1.setColumnStretch(0, 3)
        glay1.setColumnStretch(1, 2)
        glay1.setColumnStretch(2, 2)

        wid2 = QWidget()
        glay2 = QGridLayout(wid2)
        glay2.setAlignment(Qt.AlignTop)
        glay2.addWidget(self._ld_injset, 0, 0)
        glay2.addWidget(self._led_injset, 0, 1)
        glay2.addWidget(self._ld_injtype, 1, 0)
        glay2.addWidget(self._cb_injtype, 1, 1)
        glay2.addWidget(self._lb_injtype, 1, 2)
        glay2.addWidget(self._ld_sbbias, 2, 0)
        glay2.addWidget(self._sb_sbbias, 2, 1)
        glay2.addWidget(self._lb_sbbias, 2, 2)
        glay2.addWidget(self._ld_mbbias, 3, 0)
        glay2.addWidget(self._sb_mbbias, 3, 1)
        glay2.addWidget(self._lb_mbbias, 3, 2)
        glay2.addWidget(self._ld_filaopcurr, 4, 0)
        glay2.addWidget(self._sb_filaopcurr, 4, 1)
        glay2.addWidget(self._lb_filaopcurr, 4, 2)
        glay2.addWidget(self._ld_hvopvolt, 5, 0)
        glay2.addWidget(self._sb_hvopvolt, 5, 1)
        glay2.addWidget(self._lb_hvopvolt, 5, 2)
        glay2.setColumnStretch(0, 3)
        glay2.setColumnStretch(1, 2)
        glay2.setColumnStretch(2, 2)

        wid = QGroupBox('Settings')
        lay = QGridLayout(wid)
        lay.addWidget(wid1, 0, 0)
        lay.addWidget(wid2, 0, 1)
        lay.addWidget(self._wid_bl, 1, 0, 1, 2)
        return wid

    def _setupTopUpModeWidget(self):
        self._ld_tuperd = QLabel(
            'Period', self, alignment=Qt.AlignRight | Qt.AlignCenter)
        self._sb_tuperd = SiriusSpinbox(
            self, self._inj_prefix + ':TopUpPeriod-SP')
        self._sb_tuperd.showStepExponent = False
        self._lb_tuperd = PyDMLabel(
            self, self._inj_prefix + ':TopUpPeriod-RB')
        self._lb_tuperd.showUnits = True

        self._ld_tumaxpu = QLabel(
            'Max.Nr.Pulses', self, alignment=Qt.AlignRight | Qt.AlignCenter)
        self._sb_tumaxpu = SiriusSpinbox(
            self, self._inj_prefix + ':TopUpMaxNrPulses-SP')
        self._sb_tumaxpu.showStepExponent = False
        self._lb_tumaxpu = PyDMLabel(
            self, self._inj_prefix + ':TopUpMaxNrPulses-RB')
        self._lb_tumaxpu.showUnits = True

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setContentsMargins(0, 6, 0, 0)
        lay.setAlignment(Qt.AlignTop)
        lay.addWidget(self._ld_tuperd, 0, 0)
        lay.addWidget(self._sb_tuperd, 0, 1)
        lay.addWidget(self._lb_tuperd, 0, 2)
        lay.addWidget(self._ld_tumaxpu, 1, 0)
        lay.addWidget(self._sb_tumaxpu, 1, 1)
        lay.addWidget(self._lb_tumaxpu, 1, 2)
        lay.setColumnStretch(0, 3)
        lay.setColumnStretch(1, 2)
        lay.setColumnStretch(2, 2)

        wid.setStyleSheet("""
            .QLabel{
                min-width: 6.5em; max-width: 6.5em; min-height: 1em;
            }""")
        return wid

    def _setupDecayModeWidget(self):
        self._ld_autostop = QLabel(
            'Auto Stop', self, alignment=Qt.AlignRight | Qt.AlignCenter)
        self._cb_autostop = PyDMStateButton(
            self, self._inj_prefix + ':AutoStop-Sel')
        self._cb_autostop.shape = 1
        self._led_autostop = SiriusLedState(
            self, self._inj_prefix + ':AutoStop-Sts')

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignTop)
        lay.setContentsMargins(0, 6, 0, 0)
        lay.addWidget(self._ld_autostop, 0, 0)
        lay.addWidget(self._cb_autostop, 0, 1)
        lay.addWidget(self._led_autostop, 0, 2, alignment=Qt.AlignLeft)
        lay.setColumnStretch(0, 3)
        lay.setColumnStretch(1, 2)
        lay.setColumnStretch(2, 2)

        wid.setStyleSheet("""
            .QLabel{
                min-width: 6.5em; max-width: 6.5em; min-height: 1em;
            }""")
        return wid

    def _setupLogWidget(self):
        self._log = PyDMLogLabel(
            self, self._inj_prefix + ':Log-Mon',
            ['Remaining time', ])

        wid = QGroupBox('Log')
        lay = QHBoxLayout(wid)
        lay.addWidget(self._log)
        return wid

    def _setupMonitorWidget(self):
        self.wid_mon = MonitorSummaryWidget(self)

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.wid_mon, 0, 0)
        return wid

    # ---- auxiliary commands ----

    @Slot(int)
    def _handle_injtype_settings_vis(self, new_type):
        is_sb = new_type == _Const.InjTypeSel.SingleBunch
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
        is_topoup = new_mode == _Const.InjMode.TopUp
        self.wid_tudtls.setVisible(is_topoup)
        self._pb_topup.setVisible(is_topoup)
        self.wid_dcdtls.setVisible(not is_topoup)
        self._pb_tiinj.setVisible(not is_topoup)
        self.wid_tusts.setVisible(is_topoup)

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

    def mouseDoubleClickEvent(self, event):
        """Implement mouseDoubleClickEvent."""
        if event.button() == Qt.LeftButton:
            point = event.pos()
            if self.wid_curr.geometry().contains(point):
                self.showStatus.emit()
            elif self.wid_shift.geometry().contains(point):
                self.showStatus.emit()
            elif self.wid_egun.geometry().contains(point):
                self.showEgun.emit()
            elif self.wid_mon.geometry().contains(point):
                self.showMonitor.emit()
        return super().mouseDoubleClickEvent(event)

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
