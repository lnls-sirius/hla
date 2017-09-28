"""Define a class to manage windows."""
from collections import namedtuple
from pydm import PyDMApplication

class WindowManager:
    """This class manages opening windows.

    Responsibilities:
        - always open one instance of a window (w_id)
        - if window is open activate it
    """

    Window = namedtuple("Window", "id, w_class, kwargs")

    def __init__(self):
        self._window_reg = dict()
        self._windows = dict()

    def register_window(self, w_id, w_class, **kwargs):
        """Register window parameters."""
        self._window_reg[w_id] = self.Window(w_id, w_class, kwargs)

    def open_window(self, w_id):
        if w_id not in self._windows:
            # try:
            w_class = self._window_reg[w_id].w_class
            kwargs = self._window_reg[w_id].kwargs
            self._windows[w_id] = w_class(**kwargs)
            # except Exception as e:
                # print("{}".format(e))

        self._windows[w_id].show()
        self._windows[w_id].activateWindow()

    def open_widget(self, w_id, w_class, **kwargs):
        if w_id not in self._windows:
            try:
                if "parent" in kwargs:
                    self._windows[w_id] = QMainWindow(parent=kwargs["parent"])
                else:
                    self._windows[w_id] = QMainWindow()
            except Exception as e:
                print("{}".format(e))

            self._windows[w_id].setCentralWidget(w_class(**kwargs))
            PyDMApplication.instance().establish_widget_connections(
                self._windows[w_id])

        self._windows[w_id].show()
        self._windows[w_id].activateWindow()
