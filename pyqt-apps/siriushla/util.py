"""Util module."""

import siriushla.resources as _resources
from pydm.PyQt.QtCore import QFile as _QFile
import pathlib.Path as _Path
import os as _os


def set_style(app):
    """Implement sirius-hla-style.css as default Qt resource file HLA."""
    fname = _Path(_os.path.join(_Path.home(), '.sirius-hla-style.css'))
    path = _Path(fname)
    if path._is_file():
        stream = _QFile(fname)
    else:
        stream = _QFile(':/sirius-hla-style.css')

    if stream.open(_QFile.ReadOnly):
        style = str(stream.readAll(), 'utf-8')
        stream.close()
    else:
        print(stream.errorString())
    app.setStyleSheet(style)
    _resources.qCleanupResources()
