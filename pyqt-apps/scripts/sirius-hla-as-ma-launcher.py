#!/usr/bin/env python-sirius

"""Mock application launcher."""

import sys

from qtpy.QtWidgets import QAction, QMenuBar

from siriushla.sirius_application import SiriusApplication
from siriushla.as_ps_control.PSControlWindow import PSControlWindow
from siriushla.as_ps_control.PSTabControlWindow \
    import PSTabControlWindow
from siriushla.as_pm_control.PulsedMagnetControlWindow \
    import PulsedMagnetControlWindow
from siriushla.as_ap_injection.InjectionWindow import InjectionWindow
from siriushla.as_ap_servconf.ConfigManagerWindow import ConfigManagerWindow
from siriushla.as_ps_cycle.cycle_window import CycleWindow
from siriushla.as_ps_test.ps_test_window import PSTestWindow
from siriushla import util as _util
from siriushla.widgets import SiriusMainWindow


class ControlApplication(SiriusMainWindow):
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
                             PSTabControlWindow, self, section="TB",
                             discipline=1)
        openBOMagnetControlPanel = QAction("BO Magnets", self)
        _util.connect_window(openBOMagnetControlPanel,
                             PSTabControlWindow, self, section="BO",
                             discipline=1)
        openTSMagnetControlPanel = QAction("TS Magnets", self)
        _util.connect_window(openTSMagnetControlPanel,
                             PSTabControlWindow, self, section="TS",
                             discipline=1)
        openSIMagnetControlPanel = QAction("All", self)
        _util.connect_window(openSIMagnetControlPanel,
                             PSTabControlWindow, self, section="SI",
                             discipline=1)
        openSIDipoleWindow = QAction("Dipole", self)
        _util.connect_window(openSIDipoleWindow, PSControlWindow, self,
                             section="SI", discipline=1, device="dipole")
        openSIQuadrupolesWindow = QAction("Quadrupoles", self)
        _util.connect_window(openSIQuadrupolesWindow, PSControlWindow,
                             self, section="SI", discipline=1,
                             device="quadrupole")
        openSISextupolesWindow = QAction("Sextupoles", self)
        _util.connect_window(openSISextupolesWindow, PSControlWindow, self,
                             section="SI", discipline=1, device="sextupole")
        openSISlowCorrectorsWindow = QAction("Slow Correctors", self)
        _util.connect_window(openSISlowCorrectorsWindow, PSControlWindow,
                             self, section="SI", discipline=1,
                             device="corrector-slow")
        openSIFastCorrectorsWindow = QAction("Fast Correctors", self)
        _util.connect_window(openSIFastCorrectorsWindow, PSControlWindow,
                             self, section="SI", discipline=1,
                             device="corrector-fast")
        openSISkewQuadsWindow = QAction("Skew Quadrupoles", self)
        _util.connect_window(openSISkewQuadsWindow, PSControlWindow, self,
                             section="SI", discipline=1,
                             device="quadrupole-skew")

        # Tools
        openCyclingWindow = QAction('PS Cycle', self)
        _util.connect_window(openCyclingWindow, CycleWindow, self)
        openPSTestWindow = QAction('PS Test', self)
        _util.connect_window(openPSTestWindow, PSTestWindow, self)

        openPulsedMagnetsControlPanel = QAction("Pulsed Magnets", self)
        _util.connect_window(openPulsedMagnetsControlPanel,
                             PulsedMagnetControlWindow, self)

        openInjectionWindow = QAction("Injection", self)
        _util.connect_window(openInjectionWindow, InjectionWindow, self)

        openBoosterConfiguration = QAction("Booster Configuration", self)
        _util.connect_window(openBoosterConfiguration, ConfigManagerWindow,
                             self, config_type="bo_strength_pvs")
        openSIConfiguration = QAction("Sirius Configuration", self)
        _util.connect_window(openSIConfiguration, ConfigManagerWindow,
                             self, config_type="si_strength_pvs")

        # Build Menu
        menubar = QMenuBar(self)
        menubar.setNativeMenuBar(False)

        # psMenu = menubar.addMenu("Power Supplies")
        # psMenu.addAction(openCyclePanel)

        magnetsMenu = menubar.addMenu("&Magnets")
        magnetsMenu.addAction(openTBMagnetControlPanel)
        magnetsMenu.addAction(openBOMagnetControlPanel)
        magnetsMenu.addAction(openTSMagnetControlPanel)
        SIMagentMenu = magnetsMenu.addMenu("SI Magnets")
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

        cyclingMenu = menubar.addMenu("&Tools")
        cyclingMenu.addAction(openCyclingWindow)
        cyclingMenu.addAction(openPSTestWindow)

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
