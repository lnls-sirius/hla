"""Booster Ramp Main Window."""

import sys
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QLabel, QWidget, QGridLayout, QUndoStack
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets.windows import SiriusMainWindow
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriushla import util as _util
from siriuspy.ramp import ramp
from siriuspy.ramp.conn import ConnMagnets as _ConnMagnets, \
                               ConnTiming as _ConnTiming
from siriushla.bo_ramp.general_status import GeneralStatus
from siriushla.bo_ramp.ramp_settings import RampConfigSettings
from siriushla.bo_ramp.ramp_commands import RampCommands
from siriushla.bo_ramp.ramp_params import RampParameters
from siriushla.bo_ramp.optics_adjust import OpticsAdjust
from siriushla.bo_ramp.ramp_statistics import RampStatistics


class RampMain(SiriusMainWindow):
    """Main window of Booster Ramp Control HLA."""

    connUpdateSignal = pyqtSignal(_ConnMagnets, _ConnTiming)
    loadSignal = pyqtSignal(ramp.BoosterRamp)

    def __init__(self, parent=None, prefix=''):
        """Initialize object."""
        super().__init__(parent)
        self.setWindowTitle('Booster Energy Ramping')
        self.prefix = _PVName(prefix)
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
        lab = QLabel('<h3>Booster Energy Ramping</h3>', cw)
        lab.setStyleSheet('background-color: qlineargradient('
                          'spread:pad, x1:0, y1:0.0227273, x2:1, y2:0,'
                          'stop:0 rgba(173, 190, 207, 255),'
                          'stop:1 rgba(213, 213, 213, 255))')
        self.my_layout.addWidget(lab, 0, 0, 1, 2)

        self.ramp_settings = RampConfigSettings(
            self, self.prefix, self.ramp_config)
        self.setMenuBar(self.ramp_settings)

        self.ramp_parameters = RampParameters(
            self, self.prefix, self.ramp_config, self._undo_stack)
        self.my_layout.addWidget(self.ramp_parameters, 1, 0, 5, 1)

        self.optics_adjust = OpticsAdjust(self, self.prefix, self.ramp_config)
        self.my_layout.addWidget(self.optics_adjust, 6, 0, 2, 1)

        self.general_status = GeneralStatus(self, self.prefix)
        self.my_layout.addWidget(self.general_status, 1, 1, 1, 1)

        self.statistics = RampStatistics(self, self.prefix,
                                         self.ramp_config)
        self.my_layout.addWidget(self.statistics, 2, 1, 5, 1)

        self.commands = RampCommands(self, self.prefix)
        self.my_layout.addWidget(self.commands, 7, 1, 1, 1)

    def _connSignals(self):
        self.ramp_settings.configNameSignal.connect(self._receiveNewConfigName)
        self.ramp_settings.loadSignal.connect(self._emitLoadSignal)
        self.ramp_settings.saveSignal.connect(self._verifySync)
        self.ramp_settings.opticsSettingsSignal.connect(
            self.optics_adjust.handleUpdateSettings)
        self.ramp_settings.statsSettingsSignal.connect(
            self.statistics.handleUpdateSettings)

        self.ramp_parameters.dip_ramp.updateDipoleRampSignal.connect(
            self._verifySync)
        self.ramp_parameters.dip_ramp.updateDipoleRampSignal.connect(
            self.ramp_parameters.mult_ramp.updateTable)
        self.ramp_parameters.dip_ramp.updateDipoleRampSignal.connect(
            self.ramp_parameters.mult_ramp.updateGraph)
        self.ramp_parameters.mult_ramp.updateMultipoleRampSignal.connect(
            self._verifySync)
        self.ramp_parameters.mult_ramp.configsIndexChangedSignal.connect(
            self.optics_adjust.getConfigIndices)

        self.optics_adjust.normConfigChanged.connect(
            self.ramp_parameters.mult_ramp.handleNormConfigsChanges)

        self.connUpdateSignal.connect(self.general_status.getConnectors)
        self.connUpdateSignal.connect(self.commands.getConnectors)

        self.loadSignal.connect(self.ramp_settings.getRampConfig)
        self.loadSignal.connect(self.ramp_parameters.handleLoadRampConfig)
        self.loadSignal.connect(
            self.ramp_parameters.dip_ramp.handleLoadRampConfig)
        self.loadSignal.connect(
            self.ramp_parameters.mult_ramp.handleLoadRampConfig)
        self.loadSignal.connect(
            self.ramp_parameters.rf_ramp.handleLoadRampConfig)
        self.loadSignal.connect(self.optics_adjust.handleLoadRampConfig)

    def _addActions(self):
        self.act_undo = self._undo_stack.createUndoAction(self, 'Undo')
        self.act_undo.setShortcut(QKeySequence.Undo)
        self.ramp_settings.config_menu.addAction(self.act_undo)
        self.act_redo = self._undo_stack.createRedoAction(self, 'Redo')
        self.act_redo.setShortcut(QKeySequence.Redo)
        self.ramp_settings.config_menu.addAction(self.act_redo)

    @pyqtSlot(str)
    def _receiveNewConfigName(self, new_config_name):
        self.ramp_config = ramp.BoosterRamp(new_config_name, auto_update=True)
        if self.ramp_config.configsrv_exist():
            self.ramp_config.configsrv_load()
        self._emitLoadSignal()

    def _emitConnectors(self):
        self._conn_magnets = _ConnMagnets(
            ramp_config=self.ramp_config,
            prefix=self.prefix,
            connection_callback=self.general_status.updateMagnetsConnState,
            callback=self.general_status.updateMagnetsOpModeState)
        self._conn_timing = _ConnTiming(
            ramp_config=self.ramp_config,
            prefix=self.prefix,
            connection_callback=self.general_status.updateTimingConnState,
            callback=self.general_status.updateTimingOpModeState)
        self.connUpdateSignal.emit(self._conn_magnets, self._conn_timing)

    def _emitLoadSignal(self):
        self.loadSignal.emit(self.ramp_config)
        self._emitConnectors()
        self._verifySync()

    def _verifySync(self):
        """Verify sync status related to ConfServer."""
        if self.ramp_config is not None:
            if not self.ramp_config.configsrv_synchronized:
                self.ramp_parameters.setStyleSheet('QGroupBox {color: red;}')
                self.ramp_parameters.setToolTip('There are unsaved changes')
            else:
                self.ramp_parameters.setStyleSheet('')
                self.ramp_parameters.setToolTip('')


if __name__ == '__main__':
    """Run Example."""
    app = SiriusApplication()
    _util.set_style(app)
    w = RampMain(prefix=_vaca_prefix+'AS-Glob:TI-EVG:')
    w.show()
    sys.exit(app.exec_())
