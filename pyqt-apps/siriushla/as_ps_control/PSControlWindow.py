"""Defines a class to control a set of a device from a given class."""
import qtawesome as qta

from siriuspy.namesys import SiriusPVName as _PVName
from siriushla.util import connect_window, get_appropriate_color
from siriushla.widgets import SiriusMainWindow
from .control_widget.ControlWidgetFactory import ControlWidgetFactory
from .PSDetailWindow import PSDetailWindow
from .PSTrimWindow import PSTrimWindow


class PSControlWindow(SiriusMainWindow):
    """Base window to show devices of a section in tabs."""

    def __init__(self, section, discipline, device, parent=None):
        """Class constructor."""
        super(PSControlWindow, self).__init__(parent)
        self.setObjectName(section+'App')
        self._section = section
        self._discipline = discipline
        self._device = device
        if discipline.lower().startswith('ma'):
            icon = qta.icon('mdi.magnet', color=get_appropriate_color(section))
        else:
            icon = qta.icon(
                'mdi.car-battery', color=get_appropriate_color(section))
        self.setWindowIcon(icon)

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
            'corrector-slow': 'Slow Correctors '}
        #     'corrector-fast': 'Fast Correctors '}
        self.setWindowTitle(sec2label[section] +
                            (dev2label[device] if device else '') +
                            dis2label[discipline])

    def _setup_ui(self):
        self.widget = ControlWidgetFactory.factory(
            parent=self, section=self._section,
            discipline=self._discipline, device=self._device)
        self._connect_buttons(self.widget)
        self.setCentralWidget(self.widget)

    def _connect_buttons(self, widget):
        for w in widget.get_summary_widgets():
            detail_bt = w.get_detail_button()
            psname = detail_bt.text()
            if not psname:
                psname = detail_bt.toolTip()
            psname = _PVName(psname)
            connect_window(detail_bt, PSDetailWindow, self, psname=psname)

            trim_bt = w.get_trim_button()
            if trim_bt is not None:
                connect_window(trim_bt, PSTrimWindow, self, psname=psname)
