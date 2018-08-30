"""Definition of the Sirius Application class."""
from pydm import PyDMApplication
from pydm.PyQt.QtGui import QWidget, QDialog, QMainWindow, QMessageBox
from pydm.PyQt.QtCore import Qt

from .util import get_window_id


class SiriusApplication(PyDMApplication):
    """Derivation of PyDMApplication used in Sirius HLA."""

    def __init__(self, ui_file=None, command_line_args=[],
                 use_main_window=False, **kwargs):
        """Create an attribute to hold open windows."""
        super().__init__(ui_file=ui_file, command_line_args=command_line_args,
                         use_main_window=use_main_window, **kwargs)
        self._windows = dict()

    def establish_widget_connections(self, widget, propagate=True):
        """Establish widgets connections.

        The `propagate` property defines how widgets are searched.
        When True, super will handle connections. It will try to connect
        all children widgets.
        When False, widgets will be searched recursevely in a breadth first
        manner. The recursion will be cut if the widget is a Window or Dialog.
        """
        if propagate:
            super().establish_widget_connections(widget)
        else:
            # Establish connections of input widget
            self._establish_connections(widget)

            # Look into all its children widgets and then
            # establish its connections
            direct_children = widget.findChildren(
                QWidget, options=Qt.FindDirectChildrenOnly)
            for wid in direct_children:
                if isinstance(wid, (QDialog, QMainWindow)):
                    continue
                self.establish_widget_connections(wid, False)

    def close_widget_connections(self, widget, propagate=True):
        """Close widgets connections.

        The `propagate` property defines how widgets are searched.
        When True, super will handle connections. It will try to disconnect
        all children widgets.
        When False, widgets will be searched recursevely. The recursion will be
        cut if the widget is a Window or Dialog.
        """
        if propagate:
            super().close_widget_connections(widget)
        else:
            # Close connection of input widget
            self._remove_connections(widget)

            # Look into all its children widgets and then
            # close their connections
            direct_children = widget.findChildren(
                QWidget, options=Qt.FindDirectChildrenOnly)
            for wid in direct_children:
                if isinstance(wid, (QDialog, QMainWindow)):
                    continue
                self.close_widget_connections(wid, False)

    def _has_channel(self, widget):
        try:
            if hasattr(widget, 'channels'):
                return True
        except NameError:
            return False

    def _establish_connections(self, widget):
        if self._has_channel(widget):
            for channel in widget.channels():
                self.add_connection(channel)

    def _remove_connections(self, widget):
        try:
            if self._has_channel(widget):
                for channel in widget.channels():
                    self.remove_connection(channel)
        except NameError:
            pass
        # This imitates the solution adopted by pydm to handle protocol errors.
        # Errors like a channel address equal 'None'(type str) are also catched
        # TODO: It would be better if these errors were reported or raised.

    def open_window(self, w_class, parent=None, **kwargs):
        """Open new window.

        A new window will be created if it is not already open. Otherwise, the
        existing window is brought to focus.
        """
        # One top level widget as the parent?
        wid = get_window_id(w_class, **kwargs)
        # if id in self._windows:  # Show existing window
        try:
            self._show(wid)
            self._windows[wid].activateWindow()
        except (KeyError, RuntimeError):
            # KeyError - Window does not exist
            # RuntimeError: wrapped C/C++ object of type x has been deleted
            self._create_and_show(wid, w_class, parent, **kwargs)

    def _show(self, wid):
        if self._windows[wid].isHidden():
            self._windows[wid].show()
        elif self._windows[wid].isMinimized():
            self._windows[wid].showNormal()

    def _create_and_show(self, wid, w_class, parent, **kwargs):
        try:
            window = w_class(parent=parent, **kwargs)
        except ValueError as e:
            QMessageBox.critical(
                self.activeWindow(),
                'Could not open window',
                'Failed to open window: {}'.format(e))
        else:
            self._windows[wid] = window
            self._windows[wid].show()
