"""Kyma APU Control module."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGroupBox, QGridLayout, QLabel, \
    QHBoxLayout, QSizePolicy as QSzPlcy, QSpacerItem, QPushButton
import qtawesome as qta
from pydm.widgets import PyDMLabel, PyDMPushButton, PyDMSpinbox

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.search import IDSearch

from siriushla.util import connect_window, get_appropriate_color
from siriushla.widgets import SiriusMainWindow, PyDMLed, SiriusLedAlert, \
    SiriusLedState, PyDMLedMultiChannel, PyDMStateButton
from siriushla.as_ps_diag import PSGraphMonWidget

from .auxiliary_dialogs import APUAlarmDetails, APUInterlockDetails, \
    APUHardLLDetails, APUCorrs


class APUControlWindow(SiriusMainWindow):
    """Kyma APU Control Window."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        self._prefix = prefix
        self._device = _PVName(device)
        self._beamline = IDSearch.conv_idname_2_beamline(self._device)
        self.dev_pref = prefix + device
        self.setWindowTitle(device+' Control Window - '+self._beamline)
        self.setObjectName('IDApp')
        color = get_appropriate_color('ID')
        self.setWindowIcon(
            qta.icon('mdi.current-ac', 'mdi.current-ac', 'mdi.equal', options=[
                dict(scale_factor=0.48, color=color, offset=(-0.16, -0.01)),
                dict(scale_factor=0.48, color=color, offset=(0.16, -0.01)),
                dict(scale_factor=2.4, color=color, offset=(0.0, 0.0))]))
        self._setupUi()

    def _setupUi(self):
        self._label_title = QLabel(
            '<h3>'+self._device+' Control - '+self._beamline+'</h3 >', self,
            alignment=Qt.AlignCenter)
        self._label_title.setStyleSheet('max-height:1.29em;')

        cw = QWidget()
        lay = QGridLayout(cw)
        lay.addWidget(self._label_title, 0, 0, 1, 3)
        lay.addWidget(self._mainControlsWidget(), 1, 0, 2, 1)
        lay.addWidget(self._ctrlModeWidget(), 1, 1)
        lay.addWidget(self._beamLinesCtrlWidget(), 2, 1)
        lay.addWidget(self._auxCommandsWidget(), 3, 0)
        lay.addWidget(self._statusWidget(), 3, 1)
        lay.addWidget(self._corrsControlWidget(), 4, 0, 1, 2)
        lay.setRowStretch(0, 1)
        lay.setRowStretch(1, 2)
        lay.setRowStretch(2, 3)
        lay.setRowStretch(4, 5)
        self.setCentralWidget(cw)

    def _mainControlsWidget(self):
        self._ld_phs = QLabel('Phase [mm]', self)
        self._sb_phs = PyDMSpinbox(self, self.dev_pref+':Phase-SP')
        self._sb_phs.showStepExponent = False
        self._lb_phs = PyDMLabel(self, self.dev_pref+':Phase-Mon')

        self._ld_kx = QLabel('Kx', self)
        self._sb_kx = PyDMSpinbox(self, self.dev_pref+':Kx-SP')
        self._sb_kx.showStepExponent = False
        self._lb_kx = PyDMLabel(self, self.dev_pref+':Kx-Mon')

        self._ld_phsspd = QLabel('Phase Speed\n[mm/s]', self)
        self._sb_phsspd = PyDMSpinbox(self, self.dev_pref+':PhaseSpeed-SP')
        self._sb_phsspd.showStepExponent = False
        self._lb_phsspd = PyDMLabel(self, self.dev_pref+':PhaseSpeed-Mon')
        self._ld_ismov = QLabel('Motion', self)
        self._pb_start = PyDMPushButton(
            self, label='', icon=qta.icon('fa5s.play'))
        self._pb_start.setToolTip(
            'Start automatic motion towards previously entered setpoint.')
        self._pb_start.channel = self.dev_pref+':DevCtrl-Cmd'  # Start
        self._pb_start.pressValue = 3
        self._pb_start.setObjectName('Start')
        self._pb_start.setStyleSheet(
            '#Start{min-width:30px; max-width:30px; icon-size:25px;}')
        self._pb_stop = PyDMPushButton(
            self, label='', icon=qta.icon('fa5s.stop'))
        self._pb_stop.setToolTip('Stop all motion, lock all brakes.')
        self._pb_stop.channel = self.dev_pref+':DevCtrl-Cmd'  # Stop
        self._pb_stop.pressValue = 1
        self._pb_stop.setObjectName('Stop')
        self._pb_stop.setStyleSheet(
            '#Stop{min-width:30px; max-width:30px; icon-size:25px;}')
        self._led_ismov = SiriusLedState(self, self.dev_pref+':Moving-Mon')
        self._led_motenbl = SiriusLedState(
            self, self.dev_pref+':MotorsEnbld-Mon')
        hbox_motion = QHBoxLayout()
        hbox_motion.setSpacing(15)
        hbox_motion.addWidget(self._pb_start)
        hbox_motion.addWidget(self._pb_stop)
        hbox_motion.addWidget(self._led_ismov)
        hbox_motion.addWidget(self._led_motenbl)

        gbox_main = QGroupBox('Main Controls', self)
        lay_main = QGridLayout(gbox_main)
        lay_main.addWidget(self._ld_phs, 0, 0)
        lay_main.addWidget(self._sb_phs, 0, 1)
        lay_main.addWidget(self._lb_phs, 0, 2)
        lay_main.addWidget(self._ld_kx, 1, 0)
        lay_main.addWidget(self._sb_kx, 1, 1)
        lay_main.addWidget(self._lb_kx, 1, 2)
        lay_main.addWidget(self._ld_phsspd, 2, 0)
        lay_main.addWidget(self._sb_phsspd, 2, 1)
        lay_main.addWidget(self._lb_phsspd, 2, 2)
        lay_main.addItem(
            QSpacerItem(1, 10, QSzPlcy.Ignored, QSzPlcy.Fixed), 3, 0)
        lay_main.addWidget(self._ld_ismov, 4, 0)
        lay_main.addLayout(hbox_motion, 4, 1, 1, 2)
        return gbox_main

    def _statusWidget(self):
        self._ld_alarm = QLabel(
            'Alarms', self, alignment=Qt.AlignCenter)
        self._led_alarm = SiriusLedAlert(self, self.dev_pref+':Alarm-Mon')
        self._pb_alarmdetail = QPushButton(
            qta.icon('fa5s.ellipsis-h'), '', self)
        self._pb_alarmdetail.setObjectName('dtl')
        self._pb_alarmdetail.setStyleSheet(
            "#dtl{min-width:25px; max-width:25px; icon-size:20px;}")
        connect_window(
            self._pb_alarmdetail, APUAlarmDetails, self,
            prefix=self._prefix, device=self._device)

        self._ld_intlk = QLabel(
            'Interlocks', self, alignment=Qt.AlignCenter)
        self._led_intlkresume = PyDMLedMultiChannel(
            self, {self.dev_pref+':IntlkInStop-Mon': 0,
                   self.dev_pref+':IntlkInEOpnGap-Mon': 0,
                   self.dev_pref+':IntlkOutPwrEnbld-Mon': 1})
        self._pb_intlkdetail = QPushButton(
            qta.icon('fa5s.ellipsis-h'), '', self)
        self._pb_intlkdetail.setObjectName('dtl')
        self._pb_intlkdetail.setStyleSheet(
            "#dtl{min-width:25px; max-width:25px; icon-size:20px;}")
        connect_window(
            self._pb_intlkdetail, APUInterlockDetails, self,
            prefix=self._prefix, device=self._device)

        self._ld_hwsys = QLabel(
            'Hardware\n&LowLevel', self, alignment=Qt.AlignCenter)
        self._led_hwsysresume = PyDMLedMultiChannel(
            self,
            {self.dev_pref+':StateHw-Mon': {'value': [0x4C, 0x3C],
                                            'comp': 'in'},
             self.dev_pref+':State-Mon': {'value': [1, 4], 'comp': 'in'},
             self.dev_pref+':IsOperational-Mon': 1})
        self._led_hwsysresume.offColor = PyDMLed.Yellow
        self._led_hwsysresume.onColor = PyDMLed.LightGreen
        self._pb_hwsysdetail = QPushButton(
            qta.icon('fa5s.ellipsis-h'), '', self)
        self._pb_hwsysdetail.setObjectName('dtl')
        self._pb_hwsysdetail.setStyleSheet(
            "#dtl{min-width:25px; max-width:25px; icon-size:20px;}")
        connect_window(
            self._pb_hwsysdetail, APUHardLLDetails, self,
            prefix=self._prefix, device=self._device)

        self._ld_reset = QLabel(
            'Reset', self, alignment=Qt.AlignCenter)
        self._pb_reset = PyDMPushButton(
            self, label='', icon=qta.icon('fa5s.sync'))
        self._pb_reset.setToolTip('Reset active alarms.')
        self._pb_reset.channel = self.dev_pref+':DevCtrl-Cmd'  # Reset
        self._pb_reset.pressValue = 2
        self._pb_reset.setObjectName('Reset')
        self._pb_reset.setStyleSheet(
            '#Reset{min-width:30px; max-width:30px; icon-size:25px;}')

        gbox_alrmintlk = QGroupBox('Status')
        lay_alrmintlk = QGridLayout(gbox_alrmintlk)
        lay_alrmintlk.addWidget(self._pb_alarmdetail, 0, 0)
        lay_alrmintlk.addWidget(self._ld_alarm, 0, 1)
        lay_alrmintlk.addWidget(self._led_alarm, 0, 2)
        lay_alrmintlk.addWidget(self._pb_intlkdetail, 1, 0)
        lay_alrmintlk.addWidget(self._ld_intlk, 1, 1)
        lay_alrmintlk.addWidget(self._led_intlkresume, 1, 2)
        lay_alrmintlk.addWidget(self._pb_hwsysdetail, 2, 0)
        lay_alrmintlk.addWidget(self._ld_hwsys, 2, 1)
        lay_alrmintlk.addWidget(self._led_hwsysresume, 2, 2)
        lay_alrmintlk.addWidget(self._ld_reset, 3, 1)
        lay_alrmintlk.addWidget(self._pb_reset, 3, 2)
        return gbox_alrmintlk

    def _ctrlModeWidget(self):
        self._led_ctrlmode = PyDMLed(self, self.dev_pref+':IsRemote-Mon')
        self._led_ctrlmode.offColor = PyDMLed.Red
        self._led_ctrlmode.onColor = PyDMLed.LightGreen
        self._lb_ctrlmode = PyDMLabel(self, self.dev_pref+':Interface-Mon')

        gbox_ctrlmode = QGroupBox('Control Mode')
        lay_ctrlmode = QHBoxLayout(gbox_ctrlmode)
        lay_ctrlmode.setAlignment(Qt.AlignCenter)
        lay_ctrlmode.addWidget(self._led_ctrlmode)
        lay_ctrlmode.addWidget(self._lb_ctrlmode)
        return gbox_ctrlmode

    def _beamLinesCtrlWidget(self):
        self._ld_blinesenbl = QLabel('Enable', self)
        self._sb_blinesenbl = PyDMStateButton(
            self, self.dev_pref+':BeamLineCtrlEnbl-Sel')
        self._led_blinesenbl = SiriusLedState(
            self, self.dev_pref+':BeamLineCtrlEnbl-Sts')
        self._ld_blinesmon = QLabel('Status', self)
        self._led_blinesmon = SiriusLedState(
            self, self.dev_pref+':BeamLineCtrl-Mon')

        gbox_blines = QGroupBox('Beam Lines Control', self)
        lay_blines = QGridLayout(gbox_blines)
        lay_blines.addWidget(self._ld_blinesenbl, 0, 0)
        lay_blines.addWidget(self._sb_blinesenbl, 0, 1)
        lay_blines.addWidget(self._led_blinesenbl, 0, 2)
        lay_blines.addWidget(self._ld_blinesmon, 1, 0)
        lay_blines.addWidget(self._led_blinesmon, 1, 1, 1, 2)
        return gbox_blines

    def _auxCommandsWidget(self):
        self._ld_speedlim = QLabel('Max Phase Speed\n[mm/s]', self)
        self._sb_speedlim = PyDMSpinbox(
            self, self.dev_pref+':MaxPhaseSpeed-SP')
        self._sb_speedlim.showStepExponent = False
        self._lb_speedlim = PyDMLabel(
            self, self.dev_pref+':MaxPhaseSpeed-RB')

        self._ld_homeaxis = QLabel('Do homing', self)
        self._pb_home = PyDMPushButton(
            self, label='', icon=qta.icon('mdi.keyboard-return'))
        self._pb_home.setToolTip('Execute homing for selected axis.')
        self._pb_home.channel = self.dev_pref+':DevCtrl-Cmd'  # Home
        self._pb_home.pressValue = 10
        self._pb_home.setObjectName('Home')
        self._pb_home.setStyleSheet(
            '#Home{min-width:30px; max-width:30px; icon-size:25px;}')

        self._ld_standby = QLabel('Enable Standby Mode', self)
        self._pb_standby = PyDMPushButton(
            self, label='', icon=qta.icon('mdi.alpha-a-box-outline'))
        self._pb_standby.setToolTip(
            'Enable standby mode for automatic motion.')
        self._pb_standby.channel = self.dev_pref+':DevCtrl-Cmd'  # Standby
        self._pb_standby.pressValue = 5
        self._pb_standby.setObjectName('Standby')
        self._pb_standby.setStyleSheet(
            '#Standby{min-width:30px; max-width:30px; icon-size:25px;}')

        self._ld_lastcomm = QLabel('Last Command', self)
        self._lb_lastcomm = PyDMLabel(
            self, self.dev_pref+':LastDevCtrlCmd-Mon')

        gbox_auxcmd = QGroupBox('Auxiliary Commands', self)
        lay_auxcmd = QGridLayout(gbox_auxcmd)
        lay_auxcmd.addWidget(self._ld_speedlim, 0, 0)
        lay_auxcmd.addWidget(self._sb_speedlim, 0, 1)
        lay_auxcmd.addWidget(self._lb_speedlim, 0, 2)
        lay_auxcmd.addItem(
            QSpacerItem(1, 10, QSzPlcy.Ignored, QSzPlcy.Fixed), 1, 0)
        lay_auxcmd.addWidget(self._ld_homeaxis, 2, 0)
        lay_auxcmd.addWidget(self._pb_home, 2, 1, 1, 2,
                             alignment=Qt.AlignCenter)
        lay_auxcmd.addWidget(self._ld_standby, 3, 0)
        lay_auxcmd.addWidget(self._pb_standby, 3, 1, 1, 2,
                             alignment=Qt.AlignCenter)
        lay_auxcmd.addWidget(self._ld_lastcomm, 4, 0)
        lay_auxcmd.addWidget(self._lb_lastcomm, 4, 1, 1, 2)
        return gbox_auxcmd

    def _corrsControlWidget(self):
        filt = {'sec': 'SI', 'dev': 'C.*', 'sub': self._device.sub}
        self.corrs = PSGraphMonWidget(self, self._prefix, filters=filt)
        self.corrs._graph.setStyleSheet(
            '#graph{min-width:16em;min-height:10em;}')
        self.corrs.layout().setContentsMargins(0, 0, 0, 0)

        self._pb_dtls = QPushButton(
            qta.icon('fa5s.ellipsis-h'), '', self)
        self._pb_dtls.setObjectName('dtls')
        self._pb_dtls.setStyleSheet(
            '#dtls{min-width:30px; max-width:30px; icon-size:25px;}')
        connect_window(
            self._pb_dtls, APUCorrs, self,
            prefix=self._prefix, device=self._device)

        gbox = QGroupBox('Correctors', self)
        lay = QGridLayout(gbox)
        lay.addWidget(self.corrs, 0, 0)
        lay.addWidget(self._pb_dtls, 1, 0, alignment=Qt.AlignRight)
        return gbox
