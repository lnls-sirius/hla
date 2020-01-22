"""Defines window class to show trims of a magnet."""

from qtpy.QtWidgets import QWidget, QVBoxLayout

from siriuspy.namesys import SiriusPVName
from siriushla.widgets import SiriusMainWindow
from siriushla.util import connect_window
from .control_widget.TrimFamControlWidget import SITrimFamControlWidget
from .PSDetailWindow import PSDetailWindow
from .SummaryWidgets import SummaryWidget


class PSTrimWindow(SiriusMainWindow):
    """Allow controlling the trims of a given magnet."""

    def __init__(self, device, parent=None):
        """Class constructor."""
        super(PSTrimWindow, self).__init__(parent)
        self.setObjectName('SIApp')
        self._devname = SiriusPVName(device)
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(self._devname + ' Trims')
        self.central_widget = QWidget()
        self.central_widget.layout = QVBoxLayout()
        self.central_widget.setLayout(self.central_widget.layout)
        self.setCentralWidget(self.central_widget)
        # Create family MagnetWidget
        self.fam_widget = SummaryWidget(
            name=self._devname, parent=self,
            visible_props={
                'detail', 'state', 'intlk', 'setpoint', 'monitor',
                'strength_sp', 'strength_mon', 'trim'})
        self.fam_widget.get_trim_button().setVisible(False)
        # Connect family detail window
        fam_button = self.fam_widget.get_detail_button()
        connect_window(fam_button, PSDetailWindow, self, psname=self._devname)
        # Create TrimWidget
        device = self._devname.split("-")[-1]
        self.trim_widget = SITrimFamControlWidget(
            trim=device, parent=self,
            orientation=SITrimFamControlWidget.HORIZONTAL)
        # Connect Trim detail buttons
        self._connect_buttons(self.trim_widget)
        # Add to leyout
        self.central_widget.layout.addWidget(self.fam_widget)
        self.central_widget.layout.addWidget(self.trim_widget)

    def _connect_buttons(self, widget):
        for widget in widget.get_summary_widgets():
            psname = widget.devname
            detail_bt = widget.get_detail_button()
            connect_window(detail_bt, PSDetailWindow, self, psname=psname)
