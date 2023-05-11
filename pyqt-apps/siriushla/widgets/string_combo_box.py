"""Sirius String ComboBox."""

import logging
from qtpy.QtWidgets import QComboBox
from qtpy.QtCore import Qt
from pydm.widgets.base import PyDMWritableWidget


logger = logging.getLogger(__name__)


class SiriusStringComboBox(QComboBox, PyDMWritableWidget):
    """A ComboBox with a channel to handle PVs of string type."""

    def __init__(self, parent=None, init_channel=None, items=None):
        """Init."""
        QComboBox.__init__(self, parent)
        PyDMWritableWidget.__init__(self, init_channel=init_channel)
        self._has_items = False
        self.set_items(items)
        self.activated.connect(self._send_value)
        self.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.contextMenuEvent = self.open_context_menu

    def value_changed(self, new_val):
        """Handle PV value changed in widget."""
        if new_val is not None:
            if isinstance(self._items, dict):
                new_val = self._values2items.get(new_val, 'UNDEF')
            idx = self.findText(new_val)
            if idx == -1:
                logger.error("Can not change value to %r. "
                             "Not an option in SiriusStringComboBox",
                             new_val)
                return
            self.setCurrentIndex(idx)

    def set_items(self, items):
        """Add comboBox items."""
        if items is None:
            return
        elif isinstance(items, list):
            items.append('UNDEF')
            for item in items:
                try:
                    self.addItem(item)
                except TypeError as error:
                    logger.error(
                        "Invalid type '{0}'. The expected type is 'string'. "
                        "Exception: {1}".format(type(item), error))
        elif isinstance(items, dict):
            items['UNDEF'] = -1
            for item_text, data in items.items():
                try:
                    self.addItem(item_text, data)
                except TypeError as error:
                    logger.error(
                        "Invalid type '{0}'. The expected type is 'string'. "
                        "Exception: {1}".format(type(item), error))
            self._values2items = {v: t for t, v in items.items()}
        self._items = items
        self._has_items = True
        self.check_enable_state()

    def check_enable_state(self):
        """Checks whether or not the widget should be disable."""
        status = self._write_access and self._connected and self._has_items
        tooltip = ""
        if not self._connected:
            tooltip += "PV is disconnected."
        elif not self._write_access:
            tooltip += "Access denied by Channel Access Security."
        elif not self._has_items:
            tooltip += "Items not available."

        self.setToolTip(tooltip)
        self.setEnabled(status)

    def _send_value(self, index):
        text = self.itemText(index)
        if text == 'UNDEF':
            return
        if isinstance(self._items, list):
            self.send_value_signal[str].emit(text)
        elif isinstance(self._items, dict):
            value = self._items[text]
            self.send_value_signal[type(value)].emit(value)
