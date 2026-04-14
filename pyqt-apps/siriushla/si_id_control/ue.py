"""UE Control Module."""

from qtpy.QtCore import Qt, QSize
from qtpy.QtWidgets import QGroupBox, QLabel, QWidget, \
    QPushButton, QHBoxLayout, QGridLayout, QVBoxLayout
import qtawesome as qta
from pydm.widgets import PyDMPushButton

from siriuspy.namesys import SiriusPVName as _PVName
from siriushla.util import connect_newprocess, connect_window
from ..widgets import SiriusLedAlert, SiriusLabel, SiriusSpinbox, \
    SiriusLedState, SiriusLineEdit, SiriusEnumComboBox, \
    PyDMStateButton
from ..widgets.dialog import StatusDetailDialog

from .base import IDCommonControlWindow, IDCommonDialog, \
    IDCommonSummaryBase, IDCommonSummaryHeader, IDCommonSummaryWidget


class UEControlWindow(IDCommonControlWindow):
    """UE Control Window."""

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
        "Speed": {
            "SP": "Velo-SP",
            "RB": "Velo-RB"
        },
        "Acc.": {
            "SP": "Acc-SP",
            "RB": "Acc-RB"
        },
        "Pol": {
            "SP": "Pol-Sel",
            "Mon": "Pol-Mon",
            "RB": "Pol-Sts"
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

        self._lb_pol = QLabel(
            'Change Polarization', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self._pb_pol = PyDMPushButton(
            self, label='', icon=qta.icon('fa5s.play'))
        self._pb_pol.channel = self.dev_pref.substitute(propty='PolChange-Cmd')
        self._pb_pol.pressValue = 1
        self._pb_pol.setObjectName('Change_Polarization')
        self._pb_pol.setStyleSheet(
            '#Change_Polarization{min-width:30px; max-width:30px; icon-size:25px;}')

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

        lay.addWidget(self._lb_pol, row, 0)
        lay.addWidget(self._pb_pol, row, 1)
        lay.addWidget(self._lb_abort, row+1, 0)
        lay.addWidget(self._pb_abort, row+1, 1)
        lay.addWidget(self._lb_reset, row+2, 0)
        lay.addWidget(self._pb_reset, row+2, 1)

        return group

    def _statusWidget(self):
        gbox = QGroupBox("Status")
        lay = QVBoxLayout(gbox)
        lay.addStretch()

        self._pb_dtls = QPushButton(
            "Servo Motors and General Status Details", self)
        self._pb_dtls.setIcon(qta.icon('fa5s.list-ul'))
        connect_window(
            self._pb_dtls, UEDetails, self,
            prefix=self._prefix, device=self._device)
        lay.addWidget(self._pb_dtls)
        lay.addStretch()

        propty = 'Alarm-Mon'
        alarm_labels = [
            'Error',
            'Power Off',
            'Software limit disabled',
            'Hardware limit disabled',
            'Kill switches enabled',
            'Emergency stop button',
            'One or more SW limit reached',
            'One or more HW limit reached',
            'One or more kill SW reached',
        ]
        pvname = self.dev_pref.substitute(propty=propty)
        lbl_alarm = QLabel(
            'Alarm', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        led_alarm = SiriusLedAlert(self, pvname)
        pbt_alarm = QPushButton('', self)
        pbt_alarm.setIcon(qta.icon('fa5s.ellipsis-v'))
        pbt_alarm.setObjectName('sts')
        pbt_alarm.setStyleSheet(
            '#sts{min-width:18px; max-width:18px; icon-size:20px;}')
        connect_window(
            pbt_alarm, StatusDetailDialog, pvname=pvname, parent=self,
            labels=alarm_labels, section="ID", title=f'Alarm Details',
        )
        alarm_lay = QHBoxLayout()
        alarm_lay.addStretch()
        alarm_lay.addWidget(lbl_alarm)
        alarm_lay.addWidget(led_alarm)
        alarm_lay.addWidget(pbt_alarm)
        alarm_lay.addStretch()
        lay.addLayout(alarm_lay)

        warning_opr_lay = QGridLayout()
        propty_pwr = 'PowerOff-Mon'
        pvname_pwr = self.dev_pref.substitute(propty=propty_pwr)
        pwr_lbl = QLabel("Power Off")
        pwr_led = SiriusLedAlert(self, pvname_pwr)
        warning_opr_lay.addWidget(pwr_lbl, 0, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)
        warning_opr_lay.addWidget(pwr_led, 0, 1, alignment=Qt.AlignLeft | Qt.AlignVCenter)

        propty_ko = 'KillOverride-Mon'
        pvname_ko = self.dev_pref.substitute(propty=propty_ko)
        ko_led = SiriusLedAlert(self, pvname_ko)
        ko_lbl = QLabel("Kill Override")
        warning_opr_lay.addWidget(ko_lbl, 1, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)
        warning_opr_lay.addWidget(ko_led, 1, 1, alignment=Qt.AlignLeft | Qt.AlignVCenter)

        lay.addLayout(warning_opr_lay)
        lay.addStretch()

        propty = 'DeviceStatus-Mon'
        devsts_labels = [
            'Error',
            'Power Off',
            'Software limit disabled',
            'Hardware limit disabled',
            'Kill switches enabled',
            'Control enabled',
            'Moving',
            'Emergency stop button',
            'One or more SW limit reached',
            'One or more HW limit reached',
            'One or more kill SW reached',
        ]
        pvname = self.dev_pref.substitute(propty=propty)
        dev_lay = QGridLayout()
        dev_title = QLabel(f'<h4>{propty}</h4>',
                            self, alignment=Qt.AlignCenter)
        dev_lay.addWidget(dev_title, 0, 0, 1, 2, alignment=Qt.AlignCenter)
        for idx, lbl in enumerate(devsts_labels):
            sts_lbl = QLabel(lbl)
            irow = idx + 1
            read_sts = SiriusLedState(self, pvname, bit=idx)
            if lbl not in ['Control enabled', 'Moving']:
                read_sts.onColor = SiriusLedState.Red
            else:
                read_sts.onColor = SiriusLedState.Yellow
            dev_lay.addWidget(read_sts, irow, 0)
            dev_lay.addWidget(sts_lbl, irow, 1)
        lay.addLayout(dev_lay)
        lay.addStretch()

        return gbox

    def _ctrlModeWidget(self):
        gbox = QGroupBox("Operation Status")
        lay = QGridLayout(gbox)

        propty_ir = 'IsRemote-Mon'
        pvname_ir = self.dev_pref.substitute(propty=propty_ir)
        ir_lbl = QLabel("Is Remote")
        ir_led = SiriusLedState(self, pvname_ir)
        ir_led.offColor = SiriusLedState.Red
        lay.addWidget(ir_lbl, 0, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)
        lay.addWidget(ir_led, 0, 1, alignment=Qt.AlignLeft | Qt.AlignVCenter)

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
        group = QGroupBox('Feedforward Settings')
        lay = QGridLayout(group)

        hlay = QHBoxLayout()
        lb_glob = QLabel(
            "Global Loop State:", alignment=Qt.AlignRight | Qt.AlignVCenter
        )
        idff_pref = _PVName(f"SI-{self.dev_pref.sub}:BS-IDFF")
        self.bt_idffglob = PyDMStateButton(
            self, init_channel=idff_pref.substitute(propty="LoopState-Sel")
        )
        self.led_idffglob = SiriusLedState(
            self, init_channel=idff_pref.substitute(propty="LoopState-Sts")
        )
        hlay.addStretch()
        hlay.addWidget(lb_glob)
        hlay.addWidget(self.bt_idffglob)
        hlay.addWidget(self.led_idffglob)
        hlay.addStretch()
        lay.addLayout(hlay, 0, 0, 1, 3)

        for col, idffgroup in enumerate(["CHCV", "QS", "LC"]):
            but = QPushButton(f'{idffgroup}', self)
            connect_newprocess(
                but, ['sirius-hla-si-ap-idff.py', self._device,
                '-g', idffgroup]
            )
            lay.addWidget(but, 1, col)
        return group

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
        ('Alarms', 4),
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
        ld_torque = QLabel('<h4>Torque</h4>', self)

        gbox = QGroupBox('Status Details', self)
        glay = QGridLayout(gbox)
        glay.addWidget(ld_pos, 1, 0)
        glay.addWidget(ld_posmin, 2, 0)
        glay.addWidget(ld_posmax, 3, 0)
        glay.addWidget(ld_ncstate, 4, 0)
        glay.addWidget(ld_ncerror, 5, 0)
        glay.addWidget(ld_status, 6, 0)
        glay.addWidget(ld_temp, 7, 0)
        glay.addWidget(ld_torque, 8, 0)

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
                propty = f'{title}StatusIO-Mon'
                pvname = self.dev_pref.substitute(propty=propty)
                wid_stsio = QWidget()
                status_labels = [
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
                pbt_stsio = QPushButton('', self)
                pbt_stsio.setIcon(qta.icon('fa5s.ellipsis-v'))
                pbt_stsio.setObjectName('sts')
                pbt_stsio.setStyleSheet(
                    '#sts{min-width:18px; max-width:18px; icon-size:20px;}')
                connect_window(
                    pbt_stsio, StatusDetailDialog, pvname=pvname, parent=self,
                    labels=status_labels, section="ID", title=propty,
                    on_color=SiriusLedAlert.Yellow,
                    off_color=SiriusLedAlert.DarkGreen,
                )
                lb_stsio = SiriusLabel(self, pvname)
                lay_stsio = QHBoxLayout(wid_stsio)
                lay_stsio.setContentsMargins(0, 0, 0, 0)
                lay_stsio.addWidget(lb_stsio, alignment=Qt.AlignRight)
                lay_stsio.addWidget(pbt_stsio, alignment=Qt.AlignLeft)

                pvname = self.dev_pref.substitute(propty=f'{title}Temp-Mon')
                lb_temp = SiriusLabel(self, pvname)

                pvname = self.dev_pref.substitute(propty=f'{title}Torque-Mon')
                lb_torque = SiriusLabel(self, pvname)
            else:
                wid_stsio = QLabel("-", self)
                lb_temp = QLabel("-", self)
                lb_torque = QLabel("-", self)

            glay.addWidget(ld_dtl, 0, col)
            glay.addWidget(lb_pos, 1, col)
            glay.addWidget(lb_posmin, 2, col)
            glay.addWidget(lb_posmax, 3, col)
            glay.addWidget(lb_ncstate, 4, col)
            glay.addWidget(lb_ncerror, 5, col)
            glay.addWidget(wid_stsio, 6, col)
            glay.addWidget(lb_temp, 7, col)
            glay.addWidget(lb_torque, 8, col)

        gbox.setStyleSheet(
            'QLabel{qproperty-alignment: AlignCenter; max-width: 12em;}')
        lay = QHBoxLayout(self)
        lay.addWidget(gbox)
