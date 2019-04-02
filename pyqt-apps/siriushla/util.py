"""Util module."""
import os as _os
import pathlib as _pathlib
import subprocess as _subprocess

from qtpy.QtCore import QFile as _QFile
from qtpy.QtWidgets import QPushButton, QAction, QApplication
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
    signal = _define_widget_signal(widget)
    app = QApplication.instance()
    widget.w_class = w_class
    widget.kwargs = kwargs
    signal.connect(lambda: app.open_window(
        app.sender().w_class, parent=parent, **app.sender().kwargs))


def connect_newprocess(widget, cmd, **kwargs):
    """Execute a child program in a new process."""
    signal = _define_widget_signal(widget)
    signal.connect(lambda: run_newprocess(cmd, **kwargs))


def run_newprocess(cmd, **kwargs):
    # Parse kwargs
    bufsize = kwargs['bufsize'] if 'bufsize' in kwargs else -1
    executable = kwargs['executable'] if 'executable' in kwargs else None
    stdin = kwargs['stdin'] if 'stdin' in kwargs else None
    stdout = kwargs['stdout'] if 'stdout' in kwargs else None
    stderr = kwargs['stderr'] if 'stderr' in kwargs else None
    preexec_fn = kwargs['preexec_fn'] if 'preexec_fn' in kwargs else None
    close_fds = kwargs['close_fds'] if 'close_fds' in kwargs else True
    shell = kwargs['shell'] if 'shell' in kwargs else False
    cwd = kwargs['cwd'] if 'cwd' in kwargs else None
    env = kwargs['env'] if 'env' in kwargs else None
    universal_newlines = kwargs['universal_newlines'] if 'universal_newlines'\
        in kwargs else False
    startupinfo = kwargs['startupinfo'] if 'startupinfo' in kwargs else None
    creationflags = kwargs['creationflags'] if 'creationflags' in kwargs else 0
    restore_signals = kwargs['restore_signals'] if 'restore_signals' in kwargs\
        else True
    start_new_session = kwargs['start_new_session'] if 'start_new_session' in\
        kwargs else False
    pass_fds = kwargs['pass_fds'] if 'pass_fds' in kwargs else ()
    encoding = kwargs['encoding'] if 'encoding' in kwargs else None
    errors = kwargs['errors'] if 'errors' in kwargs else None

    # Maximize the window if it exists, else create a new one
    scmd = (_subprocess.list2cmdline(cmd) if isinstance(cmd, list) else cmd)
    pid = _subprocess.run(
        "ps ax | grep \"[" + scmd[0] + "]" + scmd[1:] +
        "\" | xargs | cut -f1 -d\" \" -",
        stdin=_subprocess.PIPE, shell=True, stdout=_subprocess.PIPE,
        check=True).stdout.decode('UTF-8').strip('\n')
    if pid:
        _subprocess.run(
            "xdotool windowactivate `xdotool search --pid "+pid+" | tail -1`",
            stdin=_subprocess.PIPE, shell=True)
    else:
        _subprocess.Popen(
            cmd, bufsize=bufsize, executable=executable,
            stdin=stdin, stdout=stdout, stderr=stderr,
            preexec_fn=preexec_fn, close_fds=close_fds,
            shell=shell, cwd=cwd, env=env,
            universal_newlines=universal_newlines,
            startupinfo=startupinfo, creationflags=creationflags,
            restore_signals=restore_signals,
            start_new_session=start_new_session,
            pass_fds=pass_fds, encoding=encoding, errors=errors)


def _define_widget_signal(widget):
    if isinstance(widget, QAction):
        signal = widget.triggered
    elif isinstance(widget, QPushButton):
        signal = widget.clicked
    else:
        raise AttributeError("Undefined signal for {}".format(widget))
    return signal
