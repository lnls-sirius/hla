"""MachShift widgets."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGridLayout

from siriuspy.namesys import SiriusPVName as _PVName

from ..widgets import SiriusLabel, SiriusFrame


class MachShiftLabel(QWidget):
    """Machine Shift Label."""

    def __init__(self, parent=None, prefix=''):
        """Init."""
        super().__init__(parent)

        pvname = _PVName('AS-Glob:AP-MachShift:Mode-Sts')
        pvname = pvname.substitute(prefix=prefix)

        self.label = SiriusLabel(self, pvname)
        self.label.setAlignment(Qt.AlignCenter)

        color_list = [
            SiriusFrame.Yellow,  # Users
            SiriusFrame.MediumBlue,  # Commissioning
            SiriusFrame.DarkCyan,  # Conditioning
            SiriusFrame.LightSalmon,  # Injection
            SiriusFrame.LightBlue,  # MachineStudy
            SiriusFrame.MediumGreen,  # Maintenance
            SiriusFrame.LightGray,  # Standby
            SiriusFrame.DarkGray,  # Shutdown
            SiriusFrame.MediumBlue,  # MachineStartup
        ]
        self.frame = SiriusFrame(
            self, pvname,
            color_list=color_list, is_float=False)
        self.frame.add_widget(self.label)

        lay = QGridLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.frame)
