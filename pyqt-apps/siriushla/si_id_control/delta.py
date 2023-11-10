"""DELTA Control Module."""

from qtpy.QtCore import Qt, QSize
from qtpy.QtWidgets import QGroupBox, QLabel, \
    QHBoxLayout, QVBoxLayout, QWidget, QPushButton, \
    QGridLayout
import qtawesome as qta
from epics import caget
from pydm.widgets import PyDMPushButton

from ..util import connect_window
from ..widgets import SiriusLedAlert, SiriusLabel, SiriusSpinbox, \
    PyDMLogLabel, PyDMLed, SiriusEnumComboBox, SiriusLineEdit, SiriusConnectionSignal
from ..widgets.dialog import StatusDetailDialog

from .base import IDCommonControlWindow, \
    IDCommonSummaryBase, IDCommonSummaryHeader, IDCommonSummaryWidget


class DELTAControlWindowUtils():

    STATUS_PVS = {
        "Alarms": (
            "Alarm-Mon", "AlarmBits-Mon", "AlarmLabels-Mon"
        ),
        "Interlock": (
            "Intlk-Mon", "IntlkBits-Mon", "IntlkLabels-Mon"
        ),
        "Is Operational": "IsOperational-Mon",
        "PLC State": "PLCState-Mon",
        "Sw": {
            "Killed": "KillSw-Mon",
            "Limit": "LimSw-Mon"
        },
        "Logs": {
            "IOC Log": "Log-Mon",
            "Sequencer State Machine Log": "StateMachineLog-Mon"
        }
    }

    MAIN_CONTROL_PVS = {
        "Shift": {
            "SP": "Shift-SP",
            "SP_RB": "Shift-RB",
            "RB": "GainShift-Mon"
        },
        "Start Shift": {
            "pvname": "ChangeGain-Cmd",
            "icon": "fa5s.play"
        },
        "Polarization": {
            "SP": "Pol-Sel",
            "SP_RB": "Pol-Sts",
            "RB": "Pol-Mon"
        },
        "Start Polarization": {
            "pvname": "ChangePol-Cmd",
            "icon": "fa5s.play"
        },
        "Polarization Shift": "PolShift-Mon",
        "Motion": {
            "SP_RB": "MotorsEnbld-Mon",
            "RB": "Moving-Mon"
        },
        "Abort": {
            "pvname": "Abort-Cmd",
            "icon": "fa5s.stop"
        }
    }

    AUX_CONTROL_PVS = {
        "HeaderVelAcc": (
            "Velocity", "Acceleration"
        ),
        "Polarization Mode": (
            "PolModeVelo-RB", "PolModeVelo-SP",
            "PolModeAcc-RB", "PolModeAcc-SP"
        ),
        "Gain Mode": (
            "GainModeVelo-RB", "GainModeVelo-SP",
            "GainModeAcc-RB", "GainModeAcc-SP"
        ),
        "Maximum": (
            "MaxVelo-RB", "MaxVelo-SP",
            "MaxAcc-RB", "MaxAcc-SP"
        ),
        "HeaderTol": (
            "Position", "Position for Polarization"
        ),
        "Tolerance": (
            "PosTolerance-RB", "PosTolerance-SP",
            "PolPosTolerance-RB", "PolPosTolerance-SP"
        ),
        "Start Parking": {
            "pvname": "StartParking-Cmd",
            "icon": "ri.parking-box-fill"
        }
    }


class DELTAControlWindow(IDCommonControlWindow, DELTAControlWindowUtils):
    """DELTA Control Window."""

    def _createShift(self, pv_info, lay, row):
        pvname = self.dev_pref.substitute(propty=pv_info["SP"])
        cb = SiriusLineEdit(self, init_channel=pvname)
        lay.addWidget(cb, row, 1, 1, 1)

        col = 2
        for key in ["SP_RB", "RB"]:
            pvname = self.dev_pref.substitute(propty=pv_info[key])
            lbl = SiriusLabel(self, init_channel=pvname)
            lbl.setMinimumWidth(125)
            lbl.showUnits = True
            lbl.setAlignment(Qt.AlignCenter)
            lay.addWidget(lbl, row, col, 1, 1)
            col += 1


    def _createMotion(self, pv_info, lay, row):
        motion_lay = QHBoxLayout()
        pvname = self.dev_pref.substitute(propty=pv_info["SP_RB"])
        led = PyDMLed(self, init_channel=pvname)
        led.setMaximumWidth(50)
        motion_lay.addWidget(led)

        pvname = self.dev_pref.substitute(propty=pv_info["RB"])
        led = PyDMLed(self, init_channel=pvname)
        led.setMaximumWidth(50)
        motion_lay.addWidget(led)

        lay.addLayout(motion_lay, row, 1, 1, 1)

    def _createPolarization(self, pv_info, lay, row):

        pvname = self.dev_pref.substitute(propty=pv_info["SP"])
        cb = SiriusEnumComboBox(self, init_channel=pvname)
        cb.setMinimumWidth(50)
        lay.addWidget(cb, row, 1, 1, 1)

        col = 2
        for key in ["SP_RB", "RB"]:
            pvname = self.dev_pref.substitute(propty=pv_info[key])
            lbl = SiriusLabel(self, init_channel=pvname)
            lbl.setMinimumWidth(125)
            lbl.showUnits = True
            lbl.setAlignment(Qt.AlignCenter)
            lay.addWidget(lbl, row, col, 1, 1)
            col += 1

    def _mainControlsWidget(self):
        group = QGroupBox('Main Controls')
        group.setContentsMargins(2, 2, 2, 2)
        lay = QGridLayout()
        lay.setSpacing(2)
        group.setLayout(lay)

        row = 0
        for title, pv_info in self.MAIN_CONTROL_PVS.items():
            label = QLabel(title)
            label.setFixedWidth(150)
            lay.addWidget(label, row, 0, 1, 1)

            if title == "Motion":
                self._createMotion(pv_info, lay, row)
            elif title == "Shift":
                self._createShift(pv_info, lay, row)
            elif title == "Polarization":
                self._createPolarization(pv_info, lay, row)
            elif isinstance(pv_info, str):
                pvname = self.dev_pref.substitute(propty=pv_info)
                lbl = SiriusLabel(self, init_channel=pvname)
                lbl.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
                lbl.setMinimumWidth(125)
                lbl.showUnits = True
                lbl.setMaximumHeight(40)
                lay.addWidget(lbl, row, 1, 1, 2)
            else:
                self._createIconBtns(pv_info, lay, row)
            row += 1

        return group

    def _createDetailedLedBtn(self, pv_tuple):

        btn = QPushButton('', self)
        btn.setIcon(qta.icon('fa5s.list-ul'))
        btn.setObjectName('sts')
        btn.setStyleSheet(
            '#sts{min-width:25px; max-width:25px; icon-size:20px;}')
        pvname = self.dev_pref.substitute(propty=pv_tuple[1])
        pvname_labels = self.dev_pref.substitute(propty=pv_tuple[2])

        try:
            labels = caget(pvname_labels)
            connect_window(
                btn, StatusDetailDialog, self, pvname=pvname, labels=list(labels),
                section="ID")
        except:
            btn.setEnabled(False)
        return btn

    def _createStatusWidget(self, title, pv_suffix):
        wid = QWidget()
        wid.setContentsMargins(0, 0, 0, 0)
        lay = QHBoxLayout()
        wid.setLayout(lay)

        label = QLabel(title)
        label.setFixedWidth(150)
        lay.addWidget(label)

        if isinstance(pv_suffix, tuple):
            detailed_btn = self._createDetailedLedBtn(pv_suffix)
            lay.addWidget(detailed_btn)
            pv_suffix = pv_suffix[0]

        pvname = self.dev_pref.substitute(propty=pv_suffix)
        led = SiriusLedAlert(init_channel=pvname)
        led.setFixedWidth(100)
        lay.addWidget(led)

        return wid

    def _createLogWidget(self, title, pv_suffix):
        wid = QWidget()
        wid.setContentsMargins(0, 0, 0, 0)
        lay = QVBoxLayout()
        lay.setSpacing(0)
        wid.setLayout(lay)

        label = QLabel(title)
        label.setFixedWidth(100)
        lay.addWidget(label)

        pvname = self.dev_pref.substitute(propty=pv_suffix)
        log = PyDMLogLabel(init_channel=pvname)
        lay.addWidget(log)

        return wid

    def _createStatusGroup(self, title, pvs):
        group = QGroupBox()
        group.setContentsMargins(2, 2, 2, 2)
        lay = QVBoxLayout()
        lay.setSpacing(2)
        group.setLayout(lay)
        group.setTitle(title)

        pos = [0, 0]
        for title, pv_info in pvs.items():
            if isinstance(pv_info, dict):
                widget = self._createStatusGroup(title, pv_info)
            else:
                if "Log" in title:
                    widget = self._createLogWidget(title, pv_info)
                else:
                    widget = self._createStatusWidget(title, pv_info)
            lay.addWidget(widget)
            pos[1] += 1

        return group

    def _statusWidget(self):
        return self._createStatusGroup("Status", self.STATUS_PVS)

    def _createIconBtns(self, pv_info, lay, row):
        btn = PyDMPushButton(self, label='', icon=qta.icon(pv_info["icon"]))
        btn.channel = self.dev_pref.substitute(propty=pv_info["pvname"])
        btn.pressValue = 1
        btn.setIconSize(QSize(20, 20))
        btn.setMaximumWidth(25)
        btn.setStyleSheet(
            '#Start{min-width:30px; max-width:30px; icon-size:25px;}')
        lay.addWidget(btn, row, 1, 1, 4)

    def _createHeaders(self, pv_info, lay, row):
        col = 1
        for header_lbl in pv_info:
            lbl = QLabel(header_lbl)
            lbl.setMaximumHeight(30)
            lbl.setAlignment(Qt.AlignCenter)
            lay.addWidget(lbl, row, col, 1, 2)
            col += 2

    def _createVelAcc(self, pv_info, lay, row):
        col = 1
        for enum in range(0, 2):
            pvname = self.dev_pref.substitute(propty=pv_info[enum*2])
            edit = SiriusLineEdit(self, init_channel=pvname)
            lay.addWidget(edit, row, col, 1, 1)

            pvname = self.dev_pref.substitute(propty=pv_info[(enum*2)+1])
            lbl = SiriusLabel(self, init_channel=pvname)
            lbl.setMinimumWidth(125)
            lbl.showUnits = True
            lbl.setAlignment(Qt.AlignCenter)
            lay.addWidget(lbl, row, col+1, 1, 1)
            col += 2

    def _auxCommandsWidget(self):
        group = QGroupBox('Auxiliary Controls')
        lay = QGridLayout()
        lay.setSpacing(2)
        group.setLayout(lay)

        row = 0
        for title, pv_info in self.AUX_CONTROL_PVS.items():
            if "Header" not in title:
                label = QLabel(title)
                label.setFixedWidth(150)
                lay.addWidget(label, row, 0, 1, 1)

            if title in ["Abort", "Start Parking"]:
                self._createIconBtns(pv_info, lay, row)
            elif "Header" in title:
                self._createHeaders(pv_info, lay, row)
            else:
                self._createVelAcc(pv_info, lay, row)
                row += 1
            row += 1

        return group

    def _ctrlModeWidget(self):
        gbox_ctrlmode = QGroupBox('Control Mode')
        lay_ctrlmode = QHBoxLayout(gbox_ctrlmode)
        lay_ctrlmode.setAlignment(Qt.AlignCenter)

        label = QLabel("Is Remote")
        label.setFixedWidth(100)
        lay_ctrlmode.addWidget(label)

        self._led_ctrlmode = PyDMLed(
            self, self.dev_pref.substitute(propty='IsRemote-Mon'))
        self._led_ctrlmode.offColor = PyDMLed.Red
        self._led_ctrlmode.onColor = PyDMLed.LightGreen
        lay_ctrlmode.addWidget(self._led_ctrlmode)

        return gbox_ctrlmode


class DELTASummaryBase(IDCommonSummaryBase):
    """DELTA Summary Base Widget."""

    MODEL_WIDTHS = (
        ('Alarms', 4),
        ('Interlock', 4),
        ('Shift', 6),
        ('Shift Speed', 6),
        ('Start', 4),
        ('Stop', 4),
    )


class DELTASummaryHeader(IDCommonSummaryHeader, DELTASummaryBase):
    """DELTA Summary Header."""


class DELTASummaryWidget(IDCommonSummaryWidget, DELTASummaryBase):
    """DELTA Summary Widget."""

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
        elif prop == 'Shift':
            spb = SiriusSpinbox(
                self, self.dev_pref.substitute(propty='Shift-SP'))
            wids.append(spb)
            lbl = SiriusLabel(
                self, self.dev_pref.substitute(propty='Shift-Mon'))
            wids.append(lbl)
        elif prop == 'Shift Speed':
            spb = SiriusSpinbox(
                self, self.dev_pref.substitute(propty='GainModeVelo-SP'))
            wids.append(spb)
            lbl = SiriusLabel(
                self, self.dev_pref.substitute(propty='GainModeVelo-Mon'))
            wids.append(lbl)
        elif prop == 'Start':
            btn = PyDMPushButton(self, label='', icon=qta.icon('fa5s.play'))
            btn.channel = self.dev_pref.substitute(propty='ChangeGain-Cmd')
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
