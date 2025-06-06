"""Util module."""
import os as _os
import subprocess as _subprocess
import time as _time
from functools import partial as _part

import qtawesome as qta
from pydm.utilities.stylesheet import _get_style_data as pydm_get_style_data
from qtpy.QtCore import QFile as _QFile, QThread as _QThread, Signal as _Signal
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QAction, QApplication, QDialog, QHBoxLayout, \
    QLabel, QPushButton

THREAD = None


def get_package_version():
    """Return siriushla version string."""
    from siriushla import __version__ as version
    return version


def get_monitor_icon(icon_name, color=None):
    color = color or QColor(50, 50, 50)
    return qta.icon(icon_name, 'mdi.monitor', options=[
        dict(scale_factor=0.8, color=color, offset=(0.0, -0.07)),
        dict(scale_factor=1.4, color=color, offset=(0.0, 0.00))])


def set_style(app):
    """Implement sirius-hla-style.css as default Qt resource file HLA."""
    abspath = _os.path.abspath(_os.path.dirname(__file__))
    fname = _os.path.join(abspath, 'sirius-hla-style.css')
    stream = _QFile(fname)
    if stream.open(_QFile.ReadOnly):
        style = str(stream.readAll(), 'utf-8')
        stream.close()
        pydm_style = pydm_get_style_data()
        app.setStyleSheet(style + '\n' + pydm_style)
    else:
        print('set_style: "{0}": {1}'.format(fname, stream.errorString()))


def get_window_id(w_class, **kwargs):
    """Serialize parameters."""
    return ''.join([w_class.__name__, str(kwargs)])


def connect_window(widget, w_class, parent, signal=None, **kwargs):
    """Connect a widget to a window."""
    signal = signal or get_appropriate_signal(widget)
    app = QApplication.instance()
    widget.w_class = w_class
    widget.kwargs = kwargs
    signal.connect(lambda: app.open_window(
        app.sender().w_class, parent=parent, **app.sender().kwargs))


def connect_newprocess(widget, cmd, is_window=True, parent=None, signal=None,
                       is_pydm=False, **kwargs):
    """Execute a child program in a new process."""
    signal = signal or get_appropriate_signal(widget)
    signal.connect(lambda: run_newprocess(cmd, is_pydm=is_pydm, **kwargs))
    if is_window:
        signal.connect(_part(_show_loading_message, parent, cmd, is_pydm))


def check_process(cmd, is_window=True, is_pydm=False):
    # Maximize the window if it exists, else create a new one
    scmd = (_subprocess.list2cmdline(cmd) if isinstance(cmd, list) else cmd)
    window = ''
    pid = ''
    if is_pydm:
        cmdsplit = scmd.split()
        _, _, sec, _, app = cmdsplit[0].split('-')[:5]
        options = cmdsplit[-1] if len(cmdsplit) > 1 else ''
        app = app.split('.py')[0]
        scmd = ('ps hx -o pid,command= | grep [s]iriushlacon' +
                f' | grep {app} | grep "/bin/pydm"')
        if options:
            scmd += f' | grep "{options}"'
        if sec in {'bo', 'tb', 'ts', 'si'}:
            scmd += ' | grep ' + sec.upper()
        elif sec == 'as':
            name1 = _os.path.join(app, 'main')
            name2 = _os.path.join(app, app)
            scmd += f' | grep "{name1}\\|{name2}"'
        infos = _subprocess.getoutput(scmd).split('\n')
        for info in infos:
            if not info:
                continue
            pidc, comm = info.split()[:2]
            window = check_window_by_pid(pidc, comm)
            if window:
                pid = pidc
                break
    else:
        sess = _subprocess.getoutput(
            'ps -A -o sess,args | grep "[p]s -A -o sess,args" | xargs '
            '| cut -f1 -d " " -')
        info = _subprocess.getoutput(
            'ps h -A -o pid,sess,command= | grep "['+scmd[0]+']' +
            scmd[1:]+'" | grep '+sess)
        if info and is_window:
            info = info.split('\n')[0]
            pid, _, comm = info.split()[:3]
            window = check_window_by_pid(pid, comm)
        if pid and not window:
            infos = _subprocess.getoutput(
                'ps h -o pid,command= --ppid ' + pid).split('\n')
            for info in infos:
                if not info:
                    continue
                pidc, comm = info.split()[:2]
                window = check_window_by_pid(pidc, comm)
                if window:
                    pid = pidc
                    break
    return pid, window


def check_window_by_pid(pid, comm):
    if 'edm' in comm:
        wind = _subprocess.getoutput('wmctrl -lpx | grep edm | grep SIRIUS')
    else:
        wind = _subprocess.getoutput('wmctrl -lpx | grep ' + pid)
    if not wind:
        return ''
    window = wind.split('\n')[0].split()[0]
    return window


def run_newprocess(cmd, is_window=True, is_pydm=False, **kwargs):
    pid, window = check_process(cmd, is_window=is_window, is_pydm=is_pydm)
    if window:
        _subprocess.run(
            "wmctrl -iR " + window, stdin=_subprocess.PIPE, shell=True)
    elif not pid:
        _subprocess.Popen(cmd, **kwargs)


def get_appropriate_color(section='SI'):
    dic = {
        'AS': '#d7ccc8',
        'LI': '#f3d2d5',
        'TB': '#fcaac7',
        'BO': '#c8e6c9',
        'TS': '#b2ebf2',
        'SI': '#56aeff',
        'ID': '#bbbbdd',
        'IT': '#ffece6',
    }
    if section not in dic:
        return '#efefef'
    return dic[section]


def get_appropriate_signal(widget):
    if isinstance(widget, QAction):
        signal = widget.triggered
    elif isinstance(widget, QPushButton):
        signal = widget.clicked
    else:
        raise AttributeError("Undefined signal for {}".format(widget))
    return signal


def _show_loading_message(parent, cmd, is_pydm=False):
    global THREAD
    THREAD = LoadingThread(parent, cmd=cmd, is_pydm=is_pydm)
    message = LoadingDialog(parent, 'Wait', '<h3>Loading Window</h3>')
    THREAD.openmessage.connect(message.show)
    THREAD.closemessage.connect(message.close)
    THREAD.start()


class LoadingDialog(QDialog):

    def __init__(self, parent, title, message):
        super().__init__(parent=parent)
        self.setWindowTitle(title)
        lay = QHBoxLayout(self)
        lay.addWidget(QLabel(message))


class LoadingThread(_QThread):

    openmessage = _Signal()
    closemessage = _Signal()

    def __init__(self, parent=None, cmd='', is_pydm=False):
        super().__init__(parent=parent)
        self.cmd = cmd
        self.is_pydm = is_pydm

    def run(self):
        self.openmessage.emit()
        wind = ''
        for _ in range(500):
            _, wind = check_process(self.cmd, is_pydm=self.is_pydm)
            if wind:
                break
            _time.sleep(0.01)
        self.closemessage.emit()
