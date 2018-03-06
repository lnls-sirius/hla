"""Defines a class to control a set of a device from a given class."""
from pydm import PyDMApplication

from siriushla.widgets import SiriusMainWindow
from .control_widget.ControlWidgetFactory import ControlWidgetFactory
from .PSDetailWindow import PSDetailWindow
from .PSTrimWindow import PSTrimWindow

from ..util import connect_window


class PSControlWindow(SiriusMainWindow):
    """Base window to show devices of a section in tabs."""

    def __init__(self, section, discipline, device, parent=None):
        """Class constructor."""
        super(PSControlWindow, self).__init__(parent)
        self.app = PyDMApplication.instance()
        self._section = section
        self._discipline = discipline
        self._device = device

        self._setup_ui()

        # self.app.establish_widget_connections(self)

    def _setup_ui(self):
        # Set Widget
        self.widget = ControlWidgetFactory.factory(
            self._section, self._discipline, self._device)
        if self._device != "dipole" or self._discipline == 0:
            self._connect_buttons(self.widget)
        self.setCentralWidget(self.widget)

    def _connect_buttons(self, widget):
        # buttons = widget.get_detail_buttons()
        for widget in widget.get_ps_widgets():
            psname = widget.psname
            detail_button = widget.get_detail_button()
            trim_button = widget.get_trim_button()

            connect_window(detail_button, PSDetailWindow,
                           self, psname=psname)

            if trim_button is not None:
                connect_window(trim_button, PSTrimWindow,
                               self, psname=psname)
