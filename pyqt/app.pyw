#!/usr/local/bin/python3.6
import sys
from pydm import PyDMApplication
from pydm.PyQt.QtCore import pyqtSlot
from pydm.PyQt.QtGui import QMainWindow, QAction, QMenuBar
from siriusdm.as_ma_control import ToBoosterMagnetControlWindow
from siriusdm.as_ma_control import BoosterMagnetControlWindow
from siriusdm.as_ma_control import ToSiriusMagnetControlWindow
from siriusdm.as_ma_control import SiriusMagnetControlWindow
from siriusdm.as_config_manager import ConfigManagerWindow

class ControlApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self._windows = list()
        self._setupUi()

    def _setupUi(self):
        openLTBMagnetControlPanel = QAction("LTB Magnets", self)
        openLTBMagnetControlPanel.triggered.connect(self._openLTBMagnetsWindow)
        openBoosterMagnetControlPanel = QAction("Booster Magnets", self)
        openBoosterMagnetControlPanel.triggered.connect(self._openBoosterMagnetsWindow)
        openBTSMagnetControlPanel = QAction("BTS Magnets", self)
        openBTSMagnetControlPanel.triggered.connect(self._openBTSMagnetsWindow)
        openSiriusMagnetControlPanel = QAction("Sirius Magnets", self)
        openSiriusMagnetControlPanel.triggered.connect(self._openSiriusMagnetsWindow)

        openBoosterConfiguration = QAction("Booster Configuration", self)
        openBoosterConfiguration.triggered.connect(lambda: self._openConfigurationWindow('BO'))
        openSiriusConfiguration = QAction("Sirius Configuration", self)
        openSiriusConfiguration.triggered.connect(lambda: self._openConfigurationWindow('SI'))

        menubar = QMenuBar(self)
        menubar.setNativeMenuBar(False)

        magnetsMenu = menubar.addMenu("&Magnet")
        magnetsMenu.addAction(openLTBMagnetControlPanel)
        magnetsMenu.addAction(openBoosterMagnetControlPanel)
        magnetsMenu.addAction(openBTSMagnetControlPanel)
        magnetsMenu.addAction(openSiriusMagnetControlPanel)

        configMenu = menubar.addMenu("&Configuration Control")
        configMenu.addAction(openBoosterConfiguration)
        configMenu.addAction(openSiriusConfiguration)

        self.setMenuBar(menubar)
        self.setGeometry(300, 300, 300, 300)
        self.setWindowTitle("Test Application")
        self.show()

    def _openConfigurationWindow(self, section):
        self._windows.append(ConfigManagerWindow(section, self))
        self._windows[-1].show()

    @pyqtSlot()
    def _openSiriusMagnetsWindow(self):
        self._windows.append(SiriusMagnetControlWindow(self))
        self._windows[-1].open()

    @pyqtSlot()
    def _openBTSMagnetsWindow(self):
        self._windows.append(ToSiriusMagnetControlWindow(self))
        self._windows[-1].open()

    @pyqtSlot()
    def _openBoosterMagnetsWindow(self):
        self._windows.append(BoosterMagnetControlWindow(self))
        self._windows[-1].open()

    @pyqtSlot()
    def _openLTBMagnetsWindow(self):
        self._windows.append(ToBoosterMagnetControlWindow(self))
        self._windows[-1].open()


if __name__ == "__main__":
    app = PyDMApplication(None, sys.argv)
    window = ControlApplication()
    sys.exit(app.exec_())
