"""Definition of the Sirius Application class."""
from pydm import PyDMApplication
from qtpy.QtWidgets import QMessageBox

from .util import get_window_id, set_style


class SiriusApplication(PyDMApplication):
    """Derivation of PyDMApplication used in Sirius HLA."""

    def __init__(self, ui_file=None, command_line_args=[],
                 use_main_window=False, **kwargs):
        """Create an attribute to hold open windows."""
        super().__init__(ui_file=ui_file, command_line_args=command_line_args,
                         use_main_window=use_main_window, **kwargs)
        font = self.font()
        width, _ = self._get_desktop_geometry()
        if width > 1920:
            font.setPointSize(12)
        elif width == 1920:
            font.setPointSize(10)
        else:
            font.setPointSize(7)
        self.setFont(font)
        set_style(self)
        self._windows = dict()

    def open_window(self, w_class, parent=None, **kwargs):
        """Open new window.

        A new window will be created if it is not already open. Otherwise, the
        existing window is brought to focus.
        """
        # One top level widget as the parent?
        wid = get_window_id(w_class, **kwargs)
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

    def _get_desktop_geometry(self):
        screen = self.primaryScreen()
        screenGeometry = screen.geometry()
        return screenGeometry.width(), screenGeometry.height()
