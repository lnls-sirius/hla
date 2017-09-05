"""Util module."""

import siriushla.resources as _resources
from pydm.PyQt.QtCore import QFile as _QFile


def set_style(app):
    """Implement sirius-style.css as default Qt resource file for Sirius."""
    stream = _QFile(':/style.css')
    if stream.open(_QFile.ReadOnly):
        style = str(stream.readAll(), 'utf-8')
        stream.close()
    else:
        print(stream.errorString())
    app.setStyleSheet(style)
    _resources.qCleanupResources()
