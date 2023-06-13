"""EPU Control Module."""

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

        self._ld_phsspd = QLabel('Phase Speed [mm/s]', self)
        self._sb_phsspd = SiriusSpinbox(
            self, self.dev_pref.substitute(propty='PhaseSpeed-SP'))
        self._lb_phsspd = SiriusLabel(
            self, self.dev_pref.substitute(propty='PhaseSpeed-RB'))
        self._lb_phsspdmon = SiriusLabel(
            self, self.dev_pref.substitute(propty='PhaseSpeed-Mon'))

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
        lay.addWidget(self._log, 0, 0, 1, 2)
        lay.addWidget(self._bt_logclear, 1, 0, alignment=Qt.AlignCenter)
        lay.addWidget(self._pb_dtlsts, 1, 1, alignment=Qt.AlignRight)
        return gbox

    def _auxCommandsWidget(self):
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
        self._pb_pwrenbl.setObjectName('btn')
        self._pb_pwrenbl.setStyleSheet(
            '#btn{min-width:30px; max-width:30px; icon-size:25px;}')
        self._led_pwrsts = SiriusLedState(
            self, self.dev_pref.substitute(propty='PwrPhase-Mon'))
        self._led_pwrsts.offColor = PyDMLed.Red

        self._ld_homeaxis = QLabel('Do homing', self)
        self._pb_home = PyDMPushButton(
            self, label='', icon=qta.icon('mdi.keyboard-return'))
        self._pb_home.setToolTip('Execute homing for selected axis.')
        self._pb_home.channel = self.dev_pref.substitute(propty='Home-Cmd')
        self._pb_home.pressValue = 1
        self._pb_home.setObjectName('btn')
        self._pb_home.setStyleSheet(
            '#btn{min-width:30px; max-width:30px; icon-size:25px;}')
        self._led_home = SiriusLedState(
            self, self.dev_pref.substitute(propty='Home-Mon'))

        self._ld_clrerr = QLabel('Clear Drive Errors', self)
        pvname = self.dev_pref.substitute(propty='ClearErr-Cmd')
        self._pb_clrerr = PyDMPushButton(
            parent=self, label='', icon=qta.icon('fa5s.sync'),
            init_channel=pvname, pressValue=1)
        self._pb_clrerr.setObjectName('btn')
        self._pb_clrerr.setStyleSheet(
            '#btn{min-width:30px; max-width:30px; icon-size:25px;}')

        lay = QGridLayout(gbox)
        lay.addWidget(self._ld_phsspdlim, 0, 0)
        lay.addWidget(self._sb_phsspdlim, 0, 1)
        lay.addWidget(self._lb_phsspdlim, 0, 2)
        lay.addWidget(self._ld_pwrenbl, 1, 0)
        lay.addWidget(self._pb_pwrenbl, 1, 1)
        lay.addWidget(self._led_pwrsts, 1, 2, alignment=Qt.AlignLeft)
        lay.addWidget(self._ld_homeaxis, 2, 0)
        lay.addWidget(self._pb_home, 2, 1)
        lay.addWidget(self._led_home, 2, 2, alignment=Qt.AlignLeft)
        lay.addItem(QSpacerItem(1, 15, QSzPlcy.Ignored, QSzPlcy.Fixed), 3, 0)
        lay.addWidget(self._ld_clrerr, 4, 0)
        lay.addWidget(self._pb_clrerr, 4, 1)

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
    """EPU Summary Header."""


class PAPUSummaryWidget(IDCommonSummaryWidget, PAPUSummaryBase):
    """EPU Summary Widget."""

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
            wid = SiriusLabel(self, self.dev_pref.substitute(propty=pvn))
            flay.addRow(lbl, wid)

        drivebox = QGroupBox('Drive Status', self)
        glay = QGridLayout(drivebox)
        propties = ['ResolverPos-Mon', 'Code-Mon', 'Torque-Mon',
                    'MotorTemp-Mon']
        for row, pvn in enumerate(propties):
            lbl = QLabel(pvn.split('-')[0] + ':', self)
            glay.addWidget(lbl, row, 0, alignment=Qt.AlignRight)
            wid = SiriusLabel(self, self.dev_pref.substitute(propty=pvn))
            glay.addWidget(wid, row, 1)
            if pvn == 'MotorTemp-Mon':
                c2v = {self.dev_pref.substitute(
                    propty=pvn): {'comp': 'lt', 'value': 90}}
                led = PyDMLedMultiChannel(self, c2v)
                glay.addWidget(led, row, 2, alignment=Qt.AlignLeft)

        self.setStyleSheet(
            'QLabel{qproperty-alignment: AlignCenter; max-width: 12em;}')
        lay = QVBoxLayout(self)
        lay.addWidget(connbox)
        lay.addWidget(drivebox)
