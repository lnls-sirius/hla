import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt
from pydm import PyDMApplication
from pydm.widgets.widget import PyDMWidget
from selection_matrix import SelectionMatrix
from register_menu import RegisterMenu

NR_BPMs = 160
NR_CHs  = 120
NR_CVs  = 160

def create_additional_PVs(main_window):
    main_window.PV_SOFBOnOffline = PyDMWidget(main_window,'ca://SI-Glob:AP-SOFB:OrbitOnOffline-Sel')

    main_window.PV_SOFBOOfflineOrbitXSP = PyDMWidget(main_window,'ca://SI-Glob:AP-SOFB:OfflineOrbitX-SP')
    main_window.PV_SOFBOOfflineOrbitXRB = PyDMWidget(main_window,'ca://SI-Glob:AP-SOFB:OfflineOrbitX-RB')
    main_window.PV_SOFBOOfflineOrbitYSP = PyDMWidget(main_window,'ca://SI-Glob:AP-SOFB:OfflineOrbitY-SP')
    main_window.PV_SOFBOOfflineOrbitYRB = PyDMWidget(main_window,'ca://SI-Glob:AP-SOFB:OfflineOrbitY-RB')

    main_window.PV_SOFBOOrbitRefXSP = PyDMWidget(main_window,'ca://SI-Glob:AP-SOFB:OrbitRefX-SP')
    main_window.PV_SOFBOOrbitRefXRB = PyDMWidget(main_window,'ca://SI-Glob:AP-SOFB:OrbitRefX-RB')
    main_window.PV_SOFBOOrbitRefYSP = PyDMWidget(main_window,'ca://SI-Glob:AP-SOFB:OrbitRefY-SP')
    main_window.PV_SOFBOOrbitRefYRB = PyDMWidget(main_window,'ca://SI-Glob:AP-SOFB:OrbitRefY-RB')

    main_window.PV_SOFBOOnlineOrbitXMon = PyDMWidget(main_window,'ca://SI-Glob:AP-SOFB:OnlineOrbitX-Mon')
    main_window.PV_SOFBOOnlineOrbitYMon = PyDMWidget(main_window,'ca://SI-Glob:AP-SOFB:OnlineOrbitY-Mon')

def main():
    app = PyDMApplication()
    main_win = uic.loadUi('main_window.ui')
    create_additional_PVs(main_win)
    for dev in ('BPMX', 'BPMY', 'CH', 'CV'):
        wid = getattr(main_win,'Widget_'+dev+'List')
        SelectionMatrix(wid,dev)

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


#    QtCore.QMetaObject.connectSlotsByName(Form)
if __name__ == '__main__':
    main()
