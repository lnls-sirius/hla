#!/usr/bin/env python-sirius

"""Mock application launcher."""

import sys
from pydm import PyDMApplication
from pydm.PyQt.QtGui import QMainWindow, QAction, QMenuBar
from siriushla.as_ma_control.MagnetControlWindow import MagnetControlWindow
from siriushla.as_ma_control.MagnetTabControlWindow \
    import MagnetTabControlWindow
from siriushla.as_pm_control.PulsedMagnetControlWindow \
    import PulsedMagnetControlWindow
from siriushla.as_ap_injection.InjectionWindow import InjectionWindow
from siriushla.WindowManager import WindowManager
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
        self._window_manager = WindowManager()
        self._register_windows()
        self._setup_ui()

    def _register_windows(self):
        self._window_manager.register_window(
            "si-ma-dipole", MagnetControlWindow, section="SI", device="dipole",
            window_manager=self._window_manager, parent=self)
        self._window_manager.register_window(
            "si-ma-quadruole", MagnetControlWindow,
            section="SI", device="quadrupole",
            window_manager=self._window_manager, parent=self)
        self._window_manager.register_window(
            "si-ma-sextupole", MagnetControlWindow,
            section="SI", device="sextupole",
            window_manager=self._window_manager, parent=self)
        self._window_manager.register_window(
            "si-ma-correctors-slow", MagnetControlWindow,
            section="SI", device="corrector-slow",
            window_manager=self._window_manager, parent=self)
        self._window_manager.register_window(
            "si-ma-correctors-fast", MagnetControlWindow,
            section="SI", device="corrector-fast",
            window_manager=self._window_manager, parent=self)
        self._window_manager.register_window(
            "si-ma-quadruole-skew", MagnetControlWindow,
            section="SI", device="quadrupole-skew",
            window_manager=self._window_manager, parent=self)
        self._window_manager.register_window(
            ControlApplication.SIMagnetWindow, MagnetTabControlWindow,
            section="SI", window_manager=self._window_manager, parent=self)
        self._window_manager.register_window(
            ControlApplication.TSMagnetWindow, MagnetTabControlWindow,
            section="TS", window_manager=self._window_manager, parent=self)
        self._window_manager.register_window(
            ControlApplication.BOMagnetWindow, MagnetTabControlWindow,
            section="BO", window_manager=self._window_manager, parent=self)
        self._window_manager.register_window(
            ControlApplication.TBMagnetWindow, MagnetTabControlWindow,
            section="TB", window_manager=self._window_manager, parent=self)
        self._window_manager.register_window(
            ControlApplication.PulsedMagnetsWindow, PulsedMagnetControlWindow,
            window_manager=self._window_manager, parent=self)
        self._window_manager.register_window(
            ControlApplication.InjectionWindow, InjectionWindow, parent=self)

    def _setup_ui(self):
        # openCyclePanel = QAction("PS Cycling", self)
        # openCyclePanel.triggered.connect(self._openCyclePanel)

        openTBMagnetControlPanel = QAction("TB Magnets", self)
        openTBMagnetControlPanel.triggered.connect(
            lambda: self._open_window(ControlApplication.TBMagnetWindow))
        openBOMagnetControlPanel = QAction("BO Magnets", self)
        openBOMagnetControlPanel.triggered.connect(
            lambda: self._open_window(ControlApplication.BOMagnetWindow))
        openTSMagnetControlPanel = QAction("TS Magnets", self)
        openTSMagnetControlPanel.triggered.connect(
            lambda: self._open_window(ControlApplication.TSMagnetWindow))
        openSIMagnetControlPanel = QAction("All", self)
        openSIMagnetControlPanel.triggered.connect(
            lambda: self._open_window(ControlApplication.SIMagnetWindow))
        openSIDipoleWindow = QAction("Dipole", self)
        openSIDipoleWindow.triggered.connect(
            lambda: self._open_window("si-ma-dipole"))
        openSIQuadrupolesWindow = QAction("Quadrupoles", self)
        openSIQuadrupolesWindow.triggered.connect(
            lambda: self._open_window("si-ma-quadruole"))
        openSISextupolesWindow = QAction("Sextupoles", self)
        openSISextupolesWindow.triggered.connect(
            lambda: self._open_window("si-ma-sextupole"))
        openSISlowCorrectorsWindow = QAction("Slow Correctors", self)
        openSISlowCorrectorsWindow.triggered.connect(
            lambda: self._open_window("si-ma-correctors-slow"))
        openSIFastCorrectorsWindow = QAction("Fast Correctors", self)
        openSIFastCorrectorsWindow.triggered.connect(
            lambda: self._open_window("si-ma-correctors-fast"))
        openSISkewQuadsWindow = QAction("Skew Quadrupoles", self)
        openSISkewQuadsWindow.triggered.connect(self._openSISkewQuadsWindow)

        openPulsedMagnetsControlPanel = QAction("Pulsed Magnets", self)
        openPulsedMagnetsControlPanel.triggered.connect(
            lambda: self._open_window(ControlApplication.PulsedMagnetsWindow))

        # Injection actions
        openInjectionWindow = QAction("Injection", self)
        openInjectionWindow.triggered.connect(
            lambda: self._open_window(ControlApplication.InjectionWindow))

        # openBoosterConfiguration = QAction("Booster Configuration", self)
        # openBoosterConfiguration.triggered.connect(
        #     lambda: self._openConfigurationWindow('BoForcePvs'))
        # openSIConfiguration = QAction("Sirius Configuration", self)
        # openSIConfiguration.triggered.connect(
        #     lambda: self._openConfigurationWindow('SiForcePvs'))

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

        # configMenu = menubar.addMenu("&Configuration Control")
        # configMenu.addAction(openBoosterConfiguration)
        # configMenu.addAction(openSIConfiguration)

        self.setMenuBar(menubar)
        self.setGeometry(50, 50, 1024, 800)
        self.setWindowTitle("AS Launcher")
        self.show()

    def _open_window(self, id):
        self._window_manager.open_window(id)


if __name__ == "__main__":

    app = PyDMApplication(None, sys.argv)

    # Implement sirius-style.css as default Qt resource file for Sirius!
    _util.set_style(app)

    window = ControlApplication()
    sys.exit(app.exec_())
