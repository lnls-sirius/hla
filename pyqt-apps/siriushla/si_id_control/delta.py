"""DELTA Control Module."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGroupBox, QLabel, \
    QHBoxLayout, QVBoxLayout, QWidget, QPushButton
import qtawesome as qta
from pydm.widgets import PyDMPushButton

from ..util import connect_newprocess, connect_window
from ..widgets import SiriusLedAlert, SiriusLabel, SiriusSpinbox, \
    PyDMLogLabel, PyDMLed
from ..widgets.dialog import StatusDetailDialog

from .base import IDCommonControlWindow, IDCommonDialog, \
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
        "Motors Enabled": "MotorsEnbld-Mon",
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


class DELTAControlWindow(IDCommonControlWindow, DELTAControlWindowUtils):
    """DELTA Control Window."""

    def _mainControlsWidget(self):
        return QLabel("jf")

    def _createDetailedLedBtn(self, pv_tuple):

        btn = QPushButton('', self)
        btn.setIcon(qta.icon('fa5s.list-ul'))
        btn.setObjectName('sts')
        btn.setStyleSheet(
            '#sts{min-width:25px; max-width:25px; icon-size:20px;}')
        pvname = self.dev_pref.substitute(propty=pv_tuple[1])
        pvname_labels = self.dev_pref.substitute(propty=pv_tuple[2])
        connect_window(
            btn, StatusDetailDialog, self, pvname=pvname, pv_labels=pvname_labels)
        return btn

    def _createStatusWidget(self, title, pv_suffix):
        wid = QWidget()
        wid.setContentsMargins(0, 0, 0, 0)
        lay = QHBoxLayout()
        wid.setLayout(lay)

        label = QLabel(title)
        label.setFixedWidth(100)
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

    def _auxCommandsWidget(self):
        return QLabel("123")

    def _ctrlModeWidget(self):
        self._led_ctrlmode = PyDMLed(
            self, self.dev_pref.substitute(propty='IsRemote-Mon'))
        self._led_ctrlmode.offColor = PyDMLed.Red
        self._led_ctrlmode.onColor = PyDMLed.LightGreen

        gbox_ctrlmode = QGroupBox('Control Mode')
        lay_ctrlmode = QHBoxLayout(gbox_ctrlmode)
        lay_ctrlmode.setAlignment(Qt.AlignCenter)
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
