"""
CustomToolbar
    Class for embedding a matplotlib toolbar in a Qt GUI.

Afonso Haruo Carnielli Mukai (FAC - LNLS)

2013-12-11: v0.1
"""

import matplotlib.backends.backend_qt5agg as _backend


ACTIONS_TO_DISABLE = ['back', 'forward', 'subplots', 'customize']


class CustomToolbar(_backend.NavigationToolbar2QT):
    def __init__(self, figure, parent):
        super(CustomToolbar, self).__init__(figure, parent)
        self._disable_actions()
        self._figure = figure
        self._status_changed = False

    def home(self, *args):
        self._restore_status()
        result =  _backend.NavigationToolbar2QT.home(self, *args)
        self._figure.update_plot()
        return result

    def press_pan(self, event):
        self._save_status()
        self._figure.xy_autoscale = False
        return _backend.NavigationToolbar2QT.press_pan(self, event)

    def press_zoom(self, event):
        self._save_status()
        self._figure.xy_autoscale = False
        return _backend.NavigationToolbar2QT.press_zoom(self, event)

    def _save_status(self):
        if not self._status_changed:
            self._x_autoscale = self._figure.x_autoscale
            self._y_autoscale = self._figure.y_autoscale
            self._status_changed = True

    def _restore_status(self):
        if self._status_changed:
            self._figure.x_autoscale = self._x_autoscale
            self._figure.y_autoscale = self._y_autoscale
            self._status_changed = False

    def _disable_actions(self):
        actions = self.actions()
        for action in actions:
            if str.lower(str(action.text())) in ACTIONS_TO_DISABLE:
                self.removeAction(action)
