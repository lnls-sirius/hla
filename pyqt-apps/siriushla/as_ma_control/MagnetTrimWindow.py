"""Defines window class to show trims of a magnet."""
import re

from pydm.PyQt.QtGui import QWidget, QHBoxLayout, QVBoxLayout, \
    QGridLayout, QGroupBox, QMainWindow, QApplication, QScrollArea

from siriuspy.search import MASearch
from siriushla.as_ma_control.MagnetWidget import MagnetWidget
from siriushla.as_ma_control.control_widget.TrimControlWidget \
    import TrimControlWidget
# from siriushla.as_ma_control.MagnetTrimWindow import MagnetTrimWindow


class MagnetTrimWindow(QMainWindow):
    """Allow controlling the trims of a given magnet."""

    def __init__(self, maname, parent=None):
        """Class constructor."""
        super(MagnetTrimWindow, self).__init__(parent)
        self._maname = maname

        self._setup_ui()

        self.app = QApplication.instance()
        self.app.establish_widget_connections(self)

    def _setup_ui(self):
        self.setWindowTitle(self._maname + ' Trims')

        self.central_widget = QWidget()
        self.central_widget.layout = QVBoxLayout()
        self.central_widget.setLayout(self.central_widget.layout)
        self.setCentralWidget(self.central_widget)

        self.fam_widget = MagnetWidget(self._maname, self)
        self.fam_widget.trim_button.setEnabled(False)
        device = self._maname.split("-")[-1]
        self.trim_widget = TrimControlWidget(
            MASearch.get_manames({"section": "SI", "device": device}),
            parent=self)

        self.central_widget.layout.addWidget(self.fam_widget)
        self.central_widget.layout.addWidget(self.trim_widget)

    def closeEvent(self, event):
        """Reimplement close event to close widget connections."""
        self.app.close_widget_connections(self)
        super().closeEvent(event)
