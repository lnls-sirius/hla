from PyQt5.QtWidgets import QMainWindow, QDialog
from siriushla.SiriusApplication import SiriusApplication


class SiriusMainWindow(QMainWindow):

    def closeEvent(self, ev):
        app = SiriusApplication.instance()
        app.close_widget_connections(self)
        super().closeEvent(ev)


class SiriusDialog(QDialog):

    def closeEvent(self, ev):
        app = SiriusApplication.instance()
        app.close_widget_connections(self)
        super().closeEvent(ev)
