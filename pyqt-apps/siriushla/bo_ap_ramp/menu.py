"""Booster Ramp Control HLA: Ramp Settings Module."""

from functools import partial as _part

from qtpy.QtCore import Qt, Signal, Slot
from qtpy.QtGui import QKeySequence
from qtpy.QtWidgets import QMenuBar, QAction, QMessageBox
import qtawesome as qta

from siriuspy.clientconfigdb import ConfigDBException as _ConfigDBException
from siriuspy.ramp import ramp
from siriushla import util
from siriushla.as_ap_configdb import LoadConfigDialog as _LoadConfigDialog, \
    SaveConfigDialog as _SaveConfigDialog
from .auxiliary_dialogs import OpticsAdjustSettings as _OpticsAdjustSettings


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
        self._setupUi()

    def _setupUi(self):
        self.setStyleSheet(
            """QMenuBar::item {\npadding: 0 1em 0 0.17em;\n}""")
        self.config_menu = self.addMenu('Booster Ramp Configuration')
        self.act_new = self.config_menu.addAction('New from template')
        self.act_new.setIcon(qta.icon('mdi.file'))
        self.act_new.setShortcut(QKeySequence.New)
        self.act_new.triggered.connect(self.createNewConfigFromTemplate)
        self.act_load = self.config_menu.addAction('Load existing config...')
        self.act_load.setIcon(qta.icon('mdi.folder-open'))
        self.act_load.setShortcut(QKeySequence.Open)
        self.act_load.triggered.connect(self.showLoadExistingConfigPopup)
        self.act_save = self.config_menu.addAction('Save')
        self.act_save.setIcon(qta.icon('mdi.content-save'))
        self.act_save.setShortcut(QKeySequence.Save)
        self.act_save.triggered.connect(self._saveAndEmitConfigName)
        self.act_save_as = self.config_menu.addAction('Save As...')
        self.act_save_as.setIcon(qta.icon('mdi.content-save-settings'))
        self.act_save_as.setShortcut(QKeySequence(Qt.CTRL+Qt.SHIFT+Qt.Key_S))
        self.act_save_as.triggered.connect(self.showSaveAsPopup)
        self.config_menu.addSeparator()

        self.ramp_params_menu = self.addMenu('Ramping Parameters')
        self.menu_plotunits = self.ramp_params_menu.addMenu(
            'Plot magnet waveforms in...')
        self.menu_plotunits.setIcon(qta.icon('mdi.chart-line'))
        self.act_plotcurrents = self.menu_plotunits.addAction('Currents')
        self.act_plotcurrents.triggered.connect(
            _part(self.plotUnitSignal.emit, 'Currents'))
        self.act_plotstrengths = self.menu_plotunits.addAction('Strengths')
        self.act_plotstrengths.triggered.connect(
            _part(self.plotUnitSignal.emit, 'Strengths'))

        self.act_optics = self.addAction('Optics Adjustments Settings')
        self.act_optics.triggered.connect(self._showOpticsSettingsPopup)

        self.diag_menu = self.addMenu('Ramp Diagnosis')
        self.act_dcct = self.diag_menu.addAction('DCCT')
        self.act_dcct.setIcon(qta.icon('mdi.current-dc'))
        util.connect_newprocess(
            self.act_dcct, ['sirius-hla-as-di-dcct.py', 'BO'], parent=self)
        # TODO: menu to access all windows related to diagnostics

        self.open_menu = self.addMenu('Open...')
        self.act_ma = QAction('MA', self)
        self.act_ma.setIcon(qta.icon('mdi.magnet'))
        util.connect_newprocess(self.act_ma, 'sirius-hla-bo-ma-control.py',
                                parent=self)
        self.act_pm = QAction('PM', self)
        self.act_pm.setIcon(qta.icon('mdi.current-ac'))
        util.connect_newprocess(self.act_pm, 'sirius-hla-bo-pm-control.py',
                                parent=self)
        self.act_sofb = QAction('SOFB', self)
        self.act_sofb.setIcon(qta.icon('mdi.hammer'))
        util.connect_newprocess(self.act_sofb, 'sirius-hla-bo-ap-sofb.py',
                                parent=self)
        self.act_ti = QAction('Timing', self)
        self.act_ti.setIcon(qta.icon('mdi.timer'))
        util.connect_newprocess(self.act_ti, 'sirius-hla-as-ti-control.py',
                                parent=self)
        self.open_menu.addAction(self.act_ma)
        self.open_menu.addAction(self.act_pm)
        self.open_menu.addAction(self.act_sofb)
        self.open_menu.addAction(self.act_ti)

    def verifyUnsavedChanges(self):
        if self.ramp_config is None or self.ramp_config.synchronized:
            return True
        ans = QMessageBox.question(
            self, 'Save changes?', 'There are unsaved changes in {}.\n'
            'Do you want to save?'.format(self.ramp_config.name),
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        if ans == QMessageBox.Yes:
            self._saveAndEmitConfigName()
            return False
        elif ans == QMessageBox.No:
            return True
        elif ans == QMessageBox.Cancel:
            return False

    def createNewConfigFromTemplate(self):
        if not self.verifyUnsavedChanges():
            return
        self.newConfigNameSignal.emit('**New Configuration**')

    def showLoadExistingConfigPopup(self):
        """Show popup to load an existing config."""
        if not self.verifyUnsavedChanges():
            return
        self._loadPopup = _LoadConfigDialog('bo_ramp', self)
        self._loadPopup.setWindowTitle('Load ramp configuration...')
        self._loadPopup.configname.connect(self.newConfigNameSignal.emit)
        self._loadPopup.open()

    def showSaveAsPopup(self):
        """Show a popup to get a new name to save config."""
        if self.ramp_config is None:
            return
        self._saveAsPopup = _SaveConfigDialog('bo_ramp', self)
        self._saveAsPopup.setWindowTitle('Save ramp configuration as...')
        self._saveAsPopup.configname.connect(self._saveAndEmitConfigName)
        self._saveAsPopup.open()

    def _saveAndEmitConfigName(self, new_name=None):
        if self.ramp_config is None:
            return
        if not new_name:
            new_name = None
            if self.ramp_config.name == '**New Configuration**':
                self.showSaveAsPopup()
                return
        try:
            self.ramp_config.save(new_name)
        except _ConfigDBException as err:
            QMessageBox.critical(self, 'Error', str(err), QMessageBox.Ok)
        else:
            self.loadSignal.emit()

    def _showOpticsSettingsPopup(self):
        self._opticsSettingsPopup = _OpticsAdjustSettings(
            self._tunecorr_configname, self._chromcorr_configname, self)
        self._opticsSettingsPopup.updateSettings.connect(
            self._emitOpticsSettings)
        self._opticsSettingsPopup.open()

    @Slot(str, str)
    def _emitOpticsSettings(self, tunecorr_configname, chromcorr_configname):
        self._tunecorr_configname = tunecorr_configname
        self._chromcorr_configname = chromcorr_configname
        self.opticsSettingsSignal.emit(
            tunecorr_configname, chromcorr_configname)

    @Slot(ramp.BoosterRamp)
    def getRampConfig(self, ramp_config):
        """Get new BoosterRamp object."""
        self.ramp_config = ramp_config
