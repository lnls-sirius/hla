"""DELTA Control Module."""

from qtpy.QtCore import Qt, QSize
from qtpy.QtWidgets import QGroupBox, QLabel, \
    QHBoxLayout, QVBoxLayout, QWidget, QPushButton, \
    QGridLayout, QSizePolicy as QSzPlcy
import qtawesome as qta
from pydm.widgets import PyDMPushButton

from siriuspy.epics import PV

from ..util import connect_newprocess, connect_window
from ..widgets import SiriusLedAlert, SiriusLabel, SiriusSpinbox, \
    PyDMLogLabel, PyDMLed, SiriusEnumComboBox, SiriusLineEdit
from ..widgets.dialog import StatusDetailDialog

from .base import IDCommonControlWindow, \
    IDCommonSummaryBase, IDCommonSummaryHeader, IDCommonSummaryWidget


class DELTAControlWindowUtils():
    """."""

    STATUS_PVS = {
        "Alarms": (
            "Alarm-Mon", "AlarmBits-Mon", "AlarmLabels-Cte"
        ),
        "Interlock": (
            "Intlk-Mon", "IntlkBits-Mon", "IntlkLabels-Cte"
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
        "KParam": {
            "SP": "KParam-SP",
            "RB": "KParam-RB",
            "Mon": "KParam-Mon"
        },
        "KParam Speed": {
            "SP": "KParamVelo-SP",
            "RB": "KParamVelo-RB",
        },
        "Change KParam": {
            "pvname": "KParamChange-Cmd",
            "icon": "fa5s.play"
        },
        "PParam": {
            "SP": "PParam-SP",
            "RB": "PParam-RB",
            "Mon": "PParam-Mon"
        },
        "PParam Speed": {
            "SP": "PParamVelo-SP",
            "RB": "PParamVelo-RB",
        },
        "Change PParam": {
            "pvname": "PParamChange-Cmd",
            "icon": "fa5s.play"
        },
        "Polarization": {
            "SP": "Pol-Sel",
            "RB": "Pol-Sts",
            "Mon": "Pol-Mon"
        },
        "Change Polarization": {
            "pvname": "PolChange-Cmd",
            "icon": "fa5s.play"
        },
        "Moving": "Moving-Mon",
        "Motors Enabled": "MotorsEnbld-Mon",
        "Abort": {
            "pvname": "Abort-Cmd",
            "icon": "fa5s.stop"
        }
    }

    AUX_CONTROL_PVS = {
        "Max. Speed": {
            "SP": "MaxVelo-SP",
            "RB": "MaxVelo-RB",
        },
        "Max. Acc.": {
            "SP": "MaxAcc-SP",
            "RB": "MaxAcc-RB",
        },
        "Header": (
            "KParam", "PParam"
        ),
        "Acceleration": (
            "KParamAcc-SP", "KParamAcc-RB",
            "PParamAcc-SP", "PParamAcc-RB"
        ),
        "Tolerance": (
            "PosTol-SP", "PosTol-RB",
            "PolTol-SP", "PolTol-RB"
        ),
        "Start Parking": {
            "pvname": "StartParking-Cmd",
            "icon": "fa5s.parking"
        }
    }


class DELTAControlWindow(IDCommonControlWindow, DELTAControlWindowUtils):
    """DELTA Control Window."""

    def _mainControlsWidget(self):
        group = QGroupBox('Main Controls')
        lay = QGridLayout()
        group.setLayout(lay)

        row = 0
        for title, pv_info in self.MAIN_CONTROL_PVS.items():
            label = QLabel(
                title, self, alignment=Qt.AlignRight | Qt.AlignVCenter)
            label.setFixedWidth(150)
            lay.addWidget(label, row, 0)

            if title in ("Moving", "Motors Enabled"):
                self._createMotion(pv_info, lay, row)
            elif title in ["KParam", "PParam", "KParam Speed", "PParam Speed"]:
                self._createParam(pv_info, lay, row)
            elif title == "Polarization":
                self._createPolarization(pv_info, lay, row)
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

    def _statusWidget(self):
        return self._createStatusGroup("Status", self.STATUS_PVS)

    def _auxCommandsWidget(self):
        group = QGroupBox('Auxiliary Controls')
        lay = QGridLayout()
        group.setLayout(lay)

        row = 0
        for title, pv_info in self.AUX_CONTROL_PVS.items():
            if "Header" not in title:
                label = QLabel(
                    title, self, alignment=Qt.AlignRight | Qt.AlignVCenter)
                lay.addWidget(label, row, 0)

            if title in ["Max. Speed", "Max. Acc."]:
                self._createParam(pv_info, lay, row)
            elif title in ["Abort", "Start Parking"]:
                self._createIconBtns(pv_info, lay, row)
            elif "Header" in title:
                self._createHeaders(pv_info, lay, row)
            else:
                self._createAccTol(pv_info, lay, row)
            row += 1

        return group

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

    def _ffSettingsWidget(self):
        but = QPushButton('Feedforward Settings', self)
        connect_newprocess(
            but, ['sirius-hla-si-ap-idff.py', self._device])
        return but

    # --- auxiliary methods ---

    def _createParam(self, pv_info, lay, row):
        pvname = self.dev_pref.substitute(propty=pv_info["SP"])
        cb = SiriusLineEdit(self, init_channel=pvname)
        lay.addWidget(cb, row, 1, 1, 1)
        lay.setContentsMargins(3, 3, 3, 3)

        col = 2
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

    def _createPolarization(self, pv_info, lay, row):

        pvname = self.dev_pref.substitute(propty=pv_info["SP"])
        cb = SiriusEnumComboBox(self, init_channel=pvname)
        cb.setMinimumWidth(50)
        lay.addWidget(cb, row, 1, 1, 1)
        lay.setContentsMargins(0, 0, 0, 0)

        col = 2
        for key in ["RB", "Mon"]:
            pvname = self.dev_pref.substitute(propty=pv_info[key])
            lbl = SiriusLabel(self, init_channel=pvname)
            lbl.setMinimumWidth(125)
            lbl.showUnits = True
            lbl.setAlignment(Qt.AlignCenter)
            lay.addWidget(lbl, row, col, 1, 1)
            col += 1

    def _createDetailedLedBtn(self, pv_tuple):

        btn = QPushButton('', self)
        btn.setIcon(qta.icon('fa5s.list-ul'))
        btn.setObjectName('sts')
        btn.setStyleSheet(
            '#sts{min-width:25px; max-width:25px; icon-size:20px;}')
        pvname = self.dev_pref.substitute(propty=pv_tuple[0])
        pvname_labels = self.dev_pref.substitute(propty=pv_tuple[1])

        try:
            pv = PV(pvname_labels)
            pv.wait_for_connection(timeout=5)
            labels = pv.get()
            connect_window(
                btn, StatusDetailDialog, self, pvname=pvname,
                labels=list(labels), section="ID")
        except:
            btn.setEnabled(False)
        return btn

    def _createStatusWidget(self, title, pv_suffix):
        pv_tuple = tuple()
        wid = QWidget()
        lay = QHBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        wid.setLayout(lay)

        label = QLabel(title, self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        lay.addWidget(label)

        if isinstance(pv_suffix, tuple):
            pv_tuple = (pv_suffix[1], pv_suffix[2])
            pv_suffix = pv_suffix[0]

        pvname = self.dev_pref.substitute(propty=pv_suffix)
        if 'PLC State' in title:
            led = SiriusLabel(self, pvname)
        else:
            led = SiriusLedAlert(init_channel=pvname)
        lay.addWidget(led, alignment=Qt.AlignLeft)

        if pv_tuple:
            detailed_btn = self._createDetailedLedBtn(pv_tuple)
            lay.addWidget(detailed_btn, alignment=Qt.AlignLeft)

        return wid

    def _createLogWidget(self, title, pv_suffix):
        wid = QWidget()
        lay = QVBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        wid.setLayout(lay)

        label = QLabel(title, self)
        lay.addWidget(label)

        pvname = self.dev_pref.substitute(propty=pv_suffix)
        log = PyDMLogLabel(init_channel=pvname)
        lay.addWidget(log)

        return wid

    def _createStatusGroup(self, title, pvs):
        group = QGroupBox()
        lay = QVBoxLayout()
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
            lbl = QLabel(header_lbl, self, alignment=Qt.AlignCenter)
            lbl.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Maximum)
            lay.addWidget(lbl, row, col, 1, 2)
            col += 2

    def _createAccTol(self, pv_info, lay, row):
        col = 1
        for enum in range(0, 2):
            pvname = self.dev_pref.substitute(propty=pv_info[enum*2])
            edit = SiriusLineEdit(self, init_channel=pvname)
            lay.addWidget(edit, row, col, 1, 1)

            pvname = self.dev_pref.substitute(propty=pv_info[(enum*2)+1])
            lbl = SiriusLabel(self, init_channel=pvname, keep_unit=True)
            lbl.showUnits = True
            lbl.setAlignment(Qt.AlignCenter)
            lay.addWidget(lbl, row, col+1, 1, 1)
            col += 2


class DELTASummaryBase(IDCommonSummaryBase):
    """DELTA Summary Base Widget."""

    MODEL_WIDTHS = (
        ('Alarms', 4),
        ('Interlock', 4),
        ('KParam', 6),
        ('KParam Speed', 6),
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
