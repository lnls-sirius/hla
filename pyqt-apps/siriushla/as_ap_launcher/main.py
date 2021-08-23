"""Interface to handle main operation commands."""

import qtawesome as qta

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QWidget, QGroupBox, QPushButton, QLabel, \
    QGridLayout, QApplication, QHBoxLayout, QVBoxLayout
from pydm.widgets import PyDMPushButton, PyDMLabel

from siriuspy.envars import VACA_PREFIX
from siriuspy.namesys.implementation import SiriusPVName
from siriuspy.search import LLTimeSearch as _LLTimeSearch

from ..util import get_appropriate_color, connect_newprocess
from ..widgets import SiriusMainWindow, PyDMStateButton, \
    SiriusEnumComboBox, SiriusLedState, PyDMLogLabel
from ..as_ti_control import BucketList, EVGInjectionLed
from ..as_ap_machshift import MachShiftLabel
from ..as_ap_injection import InjSysStbyControlWidget, InjDiagLed, \
    MonitorSummaryWidget
from ..as_rf_control import RFKillBeamButton
from .menu import get_object


class MainLauncher(SiriusMainWindow):
    """Main Launcher."""

    showMonitor = Signal()
    showStatus = Signal()
    showEgun = Signal()
    showInjection = Signal()

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
        connect_newprocess(
            self, 'sirius-hla-as-ap-injection.py',
            parent=self, signal=self.showInjection)

        # set focus policy
        self.setFocus(True)
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        # Machine Shift
        self.wid_shift = QGroupBox('Machine Shift')
        self.wid_shift.setStyleSheet('QGroupBox{min-width: 7em;}')
        machshift_pvname = SiriusPVName(
            'AS-Glob:AP-MachShift:Mode-Sel').substitute(prefix=self._prefix)
        cbox_shift_mode = SiriusEnumComboBox(self, machshift_pvname)
        label_shift_mode = MachShiftLabel()
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
        self.wid_inject = QGroupBox('Injection')

        # # Settings
        label_injsett = QLabel(
            '<h4>Settings</h4>', self, alignment=Qt.AlignCenter)
        led_injsett = InjDiagLed(self)

        injctrl_dev = SiriusPVName('AS-Glob:AP-InjCtrl')
        injctrl_dev = injctrl_dev.substitute(prefix=self._prefix)

        # # Auto Stop
        label_injauto = QLabel(
            '<h4>AutoStop</h4>', self, alignment=Qt.AlignCenter)
        but_injauto = PyDMStateButton(
            self, injctrl_dev.substitute(propty='AutoStop-Sel'))
        led_injauto = SiriusLedState(
            self, injctrl_dev.substitute(propty='AutoStop-Sts'))

        # # controls
        label_inj = QLabel(
            '<h4>Control</h4>', self, alignment=Qt.AlignCenter)
        but_injstop = PyDMPushButton(
            self, label='', icon=qta.icon('mdi.stop'), pressValue=0,
            init_channel=injctrl_dev.substitute(propty='Stop-Cmd'))
        but_injstop.setObjectName('bt')
        but_injstop.setStyleSheet(
            '#bt{min-width:25px; max-width:25px; icon-size:20px;}')
        but_injstart = PyDMPushButton(
            self, label='', icon=qta.icon('mdi.play'), pressValue=0,
            init_channel=injctrl_dev.substitute(propty='Start-Cmd'))
        but_injstart.setObjectName('bt')
        but_injstart.setStyleSheet(
            '#bt{min-width:25px; max-width:25px; icon-size:20px;}')
        lay_inject_sel = QHBoxLayout()
        lay_inject_sel.setSpacing(8)
        lay_inject_sel.setAlignment(Qt.AlignCenter)
        lay_inject_sel.addWidget(but_injstop)
        lay_inject_sel.addWidget(but_injstart)
        led_injsts = EVGInjectionLed(self, self._prefix)
        label_injcnt = PyDMLabel(self)
        label_injcnt.setToolTip(
            'Count injection pulses when Egun Trigger is enabled.')
        label_injcnt.channel = SiriusPVName(
            'AS-Glob:AP-CurrInfo:InjCount-Mon').substitute(prefix=self._prefix)
        label_injcnt.setStyleSheet('QLabel{max-width: 3.5em;}')
        lay_inject_sts = QHBoxLayout()
        lay_inject_sts.addWidget(led_injsts)
        lay_inject_sts.addStretch()
        lay_inject_sts.addWidget(label_injcnt)

        # # Bucket List
        bucket_list = BucketList(self, prefix=self._prefix, min_size=15)
        pbt = QPushButton('>', self)
        pbt.clicked.connect(self._toggle_expand_horizontal)
        pbt.setStyleSheet('max-width: 0.8em;')
        self.expandwid_hor = bucket_list
        self.expandwid_hor.setVisible(False)

        lay_inj = QGridLayout(self.wid_inject)
        lay_inj.setAlignment(Qt.AlignCenter)
        lay_inj.setVerticalSpacing(5)
        lay_inj.setHorizontalSpacing(12)
        lay_inj.addWidget(label_injsett, 0, 0)
        lay_inj.addWidget(led_injsett, 1, 0)
        lay_inj.addWidget(label_injauto, 0, 1)
        lay_inj.addWidget(but_injauto, 1, 1)
        lay_inj.addWidget(led_injauto, 2, 1)
        lay_inj.addWidget(label_inj, 0, 2, alignment=Qt.AlignCenter)
        lay_inj.addLayout(lay_inject_sel, 1, 2, alignment=Qt.AlignCenter)
        lay_inj.addLayout(lay_inject_sts, 2, 2, alignment=Qt.AlignCenter)
        lay_inj.addWidget(pbt, 2, 3, alignment=Qt.AlignBottom)
        lay_inj.addWidget(bucket_list, 0, 4, 3, 1)

        # Current
        label_curr = PyDMLabel(self, 'SI-Glob:AP-CurrInfo:Current-Mon')
        label_curr.showUnits = True
        label_curr.setStyleSheet("""
            QLabel{
                font-size: 16pt; qproperty-alignment: AlignCenter;
                min-width: 6em; max-width: 6em;
        }""")
        self.wid_curr = QGroupBox('Current')
        lay_curr = QHBoxLayout(self.wid_curr)
        lay_curr.addWidget(label_curr)

        # # Gamma Shutter
        # self._led_gmsht = SiriusLedAlert(
        #     self, 'AS-Glob:PP-GammaShutter:Status-Mon')
        # self.wid_gmsht = QGroupBox('Gamma')
        # lay_gmsht = QHBoxLayout(self.wid_gmsht)
        # lay_gmsht.addWidget(self._led_gmsht)

        # RF Kill Beam
        self.wid_rfkill = QGroupBox('RF Kill Beam')
        self.wid_rfkill.setObjectName('RFKillBeam')
        rfkill_bt = RFKillBeamButton(self)
        rfkill_lay = QGridLayout(self.wid_rfkill)
        rfkill_lay.addWidget(rfkill_bt)

        self.wid_injlog = QGroupBox('Injection Log')
        label_injlog = PyDMLogLabel(
            self, injctrl_dev.substitute(propty='Log-Mon'),
            replace=['Remaining time', ])
        lay_injlog = QGridLayout(self.wid_injlog)
        lay_injlog.addWidget(label_injlog, 0, 0)

        self.wid_mon = MonitorSummaryWidget(self, self._prefix)

        # menu buttons
        self.wid_pbt = QPushButton('v', self)
        self.wid_pbt.clicked.connect(self._toggle_expand)
        self.wid_pbt.setStyleSheet('max-width: 0.8em;')
        self.expandwid = get_object(ismenubar=False, parent=self)
        self.expandwid.layout().setContentsMargins(0, 0, 0, 0)
        self.expandwid.layout().setSpacing(4)
        self.expandwid.setVisible(False)

        hlay1 = QHBoxLayout()
        hlay1.setContentsMargins(0, 0, 0, 0)
        hlay1.addWidget(self.wid_shift)
        hlay1.addWidget(self.wid_injsys)
        hlay1.addWidget(self.wid_egun)
        hlay1.addWidget(self.wid_inject)
        hlay1.addWidget(self.wid_rfkill)
        hlay1.addWidget(self.wid_curr)

        hlay2 = QHBoxLayout()
        hlay2.setContentsMargins(0, 0, 0, 0)
        hlay2.addWidget(self.wid_injlog)
        hlay2.addWidget(self.wid_mon)
        hlay2.addWidget(self.wid_pbt, alignment=Qt.AlignLeft | Qt.AlignBottom)

        cw = QWidget(self)
        lay = QVBoxLayout(cw)
        lay.addLayout(hlay1)
        lay.addLayout(hlay2)
        lay.addWidget(self.expandwid)
        self.setCentralWidget(cw)

    def _toggle_expand(self):
        self.expandwid.setVisible(self.expandwid.isHidden())
        text = 'v' if self.expandwid.isHidden() else '^'
        self.sender().setText(text)
        self.centralWidget().adjustSize()
        self.adjustSize()

    def _toggle_expand_horizontal(self):
        self.expandwid_hor.setVisible(self.expandwid_hor.isHidden())
        text = '>' if self.expandwid_hor.isHidden() else '<'
        self.sender().setText(text)
        self.sender().parent().adjustSize()
        self.centralWidget().adjustSize()
        self.adjustSize()

    def mouseDoubleClickEvent(self, ev):
        """Implement mouseDoubleClickEvent."""
        if ev.button() == Qt.LeftButton:
            point = ev.pos()
            if self.wid_curr.geometry().contains(point):
                self.showStatus.emit()
            elif self.wid_shift.geometry().contains(point):
                self.showStatus.emit()
            elif self.wid_egun.geometry().contains(point):
                self.showEgun.emit()
            elif self.wid_mon.geometry().contains(point):
                self.showMonitor.emit()
            elif self.wid_inject.geometry().contains(point):
                self.showInjection.emit()
        return super().mouseDoubleClickEvent(ev)
