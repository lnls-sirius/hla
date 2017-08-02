import sys
import numpy as _np
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt
from pydm import PyDMApplication
from pydm.widgets.widget import PyDMWidget
from selection_matrix import SelectionMatrix, NR_BPMs
from register_menu import RegisterMenu
from graphic_controller import GraphicOrbitControllers
from ioc_orbit_controllers import ReferenceController, CorrectionOrbitController

def create_additional_PVs(main_window):
    opts = dict(parent=main_window, visible = False)
    main_window.PV_SOFBBPMYEnblListRB = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:BPMYEnblList-RB', **opts)

def create_additional_widgets(main_window):
    ## Create Matrix with Selection List of BPMs and Correctors:


def main():
    app = PyDMApplication()
    main_win = uic.loadUi('main_window.ui')
    create_additional_PVs(main_win)
    create_additional_widgets(main_win)

    IndividualInteligence(main_win)
    # Signal2Slots(main_win)
    main_win.show()
    sys.exit(app.exec_())

class Signal2Slots:
    def __init__(self,main_window):
        self.main_window = main_window


class IndividualInteligence:
    def __init__(self,main_window):
        self.main_window = main_window
        self.setup()

    def setup(self):
        pass

#    QtCore.QMetaObject.connectSlotsByName(Form)
if __name__ == '__main__':
    main()
