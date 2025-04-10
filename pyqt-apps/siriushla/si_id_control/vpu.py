"""VPU Control Module."""

from qtpy.QtCore import Qt, QSize
from qtpy.QtWidgets import QGroupBox, QLabel, \
    QPushButton, QHBoxLayout, QGridLayout, QSizePolicy
import qtawesome as qta
from pydm.widgets import PyDMPushButton

from siriuspy.epics import PV

from ..util import connect_newprocess, connect_window
from ..widgets import SiriusLedAlert, SiriusLabel, SiriusSpinbox, \
    SiriusLedState, SiriusLineEdit, SiriusEnumComboBox

from .base import IDCommonControlWindow, IDCommonDialog, \
    IDCommonSummaryBase, IDCommonSummaryHeader, IDCommonSummaryWidget


class VPUControlWindow(IDCommonControlWindow):
    """VPU Control Window."""

    MAIN_CONTROL_PVS = {
        "KParam": {
            "SP": "KParam-SP",
            "RB": "KParam-SP",   # this undulator doesn't have RB PVs
            "Mon": "KParam-Mon",
        },
        "KParam Speed": {
            "SP": "KParamVelo-SP",
            "RB": "KParamVelo-SP",   # this undulator doesn't have RB PVs
            "Mon": "KParamVelo-Mon",
        },
        "Taper": {
            "SP": "KParamTaper-SP",
            "RB": "KParamTaper-SP",  # this undulator doesn't have RB PVs
            "Mon": "KParamTaper-Mon",
        },
        "Taper Speed": {
            "Mon": "KParamTaperVelo-Mon",
        },
        "Center Offset": {
            "SP": "CenterOffset-SP",
            "RB": "CenterOffset-SP",  # this undulator doesn't have RB PVs
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
        "Start Movement": {
            "Cmd": "KParamChange-Cmd",
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
        "Scan Mode": {
            "SP": "ScanMode-Sel",
            "RB": "ScanMode-Sel",
        },
        "Scan Finished": {
            "StateMon": "ScanFinished-Mon",
        }
    }

    def _mainControlsWidget(self):
        group = QGroupBox('Main Controls')
        lay = QGridLayout()
        lay.setContentsMargins(3, 3, 3, 3)
        group.setLayout(lay)

        row = 0
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
        self._pb_dtls = QPushButton('', self)
        self._pb_dtls.setIcon(qta.icon('fa5s.list-ul'))
        self._pb_dtls.setToolTip('Open Servo Motor Detailed Status View')
        self._pb_dtls.setObjectName('sts')
        self._pb_dtls.setStyleSheet(
            '#sts{min-width:25px; max-width:25px; icon-size:20px;}')
        connect_window(
            self._pb_dtls, VPUDetails, self,
            prefix=self._prefix, device=self._device)

        self._ld_state = QLabel('State', self)
        self._lb_state = SiriusLabel(
            self, self.dev_pref.substitute(propty='State-Mon'))

        self._ld_flags = QLabel('Flags', self)
        self._lb_flags = SiriusLabel(
            self, self.dev_pref.substitute(propty='Flags-Mon'))

        self._ld_warn = QLabel('Warning', self)
        self._lb_warn = SiriusLabel(
            self, self.dev_pref.substitute(propty='Warning-Mon'))

        self._ld_alarm = QLabel('Alarm', self)
        self._lb_alarm = SiriusLabel(
            self, self.dev_pref.substitute(propty='Alarm-Mon'))

        gbox = QGroupBox('Status')
        gbox.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        lay = QGridLayout(gbox)
        lay.addWidget(self._pb_dtls, 0, 2, alignment=Qt.AlignRight)
        lay.addWidget(self._ld_state, 0, 0)
        lay.addWidget(self._lb_state, 0, 1, alignment=Qt.AlignRight)
        lay.addWidget(self._ld_flags, 1, 0)
        lay.addWidget(self._lb_flags, 1, 1, alignment=Qt.AlignRight)
        lay.addWidget(self._ld_warn, 2, 0)
        lay.addWidget(self._lb_warn, 2, 1, alignment=Qt.AlignRight)
        lay.addWidget(self._ld_alarm, 3, 0)
        lay.addWidget(self._lb_alarm, 3, 1, alignment=Qt.AlignRight)
        return gbox

    def _auxCommandsWidget(self):
        self._ld_speedlim = QLabel('Max Phase\nSpeed [mm/s]', self)
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

        gbox = QGroupBox('Auxiliary Parameters', self)
        lay = QGridLayout(gbox)
        lay.addWidget(self._ld_speedlim, 0, 0)
        lay.addWidget(self._sb_speedlim, 0, 1)
        lay.addWidget(self._lb_speedlim, 0, 2)
        lay.addWidget(self._ld_periodlen, 1, 0)
        lay.addWidget(self._lb_periodlen, 1, 1)
        lay.addWidget(self._ld_park, 2, 0)
        lay.addWidget(self._lb_park, 2, 1)
        gbox.setStyleSheet(
            '.QLabel{qproperty-alignment: "AlignRight | AlignVCenter";}')
        return gbox

    def _ffSettingsWidget(self):
        but = QPushButton('Feedforward Settings', self)
        connect_newprocess(
            but, ['sirius-hla-si-ap-idff.py', self._device])
        return but

    # --- auxiliary methods ---

    def _createParam(self, pv_info, lay, row):
        col = 1
        if "SP" in pv_info:
            pvname = self.dev_pref.substitute(propty=pv_info["SP"])
            widtype = SiriusEnumComboBox if pvname.endswith('Sel') \
                else SiriusLineEdit
            cb = widtype(self, init_channel=pvname)
            lay.addWidget(cb, row, col, 1, 1)
            col += 1

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
        ('KParam Speed', 6),
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


class VPUDetails(IDCommonDialog):
    """VPU Drive Details."""

    def __init__(self, parent=None, prefix='', device=''):
        """Init."""
        super().__init__(
            parent, prefix, device, title=device+' Servo Motor and Mode Details')

    def _setupUi(self):
        ld_speed = QLabel('Speed', self)
        ld_pos = QLabel('Pos.', self)
        ld_posmin = QLabel('Min Pos.', self)
        ld_posmax = QLabel('Max Pos.', self)
        ld_error = QLabel('Error', self)
        ld_errenc = QLabel('Error Encoder', self)
        ld_ncstate = QLabel('NC State', self)
        ld_status = QLabel('Status', self)

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
            "Pitch",
            "ServoMotor1",
            "ServoMotor2",
            "ServoMotor3",
            "ServoMotor4",
        ]

        for idx, title in enumerate(details):
            col = idx + 1
            posname = 'Pos' if title != 'KParam' else ''
            ld_dtl = QLabel(title, self)

            pvname = self.dev_pref.substitute(
                propty=f'{title}Velo-Mon')
            lb_speed = SiriusLabel(self, pvname)

            pvname = self.dev_pref.substitute(
                propty=f'{title}{posname}-Mon')
            lb_pos = SiriusLabel(self, pvname)

            pvname = self.dev_pref.substitute(
                propty=f'{title}Min{posname}-Cte')
            lb_posmin = SiriusLabel(self, pvname)

            pvname = self.dev_pref.substitute(
                propty=f'{title}Max{posname}-Cte')
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
