"""Util module."""
import os as _os
import time as _time
import pathlib as _pathlib
import subprocess as _subprocess
from functools import partial as _part

from qtpy.QtCore import QFile as _QFile, Signal as _Signal, QThread as _QThread
from qtpy.QtWidgets import QPushButton, QAction, QApplication, QDialog, \
    QHBoxLayout, QLabel
from pydm.utilities.stylesheet import _get_style_data as pydm_get_style_data
import siriushla.resources as _resources


def set_style(app, force_default=False):
    """Implement sirius-hla-style.css as default Qt resource file HLA."""
    if force_default:
        stream = _QFile(':/sirius-hla-style.css')
    else:
        fname = str(_os.path.join(_pathlib.Path.home(),
                    '.sirius-hla-style.css'))
        fpath = _pathlib.Path(fname)
        if not fpath.is_file():
            fname = ':/sirius-hla-style.css'
        stream = _QFile(fname)
    if stream.open(_QFile.ReadOnly):
        style = str(stream.readAll(), 'utf-8')
        stream.close()
        pydm_style = pydm_get_style_data()
        app.setStyleSheet(style + '\n' + pydm_style)
    else:
        print('set_style: "{0}": {1}'.format(fname, stream.errorString()))
    _resources.qCleanupResources()


def get_window_id(w_class, **kwargs):
    """Serialize parameters."""
    return ''.join([w_class.__name__, str(kwargs)])


def connect_window(widget, w_class, parent, **kwargs):
    """Connect a widget to a window."""
    signal = get_appropriate_signal(widget)
    app = QApplication.instance()
    widget.w_class = w_class
    widget.kwargs = kwargs
    signal.connect(lambda: app.open_window(
        app.sender().w_class, parent=parent, **app.sender().kwargs))


def connect_newprocess(widget, cmd, is_window=True, parent=None, **kwargs):
    """Execute a child program in a new process."""
    signal = get_appropriate_signal(widget)
    signal.connect(lambda: run_newprocess(cmd, **kwargs))
    if is_window:
        signal.connect(_part(_show_loading_message, parent, cmd))


def check_process(cmd, is_window=True):
    # Maximize the window if it exists, else create a new one
    scmd = (_subprocess.list2cmdline(cmd) if isinstance(cmd, list) else cmd)
    window = ''
    pid = _subprocess.run(
        "ps -A -o pid,command= | grep \"[" + scmd[0] + "]" + scmd[1:] +
        "\" | xargs | cut -f1 -d\" \" -",
        stdin=_subprocess.PIPE, shell=True, stdout=_subprocess.PIPE,
        stderr=_subprocess.DEVNULL,
        check=True).stdout.decode('UTF-8').strip('\n')
    if pid and is_window:
        window = _subprocess.run(
            "xdotool search --pid "+pid+" | tail -1",
            stdin=_subprocess.PIPE, shell=True, stdout=_subprocess.PIPE,
            stderr=_subprocess.DEVNULL, check=True).stdout.decode('UTF-8')
    return pid, window


def run_newprocess(cmd, is_window=True, **kwargs):
    pid, window = check_process(cmd, is_window=is_window)
    if window:
        _subprocess.run("xdotool windowactivate "+window,
                        stdin=_subprocess.PIPE, shell=True)
    elif not pid:
        _subprocess.Popen(cmd, **kwargs)


def get_appropriate_color(section='SI'):
    dic = {
        'AS': '#d7ccc8',
        'LI': '#ffcdd2',
        'TB': '#f8bbd0',
        'BO': '#c8e6c9',
        'TS': '#b2ebf2',
        'SI': '#bbdefb',
    }
    return dic[section]


def get_appropriate_signal(widget):
    if isinstance(widget, QAction):
        signal = widget.triggered
    elif isinstance(widget, QPushButton):
        signal = widget.clicked
    else:
        raise AttributeError("Undefined signal for {}".format(widget))
    return signal


def _show_loading_message(parent, cmd):
    th = LoadingThread(parent, cmd=cmd)
    message = LoadingDialog(parent, 'Wait', '<h3>Loading Window</h3>')
    th.openmessage.connect(message.show)
    th.closemessage.connect(message.close)
    th.start()


class LoadingDialog(QDialog):

    def __init__(self, parent, title, message):
        super().__init__(parent=parent)
        self.setWindowTitle(title)
        lay = QHBoxLayout(self)
        lay.addWidget(QLabel(message))


class LoadingThread(_QThread):

    openmessage = _Signal()
    closemessage = _Signal()

    def __init__(self, parent=None, cmd=''):
        super().__init__(parent=parent)
        self.cmd = cmd

    def run(self):
        self.openmessage.emit()
        wind = ''
        while not wind:
            _, wind = check_process(self.cmd)
            _time.sleep(0.01)
        self.closemessage.emit()
