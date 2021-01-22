"""Booster Ramp Control HLA: Ramp Settings Module."""

from functools import partial as _part

from qtpy.QtCore import Qt, Signal, Slot, QThread
from qtpy.QtGui import QKeySequence
from qtpy.QtWidgets import QMenuBar, QMessageBox, QLabel, QVBoxLayout
import qtawesome as qta

from siriuspy.clientconfigdb import ConfigDBException as _ConfigDBException, \
    PVsConfig as _PVsConfig
from siriuspy.ramp import ramp
from siriuspy.ramp.reconst_factory import BONormListFactory, BORFRampFactory, \
    BOTIRampFactory, BODipRampFactory
from siriushla import util
from siriushla.widgets.windows import SiriusDialog
from siriushla.as_ap_configdb import LoadConfigDialog as _LoadConfigDialog, \
    SaveConfigDialog as _SaveConfigDialog
from .auxiliary_dialogs import OpticsAdjustSettings as _OpticsAdjustSettings, \
    AuxiliaryRFVoltConv as _AuxRFVoltConv


class Settings(QMenuBar):
    """Widget to choose and to control a BoosterRamp configuration."""

    newConfigNameSignal = Signal(str)
    loadSignal = Signal()
    opticsSettingsSignal = Signal(str, str)
    plotUnitSignal = Signal(str)
    newDipConfigSignal = Signal(dict)
    newNormConfigsSignal = Signal(dict)
    newTIConfigSignal = Signal(dict)
    newRFConfigSignal = Signal(dict)

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
        self.act_reconst_dipconf_fromwfm = self.config_menu.addAction(
            'Reconstruct dipole configuration from waveform...')
        self.act_reconst_dipconf_fromwfm.setIcon(qta.icon('mdi.laravel'))
        self.act_reconst_dipconf_fromwfm.triggered.connect(
            _part(self._handleReconstructConfig, 'dipole'))
        self.act_reconst_normconf_fromwfm = self.config_menu.addAction(
            'Reconstruct norm. configurations from waveforms...')
        self.act_reconst_normconf_fromwfm.setIcon(qta.icon('mdi.laravel'))
        self.act_reconst_normconf_fromwfm.triggered.connect(
            _part(self._handleReconstructConfig, 'normconfigs'))
        self.act_reconst_rfparams_frompvs = self.config_menu.addAction(
            'Reconstruct RF parameters from PVs...')
        self.act_reconst_rfparams_frompvs.setIcon(qta.icon('mdi.laravel'))
        self.act_reconst_rfparams_frompvs.triggered.connect(
            _part(self._handleReconstructConfig, 'rf'))
        self.act_reconst_tiparams_frompvs = self.config_menu.addAction(
            'Reconstruct TI parameters from PVs...')
        self.act_reconst_tiparams_frompvs.setIcon(qta.icon('mdi.laravel'))
        self.act_reconst_tiparams_frompvs.triggered.connect(
            _part(self._handleReconstructConfig, 'ti'))
        self.config_menu.addSeparator()

        self.ramp_params_menu = self.addMenu('Ramping Parameters')
        self.menu_plotunits = self.ramp_params_menu.addMenu(
            'Plot waveforms in...')
        self.menu_plotunits.setIcon(qta.icon('mdi.chart-line'))
        self.act_plotcurrents = self.menu_plotunits.addAction('Currents')
        self.act_plotcurrents.triggered.connect(
            _part(self.plotUnitSignal.emit, 'Currents'))
        self.act_plotstrengths = self.menu_plotunits.addAction('Strengths')
        self.act_plotstrengths.triggered.connect(
            _part(self.plotUnitSignal.emit, 'Strengths'))
        self.act_rfconv = self.ramp_params_menu.addAction(
            'RF Voltage Convertion')
        self.act_rfconv.triggered.connect(self._showRFConvDialog)

        self.act_optics = self.addAction('Optics Adjustments Settings')
        self.act_optics.triggered.connect(self._showOpticsSettingsPopup)

        self.open_menu = self.addMenu('Open...')
        self.act_ps = self.open_menu.addAction('PS')
        self.act_ps.setIcon(qta.icon('mdi.car-battery'))
        util.connect_newprocess(
            self.act_ps, 'sirius-hla-bo-ps-control.py', parent=self)
        self.act_pm = self.open_menu.addAction('PU')
        self.act_pm.setIcon(qta.icon('mdi.current-ac'))
        util.connect_newprocess(
            self.act_pm, 'sirius-hla-bo-pu-control.py', parent=self)
        self.act_sofb = self.open_menu.addAction('SOFB')
        self.act_sofb.setIcon(qta.icon('fa5s.hammer'))
        util.connect_newprocess(
            self.act_sofb, 'sirius-hla-bo-ap-sofb.py', parent=self)
        self.act_ti = self.open_menu.addAction('Timing')
        self.act_ti.setIcon(qta.icon('mdi.timer'))
        util.connect_newprocess(
            self.act_ti, 'sirius-hla-as-ti-control.py', parent=self)
        self.act_dcct = self.open_menu.addAction('DCCT')
        self.act_dcct.setIcon(qta.icon('mdi.current-dc'))
        util.connect_newprocess(
            self.act_dcct,
            ['sirius-hla-as-di-dcct.py', 'BO-35D:DI-DCCT'], parent=self)
        self.act_tune = self.open_menu.addAction('Tune')
        self.act_tune.setIcon(qta.icon('mdi.pulse'))
        util.connect_newprocess(
            self.act_tune, 'sirius-hla-bo-di-tune.py', parent=self)

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

        resp = QMessageBox.question(
            self, 'Question',
            "Save a GLOBAL_CONFIG with name '{}'?".format(
                self.ramp_config.name))
        if resp == QMessageBox.Yes:
            global_config = _PVsConfig(config_type='global_config')
            global_config.read_and_save(self.ramp_config.name)

    def _showOpticsSettingsPopup(self):
        opticsSettingsPopup = _OpticsAdjustSettings(
            self._tunecorr_configname, self._chromcorr_configname, self)
        opticsSettingsPopup.updateSettings.connect(self._emitOpticsSettings)
        opticsSettingsPopup.open()

    def _showRFConvDialog(self):
        wind = _AuxRFVoltConv(self)
        wind.open()

    @Slot(str, str)
    def _emitOpticsSettings(self, tunecorr_configname, chromcorr_configname):
        self._tunecorr_configname = tunecorr_configname
        self._chromcorr_configname = chromcorr_configname
        self.opticsSettingsSignal.emit(
            tunecorr_configname, chromcorr_configname)

    def _handleReconstructConfig(self, params2reconstruct):
        if self.ramp_config is None:
            return
        if not self.verifyUnsavedChanges():
            return
        ans = QMessageBox.question(
            self, 'Question', 'Are you sure you want to proceed?',
            QMessageBox.Yes | QMessageBox.Cancel)
        if ans == QMessageBox.Cancel:
            return

        if params2reconstruct == 'dipole':
            th = _WaitThread(params2reconstruct='dipole',
                             ramp_config=self.ramp_config,
                             parent=self)
            th.configData.connect(self.newDipConfigSignal.emit)
        elif params2reconstruct == 'normconfigs':
            th = _WaitThread(params2reconstruct='normconfigs',
                             ramp_config=self.ramp_config,
                             parent=self)
            th.configData.connect(self.newNormConfigsSignal.emit)
            th.precReached.connect(self._showWarningPrecNotOk)
        elif params2reconstruct == 'ti':
            th = _WaitThread(params2reconstruct='ti', parent=self)
            th.configData.connect(self.newTIConfigSignal.emit)
        elif params2reconstruct == 'rf':
            th = _WaitThread(params2reconstruct='rf', parent=self)
            th.configData.connect(self.newRFConfigSignal.emit)
        dlg = _WaitDialog(self)
        th.opendiag.connect(dlg.show)
        th.closediag.connect(dlg.close)
        th.error.connect(self._showErrorMessage)
        th.start()

    @Slot(bool, float)
    def _showWarningPrecNotOk(self, prec_ok, max_error):
        if not prec_ok:
            QMessageBox.warning(
                self, 'Warning',
                'Reconstruction was unable to reproduce waveforms\n'
                'with 1e-5 accuracy (maximum error: {:.4g})!'.format(
                    max_error))

    @Slot(str)
    def _showErrorMessage(self, text):
        QMessageBox.critical(self, 'Error', text)

    @Slot(ramp.BoosterRamp)
    def getRampConfig(self, ramp_config):
        """Get new BoosterRamp object."""
        self.ramp_config = ramp_config


class _WaitDialog(SiriusDialog):
    """Auxiliary dialog to show during a long task."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Wait')
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel('Wait a moment...'))


class _WaitThread(QThread):

    opendiag = Signal()
    closediag = Signal()
    configData = Signal(dict)
    precReached = Signal(bool, float)
    error = Signal(str)

    def __init__(self, params2reconstruct='', ramp_config=None, parent=None):
        super().__init__(parent)
        self.params2reconstruct = params2reconstruct
        self.ramp_config = ramp_config

    def run(self):
        self.opendiag.emit()
        try:
            if self.params2reconstruct == 'dipole':
                dip_fac = BODipRampFactory(self.ramp_config)
                dip_fac.read_waveform()
                params = dip_fac.dip_params
            elif self.params2reconstruct == 'normconfigs':
                norm_fac = BONormListFactory(self.ramp_config)
                norm_fac.read_waveforms()
                params = norm_fac.normalized_configs
            elif self.params2reconstruct == 'ti':
                ti_fac = BOTIRampFactory()
                params = ti_fac.ti_params
            else:
                rf_fac = BORFRampFactory()
                params = rf_fac.rf_params
        except Exception as e:
            self.error.emit(str(e))
        else:
            self.configData.emit(params)
            if self.params2reconstruct == 'normconfigs':
                ok, max_error = norm_fac.precision_reached
                self.precReached.emit(ok, max_error)
        finally:
            self.closediag.emit()
