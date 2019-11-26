"""Modulet that defines the window class that control pulsed mangets."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QVBoxLayout, QTabWidget
import qtawesome as qta
from siriuspy.search import PSSearch, MASearch
from siriushla.util import get_appropriate_color
from siriushla.widgets import SiriusMainWindow
from siriushla.as_ps_control.SummaryWidgets import SummaryWidget, SummaryHeader
from siriushla.util import connect_window
from .DetailWindow import PUDetailWindow


class PUControlWindow(SiriusMainWindow):
    """Window to control pulsed magnets."""

    def __init__(self, parent=None, section=None, devtype='PU', is_main=True):
        """Constructor."""
        super().__init__(parent)
        self._section = section
        self._devtype = devtype
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
        self._setup_ui()
        self.setCentralWidget(self.main_widget)
        self.setFocusPolicy(Qt.StrongFocus)

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

        if self._devtype == 'PU':
            fsearch = PSSearch.get_psnames
        else:
            fsearch = MASearch.get_manames

        if sec in {'TB', 'BO', 'TS', 'SI'}:
            devices = fsearch({'sec': sec, 'dis': self._devtype})
        elif sec == 'InjBO':
            devices = fsearch(
                {'sec': '(TB|BO)', 'dis': self._devtype, 'dev': 'Inj'})
        elif sec == 'EjeBO':
            devices = fsearch(
                {'sec': '(BO|TS)', 'dis': self._devtype, 'dev': 'Eje'})
        elif sec == 'InjSI':
            devices = fsearch(
                {'sec': '(TS|SI)', 'dis': self._devtype, 'dev': 'Inj'})
        elif sec == 'Ping':
            devices = fsearch(
                {'sec': 'SI', 'dis': self._devtype, 'dev': 'Ping'})

        visible_props = {'detail', 'state', 'reset', 'intlk',
                         'setpoint', 'monitor', 'pulse',
                         'strength_sp', 'strength_mon'}

        lay.addWidget(SummaryHeader(devices[0], visible_props, self))
        for device in devices:
            ma_widget = SummaryWidget(device, visible_props, self)
            lay.addWidget(ma_widget)

        lay.addStretch()
        return widget

    def _connect_buttons(self):
        """Connect buttons in the SummaryWidgets."""
        widgets = self.main_widget.findChildren(SummaryWidget)
        for widget in widgets:
            devname = widget.devname
            bt = widget.get_detail_button()
            connect_window(bt, PUDetailWindow, self, devname=devname)


if __name__ == "__main__":
    import sys
    from siriushla.sirius_application import SiriusApplication
    app = SiriusApplication()
    w = PUControlWindow()
    w.show()
    sys.exit(app.exec_())
