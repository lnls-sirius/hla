"""Sirius Windows module."""
from qtpy.QtGui import QKeySequence
from qtpy.QtCore import QEvent
from qtpy.QtWidgets import QMainWindow, QDialog, QHBoxLayout, QApplication


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
        FontSizeSS = "* {{font-size: {}pt;}}"

        def __init__(self, *args, **kwargs):
            """Init."""
            super().__init__(*args, **kwargs)
            self.setFocus(True)
            self.app = QApplication.instance()
            self.installEventFilter(self)

        def _font_size_ss(self):
            return self.FontSizeSS.format(self.app.font().pointSize())

        def keyPressEvent(self, event):
            """Override keyPressEvent."""
            font = self.app.font()
            if event.matches(QKeySequence.ZoomIn):
                font.setPointSize(font.pointSize() + 1)
                self.app.setFont(font)
            elif event.matches(QKeySequence.ZoomOut) and font.pointSize() > 9:
                font.setPointSize(font.pointSize() - 1)
                self.app.setFont(font)
            super().keyPressEvent(event)

        def eventFilter(self, obj, event):
            if event.type() == QEvent.ApplicationFontChange:
                self.ensurePolished()
                self.setStyleSheet(self.Stylesheet + self._font_size_ss())
                self.setFixedSize(self.sizeHint())
            return False

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
