import logging
import functools

from collections import OrderedDict

from pydm.widgets.logdisplay import logger_destroyed, GuiHandler, \
    PyDMLogDisplay

from qtpy.QtCore import (QObject, Slot, Signal, Property,
                         Q_ENUMS, QSize)
from qtpy.QtWidgets import (QWidget, QPlainTextEdit, QComboBox, QLabel,
                            QPushButton, QHBoxLayout, QVBoxLayout)

logger = logging.getLogger(__name__)


class SiriusGuiHandler(GuiHandler):
    message = Signal(str, int)

    def __init__(self, level=logging.NOTSET, parent=None):
        """."""
        super().__init__(level=level, parent=parent)
        self.level = level

    def emit(self, record):
        """Emit formatted log messages when received but only if level is set."""
        # Avoid garbage to be presented when master log is running with DEBUG.
        if self.level == logging.NOTSET:
            return
        self.message.emit(self.format(record), record.levelno)


class SiriusLogDisplay(PyDMLogDisplay):
    """
    Standard display for Log Output

    This widget handles instantating a ``GuiHandler`` and displaying log
    messages to a ``QPlainTextEdit``. The level of the log can be changed from
    inside the widget itself, allowing users to select from any of the
    ``.levels`` specified by the widget.

    Parameters
    ----------
    parent : QObject, optional

    logname : str
        Name of log to display in widget

    level : logging.Level
        Initial level of log display

    """
    Colors = {
        PyDMLogDisplay.LogLevels.DEBUG: 'black',
        PyDMLogDisplay.LogLevels.INFO: 'black',
        PyDMLogDisplay.LogLevels.WARNING: 'yellow',
        PyDMLogDisplay.LogLevels.ERROR: 'red',
        PyDMLogDisplay.LogLevels.CRITICAL: 'red',
        }

    def __init__(self, parent=None, logname=None, level=logging.NOTSET):
        """."""
        super().__init__(parent=parent, logname=logname, level=level)
        # Create Widgets
        self.handler.message.disconnect(self.write)
        self.log.removeHandler(self.handler)
        self.handler = SiriusGuiHandler(level=level, parent=self)
        self.handler.setFormatter(logging.Formatter(self.default_format))
        self.log.addHandler(self.handler)
        self.handler.message.connect(self.writehtml)

    @Slot(str, int)
    def writehtml(self, message, levelno):
        """Write a message to the log display."""
        # We split the incoming message by new lines. In prior iterations of
        # this widget it was discovered that large blocks of text cause issues
        # at the Qt level.
        for msg in message.split(self.terminator):
            self.text.appendHtml(
                f'<p style="color:{self.Colors[levelno]:s}">{msg:s}</p>')
