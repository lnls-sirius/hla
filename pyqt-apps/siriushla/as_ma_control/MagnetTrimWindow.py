"""Defines window class to show trims of a magnet."""
from pydm import PyDMApplication
from pydm.PyQt.QtGui import QWidget, QVBoxLayout, QMainWindow

from siriuspy.search import MASearch
from siriushla.as_ma_control.MagnetWidget import MagnetWidget
from siriushla.as_ma_control.control_widget.TrimControlWidget \
    import TrimControlWidget
from siriushla.as_ma_control.MagnetDetailWindow import MagnetDetailWindow
from siriushla.WindowManager import WindowManager
# from siriushla.as_ma_control.MagnetTrimWindow import MagnetTrimWindow


class MagnetTrimWindow(QMainWindow):
    """Allow controlling the trims of a given magnet."""

    def __init__(self, maname, window_manager=None, parent=None):
        """Class constructor."""
        super(MagnetTrimWindow, self).__init__(parent)
        self.app = PyDMApplication.instance()
        self._maname = maname
        # Set window manager
        if window_manager is None:
            self._window_manager = WindowManager()
        else:
            self._window_manager = window_manager
        # Setup UI
        self._setup_ui()
        # Establish PyDM epics connections
        self.app.establish_widget_connections(self)

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
        self._window_manager.register_window(
            self._maname + "_detail", MagnetDetailWindow,
            maname=self._maname, parent=self)
        self.fam_widget.get_detail_button().clicked.connect(
            lambda: self._window_manager.open_window(
                self.sender().parent().maname + "_detail"))
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

            self._window_manager.register_window(
                maname + "_detail", MagnetDetailWindow,
                maname=maname, parent=self)
            detail_button.clicked.connect(
                lambda:  self._window_manager.open_window(
                    self.sender().text() + "_detail"))
