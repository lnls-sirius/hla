"""Booster Ramp Control HLA: Ramp Settings Module."""

from qtpy.QtCore import Qt, Signal, Slot
from qtpy.QtGui import QKeySequence
from qtpy.QtWidgets import QMenuBar, QAction
from siriuspy.servconf.util import \
    generate_config_name as _generate_config_name
from siriuspy.servconf import exceptions as _srvexceptions
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
    DiagnosisSettings as _DiagnosisSettings, \
    MessageBox as _MessageBox


class Settings(QMenuBar):
    """Widget to choose and to control a BoosterRamp configuration."""

    newConfigNameSignal = Signal(str)
    loadSignal = Signal()
    opticsSettingsSignal = Signal(list)
    diagSettingsSignal = Signal(list)
    plotUnitSignal = Signal(str)

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
        self.ramp_params_menu.addSeparator()
        self.act_tidelays = QAction('Configure TI delays', self)
        self.act_tidelays.triggered.connect(self._showTIDelaysPopup)
        self.ramp_params_menu.addAction(self.act_tidelays)

        self.optics_menu = self.addMenu('Optics Adjustments')
        self.act_optics_settings = QAction('Settings', self)
        self.act_optics_settings.triggered.connect(
            self._showOpticsSettingsPopup)
        self.optics_menu.addAction(self.act_optics_settings)

        self.diag_menu = self.addMenu('Ramp Diagnosis')
        self.act_diag_settings = QAction('Settings', self)
        self.act_diag_settings.triggered.connect(
            self._showDiagSettingsPopup)
        self.diag_menu.addAction(self.act_diag_settings)

        self.open_menu = self.addMenu('Open...')
        self.act_cycle = QAction('PS Cycle')
        _hlautil.connect_window(self.act_cycle, _CycleWindow, parent=self,
                                checked_accs=('BO,'))
        self.act_ma = QAction('Booster Magnets')
        _hlautil.connect_window(self.act_ma, _MAControlWindow, parent=self,
                                section='BO', discipline=1)  # MA
        self.act_pm = QAction('Pulsed Magnets')
        self.act_sofb = QAction('Booster SOFB')
        _hlautil.connect_newprocess(self.act_sofb, 'sirius-hla-bo-ap-sofb.py')
        _hlautil.connect_window(self.act_pm, _PMControlWindow, parent=self)
        self.open_menu.addAction(self.act_cycle)
        self.open_menu.addAction(self.act_ma)
        self.open_menu.addAction(self.act_pm)
        self.open_menu.addAction(self.act_sofb)
        # TODO: include RF and TI windows??

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
            self._tunecorr_name, self._chromcorr_name, self)
        self._opticsSettingsPopup.updateSettings.connect(
            self._emitOpticsSettings)
        self._opticsSettingsPopup.open()

    def _showDiagSettingsPopup(self):
        self._diagSettingsPopup = _DiagnosisSettings(
            self, self.prefix, self._injcurr_idx, self._ejecurr_idx)
        self._diagSettingsPopup.updateSettings.connect(self._emitDiagSettings)
        self._diagSettingsPopup.open()

    def showSaveAsPopup(self):
        """Show a popup to get a new name to save config."""
        if self.ramp_config is None:
            return
        self._saveAsPopup = _NewRampConfigGetName(
            self.ramp_config, 'bo_ramp', self, new_from_template=False)
        self._saveAsPopup.configname.connect(self._saveAndEmitConfigName)
        self._saveAsPopup.open()

    def _showTIDelaysPopup(self):
        # TODO: create dialog to config timing delays
        pass

    def _saveAndEmitConfigName(self, new_name=None):
        if not self.ramp_config:
            return
        try:
            if self.ramp_config.configsrv_exist():
                old_name = self.ramp_config.name
                if not new_name:
                    new_name = _generate_config_name(old_name)
                self.ramp_config.configsrv_save(new_name)
            else:
                self.ramp_config.configsrv_save()
        except _srvexceptions.SrvError as e:
            err_msg = _MessageBox(self, 'Error', str(e), 'Ok')
            err_msg.open()
        else:
            self._emitConfigName(self.ramp_config.name)

    def _emitConfigName(self, config_name):
        self.newConfigNameSignal.emit(config_name)

    def _emitLoadSignal(self):
        self.loadSignal.emit()

    def _emitOpticsSettings(self, settings):
        self._tunecorr_name = settings[0]
        self._chromcorr_name = settings[1]
        self.opticsSettingsSignal.emit(settings)

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
