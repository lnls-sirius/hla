"""Sirius Windows module."""
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QMainWindow, QDialog, QHBoxLayout


def _create_siriuswindow(qt_type):
    """Create a _SiriusWindow that inherits from qt_type."""
    class _SiriusWindow(qt_type):
        """Auxiliar _SiriusWindow class.

        Parameters
        ----------
        parent : QWidget
            The parent widget for the SiriusMainWindow
        """

        Stylesheet = ""
        FontSizeSS = "* {{font-size: {}px;}}"

        def __init__(self, *args, **kwargs):
            """Init."""
            super().__init__(*args, **kwargs)
            self._font_size = 10
            self._window_size = list()
            self.setStyleSheet(self.Stylesheet + self._font_size_ss())

        def _font_size_ss(self):
            return self.FontSizeSS.format(self._font_size)

        def _increase_font_size(self):
            self._font_size += 1
            self.setStyleSheet(self.Stylesheet + self._font_size_ss())
            self.setFixedSize(self.sizeHint())

        def _decrease_font_size(self):
            if self._font_size == 10:
                return
            self._font_size -= 1
            self.setStyleSheet(self.Stylesheet + self._font_size_ss())
            self.setFixedSize(self.sizeHint())

        def keyPressEvent(self, event):
            """Override keyPressEvent."""
            if event.key() == Qt.Key_Plus:
                return self._increase_font_size()
            elif event.key() == Qt.Key_Minus:
                return self._decrease_font_size()
            super().keyPressEvent(event)

    return _SiriusWindow


SiriusMainWindow = _create_siriuswindow(QMainWindow)
SiriusDialog = _create_siriuswindow(QDialog)


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
