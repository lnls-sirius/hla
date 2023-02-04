"""Definition of the Sirius Application class."""
import sys
import os
import time
import traceback
import logging as _log
from io import StringIO
from qtpy.QtWidgets import QMessageBox
from pydm import PyDMApplication, data_plugins

from .util import get_window_id, set_style


# Create log file
LOGFILE = '/tmp/sirius-hla.log'
try:
    open(LOGFILE, 'a').close()
    os.chmod(LOGFILE, 0o666)
except (OSError, PermissionError):
    pass


# Configure Logging
fmt = '%(levelname)7s | %(asctime)s | ' +\
      '%(module)15s.%(funcName)-20s[%(lineno)4d] ::: %(message)s'
_log.basicConfig(
    format=fmt, datefmt='%F %T', level=_log.INFO,
    filename=LOGFILE, filemode='a')


# https://riverbankcomputing.com/pipermail/pyqt/2009-May/022961.html
def excepthook(exctype, excvalue, tracebackobj):
    """
    Global function to catch unhandled exceptions.

    @param exctype exception type
    @param excvalue exception value
    @param tracebackobj traceback object
    """
    app = SiriusApplication.instance()
    if app is None:
        app = SiriusApplication(None, sys.argv)

    separator = '-' * 120 + '\n'
    notice = \
        'An unhandled exception occurred. Please report the problem '\
        'via email to <{}>.\nA log has {{}}been written to "{}".\n\n'\
        'Error information:\n'.format("ana.clara@lnls.br", LOGFILE)
    timestring = time.strftime("%Y-%m-%d, %H:%M:%S") + '\n'

    tbinfofile = StringIO()
    traceback.print_tb(tracebackobj, None, tbinfofile)
    tbinfofile.seek(0)
    tbinfo = tbinfofile.read()

    errmsg = '%s: \n%s\n' % (str(exctype), str(excvalue))
    sections = [timestring, errmsg, tbinfo]
    msg = separator.join(sections)
    try:
        with open(LOGFILE, 'a') as fil:
            fil.write('\n' + msg + '\n')
        try:
            os.chmod(LOGFILE, 0o666)
        except OSError:
            pass
    except PermissionError:
        notice = notice.format('NOT ')
    else:
        notice = notice.format('')
    errorbox = QMessageBox()
    errorbox.setText(notice)
    errorbox.setInformativeText(msg)
    errorbox.setIcon(QMessageBox.Critical)
    errorbox.setWindowTitle('Error')
    errorbox.setStyleSheet(
        '#qt_msgbox_informativelabel {min-width: 40em;}')
    errorbox.exec_()


sys.excepthook = excepthook


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

    def open_window(self, w_class, position=(0, 20), size='default', parent=None, **kwargs):
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
            self._create_and_show(wid, w_class, position, size, parent, **kwargs)

    def _show(self, wid):
        if self._windows[wid].isHidden():
            self._windows[wid].show()
        elif self._windows[wid].isMinimized():
            self._windows[wid].showNormal()

    def _create_and_show(self, wid, w_class, position, size, parent, **kwargs):
        with data_plugins.connection_queue():
            window = w_class(parent=parent, **kwargs)
            self._windows[wid] = window
            self._windows[wid].move(position[0], position[1])
            if size != 'default':
                if size == 'maximized':
                    self._windows[wid].showMaximized()
                elif size == 'minimized':
                    self._windows[wid].showMinimized()
                else:
                    self._windows[wid].resize(size[0], size[1])
            else:
                self._windows[wid].show()

    def _get_desktop_geometry(self):
        screen = self.primaryScreen()
        screenGeometry = screen.geometry()
        return screenGeometry.width(), screenGeometry.height()
