from PyQt5.QtWidgets import QMainWindow, QDialog
from siriushla.sirius_application import SiriusApplication


class SiriusMainWindow(QMainWindow):

    def closeEvent(self, ev):
        app = SiriusApplication.instance()
        app.close_widget_connections(self, False)
        super().closeEvent(ev)


class SiriusDialog(QDialog):

    def closeEvent(self, ev):
        app = SiriusApplication.instance()
        app.close_widget_connections(self, False)
        super().closeEvent(ev)
