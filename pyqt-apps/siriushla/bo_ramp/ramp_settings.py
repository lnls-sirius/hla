"""Booster Ramp Control HLA: Ramp Settings Module."""

from copy import deepcopy as _dcopy
from PyQt5.QtCore import Qt, pyqtSignal, QStringListModel
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QSpacerItem, \
                            QPushButton, QLabel, QLineEdit, QCompleter, \
                            QSizePolicy as QSzPlcy, QInputDialog
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.ramp import ramp
from siriuspy.servconf.conf_service import ConfigService as _ConfigService
from siriushla.bo_ramp.auxiliar_classes import MessageBox as _MessageBox


class RampConfigSettings(QGroupBox):
    """Widget to choose and to control a BoosterRamp configuration."""

    configSignal = pyqtSignal(str)
    loadSignal = pyqtSignal(ramp.BoosterRamp)

    def __init__(self, parent=None, prefix='', ramp_config=None):
        """Initialize object."""
        super().__init__('Ramp Configuration', parent)
        self.prefix = _PVName(prefix)
        self.ramp_config = ramp_config
        self._setupUi()
        self.loadSignal.connect(self._getRampConfig)

    def _setupUi(self):
        if self.ramp_config is not None:
            le_text = self.ramp_config.name
        else:
            le_text = ''
        label_name = QLabel('Name', self)
        label_name.setAlignment(Qt.AlignCenter)
        label_name.setFixedHeight(40)
        self.le_config = QLineEdit(le_text, self)
        self.bt_load = QPushButton('Load', self)
        self.bt_save = QPushButton('Save', self)
        self.bt_save_as = QPushButton('Save As...', self)

        completer = QCompleter()
        self._completer_model = QStringListModel()
        completer.setModel(self._completer_model)
        allconfigs = _ConfigService().find_configs(config_type='bo_ramp')
        string_list = list()
        for c in allconfigs['result']:
            string_list.append(c['name'])
        self._completer_model.setStringList(string_list)
        self.le_config.setCompleter(completer)
        self.le_config.editingFinished.connect(self._le_config_textChanged)
        self.bt_load.clicked.connect(self._load)
        self.bt_save.clicked.connect(self._save)
        self.bt_save_as.clicked.connect(self._showSaveAsPopup)

        lay = QVBoxLayout(self)
        lay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding))
        lay.addWidget(label_name)
        lay.addWidget(self.le_config)
        lay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding))
        lay.addWidget(self.bt_load)
        lay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding))
        lay.addWidget(self.bt_save)
        lay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding))
        lay.addWidget(self.bt_save_as)
        lay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding))

    def _le_config_textChanged(self):
        name = self.le_config.text()
        if ramp.BoosterRamp(name).configsrv_exist():
            if ((self.ramp_config is None) or
                    (self.ramp_config is not None and
                     name != self.ramp_config.name)):
                self.bt_load.setStyleSheet("""background-color:#1F64FF;""")
        elif name != '':
            create_config = _MessageBox(
                self, 'Create a new configuration?',
                'There is no configuration with name \"{}\". \n'
                'Create a new one?'.format(name), 'Yes', 'Cancel')
            create_config.acceptedSignal.connect(self._emitConfigSignal)
            create_config.show()

    def _emitConfigSignal(self):
        self.configSignal.emit(self.le_config.text())

    def _load(self):
        name = self.le_config.text()
        if ramp.BoosterRamp(name).configsrv_exist():
            if self.ramp_config is not None:
                if not self.ramp_config.configsrv_synchronized:
                    save_changes = _MessageBox(
                        self, 'Save changes?',
                        'There are unsaved changes. \n'
                        'Do you want to save?'.format(name),
                        'Yes', 'Cancel')
                    save_changes.acceptedSignal.connect(self._save)
                    save_changes.exec_()

                if name != self.ramp_config.name:
                    self.configSignal.emit(name)
                else:
                    self.ramp_config.configsrv_load()
                    self.ramp_config.configsrv_load_normalized_configs()
                    self.loadSignal.emit(self.ramp_config)
            else:
                self.configSignal.emit(name)
            self.verifySync()

    def _save(self):
        config_exists = self.ramp_config.configsrv_exist()
        if config_exists:
            self.ramp_config.configsrv_update()
        else:
            self.ramp_config.configsrv_save()
        self.verifySync()

    def _showSaveAsPopup(self):
        if self.ramp_config is not None:
            text, ok = QInputDialog.getText(self, 'Save As...',
                                            'Ramp config. name:',
                                            echo=QLineEdit.Normal, text='')
            if not ok:
                return
            self._name_to_saveas = text
            allconfigs = _ConfigService().find_configs(config_type='bo_ramp')
            for c in allconfigs['result']:
                if text == c['name']:
                    save_changes = _MessageBox(
                        self, 'Overwrite configuration?',
                        'There is a configuration with name {}. \n'
                        'Do you want to replace it?'.format(text),
                        'Yes', 'Cancel')
                    save_changes.acceptedSignal.connect(self._save_as)
                    save_changes.exec_()
                    break
            else:
                self._save_as()

    def _save_as(self):
        config_tosave = _dcopy(self.ramp_config)
        config_tosave.name = self._name_to_saveas
        config_tosave.configsrv_save()

        # update completion
        allconfigs = _ConfigService().find_configs(config_type='bo_ramp')
        string_list = list()
        for c in allconfigs['result']:
            string_list.append(c['name'])
        self._completer_model.setStringList(string_list)

    def _getRampConfig(self, ramp_config):
        """Get new BoosterRamp object."""
        self.ramp_config = ramp_config
        self.bt_load.setStyleSheet("")

    def verifySync(self):
        """Verify sync status related to ConfServer."""
        if self.ramp_config is not None:
            if not self.ramp_config.configsrv_synchronized:
                self.bt_save.setStyleSheet("""background-color: #1F64FF;""")
            else:
                self.bt_save.setStyleSheet("")
