"""Modulet that defines the window class that control pulsed mangets."""
from pydm import PyDMApplication
from pydm.PyQt.QtCore import Qt, pyqtSlot
from pydm.PyQt.QtGui import QMainWindow, QWidget, QVBoxLayout, QTabWidget

from siriuspy.search import MASearch
from siriushla.as_pm_control.PulsedMagnetWidget import PulsedMagnetWidget
from siriushla.as_pm_control.PulsedMagnetDetailWidget \
    import PulsedMagnetDetailWidget


class PulsedMagnetControlWindow(QMainWindow):
    """Window to control pulsed magnets."""

    Instance = None

    StyleSheet = """
    """

    def __init__(self, parent=None):
        """Constructor."""
        if PulsedMagnetControlWindow.Instance is not None:
            return PulsedMagnetControlWindow.Instance

        self.app = PyDMApplication.instance()

        super().__init__(parent)
        self._setup_ui()
        self.setStyleSheet(PulsedMagnetControlWindow.StyleSheet)

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.app.establish_widget_connections(self)

        PulsedMagnetControlWindow.Instance = self

    def _setup_ui(self):
        self.main_widget = QTabWidget(self)
        self.main_widget.layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_widget.layout)
        self.setCentralWidget(self.main_widget)
        self.setWindowTitle("Pulsed magnets control window")
        self.setFocus()

        self.main_widget.addTab(self._make_tab_widget("TB"), "LTB")
        self.main_widget.addTab(self._make_tab_widget("BO"), "Booster")
        self.main_widget.addTab(self._make_tab_widget("TS"), "LTS")
        self.main_widget.addTab(self._make_tab_widget("SI"), "Storage Ring")

        self._connect_buttons()

    def _make_tab_widget(self, section):
        widget = QWidget(self)
        widget.layout = QVBoxLayout()

        magnets = MASearch.get_manames(
            {"section": section, "discipline": "PM"})

        header = True
        for magnet in magnets:
            ma_widget = PulsedMagnetWidget(magnet, header, self)
            widget.layout.addWidget(ma_widget)
            header &= False

        widget.layout.addStretch()

        widget.setLayout(widget.layout)
        return widget

    def _connect_buttons(self):
        """Return buttons in the PulsedMagnetWidgets."""
        widgets = self.main_widget.findChildren(PulsedMagnetWidget)
        for widget in widgets:
            button = widget.get_magnet_button()
            button.clicked.connect(self._openMagnetDetailWindow)

    @pyqtSlot()
    def _openMagnetDetailWindow(self):
        sender = self.sender()
        maname = sender.text()
        self.w = QMainWindow(self)
        self.w.setCentralWidget(PulsedMagnetDetailWidget(maname, self.w))
        self.app.establish_widget_connections(self.w)
        self.w.show()

    def closeEvent(self, event):
        """Reimplement closed event to close widget connections."""
        self.app.close_widget_connections(self)
        PulsedMagnetControlWindow.Instance = None
        super().closeEvent(event)


if __name__ == "__main__":
    import sys

    app = PyDMApplication(None, sys.argv)
    w = PulsedMagnetControlWindow()
    w.show()
    sys.exit(app.exec_())
