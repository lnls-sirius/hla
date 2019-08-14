"""Modulet that defines the window class that control pulsed mangets."""
import qtawesome as qta
from pydm import PyDMApplication
from qtpy.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from siriuspy.search import MASearch
from siriushla.widgets import SiriusMainWindow
from siriushla.as_ps_control.PSWidget import PulsedMAWidget
from siriushla.as_pm_control.PulsedMagnetDetailWindow \
    import PulsedMagnetDetailWindow
from siriushla.util import connect_window


class PulsedMagnetControlWindow(SiriusMainWindow):
    """Window to control pulsed magnets."""

    StyleSheet = """
    """

    def __init__(self, parent=None, is_main=True, section=None):
        """Constructor."""
        super().__init__(parent)
        self._is_main = is_main
        self._section = section
        self.setObjectName(self._section+'App')
        self._setup_ui()
        self.setStyleSheet(PulsedMagnetControlWindow.StyleSheet)
        self.setCentralWidget(self.main_widget)
        self.setWindowTitle(section.upper() + ' Pulsed Magnets Control Window')
        self.setWindowIcon(qta.icon('mdi.current-ac', color='#969696'))
        self.setFocus()

    def _setup_ui(self):
        if self._is_main:
            self.main_widget = QTabWidget(self)
            self.main_widget.layout = QVBoxLayout()
            self.main_widget.setLayout(self.main_widget.layout)

            self.main_widget.addTab(self._make_tab_widget('TB'), 'TB')
            self.main_widget.addTab(self._make_tab_widget('BO'), 'Booster')
            self.main_widget.addTab(self._make_tab_widget('TS'), 'TS')
            self.main_widget.addTab(self._make_tab_widget('SI'),
                                    'Storage Ring')
            self._connect_buttons()
        elif self._section is not None:
            if self._section == 'TB':
                self.main_widget = self._make_tab_widget('TB')
            elif self._section == 'BO':
                self.main_widget = self._make_tab_widget('BO')
            elif self._section == 'TS':
                self.main_widget = self._make_tab_widget('TS')
            elif self._section == 'SI':
                self.main_widget = self._make_tab_widget('SI')
            self._connect_buttons()
        else:
            raise ValueError('Invalid \'section\' argument!')

    def _make_tab_widget(self, section):
        widget = QWidget(self)
        widget.layout = QVBoxLayout()

        magnets = MASearch.get_manames({'sec': section, 'dis': 'PM'})

        header = True
        for magnet in magnets:
            ma_widget = PulsedMAWidget(magnet, header, self)
            widget.layout.addWidget(ma_widget)
            header &= False

        widget.layout.addStretch()

        widget.setLayout(widget.layout)
        return widget

    def _connect_buttons(self):
        """Return buttons in the PulsedMAWidgets."""
        widgets = self.main_widget.findChildren(PulsedMAWidget)
        for widget in widgets:
            maname = widget.psname
            button = widget.get_detail_button()
            connect_window(button, PulsedMagnetDetailWindow,
                           parent=self, maname=maname)


if __name__ == "__main__":
    import sys

    app = PyDMApplication(None, sys.argv)
    w = PulsedMagnetControlWindow()
    w.show()
    sys.exit(app.exec_())
