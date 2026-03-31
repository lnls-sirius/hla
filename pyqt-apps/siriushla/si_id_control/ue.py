"""UE Control Module."""

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


class UEControlWindow(IDCommonControlWindow):
    """UE Control Window."""

    OPERATION_PVS = {
        "Pol": {
            "Sel": "Pol-Sel",
            "Mon": "Pol-Mon"
        },
        "Power Off": "PowerOff-Mon",
        "Kill Override": "KillOverride-Mon",
        "Is Remote": "IsRemote-Mon",
        "Device Status": "DeviceStatus-Mon",
        "Start Parking": {
            "Cmd": "StartParking-Cmd",
            "icon": "fa5s.parking"
        },
        "Sw": {
            "Kill Override": "KillOverride-Mon"
        },
        "Abort": {
            "Cmd": "Abort-Cmd",
            "icon": "fa5s.stop"
        }
    }

    MAIN_CONTROL_PVS = {
        "KParam": {
            "SP": "KParam-SP",
            "Mon": "KParam-Mon"
        },
        "KParam Speed": {
            "SP": "KParamVelo-SP",
            "RB": "KParamVelo-RB",
            "Mon": "KParamVelo-Mon"
        },
        "KParam Min Pos": {
            "Cte": "KParamMinPos-Cte"
        },
        "KParam Max Pos": {
            "Cte": "KParamMaxPos-Cte"
        },
        "KParam Parked": {
            "Cte": "KParamParked-Cte"
        },
        "Change KParam": {
            "Cmd": "KParamChange-Cmd",
            "icon": "fa5s.play"
        },
        "PParam": {
            "SP": "PParam-SP",
            "Mon": "PParam-Mon"
        },
        "PParam Speed": {
            "SP": "PParamVelo-SP",
            "RB": "PParamVelo-RB",
            "Mon": "PParamVelo-Mon"
        },
        "PParam Min Pos": {
            "Cte": "PParamMinPos-Cte"
        },
        "PParam Max Pos": {
            "Cte": "PParamMaxPos-Cte"
        },
        "PParam Parked": {
            "Cte": "PParamParked-Cte"
        },
        "Change PParam": {
            "Cmd": "PParamChange-Cmd",
            "icon": "fa5s.play"
        },
        "CParam": {
            "SP": "CParam-SP",
            "Mon": "CParam-Mon"
        },
        "CParam Speed": {
            "SP": "CParamVelo-SP",
            "RB": "CParamVelo-RB",
            "Mon": "CParamVelo-Mon"
        },
        "CParam Min Pos": {
            "Cte": "CParamMinPos-Cte"
        },
        "CParam Max Pos": {
            "Cte": "CParamMaxPos-Cte"
        },
        "CParam State NC": {
            "Mon": "CParamStateNC-Mon"
        },
        "CParam Error NC": {
            "Mon": "CParamErrorNC-Mon"
        },
        "CParam Parked": {
            "Cte": "CParamParked-Cte"
        },
        "Change CParam": {
            "Cmd": "CParamChange-Cmd",
            "icon": "fa5s.play"
        },
        "Offset": {
            "SP": "Offset-SP",
            "Mon": "Offset-Mon"
        },
        "Offset Speed": "OffsetVelo-Mon",
        "Offset Min Pos": "OffsetMinPos-Cte",
        "Offset Max Pos": "OffsetMaxPos-Cte",
        "Offset NC State": "OffsetStateNC-Mon",
        "Offset NC Error": "OffsetErrorNC-Mon",
        "Servos Positions": {
            "Top Right": "TIPos-Mon",
            "Top Left": "TOPos-Mon",
            "Bottom Right": "BIPos-Mon",
            "Bottom Left": "BOPos-Mon"
        },
        "Servos IO Status": {
            "Top Outside": "TOStatusIO-Mon",
            "Top Inside": "TIStatusIO-Mon",
            "Bot Outside": "BOStatusIO-Mon",
            "Bot Inside": "BIStatusIO-Mon"
        },
        "Servos NC Status": {
            "Top Outside": "TOStateNC-Mon",
            "Top Inside": "TIStateNC-Mon",
            "Bot Outside": "BOStateNC-Mon",
            "Bot Inside": "BIStateNC-Mon"
        },
        "Servos Error NC": {
            "Top Outside": "TOErrorNC-Mon",
            "Top Inside": "TIErrorNC-Mon",
            "Bot Outside": "BOErrorNC-Mon",
            "Bot Inside": "BIErrorNC-Mon"
        },
        "KShift NC State": "KShiftStateNC-Mon",
        "KShift NC Error": "KShiftErrorNC-Mon",
        "PShift NC State": "PShiftStateNC-Mon",
        "PShift NC Error": "PShiftErrorNC-Mon",
        "CParam NC State": "CParamStateNC-Mon",
        "CParam NC Error": "CParamErrorNC-Mon",
        "Max. Speed": {
            "SP": "MaxVelo-SP",
            "RB": "MaxVelo-RB"
        },
        "Speed Setpoint": "Velo-SP",
        "Acc. Setpoint": "Acc-SP",
        "Period Length": "PeriodLength-Cte",
        "Moving": "Moving-Mon"
    }

    SCANS_PVS = {
        "Read Traj": {
            "Cmd": "ReadTraj-Cmd",
            "icon": "fa5s.play"
        },
        "Write Traj": {
            "Cmd": "WriteTraj-Cmd",
            "icon": "mdi.keyboard-return"
        },
        "Fly First Pos": "FlyFirstPos-Mon",
        "Scan Done": "ScanDone-Mon",
        "Scan Mode": "ScanMode-Sel"
    }
