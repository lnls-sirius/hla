"""Sirius Windows module."""
from qtpy.QtWidgets import QMainWindow, QDialog, QHBoxLayout


class SiriusMainWindow(QMainWindow):
    pass


class SiriusDialog(QDialog):
    pass


def create_window_from_widget(
                WidgetClass, name=None, size=None, is_main=False):

    if is_main:
        class MyWindow(SiriusMainWindow):

            def __init__(self, parent, *args, **kwargs):
                super().__init__(parent)
                wid = WidgetClass(self, *args, **kwargs)
                self.setCentralWidget(wid)
                if size:
                    self.resize(*size)
    else:
        class MyWindow(SiriusDialog):

            def __init__(self, parent, *args, **kwargs):
                super().__init__(parent)
                hbl = QHBoxLayout(self)
                wid = WidgetClass(self, *args, **kwargs)
                hbl.addWidget(wid)
                if size:
                    self.resize(*size)

    if name:
        MyWindow.__name__ = name
    return MyWindow
