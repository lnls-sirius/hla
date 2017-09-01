"""Define a window with detailed controls for a given magnet."""
from pydm.PyQt.QtGui import QApplication, QDialog, QVBoxLayout
from .detail_widget.DetailWidgetFactory import DetailWidgetFactory


class MagnetDetailWindow(QDialog):
    """Window to control a detailed widget."""

    STYLESHEET = """
    """

    def __init__(self, maname, parent=None):
        """Init UI."""
        super(MagnetDetailWindow, self).__init__(parent)
        self.app = QApplication.instance()

        self._ma = maname

        self._setup_ui()
        self.setStyleSheet(self.STYLESHEET)

        # self.app.establish_widget_connections(self)

    def _setup_ui(self):
        # Set window layout
        self.layout = QVBoxLayout()

        self.widget = DetailWidgetFactory.factory(self._ma, self)
        self.layout.addWidget(self.widget)

        self.setWindowTitle(self._ma + ' Detail')
        self.setLayout(self.layout)

    def showEvent(self, event):
        self.app.establish_widget_connections(self)
        super().showEvent(event)

    def closeEvent(self, event):
        """Override closeEvent in order to close iwdget connections."""
        self.app.close_widget_connections(self)


if __name__ == '__main__':
    import sys
    from pydm import PyDMApplication
    app = PyDMApplication(None, sys.argv)
    window = MagnetDetailWindow("SI-Fam:MA-QFA")
    window.show()
    app.exec_()
