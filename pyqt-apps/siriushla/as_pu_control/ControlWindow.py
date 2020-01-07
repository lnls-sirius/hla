"""Modulet that defines the window class that control pulsed mangets."""

from qtpy.QtCore import Qt, Slot
from qtpy.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QAction, QMenu
import qtawesome as qta
from siriuspy.search import PSSearch
from siriushla.util import get_appropriate_color
from siriushla.widgets import SiriusMainWindow
from siriushla.as_ps_control.SummaryWidgets import SummaryWidget, SummaryHeader
from siriushla.util import connect_window
from .DetailWindow import PUDetailWindow


class PUControlWindow(SiriusMainWindow):
    """Window to control pulsed magnets."""

    def __init__(self, parent=None, section=None, is_main=True):
        """Constructor."""
        super().__init__(parent)
        self._section = section
        self._is_main = is_main
        self.setWindowTitle(section.upper() + ' Pulsed Magnets Control Window')
        if section in {'InjBO', 'EjeBO'}:
            color = get_appropriate_color('BO')
            self.setObjectName('BOApp')
        elif section in {'InjSI', 'Ping'}:
            color = get_appropriate_color('SI')
            self.setObjectName('SIApp')
        else:
            color = get_appropriate_color(section)
            self.setObjectName(section+'App')
        self.setWindowIcon(qta.icon('mdi.current-ac', color=color))
        self.pu_widgets_dict = dict()
        self._setup_ui()
        self.setCentralWidget(self.main_widget)
        self.setFocusPolicy(Qt.StrongFocus)
        self._create_actions()

    def _setup_ui(self):
        if self._is_main:
            self.main_widget = QTabWidget(self)
            self.main_widget.layout = QVBoxLayout()
            self.main_widget.setLayout(self.main_widget.layout)
            self.main_widget.addTab(self._make_tab_widget('TB'), 'TB')
            self.main_widget.addTab(self._make_tab_widget('BO'), 'Booster')
            self.main_widget.addTab(self._make_tab_widget('TS'), 'TS')
            self.main_widget.addTab(
                self._make_tab_widget('SI'), 'Storage Ring')
            self._connect_buttons()
        elif self._section is not None:
            self.main_widget = self._make_tab_widget(self._section)
            self._connect_buttons()
        else:
            raise ValueError('Invalid \'section\' argument!')

    def _make_tab_widget(self, sec):
        widget = QWidget(self)
        lay = QVBoxLayout(widget)

        if sec in {'TB', 'BO', 'TS', 'SI'}:
            devices = PSSearch.get_psnames({'sec': sec, 'dis': 'PU'})
        elif sec == 'InjBO':
            devices = PSSearch.get_psnames(
                {'sec': '(TB|BO)', 'dis': 'PU', 'dev': 'Inj'})
        elif sec == 'EjeBO':
            devices = PSSearch.get_psnames(
                {'sec': '(BO|TS)', 'dis': 'PU', 'dev': 'Eje'})
        elif sec == 'InjSI':
            devices = PSSearch.get_psnames(
                {'sec': '(TS|SI)', 'dis': 'PU', 'dev': 'Inj'})
        elif sec == 'Ping':
            devices = PSSearch.get_psnames(
                {'sec': 'SI', 'dis': 'PU', 'dev': 'Ping'})

        visible_props = {'detail', 'state', 'reset', 'intlk',
                         'setpoint', 'monitor', 'pulse',
                         'strength_sp', 'strength_mon'}

        lay.addWidget(SummaryHeader(devices[0], visible_props, self))
        for device in devices:
            ma_widget = SummaryWidget(device, visible_props, self)
            lay.addWidget(ma_widget)
            self.pu_widgets_dict[device] = ma_widget

        lay.addStretch()
        return widget

    def _connect_buttons(self):
        """Connect buttons in the SummaryWidgets."""
        widgets = self.main_widget.findChildren(SummaryWidget)
        for widget in widgets:
            devname = widget.devname
            bt = widget.get_detail_button()
            connect_window(bt, PUDetailWindow, self, devname=devname)

    # Actions methods
    def _create_actions(self):
        wid = self.centralWidget()
        self.turn_on_act = QAction("Turn On", wid)
        self.turn_on_act.triggered.connect(lambda: self._set_pwrstate(True))

        self.turn_off_act = QAction("Turn Off", wid)
        self.turn_off_act.triggered.connect(lambda: self._set_pwrstate(False))

        self.pulse_on_act = QAction("Pulse On", wid)
        self.pulse_on_act.triggered.connect(lambda: self._set_pulse(True))

        self.pulse_off_act = QAction("Pulse Off", wid)
        self.pulse_off_act.triggered.connect(lambda: self._set_pulse(False))

        self.reset_act = QAction("Reset Interlocks", wid)
        self.reset_act.triggered.connect(self._reset_interlocks)

        self.reset_act = QAction("Set Voltage to 0.0", wid)
        self.reset_act.triggered.connect(self._set_voltage)

    # # Overloaded method
    def contextMenuEvent(self, event):
        """Show a custom context menu."""
        point = event.pos()
        menu = QMenu("Actions", self)
        menu.addAction(self.turn_on_act)
        menu.addAction(self.turn_off_act)
        menu.addAction(self.pulse_on_act)
        menu.addAction(self.pulse_off_act)
        menu.addAction(self.reset_act)
        menu.popup(self.mapToGlobal(point))

    @Slot(bool)
    def _set_pwrstate(self, state):
        """Execute turn on/off actions."""
        for widget in self.pu_widgets_dict.values():
            try:
                if state:
                    widget.turn_on()
                else:
                    widget.turn_off()
            except TypeError:
                pass

    @Slot(bool)
    def _set_pulse(self, state):
        """Execute turn on/off actions."""
        for widget in self.pu_widgets_dict.values():
            try:
                if state:
                    widget.pulse_on()
                else:
                    widget.pulse_off()
            except TypeError:
                pass

    @Slot()
    def _reset_interlocks(self):
        """Reset interlocks."""
        for widget in self.pu_widgets_dict.values():
            try:
                widget.reset()
            except TypeError:
                pass

    @Slot()
    def _set_voltage(self):
        """Reset interlocks."""
        for widget in self.pu_widgets_dict.values():
            try:
                widget.setpoint.sp_lineedit.setText('0.0')
                widget.setpoint.sp_lineedit.send_value()
            except TypeError:
                pass


if __name__ == "__main__":
    import sys
    from siriushla.sirius_application import SiriusApplication
    app = SiriusApplication()
    w = PUControlWindow()
    w.show()
    sys.exit(app.exec_())
