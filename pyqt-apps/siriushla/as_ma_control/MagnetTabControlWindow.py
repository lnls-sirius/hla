"""Defines a class to control elements from a given class."""
from pydm.PyQt.QtGui import QTabWidget, QWidget, QGridLayout

from siriushla.as_ma_control.MagnetControlWindow import MagnetControlWindow
from .control_widget.ControlWidgetFactory import ControlWidgetFactory


class MagnetTabControlWindow(MagnetControlWindow):
    """Base window to show devices of a section in tabs."""

    Devices = {
        "TB": ["dipole", "corrector-slow"],
        "BO": ["dipole", "quadrupole", "sextupole", "corrector-slow",
               "quadrupole-skew"],
        "TS": ["dipole", "corrector-slow"],
        "SI": ["dipole", "quadrupole", "sextupole", "corrector-slow",
               "corrector-fast", "quadrupole-skew"]}

    TabName = {"dipole": "Dipoles",
               "quadrupole": "Quadrupoles",
               "sextupole": "Sextupoles",
               "corrector-slow": "Slow Correctors",
               "corrector-fast": "Fast Correctors",
               "quadrupole-skew": "Quadrupoles Skew"}

    def __init__(self, section, parent=None):
        """Class constructor."""
        super().__init__(section=section,
                         device=None,
                         parent=parent)

    def _setup_ui(self):
        # Create Tabs
        self.tabs = QTabWidget()
        self.tabs.setObjectName(self._section + "Tab")
        self._addTabs()
        # Set widget layout
        self.setCentralWidget(self.tabs)

    def _addTabs(self):
        for device in self.Devices[self._section]:
            widget = ControlWidgetFactory.factory(self._section, device)
            if device == "dipole":
                widget = self._dipoleWidgetWrapper(widget)
            if device != "dipole":
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
