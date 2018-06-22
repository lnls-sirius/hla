"""Booster Ramp Control HLA."""

import sys
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QLabel, QWidget, QGridLayout
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets.windows import SiriusMainWindow
from siriuspy.namesys import SiriusPVName as _PVName
from siriushla import util as _util
from siriuspy.ramp import ramp
from ramp_settings import RampSettings
from ramp_commands import RampCommands
from ramp_params import RampParameters
from optics_adjust import OpticsAdjust
from ramp_statistics import RampStatistics


class RampMain(SiriusMainWindow):
    """Main window of Booster Ramp Control HLA."""

    def __init__(self, parent=None, prefix=''):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self.ramp_config = None
        self._setupUi()
        self._connSignals()

    def _setupUi(self):
        # self.resize(2000, 2000)
        cw = QWidget(self)
        self.setCentralWidget(cw)
        self.my_layout = QGridLayout(cw)
        self.my_layout.setHorizontalSpacing(20)
        self.my_layout.setVerticalSpacing(20)
        lab = QLabel('<h1>Booster Energy Ramping</h1>', cw)
        self.my_layout.addWidget(lab, 0, 0, 1, 3)
        self.my_layout.setAlignment(lab, Qt.AlignCenter)

        self.ramp_settings = RampSettings(self, self.prefix, self.ramp_config)
        self.my_layout.addWidget(self.ramp_settings, 1, 0)

        self.commands = RampCommands(self, self.prefix, self.ramp_config)
        self.my_layout.addWidget(self.commands, 2, 0, 2, 1)

        self.ramp_parameters = RampParameters(self, self.prefix,
                                              self.ramp_config)
        self.my_layout.addWidget(self.ramp_parameters, 1, 1, 2, 1)

        self.optics_adjust = OpticsAdjust(self, self.prefix, self.ramp_config)
        self.my_layout.addWidget(self.optics_adjust, 3, 1)

        self.statistics = RampStatistics(self, self.prefix, self.ramp_config)
        self.my_layout.addWidget(self.statistics, 1, 2, 3, 1)

    def _connSignals(self):
        self.ramp_settings.configSignal.connect(self._receiveNewConfigName)

        self.ramp_settings.loadSignal.connect(
            self.ramp_parameters.dip_ramp.handleLoadRampConfig)
        self.ramp_settings.loadSignal.connect(
            self.ramp_parameters.mult_ramp.handleLoadRampConfig)

        self.ramp_parameters.dip_ramp.updateDipoleRampSignal.connect(
            self.ramp_settings.verifySync)
        self.ramp_parameters.dip_ramp.updateDipoleRampSignal.connect(
            self.ramp_parameters.mult_ramp.updateTable)
        self.ramp_parameters.dip_ramp.updateDipoleRampSignal.connect(
            self.ramp_parameters.mult_ramp.updateGraph)
        self.ramp_parameters.mult_ramp.updateMultipoleRampSignal.connect(
            self.ramp_settings.verifySync)

    @pyqtSlot(str)
    def _receiveNewConfigName(self, new_config_name):
        self.ramp_config = ramp.BoosterRamp(new_config_name)
        if self.ramp_config.configsrv_check():
            self.ramp_config.configsrv_load()
            self.ramp_config.configsrv_load_normalized_configs()
        self._setupUi()
        self._connSignals()
        self.ramp_settings.loadSignal.emit()
        self.ramp_settings.verifySync()


if __name__ == '__main__':
    """Run Example."""
    app = SiriusApplication()
    _util.set_style(app)
    w = RampMain(
        prefix='ca://fernando-lnls452-linux-AS-Glob:TI-EVG:')
    w.show()
    sys.exit(app.exec_())
