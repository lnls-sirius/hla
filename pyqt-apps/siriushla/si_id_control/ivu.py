"""IVU Control Module."""

from qtpy.QtCore import Qt, QSize
from qtpy.QtWidgets import QGroupBox, QLabel, \
    QHBoxLayout, QPushButton, QWidget, \
    QGridLayout, QVBoxLayout
import qtawesome as qta
from pydm.widgets import PyDMPushButton

from ..util import connect_newprocess, connect_window
from ..widgets import SiriusLedAlert, SiriusLabel, SiriusSpinbox, \
    PyDMLed, PyDMStateButton, SiriusLineEdit, SiriusLedState

from .base import IDCommonControlWindow, IDCommonDialog, \
    IDCommonSummaryBase, IDCommonSummaryHeader, IDCommonSummaryWidget

import json


class IVUControlWindow(IDCommonControlWindow):
    """IVU Control Window."""

    MAIN_CONTROL_PVS = {
        "KParam": {
            "SP": "KParam-SP",
            "RB": "KParam-RB",
            "Mon": "KParam-Mon"
        },
        "KParam Speed": {
            "SP": "KParamVelo-SP",
            "RB": "KParamVelo-RB"
        },
        "KParam Taper": {
            "SP": "KParamTaper-SP",
            "RB": "KParamTaper-RB",
            "Mon": "KParamTaper-Mon"
        },
        "Center Mode": {
            "Sel": "CenterMode-Sel",
            "Sts": "CenterMode-Sts",
            "Mon": "CenterOffset-SP"
        },
        "Center Offset": {
            "SP": "CenterOffset-SP",
            "RB": "CenterOffset-RB",
            "Mon": "CenterOffset-Mon"
        },
        "Pitch Mode": {
            "Sel": "PitchMode-Sel",
            "Sts": "PitchMode-Sts",
            "Mon": "PitchOffset-SP"
        },
        "Pitch Offset": {
            "SP": "PitchOffset-SP",
            "RB": "PitchOffset-RB",
            "Mon": "PitchOffset-Mon"
        },
        "Moving": "Moving-Mon",
        "Start Movement": {
            "pvname": "KParamChange-Cmd",
            "icon": "fa5s.play"
        },
        "Abort": {
            "pvname": "Abort-Cmd",
            "icon": "fa5s.stop"
        },
        "Reset": {
            "pvname": "Reset-Cmd",
            "icon": "fa5s.sync"
        },
    }

    SCAN_CONTROL_PVS = {
        "Master": {
            "Sel": "Fly_Master_Mode",
            "Sts": "Fly_Master_Mode",
            "Mon": "Fly_Master_Mode"
        },
        "Slave": {
            "Sel": "Fly_Slave_Mode",
            "Sts": "Fly_Slave_Mode",
            "Mon": "Fly_Slave_Mode"
        },
        "Step": {
            "Sel": "Step_Mode",
            "Sts": "Step_Mode",
            "Mon": "Step_Mode"
        }
    }

    AUXILIARY_PVS = {
        "Max Speed": {
            "SP": "KParamMaxVelo-SP",
            "RB": "KParamMaxVelo-RB"
        },
        "Entrance Gap": {
            "Mon": "EntranceGap-Mon"
        },
        "Exit Gap": {
            "Mon": "ExitGap-Mon"
        },
        "State Machine": {
            "RB": "State_Machine"
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

            if title in ("Moving"):
                self._createMotion(pv_info, lay, row)
            elif title in ["KParam", "KParam Speed", "Max Speed",
                    "KParam Taper", "Center Offset", "Pitch Offset"]:
                self._createParam(pv_info, lay, row)
            elif title in ["Pitch Mode", "Center Mode"]:
                self._createModeSwitch(pv_info, lay, row)
            elif isinstance(pv_info, str):
                pvname = self.dev_pref.substitute(propty=pv_info)
                lbl = SiriusLabel(self, init_channel=pvname)
                lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                lbl.setMinimumWidth(125)
                lbl.showUnits = True
                lbl.setMaximumHeight(40)
                lay.addWidget(lbl, row, 1, 1, 2)
            else:
                self._createIconBtns(pv_info, lay, row)
            row += 1

        return group

    def _auxParametersWidget(self):
        group = QGroupBox('Auxiliary Parameters')
        lay = QGridLayout()
        group.setLayout(lay)

        for row, (title, pv_info) in enumerate(self.AUXILIARY_PVS.items()):
            label = QLabel(
                title, self, alignment=Qt.AlignRight | Qt.AlignVCenter)
            label.setFixedWidth(150)
            lay.addWidget(label, row, 0)
            self._createParam(pv_info, lay, row)
        return group

    def _scanControlsWidget(self):
        group = QGroupBox('Scan Mode Controls')
        lay = QGridLayout()
        group.setLayout(lay)

        self.scan_buttons = {}
        self.scan_mon_pvs = {}

        for row, (title, pv_info) in enumerate(self.SCAN_CONTROL_PVS.items()):
            label = QLabel(
                title, self, alignment=Qt.AlignRight | Qt.AlignVCenter)
            label.setFixedWidth(150)
            lay.addWidget(label, row, 0)
            button = self._createModeSwitchScans(pv_info, lay, row)
            self.scan_buttons[title] = button
            self.scan_mon_pvs[title] = self.dev_pref.substitute(propty=pv_info["Mon"])

        self._applyScanRules()
        return group

    def _auxCommandsWidget(self):
        widget = QWidget()
        vlay = QVBoxLayout()
        widget.setLayout(vlay)
        vlay.setContentsMargins(0, 0, 0, 0)
        vlay.addWidget(self._auxParametersWidget())
        vlay.addWidget(self._scanControlsWidget())
        return widget

    def _createModeSwitch(self, pv_info, lay, row):
        pvname = self.dev_pref.substitute(propty=pv_info["Sel"])
        pvname_mon = self.dev_pref.substitute(propty=pv_info["Mon"])
        self.mode_sp = PyDMStateButton(init_channel=pvname)
        self.mode_sp.rules = (
            '[{"name": "VisibleWarning", "property": "Enable", "expression": "ch[0] == 0",' +
            '"channels": [{"channel": "'+pvname_mon+'", "trigger": true}]}]')

        lay.addWidget(self.mode_sp, row, 1)

        pvname = self.dev_pref.substitute(propty=pv_info["Sts"])
        self.mode_rb = PyDMLed(init_channel=pvname)
        lay.addWidget(self.mode_rb, row, 2)

        warning = PyDMPushButton(label="The Offset value must be 0!")
        warning.setStyleSheet("color: #ff0000")
        warning.setFlat(True)
        warning.rules = (
            '[{"name": "VisibleWarning", "property": "Visible", "expression": "ch[0] != 0",' +
            '"channels": [{"channel": "'+pvname_mon+'", "trigger": true}]}]')
        lay.addWidget(warning, row, 3)

    def _createModeSwitchScans(self, pv_info, lay, row):
        pvname = self.dev_pref.substitute(propty=pv_info["Sel"])
        button = PyDMStateButton(init_channel=pvname)

        lay.addWidget(button, row, 1)

        pvname = self.dev_pref.substitute(propty=pv_info["Sts"])
        self.mode_rb = PyDMLed(init_channel=pvname)
        lay.addWidget(self.mode_rb, row, 2)

        return button

    def _applyScanRules(self):
        for name, button in self.scan_buttons.items():
            other_modes = [k for k in self.scan_buttons if k != name]

            channels = [
                {"channel": self.scan_mon_pvs[mode], "trigger": True}
                for mode in other_modes
            ]
            rule = [{
                "name": f"disable_{name.lower()}",
                "property": "Enable",
                "expression": "not (" + " or ".join([f"ch[{i}] == 1" for i in range(len(channels))]) + ")",
                "channels": channels
            }]

            button.rules = json.dumps(rule)

    def _ctrlModeWidget(self):
        gbox_ctrlmode = QGroupBox('Control Mode')
        lay_ctrlmode = QHBoxLayout(gbox_ctrlmode)
        lay_ctrlmode.setAlignment(Qt.AlignCenter)

        label = QLabel("Is Remote")
        lay_ctrlmode.addWidget(label, alignment=Qt.AlignRight)

        self._led_ctrlmode = PyDMLed(
            self, self.dev_pref.substitute(propty='IsRemote-Mon'))
        self._led_ctrlmode.offColor = PyDMLed.Red
        self._led_ctrlmode.onColor = PyDMLed.LightGreen
        lay_ctrlmode.addWidget(self._led_ctrlmode, alignment=Qt.AlignLeft)

        return gbox_ctrlmode

    def _statusWidget(self):
        gbox = QGroupBox('Status')
        lay = QVBoxLayout(gbox)
        lay.addStretch()

        self._pb_dtls = QPushButton(
            "Control Status Details", self)
        self._pb_dtls.setIcon(qta.icon('fa5s.list-ul'))
        connect_window(
            self._pb_dtls, IVUControlDetails, self,
            prefix=self._prefix, device=self._device)
        lay.addWidget(self._pb_dtls)

        self._pb_tilt_dtls = QPushButton(
            "Tilt Meter Details", self)
        self._pb_tilt_dtls.setIcon(qta.icon('fa5s.list-ul'))
        connect_window(
            self._pb_tilt_dtls, IVUTiltDetails, self,
            prefix=self._prefix, device=self._device)
        lay.addWidget(self._pb_tilt_dtls)

        self._pb_temp_dtls = QPushButton(
            "Temperature Status Details", self)
        self._pb_temp_dtls.setIcon(qta.icon('fa5s.temperature-high'))
        connect_window(
            self._pb_temp_dtls, IVUTempDetails, self,
            prefix=self._prefix, device=self._device)
        lay.addWidget(self._pb_temp_dtls)

        lay.addStretch()

        propty = 'System Status Monitoring'
        devsts_labels = [
            'HeartBeat',
            'IsAtMaxGap-Mon',
            'Interlocked-Mon',
            'UN_Reach',
            'Pitch_Err',
            'Status-Mon',
        ]

        dev_lay = QGridLayout()
        dev_title = QLabel(f'<h4>{propty}</h4>',
                            self, alignment=Qt.AlignCenter)
        dev_lay.addWidget(dev_title, 0, 0, 1, 2, alignment=Qt.AlignCenter)
        for idx, lbl in enumerate(devsts_labels):
            pvname = self.dev_pref.substitute(propty=lbl)
            if "Mon" in lbl:
                lbl = lbl.split('-')[0]
            if "Status" in lbl:
                lbl = "ID Status"
            sts_lbl = QLabel(lbl)
            irow = idx + 1
            read_sts = SiriusLedState(self, init_channel=pvname)
            if lbl == "HeartBeat":
                read_sts.offColor = SiriusLedState.Gray
            elif lbl == "IsAtMaxGap":
                read_sts.offColor = SiriusLedState.Yellow
            elif lbl in ["Interlocked", "Pitch_Err", "ID Status"]:
                read_sts.offColor = SiriusLedState.Red
            dev_lay.addWidget(read_sts, irow, 0)
            dev_lay.addWidget(sts_lbl, irow, 1)
        lay.addLayout(dev_lay)
        lay.addStretch()

        return gbox

    def _ffSettingsWidget(self):
        but = QPushButton('Feedforward Settings', self)
        connect_newprocess(
            but, ['sirius-hla-si-ap-idff.py', self._device])
        return but

    def _createParam(self, pv_info, lay, row):
        if "SP" in pv_info:
            pvname = self.dev_pref.substitute(propty=pv_info["SP"])
            cb = SiriusLineEdit(self, init_channel=pvname)
            lay.addWidget(cb, row, 1, 1, 1)
            lay.setContentsMargins(3, 3, 3, 3)
            col = 2
        else:
            col = 1
        for key in ["RB", "Mon"]:
            if key not in pv_info:
                continue
            pvname = self.dev_pref.substitute(propty=pv_info[key])
            lbl = SiriusLabel(self, init_channel=pvname, keep_unit=True)
            lbl.setMinimumWidth(125)
            lbl.showUnits = True
            lbl.setAlignment(Qt.AlignCenter)
            lay.addWidget(lbl, row, col, 1, 1)
            col += 1

    def _createMotion(self, pv_info, lay, row):
        pvname = self.dev_pref.substitute(propty=pv_info)
        led = PyDMLed(self, init_channel=pvname)
        led.setMaximumWidth(50)
        lay.addWidget(led, row, 1, 1, 1)

    def _createIconBtns(self, pv_info, lay, row):
        btn = PyDMPushButton(self, label='', icon=qta.icon(pv_info["icon"]))
        btn.channel = self.dev_pref.substitute(propty=pv_info["pvname"])
        btn.pressValue = 1
        btn.setIconSize(QSize(20, 20))
        btn.setMaximumWidth(25)
        btn.setStyleSheet(
            '#Start{min-width:30px; max-width:30px; icon-size:25px;}')
        lay.addWidget(btn, row, 1, 1, 4)


class IVUSummaryBase(IDCommonSummaryBase):
    """IVU Summary Base Widget."""

    MODEL_WIDTHS = (
        ('KParam', 6),
        ('KParam Speed', 6),
        ('Start', 4),
        ('Stop', 4),
    )


class IVUSummaryHeader(IDCommonSummaryHeader, IVUSummaryBase):
    """IVU Summary Header."""


class IVUSummaryWidget(IDCommonSummaryWidget, IVUSummaryBase):
    """IVU Summary Widget."""

    def _get_widgets(self, prop):
        wids, orientation = super()._get_widgets(prop)
        if prop == 'Alarms':
            led = SiriusLedAlert(
                self, self.dev_pref.substitute(propty='Alarm-Mon'))
            wids.append(led)
        if prop == 'Interlock':
            led = SiriusLedAlert(
                self, self.dev_pref.substitute(propty='Intlk-Mon'))
            wids.append(led)
        elif prop == 'KParam':
            spb = SiriusSpinbox(
                self, self.dev_pref.substitute(propty='KParam-SP'))
            wids.append(spb)
            lbl = SiriusLabel(
                self, self.dev_pref.substitute(propty='KParam-Mon'))
            wids.append(lbl)
        elif prop == 'KParam Speed':
            spb = SiriusSpinbox(
                self, self.dev_pref.substitute(propty='KParamVelo-SP'))
            wids.append(spb)
            lbl = SiriusLabel(
                self, self.dev_pref.substitute(propty='KParamVelo-RB'))
            wids.append(lbl)
        elif prop == 'Start':
            btn = PyDMPushButton(self, label='', icon=qta.icon('fa5s.play'))
            btn.channel = self.dev_pref.substitute(propty='KParamChange-Cmd')
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


class IVUControlDetails(IDCommonDialog):
    """IVU Control Details"""

    def __init__(self, parent=None, prefix='', device=''):
        """Init."""
        super().__init__(
            parent, prefix, device, title=device+' General Status Details')

    def _setupUi(self):
        gbox = QGroupBox('Status Details', self)
        glay = QGridLayout(gbox)

        ex_details = [
            "EnUp",
            "EnDn",
            "ExUp",
            "ExDn",
        ]

        details = [
            "MaxKill",
            "MinKill",
            "MaxLimit",
            "MinLimit",
            "Reach",
            "Stop",
            "Enable",
            "Gearin",
            "Gearout",
            "Reset",
            "Move",
            "Max_SoftLimit",
            "Min_SoftLimit",
        ]

        for i, ex in enumerate(ex_details):
            lin = i + 1
            ld_ex = QLabel('<h4>'+ex+'</h4>', self)
            glay.addWidget(ld_ex, lin, 0)
            for idx, title in enumerate(details):
                col = idx + 1
                lb_dtl = QLabel('<h4>'+title+'</h4>', self)
                glay.addWidget(lb_dtl, 0, col)
                pv_info = f'{ex}_{title}'
                pvname = self.dev_pref.substitute(propty=pv_info)
                ld_dtl = SiriusLedState(self, pvname)
                glay.addWidget(ld_dtl, lin, col)

        gbox.setStyleSheet(
            'QLabel{qproperty-alignment: AlignCenter; max-width: 12em;}')
        lay = QVBoxLayout(self)
        lay.addWidget(gbox)

        lay_sts = QHBoxLayout()

        gbox_pos = QGroupBox('Current Position', self)
        glay_pos = QGridLayout(gbox_pos)

        for i, ex in enumerate(ex_details):
            lbl = QLabel(ex+'_LAE')
            pv_info = f'{ex}_SSI_Encoder'
            pvname = self.dev_pref.substitute(propty=pv_info)
            pos_lbl = SiriusLabel(self, pvname)
            glay_pos.addWidget(lbl, i, 0)
            glay_pos.addWidget(pos_lbl, i, 1)

        lay_sts.addWidget(gbox_pos)

        err_sys = [
            "ExUp_Tilt",
            "ExDn_Tilt",
            "Center",
            "Center_Taper",
            "EnUp_ExUp",
            "EnDn_ExDn",
            "EnUp_EnDn",
        ]

        center_sys = [
            "Inhibit",
            "Moving",
            "Reach",
        ]

        em_stop = [
            "Local",
            "Mach1",
            "Mach2",
        ]

        tap_lim = [
            "Max",
            "Min",
        ]

        lim = [
            "MaxOffset",
            "MinOffset",
        ]

        gen_sts = [
            "BLS",
            "Status-Mon",
            "SystemOK-Mon",
        ]

        gbox_sts = QGroupBox('General Status', self)
        glay_sts = QGridLayout(gbox_sts)

        glay_sts.addWidget(QLabel('<h4>Err</h4>'), 0, 1, alignment=Qt.AlignCenter)
        glay_sts.addWidget(QLabel('<h4>Center</h4>'), 0, 3, alignment=Qt.AlignCenter)
        glay_sts.addWidget(QLabel('<h4>EMStop</h4>'), 0, 5, alignment=Qt.AlignCenter)
        glay_sts.addWidget(QLabel('<h4>Taper Limit</h4>'), 0, 7, alignment=Qt.AlignCenter)
        glay_sts.addWidget(QLabel('<h4>Limit</h4>'), 0, 9, alignment=Qt.AlignCenter)

        for idx, sts in enumerate(err_sys):
            lin = idx + 1
            lbl = QLabel(sts)
            pv_info = f'{sts}_Err'
            pvname = self.dev_pref.substitute(propty=pv_info)
            ld_gen = SiriusLedState(self, pvname)
            glay_sts.addWidget(lbl, lin, 0)
            glay_sts.addWidget(ld_gen, lin, 1, alignment=Qt.AlignCenter)

        for idx, sts in enumerate(center_sys):
            lin = idx + 1
            lbl = QLabel(sts)
            pv_info = f'Center_{sts}'
            pvname = self.dev_pref.substitute(propty=pv_info)
            ld_gen = SiriusLedState(self, pvname)
            glay_sts.addWidget(lbl, lin, 2, alignment=Qt.AlignCenter)
            glay_sts.addWidget(ld_gen, lin, 3, alignment=Qt.AlignCenter)

        for idx, sts in enumerate(em_stop):
            lin = idx + 1
            lbl = QLabel(sts)
            pv_info = f'{sts}_EMStop'
            pvname = self.dev_pref.substitute(propty=pv_info)
            ld_gen = SiriusLedState(self, pvname)
            glay_sts.addWidget(lbl, lin, 4, alignment=Qt.AlignCenter)
            glay_sts.addWidget(ld_gen, lin, 5, alignment=Qt.AlignCenter)

        for idx, sts in enumerate(tap_lim):
            lin = idx + 1
            lbl = QLabel(sts)
            pv_info = f'{sts}_TaperLimit'
            pvname = self.dev_pref.substitute(propty=pv_info)
            ld_gen = SiriusLedState(self, pvname)
            glay_sts.addWidget(lbl, lin, 6, alignment=Qt.AlignCenter)
            glay_sts.addWidget(ld_gen, lin, 7, alignment=Qt.AlignCenter)

        for idx, sts in enumerate(lim):
            lin = idx + 1
            lbl = QLabel(sts)
            pv_info = f'{sts}_Limit'
            pvname = self.dev_pref.substitute(propty=pv_info)
            ld_gen = SiriusLedState(self, pvname)
            glay_sts.addWidget(lbl, lin, 8, alignment=Qt.AlignCenter)
            glay_sts.addWidget(ld_gen, lin, 9, alignment=Qt.AlignCenter)

        for idx, sts in enumerate(gen_sts):
            lin = idx + 1
            lbl = QLabel(sts)
            pv_info = f'{sts}'
            pvname = self.dev_pref.substitute(propty=pv_info)
            ld_gen = SiriusLedState(self, pvname)
            glay_sts.addWidget(lbl, lin, 10, alignment=Qt.AlignCenter)
            glay_sts.addWidget(ld_gen, lin, 11, alignment=Qt.AlignCenter)

        lay_sts.addWidget(gbox_sts)

        gbox_ctrl = QGroupBox('Control', self)
        glay_ctrl = QGridLayout(gbox_ctrl)

        pv_info = "Kill_Disable"
        pvname = self.dev_pref.substitute(propty=pv_info)

        kill_lbl = QLabel("Kill Disable")
        kill_btn = PyDMStateButton(init_channel=pvname)
        ld_kill = PyDMLed(init_channel=pvname)

        glay_ctrl.addWidget(kill_lbl, 0, 0)
        glay_ctrl.addWidget(kill_btn, 0, 1)
        glay_ctrl.addWidget(ld_kill, 0, 2)

        lay_sts.addWidget(gbox_ctrl)

        lay.addLayout(lay_sts)


class IVUTempDetails(IDCommonDialog):
    """IVU Temperature Control Details"""

    def __init__(self, parent=None, prefix='', device=''):
        """Init."""
        super().__init__(
            parent, prefix, device, title=device+' Temperature Status Details')

    def _setupUi(self):
        gbox = QGroupBox('System Status', self)
        glay = QGridLayout(gbox)

        up_dn_gird = [
            "UpGird1",
            "UpGird2",
            "UpGird3",
            "UpGird4",
            "UpGird5",
            "UpGird6",
            "UpGird7",
            "UpGird8",
            "DnGird1",
            "DnGird2",
            "DnGird3",
            "DnGird4",
            "DnGird5",
            "DnGird6",
            "DnGird7",
            "DnGird8",
        ]

        glay.addWidget(QLabel('<h4>Overrage</h4>'), 1, 0)

        for idx, gird in enumerate(up_dn_gird):
            col = idx + 1
            title_gird = QLabel("<h4>"+gird+"</h4>")
            pv_info = f"{gird}_Overrage"
            pvname = self.dev_pref.substitute(propty=pv_info)
            ld_gird = SiriusLedState(self, pvname)
            glay.addWidget(title_gird, 0, col, alignment=Qt.AlignCenter)
            glay.addWidget(ld_gird, 1, col, alignment=Qt.AlignCenter)

        gbox.setStyleSheet(
            'QLabel{qproperty-alignment: AlignCenter; max-width: 12em;}')
        lay = QVBoxLayout(self)

        glay.addWidget(QLabel('<h4>Water Flow Interlock</h4>'), 3, 0)

        for i in range(6):
            col = i + 1
            title_intlk = QLabel(f"<h4>Intlk {i+1}</h4>")
            pv_info = f"WF_Interlock{i+1}"
            pvname = self.dev_pref.substitute(propty=pv_info)
            ld_intlk = SiriusLedState(self, pvname)
            glay.addWidget(title_intlk, 2, col, alignment=Qt.AlignCenter)
            glay.addWidget(ld_intlk, 3, col, alignment=Qt.AlignCenter)

        lay.addWidget(gbox)

        gbox_pos = QGroupBox('Current Position', self)
        glay_pos = QGridLayout(gbox_pos)

        glay_pos.addWidget(QLabel("<h4>RTD</h4>"), 1, 0, alignment=Qt.AlignRight)
        glay_pos.addWidget(QLabel("<h4>RTD</h4>"), 3, 0, alignment=Qt.AlignRight)

        for i in range(8):
            col = i + 1
            title = QLabel(f"<h4>Upgird{i+1}</h4>")
            pv_info = f"RTD_Upgird{i+1}"
            pvname = self.dev_pref.substitute(propty=pv_info)
            lbl_pos = SiriusLabel(self, pvname)
            lbl_pos.showUnits = True
            glay_pos.addWidget(title, 0, col, alignment=Qt.AlignCenter)
            glay_pos.addWidget(lbl_pos, 1, col, alignment=Qt.AlignCenter)

        for i in range(8):
            col = i + 1
            title = QLabel(f"<h4>Dngird{i+1}</h4>")
            pv_info = f"RTD_Dngird{i+1}"
            pvname = self.dev_pref.substitute(propty=pv_info)
            lbl_pos = SiriusLabel(self, pvname)
            lbl_pos.showUnits = True
            glay_pos.addWidget(title, 2, col, alignment=Qt.AlignCenter)
            glay_pos.addWidget(lbl_pos, 3, col, alignment=Qt.AlignCenter)

        lay.addWidget(gbox_pos)

        gbox_set = QGroupBox('Settings', self)
        glay_set = QGridLayout(gbox_set)

        glay_set.addWidget(QLabel("<h4>Alarm</h4>"), 1, 0, alignment=Qt.AlignRight)
        glay_set.addWidget(QLabel("<h4>Alarm</h4>"), 3, 0, alignment=Qt.AlignRight)

        for i in range(8):
            col = i + 1
            title = QLabel(f"<h4>UpGird{i+1}</h4>")
            pv_info = f"UpGird{i+1}_Alarm"
            pvname = self.dev_pref.substitute(propty=pv_info)
            lbl_set = SiriusLineEdit(self, pvname)
            glay_set.addWidget(title, 0, col, alignment=Qt.AlignCenter)
            glay_set.addWidget(lbl_set, 1, col, alignment=Qt.AlignCenter)

        for i in range(8):
            col = i + 1
            title = QLabel(f"<h4>DnGird{i+1}</h4>")
            pv_info = f"DnGird{i+1}_Alarm"
            pvname = self.dev_pref.substitute(propty=pv_info)
            lbl_set = SiriusLineEdit(self, pvname)
            glay_set.addWidget(title, 2, col, alignment=Qt.AlignCenter)
            glay_set.addWidget(lbl_set, 3, col, alignment=Qt.AlignCenter)

        lay.addWidget(gbox_set)


class IVUTiltDetails(IDCommonDialog):
    """IVU Tilt Meter Control Details"""

    def __init__(self, parent=None, prefix='', device=''):
        """Init."""
        super().__init__(
            parent, prefix, device, title=device+' Tilt Meter Status Details')

    def _setupUi(self):
        ex_list = ["ExUp_Tilt_Meter",
                   "ExDn_Tilt_Meter",
                   "ExUp_Tilt_MeterR",
                   "ExDn_Tilt_MeterR",
                ]

        gbox = QGroupBox('Current Position', self)
        glay = QGridLayout(gbox)

        for idx, ex in enumerate(ex_list):
            title_ex = QLabel("<h4>"+ex+"</h4>")
            pvname = self.dev_pref.substitute(propty=ex)
            lbl_ex = SiriusLabel(self, pvname)
            glay.addWidget(title_ex, 0, idx, alignment=Qt.AlignCenter)
            glay.addWidget(lbl_ex, 1, idx, alignment=Qt.AlignCenter)

        gbox.setStyleSheet(
            'QLabel{qproperty-alignment: AlignCenter; max-width: 12em;}')

        lay = QVBoxLayout(self)

        lay.addWidget(gbox)

        gbox_set = QGroupBox('Setting')
        glay_set = QGridLayout(gbox_set)
        lay_h = QHBoxLayout()

        glay_set.addWidget(QLabel("<h4>Offset UpTilt</h4>"), 0, 0, alignment=Qt.AlignCenter)
        glay_set.addWidget(QLabel("<h4>Offset DnTilt</h4>"), 1, 0, alignment=Qt.AlignCenter)

        pv_up = self.dev_pref.substitute(propty="OFFSET_UPTILT")
        uptilt = SiriusLabel(self, pv_up)
        glay_set.addWidget(uptilt, 0, 1, alignment=Qt.AlignCenter)

        pv_dn = self.dev_pref.substitute(propty="OFFSET_DNTILT")
        dntilt = SiriusLabel(self, pv_dn)
        glay_set.addWidget(dntilt, 1, 1, alignment=Qt.AlignCenter)

        lay_h.addWidget(gbox_set)

        gbox_ctrl = QGroupBox('Control')
        glay_ctrl = QGridLayout(gbox_ctrl)
        lay_h = QHBoxLayout()

        glay_ctrl.addWidget(QLabel("<h4>BYPASS UpTilt</h4>"), 0, 0, alignment=Qt.AlignCenter)
        glay_ctrl.addWidget(QLabel("<h4>BYPASS DnTilt</h4>"), 1, 0, alignment=Qt.AlignCenter)

        pv_info_up = self.dev_pref.substitute(propty="BYPASS_UPTILT")
        uptilt = PyDMStateButton(self, pv_info_up)
        ld_uptilt = PyDMLed(init_channel=pv_info_up)
        glay_ctrl.addWidget(uptilt, 0, 1, alignment=Qt.AlignCenter)
        glay_ctrl.addWidget(ld_uptilt, 0, 2, alignment=Qt.AlignCenter)

        pv_info_dn = self.dev_pref.substitute(propty="BYPASS_DNTILT")
        dntilt = PyDMStateButton(init_channel=pv_info_dn)
        ld_dntilt = PyDMLed(init_channel=pv_info_dn)
        glay_ctrl.addWidget(dntilt, 1, 1, alignment=Qt.AlignCenter)
        glay_ctrl.addWidget(ld_dntilt, 1, 2, alignment=Qt.AlignCenter)

        lay_h.addWidget(gbox_set)
        lay_h.addWidget(gbox_ctrl)

        lay.addLayout(lay_h)
