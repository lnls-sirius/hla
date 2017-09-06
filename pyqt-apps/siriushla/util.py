"""Util module."""

import siriushla.resources as _resources
from pydm.PyQt.QtCore import QFile as _QFile
import pathlib as _pathlib
import os as _os


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
        app.setStyleSheet(style)
    else:
        print('set_style: "{0}": {1}'.format(fname, stream.errorString()))
    _resources.qCleanupResources()
