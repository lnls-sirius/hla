"""PAPU Control Module."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGroupBox, QGridLayout, QLabel, QFormLayout, \
    QHBoxLayout, QSizePolicy as QSzPlcy, QSpacerItem, QPushButton, QVBoxLayout
import qtawesome as qta
from pydm.widgets import PyDMPushButton

from ..util import connect_newprocess, connect_window
from ..widgets import PyDMLogLabel, PyDMLed, PyDMLedMultiChannel, \
    SiriusLedState, SiriusLabel, SiriusSpinbox

from .base import IDCommonControlWindow, IDCommonDialog, \
    IDCommonSummaryBase, IDCommonSummaryHeader, IDCommonSummaryWidget


class PAPUControlWindow(IDCommonControlWindow):
    """PAPU Control Window."""

    def _mainControlsWidget(self):
        gbox = QGroupBox('Main Controls', self)
        lay = QGridLayout(gbox)

        self._ld_phs = QLabel('Phase [mm]', self)
        self._sb_phs = SiriusSpinbox(
            self, self.dev_pref.substitute(propty='Phase-SP'))
        self._lb_phs = SiriusLabel(
            self, self.dev_pref.substitute(propty='Phase-RB'))
        self._lb_phsmon = SiriusLabel(
            self, self.dev_pref.substitute(propty='Phase-Mon'))
        self._lb_phsmon.setStyleSheet('QLabel{min-width:6em;}')

        self._ld_phsspd = QLabel('Phase Speed [mm/s]', self)
        self._sb_phsspd = SiriusSpinbox(
            self, self.dev_pref.substitute(propty='PhaseSpeed-SP'))
        self._lb_phsspd = SiriusLabel(
            self, self.dev_pref.substitute(propty='PhaseSpeed-RB'))
        self._lb_phsspdmon = SiriusLabel(
            self, self.dev_pref.substitute(propty='PhaseSpeed-Mon'))
        self._lb_phsspdmon.setStyleSheet('QLabel{min-width:6em;}')

        self._ld_enbl = QLabel('Allow Phase Motion', self)
        self._ld_enbl.setToolTip('Enable Axis and Release Brakes')
        pvname = self.dev_pref.substitute(propty='EnblAndReleasePhase-Sel')
        self._pb_movdsbl = PyDMPushButton(
            parent=self, label='Dsbl', init_channel=pvname, pressValue=0)
        self._pb_movdsbl.setObjectName('btn')
        self._pb_movdsbl.setStyleSheet('#btn{min-width:3em; max-width:3em;}')
        self._pb_movenbl = PyDMPushButton(
            parent=self, label='Enbl', init_channel=pvname, pressValue=1)
        self._pb_movenbl.setObjectName('btn')
        self._pb_movenbl.setStyleSheet('#btn{min-width:3em; max-width:3em;}')
        self._led_movsts = SiriusLedState(
            self, self.dev_pref.substitute(propty='AllowedToChangePhase-Mon'))
        hbox_enbl = QHBoxLayout()
        hbox_enbl.setContentsMargins(0, 0, 0, 0)
        hbox_enbl.setSpacing(3)
        hbox_enbl.addWidget(self._pb_movdsbl)
        hbox_enbl.addWidget(self._pb_movenbl)
        hbox_enbl.addWidget(self._led_movsts)
        hbox_enbl.addStretch()

        self._ld_phsismov = QLabel('Phase Motion', self)
        self._pb_phsstop = PyDMPushButton(
            self, label='', icon=qta.icon('fa5s.stop'))
        self._pb_phsstop.setToolTip('Stop all phase motion, lock all brakes.')
        pvname = self.dev_pref.substitute(propty='StopPhase-Cmd')
        self._pb_phsstop.channel = pvname
        self._pb_phsstop.pressValue = 1  # Stop
        self._pb_phsstop.setObjectName('Stop')
        self._pb_phsstop.setStyleSheet(
            '#Stop{min-width:30px; max-width:30px; icon-size:25px;}')
        self._pb_phsstart = PyDMPushButton(
            self, label='', icon=qta.icon('fa5s.play'))
        self._pb_phsstart.setToolTip(
            'Start automatic Phase motion towards previously '
            'entered setpoint.')
        pvname = self.dev_pref.substitute(propty='ChangePhase-Cmd')
        self._pb_phsstart.channel = pvname
        self._pb_phsstart.pressValue = 1
        self._pb_phsstart.setObjectName('Start')
        self._pb_phsstart.setStyleSheet(
            '#Start{min-width:30px; max-width:30px; icon-size:25px;}')

        self._led_ismov = SiriusLedState(
            self, self.dev_pref.substitute(propty='Moving-Mon'))
        hbox_mov = QHBoxLayout()
        hbox_mov.setSpacing(24)
        hbox_mov.addWidget(self._pb_phsstop)
        hbox_mov.addWidget(self._pb_phsstart)
        hbox_mov.addWidget(self._led_ismov)
        hbox_mov.addStretch()

        lay.addWidget(self._ld_phs, 0, 0)
        lay.addWidget(self._sb_phs, 0, 1)
        lay.addWidget(self._lb_phs, 0, 2)
        lay.addWidget(self._lb_phsmon, 0, 3)
        lay.addWidget(self._ld_phsspd, 1, 0)
        lay.addWidget(self._sb_phsspd, 1, 1)
        lay.addWidget(self._lb_phsspd, 1, 2)
        lay.addWidget(self._lb_phsspdmon, 1, 3)
        lay.addWidget(self._ld_enbl, 2, 0)
        lay.addLayout(hbox_enbl, 2, 1, 1, 3)
        lay.addWidget(self._ld_phsismov, 3, 0)
        lay.addLayout(hbox_mov, 3, 1, 1, 3)
        lay.addItem(QSpacerItem(1, 15, QSzPlcy.Ignored, QSzPlcy.Fixed), 4, 0)

        gbox.setStyleSheet(
            '.QLabel{qproperty-alignment: "AlignRight | AlignVCenter";}')
        return gbox

    def _statusWidget(self):
        self._ld_drivests = QLabel(
            'Drive Status:', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self._lb_drivests = SiriusLabel(
            self, self.dev_pref.substitute(propty='DiagMessage-Mon'))
        self._lb_drivests.setStyleSheet('QLabel{min-width: 10em;}')
        self._lb_drivests.displayFormat = SiriusLabel.DisplayFormat.String
        self._led_drivests = PyDMLedMultiChannel(
            self, {
                self.dev_pref.substitute(propty='Code-Mon'): {
                    'comp': 'in', 'value': ['A211', 'A012']}})

        self._pb_dtlsts = QPushButton('', self)
        self._pb_dtlsts.setIcon(qta.icon('fa5s.list-ul'))
        self._pb_dtlsts.setToolTip('Open Detailed Status View')
        self._pb_dtlsts.setObjectName('sts')
        self._pb_dtlsts.setStyleSheet(
            '#sts{min-width:25px; max-width:25px; icon-size:20px;}')
        connect_window(
            self._pb_dtlsts, PAPUDetails, self,
            prefix=self._prefix, device=self._device)

        self._log = PyDMLogLabel(
            self, init_channel=self.dev_pref.substitute(propty='Log-Mon'))
        self._log.setSizePolicy(
            QSzPlcy.MinimumExpanding, QSzPlcy.MinimumExpanding)
        self._log.setAlternatingRowColors(True)
        self._log.maxCount = 2000

        self._bt_logclear = QPushButton('Clear Log', self)
        self._bt_logclear.clicked.connect(self._log.clear)

        gbox = QGroupBox('Status')
        gbox.setSizePolicy(QSzPlcy.MinimumExpanding, QSzPlcy.Preferred)
        lay = QGridLayout(gbox)
        lay.addWidget(self._ld_drivests, 0, 0)
        lay.addWidget(self._lb_drivests, 0, 1)
        lay.addWidget(self._led_drivests, 0, 2)
        lay.addWidget(self._pb_dtlsts, 0, 3, alignment=Qt.AlignRight)
        lay.addWidget(self._log, 1, 0, 1, 4)
        lay.addWidget(self._bt_logclear, 2, 0, 1, 4, alignment=Qt.AlignCenter)
        return gbox

    def _auxCommandsWidget(self):
        btnname = 'btn'
        btnsty = '#btn{min-width:30px; max-width:30px; icon-size:25px;}'

        gbox = QGroupBox('Auxiliary Commands', self)

        self._ld_phsspdlim = QLabel('Max Phase Speed [mm/s]', self)
        self._sb_phsspdlim = SiriusSpinbox(
            self, self.dev_pref.substitute(propty='MaxPhaseSpeed-SP'))
        self._sb_phsspdlim.setStyleSheet('max-width:4.5em;')
        self._lb_phsspdlim = SiriusLabel(
            self, self.dev_pref.substitute(propty='MaxPhaseSpeed-RB'))

        self._ld_pwrenbl = QLabel('Enable Phase Drives Power', self)
        pvname = self.dev_pref.substitute(propty='EnblPwrPhase-Cmd')
        self._pb_pwrenbl = PyDMPushButton(
            parent=self, label='', icon=qta.icon('fa5s.plug'),
            init_channel=pvname, pressValue=1)
        self._pb_pwrenbl.setObjectName(btnname)
        self._pb_pwrenbl.setStyleSheet(btnsty)
        self._led_pwrsts = SiriusLedState(
            self, self.dev_pref.substitute(propty='PwrPhase-Mon'))
        self._led_pwrsts.offColor = PyDMLed.Red

        self._ld_homeaxis = QLabel('Do homing', self)
        self._pb_home = PyDMPushButton(
            self, label='', icon=qta.icon('mdi.keyboard-return'))
        self._pb_home.setToolTip('Execute homing for selected axis.')
        self._pb_home.channel = self.dev_pref.substitute(propty='Home-Cmd')
        self._pb_home.pressValue = 1
        self._pb_home.setObjectName(btnname)
        self._pb_home.setStyleSheet(btnsty)
        self._led_home = SiriusLabel(
            self, self.dev_pref.substitute(propty='Home-Mon'))

        self._ld_parkspd = QLabel('Park Speed [mm/s]', self)
        self._sb_parkspd = SiriusSpinbox(
            self, self.dev_pref.substitute(propty='ParkSpeed-SP'))
        self._sb_parkspd.setStyleSheet('max-width:4.5em;')
        self._lb_parkspd = SiriusLabel(
            self, self.dev_pref.substitute(propty='ParkSpeed-RB'))

        self._ld_park = QLabel('Do parking', self)
        pvname = self.dev_pref.substitute(propty='Park-Cmd')
        self._pb_park = PyDMPushButton(
            parent=self, label='', icon=qta.icon('fa5s.parking'),
            init_channel=pvname, pressValue=1)
        self._pb_park.setObjectName(btnname)
        self._pb_park.setStyleSheet(btnsty)

        self._ld_gotomin = QLabel('Go to minimum Phase', self)
        pvname = self.dev_pref.substitute(propty='GoToMinPhase-Cmd')
        self._pb_gotomin = PyDMPushButton(
            parent=self, label='Go to minimum',
            init_channel=pvname, pressValue=1)
        self._ld_gotoop = QLabel('Go to operation Phase', self)
        pvname = self.dev_pref.substitute(propty='GoToOpPhase-Cmd')
        self._pb_gotoop = PyDMPushButton(
            parent=self, label='Go to operation',
            init_channel=pvname, pressValue=1)

        self._ld_clrerr = QLabel('Clear Drive Errors', self)
        pvname = self.dev_pref.substitute(propty='ClearErr-Cmd')
        self._pb_clrerr = PyDMPushButton(
            parent=self, label='', icon=qta.icon('fa5s.sync'),
            init_channel=pvname, pressValue=1)
        self._pb_clrerr.setObjectName(btnname)
        self._pb_clrerr.setStyleSheet(btnsty)

        lay = QGridLayout(gbox)
        lay.addWidget(self._ld_phsspdlim, 0, 0)
        lay.addWidget(self._sb_phsspdlim, 0, 1)
        lay.addWidget(self._lb_phsspdlim, 0, 2)
        lay.addItem(QSpacerItem(1, 8, QSzPlcy.Ignored, QSzPlcy.Fixed), 1, 0)
        lay.addWidget(self._ld_pwrenbl, 2, 0)
        lay.addWidget(self._pb_pwrenbl, 2, 1)
        lay.addWidget(self._led_pwrsts, 2, 2, alignment=Qt.AlignLeft)
        lay.addItem(QSpacerItem(1, 8, QSzPlcy.Ignored, QSzPlcy.Fixed), 3, 0)
        lay.addWidget(self._ld_homeaxis, 4, 0)
        lay.addWidget(self._pb_home, 4, 1)
        lay.addWidget(self._led_home, 4, 2, alignment=Qt.AlignLeft)
        lay.addItem(QSpacerItem(1, 8, QSzPlcy.Ignored, QSzPlcy.Fixed), 5, 0)
        lay.addWidget(self._ld_parkspd, 6, 0)
        lay.addWidget(self._sb_parkspd, 6, 1)
        lay.addWidget(self._lb_parkspd, 6, 2)
        lay.addWidget(self._ld_park, 7, 0)
        lay.addWidget(self._pb_park, 7, 1)
        lay.addItem(QSpacerItem(1, 8, QSzPlcy.Ignored, QSzPlcy.Fixed), 8, 0)
        lay.addWidget(self._ld_gotomin, 9, 0)
        lay.addWidget(self._pb_gotomin, 9, 1, 1, 2)
        lay.addWidget(self._ld_gotoop, 10, 0)
        lay.addWidget(self._pb_gotoop, 10, 1, 1, 2)
        lay.addItem(QSpacerItem(1, 8, QSzPlcy.Ignored, QSzPlcy.Fixed), 11, 0)
        lay.addWidget(self._ld_clrerr, 12, 0)
        lay.addWidget(self._pb_clrerr, 12, 1)

        gbox.setStyleSheet(
            '.QLabel{qproperty-alignment: "AlignRight | AlignVCenter";}')
        return gbox

    def _ffSettingsWidget(self):
        but = QPushButton('Feedforward Settings', self)
        connect_newprocess(
            but, ['sirius-hla-si-ap-idff.py', self._device])
        return but


class PAPUSummaryBase(IDCommonSummaryBase):
    """PAPU Summary Base Widget."""

    MODEL_WIDTHS = (
        ('Status', 4),
        ('Phase', 6),
        ('Phase Speed', 6),
        ('Start Phase', 4),
        ('Stop Phase', 4),
    )


class PAPUSummaryHeader(IDCommonSummaryHeader, PAPUSummaryBase):
    """PAPU Summary Header."""


class PAPUSummaryWidget(IDCommonSummaryWidget, PAPUSummaryBase):
    """PAPU Summary Widget."""

    def _get_widgets(self, prop):
        wids, orientation = super()._get_widgets(prop)
        if not wids:
            orientation = 'v'
        if prop == 'Status':
            led = SiriusLedState(
                self, self.dev_pref.substitute(
                    propty='AllowedToChangePhase-Mon'))
            led.offColor = led.Red
            wids.append(led)
        elif prop == 'Phase':
            spb = SiriusSpinbox(
                self, self.dev_pref.substitute(propty='Phase-SP'))
            wids.append(spb)
            lbl = SiriusLabel(
                self, self.dev_pref.substitute(propty='Phase-Mon'))
            wids.append(lbl)
        elif prop == 'Phase Speed':
            spb = SiriusSpinbox(
                self, self.dev_pref.substitute(propty='PhaseSpeed-SP'))
            wids.append(spb)
            lbl = SiriusLabel(
                self, self.dev_pref.substitute(propty='PhaseSpeed-Mon'))
            wids.append(lbl)
        elif prop == 'Start Phase':
            btn = PyDMPushButton(self, label='', icon=qta.icon('fa5s.play'))
            btn.setToolTip(
                'Start automatic motion towards previously entered setpoint.')
            btn.channel = self.dev_pref.substitute(propty='ChangePhase-Cmd')
            btn.pressValue = 1
            btn.setObjectName('Start')
            btn.setStyleSheet(
                '#Start{min-width:30px; max-width:30px; icon-size:25px;}')
            wids.append(btn)
        elif prop == 'Stop Phase':
            btn = PyDMPushButton(self, label='', icon=qta.icon('fa5s.stop'))
            btn.setToolTip('Stop all motion, lock all brakes.')
            btn.channel = self.dev_pref.substitute(propty='StopPhase-Cmd')
            btn.pressValue = 1
            btn.setObjectName('Stop')
            btn.setStyleSheet(
                '#Stop{min-width:30px; max-width:30px; icon-size:25px;}')
            wids.append(btn)
        return wids, orientation


class PAPUDetails(IDCommonDialog):
    """PAPU Details."""

    def __init__(self, parent=None, prefix='', device=''):
        """Init."""
        super().__init__(
            parent, prefix, device, title=device+' Drive Details')

    def _setupUi(self):
        connbox = QGroupBox('Connection', self)
        flay = QFormLayout(connbox)
        flay.setLabelAlignment(Qt.AlignRight)
        for pvn in ['Connected-Mon', 'MsgServerConnected-Mon',
                    'IoServerConnected-Mon', 'SerialConnected-Mon']:
            lbl = pvn.split('-')[0] + ':'
            wid = SiriusLedState(self, self.dev_pref.substitute(propty=pvn))
            flay.addRow(lbl, wid)

        drivebox = QGroupBox('Drive Status', self)
        glay = QGridLayout(drivebox)
        propties = ['ResolverPos-Mon', 'Torque-Mon', 'MotorTemp-Mon',
                    'Code-Mon', 'DiagMessage-Mon']
        for row, pvn in enumerate(propties):
            lbl = QLabel(pvn.split('-')[0] + ':', self)
            glay.addWidget(lbl, row, 0, alignment=Qt.AlignRight)
            wid = SiriusLabel(self, self.dev_pref.substitute(propty=pvn))
            wid.showUnits = True
            if pvn == 'DiagMessage-Mon':
                wid.displayFormat = wid.DisplayFormat.String
            glay.addWidget(wid, row, 1)

            c2v = None
            if pvn == 'Code-Mon':
                c2v = {self.dev_pref.substitute(
                    propty=pvn): {'comp': 'in', 'value': ['A211', 'A012']}}
            elif pvn == 'MotorTemp-Mon':
                c2v = {self.dev_pref.substitute(
                    propty=pvn): {'comp': 'lt', 'value': 90}}
            if c2v:
                led = PyDMLedMultiChannel(self, c2v)
                led.offColor = led.Yellow
                glay.addWidget(led, row, 2, alignment=Qt.AlignLeft)

        self.setStyleSheet(
            'QLabel{qproperty-alignment: AlignCenter; max-width: 12em;}')
        lay = QVBoxLayout(self)
        lay.addWidget(connbox)
        lay.addWidget(drivebox)
