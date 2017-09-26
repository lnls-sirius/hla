"""Defines a class to control elements from a given class."""
from pydm.PyQt.QtGui import QMainWindow, QTabWidget, QVBoxLayout, \
    QApplication


class BaseMagnetControlWindow(QMainWindow):
    """Base window class to control elements of a given section."""

    DETAIL = 0
    TRIM = 1

    _window = None

    STYLESHEET = """
    """

    def __init__(self, parent=None):
        """Class constructor."""
        super(BaseMagnetControlWindow, self).__init__(parent)
        self.app = QApplication.instance()
        # self.msg = QMessageBox()
        # t = Thread(target=self.msg.exec_)
        # t.start()
        self._setup_ui()
        self.setStyleSheet(self.STYLESHEET)
        # t = Thread(target=self.app.establish_widget_connections, args=[self])
        # t.start()
        self.app.establish_widget_connections(self)
        # self.msg.accept()

    def _setup_ui(self):
        # Create Tabs
        self.tabs = QTabWidget()
        self._addTabs()
        # Set widget layout
        self.setCentralWidget(self.tabs)

    def _addTabs(self): pass

    # def _connectButtons(self, buttons):
    #     for button in buttons:
    #         try:
    #             type_ = button.objectName().split("_")[0]
    #             if type_ in ["label", "trim"]:
    #                 button.clicked.connect(self._openWindow)
    #         except Exception:
    #             pass

    # def _openWindow(self):
    #     sender = self.sender()
    #
    #     name_split = sender.objectName().split("_")
    #     type_ = name_split[0]
    #     ma = name_split[1]
    #
    #     if ma:
    #         if type_ == "label":
    #             self._window = MagnetDetailWindow(ma, self)
    #         elif type_ == "trim":
    #             self._window = MagnetTrimWindow(ma, self)
    #
    #     self._window.show()

    def closeEvent(self, event):
        """Reimplement closed event to close widget connections."""
        # self.app.close_widget_connections(self)
        super().closeEvent(event)
