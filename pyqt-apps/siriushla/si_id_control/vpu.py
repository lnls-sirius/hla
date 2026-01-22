"""VPU Control Module."""

from qtpy.QtCore import Qt, QSize
from qtpy.QtWidgets import QGroupBox, QLabel, QWidget, \
    QPushButton, QHBoxLayout, QGridLayout, QSizePolicy
import qtawesome as qta
from pydm.widgets import PyDMPushButton

from ..util import connect_newprocess, connect_window
from ..widgets import SiriusLedAlert, SiriusLabel, SiriusSpinbox, \
    SiriusLedState, SiriusLineEdit, SiriusEnumComboBox
from ..widgets.dialog import StatusDetailDialog

from .base import IDCommonControlWindow, IDCommonDialog, \
    IDCommonSummaryBase, IDCommonSummaryHeader, IDCommonSummaryWidget


class VPUControlWindow(IDCommonControlWindow):
    """VPU Control Window."""

    MAIN_CONTROL_PVS = {
        "KParam": {
            "SP": "KParam-SP",
            "RB": "KParam-RB",
            "Mon": "KParam-Mon",
        },
        "Taper": {
            "SP": "Taper-SP",
            "RB": "Taper-RB",
            "Mon": "Taper-Mon",
        },
        "Taper Speed": {
            "Mon": "TaperVelo-Mon",
        },
        "Center Offset": {
            "SP": "CenterOffset-SP",
            "RB": "CenterOffset-RB",
            "Mon": "CenterOffset-Mon",
        },
        "Center Offset Speed": {
            "Mon": "CenterOffsetVelo-Mon",
        },
        "Pitch Offset": {
            "Mon": "PitchOffset-Mon",
        },
        "Pitch Offset Speed": {
            "Mon": "PitchOffsetVelo-Mon",
        },
        "Movement Speed": {
            "SP": "MoveVelo-SP",
            "RB": "MoveVelo-RB",
        },
        "Movement Acceleration": {
            "SP": "MoveAcc-SP",
            "RB": "MoveAcc-RB",
        },
        "Start Movement": {
            "Cmd": "MoveStart-Cmd",
            "icon": "fa5s.play",
        },
        "Abort": {
            "Cmd": "Abort-Cmd",
            "icon": "fa5s.stop",
        },
        "Reset": {
            "Cmd": "Reset-Cmd",
            "icon": "fa5s.sync",
        },
        "Moving": {
            "StateMon": "Moving-Mon",
        },
    }

    SCAN_CONTROL_PVS = {
        "Scan Mode": {
            "SP": "ScanMode-Sel",
            "RB": "ScanMode-Sel",
        },
        "Scan Mode Activate": {
            "Cmd": "ActivateScanMode-Cmd",
            "icon": "fa5s.check",
        },
        "Fly-Scan Start": {
            "Cmd": "FlyScanStart-Cmd",
            "icon": "fa5s.play",
        },
        "Scan Finished": {
            "StateMon": "ScanFinished-Mon",
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

        return group

    def _statusWidget(self):
        gbox = QGroupBox('Status')
        gbox.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        lay = QGridLayout(gbox)
        lay.setVerticalSpacing(15)
        row = 0

        self._pb_dtls = QPushButton('Servo Motors and Mode Details', self)
        self._pb_dtls.setIcon(qta.icon('fa5s.list-ul'))
        self._pb_dtls.setToolTip('Open Servo Motor Detailed Status View')
        connect_window(
            self._pb_dtls, VPUDetails, self,
            prefix=self._prefix, device=self._device)
        lay.addWidget(self._pb_dtls, row, 0, 1, 2)
        row += 1

        alarm2labels = {
            'Warning-Mon': [
                'Motor_axis_1_max_sw',
                'Motor_axis_1_min_sw',
                'Motor_axis_2_max_sw',
                'Motor_axis_2_min_sw',
                'Motor_axis_3_max_sw',
                'Motor_axis_3_min_sw',
                'Motor_axis_4_max_sw',
                'Motor_axis_4_min_sw',
                'Gap_max_sw',
                'Gap_min_sw',
                'Offset_max_sw',
                'Offset_min_sw',
                'Taper_max_sw',
                'Taper_min_sw',
                'Skew_max_sw',
                'Skew_min_sw',
                'Motor_axis_1_max_ls',
                'Motor_axis_1_min_ls',
                'Motor_axis_2_max_ls',
                'Motor_axis_2_min_ls',
                'Motor_axis_3_max_ls',
                'Motor_axis_3_min_ls',
                'Motor_axis_4_max_ls',
                'Motor_axis_4_min_ls',
                'Kill_switch_override',
                'Power_off',
                'Targets_out_of_bounds',
            ],
            'Alarm-Mon': [
                'Machine_params_error',
                'Drive_1_error',
                'Drive_2_error',
                'Drive_3_error',
                'Drive_4_error',
                'Motor_axis_1_error',
                'Motor_axis_2_error',
                'Motor_axis_3_error',
                'Motor_axis_4_error',
                'Virtual_axis_1_error',
                'Virtual_axis_2_error',
                'Virtual_axis_3_error',
                'Virtual_axis_4_error',
                'Int_ZF_gap',
                'Estop_activated',
                'Motor_axis_1_max_kill_sw',
                'Motor_axis_1_min_kill_sw',
                'Motor_axis_2_max_kill_sw',
                'Motor_axis_2_min_kill_sw',
                'Motor_axis_3_max_kill_sw',
                'Motor_axis_3_min_kill_sw',
                'Motor_axis_4_max_kill_sw',
                'Motor_axis_4_min_kill_sw',
                'Encoder_1_error',
                'Encoder_2_error',
                'Encoder_3_error',
                'Encoder_4_error',
                'Drive_circuit_breaker',
            ],
        }
        alay = QGridLayout()
        arow = 0
        for status, labels in  alarm2labels.items():
            pvname = self.dev_pref.substitute(propty=status)
            title = status.split('-')[0]
            lbl = QLabel(
                title, self,
                alignment=Qt.AlignRight | Qt.AlignVCenter)
            read = SiriusLedAlert(self, pvname)
            if title == 'Warning':
                read.onColor = SiriusLedAlert.Yellow
            pbt = QPushButton('', self)
            pbt.setIcon(qta.icon('fa5s.ellipsis-v'))
            pbt.setObjectName('sts')
            pbt.setStyleSheet(
                '#sts{min-width:18px; max-width:18px; icon-size:20px;}')
            connect_window(
                pbt, StatusDetailDialog, pvname=pvname, parent=self,
                labels=labels, section="ID", title=f'{title} Detailed')
            alay.addWidget(lbl, arow, 0)
            alay.addWidget(read, arow, 1, alignment=Qt.AlignRight)
            alay.addWidget(pbt, arow, 2, alignment=Qt.AlignLeft)
            arow += 1
        pvname = self.dev_pref.substitute(propty='Warning-Mon')
        power_off_lbl = QLabel('Power Off')
        power_off_led = SiriusLedAlert(self, init_channel=pvname, bit=25)
        power_off_led.onColor = SiriusLedAlert.Yellow
        alay.addWidget(power_off_lbl, arow, 0)
        alay.addWidget(power_off_led, arow, 1, alignment=Qt.AlignRight)
        lay.addLayout(alay, 1, 0, 1, 2, alignment=Qt.AlignHCenter)
        row += 1

        status2labels = {
            'State-Mon': [
                'Error',
                'LimitSw_SW_MIN',
                'LimitSw_SW_MAX',
                'LimitSw_HW_MIN',
                'LimitSW_HW_MAX',
                'KillSW_HW_MIN',
                'KillSW_HW_MAX',
                'BrakeDisabled',
                'ControllerEnabled',
            ],
            'Flags-Mon': [
                'Connected',
                'Error',
                'LocalControl',
                'RemoteControl',
                'Moving',
                'Debug',
                'SWLimitSwitchEnabled',
                'HWLimitSwitchEnabled',
                'KillSwitchEnabled',
                'INT_Permission_To_Move',
                'INT_ZF_GAP',
            ],
        }
        vcol = 0
        for status, labels in status2labels.items():
            pvname = self.dev_pref.substitute(propty=status)
            vlay = QGridLayout()
            lbl = QLabel('<h4>'+status+'</h4>', self, alignment=Qt.AlignCenter)
            vlay.addWidget(lbl, 0, 0, 1, 2)
            for idx, lbl in enumerate(labels):
                irow = idx + 1
                read = SiriusLedState(self, pvname, bit=idx)
                if lbl == 'Error':
                    read.onColor = SiriusLedState.Red
                else:
                    read.onColor = SiriusLedState.Yellow
                vlay.addWidget(read, irow, 0)
                vlay.addWidget(QLabel(lbl), irow, 1)
            lay.addLayout(vlay, row, vcol, alignment=Qt.AlignTop)
            vcol += 1

        return gbox

    def _auxCommandsWidget(self):
        # scan controls
        scangroup = QGroupBox('Scan Controls')
        scanlay = QGridLayout()
        scanlay.setContentsMargins(3, 3, 3, 3)
        scangroup.setLayout(scanlay)

        scanlay.addWidget(
            QLabel('<h4>SP</h4>', self, alignment=Qt.AlignCenter), 0, 1)
        scanlay.addWidget(
            QLabel('<h4>RB</h4>', self, alignment=Qt.AlignCenter), 0, 2)

        row = 1
        for title, pv_info in self.SCAN_CONTROL_PVS.items():
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

        # auxiliary Parameters
        auxgbox = QGroupBox('Auxiliary Parameters', self)

        self._ld_speedlim = QLabel('Max Speed [mm/s]', self)
        self._sb_speedlim = SiriusSpinbox(
            self, self.dev_pref.substitute(propty='KParamMaxVelo-SP'))
        self._sb_speedlim.setStyleSheet('max-width:4.5em;')
        self._lb_speedlim = SiriusLabel(
            self, self.dev_pref.substitute(propty='KParamMaxVelo-RB'))

        self._ld_periodlen = QLabel('Period Length', self)
        self._lb_periodlen = SiriusLabel(
            self, self.dev_pref.substitute(propty='PeriodLength-Cte'))

        self._ld_park = QLabel('KParam Park Pos.', self)
        self._lb_park = SiriusLabel(
            self, self.dev_pref.substitute(propty='KParamParked-Cte'))

        # TODO: add StartParking-Cmd if implemented

        auxlay = QGridLayout(auxgbox)
        auxlay.addWidget(self._ld_speedlim, 0, 0)
        auxlay.addWidget(self._sb_speedlim, 0, 1)
        auxlay.addWidget(self._lb_speedlim, 0, 2)
        auxlay.addWidget(self._ld_periodlen, 1, 0)
        auxlay.addWidget(self._lb_periodlen, 1, 1)
        auxlay.addWidget(self._ld_park, 2, 0)
        auxlay.addWidget(self._lb_park, 2, 1)
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

    # --- auxiliary methods ---

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

    def _createLedState(self, pv_info, lay, row):
        pvname = self.dev_pref.substitute(propty=pv_info["StateMon"])
        led = SiriusLedState(self, init_channel=pvname)
        lay.addWidget(led, row, 1, alignment=Qt.AlignLeft)

    def _createCmdBtns(self, pv_info, lay, row):
        btn = PyDMPushButton(self, label='', icon=qta.icon(pv_info["icon"]))
        btn.channel = self.dev_pref.substitute(propty=pv_info["Cmd"])
        btn.pressValue = 1
        btn.setIconSize(QSize(20, 20))
        btn.setMaximumWidth(25)
        btn.setStyleSheet(
            '#Start{min-width:30px; max-width:30px; icon-size:25px;}')
        lay.addWidget(btn, row, 1, 1, 4)


class VPUSummaryBase(IDCommonSummaryBase):
    """VPU Summary Base Widget."""

    MODEL_WIDTHS = (
        ('Alarms', 4),
        ('KParam', 6),
        ('Speed', 6),
        ('Start', 4),
        ('Stop', 4),
    )


class VPUSummaryHeader(IDCommonSummaryHeader, VPUSummaryBase):
    """VPU Summary Header."""


class VPUSummaryWidget(IDCommonSummaryWidget, VPUSummaryBase):
    """VPU Summary Widget."""

    def _get_widgets(self, prop):
        wids, orientation = super()._get_widgets(prop)
        if prop == 'Alarms':
            led = SiriusLedAlert(
                self, self.dev_pref.substitute(propty='Alarm-Mon'))
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
                self, self.dev_pref.substitute(propty='MoveVelo-SP'))
            wids.append(spb)
            lbl = SiriusLabel(
                self, self.dev_pref.substitute(propty='MoveVelo-RB'))
            wids.append(lbl)
        elif prop == 'Start':
            btn = PyDMPushButton(self, label='', icon=qta.icon('fa5s.play'))
            btn.channel = self.dev_pref.substitute(propty='MoveStart-Cmd')
            btn.pressValue = 1
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


class VPUDetails(IDCommonDialog):
    """VPU Drive Details."""

    def __init__(self, parent=None, prefix='', device=''):
        """Init."""
        super().__init__(
            parent, prefix, device, title=device+' Servo Motor and Mode Details')

    def _setupUi(self):
        ld_speed = QLabel('<h4>Speed</h4>', self)
        ld_pos = QLabel('<h4>Pos.</h4>', self)
        ld_posmin = QLabel('<h4>Min Pos.</h4>', self)
        ld_posmax = QLabel('<h4>Max Pos.</h4>', self)
        ld_error = QLabel('<h4>Error</h4>', self)
        ld_errenc = QLabel('<h4>Error Encoder</h4>', self)
        ld_ncstate = QLabel('<h4>NC State</h4>', self)
        ld_status = QLabel('<h4>Status</h4>', self)

        gbox = QGroupBox('Status Details', self)
        glay = QGridLayout(gbox)
        glay.addWidget(ld_speed, 1, 0)
        glay.addWidget(ld_pos, 2, 0)
        glay.addWidget(ld_posmin, 3, 0)
        glay.addWidget(ld_posmax, 4, 0)
        glay.addWidget(ld_error, 5, 0)
        glay.addWidget(ld_errenc, 6, 0)
        glay.addWidget(ld_ncstate, 7, 0)
        glay.addWidget(ld_status, 8, 0)

        details = [
            "KParam",
            "CenterOffset",
            "Taper",
            "PitchOffset",
            "ServoMotor1",
            "ServoMotor2",
            "ServoMotor3",
            "ServoMotor4",
        ]

        for idx, title in enumerate(details):
            col = idx + 1
            posname = 'Pos' if title not in \
                ['KParam', 'Taper', 'CenterOffset', 'PitchOffset'] else ''
            minmaxposname = 'Pos' if title not in \
                ['KParam', ] else ''
            ld_dtl = QLabel('<h4>'+title+'</h4>', self)

            pvname = self.dev_pref.substitute(
                propty=f'{title}Velo-Mon')
            lb_speed = SiriusLabel(self, pvname)

            pvname = self.dev_pref.substitute(
                propty=f'{title}{posname}-Mon')
            lb_pos = SiriusLabel(self, pvname)

            pvname = self.dev_pref.substitute(
                propty=f'{title}Min{minmaxposname}-Cte')
            lb_posmin = SiriusLabel(self, pvname)

            pvname = self.dev_pref.substitute(
                propty=f'{title}Max{minmaxposname}-Cte')
            lb_posmax = SiriusLabel(self, pvname)

            pvname = self.dev_pref.substitute(
                propty=f'{title}Error-Mon')
            lb_error = SiriusLabel(self, pvname)

            pvname = self.dev_pref.substitute(
                propty=f'{title}ErrorEncoder-Mon')
            lb_errenc = SiriusLabel(self, pvname)

            pvname = self.dev_pref.substitute(
                propty=f'{title}NCState-Mon')
            lb_ncstate = SiriusLabel(self, pvname)

            pvname = self.dev_pref.substitute(
                propty=f'{title}Status-Mon')
            lb_status = SiriusLabel(self, pvname)

            glay.addWidget(ld_dtl, 0, col)
            glay.addWidget(lb_speed, 1, col)
            glay.addWidget(lb_pos, 2, col)
            glay.addWidget(lb_posmin, 3, col)
            glay.addWidget(lb_posmax, 4, col)
            glay.addWidget(lb_error, 5, col)
            glay.addWidget(lb_errenc, 6, col)
            glay.addWidget(lb_ncstate, 7, col)
            glay.addWidget(lb_status, 8, col)

        gbox.setStyleSheet(
            'QLabel{qproperty-alignment: AlignCenter; max-width: 12em;}')
        lay = QHBoxLayout(self)
        lay.addWidget(gbox)
