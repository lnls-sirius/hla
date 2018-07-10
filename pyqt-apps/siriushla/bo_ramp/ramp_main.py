"""Booster Ramp Main Window."""

import sys
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QLabel, QWidget, QGridLayout
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets.windows import SiriusMainWindow
from siriuspy.namesys import SiriusPVName as _PVName
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

    def __init__(self, parent=None, prefix=''):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self.ramp_config = None
        self._conn_magnets = None
        self._conn_timing = None
        self._setupUi()
        self._connSignals()

    def _setupUi(self):
        cw = QWidget(self)
        self.setCentralWidget(cw)
        self.my_layout = QGridLayout(cw)
        self.my_layout.setHorizontalSpacing(20)
        self.my_layout.setVerticalSpacing(20)
        lab = QLabel('<h1>Booster Energy Ramping</h1>', cw)
        self.my_layout.addWidget(lab, 0, 0, 1, 3)
        self.my_layout.setAlignment(lab, Qt.AlignCenter)

        self.general_status = GeneralStatus(self, self.prefix)
        self.my_layout.addWidget(self.general_status, 1, 0)

        self.ramp_settings = RampConfigSettings(self, self.prefix,
                                                self.ramp_config)
        self.my_layout.addWidget(self.ramp_settings, 2, 0)

        self.commands = RampCommands(self, self.prefix)
        self.my_layout.addWidget(self.commands, 3, 0)

        self.ramp_parameters = RampParameters(self, self.prefix,
                                              self.ramp_config)
        self.my_layout.addWidget(self.ramp_parameters, 1, 1, 2, 1)

        self.optics_adjust = OpticsAdjust(self, self.prefix)
        self.my_layout.addWidget(self.optics_adjust, 3, 1)

        self.statistics = RampStatistics(self, self.prefix,
                                         self.ramp_config)
        self.my_layout.addWidget(self.statistics, 1, 2, 3, 1)

    def _connSignals(self):
        self.ramp_settings.configSignal.connect(self._receiveNewConfigName)

        self.ramp_settings.loadSignal.connect(
            self.ramp_parameters.dip_ramp.handleLoadRampConfig)
        self.ramp_settings.loadSignal.connect(
            self.ramp_parameters.mult_ramp.handleLoadRampConfig)
        self.ramp_settings.loadSignal.connect(
            self.ramp_parameters.rf_ramp.handleLoadRampConfig)

        self.ramp_parameters.dip_ramp.updateDipoleRampSignal.connect(
            self.ramp_settings.verifySync)
        self.ramp_parameters.dip_ramp.updateDipoleRampSignal.connect(
            self.ramp_parameters.mult_ramp.updateTable)
        self.ramp_parameters.dip_ramp.updateDipoleRampSignal.connect(
            self.ramp_parameters.mult_ramp.updateGraph)
        self.ramp_parameters.mult_ramp.updateMultipoleRampSignal.connect(
            self.ramp_settings.verifySync)

        self.ramp_parameters.mult_ramp.configsIndexChangedSignal.connect(
            self.optics_adjust.getConfigIndices)
        self.optics_adjust.normConfigChanged.connect(
            self.ramp_parameters.mult_ramp.handleNormConfigsChanges)

        self.connUpdateSignal.connect(self.general_status.getConnectors)
        self.connUpdateSignal.connect(self.commands.getConnectors)

    @pyqtSlot(str)
    def _receiveNewConfigName(self, new_config_name):
        self.ramp_config = ramp.BoosterRamp(new_config_name, auto_update=True)
        if self.ramp_config.configsrv_exist():
            self.ramp_config.configsrv_load()
            self.ramp_config.configsrv_load_normalized_configs()
        self.ramp_settings.loadSignal.emit(self.ramp_config)
        self.ramp_settings.verifySync()

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


if __name__ == '__main__':
    """Run Example."""
    app = SiriusApplication()
    _util.set_style(app)
    w = RampMain(
        prefix='ca://fernando-lnls452-linux-AS-Glob:TI-EVG:')
    w.show()
    sys.exit(app.exec_())
