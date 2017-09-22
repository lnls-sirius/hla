#!/usr/bin/env python-sirius

"""Mock application launcher."""

import sys
from pydm import PyDMApplication
from pydm.PyQt.QtCore import pyqtSlot
from pydm.PyQt.QtGui import QMainWindow, QAction, QMenuBar, QSizePolicy
from siriushla.as_ma_control.detail_widget.DipoleDetailWidget \
    import DipoleDetailWidget
from siriushla.as_ma_control.control_widget.FamQuadrupoleControlWidget import \
    SiFamQuadrupoleControlWidget
from siriushla.as_ma_control.control_widget.FamSextupoleControlWidget import \
    SiFamSextupoleControlWidget
from siriushla.as_ma_control.control_widget.SlowCorrectorControlWidget import \
    SiSlowCorrectorControlWidget
from siriushla.as_ma_control.control_widget.FastCorrectorControlWidget import \
    SiFastCorrectorControlWidget
from siriushla.as_ma_control.control_widget.SkewQuadControlWidget import \
    SiSkewQuadControlWidget
from siriushla.as_ma_control import TBMagnetControlWindow
from siriushla.as_ma_control import BOMagnetControlWindow
from siriushla.as_ma_control import TSMagnetControlWindow
from siriushla.as_ma_control import SIMagnetControlWindow
from siriushla.as_pm_control.PulsedMagnetControlWindow \
    import PulsedMagnetControlWindow
from siriushla.as_ap_injection.InjectionWindow import InjectionWindow
from siriushla import util as _util
from siriuspy.search import MASearch


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
        self._windows = dict()
        self._magnets = [x for x in MASearch.get_manames()]
        self._setupUi()

    def _setupUi(self):
        # openCyclePanel = QAction("PS Cycling", self)
        # openCyclePanel.triggered.connect(self._openCyclePanel)

        openTBMagnetControlPanel = QAction("TB Magnets", self)
        openTBMagnetControlPanel.triggered.connect(self._openTBMagnetsWindow)
        openBOMagnetControlPanel = QAction("BO Magnets", self)
        openBOMagnetControlPanel.triggered.connect(
            self._openBOMagnetsWindow)
        openTSMagnetControlPanel = QAction("TS Magnets", self)
        openTSMagnetControlPanel.triggered.connect(
            self._openTSMagnetsWindow)
        openSIMagnetControlPanel = QAction("All", self)
        openSIMagnetControlPanel.triggered.connect(
            self._openSIMagnetsWindow)
        openSIDipoleWindow = QAction("Dipole", self)
        openSIDipoleWindow.triggered.connect(self._openSIDipoleWindow)
        openSIQuadrupolesWindow = QAction("Quadrupoles", self)
        openSIQuadrupolesWindow.triggered.connect(self._openSIQuadrupolesWindow)
        openSISextupolesWindow = QAction("Sextupoles", self)
        openSISextupolesWindow.triggered.connect(self._openSISextupolesWindow)
        openSISlowCorrectorsWindow = QAction("Slow Correctors", self)
        openSISlowCorrectorsWindow.triggered.connect(self._openSISlowCorrectorsWindow)
        openSIFastCorrectorsWindow = QAction("Fast Correctors", self)
        openSIFastCorrectorsWindow.triggered.connect(self._openSIFastCorrectorsWindow)
        openSISkewQuadsWindow = QAction("Skew Quadrupoles", self)
        openSISkewQuadsWindow.triggered.connect(self._openSISkewQuadsWindow)

        openPulsedMagnetsControlPanel = QAction("Pulsed Magnets", self)
        openPulsedMagnetsControlPanel.triggered.connect(
            self._openPulsedMagnetWindow)

        # Injection actions
        openInjectionWindow = QAction("Injection", self)
        openInjectionWindow.triggered.connect(
            lambda: self._open_window(
                ControlApplication.InjectionWindow, InjectionWindow))

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
        self.setWindowTitle("Test Application")
        self.show()

    # def _openCyclePanel(self, section):
    #     self._windows.append(PsCycleWindow(self))
    #     self._windows[-1].open()

    # def _openConfigurationWindow(self, section):
    #     self._windows.append(ConfigManagerWindow(section, self))
    #     self._windows[-1].show()

    def _open_window(self, window, window_class, **kwargs):
        if window not in self._windows:
            self._windows[window] = window_class(parent=self, **kwargs)
        self._windows[window].show()
        self._windows[window].activateWindow()

    def _create_and_open_window(self, widget, widget_class, **kwargs):
        if widget not in self._windows:
            self._windows[widget] = QMainWindow(self)
            self._windows[widget].setCentralWidget(
                widget_class(parent=self._windows[widget], **kwargs))
            PyDMApplication.instance().establish_widget_connections(
                self._windows[widget])
        self._windows[widget].show()
        self._windows[widget].activateWindow()

    @pyqtSlot()
    def _openSIDipoleWindow(self):
        self._create_and_open_window(
            "si-ma-dipole", DipoleDetailWidget, magnet_name="SI-Fam:MA-B1B2")

    @pyqtSlot()
    def _openSIQuadrupolesWindow(self):
        self._create_and_open_window(
            "si-ma-quadruole", SiFamQuadrupoleControlWidget,
            magnet_list=self._magnets, orientation=2)

    @pyqtSlot()
    def _openSISextupolesWindow(self):
        self._create_and_open_window(
            "si-ma-sextupole", SiFamSextupoleControlWidget,
            magnet_list=self._magnets, orientation=2)

    @pyqtSlot()
    def _openSISlowCorrectorsWindow(self):
        self._create_and_open_window(
            "si-ma-correctors-slow", SiSlowCorrectorControlWidget,
            magnet_list=self._magnets)

    @pyqtSlot()
    def _openSIFastCorrectorsWindow(self):
        self._create_and_open_window(
            "si-ma-correctors-fast", SiFastCorrectorControlWidget,
            magnet_list=self._magnets)

    @pyqtSlot()
    def _openSISkewQuadsWindow(self):
        self._create_and_open_window(
            "si-ma-quadruole-skew", SiSkewQuadControlWidget,
            magnet_list=self._magnets)

    @pyqtSlot()
    def _openSIMagnetsWindow(self):
        self._open_window(
            ControlApplication.SIMagnetWindow, SIMagnetControlWindow)

    @pyqtSlot()
    def _openTSMagnetsWindow(self):
        self._open_window(
            ControlApplication.TSMagnetWindow, TSMagnetControlWindow)

    @pyqtSlot()
    def _openBOMagnetsWindow(self):
        self._open_window(
            ControlApplication.BOMagnetWindow, BOMagnetControlWindow)

    @pyqtSlot()
    def _openTBMagnetsWindow(self):
        self._open_window(
            ControlApplication.TBMagnetWindow, TBMagnetControlWindow)

    @pyqtSlot()
    def _openPulsedMagnetWindow(self):
        self._open_window(
            ControlApplication.PulsedMagnetsWindow, PulsedMagnetControlWindow)

    @pyqtSlot()
    def _openInjectionWindow(self):
        self._open_window(ControlApplication.InjectionWindow, InjectionWindow)


if __name__ == "__main__":

    app = PyDMApplication(None, sys.argv)

    # Implement sirius-style.css as default Qt resource file for Sirius !
    # import siriushla.resources
    # from pydm.PyQt.QtCore import QFile
    # stream = QFile(':/style.css')
    # if stream.open(QFile.ReadOnly):
    #     style = str(stream.readAll(), 'utf-8')
    #     stream.close()
    # else:
    #     print(stream.errorString())
    # app.setStyleSheet(style)
    _util.set_style(app)

    window = ControlApplication()
    sys.exit(app.exec_())
