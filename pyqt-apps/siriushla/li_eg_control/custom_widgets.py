"""Custom widgets for Linac Egun."""

from qtpy.QtWidgets import QLabel, QGridLayout

from siriuspy.namesys import SiriusPVName
from siriuspy.pwrsupply.csdev import Const as _PSConst

from ..widgets import SiriusDialog, PyDMLedMultiChannel


class LIEGTrigEnblDetail(SiriusDialog):
    """Detail window for e-gun enablereal status conditions."""

    def __init__(self, parent=None, device="", prefix=""):
        """."""
        super().__init__(parent=parent)
        self._prefix = prefix
        self._device = device
        self._devpref = SiriusPVName(device).substitute(prefix=prefix)
        self.setObjectName('LIApp')
        self._setupUi()

    def _setupUi(self):
        desc2cond = {
            1: {
                "LI-01:EG-TriggerPS is enable": {
                    "LI-01:EG-TriggerPS:enable": _PSConst.OffOn.On
                },
                "LI-01:PS-Spect Current is out of operation range": {
                    "LI-01:PS-Spect:Current-Mon": {
                        "comp": "ou",
                        "value": [0.5, 12.0],
                    }
                },
            },
            2: {
                "LI-01:EG-TriggerPS is enable": {
                    "LI-01:EG-TriggerPS:enable": _PSConst.OffOn.On
                },
                "TB-Fam:PS-B OpMode is in SlowRef": {
                    "TB-Fam:PS-B:OpMode-Sts": _PSConst.States.SlowRef
                },
                "TB-Fam:PS-B Current is greater than 5A": {
                    "TB-Fam:PS-B:Current-Mon": {
                        "comp": "ge",
                        "value": 5.0,
                    }
                },
                "TB-04:PU-InjSept Pulse is On": {
                    "TB-04:PU-InjSept:Pulse-Sts": _PSConst.OffOn.On
                },
                "TB-04:PU-InjSept Voltage is greater than 400V": {
                    "TB-04:PU-InjSept:Voltage-Mon": {
                        "comp": "ge",
                        "value": 400.0,
                    }
                },
            }
        }
        lay = QGridLayout(self)

        title = QLabel("<h4>Linac E-gun Trigger Conditions</h4>")
        lay.addWidget(title, 0, 0, 1, 2)

        row = 1
        for group, conds in desc2cond.items():
            if group > 1:
                lay.addWidget(QLabel('<h4>or</h4>'), row, 1, 1, 2)
                row += 1
            for desc, cond in conds.items():
                label = QLabel(desc, self)
                led = PyDMLedMultiChannel(self, channels2values=cond)
                lay.addWidget(led, row, 0)
                lay.addWidget(label, row, 1)
                row += 1
