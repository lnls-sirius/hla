"""Defines a class to control elements from a given class."""
from qtpy.QtWidgets import QTabWidget, QWidget, QGridLayout

from siriushla.as_ps_control.PSControlWindow import PSControlWindow
from .control_widget.ControlWidgetFactory import ControlWidgetFactory


class PSTabControlWindow(PSControlWindow):
    """Base window to show devices of a section in tabs."""

    Devices = {
        "TB": ["dipole", "quadrupole", "corrector-slow"],
        "BO": ["dipole", "quadrupole", "sextupole", "corrector-slow",
               "quadrupole-skew"],
        "TS": ["dipole", "quadrupole", "corrector-slow"],
        "SI": ["dipole", "quadrupole", "sextupole", "corrector-slow",
               "corrector-fast", "quadrupole-skew"]}

    TabName = {"dipole": "Dipoles",
               "quadrupole": "Quadrupoles",
               "sextupole": "Sextupoles",
               "corrector-slow": "Slow Correctors",
               "corrector-fast": "Fast Correctors",
               "quadrupole-skew": "Quadrupoles Skew"}

    def __init__(self, section, discipline, parent=None):
        """Class constructor."""
        super().__init__(section=section,
                         discipline=discipline,
                         device=None,
                         parent=parent)

    def _setup_ui(self):
        self.setWindowTitle(self._section+' '+self._discipline+' Control')
        # Create Tabs
        self.tabs = QTabWidget()
        self.tabs.setObjectName(self._section + "Tab")
        self._addTabs()
        # Set widget layout
        self.setCentralWidget(self.tabs)

    def _addTabs(self):
        for device in self.Devices[self._section]:
            widget = ControlWidgetFactory.factory(
                self, self._section, self._discipline, device)
            if device == "dipole" and self._discipline == 'MA':
                widget = self._dipoleWidgetWrapper(widget)
            if device != "dipole" or self._discipline == 'PS':
                self._connect_buttons(widget)
            self.tabs.addTab(widget, self.TabName[device])

    def _dipoleWidgetWrapper(self, widget):
        wrapper = QWidget(self)
        wrapper.layout = QGridLayout()
        wrapper.setLayout(wrapper.layout)

        wrapper.layout.addWidget(widget, 0, 0)
        wrapper.layout.setRowStretch(1, 1)
        wrapper.layout.setColumnStretch(1, 1)

        return wrapper
