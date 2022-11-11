"""EPU Control Module."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGroupBox, QGridLayout, QLabel, \
    QHBoxLayout, QSizePolicy as QSzPlcy, QSpacerItem, QPushButton
import qtawesome as qta
from pydm.widgets import PyDMPushButton

from siriushla.util import connect_window
from siriushla.widgets import PyDMLogLabel, SiriusLedAlert, \
    SiriusLedState, PyDMLedMultiChannel, SiriusLabel, SiriusSpinbox

from .base import IDCommonControlWindow, IDCommonDialog, \
    IDCommonSummaryBase, IDCommonSummaryHeader, IDCommonSummaryWidget


class EPUControlWindow(IDCommonControlWindow):
    """EPU Control Window."""

    def _mainControlsWidget(self):
        self._ld_kx = QLabel('Kx', self)
        self._sb_kx = SiriusSpinbox(
            self, self.dev_pref.substitute(propty='Kx-SP'))
        self._lb_kx = SiriusLabel(
            self, self.dev_pref.substitute(propty='Kx-RB'))
        self._lb_kxmon = SiriusLabel(
            self, self.dev_pref.substitute(propty='Kx-Mon'))

        self._ld_ky = QLabel('Ky', self)
        self._sb_ky = SiriusSpinbox(
            self, self.dev_pref.substitute(propty='Ky-SP'))
        self._lb_ky = SiriusLabel(
            self, self.dev_pref.substitute(propty='Ky-RB'))
        self._lb_kymon = SiriusLabel(
            self, self.dev_pref.substitute(propty='Ky-Mon'))

        gbox = QGroupBox('Main Controls', self)
        lay = QGridLayout(gbox)
        lay.addWidget(self._ld_kx, 0, 0)
        lay.addWidget(self._sb_kx, 0, 1)
        lay.addWidget(self._lb_kx, 0, 2)
        lay.addWidget(self._lb_kxmon, 0, 3)
        lay.addWidget(self._ld_ky, 1, 0)
        lay.addWidget(self._sb_ky, 1, 1)
        lay.addWidget(self._lb_ky, 1, 2)
        lay.addWidget(self._lb_kymon, 1, 3)
        lay.addItem(
            QSpacerItem(1, 15, QSzPlcy.Ignored, QSzPlcy.Fixed), 2, 0)

        row = 3
        for prop in ['Phase', 'Gap']:
            ld_prop = QLabel(prop+' [mm]', self)
            sb_prop = SiriusSpinbox(
                self, self.dev_pref.substitute(propty=prop+'-SP'))
            lb_prop = SiriusLabel(
                self, self.dev_pref.substitute(propty=prop+'-RB'))
            lb_propmon = SiriusLabel(
                self, self.dev_pref.substitute(propty=prop+'-Mon'))

            ld_propspd = QLabel(prop+' Speed [mm/s]', self)
            sb_propspd = SiriusSpinbox(
                self, self.dev_pref.substitute(propty=prop+'Speed-SP'))
            lb_propspd = SiriusLabel(
                self, self.dev_pref.substitute(propty=prop+'Speed-RB'))
            lb_propspdmon = SiriusLabel(
                self, self.dev_pref.substitute(propty=prop+'Speed-Mon'))

            axis = 'A and B' if prop == 'Phase' else 'S and I'
            ld_enbl = QLabel('Allow '+prop+' Motion', self)
            ld_enbl.setToolTip('Enable '+axis+' Axis and Release Brakes')
            pvname = self.dev_pref.substitute(
                propty='EnblAndRelease'+prop+'-Sel')
            pb_movdsbl = PyDMPushButton(
                parent=self, label='Dsbl', init_channel=pvname, pressValue=0)
            pb_movdsbl.setObjectName('btn')
            pb_movdsbl.setStyleSheet('#btn{min-width:3em; max-width:3em;}')
            pb_movenbl = PyDMPushButton(
                parent=self, label='Enbl', init_channel=pvname, pressValue=1)
            pb_movenbl.setObjectName('btn')
            pb_movenbl.setStyleSheet('#btn{min-width:3em; max-width:3em;}')
            led_movsts = SiriusLedState(
                self, self.dev_pref.substitute(
                    propty='AllowedToChange'+prop+'-Mon'))
            hbox_enbl = QHBoxLayout()
            hbox_enbl.setContentsMargins(0, 0, 0, 0)
            hbox_enbl.setSpacing(3)
            hbox_enbl.addWidget(pb_movdsbl)
            hbox_enbl.addWidget(pb_movenbl)
            hbox_enbl.addWidget(led_movsts)
            hbox_enbl.addStretch()

            ld_propismov = QLabel(prop+' Motion', self)
            pb_propstop = PyDMPushButton(
                self, label='', icon=qta.icon('fa5s.stop'))
            pb_propstop.setToolTip(
                'Stop all'+prop+'motion, lock all brakes.')
            pvname = self.dev_pref.substitute(propty='Stop'+prop+'-Cmd')
            pb_propstop.channel = pvname
            pb_propstop.pressValue = 1  # Stop
            pb_propstop.setObjectName('Stop')
            pb_propstop.setStyleSheet(
                '#Stop{min-width:30px; max-width:30px; icon-size:25px;}')
            pb_propstart = PyDMPushButton(
                self, label='', icon=qta.icon('fa5s.play'))
            pb_propstart.setToolTip(
                'Start automatic '+prop+' motion towards previously '
                'entered setpoint.')
            pvname = self.dev_pref.substitute(propty='Change'+prop+'-Cmd')
            pb_propstart.channel = pvname
            pb_propstart.pressValue = 1
            pb_propstart.setObjectName('Start')
            pb_propstart.setStyleSheet(
                '#Start{min-width:30px; max-width:30px; icon-size:25px;}')
            hbox_mov = QHBoxLayout()
            hbox_mov.setSpacing(24)
            hbox_mov.addWidget(pb_propstop)
            hbox_mov.addWidget(pb_propstart)
            hbox_mov.addStretch()

            lay.addWidget(ld_prop, row, 0)
            lay.addWidget(sb_prop, row, 1)
            lay.addWidget(lb_prop, row, 2)
            lay.addWidget(lb_propmon, row, 3)
            lay.addWidget(ld_propspd, row+1, 0)
            lay.addWidget(sb_propspd, row+1, 1)
            lay.addWidget(lb_propspd, row+1, 2)
            lay.addWidget(lb_propspdmon, row+1, 3)
            lay.addWidget(ld_enbl, row+2, 0)
            lay.addLayout(hbox_enbl, row+2, 1, 1, 3)
            lay.addWidget(ld_propismov, row+3, 0)
            lay.addLayout(hbox_mov, row+3, 1, 1, 3)
            lay.addItem(
                QSpacerItem(1, 15, QSzPlcy.Ignored, QSzPlcy.Fixed), row+4, 0)

            row += 5

        self._ld_stopall = QLabel('Stop all', self)
        self._pb_stopall = PyDMPushButton(
                self, label='', icon=qta.icon('fa5s.times'))
        self._pb_stopall.setToolTip('Stop all motion, lock all brakes.')
        pvname = self.dev_pref.substitute(propty='Stop-Cmd')
        self._pb_stopall.channel = pvname
        self._pb_stopall.pressValue = 1
        self._pb_stopall.setObjectName('Stop')
        self._pb_stopall.setStyleSheet(
            '#Stop{min-width:30px; max-width:30px; icon-size:25px;}')

        self._ld_ismov = QLabel('Moving', self)
        self._led_ismov = SiriusLedState(
            self, self.dev_pref.substitute(propty='Moving-Mon'))

        lay.addWidget(self._ld_stopall, row, 0)
        lay.addWidget(self._pb_stopall, row, 1)
        lay.addWidget(self._ld_ismov, row+1, 0)
        lay.addWidget(self._led_ismov, row+1, 1, alignment=Qt.AlignLeft)

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
            self._pb_dtlsts, EPUDriveDetails, self,
            prefix=self._prefix, device=self._device)

        self._ld_isbusy = QLabel('Is Busy', self)
        self._led_isbusy = SiriusLedAlert(
            self, self.dev_pref.substitute(propty='IsBusy-Mon'))

        self._ld_status = QLabel('Status', self)
        self._led_status = SiriusLedAlert(
            self, self.dev_pref.substitute(propty='Status-Mon'))

        self._log = PyDMLogLabel(
            self, init_channel=self.dev_pref.substitute(propty='Log-Mon'))
        self._log.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.MinimumExpanding)
        self._log.setAlternatingRowColors(True)
        self._log.maxCount = 2000

        self._bt_logclear = QPushButton('Clear Log', self)
        self._bt_logclear.clicked.connect(self._log.clear)

        gbox = QGroupBox('Status')
        lay = QGridLayout(gbox)
        lay.addWidget(self._led_isbusy, 0, 0, alignment=Qt.AlignRight)
        lay.addWidget(self._ld_isbusy, 0, 1)
        lay.addWidget(self._pb_dtlsts, 0, 2, alignment=Qt.AlignRight)
        lay.addWidget(self._led_status, 1, 0, alignment=Qt.AlignRight)
        lay.addWidget(self._ld_status, 1, 1)
        lay.addWidget(self._log, 2, 0, 1, 3)
        lay.addWidget(self._bt_logclear, 3, 0, 1, 3, alignment=Qt.AlignCenter)
        return gbox

    def _ctrlModeWidget(self):
        return None

    def _auxCommandsWidget(self):
        self._ld_phsspdlim = QLabel('Max Phase\nSpeed [mm/s]', self)
        self._sb_phsspdlim = SiriusSpinbox(
            self, self.dev_pref.substitute(propty='MaxPhaseSpeed-SP'))
        self._sb_phsspdlim.setStyleSheet('max-width:4.5em;')
        self._lb_phsspdlim = SiriusLabel(
            self, self.dev_pref.substitute(propty='MaxPhaseSpeed-RB'))

        self._ld_gapspdlim = QLabel('Max Gap\nSpeed [mm/s]', self)
        self._sb_gapspdlim = SiriusSpinbox(
            self, self.dev_pref.substitute(propty='MaxGapSpeed-SP'))
        self._sb_gapspdlim.setStyleSheet('max-width:4.5em;')
        self._lb_gapspdlim = SiriusLabel(
            self, self.dev_pref.substitute(propty='MaxGapSpeed-RB'))

        gbox = QGroupBox('Auxiliary Commands', self)
        lay = QGridLayout(gbox)
        lay.addWidget(self._ld_phsspdlim, 0, 0)
        lay.addWidget(self._sb_phsspdlim, 0, 1)
        lay.addWidget(self._lb_phsspdlim, 0, 2)
        lay.addWidget(self._ld_gapspdlim, 1, 0)
        lay.addWidget(self._sb_gapspdlim, 1, 1)
        lay.addWidget(self._lb_gapspdlim, 1, 2)
        gbox.setStyleSheet(
            '.QLabel{qproperty-alignment: "AlignRight | AlignVCenter";}')
        return gbox


class EPUSummaryBase(IDCommonSummaryBase):
    """EPU Summary Base Widget."""

    MODEL_WIDTHS = (
        ('Status', 4),
        ('Kx', 6),
        ('Ky', 6),
        ('Phase', 6),
        ('Phase Speed', 6),
        ('Start Phase', 4),
        ('Stop Phase', 4),
        ('Gap', 6),
        ('Gap Speed', 6),
        ('Start Gap', 4),
        ('Stop Gap', 4),
    )


class EPUSummaryHeader(IDCommonSummaryHeader, EPUSummaryBase):
    """EPU Summary Header."""


class EPUSummaryWidget(IDCommonSummaryWidget, EPUSummaryBase):
    """EPU Summary Widget."""

    def _get_widgets(self, prop):
        wids, orientation = super()._get_widgets(prop)
        if not wids:
            orientation = 'v'
        if prop == 'Status':
            led = PyDMLedMultiChannel(
                self,
                {self.dev_pref.substitute(propty='Alarm-Mon'): 0,
                 self.dev_pref.substitute(propty='IntlkInStop-Mon'): 0,
                 self.dev_pref.substitute(propty='IntlkInEOpnGap-Mon'): 0,
                 self.dev_pref.substitute(propty='IntlkOutPwrEnbld-Mon'): 1,
                 self.dev_pref.substitute(propty='IsOperational-Mon'): 1})
            wids.append(led)
        elif prop == 'Kx':
            spb = SiriusSpinbox(
                self, self.dev_pref.substitute(propty='Kx-SP'))
            wids.append(spb)
            lbl = SiriusLabel(
                self, self.dev_pref.substitute(propty='Kx-Mon'))
            wids.append(lbl)
        elif prop == 'Ky':
            spb = SiriusSpinbox(
                self, self.dev_pref.substitute(propty='Ky-SP'))
            wids.append(spb)
            lbl = SiriusLabel(
                self, self.dev_pref.substitute(propty='Ky-Mon'))
            wids.append(lbl)
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
        elif prop == 'Gap':
            spb = SiriusSpinbox(
                self, self.dev_pref.substitute(propty='Gap-SP'))
            wids.append(spb)
            lbl = SiriusLabel(
                self, self.dev_pref.substitute(propty='Gap-Mon'))
            wids.append(lbl)
        elif prop == 'Gap Speed':
            spb = SiriusSpinbox(
                self, self.dev_pref.substitute(propty='GapSpeed-SP'))
            wids.append(spb)
            lbl = SiriusLabel(
                self, self.dev_pref.substitute(propty='GapSpeed-Mon'))
            wids.append(lbl)
        elif prop == 'Start Gap':
            btn = PyDMPushButton(self, label='', icon=qta.icon('fa5s.play'))
            btn.setToolTip(
                'Start automatic motion towards previously entered setpoint.')
            btn.channel = self.dev_pref.substitute(propty='ChangeGap-Cmd')
            btn.pressValue = 1
            btn.setObjectName('Start')
            btn.setStyleSheet(
                '#Start{min-width:30px; max-width:30px; icon-size:25px;}')
            wids.append(btn)
        elif prop == 'Stop Gap':
            btn = PyDMPushButton(self, label='', icon=qta.icon('fa5s.stop'))
            btn.setToolTip('Stop all motion, lock all brakes.')
            btn.channel = self.dev_pref.substitute(propty='StopGap-Cmd')
            btn.pressValue = 1
            btn.setObjectName('Stop')
            btn.setStyleSheet(
                '#Stop{min-width:30px; max-width:30px; icon-size:25px;}')
            wids.append(btn)
        return wids, orientation


class EPUDriveDetails(IDCommonDialog):
    """EPU Drive Details."""

    def __init__(self, parent=None, prefix='', device=''):
        super().__init__(
            parent, prefix, device, title=device+' Drive Details')

    def _setupUi(self):
        ld_respos = QLabel('Resolver Pos', self)
        ld_encpos = QLabel('Encoder Pos', self)
        ld_diagcode = QLabel('Diag Code', self)
        ld_diagmsg = QLabel('Diag Msg', self)
        ld_moving = QLabel('Moving', self)

        gbox = QGroupBox('Drive Status', self)
        glay = QGridLayout(gbox)
        glay.addWidget(ld_respos, 1, 0)
        glay.addWidget(ld_encpos, 2, 0)
        glay.addWidget(ld_diagcode, 3, 0)
        glay.addWidget(ld_diagmsg, 4, 0)
        glay.addWidget(ld_moving, 5, 0)

        for idx, drive in enumerate(['A', 'B', 'S', 'I']):
            col = idx + 1
            ld_drive = QLabel('Drive '+drive, self)

            pvname = self.dev_pref.substitute(
                propty='Drive'+drive+'ResolverPos-Mon')
            lb_respos = SiriusLabel(self, pvname)

            pvname = self.dev_pref.substitute(
                propty='Drive'+drive+'EncoderPos-Mon')
            lb_encpos = SiriusLabel(self, pvname)

            pvname = self.dev_pref.substitute(
                propty='Drive'+drive+'DiagCode-Mon')
            lb_diagcode = SiriusLabel(self, pvname)

            pvname = self.dev_pref.substitute(
                propty='Drive'+drive+'DiagMsg-Mon')
            lb_diagmsg = SiriusLabel(self, pvname)

            pvname = self.dev_pref.substitute(
                propty='Drive'+drive+'Moving-Mon')
            lb_moving = SiriusLabel(self, pvname)

            glay.addWidget(ld_drive, 0, col)
            glay.addWidget(lb_respos, 1, col)
            glay.addWidget(lb_encpos, 2, col)
            glay.addWidget(lb_diagcode, 3, col)
            glay.addWidget(lb_diagmsg, 4, col)
            glay.addWidget(lb_moving, 5, col)

        gbox.setStyleSheet(
            '.QLabel{qproperty-alignment: AlignCenter;}')
        lay = QHBoxLayout(self)
        lay.addWidget(gbox)
