"""APU Control Module."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGroupBox, QGridLayout, QLabel, \
    QHBoxLayout, QSizePolicy as QSzPlcy, QSpacerItem, QPushButton
import qtawesome as qta
from pydm.widgets import PyDMPushButton

from siriushla.util import connect_window
from siriushla.widgets import PyDMLed, SiriusLedAlert, \
    SiriusLedState, PyDMLedMultiChannel, SiriusLabel, SiriusSpinbox

from .base import IDCommonControlWindow, IDCommonDialog, \
    IDCommonSummaryBase, IDCommonSummaryHeader, IDCommonSummaryWidget


class APUControlWindow(IDCommonControlWindow):
    """APU Control Window."""

    def _mainControlsWidget(self):
        self._ld_kx = QLabel('Kx', self)
        self._sb_kx = SiriusSpinbox(
            self, self.dev_pref.substitute(propty='Kx-SP'))
        self._lb_kx = SiriusLabel(
            self, self.dev_pref.substitute(propty='Kx-Mon'))

        self._ld_phs = QLabel('Phase [mm]', self)
        self._sb_phs = SiriusSpinbox(
            self, self.dev_pref.substitute(propty='Phase-SP'))
        self._lb_phs = SiriusLabel(
            self, self.dev_pref.substitute(propty='Phase-Mon'))

        self._ld_phsspd = QLabel('Phase Speed [mm/s]', self)
        self._sb_phsspd = SiriusSpinbox(
            self, self.dev_pref.substitute(propty='PhaseSpeed-SP'))
        self._lb_phsspd = SiriusLabel(
            self, self.dev_pref.substitute(propty='PhaseSpeed-Mon'))

        self._ld_ismov = QLabel('Motion', self)
        self._pb_stop = PyDMPushButton(
            self, label='', icon=qta.icon('fa5s.stop'))
        self._pb_stop.setToolTip('Stop all motion, lock all brakes.')
        self._pb_stop.channel = self.dev_pref.substitute(propty='DevCtrl-Cmd')
        self._pb_stop.pressValue = 1  # Stop
        self._pb_stop.setObjectName('Stop')
        self._pb_stop.setStyleSheet(
            '#Stop{min-width:30px; max-width:30px; icon-size:25px;}')
        self._pb_start = PyDMPushButton(
            self, label='', icon=qta.icon('fa5s.play'))
        self._pb_start.setToolTip(
            'Start automatic motion towards previously entered setpoint.')
        self._pb_start.channel = self.dev_pref.substitute(propty='DevCtrl-Cmd')
        self._pb_start.pressValue = 3  # Start
        self._pb_start.setObjectName('Start')
        self._pb_start.setStyleSheet(
            '#Start{min-width:30px; max-width:30px; icon-size:25px;}')
        self._led_ismov = SiriusLedState(self, self.dev_pref+':Moving-Mon')
        self._led_motenbl = SiriusLedState(
            self, self.dev_pref.substitute(propty='MotorsEnbld-Mon'))
        hbox_motion = QHBoxLayout()
        hbox_motion.setSpacing(15)
        hbox_motion.addWidget(self._pb_stop)
        hbox_motion.addWidget(self._pb_start)
        hbox_motion.addWidget(self._led_ismov)
        hbox_motion.addWidget(self._led_motenbl)

        gbox = QGroupBox('Main Controls', self)
        lay = QGridLayout(gbox)
        lay.addWidget(self._ld_kx, 0, 0)
        lay.addWidget(self._sb_kx, 0, 1)
        lay.addWidget(self._lb_kx, 0, 2)
        lay.addWidget(self._ld_phs, 1, 0)
        lay.addWidget(self._sb_phs, 1, 1)
        lay.addWidget(self._lb_phs, 1, 2)
        lay.addWidget(self._ld_phsspd, 2, 0)
        lay.addWidget(self._sb_phsspd, 2, 1)
        lay.addWidget(self._lb_phsspd, 2, 2)
        lay.addItem(
            QSpacerItem(1, 10, QSzPlcy.Ignored, QSzPlcy.Fixed), 3, 0)
        lay.addWidget(self._ld_ismov, 4, 0)
        lay.addLayout(hbox_motion, 4, 1, 1, 2)
        gbox.setStyleSheet(
            '.QLabel{qproperty-alignment: "AlignRight | AlignVCenter";}')
        return gbox

    def _statusWidget(self):
        self._ld_alarm = QLabel(
            'Alarms', self, alignment=Qt.AlignCenter)
        self._led_alarm = SiriusLedAlert(
            self, self.dev_pref.substitute(propty='Alarm-Mon'))
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
            self, {self.dev_pref.substitute(propty='IntlkInStop-Mon'): 0,
                   self.dev_pref.substitute(propty='IntlkInEOpnGap-Mon'): 0,
                   self.dev_pref.substitute(propty='IntlkOutPwrEnbld-Mon'): 1})
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
            {self.dev_pref.substitute(propty='StateHw-Mon'): {
                'value': [0x4C, 0x3C], 'comp': 'in'},
             self.dev_pref.substitute(propty='State-Mon'): {
                 'value': [1, 4], 'comp': 'in'},
             self.dev_pref.substitute(propty='IsOperational-Mon'): 1})
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
        self._pb_reset.channel = self.dev_pref.substitute(propty='DevCtrl-Cmd')
        self._pb_reset.pressValue = 2  # Reset
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
        self._led_ctrlmode = PyDMLed(
            self, self.dev_pref.substitute(propty='IsRemote-Mon'))
        self._led_ctrlmode.offColor = PyDMLed.Red
        self._led_ctrlmode.onColor = PyDMLed.LightGreen
        self._lb_ctrlmode = SiriusLabel(
            self, self.dev_pref.substitute(propty='Interface-Mon'))

        gbox_ctrlmode = QGroupBox('Control Mode')
        lay_ctrlmode = QHBoxLayout(gbox_ctrlmode)
        lay_ctrlmode.setAlignment(Qt.AlignCenter)
        lay_ctrlmode.addWidget(self._led_ctrlmode)
        lay_ctrlmode.addWidget(self._lb_ctrlmode)
        return gbox_ctrlmode

    def _auxCommandsWidget(self):
        self._ld_speedlim = QLabel('Max Phase\nSpeed [mm/s]', self)
        self._sb_speedlim = SiriusSpinbox(
            self, self.dev_pref.substitute(propty='MaxPhaseSpeed-SP'))
        self._sb_speedlim.setStyleSheet('max-width:4.5em;')
        self._lb_speedlim = SiriusLabel(
            self, self.dev_pref.substitute(propty='MaxPhaseSpeed-RB'))

        self._ld_homeaxis = QLabel('Do homing', self)
        self._pb_home = PyDMPushButton(
            self, label='', icon=qta.icon('mdi.keyboard-return'))
        self._pb_home.setToolTip('Execute homing for selected axis.')
        self._pb_home.channel = self.dev_pref.substitute(propty='DevCtrl-Cmd')
        self._pb_home.pressValue = 10  # Home
        self._pb_home.setObjectName('Home')
        self._pb_home.setStyleSheet(
            '#Home{min-width:30px; max-width:30px; icon-size:25px;}')

        self._ld_standby = QLabel('Enable Standby Mode', self)
        self._pb_standby = PyDMPushButton(
            self, label='', icon=qta.icon('mdi.alpha-a-box-outline'))
        self._pb_standby.setToolTip(
            'Enable standby mode for automatic motion.')
        self._pb_standby.channel = \
            self.dev_pref.substitute(propty='DevCtrl-Cmd')
        self._pb_standby.pressValue = 5  # Standby
        self._pb_standby.setObjectName('Standby')
        self._pb_standby.setStyleSheet(
            '#Standby{min-width:30px; max-width:30px; icon-size:25px;}')

        self._ld_lastcomm = QLabel('Last Command', self)
        self._lb_lastcomm = SiriusLabel(
            self, self.dev_pref.substitute(propty='LastDevCtrlCmd-Mon'))

        gbox = QGroupBox('Auxiliary Commands', self)
        lay = QGridLayout(gbox)
        lay.addWidget(self._ld_speedlim, 0, 0)
        lay.addWidget(self._sb_speedlim, 0, 1)
        lay.addWidget(self._lb_speedlim, 0, 2)
        lay.addItem(
            QSpacerItem(1, 10, QSzPlcy.Ignored, QSzPlcy.Fixed), 1, 0)
        lay.addWidget(self._ld_homeaxis, 2, 0)
        lay.addWidget(self._pb_home, 2, 1, 1, 2, alignment=Qt.AlignCenter)
        lay.addWidget(self._ld_standby, 3, 0)
        lay.addWidget(self._pb_standby, 3, 1, 1, 2, alignment=Qt.AlignCenter)
        lay.addWidget(self._ld_lastcomm, 4, 0)
        lay.addWidget(self._lb_lastcomm, 4, 1, 1, 2)
        gbox.setStyleSheet(
            '.QLabel{qproperty-alignment: "AlignRight | AlignVCenter";}')
        return gbox


class APUAlarmDetails(IDCommonDialog):
    """APU Alarm Details Dialog."""

    def __init__(self, parent=None, prefix='', device=''):
        super().__init__(
            parent, prefix, device, title=device+' Alarm Details')

    def _setupUi(self):
        self._ld_almaxctrl = QLabel('<h4>Axis Control</h4>', self)

        self._ld_almflag = QLabel('Flag', self)
        self._lb_almflag = SiriusLabel(
            self, self.dev_pref.substitute(propty='AlrmPhase-Mon'))

        self._ld_almeid = QLabel('Error ID Code', self)
        self._lb_almeid = SiriusLabel(
            self, self.dev_pref.substitute(propty='AlrmPhaseErrID-Mon'))

        self._ld_almsttdw = QLabel('State DWord', self)
        self._lb_almsttdw = SiriusLabel(
            self, self.dev_pref.substitute(propty='AlrmPhaseSttDW-Mon'))

        self._ld_almsttcode = QLabel('State Code', self)
        self._lb_almsttcode = SiriusLabel(
            self, self.dev_pref.substitute(propty='AlrmPhaseStt-Mon'))

        self._ld_almrack = QLabel('<h4>Rack</h4>', self)

        self._ld_almestop = QLabel('E-Stop button pressed', self)
        self._led_almestop = PyDMLed(
            self, self.dev_pref.substitute(propty='AlrmRackEStop-Mon'))
        self._led_almestop.offColor = PyDMLed.LightGreen
        self._led_almestop.onColor = PyDMLed.Red

        self._ld_almkillpres = QLabel('Kill switch pressed', self)
        self._led_almkillpres = PyDMLed(
            self, self.dev_pref.substitute(propty='AlrmRackKill-Mon'))
        self._led_almkillpres.offColor = PyDMLed.LightGreen
        self._led_almkillpres.onColor = PyDMLed.Red

        self._ld_almkilldsbl = QLabel('Kill switches disabled', self)
        self._led_almkilldsbl = PyDMLed(
            self, self.dev_pref.substitute(propty='AlrmRackKillDsbld-Mon'))
        self._led_almkilldsbl.offColor = PyDMLed.LightGreen
        self._led_almkilldsbl.onColor = PyDMLed.Red

        self._ld_almpwrdsbl = QLabel('Power disabled', self)
        self._led_almpwrdsbl = PyDMLed(
            self, self.dev_pref.substitute(propty='AlrmRackPwrDsbld-Mon'))
        self._led_almpwrdsbl.offColor = PyDMLed.LightGreen
        self._led_almpwrdsbl.onColor = PyDMLed.Red

        lay = QGridLayout(self)
        lay.addWidget(
            QLabel('<h4>Alarms</h4>', self,
                   alignment=Qt.AlignCenter), 0, 0, 1, 2)
        lay.addWidget(self._ld_almaxctrl, 1, 0, 1, 2)
        lay.addWidget(self._ld_almflag, 2, 0)
        lay.addWidget(self._lb_almflag, 2, 1)
        lay.addWidget(self._ld_almeid, 3, 0)
        lay.addWidget(self._lb_almeid, 3, 1)
        lay.addWidget(self._ld_almsttdw, 4, 0)
        lay.addWidget(self._lb_almsttdw, 4, 1)
        lay.addWidget(self._ld_almsttcode, 5, 0)
        lay.addWidget(self._lb_almsttcode, 5, 1)
        lay.addItem(QSpacerItem(1, 10, QSzPlcy.Ignored, QSzPlcy.Fixed), 6, 0)
        lay.addWidget(self._ld_almrack, 7, 0, 1, 2)
        lay.addWidget(self._ld_almestop, 8, 0)
        lay.addWidget(self._led_almestop, 8, 1)
        lay.addWidget(self._ld_almkillpres, 9, 0)
        lay.addWidget(self._led_almkillpres, 9, 1)
        lay.addWidget(self._ld_almkilldsbl, 10, 0)
        lay.addWidget(self._led_almkilldsbl, 10, 1)
        lay.addWidget(self._ld_almpwrdsbl, 11, 0)
        lay.addWidget(self._led_almpwrdsbl, 11, 1)


class APUInterlockDetails(IDCommonDialog):
    """APU Interlock Details Dialog."""

    def __init__(self, parent=None, prefix='', device=''):
        super().__init__(
            parent, prefix, device, title=device+' Interlock Details')

    def _setupUi(self):
        self._ld_ilkistop = QLabel('Stop\n(Input)', self)
        self._led_ilkistop = PyDMLed(
            self, self.dev_pref.substitute(propty='IntlkInStop-Mon'))
        self._led_ilkistop.offColor = PyDMLed.LightGreen
        self._led_ilkistop.onColor = PyDMLed.Red
        self._lb_ilkistop = SiriusLabel(
            self, self.dev_pref.substitute(propty='IntlkInStop-Mon'))
        hbox_ilkistop = QHBoxLayout()
        hbox_ilkistop.addWidget(self._led_ilkistop)
        hbox_ilkistop.addWidget(self._lb_ilkistop)

        self._ld_ilkieopn = QLabel('Emergency Open Gap\n(Input)', self)
        self._led_ilkieopn = PyDMLed(
            self, self.dev_pref.substitute(propty='IntlkInEOpnGap-Mon'))
        self._led_ilkieopn.offColor = PyDMLed.LightGreen
        self._led_ilkieopn.onColor = PyDMLed.Red
        self._lb_ilkieopn = SiriusLabel(
            self, self.dev_pref.substitute(propty='IntlkInEOpnGap-Mon'))
        hbox_eopngap = QHBoxLayout()
        hbox_eopngap.addWidget(self._led_ilkieopn)
        hbox_eopngap.addWidget(self._lb_ilkieopn)

        self._ld_ilkogapopn = QLabel('Gap Opened\n(Output)', self)
        self._lb_ilkogapopn = SiriusLabel(
            self, self.dev_pref.substitute(propty='IntlkOutGapStt-Mon'))
        self._lb_ilkogapopn.setAlignment(Qt.AlignCenter)

        self._ld_ilkopwr = QLabel('Power Enabled\n(Output)', self)
        self._led_ilkopwr = PyDMLed(
            self, self.dev_pref.substitute(propty='IntlkOutPwrEnbld-Mon'))
        self._led_ilkopwr.offColor = PyDMLed.Red
        self._led_ilkopwr.onColor = PyDMLed.LightGreen

        lay = QGridLayout(self)
        lay.addWidget(
            QLabel('<h4>Interlock status</h4>', self,
                   alignment=Qt.AlignCenter), 0, 0, 1, 2)
        lay.addWidget(self._ld_ilkistop, 1, 0)
        lay.addLayout(hbox_ilkistop, 1, 1)
        lay.addWidget(self._ld_ilkieopn, 2, 0)
        lay.addLayout(hbox_eopngap, 2, 1)
        lay.addWidget(self._ld_ilkogapopn, 3, 0)
        lay.addWidget(self._lb_ilkogapopn, 3, 1)
        lay.addWidget(self._ld_ilkopwr, 4, 0)
        lay.addWidget(self._led_ilkopwr, 4, 1)


class APUHardLLDetails(IDCommonDialog):
    """APU Hardware and LowLevel Details Dialog."""

    def __init__(self, parent=None, prefix='', device=''):
        super().__init__(
            parent, prefix, device,
            title=device+' Hardware and LowLevel Details')

    def _setupUi(self):
        self._ld_stthw = QLabel('Hardware state', self)
        self._led_stthw = PyDMLedMultiChannel(
            self, channels2values={
                self.dev_pref.substitute(propty='StateHw-Mon'):
                    {'value': [0x4C, 0x3C], 'comp': 'in'}})  # in [Op, Ready]
        self._led_stthw.offColor = PyDMLed.Yellow
        self._led_stthw.onColor = PyDMLed.LightGreen
        self._led_stthw.setObjectName('led')
        self._led_stthw.setStyleSheet('#led{max-width: 1.29em;}')
        self._led_stthw.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Preferred)
        self._lb_stthw = SiriusLabel(
            self, self.dev_pref.substitute(propty='StateHw-Mon'))

        self._ld_sttsys = QLabel('System state', self)
        self._led_sttsys = PyDMLedMultiChannel(
            self, channels2values={
                self.dev_pref.substitute(propty='State-Mon'):
                    {'value': [1, 4], 'comp': 'in'}})  # in [Op, Standby]
        self._led_sttsys.offColor = PyDMLed.Yellow
        self._led_sttsys.onColor = PyDMLed.LightGreen
        self._led_sttsys.setObjectName('led')
        self._led_sttsys.setStyleSheet('#led{max-width: 1.29em;}')
        self._led_sttsys.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Preferred)
        self._lb_sttsys = SiriusLabel(
            self, self.dev_pref.substitute(propty='State-Mon'))

        self._ld_isopr = QLabel('Is operational', self)
        self._led_isopr = PyDMLed(
            self, self.dev_pref.substitute(propty='IsOperational-Mon'))
        self._led_isopr.offColor = PyDMLed.Red
        self._led_isopr.onColor = PyDMLed.LightGreen
        self._led_isopr.setStyleSheet('max-width: 1.29em;')
        self._led_isopr.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Preferred)

        lay_hwsys = QGridLayout(self)
        lay_hwsys.addWidget(
            QLabel('<h4>Hardware&&LowLevel</h4>', self,
                   alignment=Qt.AlignCenter), 0, 0, 1, 3)
        lay_hwsys.addWidget(self._ld_stthw, 2, 0)
        lay_hwsys.addWidget(self._led_stthw, 2, 1)
        lay_hwsys.addWidget(self._lb_stthw, 2, 2)
        lay_hwsys.addWidget(self._ld_sttsys, 3, 0)
        lay_hwsys.addWidget(self._led_sttsys, 3, 1)
        lay_hwsys.addWidget(self._lb_sttsys, 3, 2)
        lay_hwsys.addWidget(self._ld_isopr, 4, 0)
        lay_hwsys.addWidget(self._led_isopr, 4, 1)


class APUSummaryBase(IDCommonSummaryBase):
    """APU Summary Base Widget."""

    MODEL_WIDTHS = (
        ('Alarms', 4),
        ('Kx', 6),
        ('Phase', 6),
        ('Phase Speed', 6),
        ('Start', 4),
        ('Stop', 4),
    )


class APUSummaryHeader(IDCommonSummaryHeader, APUSummaryBase):
    """APU Summary Header."""


class APUSummaryWidget(IDCommonSummaryWidget, APUSummaryBase):
    """APU Summary Widget."""

    def _get_widgets(self, prop):
        wids, orientation = super()._get_widgets(prop)
        if not wids:
            orientation = 'v'
        if prop == 'Alarms':
            led = PyDMLedMultiChannel(
                self,
                {self.dev_pref.substitute(propty='Alarm-Mon'): 0,
                 self.dev_pref.substitute(propty='IntlkInStop-Mon'): 0,
                 self.dev_pref.substitute(propty='IntlkInEOpnGap-Mon'): 0,
                 self.dev_pref.substitute(propty='IntlkOutPwrEnbld-Mon'): 1,
                 self.dev_pref.substitute(propty='IsOperational-Mon'): 1})
            wids.append(led)
        elif prop == 'Phase':
            spb = SiriusSpinbox(
                self, self.dev_pref.substitute(propty='Phase-SP'))
            wids.append(spb)
            lbl = SiriusLabel(
                self, self.dev_pref.substitute(propty='Phase-Mon'))
            wids.append(lbl)
        elif prop == 'Kx':
            spb = SiriusSpinbox(
                self, self.dev_pref.substitute(propty='Kx-SP'))
            wids.append(spb)
            lbl = SiriusLabel(
                self, self.dev_pref.substitute(propty='Kx-Mon'))
            wids.append(lbl)
        elif prop == 'Phase Speed':
            spb = SiriusSpinbox(
                self, self.dev_pref.substitute(propty='PhaseSpeed-SP'))
            wids.append(spb)
            lbl = SiriusLabel(
                self, self.dev_pref.substitute(propty='PhaseSpeed-Mon'))
            wids.append(lbl)
        elif prop == 'Start':
            btn = PyDMPushButton(self, label='', icon=qta.icon('fa5s.play'))
            btn.setToolTip(
                'Start automatic motion towards previously entered setpoint.')
            btn.channel = self.dev_pref.substitute(propty='DevCtrl-Cmd')
            btn.pressValue = 3  # Start
            btn.setObjectName('Start')
            btn.setStyleSheet(
                '#Start{min-width:30px; max-width:30px; icon-size:25px;}')
            wids.append(btn)
        elif prop == 'Stop':
            btn = PyDMPushButton(self, label='', icon=qta.icon('fa5s.stop'))
            btn.setToolTip('Stop all motion, lock all brakes.')
            btn.channel = self.dev_pref.substitute(propty='DevCtrl-Cmd')
            btn.pressValue = 1  # Stop
            btn.setObjectName('Stop')
            btn.setStyleSheet(
                '#Stop{min-width:30px; max-width:30px; icon-size:25px;}')
            wids.append(btn)
        return wids, orientation
