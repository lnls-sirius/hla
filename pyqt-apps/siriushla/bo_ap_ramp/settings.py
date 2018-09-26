"""Booster Ramp Control HLA: Ramp Settings Module."""

from copy import deepcopy as _dcopy
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QMenuBar, QInputDialog, QAction, QLineEdit
from siriuspy.servconf.conf_service import ConfigService as _ConfigService
from siriushla.bo_ap_ramp.auxiliar_classes import \
    LoadRampConfig as _LoadRampConfig, \
    NewRampConfigGetName as _NewRampConfigGetName, \
    OpticsAdjustSettings as _OpticsAdjustSettings, \
    StatisticSettings as _StatisticSettings, \
    MessageBox as _MessageBox


class Settings(QMenuBar):
    """Widget to choose and to control a BoosterRamp configuration."""

    configNameSignal = pyqtSignal(str)
    loadSignal = pyqtSignal()
    saveSignal = pyqtSignal()
    opticsSettingsSignal = pyqtSignal(list)
    statsSettingsSignal = pyqtSignal(list)

    def __init__(self, parent=None, prefix='', ramp_config=None):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = prefix
        self.ramp_config = ramp_config
        self._tunecorr_name = 'Default_1'
        self._chromcorr_name = 'Default'
        self._injcurr_idx = 0
        self._ejecurr_idx = -1
        self._setupUi()

    def _setupUi(self):
        self.config_menu = self.addMenu('Booster Ramp Configuration')
        self.act_new = QAction('New from template', self)
        self.act_new.setShortcut(QKeySequence.New)
        self.act_new.triggered.connect(self._showGetNewConfigName)
        self.act_load = QAction('Load existing config...', self)
        self.act_load.setShortcut(QKeySequence.Open)
        self.act_load.triggered.connect(self._showLoadExistingConfig)
        self.act_save = QAction('Save', self)
        self.act_save.setShortcut(QKeySequence.Save)
        self.act_save.triggered.connect(self._save)
        self.act_save_as = QAction('Save As...', self)
        self.act_save_as.setShortcut(QKeySequence(Qt.CTRL+Qt.SHIFT+Qt.Key_S))
        self.act_save_as.triggered.connect(self._showSaveAsPopup)
        self.config_menu.addAction(self.act_new)
        self.config_menu.addAction(self.act_load)
        self.config_menu.addAction(self.act_save)
        self.config_menu.addAction(self.act_save_as)

        self.optics_menu = self.addMenu('Optics Adjustments')
        self.act_optics_settings = QAction('Settings', self)
        self.act_optics_settings.triggered.connect(
            self._showOpticsSettingsPopup)
        self.optics_menu.addAction(self.act_optics_settings)

        self.stats_menu = self.addMenu('Statistics')
        self.act_stats_settings = QAction('Settings', self)
        self.act_stats_settings.triggered.connect(
            self._showStatsSettingsPopup)
        self.stats_menu.addAction(self.act_stats_settings)

    def _showGetNewConfigName(self):
        self._newConfigPopup = _NewRampConfigGetName(self, self.ramp_config)
        self._newConfigPopup.configNameSignal.connect(
            self._emitConfigNameSignal)
        self._newConfigPopup.saveSignal.connect(self._save)
        self._newConfigPopup.open()

    def _showLoadExistingConfig(self):
        self._loadPopup = _LoadRampConfig(self, self.ramp_config)
        self._loadPopup.configNameSignal.connect(self._emitConfigNameSignal)
        self._loadPopup.loadSignal.connect(self._emitLoadSignal)
        self._loadPopup.saveSignal.connect(self._save)
        self._loadPopup.open()

    def _showOpticsSettingsPopup(self):
        self._opticsSettingsPopup = _OpticsAdjustSettings(
            self, self._tunecorr_name, self._chromcorr_name)
        self._opticsSettingsPopup.updateSettings.connect(
            self._emitOpticsSettings)
        self._opticsSettingsPopup.open()

    def _showStatsSettingsPopup(self):
        self._statsSettingsPopup = _StatisticSettings(
            self, self.prefix, self._injcurr_idx, self._ejecurr_idx)
        self._statsSettingsPopup.updateSettings.connect(
            self._emitStatsSettings)
        self._statsSettingsPopup.open()

    def _emitConfigNameSignal(self, config_name):
        self.configNameSignal.emit(config_name)

    def _emitLoadSignal(self):
        self.loadSignal.emit()

    def _emitOpticsSettings(self, settings):
        self._tunecorr_name = settings[0]
        self._chromcorr_name = settings[1]
        self.opticsSettingsSignal.emit(settings)

    def _emitStatsSettings(self, settings):
        self._injcurr_idx = settings[0]
        self._ejecurr_idx = settings[1]
        self.statsSettingsSignal.emit(settings)

    def _save(self):
        config_exists = self.ramp_config.configsrv_exist()
        if config_exists:
            self.ramp_config.configsrv_update()
        else:
            self.ramp_config.configsrv_save()
        self.saveSignal.emit()

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

    def getRampConfig(self, ramp_config):
        """Get new BoosterRamp object."""
        self.ramp_config = ramp_config
