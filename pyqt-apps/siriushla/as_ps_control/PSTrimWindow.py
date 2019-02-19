"""Defines window class to show trims of a magnet."""
from pydm import PyDMApplication
from qtpy.QtWidgets import QWidget, QVBoxLayout

from siriushla.widgets import SiriusMainWindow
from siriushla.as_ps_control.PSWidget import PSWidgetFactory
from siriushla.as_ps_control.control_widget.TrimControlWidget \
    import TrimControlWidget
from siriushla.as_ps_control.PSDetailWindow import PSDetailWindow
# from siriushla.as_ma_control.MagnetTrimWindow import MagnetTrimWindow

from ..util import connect_window


class PSTrimWindow(SiriusMainWindow):
    """Allow controlling the trims of a given magnet."""

    def __init__(self, psname, parent=None):
        """Class constructor."""
        super(PSTrimWindow, self).__init__(parent)
        self.app = PyDMApplication.instance()
        self._psname = psname
        # Setup UI
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(self._psname + ' Trims')
        self.central_widget = QWidget()
        self.central_widget.layout = QVBoxLayout()
        self.central_widget.setLayout(self.central_widget.layout)
        self.setCentralWidget(self.central_widget)
        # Create family MagnetWidget
        self.fam_widget = PSWidgetFactory.factory(
            psname=self._psname, parent=self)
        self.fam_widget.trim_button.setEnabled(False)
        # Connect family detail window
        fam_button = self.fam_widget.get_detail_button()
        connect_window(fam_button, PSDetailWindow,
                       self, psname=self._psname)
        # Create TrimWidget
        device = self._psname.split("-")[-1]
        self.trim_widget = TrimControlWidget(
            dev_type='PS', trim=device, parent=self,
            orientation=TrimControlWidget.VERTICAL)
        # Connect Trim detail buttons
        self._connect_buttons(self.trim_widget)
        # Add to leyout
        self.central_widget.layout.addWidget(self.fam_widget)
        self.central_widget.layout.addWidget(self.trim_widget)

    def _connect_buttons(self, widget):
        for widget in widget.get_ps_widgets():
            psname = widget.psname
            detail_button = widget.get_detail_button()
            connect_window(detail_button, PSDetailWindow,
                           self, psname=psname)
