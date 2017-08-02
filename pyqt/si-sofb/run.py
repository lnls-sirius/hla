"""Main module of the Application Interface."""

import sys
from PyQt5 import uic
from PyQt5.QtCore import Qt
from pydm import PyDMApplication
from pydm.widgets.widget import PyDMWidget
from selection_matrix import SelectionMatrix
from register_menu import RegisterMenu
from graphic_controller import GraphicOrbitControllers
from ioc_orbit_controllers import ReferenceController
from ioc_orbit_controllers import CorrectionOrbitController


def _main():
    app = PyDMApplication()
    main_win = uic.loadUi('main_window.ui')
    _create_additional_PVs(main_win)
    _create_additional_widgets(main_win)
    _create_context_menus(main_win)

    # Define Behaviour of Orbit Visualization buttons
    for i in range(1, 4):
        GraphicOrbitControllers(main_win, i)

    # Define controllers for the IOC orbit and reference selection:
    ReferenceController(main_win)
    CorrectionOrbitController(main_win)

    # Signal2Slots(main_win)
    main_win.show()
    sys.exit(app.exec_())


def _create_additional_PVs(main_window):
    opts = dict(parent=main_window, visible=False)
    main_window.PV_SOFBCorrectionModeSP = PyDMWidget(
        init_channel='ca://SI-Glob:AP-SOFB:CorrectionMode-Sel', **opts)
    main_window.PV_SOFBCorrectionModeRB = PyDMWidget(
        init_channel='ca://SI-Glob:AP-SOFB:CorrectionMode-Sts', **opts)

    main_window.PV_SOFBOfflineOrbitXSP = PyDMWidget(
        init_channel='ca://SI-Glob:AP-SOFB:OfflineOrbitX-SP', **opts)
    main_window.PV_SOFBOfflineOrbitXRB = PyDMWidget(
        init_channel='ca://SI-Glob:AP-SOFB:OfflineOrbitX-RB', **opts)
    main_window.PV_SOFBOfflineOrbitYSP = PyDMWidget(
        init_channel='ca://SI-Glob:AP-SOFB:OfflineOrbitY-SP', **opts)
    main_window.PV_SOFBOfflineOrbitYRB = PyDMWidget(
        init_channel='ca://SI-Glob:AP-SOFB:OfflineOrbitY-RB', **opts)

    main_window.PV_SOFBOrbitRefXSP = PyDMWidget(
        init_channel='ca://SI-Glob:AP-SOFB:OrbitRefX-SP', **opts)
    main_window.PV_SOFBOrbitRefXRB = PyDMWidget(
        init_channel='ca://SI-Glob:AP-SOFB:OrbitRefX-RB', **opts)
    main_window.PV_SOFBOrbitRefYSP = PyDMWidget(
        init_channel='ca://SI-Glob:AP-SOFB:OrbitRefY-SP', **opts)
    main_window.PV_SOFBOrbitRefYRB = PyDMWidget(
        init_channel='ca://SI-Glob:AP-SOFB:OrbitRefY-RB', **opts)

    main_window.PV_SOFBGoldenOrbitXSP = PyDMWidget(
        init_channel='ca://SI-Glob:AP-SOFB:GoldenOrbitX-SP', **opts)
    main_window.PV_SOFBGoldenOrbitXRB = PyDMWidget(
        init_channel='ca://SI-Glob:AP-SOFB:GoldenOrbitX-RB', **opts)
    main_window.PV_SOFBGoldenOrbitYSP = PyDMWidget(
        init_channel='ca://SI-Glob:AP-SOFB:GoldenOrbitY-SP', **opts)
    main_window.PV_SOFBGoldenOrbitYRB = PyDMWidget(
        init_channel='ca://SI-Glob:AP-SOFB:GoldenOrbitY-RB', **opts)

    main_window.PV_SOFBCorrOrbitXMon = PyDMWidget(
        init_channel='ca://SI-Glob:AP-SOFB:CorrOrbitX-Mon', **opts)
    main_window.PV_SOFBCorrOrbitYMon = PyDMWidget(
        init_channel='ca://SI-Glob:AP-SOFB:CorrOrbitY-Mon', **opts)

    main_window.PV_SOFBOnlineOrbitXMon = PyDMWidget(
        init_channel='ca://SI-Glob:AP-SOFB:OnlineOrbitX-Mon', **opts)
    main_window.PV_SOFBOnlineOrbitYMon = PyDMWidget(
        init_channel='ca://SI-Glob:AP-SOFB:OnlineOrbitY-Mon', **opts)

    main_window.PV_SOFBBPMXEnblListRB = PyDMWidget(
        init_channel='ca://SI-Glob:AP-SOFB:BPMXEnblList-RB', **opts)
    main_window.PV_SOFBBPMYEnblListRB = PyDMWidget(
        init_channel='ca://SI-Glob:AP-SOFB:BPMYEnblList-RB', **opts)


def _create_additional_widgets(main_window):
    # Create Matrix with Selection List of BPMs and Correctors:
    for dev in ('BPMX', 'BPMY', 'CH', 'CV'):
        wid = getattr(main_window, 'Widget_' + dev + 'List')
        SelectionMatrix(wid, dev)


def _create_context_menus(main_window):
    # Create Context Menus for Registers and
    # assign them to the clicked signal
    for i in range(1, 10):
        cm = RegisterMenu(main_window, i)
        setattr(main_window, 'CM_Register' + str(i), cm)
        pb = getattr(main_window, 'PB_Register' + str(i))
        pb.setContextMenuPolicy(Qt.CustomContextMenu)
        pb.setMenu(cm)
        pb.clicked.connect(pb.showMenu)


class _Signal2Slots:
    def __init__(self, main_window):
        self.main_window = main_window
        self.main_window.PyDMCB_OrbitMode.valueChanged.connect(
                self.PyDMCB_OrbitMode_2_OfflineOrbit)

    def PyDMCB_OrbitMode_2_OfflineOrbit(self, int_):
        if int_:
            self.main_window.LB_OfflineOrbit.setDisabled()
            self.main_window.CB_OfflineOrbit.setDisabled()
        else:
            self.main_window.LB_OfflineOrbit.setEnabled()
            self.main_window.CB_OfflineOrbit.setEnabled()


#    QtCore.QMetaObject.connectSlotsByName(Form)
if __name__ == '__main__':
    _main()
