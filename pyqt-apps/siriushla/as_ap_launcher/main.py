"""Interface to handle main operation commands."""

import qtawesome as qta

from qtpy.QtCore import Qt, Slot, Signal, QEvent
from qtpy.QtWidgets import QWidget, QGroupBox, QPushButton, QLabel, \
    QGridLayout, QApplication, QHBoxLayout
from pydm.widgets import PyDMPushButton, PyDMLabel

from siriuspy.envars import VACA_PREFIX
from siriuspy.namesys.implementation import SiriusPVName
from siriuspy.injctrl.csdev import Const as _InjConst

from ..util import get_appropriate_color, connect_newprocess
from ..widgets import SiriusMainWindow, PyDMStateButton, SiriusLabel, \
    SiriusEnumComboBox, SiriusLedState, PyDMLogLabel, SiriusConnectionSignal, \
    SiriusSpinbox
from ..as_ti_control import BucketList, EVGInjectionLed, EVGInjectionButton
from ..as_ap_machshift import MachShiftLabel
from ..as_ap_injection import InjSysStbyControlWidget, InjDiagLed, \
    MonitorSummaryWidget, ClockLabel
from ..as_ap_injection import RFKillBeamButton
from .menu import get_object


class MainLauncher(SiriusMainWindow):
    """Main Launcher."""

    showMonitor = Signal()
    showStatus = Signal()
    showEgun = Signal()

    def __init__(self, parent=None, prefix=VACA_PREFIX):
        """Init."""
        super().__init__(parent)
        self._prefix = prefix

        # window settings
        self.setObjectName('ASApp')
        self.setWindowTitle('Sirius Launcher')
        self.setWindowIcon(
            qta.icon('mdi.rocket', color=get_appropriate_color('AS')))

        screens = QApplication.screens()
        screen_idx = 3 if len(screens) == 8 else 0
        topleft = screens[screen_idx].geometry().topLeft()
        self.move(topleft.x(), topleft.y()+20)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        # menubar
        menubar = get_object(ismenubar=True)
        menubar.setNativeMenuBar(False)
        self.setMenuBar(menubar)
        self._setupUi()

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

        # set focus policy
        self.setFocus(True)
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        # Machine Shift
        self.wid_shift = QGroupBox('Machine Shift')
        machshift_pvname = SiriusPVName(
            'AS-Glob:AP-MachShift:Mode-Sel').substitute(prefix=self._prefix)
        cbox_shift_mode = SiriusEnumComboBox(self, machshift_pvname)
        label_shift_mode = MachShiftLabel(self, self._prefix)
        label_shift_mode.label.setStyleSheet(
            'QLabel{max-height: 2em; min-width: 7em;}')
        lay_shift = QGridLayout(self.wid_shift)
        lay_shift.setVerticalSpacing(5)
        lay_shift.setAlignment(Qt.AlignCenter)
        lay_shift.addWidget(cbox_shift_mode, 1, 0)
        lay_shift.addWidget(label_shift_mode, 2, 0)

        # Injection System
        self.wid_injsys = QGroupBox('Inj.System')
        wid_injsys = InjSysStbyControlWidget(
            self, self._prefix, is_summary=True)
        lay_injsys = QGridLayout(self.wid_injsys)
        lay_injsys.setAlignment(Qt.AlignCenter)
        lay_injsys.setContentsMargins(0, 0, 0, 0)
        lay_injsys.addWidget(wid_injsys)

        # Egun triggers
        self.wid_egun = QGroupBox('Egun Trig.')
        self.wid_egun.setStyleSheet('min-width: 5em;')
        egun_dev = SiriusPVName(
            'LI-01:EG-TriggerPS').substitute(prefix=self._prefix)
        but_egun_trigger = PyDMStateButton(
            self, egun_dev.substitute(propty_name='enable'))
        led_egun_trigger = SiriusLedState(
            self, egun_dev.substitute(propty_name='enablereal'))
        lay_egun = QGridLayout(self.wid_egun)
        lay_egun.setVerticalSpacing(5)
        lay_egun.addWidget(but_egun_trigger, 1, 0)
        lay_egun.addWidget(led_egun_trigger, 2, 0)

        # injection control
        injctrl_dev = SiriusPVName('AS-Glob:AP-InjCtrl')
        injctrl_dev = injctrl_dev.substitute(prefix=self._prefix)

        self.wid_inject = QGroupBox('Injection')
        self.ch_injmode = SiriusConnectionSignal(
            injctrl_dev.substitute(propty='Mode-Sts'))
        self.ch_injmode.new_value_signal[int].connect(
            self._handle_injmode_settings_vis)

        # # Settings
        label_sett = QLabel(
            '<h4>Sett.</h4>', self, alignment=Qt.AlignCenter)
        led_sett = InjDiagLed(self)
        self.wid_injsett = QWidget()
        lay_injsett = QGridLayout(self.wid_injsett)
        lay_injsett.setContentsMargins(0, 0, 0, 0)
        lay_injsett.setAlignment(Qt.AlignTop)
        lay_injsett.addWidget(label_sett, 0, 0)
        lay_injsett.addWidget(led_sett, 1, 0)

        # # Auto Stop
        self.label_injauto = QLabel(
            '<h4>AutoStop</h4>', self, alignment=Qt.AlignCenter)
        self.but_injauto = PyDMStateButton(
            self, injctrl_dev.substitute(propty='AutoStop-Sel'))
        self.led_injauto = SiriusLedState(
            self, injctrl_dev.substitute(propty='AutoStop-Sts'))
        self.wid_injauto = QWidget()
        self.wid_injauto.setObjectName('wid')
        self.wid_injauto.setStyleSheet("#wid{min-width: 8em; max-width: 8em;}")
        lay_injauto = QGridLayout(self.wid_injauto)
        lay_injauto.setContentsMargins(0, 0, 0, 0)
        lay_injauto.setAlignment(Qt.AlignTop)
        lay_injauto.addWidget(self.label_injauto, 0, 0)
        lay_injauto.addWidget(self.but_injauto, 1, 0)
        lay_injauto.addWidget(self.led_injauto, 2, 0)

        # # Top-up status
        label_tusts = QLabel(
            '<h4>Status</h4>', self, alignment=Qt.AlignCenter)
        label_tunow = ClockLabel(self)
        label_tunow.setStyleSheet('max-height:2em;')
        label_tunxt = SiriusLabel(
            self, injctrl_dev.substitute(propty='TopUpNextInj-Mon'))
        label_tunxt.displayFormat = SiriusLabel.DisplayFormat.Time
        label_tunxt.setAlignment(Qt.AlignCenter)
        label_tunxt.setStyleSheet('max-height:2em;')
        but_round = PyDMPushButton(
            self, '', qta.icon('mdi.tilde'), 1, False,
            injctrl_dev.substitute(propty='TopUpNextInjRound-Cmd'))
        but_round.setObjectName('but')
        but_round.setStyleSheet(
            '#but{min-width:18px; max-width:18px; icon-size:16px;}')
        self.wid_tusts = QWidget()
        self.wid_tusts.setObjectName('wid')
        self.wid_tusts.setStyleSheet("#wid{min-width: 8em; max-width: 8em;}")
        lay_tusts = QGridLayout(self.wid_tusts)
        lay_tusts.setContentsMargins(0, 0, 0, 0)
        lay_tusts.setAlignment(Qt.AlignTop)
        lay_tusts.addWidget(label_tusts, 0, 0, 1, 2)
        lay_tusts.addWidget(QLabel('Now:', self), 1, 0)
        lay_tusts.addWidget(label_tunow, 1, 1)
        lay_tusts.addWidget(QLabel('Next:', self), 2, 0)
        lay_tusts.addWidget(label_tunxt, 2, 1)
        lay_tusts.addWidget(but_round, 2, 2)
        self.wid_tusts.setVisible(False)

        # # Control
        label_inj = QLabel(
            '<h4>Control</h4>', self, alignment=Qt.AlignCenter)
        self.but_tiinj = EVGInjectionButton(self, self._prefix)
        self.but_topup = PyDMStateButton(
            self, injctrl_dev.substitute(propty='TopUpState-Sel'))
        self.but_topup.setVisible(False)
        lay_inject_sel = QGridLayout()
        lay_inject_sel.setAlignment(Qt.AlignCenter)
        lay_inject_sel.addWidget(self.but_tiinj, 0, 0)
        lay_inject_sel.addWidget(self.but_topup, 0, 0)
        led_injsts = EVGInjectionLed(self, self._prefix)
        label_injcnt = PyDMLabel(self)
        label_injcnt.setToolTip(
            'Count injection pulses when Egun Trigger is enabled.')
        label_injcnt.channel = SiriusPVName(
            'AS-Glob:AP-CurrInfo:InjCount-Mon').substitute(prefix=self._prefix)
        label_injcnt.setStyleSheet('QLabel{max-width: 3.5em;}')
        lay_inject_sts = QHBoxLayout()
        lay_inject_sts.setContentsMargins(0, 0, 0, 0)
        lay_inject_sts.setAlignment(Qt.AlignTop)
        lay_inject_sts.addWidget(led_injsts)
        lay_inject_sts.addWidget(label_injcnt)
        self.wid_injctrl = QWidget()
        lay_injctrl = QGridLayout(self.wid_injctrl)
        lay_injctrl.setContentsMargins(0, 0, 0, 0)
        lay_injctrl.setAlignment(Qt.AlignTop)
        lay_injctrl.addWidget(label_inj, 0, 2, alignment=Qt.AlignCenter)
        lay_injctrl.addLayout(lay_inject_sel, 1, 2, alignment=Qt.AlignCenter)
        lay_injctrl.addLayout(lay_inject_sts, 2, 2, alignment=Qt.AlignCenter)

        # # Injection Auxiliary section
        self.wid_injlog = QGroupBox('Injection Log')
        label_injlog = PyDMLogLabel(
            self, injctrl_dev.substitute(propty='Log-Mon'),
            replace=['Remaining time', ])
        lay_injlog = QGridLayout(self.wid_injlog)
        lay_injlog.addWidget(label_injlog, 0, 0)
        self.wid_injlog.setVisible(False)

        self.wid_mon = MonitorSummaryWidget(self, self._prefix)
        self.wid_mon.setVisible(False)

        # # Target Current
        self._ld_currtgt = QLabel(
            '<h4>Target Curr.</h4>', self, alignment=Qt.AlignCenter)
        self._sb_currtgt = SiriusSpinbox(
            self, injctrl_dev.substitute(propty='TargetCurrent-SP'))
        self._sb_currtgt.showStepExponent = False
        self._lb_currtgt = PyDMLabel(
            self, injctrl_dev.substitute(propty='TargetCurrent-RB'))
        self._lb_currtgt.showUnits = True
        self._wid_tcurr = QWidget()
        lay_tcurr = QGridLayout(self._wid_tcurr)
        lay_tcurr.setContentsMargins(0, 0, 0, 0)
        lay_tcurr.setAlignment(Qt.AlignTop)
        lay_tcurr.addWidget(self._ld_currtgt, 0, 0)
        lay_tcurr.addWidget(self._sb_currtgt, 1, 0)
        lay_tcurr.addWidget(self._lb_currtgt, 2, 0)

        # # Bucket List
        self._bucket_list = BucketList(self, prefix=self._prefix, min_size=15)

        self.wid_fill = QWidget()
        lay_fill = QGridLayout(self.wid_fill)
        lay_fill.setContentsMargins(0, 0, 0, 0)
        lay_fill.setHorizontalSpacing(9)
        lay_fill.addWidget(self._wid_tcurr, 0, 0)
        lay_fill.addWidget(self._bucket_list, 0, 1)
        self.wid_fill.setVisible(False)

        pbt_aux = QPushButton('v', self)
        pbt_aux.setToolTip('Show Injection Auxiliary section.')
        pbt_aux.clicked.connect(self._toggle_show_injaux)
        pbt_aux.setStyleSheet('QPushButton{max-width: 0.8em;}')
        pbt_bl = QPushButton('>', self)
        pbt_bl.setToolTip('Show bucket list and target current controls.')
        pbt_bl.clicked.connect(self._toggle_show_bucketlist)
        pbt_bl.setStyleSheet('QPushButton{max-width: 0.8em;}')

        lay_inj = QGridLayout(self.wid_inject)
        lay_inj.setAlignment(Qt.AlignTop)
        lay_inj.setVerticalSpacing(5)
        lay_inj.setHorizontalSpacing(12)
        lay_inj.addWidget(self.wid_injsett, 0, 0, 2, 1)
        lay_inj.addWidget(self.wid_injauto, 0, 1, 2, 1)
        lay_inj.addWidget(self.wid_tusts, 0, 1, 2, 1)
        lay_inj.addWidget(self.wid_injctrl, 0, 2, 2, 1)
        lay_inj.addWidget(pbt_bl, 0, 3, alignment=Qt.AlignTop)
        lay_inj.addWidget(pbt_aux, 1, 3, alignment=Qt.AlignBottom)
        lay_inj.addWidget(self.wid_fill, 0, 4, 2, 1)

        # Current
        curr_pvname = SiriusPVName(
            'SI-Glob:AP-CurrInfo:Current-Mon').substitute(prefix=self._prefix)
        self.label_curr = PyDMLabel(self, curr_pvname)
        self.label_curr.showUnits = True
        self.label_curr.setStyleSheet("""
            QLabel{
                font-size: 18pt; qproperty-alignment: AlignCenter;
                min-width: 6em; max-width: 6em;
            }""")
        self.wid_curr = QGroupBox('Current')
        lay_curr = QHBoxLayout(self.wid_curr)
        lay_curr.addWidget(self.label_curr)

        # RF Kill Beam
        self.wid_rfkill = QGroupBox('RF Kill Beam')
        self.wid_rfkill.setObjectName('RFKillBeam')
        rfkill_bt = RFKillBeamButton(self)
        rfkill_lay = QGridLayout(self.wid_rfkill)
        rfkill_lay.addWidget(rfkill_bt)

        # menu buttons
        self.wid_pbt = QPushButton('v', self)
        self.wid_pbt.clicked.connect(self._toggle_show_menubutton)
        self.wid_pbt.setStyleSheet('QPushButton{max-width: 0.8em;}')
        self._menubutton = get_object(ismenubar=False, parent=self)
        self._menubutton.layout().setContentsMargins(0, 0, 0, 0)
        self._menubutton.layout().setSpacing(4)
        self._menubutton.setVisible(False)

        hlay1 = QHBoxLayout()
        hlay1.setContentsMargins(0, 0, 0, 0)
        hlay1.addWidget(self.wid_shift)
        hlay1.addWidget(self.wid_injsys)
        hlay1.addWidget(self.wid_egun)
        hlay1.addWidget(self.wid_inject)
        hlay1.addWidget(self.wid_curr)
        hlay1.addWidget(self.wid_rfkill)

        hlay2 = QHBoxLayout()
        hlay2.setContentsMargins(0, 0, 0, 0)
        hlay2.addWidget(self.wid_injlog)
        hlay2.addWidget(self.wid_mon)

        cwid = QWidget(self)
        lay = QGridLayout(cwid)
        lay.addLayout(hlay1, 0, 0)
        lay.addLayout(hlay2, 1, 0)
        lay.addWidget(self._menubutton, 2, 0, 1, 2)
        lay.addWidget(
            self.wid_pbt, 0, 1, 2, 1, alignment=Qt.AlignRight | Qt.AlignBottom)
        self.setCentralWidget(cwid)

    def _toggle_show_menubutton(self):
        self._menubutton.setVisible(self._menubutton.isHidden())
        text = 'v' if self._menubutton.isHidden() else '^'
        self.sender().setText(text)
        self.centralWidget().adjustSize()
        self.adjustSize()

    def _toggle_show_bucketlist(self):
        show = self.wid_fill.isHidden()
        self.wid_fill.setVisible(show)
        text = '<' if show else '>'
        tooltip = ('Hide' if show else 'Show')+' bucket list controls.'
        self.sender().setText(text)
        self.sender().setToolTip(tooltip)
        self.sender().parent().adjustSize()
        self.centralWidget().adjustSize()
        self.adjustSize()

    def _toggle_show_injaux(self):
        show = self.wid_mon.isHidden()
        self.wid_mon.setVisible(show)
        self.wid_injlog.setVisible(show)
        text = '^' if show else 'v'
        tooltip = ('Hide' if show else 'Show')+' Injection Auxiliary section.'
        self.sender().setText(text)
        self.sender().setToolTip(tooltip)
        self.sender().parent().adjustSize()
        self.centralWidget().adjustSize()
        self.adjustSize()

    @Slot(int)
    def _handle_injmode_settings_vis(self, new_mode):
        is_topup = new_mode == _InjConst.InjMode.TopUp
        self.label_injauto.setVisible(not is_topup)
        self.but_injauto.setVisible(not is_topup)
        self.led_injauto.setVisible(not is_topup)
        self.wid_tusts.setVisible(is_topup)
        self.but_tiinj.setVisible(not is_topup)
        self.but_topup.setVisible(is_topup)

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
            self.label_curr.setStyleSheet(
                'QLabel{'
                '    font-size: '+str(fontsize+8)+'pt;'
                '    qproperty-alignment: AlignCenter;'
                '    min-width: 6em; max-width: 6em;'
                '}')
            self.ensurePolished()
