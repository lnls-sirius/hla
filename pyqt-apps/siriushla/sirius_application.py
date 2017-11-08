"""Definition of the Sirius Application class."""
from pydm import PyDMApplication
from .util import get_window_id


class SiriusApplication(PyDMApplication):
    """Derivation of PyDMApplication used in Sirius HLA."""

    def __init__(self, ui_file=None, command_line_args=[], **kwargs):
        """Create an attribute to hold open windows."""
        super().__init__(ui_file, command_line_args, kwargs)
        self._windows = dict()

    def open_window(self, w_class, parent=None, **kwargs):
        """Open new window.

        A new window will be created if it is not already open. Otherwise, the
        existing window is brought to focus.
        """
        # One top level widget as the parent?
        id = get_window_id(w_class, **kwargs)
        if id in self._windows:  # Show existing window
            if self._windows[id].isHidden():
                self.establish_widget_connections(self._windows[id])
                self._windows[id].show()
            elif self._windows[id].isMinimized():
                self._windows[id].showNormal()
            self._windows[id].activateWindow()
        else:  # Create new window
            wid = w_class(parent=parent, **kwargs)
            self._windows[id] = wid
            self.establish_widget_connections(wid)
            self._windows[id].show()
