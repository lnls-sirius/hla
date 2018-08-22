"""Sirius Windows module."""
from PyQt5.QtWidgets import QMainWindow, QDialog
from siriushla.sirius_application import SiriusApplication


def _create_siriuswindow(qt_type):
    """Create a _SiriusWindow that inherits from qt_type."""
    class _SiriusWindow(qt_type):
        """
        Auxiliar _SiriusWindow class.

        Parameters
        ----------
        parent : QWidget
            The parent widget for the SiriusMainWindow
        disconnect_when_hidden: bool
            If True (default), close widgets connections when window is hidden
            and establish widgets connections when shown. Else, establish
            connections when initialize and close connections only when closed.
        """

        def __init__(self, parent=None, disconnect_when_hidden=True, **kwargs):
            """Class constructor."""
            super().__init__(parent, **kwargs)
            self._app = SiriusApplication.instance()
            self._is_connected = False
            self._disconnect_when_hidden = disconnect_when_hidden

        def showEvent(self, ev):
            """Reimplement showEvent to establish widget connections."""
            if self._disconnect_when_hidden or not self._is_connected:
                self._app.establish_widget_connections(self, False)
                self._is_connected = True
            super().showEvent(ev)

        def hideEvent(self, ev):
            """Reimplement hideEvent to close widget connections."""
            if self._disconnect_when_hidden and self._is_connected:
                self._app.close_widget_connections(self, False)
                self._is_connected = False
            super().hideEvent(ev)

        def closeEvent(self, ev):
            """Reimplement closeEvent to close widget connections."""
            if self._is_connected:
                self._app.close_widget_connections(self, False)
                self._is_connected = False
            super().closeEvent(ev)

    return _SiriusWindow


SiriusMainWindow = _create_siriuswindow(QMainWindow)
SiriusDialog = _create_siriuswindow(QDialog)
