from pydm import Display
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtWidgets import QApplication
from epics import PV
from os import path
from siriuspy.magnet import magdata
import threading
import datetime

class DiagnosticsMainWindow(Display):

    def __init__(self, parent=None, args=None):

        super(DiagnosticsMainWindow, self).__init__(parent)

    def ui_filename(self):

        return 'main_window.ui'

    def ui_filepath(self):

        return path.join(path.dirname(path.realpath(__file__)), self.ui_filename())

    def _load_widgets(self):
        pass

    def _configure_signals(self):
        pass


intelclass = DiagnosticsMainWindow
