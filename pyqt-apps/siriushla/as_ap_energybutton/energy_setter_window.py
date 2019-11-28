"""Main window."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QTabWidget, QHBoxLayout, QWidget

from siriushla.widgets import SiriusMainWindow
from siriushla.as_ap_energybutton.energy_button import EnergyButton


class EnergySetterWindow(SiriusMainWindow):
    """."""

    def __init__(self, parent=None):
        """."""
        super().__init__(parent)
        self._setup_ui()
        self.setWindowTitle('Energy Button Application')
        self.setFocusPolicy(Qt.StrongFocus)
        self.setObjectName('ASApp')

    def _setup_ui(self):
        cwid = QTabWidget()

        for section in ('tb', 'bo', 'ts', 'si'):
            widget = EnergyButton(section, parent=cwid)
            cwid.addTab(widget, section.upper())
        self.setCentralWidget(cwid)
        cwid.setObjectName('cwid')
        cwid.setStyleSheet('#cwid{width: 20em; height: 25em;}')


if __name__ == '__main__':
    import sys
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()
    w = EnergySetterWindow()
    w.show()
    sys.exit(app.exec_())
