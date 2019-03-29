"""Defines a class to control a set of a device from a given class."""
from pydm import PyDMApplication

from qtpy.QtWidgets import QWidget

from siriushla.widgets import SiriusMainWindow
from .DCLinkWidget import DCLinkWidget
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

        sec2label = {
            'TB': 'LTB ',
            'BO': 'Booster ',
            'TS': 'BTS ',
            'SI': 'Storage Ring '}
        dis2label = {
            'MA': 'Magnets ',
            'PS': 'Power Supplies '}
        dev2label = {
            'dipole': 'Dipoles ',
            'quadrupole': 'Quadrupoles ',
            'sextupole': 'Sextupoles ',
            'quadrupole-skew': 'Skew Quadrupoles ',
            'corrector-slow': 'Slow Correctors ',
            'corrector-fast': 'Fast Correctors '}
        self.setWindowTitle(sec2label[section] +
                            (dev2label[device] if device else '') +
                            dis2label[discipline])

    def _setup_ui(self):
        # Set Widget
        self.widget = ControlWidgetFactory.factory(
            parent=self, section=self._section,
            discipline=self._discipline, device=self._device)
        # if self._device != "dipole" or self._discipline == 'PS':
        self._connect_buttons(self.widget)
        self.setCentralWidget(self.widget)

    def _connect_buttons(self, widget):
        for w in widget.get_ps_widgets():
            psname = w.psname
            detail_button = w.get_detail_button()
            trim_button = w.get_trim_button()

            connect_window(detail_button, PSDetailWindow,
                           self, psname=psname)

            if trim_button is not None:
                connect_window(trim_button, PSTrimWindow,
                               self, psname=psname)

        for w in widget.findChildren(DCLinkWidget):
            btn = w.detail_btn
            name = btn.text()
            connect_window(
                w.detail_btn, PSDetailWindow, self, psname=[name])
