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
from siriushla.as_ma_control import ToBoosterMagnetControlWindow
from siriushla.as_ma_control import BoosterMagnetControlWindow
from siriushla.as_ma_control import ToSiriusMagnetControlWindow
from siriushla.as_ma_control import SiriusMagnetControlWindow
from siriushla.as_pm_control.PulsedMagnetControlWindow \
    import PulsedMagnetControlWindow
from siriushla.as_ap_injection.InjectionWindow import InjectionWindow
from siriushla import util as _util
from siriuspy.search import MASearch


class ControlApplication(QMainWindow):
    """Application that act as a launcher."""

    LTBMagnetWindow = "ltb_magnets"
    BoosterMagnetWindow = "bo_magnets"
    BTSMagnetWindow = "bts_magnets"
    SiriusMagnetWindow = "sirius_magnets"
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

        openLTBMagnetControlPanel = QAction("LTB Magnets", self)
        openLTBMagnetControlPanel.triggered.connect(self._openLTBMagnetsWindow)
        openBoosterMagnetControlPanel = QAction("Booster Magnets", self)
        openBoosterMagnetControlPanel.triggered.connect(
            self._openBoosterMagnetsWindow)
        openBTSMagnetControlPanel = QAction("BTS Magnets", self)
        openBTSMagnetControlPanel.triggered.connect(
            self._openBTSMagnetsWindow)
        openSiriusMagnetControlPanel = QAction("All", self)
        openSiriusMagnetControlPanel.triggered.connect(
            self._openSiriusMagnetsWindow)
        openSiriusDipoleWindow = QAction("Dipole", self)
        openSiriusDipoleWindow.triggered.connect(self._openSiriusDipoleWindow)
        openSiriusQuadrupolesWindow = QAction("Quadrupoles", self)
        openSiriusQuadrupolesWindow.triggered.connect(self._openSiriusQuadrupolesWindow)
        openSiriusSextupolesWindow = QAction("Sextupoles", self)
        openSiriusSextupolesWindow.triggered.connect(self._openSiriusSextupolesWindow)
        openSiriusSlowCorrectorsWindow = QAction("Slow Correctors", self)
        openSiriusSlowCorrectorsWindow.triggered.connect(self._openSiriusSlowCorrectorsWindow)
        openSiriusFastCorrectorsWindow = QAction("Fast Correctors", self)
        openSiriusFastCorrectorsWindow.triggered.connect(self._openSiriusFastCorrectorsWindow)
        openSiriusSkewQuadsWindow = QAction("Skew Quadrupoles", self)
        openSiriusSkewQuadsWindow.triggered.connect(self._openSiriusSkewQuadsWindow)

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
        # openSiriusConfiguration = QAction("Sirius Configuration", self)
        # openSiriusConfiguration.triggered.connect(
        #     lambda: self._openConfigurationWindow('SiForcePvs'))

        menubar = QMenuBar(self)
        menubar.setNativeMenuBar(False)

        # psMenu = menubar.addMenu("Power Supplies")
        # psMenu.addAction(openCyclePanel)

        magnetsMenu = menubar.addMenu("&Magnets")
        magnetsMenu.addAction(openLTBMagnetControlPanel)
        magnetsMenu.addAction(openBoosterMagnetControlPanel)
        magnetsMenu.addAction(openBTSMagnetControlPanel)
        siriusMagnetMenu = magnetsMenu.addMenu("Sirius Magnets")
        siriusMagnetMenu.addAction(openSiriusMagnetControlPanel)
        siriusMagnetMenu.addAction(openSiriusDipoleWindow)
        siriusMagnetMenu.addAction(openSiriusQuadrupolesWindow)
        siriusMagnetMenu.addAction(openSiriusSextupolesWindow)
        siriusMagnetMenu.addAction(openSiriusSlowCorrectorsWindow)
        siriusMagnetMenu.addAction(openSiriusFastCorrectorsWindow)
        siriusMagnetMenu.addAction(openSiriusSkewQuadsWindow)
        # magnetsMenu.addAction(openSiriusMagnetControlPanel)

        pulsedMagnetsMenu = menubar.addMenu("&Pulsed Magnets")
        pulsedMagnetsMenu.addAction(openPulsedMagnetsControlPanel)

        injectionMenu = menubar.addMenu("&Injection")
        injectionMenu.addAction(openInjectionWindow)

        # configMenu = menubar.addMenu("&Configuration Control")
        # configMenu.addAction(openBoosterConfiguration)
        # configMenu.addAction(openSiriusConfiguration)

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
    def _openSiriusDipoleWindow(self):
        self._create_and_open_window(
            "si-ma-dipole", DipoleDetailWidget, magnet_name="SI-Fam:MA-B1B2")

    @pyqtSlot()
    def _openSiriusQuadrupolesWindow(self):
        self._create_and_open_window(
            "si-ma-quadruole", SiFamQuadrupoleControlWidget,
            magnet_list=self._magnets, orientation=2)

    @pyqtSlot()
    def _openSiriusSextupolesWindow(self):
        self._create_and_open_window(
            "si-ma-sextupole", SiFamSextupoleControlWidget,
            magnet_list=self._magnets, orientation=2)

    @pyqtSlot()
    def _openSiriusSlowCorrectorsWindow(self):
        self._create_and_open_window(
            "si-ma-correctors-slow", SiSlowCorrectorControlWidget,
            magnet_list=self._magnets)

    @pyqtSlot()
    def _openSiriusFastCorrectorsWindow(self):
        self._create_and_open_window(
            "si-ma-correctors-fast", SiFastCorrectorControlWidget,
            magnet_list=self._magnets)

    @pyqtSlot()
    def _openSiriusSkewQuadsWindow(self):
        self._create_and_open_window(
            "si-ma-quadruole-skew", SiSkewQuadControlWidget,
            magnet_list=self._magnets)

    @pyqtSlot()
    def _openSiriusMagnetsWindow(self):
        self._open_window(
            ControlApplication.SiriusMagnetWindow, SiriusMagnetControlWindow)

    @pyqtSlot()
    def _openBTSMagnetsWindow(self):
        self._open_window(
            ControlApplication.BTSMagnetWindow, ToSiriusMagnetControlWindow)

    @pyqtSlot()
    def _openBoosterMagnetsWindow(self):
        self._open_window(
            ControlApplication.BoosterMagnetWindow, BoosterMagnetControlWindow)

    @pyqtSlot()
    def _openLTBMagnetsWindow(self):
        self._open_window(
            ControlApplication.LTBMagnetWindow, ToBoosterMagnetControlWindow)

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
