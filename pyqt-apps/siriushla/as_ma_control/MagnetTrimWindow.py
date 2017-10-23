"""Defines window class to show trims of a magnet."""
from pydm import PyDMApplication
from pydm.PyQt.QtGui import QWidget, QVBoxLayout, QMainWindow

from siriuspy.search import MASearch
from siriushla.as_ma_control.MagnetWidget import MagnetWidget
from siriushla.as_ma_control.control_widget.TrimControlWidget \
    import TrimControlWidget
from siriushla.as_ma_control.MagnetDetailWindow import MagnetDetailWindow
# from siriushla.as_ma_control.MagnetTrimWindow import MagnetTrimWindow

from ..util import connect_window


class MagnetTrimWindow(QMainWindow):
    """Allow controlling the trims of a given magnet."""

    def __init__(self, maname, parent=None):
        """Class constructor."""
        super(MagnetTrimWindow, self).__init__(parent)
        self.app = PyDMApplication.instance()
        self._maname = maname
        # Setup UI
        self._setup_ui()
        # Establish PyDM epics connections
        # self.app.establish_widget_connections(self)

    def _setup_ui(self):
        self.setWindowTitle(self._maname + ' Trims')
        self.central_widget = QWidget()
        self.central_widget.layout = QVBoxLayout()
        self.central_widget.setLayout(self.central_widget.layout)
        self.setCentralWidget(self.central_widget)
        # Create family MagnetWidget
        self.fam_widget = MagnetWidget(self._maname, self)
        self.fam_widget.trim_button.setEnabled(False)
        # Connect family detail window
        fam_button = self.fam_widget.get_detail_button()
        connect_window(fam_button, MagnetDetailWindow,
                       self, maname=self._maname)
        # Create TrimWidget
        device = self._maname.split("-")[-1]
        self.trim_widget = TrimControlWidget(
            MASearch.get_manames({"section": "SI", "device": device}),
            parent=self, orientation=TrimControlWidget.VERTICAL)
        # Connect Trim detail buttons
        self._connect_buttons(self.trim_widget)
        # Add to leyout
        self.central_widget.layout.addWidget(self.fam_widget)
        self.central_widget.layout.addWidget(self.trim_widget)

    def _connect_buttons(self, widget):
        for widget in widget.get_magnet_widgets():
            maname = widget.maname
            detail_button = widget.get_detail_button()
            connect_window(detail_button, MagnetDetailWindow,
                           self, maname=maname)

    def showEvent(self, event):
        """Establish connections and call super."""
        self.app.establish_widget_connections(self)
        super().showEvent(event)

    def closeEvent(self, event):
        """Override closeEvent in order to close iwdget connections."""
        self.app.close_widget_connections(self)
        super().closeEvent(event)
