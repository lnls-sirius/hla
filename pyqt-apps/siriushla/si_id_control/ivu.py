"""IVU Control Module."""

from qtpy.QtCore import Qt, QSize
from qtpy.QtWidgets import QGroupBox, QLabel, \
    QHBoxLayout, QPushButton, \
    QGridLayout
import qtawesome as qta
from pydm.widgets import PyDMPushButton

from siriuspy.epics import PV

from ..util import connect_newprocess, connect_window
from ..widgets import SiriusLedAlert, SiriusLabel, SiriusSpinbox, \
    PyDMLed, PyDMStateButton, SiriusLineEdit
from ..widgets.dialog import StatusDetailDialog

from .base import IDCommonControlWindow, \
    IDCommonSummaryBase, IDCommonSummaryHeader, IDCommonSummaryWidget


class IVUControlWindowUtils():
    """."""

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
        }
    }


class IVUControlWindow(IDCommonControlWindow, IVUControlWindowUtils):
    """IVU Control Window."""

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

            if title in ("Moving"):
                self._createMotion(pv_info, lay, row)
            elif title in ["KParam", "KParam Speed", 
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
