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
    main_window.PV_SOFBCorrectionModeSP = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:CorrectionMode-Sel', **opts)
    main_window.PV_SOFBCorrectionModeRB = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:CorrectionMode-Sts', **opts)

    main_window.PV_SOFBOfflineOrbitXSP = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:OfflineOrbitX-SP', **opts)
    main_window.PV_SOFBOfflineOrbitXRB = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:OfflineOrbitX-RB', **opts)
    main_window.PV_SOFBOfflineOrbitYSP = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:OfflineOrbitY-SP', **opts)
    main_window.PV_SOFBOfflineOrbitYRB = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:OfflineOrbitY-RB', **opts)

    main_window.PV_SOFBOrbitRefXSP = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:OrbitRefX-SP', **opts)
    main_window.PV_SOFBOrbitRefXRB = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:OrbitRefX-RB', **opts)
    main_window.PV_SOFBOrbitRefYSP = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:OrbitRefY-SP', **opts)
    main_window.PV_SOFBOrbitRefYRB = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:OrbitRefY-RB', **opts)

    main_window.PV_SOFBGoldenOrbitXSP = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:GoldenOrbitX-SP', **opts)
    main_window.PV_SOFBGoldenOrbitXRB = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:GoldenOrbitX-RB', **opts)
    main_window.PV_SOFBGoldenOrbitYSP = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:GoldenOrbitY-SP', **opts)
    main_window.PV_SOFBGoldenOrbitYRB = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:GoldenOrbitY-RB', **opts)

    main_window.PV_SOFBCorrOrbitXMon = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:CorrOrbitX-Mon', **opts)
    main_window.PV_SOFBCorrOrbitYMon = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:CorrOrbitY-Mon', **opts)

    main_window.PV_SOFBOnlineOrbitXMon = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:OnlineOrbitX-Mon', **opts)
    main_window.PV_SOFBOnlineOrbitYMon = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:OnlineOrbitY-Mon', **opts)

    main_window.PV_OrbitOrbitXMon = PyDMWidget(init_channel='ca://SI-Glob:AP-Orbit:PosX-Mon', **opts)
    main_window.PV_OrbitOrbitYMon = PyDMWidget(init_channel='ca://SI-Glob:AP-Orbit:PosY-Mon', **opts)

    main_window.PV_SOFBBPMXEnblListRB = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:BPMXEnblList-RB', **opts)
    main_window.PV_SOFBBPMYEnblListRB = PyDMWidget(init_channel='ca://SI-Glob:AP-SOFB:BPMYEnblList-RB', **opts)

def create_additional_widgets(main_window):
    ## Create Matrix with Selection List of BPMs and Correctors:
    for dev in ('BPMX', 'BPMY', 'CH', 'CV'):
        wid = getattr(main_window,'Widget_'+dev+'List')
        SelectionMatrix(wid,dev)

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
        self.main_window.PyDMCB_OrbitMode.valueChanged.connect(self.PyDMCB_OrbitMode_2_OfflineOrbit)

    def PyDMCB_OrbitMode_2_OfflineOrbit(self,int_):
        if int_:
            self.main_window.LB_OfflineOrbit.setDisabled()
            self.main_window.CB_OfflineOrbit.setDisabled()
        else:
            self.main_window.LB_OfflineOrbit.setEnabled()
            self.main_window.CB_OfflineOrbit.setEnabled()

class IndividualInteligence:
    def __init__(self,main_window):
        self.main_window = main_window
        self.setup()

    def setup(self):
        # Create Context Menus for Registers and assign them to the clicked signal
        for i in range(1,10):
            cm  = RegisterMenu(self.main_window,i)
            setattr(self.main_window,'CM_Register'+str(i),cm)
            pb = getattr(self.main_window,'PB_Register'+str(i))
            pb.setContextMenuPolicy(Qt.CustomContextMenu)
            pb.setMenu(cm)
            pb.clicked.connect(pb.showMenu)

        # Define Behaviour of Orbit Visualization buttons
        for i in range(1,4):
            orbC = GraphicOrbitControllers(self.main_window,i)

        # Define controllers for the IOC orbit and reference selection:
        ReferenceController(self.main_window)
        CorrectionOrbitController(self.main_window)


#    QtCore.QMetaObject.connectSlotsByName(Form)
if __name__ == '__main__':
    main()
