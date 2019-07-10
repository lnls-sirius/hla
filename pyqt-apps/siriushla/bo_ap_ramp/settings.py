"""Booster Ramp Control HLA: Ramp Settings Module."""

from qtpy.QtCore import Qt, Signal, Slot
from qtpy.QtGui import QKeySequence
from qtpy.QtWidgets import QMenuBar, QAction, QMessageBox
from siriuspy.clientconfigdb import ConfigDBException as _ConfigDBException, \
    ConfigDBDocument as _ConfigDBDocument
from siriuspy.ramp import ramp
from siriushla import util as _hlautil
from siriushla.as_ps_control.PSTabControlWindow import \
    PSTabControlWindow as _MAControlWindow
from siriushla.as_pm_control.PulsedMagnetControlWindow import \
    PulsedMagnetControlWindow as _PMControlWindow
from siriushla.as_ps_cycle.cycle_window import CycleWindow as _CycleWindow
from .auxiliar_classes import \
    LoadRampConfig as _LoadRampConfig, \
    NewRampConfigGetName as _NewRampConfigGetName, \
    OpticsAdjustSettings as _OpticsAdjustSettings


class Settings(QMenuBar):
    """Widget to choose and to control a BoosterRamp configuration."""

    newConfigNameSignal = Signal(str)
    loadSignal = Signal()
    opticsSettingsSignal = Signal(str, str)
    diagSettingsSignal = Signal(list)
    plotUnitSignal = Signal(str)

    def __init__(self, parent=None, prefix='', ramp_config=None,
                 tunecorr_configname='', chromcorr_configname=''):
        """Initialize object."""
        super().__init__(parent)
        self.setObjectName('BOApp')
        self.prefix = prefix
        self.ramp_config = ramp_config
        self._tunecorr_configname = tunecorr_configname
        self._chromcorr_configname = chromcorr_configname
        self._injcurr_idx = 0
        self._ejecurr_idx = -1
        self._setupUi()

    def _setupUi(self):
        self.setStyleSheet(
            """QMenuBar::item {\npadding: 0 1em 0 0.17em;\n}""")
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
        self.config_menu.addSeparator()

        self.ramp_params_menu = self.addMenu('Ramping Parameters')
        self.menu_plotunits = self.ramp_params_menu.addMenu(
            'Plot magnet waveforms in...')
        self.act_plotcurrents = QAction('Currents', self)
        self.act_plotcurrents.triggered.connect(self._emitPlotUnits)
        self.act_plotstrengths = QAction('Strengths', self)
        self.act_plotstrengths.triggered.connect(self._emitPlotUnits)
        self.menu_plotunits.addAction(self.act_plotcurrents)
        self.menu_plotunits.addAction(self.act_plotstrengths)

        self.optics_menu = self.addMenu('Optics Adjustments')
        self.act_optics_settings = QAction('Settings', self)
        self.act_optics_settings.triggered.connect(
            self._showOpticsSettingsPopup)
        self.optics_menu.addAction(self.act_optics_settings)

        self.diag_menu = self.addMenu('Ramp Diagnosis')
        # TODO: menu to access all windows related to diagnostics

        self.open_menu = self.addMenu('Open...')
        self.act_cycle = QAction('PS Cycle')
        _hlautil.connect_window(self.act_cycle, _CycleWindow, parent=self,
                                checked_accs=('BO',))
        self.act_ma = QAction('Booster Magnets')
        _hlautil.connect_window(self.act_ma, _MAControlWindow, parent=self,
                                section='BO', discipline='MA')
        self.act_pm = QAction('Pulsed Magnets')
        _hlautil.connect_window(self.act_pm, _PMControlWindow, section='BO',
                                parent=self)
        self.act_sofb = QAction('Booster SOFB')
        _hlautil.connect_newprocess(self.act_sofb, 'sirius-hla-bo-ap-sofb.py')
        self.act_ti = QAction('Timing')
        _hlautil.connect_newprocess(self.act_ti, 'sirius-hla-as-ti-control.py')
        self.open_menu.addAction(self.act_cycle)
        self.open_menu.addAction(self.act_ma)
        self.open_menu.addAction(self.act_pm)
        self.open_menu.addAction(self.act_sofb)
        self.open_menu.addAction(self.act_ti)

    def _showGetNewConfigNamePopup(self):
        self._newConfigNamePopup = _NewRampConfigGetName(
            self.ramp_config, 'bo_ramp', self, new_from_template=True)
        self._newConfigNamePopup.configname.connect(self._emitConfigName)
        self._newConfigNamePopup.saveSignal.connect(self.showSaveAsPopup)
        self._newConfigNamePopup.open()

    def _showLoadExistingConfigPopup(self):
        self._loadPopup = _LoadRampConfig(self.ramp_config, self)
        self._loadPopup.configname.connect(self._emitConfigName)
        self._loadPopup.loadSignal.connect(self._emitLoadSignal)
        self._loadPopup.saveSignal.connect(self.showSaveAsPopup)
        self._loadPopup.open()

    def _showOpticsSettingsPopup(self):
        self._opticsSettingsPopup = _OpticsAdjustSettings(
            self._tunecorr_configname, self._chromcorr_configname, self)
        self._opticsSettingsPopup.updateSettings.connect(
            self._emitOpticsSettings)
        self._opticsSettingsPopup.open()

    def showSaveAsPopup(self):
        """Show a popup to get a new name to save config."""
        if self.ramp_config is None:
            return
        self._saveAsPopup = _NewRampConfigGetName(
            self.ramp_config, 'bo_ramp', self, new_from_template=False)
        self._saveAsPopup.configname.connect(self._saveAndEmitConfigName)
        self._saveAsPopup.open()

    def _saveAndEmitConfigName(self, new_name=None):
        if not self.ramp_config:
            return
        try:
            if self.ramp_config.exist():
                old_name = self.ramp_config.name
                if not new_name:
                    new_name = _ConfigDBDocument.generate_config_name(old_name)
                self.ramp_config.save(new_name)
            else:
                self.ramp_config.save()
        except _ConfigDBException as err:
            QMessageBox.critical(self, 'Error', str(err), QMessageBox.Ok)
        else:
            self._emitConfigName(self.ramp_config.name)

    def _emitConfigName(self, config_name):
        self.newConfigNameSignal.emit(config_name)

    def _emitLoadSignal(self):
        self.loadSignal.emit()

    @Slot(str, str)
    def _emitOpticsSettings(self, tunecorr_configname, chromcorr_configname):
        self._tunecorr_configname = tunecorr_configname
        self._chromcorr_configname = chromcorr_configname
        self.opticsSettingsSignal.emit(
            tunecorr_configname, chromcorr_configname)

    def _emitDiagSettings(self, settings):
        self._injcurr_idx = settings[0]
        self._ejecurr_idx = settings[1]
        self.diagSettingsSignal.emit(settings)

    def _emitPlotUnits(self):
        sender_text = self.sender().text()
        self.plotUnitSignal.emit(sender_text)

    @Slot(ramp.BoosterRamp)
    def getRampConfig(self, ramp_config):
        """Get new BoosterRamp object."""
        self.ramp_config = ramp_config
