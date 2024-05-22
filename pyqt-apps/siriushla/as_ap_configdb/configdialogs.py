"""Define a window to save configurations."""

import logging
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, \
    QWidget, QLabel, QPushButton, QMessageBox
from qtpy.QtCore import Slot, Signal

from siriuspy.clientconfigdb import ConfigDBClient
from siriushla.widgets.windows import SiriusDialog
from .configwidgets import ConfigTableWidget, ConfigDBInfoHeader, \
    ConfigDBSearchEngine


class _BaseConfigManipulation(SiriusDialog):
    configname = Signal(str)

    def __init__(self, config_type, parent=None):
        """Constructor."""
        super().__init__(parent)
        self._client = ConfigDBClient(config_type=config_type)
        self._config_type = config_type
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)
        self._setupui()
        self._config = ''
        self._status = False
        self.setWindowTitle("Configuration Database Manager")

    def _setupui(self):
        self.layoutv = QVBoxLayout(self)

        # Basic widgets
        self.editor = ConfigTableWidget(self._client, self)
        self.editor.config_type = self._config_type
        self.cancel_button = QPushButton('Cancel', self)
        self.cancel_button.pressed.connect(self.reject)
        self.ok_button = QPushButton('Load', self)
        self.ok_button.setEnabled(False)
        self.ok_button.pressed.connect(self._load_configuration)

        self.search_le = ConfigDBSearchEngine(self.editor, self)
        self.label_exist = QLabel('', self)

        # Config View Widget
        self.config_viewer = QWidget(self)
        self.config_viewer.layout = QVBoxLayout(self.config_viewer)
        self.config_viewer.layout.addWidget(self.search_le)
        self.config_viewer.layout.addWidget(self.label_exist)
        self.config_viewer.layout.addWidget(self.editor)
        hbl = QHBoxLayout()
        hbl.addStretch()
        hbl.addWidget(self.cancel_button)
        hbl.addStretch()
        hbl.addWidget(self.ok_button)
        hbl.addStretch()
        self.config_viewer.layout.addLayout(hbl)

        # Sub header with database general information
        self.sub_header = ConfigDBInfoHeader(
            self._client, parent=self, config_type=self._config_type)

        # Main widget layout setup
        self.layoutv.addWidget(self.sub_header)
        self.layoutv.addWidget(self.config_viewer)

        # Update Selection when a configuration is selected
        self.editor.configChanged.connect(self._update_selection)
        # Connect database error to slot that show messages
        self.editor.connectionError.connect(self._database_error)

    @property
    def client(self):
        """."""
        return self._client

    @property
    def config_name(self):
        return self.editor.config_name

    def accept(self):
        """Override accept."""
        self._status = True
        super().accept()

    def exec_(self):
        """Override exec."""
        super().exec_()
        return self._config, self._status

    def exec(self):
        return self.exec_()

    @Slot(str, str)
    def _update_selection(self, selected, deselected):
        config = selected
        if config:
            self.ok_button.setEnabled(True)
            self.ok_button.setText('Load {}'.format(config))
        else:
            self.ok_button.setEnabled(False)
        self.ok_button.style().polish(self.ok_button)

    @Slot()
    def _load_configuration(self):
        config = self.config_name
        if config:
            self.configname.emit(config)
            self._config = config
        self.accept()

    @Slot(int, str, str)
    def _database_error(self, code, message, operation):
        tpe = QMessageBox.Warning
        title = 'Something went wrong'
        msg = '{}: {}, while trying to {}'.format(code, message, operation)
        QMessageBox(tpe, title, msg).exec_()


class LoadConfigDialog(_BaseConfigManipulation):
    """Load configurations."""


class SaveConfigDialog(_BaseConfigManipulation):
    """Save configurations."""

    configname = Signal(str)

    def __init__(self, config_type, parent=None):
        """Constructor."""
        super().__init__(config_type, parent)
        self.ok_button.setText('Save')
        self.search_le.setPlaceholderText('Type the configuration name...')
        self.search_le.filteredidcs.connect(self._filtered_indices)

    @property
    def config_name(self):
        return self.search_le.text()

    @Slot(str, str)
    def _update_selection(self, selected, deselected):
        config = selected
        if config:
            self.search_le.setText(config)
        self.ok_button.style().polish(self.ok_button)

    @Slot(list)
    def _filtered_indices(self, idxlist):
        valid = True
        txt = self.search_le.text()
        for idx in idxlist:
            name = self.editor.model().createIndex(
                            idx, self.editor.NAME_COL).data()
            valid &= not txt == name

        self.ok_button.setEnabled(bool(txt))
        if not bool(txt):
            savetext = 'Save'
            labltext = ''
        elif valid:
            savetext = 'Save '
            labltext = '<b>Name Valid</b>'
        else:
            savetext = 'Overwrite '
            labltext = '<b>Caution, configuration will be overwritten!!</b.'
        self.label_exist.setText(labltext)
        self.ok_button.setText(savetext + txt)


class RenameConfigDialog(SaveConfigDialog):
    """Rename configurations."""

    configname = Signal(str)

    def __init__(self, config_type, parent=None):
        """Constructor."""
        super().__init__(config_type, parent)
        self.ok_button.setText('Rename')
        self.search_le.setPlaceholderText('Type the new name...')

    @Slot(list)
    def _filtered_indices(self, idxlist):
        txt = self.search_le.text()
        valid = bool(txt)
        for idx in idxlist:
            name = self.editor.model().createIndex(
                            idx, self.editor.NAME_COL).data()
            valid &= not txt == name

        self.ok_button.setEnabled(valid)
        if not valid:
            rnmetext = 'Rename'
            labltext = '<b>Name already taken. Choose another one.</b.'
        else:
            rnmetext = 'Rename to ' + txt
            labltext = '<b>Name Valid</b>'
        self.label_exist.setText(labltext)
        self.ok_button.setText(rnmetext)
