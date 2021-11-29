"""MachShift widgets."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGridLayout

from ..widgets import SiriusLabel, SiriusFrame


class MachShiftLabel(QWidget):
    """Machine Shift Label."""

    def __init__(self, parent=None, prefix=''):
        """Init."""
        super().__init__(parent)

        self.label = SiriusLabel(
            self, prefix+'AS-Glob:AP-MachShift:Mode-Sts')
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
        ]
        self.frame = SiriusFrame(
            self, prefix+'AS-Glob:AP-MachShift:Mode-Sts',
            color_list=color_list, is_float=False)
        self.frame.add_widget(self.label)

        lay = QGridLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.frame)
