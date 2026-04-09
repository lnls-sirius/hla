"""UE Control Module."""

from qtpy.QtCore import Qt, QSize
from qtpy.QtWidgets import QGroupBox, QLabel, QWidget, \
    QPushButton, QHBoxLayout, QGridLayout, QSizePolicy
import qtawesome as qta
from pydm.widgets import PyDMPushButton

from siriushla.util import connect_newprocess, connect_window
from ..widgets import SiriusLedAlert, SiriusLabel, SiriusSpinbox, \
    SiriusLedState, SiriusLineEdit, SiriusEnumComboBox
from ..widgets.dialog import StatusDetailDialog

from .base import IDCommonControlWindow, IDCommonDialog, \
    IDCommonSummaryBase, IDCommonSummaryHeader, IDCommonSummaryWidget


class UEControlWindow(IDCommonControlWindow):
    """UE Control Window."""

    OPERATION_PVS = {
        "Power Off": {
            "StateMon": "PowerOff-Mon"
        },
        "Kill Override": {
            "StateMon": "KillOverride-Mon"
        },
        "Is Remote": {
            "StateMon": "IsRemote-Mon"
        },
        "Device Status": {
            "StateMon": "DeviceStatus-Mon"
        },
    }

    MAIN_CONTROL_PVS = {
        "KParam": {
            "SP": "KParam-SP",
            "Mon": "KParam-Mon",
            "RB": "KParam-RB"
        },
        "Change KParam": {
            "Cmd": "KParamChange-Cmd",
            "icon": "fa5s.play"
        },
        "PParam": {
            "SP": "PParam-SP",
            "Mon": "PParam-Mon",
            "RB": "PParam-RB"
        },
        "Change PParam": {
            "Cmd": "PParamChange-Cmd",
            "icon": "fa5s.play"
        },
        "CParam": {
            "SP": "CParam-SP",
            "Mon": "CParam-Mon",
            "RB": "CParam-RB"
        },
        "Change CParam": {
            "Cmd": "CParamChange-Cmd",
            "icon": "fa5s.play"
        },
        "Offset": {
            "SP": "Offset-SP",
            "Mon": "Offset-Mon",
            "RB": "Offset-RB"
        },
        "Offset Speed": {
            "Mon": "OffsetVelo-Mon"
        },
        "Speed Setpoint": {
            "SP": "Velo-SP",
            "Mon": "Velo-Mon",
            "RB": "Velo-RB"
        },
        "Acc. Setpoint": {
            "SP": "Acc-SP",
            "Mon": "Acc-Mon",
            "RB": "Acc-RB"
        },
        "Pol": {
            "SP": "Pol-Sel",
            "Mon": "Pol-Mon",
            "RB": "Pol-RB"
        },
        "Moving": {
            "StateMon": "Moving-Mon"
        }
    }

    SCANS_PVS = {
        "Scan Mode": {
            "SP": "ScanMode-Sel"
        },
        "Scan Done": {
            "StateMon": "ScanDone-Mon"
        },
        "Read Traj": {
            "Cmd": "ReadTraj-Cmd",
            "icon": "fa5s.play"
        },
        "Write Traj": {
            "Cmd": "WriteTraj-Cmd",
            "icon": "mdi.keyboard-return"
        },
        "Fly First Pos": {
            "StateMon": "FlyFirstPos-Mon"
        },
    }

    def _mainControlsWidget(self):
        group = QGroupBox('Main Controls')
        lay = QGridLayout()
        lay.setContentsMargins(3, 3, 3, 3)
        group.setLayout(lay)

        lay.addWidget(
            QLabel('<h4>SP</h4>', self, alignment=Qt.AlignCenter), 0, 1)
        lay.addWidget(
            QLabel('<h4>RB</h4>', self, alignment=Qt.AlignCenter), 0, 2)
        lay.addWidget(
            QLabel('<h4>Mon</h4>', self, alignment=Qt.AlignCenter), 0, 3)

        row = 1
        for title, pv_info in self.MAIN_CONTROL_PVS.items():
            label = QLabel(
                title, self, alignment=Qt.AlignRight | Qt.AlignVCenter)
            label.setFixedWidth(150)
            lay.addWidget(label, row, 0)

            if isinstance(pv_info, dict):
                if "Cmd" in pv_info:
                    self._createCmdBtns(pv_info, lay, row)
                elif "StateMon" in pv_info:
                    self._createLedState(pv_info, lay, row)
                else:
                    self._createParam(pv_info, lay, row)
            else:
                raise NotImplementedError
            row += 1

        self._lb_start = QLabel(
            'Start Movement', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self._pb_start = PyDMPushButton(
            self, label='', icon=qta.icon("fa5s.play"))
        self._pb_start.channel = self.dev_pref.substitute(propty='DevCtrl-Cmd')
        self._pb_start.pressValue = 120
        self._pb_start.setObjectName("Start")
        self._pb_start.setStyleSheet(
            '#Start{min-width:30px; max-width:30px; icon-size:25px;}')

        self._lb_abort = QLabel(
            'Abort', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self._pb_abort = PyDMPushButton(
            self, label='', icon=qta.icon("fa5s.stop"))
        self._pb_abort.channel = self.dev_pref.substitute(propty='Abort-Cmd')
        self._pb_abort.pressValue = 1
        self._pb_abort.setObjectName("Stop")
        self._pb_abort.setStyleSheet(
            '#Stop{min-width:30px; max-width:30px; icon-size:25px;}')

        self._lb_reset = QLabel(
            'Reset', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self._pb_reset = PyDMPushButton(
            self, label='', icon=qta.icon('fa5s.sync'))
        self._pb_reset.channel = self.dev_pref.substitute(propty='DevCtrl-Cmd')
        self._pb_reset.pressValue = 100  # Reset
        self._pb_reset.setObjectName('Reset')
        self._pb_reset.setStyleSheet(
            '#Reset{min-width:30px; max-width:30px; icon-size:25px;}')

        lay.addWidget(self._lb_start, row, 0)
        lay.addWidget(self._pb_start, row, 1)
        lay.addWidget(self._lb_abort, row+1, 0)
        lay.addWidget(self._pb_abort, row+1, 1)
        lay.addWidget(self._lb_reset, row+2, 0)
        lay.addWidget(self._pb_reset, row+2, 1)

        return group

    def _statusWidget(self):
        gbox = QGroupBox("Status")
        gbox.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        lay = QGridLayout(gbox)
        lay.setVerticalSpacing(15)
        row = 0

        self._pb_dtls = QPushButton(
            "Servo Motors and General Status Details", self)
        self._pb_dtls.setIcon(qta.icon('fa5s.list-ul'))
        connect_window(
            self._pb_dtls, UEDetails, self,
            prefix=self._prefix, device=self._device)
        lay.addWidget(self._pb_dtls, row, 0, 1, 2)
        row += 1

        axis_status_labels = {
            'TOStatusIO-Mon': [
                'Min SW limit reached',
                'Max SW limit reached',
                'Min limit switch activated',
                'Max limit switch activated',
                'Min kill switch activated',
                'Max kill switch activated',
                'Pneumatic brake released',
                'Pneumatic brake locked',
                'Pneumatic brake Worn',
                'Linear encoder fault',
                'Driver channel fault'
            ],
            'TIStatusIO-Mon': [
                'Min SW limit reached',
                'Max SW limit reached',
                'Min limit switch activated',
                'Max limit switch activated',
                'Min kill switch activated',
                'Max kill switch activated',
                'Pneumatic brake released',
                'Pneumatic brake locked',
                'Pneumatic brake Worn',
                'Linear encoder fault',
                'Driver channel fault'
            ],
            'BOStatusIO-Mon': [
                'Min SW limit reached',
                'Max SW limit reached',
                'Min limit switch activated',
                'Max limit switch activated',
                'Min kill switch activated',
                'Max kill switch activated',
                'Pneumatic brake released',
                'Pneumatic brake locked',
                'Pneumatic brake Worn',
                'Linear encoder fault',
                'Driver channel fault'
            ],
            'BIStatusIO-Mon': [
                'Min SW limit reached',
                'Max SW limit reached',
                'Min limit switch activated',
                'Max limit switch activated',
                'Min kill switch activated',
                'Max kill switch activated',
                'Pneumatic brake released',
                'Pneumatic brake locked',
                'Pneumatic brake Worn',
                'Linear encoder fault',
                'Driver channel fault'
            ]
        }

        servos_lay = QGridLayout()
        servos_row = 0

        for status, labels in axis_status_labels.items():
            pvname = self.dev_pref.substitute(propty=status)
            servo_lbl = status.split('-')[0]
            lbl = QLabel(
                servo_lbl, self,
                alignment=Qt.AlignRight | Qt.AlignVCenter)
            read_sts = SiriusLedAlert(self, pvname)
            pbt = QPushButton('', self)
            pbt.setIcon(qta.icon('fa5s.ellipsis-v'))
            pbt.setObjectName('sts')
            pbt.setStyleSheet(
                '#sts{min-width:18px; max-width:18px; icon-size:20px;}')
            connect_window(
                pbt, StatusDetailDialog, pvname=pvname, parent=self,
                labels=labels, section="ID", title=f'{servo_lbl} Detailed Status')
            servos_lay.addWidget(lbl, servos_row, 0)
            servos_lay.addWidget(read_sts, servos_row, 1, alignment=Qt.AlignRight)
            servos_lay.addWidget(pbt, servos_row, 2, alignment=Qt.AlignLeft)
            servos_row += 1
        lay.addLayout(servos_lay, 1, 0, 1, 2, alignment=Qt.AlignHCenter)
        row += 1

        status2labels = {
            'DeviceStatus-Mon': [
                'Error',
                'Power Off',
                'Software limit enabled',
                'Hardware limit enabled',
                'Kill switches enabled',
                'Control enabled',
                'Moving',
                'Emergency stop button',
                'One or more SW limit reached',
                'One or more HW limit reached',
                'One or more kill SW reached'
            ]
        }

        for dev_sts, label in status2labels.items():
            pvname = self.dev_pref.substitute(propty=dev_sts)
            dev_lay = QGridLayout()
            dev_title = QLabel(f'<h4>{dev_sts}</h4>',
                               self, alignment=Qt.AlignCenter)
            dev_lay.addWidget(dev_title, 0, 0, alignment=Qt.AlignCenter)
            for idx, lbl in enumerate(label):
                sts_lbl = QLabel(lbl)
                irow = idx + 1
                read_sts = SiriusLedAlert(self, pvname, bit=idx)
                if lbl == "Error":
                    read_sts.onColor = SiriusLedState.Red
                else:
                    read_sts.onColor = SiriusLedState.Yellow
                dev_lay.addWidget(read_sts, irow, 0)
                dev_lay.addWidget(sts_lbl, irow, 1)
        lay.addLayout(dev_lay, row, 0)

        return gbox

    def _ctrlModeWidget(self):
        gbox = QGroupBox("Operation Status")
        gbox.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        lay = QGridLayout(gbox)
        lay.setVerticalSpacing(15)
        row = 0

        for title, pv_info in self.OPERATION_PVS.items():
            label = QLabel(
                title, self, alignment=Qt.AlignRight | Qt.AlignVCenter)
            label.setFixedWidth(150)
            lay.addWidget(label, row, 0)

            if isinstance(pv_info, dict):
                if "Cmd" in pv_info:
                    self._createCmdBtns(pv_info, lay, row)
                elif "StateMon" in pv_info:
                    self._createLedState(pv_info, lay, row)
                else:
                    self._createParam(pv_info, lay, row)
            else:
                raise NotImplementedError
            row += 1

        return gbox

    def _auxCommandsWidget(self):
        # scan controls
        scangroup = QGroupBox('Scan Controls')
        scanlay = QGridLayout()
        scanlay.setContentsMargins(3, 3, 3, 3)
        scangroup.setLayout(scanlay)

        row = 0
        for title, pv_info in self.SCANS_PVS.items():
            label = QLabel(
                title, self, alignment=Qt.AlignRight | Qt.AlignVCenter)
            label.setFixedWidth(150)
            scanlay.addWidget(label, row, 0)

            if isinstance(pv_info, dict):
                if "Cmd" in pv_info:
                    self._createCmdBtns(pv_info, scanlay, row)
                elif "StateMon" in pv_info:
                    self._createLedState(pv_info, scanlay, row)
                else:
                    self._createParam(pv_info, scanlay, row)
            else:
                raise NotImplementedError
            row += 1

        # auxiliary parameters
        auxgbox = QGroupBox('Auxiliary Parameters', self)

        self._speed_lim = QLabel('Max Speed [mm/s]', self)
        self._spin_box_sl = SiriusSpinbox(
            self, self.dev_pref.substitute(propty="MaxVelo-SP"))
        self._spin_box_sl.setStyleSheet('max-width:4.5em;')
        self._lb_spin_box_sl = SiriusLabel(
            self, self.dev_pref.substitute(propty="MaxVelo-RB"))

        self._ld_periodlen = QLabel('Period Length', self)
        self._lb_periodlen = SiriusLabel(
            self, self.dev_pref.substitute(propty='PeriodLength-Cte'))

        self._ld_kpark = QLabel('KParam Park Pos.', self)
        self._lb_kpark = SiriusLabel(
            self, self.dev_pref.substitute(propty='KParamParked-Cte'))

        self._ld_ppark = QLabel('PParam Park Pos.', self)
        self._lb_ppark = SiriusLabel(
            self, self.dev_pref.substitute(propty='PParamParked-Cte'))

        self._ld_cpark = QLabel('CParam Park Pos.', self)
        self._lb_cpark = SiriusLabel(
            self, self.dev_pref.substitute(propty='CParamParked-Cte'))

        self._lb_park = QLabel('Start Parking', self)
        self._pb_park = PyDMPushButton(
            self, label='', icon=qta.icon("fa5s.parking"))
        self._pb_park.channel = self.dev_pref.substitute(propty="StartParking-Cmd")
        self._pb_park.pressValue = 1
        self._pb_park.setIconSize(QSize(20, 20))
        self._pb_park.setMaximumWidth(25)
        self._pb_park.setStyleSheet(
            '#Start{min-width:30px; max-width:30px; icon-size:25px;}')

        auxlay = QGridLayout(auxgbox)
        auxlay.addWidget(self._speed_lim, 0, 0)
        auxlay.addWidget(self._spin_box_sl, 0, 1)
        auxlay.addWidget(self._lb_spin_box_sl, 0, 2)
        auxlay.addWidget(self._ld_periodlen, 1, 0)
        auxlay.addWidget(self._lb_periodlen, 1, 1)
        auxlay.addWidget(self._ld_kpark, 2, 0)
        auxlay.addWidget(self._lb_kpark, 2, 1)
        auxlay.addWidget(self._ld_ppark, 3, 0)
        auxlay.addWidget(self._lb_ppark, 3, 1)
        auxlay.addWidget(self._ld_cpark, 4, 0)
        auxlay.addWidget(self._lb_cpark, 4, 1)
        auxlay.addWidget(self._lb_park, 5, 0)
        auxlay.addWidget(self._pb_park, 5, 1)

        auxgbox.setStyleSheet(
            '.QLabel{qproperty-alignment: "AlignRight | AlignVCenter";}')

        group = QWidget()
        lay = QGridLayout(group)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(scangroup, 0, 0)
        lay.addWidget(auxgbox, 1, 0)

        return group

    def _ffSettingsWidget(self):
        but = QPushButton('Feedforward Settings', self)
        connect_newprocess(
            but, ['sirius-hla-si-ap-idff.py', self._device])
        return but

    def _createCmdBtns(self, pv_info, lay, row):
        btn = PyDMPushButton(self, label='', icon=qta.icon(pv_info["icon"]))
        btn.channel = self.dev_pref.substitute(propty=pv_info["Cmd"])
        btn.pressValue = 1
        btn.setIconSize(QSize(20, 20))
        btn.setMaximumWidth(25)
        btn.setStyleSheet(
            '#Start{min-width:30px; max-width:30px; icon-size:25px;}')
        lay.addWidget(btn, row, 1, 1, 4)

    def _createLedState(self, pv_info, lay, row):
        pvname = self.dev_pref.substitute(propty=pv_info["StateMon"])
        led = SiriusLedState(self, init_channel=pvname)
        lay.addWidget(led, row, 1, alignment=Qt.AlignLeft)

    def _createParam(self, pv_info, lay, row):
        if "SP" in pv_info:
            pvname = self.dev_pref.substitute(propty=pv_info["SP"])
            widtype = SiriusEnumComboBox if pvname.endswith('Sel') \
                else SiriusLineEdit
            cb = widtype(self, init_channel=pvname)
            lay.addWidget(cb, row, 1, 1, 1)

        for col, key in {2: "RB", 3: "Mon"}.items():
            if key not in pv_info:
                continue
            pvname = self.dev_pref.substitute(propty=pv_info[key])
            lbl = SiriusLabel(self, init_channel=pvname, keep_unit=True)
            lbl.setMinimumWidth(125)
            lbl.showUnits = True
            lbl.setAlignment(Qt.AlignCenter)
            lay.addWidget(lbl, row, col, 1, 1)


class UESummaryBase(IDCommonSummaryBase):
    """UE Summary Base Widget."""

    MODEL_WIDTHS = (
        ('Device Status', 4),
        ('KParam', 6),
        ('Speed', 6),
        ('Start', 4),
        ('Stop', 4),
    )


class UESummaryHeader(IDCommonSummaryHeader, UESummaryBase):
    """UE Summary Header."""


class UESummaryWidget(IDCommonSummaryWidget, UESummaryBase):
    """UE Summary Widget."""

    def _get_widgets(self, prop):
        wids, orientation = super()._get_widgets(prop)
        if prop == 'Device Status':
            led = SiriusLedAlert(
                self, self.dev_pref.substitute(propty='DeviceStatus-Mon'))
            wids.append(led)
        elif prop == 'KParam':
            spb = SiriusSpinbox(
                self, self.dev_pref.substitute(propty='KParam-SP'))
            wids.append(spb)
            lbl = SiriusLabel(
                self, self.dev_pref.substitute(propty='KParam-Mon'))
            wids.append(lbl)
        elif prop == 'Speed':
            spb = SiriusLineEdit(
                self, self.dev_pref.substitute(propty='Velo-SP'))
            wids.append(spb)
            lbl = SiriusLabel(
                self, self.dev_pref.substitute(propty='Velo-RB'))
            wids.append(lbl)
        elif prop == 'Start':
            btn = PyDMPushButton(self, label='', icon=qta.icon('fa5s.play'))
            btn.channel = self.dev_pref.substitute(propty='DevCtrl-Cmd')
            btn.pressValue = 120
            btn.setObjectName('Start')
            btn.setStyleSheet(
                '#Start{min-width:30px; max-width:30px; icon-size:25px;}')
            wids.append(btn)
        elif prop == 'Stop':
            btn = PyDMPushButton(self, label='', icon=qta.icon('fa5s.stop'))
            btn.setToolTip('Stop all motion, lock all brakes.')
            btn.channel = self.dev_pref.substitute(propty='Abort-Cmd')
            btn.pressValue = 1
            btn.setObjectName('Stop')
            btn.setStyleSheet(
                '#Stop{min-width:30px; max-width:30px; icon-size:25px;}')
            wids.append(btn)
        return wids, orientation


class UEDetails(IDCommonDialog):
    """UE Drive Details"""

    def __init__(self, parent=None, prefix='', device=''):
        """Init."""
        super().__init__(
            parent, prefix, device, title=device+' Servo Motors and General Status Details')

    def _setupUi(self):
        ld_pos = QLabel('<h4>Pos.</h4>', self)
        ld_posmin = QLabel('<h4>Min Pos.</h4>', self)
        ld_posmax = QLabel('<h4>Max Pos.</h4>', self)
        ld_ncstate = QLabel('<h4>NC State</h4>', self)
        ld_ncerror = QLabel('<h4>NC Error', self)
        ld_status = QLabel('<h4>StatusIO</h4>', self)
        ld_temp = QLabel('<h4>Temperature</h4>', self)

        gbox = QGroupBox('Status Details', self)
        glay = QGridLayout(gbox)
        glay.addWidget(ld_pos, 1, 0)
        glay.addWidget(ld_posmin, 2, 0)
        glay.addWidget(ld_posmax, 3, 0)
        glay.addWidget(ld_ncstate, 4, 0)
        glay.addWidget(ld_ncerror, 5, 0)
        glay.addWidget(ld_status, 6, 0)
        glay.addWidget(ld_temp, 7, 0)

        details = [
            "KParam",
            "PParam",
            "CParam",
            "Offset",
            "KShift",
            "PShift",
            "TI",
            "TO",
            "BI",
            "BO",
        ]

        for idx, title in enumerate(details):
            col = idx + 1
            posname = 'Pos' if title not in \
                ['KParam', 'PParam', 'CParam', 'Offset'] else ''
            ld_dtl = QLabel('<h4>'+title+'</h4>', self)

            if title not in ['KShift', 'PShift']:
                pvname = self.dev_pref.substitute(
                    propty=f'{title}{posname}-Mon')
                lb_pos = SiriusLabel(self, pvname)
            else:
                lb_pos = QLabel("-", self)

            if title in ['KParam', 'PParam', 'CParam', 'Offset']:
                pvname = self.dev_pref.substitute(
                    propty=f'{title}MinPos-Cte')
                lb_posmin = SiriusLabel(self, pvname)
                pvname = self.dev_pref.substitute(
                    propty=f'{title}MaxPos-Cte')
                lb_posmax = SiriusLabel(self, pvname)
            else:
                lb_posmin = QLabel("-", self)
                lb_posmax = QLabel("-", self)

            if title not in ['KParam', 'PParam']:
                pvname = self.dev_pref.substitute(
                    propty=f'{title}StateNC-Mon')
                lb_ncstate = SiriusLabel(self, pvname)
                pvname = self.dev_pref.substitute(
                propty=f'{title}ErrorNC-Mon')
                lb_ncerror = SiriusLabel(self, pvname)
            else:
                lb_ncstate = QLabel("-", self)
                lb_ncerror = QLabel("-", self)

            if title in ["TI", "TO", "BI", "BO"]:
                pvname = self.dev_pref.substitute(
                    propty=f'{title}StatusIO-Mon')
                lb_status = SiriusLabel(self, pvname)
                pvname = self.dev_pref.substitute(
                    propty=f'{title}Temp-Mon')
                lb_temp = SiriusLabel(self, pvname)
            else:
                lb_status = QLabel("-", self)
                lb_temp = QLabel("-", self)

            glay.addWidget(ld_dtl, 0, col)
            glay.addWidget(lb_pos, 1, col)
            glay.addWidget(lb_posmin, 2, col)
            glay.addWidget(lb_posmax, 3, col)
            glay.addWidget(lb_ncstate, 4, col)
            glay.addWidget(lb_ncerror, 5, col)
            glay.addWidget(lb_status, 6, col)
            glay.addWidget(lb_temp, 7, col)

        gbox.setStyleSheet(
            'QLabel{qproperty-alignment: AlignCenter; max-width: 12em;}')
        lay = QHBoxLayout(self)
        lay.addWidget(gbox)
