"""Defines a class to control a set of a device from a given class."""
from pydm import PyDMApplication
from pydm.PyQt.QtGui import QMainWindow

from ..WindowManager import WindowManager
from .control_widget.ControlWidgetFactory import ControlWidgetFactory
from .MagnetDetailWindow import MagnetDetailWindow
from .MagnetTrimWindow import MagnetTrimWindow


class MagnetControlWindow(QMainWindow):
    """Base window to show devices of a section in tabs."""

    def __init__(self, section, device, window_manager=None, parent=None):
        """Class constructor."""
        super(MagnetControlWindow, self).__init__(parent)
        self.app = PyDMApplication.instance()
        self._section = section
        self._device = device

        if window_manager is None:
            self._window_manager = WindowManager()
        else:
            self._window_manager = window_manager

        self._setup_ui()

        self.app.establish_widget_connections(self)

    def _setup_ui(self):
        # Set Widget
        self.widget = ControlWidgetFactory.factory(self._section, self._device)
        if self._device != "dipole":
            self._connect_buttons(self.widget)
        self.setCentralWidget(self.widget)

    def _connect_buttons(self, widget):
        # buttons = widget.get_detail_buttons()
        for widget in widget.get_magnet_widgets():
            maname = widget.maname
            detail_button = widget.get_detail_button()
            trim_button = widget.get_trim_button()

            self._window_manager.register_window(
                maname + "_detail", MagnetDetailWindow,
                maname=maname, parent=self)
            detail_button.clicked.connect(
                lambda:  self._window_manager.open_window(self.sender().text() + "_detail"))
            if trim_button is not None:
                self._window_manager.register_window(
                    maname + "_trim", MagnetTrimWindow,
                    maname=maname, parent=self)
                trim_button.clicked.connect(
                    lambda: self._window_manager.open_window(self.sender().text() + "_trim"))
