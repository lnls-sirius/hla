"""Modulet that defines the window class that control pulsed mangets."""

from qtpy.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from siriuspy.search import MASearch
from siriushla.widgets import SiriusMainWindow
from siriushla.as_ps_control.SummaryWidgets import SummaryWidget, SummaryHeader
from siriushla.util import connect_window
from .PulsedMagnetDetailWindow import PulsedMagnetDetailWindow


class PulsedMagnetControlWindow(SiriusMainWindow):
    """Window to control pulsed magnets."""

    def __init__(self, parent=None, is_main=True, section=None):
        """Constructor."""
        super().__init__(parent)
        self._is_main = is_main
        self._section = section
        self.setObjectName(self._section+'App')
        self.setWindowTitle(section.upper() + ' Pulsed Magnets Control Window')
        self.setWindowIcon(qta.icon('mdi.current-ac', color='#969696'))
        self._setup_ui()
        self.setCentralWidget(self.main_widget)
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
        lay = QVBoxLayout(widget)

        magnets = MASearch.get_manames({'sec': section, 'dis': 'PM'})

        visible_props = {'detail', 'state', 'intlk', 'reset',
                         'setpoint', 'monitor', 'strength_sp', 'strength_mon'}

        lay.addWidget(SummaryHeader(magnets[0], visible_props, self))
        for magnet in magnets:
            ma_widget = SummaryWidget(magnet, visible_props, self)
            lay.addWidget(ma_widget)

        lay.addStretch()
        return widget

    def _connect_buttons(self):
        """Connect buttons in the SummaryWidgets."""
        widgets = self.main_widget.findChildren(SummaryWidget)
        for widget in widgets:
            maname = widget.devname
            bt = widget.get_detail_button()
            connect_window(bt, PulsedMagnetDetailWindow, self, maname=maname)


if __name__ == "__main__":
    import sys
    from sirius_application import SiriusApplication
    app = SiriusApplication()
    w = PulsedMagnetControlWindow()
    w.show()
    sys.exit(app.exec_())
