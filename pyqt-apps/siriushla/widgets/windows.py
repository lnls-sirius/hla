from PyQt5.QtWidgets import QMainWindow, QDialog
from siriushla.SiriusApplication import SiriusApplication


class SiriusMainWindow(QMainWindow):

    def show(self):
        app = SiriusApplication.instance()
        app.establish_widget_connections(self)
        super().show()

    def closeEvent(self, ev):
        app = SiriusApplication.instance()
        app.close_widget_connections(self)
        super().closeEvent(ev)


class SiriusDialog(QDialog):

    def show(self):
        app = SiriusApplication.instance()
        app.establish_widget_connections(self)
        super().show()

    def closeEvent(self, ev):
        app = SiriusApplication.instance()
        app.close_widget_connections(self)
        super().closeEvent(ev)
