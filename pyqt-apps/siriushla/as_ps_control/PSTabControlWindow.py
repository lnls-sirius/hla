"""Defines a class to control elements from a given class."""
import time as _time
from qtpy.QtWidgets import QTabWidget, QWidget, QGridLayout, QLabel
from qtpy.QtCore import Signal, QThread
from siriushla.widgets import SiriusDialog
from .PSControlWindow import PSControlWindow
from .control_widget.ControlWidgetFactory import ControlWidgetFactory


class PSTabControlWindow(PSControlWindow):
    """Base window to show devices of a section in tabs."""

    Devices = {
        "LI": ["lens", "corrector-slow", "solenoid", "quadrupole",
               "spectrometer"],
        "TB": ["dipole", "quadrupole", "corrector-slow"],
        "BO": ["dipole", "quadrupole", "sextupole", "corrector-slow",
               "skew-quadrupole"],
        "TS": ["dipole", "quadrupole", "corrector-slow"],
        "SI": ["dipole", "quadrupole", "sextupole"],
        "IT": ["lens", ]}

    TabName = {"dipole": "Dipoles",
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

    tabFilled = Signal()

    def __init__(self, section, parent=None):
        """Class constructor."""
        super().__init__(section=section,
                         device=None,
                         parent=parent)

    def _setup_ui(self):
        self.setWindowTitle(self._section+' PS Control')
        # Create Tabs
        self.tabs = QTabWidget()
        self.tabs.setObjectName(self._section + "Tab")
        self.TabIndex = dict()
        self._addTabs()
        self.tabs.currentChanged.connect(self._fillTabTask)
        # Set widget layout
        self.setCentralWidget(self.tabs)

    def _addTabs(self):
        for device in self.Devices[self._section]:
            widget = QWidget(self)
            index = self.tabs.addTab(widget, self.TabName[device])
            self.TabIndex[index] = {
                'device': device, 'widget': widget, 'filled': False}
            if index in range(3):
                self._fillTab(index)

    def _fillTabTask(self, index):
        if self.TabIndex[index]['filled']:
            return
        th = _WaitThread(parent=self, index=index)
        dlg = _WaitDialog(self)
        th.opendiag.connect(dlg.show)
        th.closediag.connect(dlg.close)
        th.tabIndex.connect(self._fillTab)
        self.tabFilled.connect(th.exit_thread)
        th.start()

    def _fillTab(self, index):
        self.TabIndex[index]['filled'] = True
        device = self.TabIndex[index]['device']
        widget = self.TabIndex[index]['widget']
        widget.setLayout(QGridLayout())
        widget.layout().setContentsMargins(0, 0, 0, 0)
        tabwid = ControlWidgetFactory.factory(
            self, self._section, device)
        self._connect_buttons(tabwid)
        widget.layout().addWidget(tabwid)
        self.tabFilled.emit()

    def _dipoleWidgetWrapper(self, widget):
        wrapper = QWidget(self)
        wrapper.layout = QGridLayout()
        wrapper.setLayout(wrapper.layout)

        wrapper.layout.addWidget(widget, 0, 0)
        wrapper.layout.setRowStretch(1, 1)
        wrapper.layout.setColumnStretch(1, 1)

        return wrapper


class _WaitDialog(SiriusDialog):
    """Auxiliary dialog to show during a long task."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Wait')
        lay = QGridLayout(self)
        lay.addWidget(QLabel('Wait a moment...'))


class _WaitThread(QThread):

    opendiag = Signal()
    closediag = Signal()
    tabIndex = Signal(int)

    def __init__(self, parent=None, section='', index={}):
        super().__init__(parent)
        self._index = index
        self._exit_thread = False

    def exit_thread(self):
        self._exit_thread = True

    def run(self):
        self.opendiag.emit()
        self.tabIndex.emit(self._index)
        while not self._exit_thread:
            _time.sleep(0.1)
        self.closediag.emit()
