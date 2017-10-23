#!/usr/bin/env python-sirius

"""Mock application launcher."""

import sys
from siriushla.SiriusApplication import SiriusApplication
from pydm.PyQt.QtGui import QMainWindow, QAction, QMenuBar
from siriushla.as_ma_control.MagnetControlWindow import MagnetControlWindow
from siriushla.as_ma_control.MagnetTabControlWindow \
    import MagnetTabControlWindow
from siriushla.as_pm_control.PulsedMagnetControlWindow \
    import PulsedMagnetControlWindow
from siriushla.as_ap_injection.InjectionWindow import InjectionWindow
from siriushla.as_config_manager.ConfigManagerWindow import ConfigManagerWindow
from siriushla import util as _util


class ControlApplication(QMainWindow):
    """Application that act as a launcher."""

    TBMagnetWindow = "tb_magnets"
    BOMagnetWindow = "bo_magnets"
    TSMagnetWindow = "ts_magnets"
    SIMagnetWindow = "si_magnets"
    PulsedMagnetsWindow = "pulsed_magnets"
    InjectionWindow = "injection"

    def __init__(self):
        """Constructor."""
        super().__init__()
        self.app = SiriusApplication.instance()
        # self._window_manager = WindowManager()
        # self._register_windows()
        self._setup_ui()

    def _setup_ui(self):
        # openCyclePanel = QAction("PS Cycling", self)
        # openCyclePanel.triggered.connect(self._openCyclePanel)

        # Create Actions
        openTBMagnetControlPanel = QAction("TB Magnets", self)
        _util.connect_window(openTBMagnetControlPanel,
                             MagnetTabControlWindow, self, section="TB")
        openBOMagnetControlPanel = QAction("BO Magnets", self)
        _util.connect_window(openBOMagnetControlPanel,
                             MagnetTabControlWindow, self, section="BO")
        openTSMagnetControlPanel = QAction("TS Magnets", self)
        _util.connect_window(openTSMagnetControlPanel,
                             MagnetTabControlWindow, self, section="TS")
        openSIMagnetControlPanel = QAction("All", self)
        _util.connect_window(openSIMagnetControlPanel,
                             MagnetTabControlWindow, self, section="SI")
        openSIDipoleWindow = QAction("Dipole", self)
        _util.connect_window(openSIDipoleWindow, MagnetControlWindow, self,
                             section="SI", device="dipole")
        openSIQuadrupolesWindow = QAction("Quadrupoles", self)
        _util.connect_window(openSIQuadrupolesWindow, MagnetControlWindow,
                             self, section="SI", device="quadrupole")
        openSISextupolesWindow = QAction("Sextupoles", self)
        _util.connect_window(openSISextupolesWindow, MagnetControlWindow, self,
                             section="SI", device="sextupole")
        openSISlowCorrectorsWindow = QAction("Slow Correctors", self)
        _util.connect_window(openSISlowCorrectorsWindow, MagnetControlWindow,
                             self, section="SI", device="corrector-slow")
        openSIFastCorrectorsWindow = QAction("Fast Correctors", self)
        _util.connect_window(openSIFastCorrectorsWindow, MagnetControlWindow,
                             self, section="SI", device="corrector-fast")
        openSISkewQuadsWindow = QAction("Skew Quadrupoles", self)
        _util.connect_window(openSISkewQuadsWindow, MagnetControlWindow, self,
                             section="SI", device="quadrupole-skew")

        openPulsedMagnetsControlPanel = QAction("Pulsed Magnets", self)
        _util.connect_window(openPulsedMagnetsControlPanel,
                             PulsedMagnetControlWindow, self)

        openInjectionWindow = QAction("Injection", self)
        _util.connect_window(openInjectionWindow, InjectionWindow, self)

        openBoosterConfiguration = QAction("Booster Configuration", self)
        _util.connect_window(openBoosterConfiguration, ConfigManagerWindow,
                             self, config_type="BoStrengthPvs")
        openSIConfiguration = QAction("Sirius Configuration", self)
        _util.connect_window(openSIConfiguration, ConfigManagerWindow,
                             self, config_type="SiStrengthPvs")

        # Build Menu
        menubar = QMenuBar(self)
        menubar.setNativeMenuBar(False)

        # psMenu = menubar.addMenu("Power Supplies")
        # psMenu.addAction(openCyclePanel)

        magnetsMenu = menubar.addMenu("&Magnets")
        magnetsMenu.addAction(openTBMagnetControlPanel)
        magnetsMenu.addAction(openBOMagnetControlPanel)
        magnetsMenu.addAction(openTSMagnetControlPanel)
        SIMagentMenu = magnetsMenu.addMenu("Sirius Magnets")
        SIMagentMenu.addAction(openSIMagnetControlPanel)
        SIMagentMenu.addAction(openSIDipoleWindow)
        SIMagentMenu.addAction(openSIQuadrupolesWindow)
        SIMagentMenu.addAction(openSISextupolesWindow)
        SIMagentMenu.addAction(openSISlowCorrectorsWindow)
        SIMagentMenu.addAction(openSIFastCorrectorsWindow)
        SIMagentMenu.addAction(openSISkewQuadsWindow)
        # magnetsMenu.addAction(openSIMagnetControlPanel)

        pulsedMagnetsMenu = menubar.addMenu("&Pulsed Magnets")
        pulsedMagnetsMenu.addAction(openPulsedMagnetsControlPanel)

        injectionMenu = menubar.addMenu("&Injection")
        injectionMenu.addAction(openInjectionWindow)

        configMenu = menubar.addMenu("&Offline Configuration")
        configMenu.addAction(openBoosterConfiguration)
        configMenu.addAction(openSIConfiguration)

        self.setMenuBar(menubar)
        self.setGeometry(50, 50, 1024, 800)
        self.setWindowTitle("AS Launcher")
        self.show()


if __name__ == "__main__":

    app = SiriusApplication()

    # Implement sirius-style.css as default Qt resource file for Sirius!
    _util.set_style(app)

    window = ControlApplication()
    sys.exit(app.exec_())
