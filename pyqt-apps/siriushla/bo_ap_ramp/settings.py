"""Booster Ramp Control HLA: Ramp Settings Module."""

from qtpy.QtCore import Qt, Signal, Slot
from qtpy.QtGui import QKeySequence
from qtpy.QtWidgets import QMenuBar, QAction
from siriuspy.servconf.util import \
    generate_config_name as _generate_config_name
from siriuspy.ramp import ramp
from siriushla import util as _hlautil
from siriushla.as_ps_control.PSTabControlWindow import \
    PSTabControlWindow as _MAControlWindow
from siriushla.as_pm_control.PulsedMagnetControlWindow import \
    PulsedMagnetControlWindow as _PMControlWindow
from siriushla.as_ps_cycle.cycle_window import CycleWindow as _CycleWindow
from siriushla.bo_ap_ramp.auxiliar_classes import \
    LoadRampConfig as _LoadRampConfig, \
    NewRampConfigGetName as _NewRampConfigGetName, \
    OpticsAdjustSettings as _OpticsAdjustSettings, \
    StatisticSettings as _StatisticSettings


class Settings(QMenuBar):
    """Widget to choose and to control a BoosterRamp configuration."""

    newConfigNameSignal = Signal(str)
    loadSignal = Signal()
    opticsSettingsSignal = Signal(list)
    statsSettingsSignal = Signal(list)

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
        self.setStyleSheet(
            """QMenuBar::item {
                padding: 0 30px 0 5px;
            }""")
        self.config_menu = self.addMenu('Booster Ramp Configuration')
        self.act_new = QAction('New from template', self)
        self.act_new.setShortcut(QKeySequence.New)
        self.act_new.triggered.connect(self._showGetNewConfigNamePopup)
        self.act_load = QAction('Load existing config...', self)
        self.act_load.setShortcut(QKeySequence.Open)
        self.act_load.triggered.connect(self._showLoadExistingConfigPopup)
        self.act_save = QAction('Save', self)
        self.act_save.setShortcut(QKeySequence.Save)
        self.act_save.triggered.connect(self._saveAndEmitConfigName)
        self.act_save_as = QAction('Save As...', self)
        self.act_save_as.setShortcut(QKeySequence(Qt.CTRL+Qt.SHIFT+Qt.Key_S))
        self.act_save_as.triggered.connect(self.showSaveAsPopup)
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

        self.open_menu = self.addMenu('Open...')
        self.act_cycle = QAction('PS Cycle')
        _hlautil.connect_window(self.act_cycle, _CycleWindow, parent=self)
        self.act_ma = QAction('Booster MA')
        _hlautil.connect_window(self.act_ma, _MAControlWindow, parent=self,
                                section='BO', discipline=1)  # MA
        self.act_pm = QAction('PM')
        _hlautil.connect_window(self.act_pm, _PMControlWindow, parent=self)
        self.open_menu.addAction(self.act_cycle)
        self.open_menu.addAction(self.act_ma)
        self.open_menu.addAction(self.act_pm)
        # TODO: include RF and TI windows??

    def _showGetNewConfigNamePopup(self):
        self._newConfigFromTemplateGetNamePopup = _NewRampConfigGetName(
            self, self.ramp_config, ramp.BoosterRamp, new_from_template=True)
        self._newConfigFromTemplateGetNamePopup.newConfigNameSignal.connect(
            self._emitConfigName)
        self._newConfigFromTemplateGetNamePopup.saveSignal.connect(
            self.showSaveAsPopup)
        self._newConfigFromTemplateGetNamePopup.open()

    def _showLoadExistingConfigPopup(self):
        self._loadPopup = _LoadRampConfig(self, self.ramp_config)
        self._loadPopup.newConfigNameSignal.connect(self._emitConfigName)
        self._loadPopup.loadSignal.connect(self._emitLoadSignal)
        self._loadPopup.saveSignal.connect(self.showSaveAsPopup)
        self._loadPopup.open()

    def _showOpticsSettingsPopup(self):
        self._opticsSettingsPopup = _OpticsAdjustSettings(
            self._tunecorr_name, self._chromcorr_name, self)
        self._opticsSettingsPopup.updateSettings.connect(
            self._emitOpticsSettings)
        self._opticsSettingsPopup.open()

    def _showStatsSettingsPopup(self):
        self._statsSettingsPopup = _StatisticSettings(
            self, self.prefix, self._injcurr_idx, self._ejecurr_idx)
        self._statsSettingsPopup.updateSettings.connect(
            self._emitStatsSettings)
        self._statsSettingsPopup.open()

    def showSaveAsPopup(self):
        """Show a popup to get a new name to save config."""
        if self.ramp_config is None:
            return
        self._saveAsPopup = _NewRampConfigGetName(
            self, self.ramp_config, ramp.BoosterRamp, new_from_template=False)
        self._saveAsPopup.newConfigNameSignal.connect(
            self._saveAndEmitConfigName)
        self._saveAsPopup.open()

    def _saveAndEmitConfigName(self, new_name=None):
        if self.ramp_config.configsrv_exist():
            old_name = self.ramp_config.name
            if not new_name:
                new_name = _generate_config_name(old_name)
            self.ramp_config.configsrv_save(new_name)
        else:
            self.ramp_config.configsrv_save()
        self._emitConfigName(self.ramp_config.name)

    def _emitConfigName(self, config_name):
        self.newConfigNameSignal.emit(config_name)

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

    @Slot(ramp.BoosterRamp)
    def getRampConfig(self, ramp_config):
        """Get new BoosterRamp object."""
        self.ramp_config = ramp_config
