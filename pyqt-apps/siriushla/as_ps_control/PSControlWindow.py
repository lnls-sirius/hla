"""Defines a class to control a set of a device from a given class."""
import qtawesome as qta

from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.search import PSSearch
from siriushla.util import connect_window, get_appropriate_color, \
    connect_newprocess
from siriushla.widgets import SiriusMainWindow
from .control_widget.ControlWidgetFactory import ControlWidgetFactory
from .PSDetailWindow import PSDetailWindow
from .PSTrimWindow import PSTrimWindow


class PSControlWindow(SiriusMainWindow):
    """Base window to show devices of a section in tabs."""

    def __init__(self, section, device, subsection=None, parent=None):
        """Class constructor."""
        super(PSControlWindow, self).__init__(parent)
        self.setObjectName(section+'App')
        self._section = section
        self._device = device
        self._subsection = subsection
        icon = qta.icon(
            'mdi.car-battery', color=get_appropriate_color(section))
        self.setWindowIcon(icon)

        self._setup_ui()

        sec2label = {
            'LI': 'Linac ',
            'TB': 'Linac to Booster ',
            'BO': 'Booster ',
            'TS': 'Booster to Storage Ring ',
            'SI': 'Storage Ring ',
            'IT': 'Injector Test '}
        dev2label = {
            "dipole": "Dipoles",
            "spectrometer": "Spectrometer",
            "quadrupole": "Quadrupoles",
            "sextupole": "Sextupoles",
            "solenoid": "Solenoids",
            "corrector-slow": "Slow Correctors",
            "corrector-fast": "Fast Correctors",
            "skew-quadrupole": "Quadrupoles Skew",
            "trim-quadrupole": "Trims",
            "lens": "Lens",
            }
        self.setWindowTitle(
            sec2label[section] +
            (dev2label[device] if device else '') +
            ' Power Supplies ' +
            ('- Subsection '+subsection if subsection else ''))

    def _setup_ui(self):
        self.widget = ControlWidgetFactory.factory(
            parent=self, section=self._section,
            subsection=self._subsection, device=self._device)
        self._connect_buttons(self.widget)
        self.setCentralWidget(self.widget)

    def _connect_buttons(self, widget):
        for w in widget.get_summary_widgets():
            detail_bt = w.get_detail_button()
            psname = detail_bt.text()
            if not psname:
                psname = detail_bt.toolTip()
            psname = _PVName(psname)
            if PSSearch.conv_psname_2_psmodel(psname) == 'REGATRON_DCLink':
                connect_newprocess(
                    w, ['sirius-hla-as-ps-regatron-individual',
                        '-dev', psname], parent=self, is_pydm=True)
            else:
                connect_window(detail_bt, PSDetailWindow, self, psname=psname)

            trim_bt = w.get_trim_button()
            if trim_bt is not None:
                connect_window(trim_bt, PSTrimWindow, self, device=psname)
