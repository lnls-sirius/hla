"""Define a window with detailed controls for a given magnet."""
from pydm import PyDMApplication
from siriushla.widgets import SiriusMainWindow
from .detail_widget.DetailWidgetFactory import DetailWidgetFactory


class MagnetDetailWindow(SiriusMainWindow):
    """Window to control a detailed widget."""

    STYLESHEET = """
    """

    def __init__(self, maname, parent=None):
        """Init UI."""
        super(MagnetDetailWindow, self).__init__(parent)
        self.app = PyDMApplication.instance()

        self._ma = maname

        self._setup_ui()
        self.setStyleSheet(self.STYLESHEET)
        # self.app.establish_widget_connections(self)

    def _setup_ui(self):
        # Set window layout
        self.setWindowTitle(self._ma)
        self.widget = DetailWidgetFactory.factory(self._ma, self)
        self.setCentralWidget(self.widget)


if __name__ == '__main__':
    import sys
    app = PyDMApplication(None, sys.argv)
    window = MagnetDetailWindow("SI-Fam:MA-QFA")
    window.show()
    app.exec_()
