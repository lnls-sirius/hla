"""Sirius Windows module."""
from PyQt5.QtWidgets import QMainWindow, QDialog
from siriushla.sirius_application import SiriusApplication


class SiriusMainWindow(QMainWindow):
    """
    SiriusMainWindow class.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the SiriusMainWindow
    disconnect_when_hidden: bool
        If True (default), close widgets connections when window is hidden and
        establish widgets connections when shown. Else, establish connections
        when first shown and close connections only on closeEvent.
    """

    def __init__(self, parent=None, disconnect_when_hidden=True, **kwargs):
        """Reimplement constructor to include _is_connected flag."""
        self._is_connected = False
        self._disconnect_when_hidden = disconnect_when_hidden
        super().__init__(parent, **kwargs)

    def showEvent(self, ev):
        """Reimplement showEvent to establish widget connections."""
        if self._disconnect_when_hidden or not self._is_connected:
            app = SiriusApplication.instance()
            app.establish_widget_connections(self, False)
            self._is_connected = True
        super().showEvent(ev)

    def hideEvent(self, ev):
        """Reimplement hideEvent to close widget connections."""
        if self._disconnect_when_hidden:
            app = SiriusApplication.instance()
            app.close_widget_connections(self, False)
        super().hideEvent(ev)

    def closeEvent(self, ev):
        """Reimplement closeEvent to close widget connections."""
        if not self._disconnect_when_hidden:
            app = SiriusApplication.instance()
            app.close_widget_connections(self, False)
        super().closeEvent(ev)


class SiriusDialog(QDialog):
    """
    SiriusDialog class.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the SiriusMainWindow
    disconnect_when_hidden: bool
        If True (default), close widgets connections when window is hidden and
        establish widgets connections when shown. Else, establish connections
        when first shown and close connections only on closeEvent.
    """

    def __init__(self, parent=None, disconnect_when_hidden=True, **kwargs):
        """Reimplement constructor to include _is_connected flag."""
        self._is_connected = False
        self._disconnect_when_hidden = disconnect_when_hidden
        super().__init__(parent, **kwargs)

    def showEvent(self, ev):
        """Reimplement showEvent to establish widget connections."""
        if self._disconnect_when_hidden or not self._is_connected:
            app = SiriusApplication.instance()
            app.establish_widget_connections(self, False)
            self._is_connected = True
        super().showEvent(ev)

    def hideEvent(self, ev):
        """Reimplement hideEvent to close widget connections."""
        if self._disconnect_when_hidden:
            app = SiriusApplication.instance()
            app.close_widget_connections(self, False)
        super().hideEvent(ev)

    def closeEvent(self, ev):
        """Reimplement closeEvent to close widget connections."""
        if not self._disconnect_when_hidden:
            app = SiriusApplication.instance()
            app.close_widget_connections(self, False)
        super().closeEvent(ev)
