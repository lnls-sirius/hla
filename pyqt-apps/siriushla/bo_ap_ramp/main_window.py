"""Booster Ramp Main Window."""

import sys
from qtpy.QtCore import Slot, Signal, Qt
from qtpy.QtGui import QKeySequence
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, QUndoStack
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets.windows import SiriusMainWindow
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriushla import util as _util
from siriuspy.ramp import ramp
from siriuspy.ramp.conn import ConnMagnets as _ConnMagnets, ConnRF as _ConnRF,\
                               ConnTiming as _ConnTiming, ConnSOFB as _ConnSOFB
from siriuspy.servconf import exceptions as _srvexceptions
from siriushla.bo_ap_ramp.status_and_commands import StatusAndCommands
from siriushla.bo_ap_ramp.settings import Settings
from siriushla.bo_ap_ramp.config_params import ConfigParameters
from siriushla.bo_ap_ramp.optics_adjust import OpticsAdjust
from siriushla.bo_ap_ramp.diagnosis import Diagnosis
from siriushla.bo_ap_ramp.auxiliar_classes import MessageBox as _MessageBox


class RampMain(SiriusMainWindow):
    """Main window of Booster Ramp Control HLA."""

    connUpdateSignal = Signal(_ConnMagnets, _ConnTiming, _ConnRF, _ConnSOFB)
    loadSignal = Signal(ramp.BoosterRamp)

    def __init__(self, parent=None, prefix=''):
        """Initialize object."""
        super().__init__(parent)
        self.setWindowTitle('Booster Energy Ramping')
        self.prefix = prefix
        self.ramp_config = None
        self._conn_magnets = None
        self._conn_timing = None
        self._undo_stack = QUndoStack(self)
        self._setupUi()
        self._connSignals()
        self._addActions()

    def _setupUi(self):
        cw = QWidget(self)
        self.setCentralWidget(cw)
        self.my_layout = QGridLayout(cw)
        self.my_layout.setHorizontalSpacing(20)
        self.my_layout.setVerticalSpacing(20)
        lab = QLabel('<h3>Booster Energy Ramping</h3>', cw,
                     alignment=Qt.AlignRight)
        lab.setStyleSheet('background-color: qlineargradient('
                          'spread:pad, x1:1, y1:0.0227273, x2:0, y2:0,'
                          'stop:0 rgba(173, 190, 207, 255),'
                          'stop:1 rgba(213, 213, 213, 255))')
        self.my_layout.addWidget(lab, 0, 0, 1, 2)

        self.settings = Settings(
            self, self.prefix, self.ramp_config)
        self.setMenuBar(self.settings)

        self.config_parameters = ConfigParameters(
            self, self.prefix, self.ramp_config, self._undo_stack)
        self.my_layout.addWidget(self.config_parameters, 1, 0, 5, 1)

        self.optics_adjust = OpticsAdjust(self, self.prefix, self.ramp_config)
        self.my_layout.addWidget(self.optics_adjust, 6, 0, 2, 1)

        self.status_and_commands = StatusAndCommands(self, self.prefix)
        self.my_layout.addWidget(self.status_and_commands, 1, 1, 2, 1)

        self.diagnosis = Diagnosis(self, self.prefix, self.ramp_config)
        self.my_layout.addWidget(self.diagnosis, 3, 1, 5, 1)

    def _connSignals(self):
        self.settings.newConfigNameSignal.connect(self._receiveNewConfigName)
        self.settings.loadSignal.connect(self._emitLoadSignal)
        self.settings.opticsSettingsSignal.connect(
            self.optics_adjust.handleUpdateSettings)
        self.settings.diagSettingsSignal.connect(
            self.diagnosis.handleUpdateSettings)
        self.settings.plotUnitSignal.connect(
            self.config_parameters.getPlotUnits)

        self.config_parameters.dip_ramp.updateDipoleRampSignal.connect(
            self._verifySync)
        self.config_parameters.dip_ramp.updateDipoleRampSignal.connect(
            self.config_parameters.mult_ramp.updateTable)
        self.config_parameters.dip_ramp.updateDipoleRampSignal.connect(
            self.config_parameters.mult_ramp.updateGraph)
        self.config_parameters.mult_ramp.updateMultipoleRampSignal.connect(
            self._verifySync)
        self.config_parameters.mult_ramp.configsIndexChangedSignal.connect(
            self.optics_adjust.getConfigIndices)
        self.config_parameters.rf_ramp.updateRFRampSignal.connect(
            self._verifySync)

        self.optics_adjust.normConfigChanged.connect(
            self.config_parameters.mult_ramp.handleNormConfigsChanged)

        self.connUpdateSignal.connect(self.optics_adjust.getConnectors)
        self.connUpdateSignal.connect(self.status_and_commands.getConnectors)

        self.loadSignal.connect(self.settings.getRampConfig)
        self.loadSignal.connect(self.config_parameters.handleLoadRampConfig)
        self.loadSignal.connect(
            self.config_parameters.dip_ramp.handleLoadRampConfig)
        self.loadSignal.connect(
            self.config_parameters.mult_ramp.handleLoadRampConfig)
        self.loadSignal.connect(
            self.config_parameters.rf_ramp.handleLoadRampConfig)
        self.loadSignal.connect(self.optics_adjust.handleLoadRampConfig)

    def _addActions(self):
        self.act_undo = self._undo_stack.createUndoAction(self, 'Undo')
        self.act_undo.setShortcut(QKeySequence.Undo)
        self.settings.config_menu.addAction(self.act_undo)
        self.act_redo = self._undo_stack.createRedoAction(self, 'Redo')
        self.act_redo.setShortcut(QKeySequence.Redo)
        self.settings.config_menu.addAction(self.act_redo)

    @Slot(str)
    def _receiveNewConfigName(self, new_config_name):
        self.ramp_config = ramp.BoosterRamp(new_config_name, auto_update=True)
        self._emitLoadSignal()

    def _emitConnectors(self):
        self._conn_magnets = _ConnMagnets(
            ramp_config=self.ramp_config, prefix=self.prefix,
            connection_callback=self.status_and_commands.updateMAConn,
            callback=self.status_and_commands.updateMAStatus)
        self._conn_timing = _ConnTiming(
            ramp_config=self.ramp_config, prefix=self.prefix,
            connection_callback=self.status_and_commands.updateTIConn,
            callback=self.status_and_commands.updateTIStatus)
        self._conn_rf = _ConnRF(
            ramp_config=self.ramp_config, prefix=self.prefix,
            connection_callback=self.status_and_commands.updateRFConn,
            callback=self.status_and_commands.updateRFStatus)
        self._conn_sofb = _ConnSOFB(
            ramp_config=self.ramp_config, prefix=self.prefix,
            connection_callback=self.status_and_commands.updateSOFBConn)
        self.connUpdateSignal.emit(self._conn_magnets, self._conn_timing,
                                   self._conn_rf, self._conn_sofb)

    def _emitLoadSignal(self):
        try:
            if self.ramp_config.configsrv_exist():
                self.ramp_config.configsrv_load()
        except _srvexceptions.SrvError as e:
            err_msg = _MessageBox(self, 'Error', str(e), 'Ok')
            err_msg.open()
        else:
            self.loadSignal.emit(self.ramp_config)
            self._emitConnectors()
        finally:
            self._verifySync()

    def _verifySync(self):
        """Verify sync status related to ConfServer."""
        if self.ramp_config is not None:
            if not self.ramp_config.configsrv_synchronized:
                self.config_parameters.setStyleSheet('QGroupBox {color: red;}')
                self.config_parameters.setToolTip('There are unsaved changes')
            else:
                self.config_parameters.setStyleSheet('')
                self.config_parameters.setToolTip('')

    def closeEvent(self, ev):
        """Reimplement closeEvent to avoid forgeting saving changes."""
        self.close_ev = ev

        if self.ramp_config is None:
            return self._acceptClose()

        if not self.ramp_config.configsrv_synchronized:
            save_changes = _MessageBox(
                self, 'Save changes?',
                'There are unsaved changes in {}. \n'
                'Do you want to save?'.format(self.ramp_config.name),
                'Yes', 'Cancel')
            save_changes.acceptedSignal.connect(self._ignoreCloseAndSave)
            save_changes.rejectedSignal.connect(self._acceptClose)
            save_changes.exec_()

    def _ignoreCloseAndSave(self):
        self.close_ev.ignore()
        self.settings.showSaveAsPopup()

    def _acceptClose(self):
        self.close_ev.accept()
        super().closeEvent(self.close_ev)


if __name__ == '__main__':
    """Run Example."""
    app = SiriusApplication()
    _util.set_style(app)
    w = RampMain(prefix=_vaca_prefix)
    w.show()
    sys.exit(app.exec_())
