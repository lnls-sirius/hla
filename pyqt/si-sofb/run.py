from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from pydm import PyDMApplication
from test import Ui_MainWindow
import sys

app = PyDMApplication()
#app = QApplication([])
#main_win = QMainWindow()
#uii = Ui_MainWindow()
#uii.setupUi(main_win)
main_win = uic.loadUi('main_window.ui')
main_win.show()
sys.exit(app.exec_())
