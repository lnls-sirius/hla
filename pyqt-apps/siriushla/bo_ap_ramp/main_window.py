"""Booster Ramp Main Window."""

from copy import deepcopy as _dcopy

from qtpy.QtCore import Qt, Slot, Signal
from qtpy.QtGui import QKeySequence, QPalette
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, \
                           QUndoStack, QMessageBox
import qtawesome as qta

from siriuspy.ramp import ramp
from siriuspy.clientconfigdb import ConfigDBException as _ConfigDBException

from siriushla.util import get_appropriate_color
from siriushla.widgets.windows import SiriusMainWindow
from .menu import Settings
from .boramp_edit import ConfigParameters
from .status_and_commands import StatusAndCommands


class RampMain(SiriusMainWindow):
    """Main window of Booster Ramp Control HLA."""

    loadSignal = Signal(ramp.BoosterRamp)

    def __init__(self, parent=None, prefix=''):
        """Initialize object."""
        super().__init__(parent)
        self.setWindowTitle('Booster Energy Ramping')
        self.setObjectName('BOApp')
        cor = get_appropriate_color(section='BO')
        self.setWindowIcon(qta.icon(
            'mdi.escalator', scale_factor=1.5, color=cor))

        self.prefix = prefix
        self.ramp_config = None
        self._undo_stack = QUndoStack(self)

        self._tunecorr_configname = 'BO.V05.04.M0'
        self._chromcorr_configname = 'BO.V05.04.M0'

        self._setupUi()
        self._connSignals()
        self._addActions()

        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        cw = QWidget(self)
        glay = QGridLayout(cw)
        glay.setHorizontalSpacing(10)
        glay.setVerticalSpacing(10)
        lab = QLabel('<h3>Booster Energy Ramping</h3>', cw)
        lab.setStyleSheet("""
            min-height:1.55em; max-height: 1.55em;
            qproperty-alignment: 'AlignVCenter | AlignRight';
            background-color: qlineargradient(spread:pad, x1:1, y1:0.0227273,
                              x2:0, y2:0, stop:0 rgba(173, 190, 207, 255),
                              stop:1 rgba(213, 213, 213, 255));""")
        glay.addWidget(lab, 0, 0, 1, 2)

        self.settings = Settings(
            self, self.prefix, self.ramp_config,
            self._tunecorr_configname, self._chromcorr_configname)
        self.setMenuBar(self.settings)

        self.status_and_commands = StatusAndCommands(
            self, self.prefix, self.ramp_config)
        glay.addWidget(self.status_and_commands, 1, 1)

        self.config_parameters = ConfigParameters(
            self, self.prefix, self.ramp_config, self._undo_stack,
            self._tunecorr_configname, self._chromcorr_configname)
        self.config_parameters.setObjectName('ConfigParameters')
        glay.addWidget(self.config_parameters, 1, 0)

        glay.setColumnStretch(0, 15)
        glay.setColumnStretch(1, 1)
        self.setCentralWidget(cw)

    def _connSignals(self):
        self.settings.newConfigNameSignal.connect(self._receiveNewConfigName)
        self.settings.loadSignal.connect(self._emitLoadSignal)
        self.settings.opticsSettingsSignal.connect(
            self._handleUpdateOpticsAdjustSettings)
        self.settings.plotUnitSignal.connect(
            self.config_parameters.getPlotUnits)
        self.settings.newNormConfigsSignal.connect(self._receiveNewNormConfigs)
        self.settings.newTIConfig.connect(self._receiveNewTIConfig)
        self.settings.newRFConfig.connect(self._receiveNewRFConfig)

        self.config_parameters.dip_ramp.updateDipoleRampSignal.connect(
            self._verifySync)
        self.config_parameters.dip_ramp.updateDipoleRampSignal.connect(
            self.config_parameters.mult_ramp.updateTable)
        self.config_parameters.dip_ramp.updateDipoleRampSignal.connect(
            self.config_parameters.mult_ramp.updateGraph)
        self.config_parameters.dip_ramp.updateDipoleRampSignal.connect(
            self.config_parameters.rf_ramp.updateGraph)
        self.config_parameters.dip_ramp.updateDipoleRampSignal.connect(
            self.status_and_commands.update_ps_params)
        self.config_parameters.dip_ramp.updateDipoleRampSignal.connect(
            self.status_and_commands.update_ti_params)
        self.config_parameters.dip_ramp.applyChanges2MachineSignal.connect(
            self.status_and_commands.apply_changes)
        self.config_parameters.mult_ramp.updateMultipoleRampSignal.connect(
            self._verifySync)
        self.config_parameters.mult_ramp.updateMultipoleRampSignal.connect(
            self.status_and_commands.update_ps_params)
        self.config_parameters.mult_ramp.applyChanges2MachineSignal.connect(
            self.status_and_commands.apply_changes)
        self.config_parameters.mult_ramp.plotUnitSignal.connect(
            self.config_parameters.getPlotUnits)
        self.config_parameters.rf_ramp.updateRFRampSignal.connect(
            self._verifySync)
        self.config_parameters.rf_ramp.updateRFRampSignal.connect(
            self.status_and_commands.update_rf_params)
        self.config_parameters.rf_ramp.updateRFRampSignal.connect(
            self.status_and_commands.update_ti_params)
        self.config_parameters.rf_ramp.applyChanges2MachineSignal.connect(
            self.status_and_commands.apply_changes)

        self.status_and_commands.inj_eje_times.connect(
            self.config_parameters.dip_ramp.updateInjEjeTimes)

        self.loadSignal.connect(self.settings.getRampConfig)
        self.loadSignal.connect(self.config_parameters.handleLoadRampConfig)
        self.loadSignal.connect(self.status_and_commands.handleLoadRampConfig)

    def _addActions(self):
        self.act_undo = self._undo_stack.createUndoAction(self, 'Undo')
        self.act_undo.setIcon(qta.icon('mdi.undo'))
        self.act_undo.setShortcut(QKeySequence.Undo)
        self.settings.config_menu.addAction(self.act_undo)
        self.act_redo = self._undo_stack.createRedoAction(self, 'Redo')
        self.act_redo.setIcon(qta.icon('mdi.redo'))
        self.act_redo.setShortcut(QKeySequence.Redo)
        self.settings.config_menu.addAction(self.act_redo)

    @Slot(str)
    def _receiveNewConfigName(self, new_config_name):
        if self.ramp_config is None or \
                self.ramp_config.name != new_config_name or \
                self.ramp_config.name == '**New Configuration**':
            self.ramp_config = ramp.BoosterRamp(new_config_name,
                                                auto_update=True)
            self._undo_stack.clear()
        self._emitLoadSignal()

    @Slot(dict)
    def _receiveNewNormConfigs(self, norm_configs):
        old_norm_configs = _dcopy(
            self.config_parameters.mult_ramp.normalized_configs)
        self.ramp_config.ps_normalized_configs_set(norm_configs)
        self.loadSignal.emit(self.ramp_config)
        self._verifySync()
        new_norm_configs = _dcopy(
            self.config_parameters.mult_ramp.normalized_configs)
        self.config_parameters.mult_ramp.stackUndoMultipoleTableCommand(
            description='reconstruct normalized configs from waveforms',
            old=old_norm_configs, new=new_norm_configs)

    @Slot(dict)
    def _receiveNewTIConfig(self, params):
        for param, value in params.items():
            attr_name = 'ti_params_'+param
            setattr(self.ramp_config, attr_name, value)
        self.loadSignal.emit(self.ramp_config)
        self._verifySync()

    @Slot(dict)
    def _receiveNewRFConfig(self, params):
        for param, value in params.items():
            if 'duration' in param:
                continue
            attr_name = 'rf_ramp_'+param
            setattr(self.ramp_config, attr_name, value)
        self.ramp_config.rf_ramp_rampup_start_time = params['bottom_duration']
        self.ramp_config.rf_ramp_rampup_stop_time = \
            params['bottom_duration'] + \
            params['rampup_duration']
        self.ramp_config.rf_ramp_rampdown_start_time = \
            params['bottom_duration'] + \
            params['rampup_duration'] + \
            params['top_duration']
        self.ramp_config.rf_ramp_rampdown_stop_time = \
            params['bottom_duration'] + \
            params['rampup_duration'] + \
            params['top_duration'] + \
            params['rampdown_duration']
        self.loadSignal.emit(self.ramp_config)
        self._verifySync()

    def _emitLoadSignal(self):
        try:
            if self.ramp_config.exist():
                self.ramp_config.load()
        except _ConfigDBException as err:
            QMessageBox.critical(self, 'Error', str(err), QMessageBox.Ok)
        else:
            self.loadSignal.emit(self.ramp_config)
        finally:
            self._verifySync()

    def _verifySync(self):
        """Verify sync status related to ConfServer."""
        if self.ramp_config is not None:
            if not self.ramp_config.synchronized:
                pal = self.config_parameters.palette()
                pal.setColor(QPalette.Text, Qt.red)
                self.config_parameters.setPalette(pal)
                self.config_parameters.setToolTip('There are unsaved changes')
            else:
                pal = self.config_parameters.palette()
                pal.setColor(QPalette.Text, Qt.black)
                self.config_parameters.setPalette(pal)
                self.config_parameters.setToolTip('')

    def closeEvent(self, ev):
        """Reimplement closeEvent to avoid forgeting saving changes."""
        if self.ramp_config is None:
            ev.accept()
            super().closeEvent(ev)
        elif not self.ramp_config.synchronized:
            accept = self.settings.verifyUnsavedChanges()
            if accept:
                ev.accept()
                super().closeEvent(ev)
            else:
                ev.ignore()

    @Slot(str, str)
    def _handleUpdateOpticsAdjustSettings(self, tune_cname, chrom_cname):
        self._tunecorr_configname = tune_cname
        self._chromcorr_configname = chrom_cname
        self.config_parameters.updateOpticsAdjustSettings(
            tune_cname, chrom_cname)


if __name__ == '__main__':
    """Run Example."""
    import sys
    from siriushla.sirius_application import SiriusApplication
    from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX

    app = SiriusApplication()
    w = RampMain(prefix=_VACA_PREFIX)
    w.show()
    sys.exit(app.exec_())
