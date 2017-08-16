"""Main module of the Application Interface."""

import sys as _sys
import os as _os
from PyQt5 import uic as _uic
from PyQt5.QtCore import Qt as _Qt
from pydm import PyDMApplication as _PyDMApplication
from pydm.widgets.widget import PyDMWidget as _PyDMWidget
from pydm.utilities.macro import substitute_in_file as _substitute_in_file
from siriuspy.envars import vaca_prefix as LL_PREF

from siriushla.si_ap_sofb.selection_matrix import SelectionMatrix
from siriushla.si_ap_sofb.selection_matrix import NR_BPMs, NR_CHs, NR_CVs
from siriushla.si_ap_sofb.register_menu import RegisterMenu
from siriushla.si_ap_sofb.graphic_controller import GraphicOrbitControllers
from siriushla.si_ap_sofb.orbit_controllers import ReferenceController
from siriushla.si_ap_sofb.orbit_controllers import CorrectionOrbitController

_dir = _os.path.dirname(_os.path.abspath(__file__))
UI_FILE = _os.path.sep.join([_dir, 'main_window.ui'])


def main(prefix=None):
    """Return Main window of the interface."""
    ll_pref = 'ca://' + (prefix or LL_PREF)
    prefix = ll_pref + 'SI-Glob:AP-SOFB:'
    tmp_file = _substitute_in_file(UI_FILE,
                                   {'PREFIX': prefix, 'LL_PREF': ll_pref})
    main_win = _uic.loadUi(tmp_file)
    _create_additional_PVs(main_win, prefix)
    _create_additional_widgets(main_win, prefix)
    _create_context_menus(main_win)

    # Define Behaviour of Orbit Visualization buttons
    for i in range(1, 4):
        GraphicOrbitControllers(main_win, i)

    # Define controllers for the IOC orbit and reference selection:
    ReferenceController(main_win)
    CorrectionOrbitController(main_win)

    return main_win


def _create_additional_PVs(MWin, prefix):
    opts = dict(parent=MWin, visible=False)
    MWin.PV_SOFBCorrectionModeSP = _PyDMWidget(
        init_channel=prefix + 'CorrectionMode-Sel', **opts)
    MWin.PV_SOFBCorrectionModeRB = _PyDMWidget(
        init_channel=prefix + 'CorrectionMode-Sts', **opts)

    MWin.PV_SOFBOfflineOrbitXSP = _PyDMWidget(
        init_channel=prefix + 'OfflineOrbitX-SP', **opts)
    MWin.PV_SOFBOfflineOrbitXRB = _PyDMWidget(
        init_channel=prefix + 'OfflineOrbitX-RB', **opts)
    MWin.PV_SOFBOfflineOrbitYSP = _PyDMWidget(
        init_channel=prefix + 'OfflineOrbitY-SP', **opts)
    MWin.PV_SOFBOfflineOrbitYRB = _PyDMWidget(
        init_channel=prefix + 'OfflineOrbitY-RB', **opts)

    MWin.PV_SOFBOrbitRefXSP = _PyDMWidget(
        init_channel=prefix + 'OrbitRefX-SP', **opts)
    MWin.PV_SOFBOrbitRefXRB = _PyDMWidget(
        init_channel=prefix + 'OrbitRefX-RB', **opts)
    MWin.PV_SOFBOrbitRefYSP = _PyDMWidget(
        init_channel=prefix + 'OrbitRefY-SP', **opts)
    MWin.PV_SOFBOrbitRefYRB = _PyDMWidget(
        init_channel=prefix + 'OrbitRefY-RB', **opts)

    MWin.PV_SOFBGoldenOrbitXSP = _PyDMWidget(
        init_channel=prefix + 'GoldenOrbitX-SP', **opts)
    MWin.PV_SOFBGoldenOrbitXRB = _PyDMWidget(
        init_channel=prefix + 'GoldenOrbitX-RB', **opts)
    MWin.PV_SOFBGoldenOrbitYSP = _PyDMWidget(
        init_channel=prefix + 'GoldenOrbitY-SP', **opts)
    MWin.PV_SOFBGoldenOrbitYRB = _PyDMWidget(
        init_channel=prefix + 'GoldenOrbitY-RB', **opts)

    MWin.PV_SOFBCorrOrbitXMon = _PyDMWidget(
        init_channel=prefix + 'CorrOrbitX-Mon', **opts)
    MWin.PV_SOFBCorrOrbitYMon = _PyDMWidget(
        init_channel=prefix + 'CorrOrbitY-Mon', **opts)

    MWin.PV_SOFBOnlineOrbitXMon = _PyDMWidget(
        init_channel=prefix + 'OnlineOrbitX-Mon', **opts)
    MWin.PV_SOFBOnlineOrbitYMon = _PyDMWidget(
        init_channel=prefix + 'OnlineOrbitY-Mon', **opts)

    MWin.PV_SOFBBPMXEnblListRB = _PyDMWidget(
        init_channel=prefix + 'BPMXEnblList-RB', **opts)
    MWin.PV_SOFBBPMYEnblListRB = _PyDMWidget(
        init_channel=prefix + 'BPMYEnblList-RB', **opts)


def _create_additional_widgets(MWin, prefix):
    # Create Matrix with Selection List of BPMs and Correctors:
    for dev in ('BPMX', 'BPMY', 'CH', 'CV'):
        wid = getattr(MWin, 'Widget_' + dev + 'List')
        SelectionMatrix(wid, dev, prefix)


def _create_context_menus(MWin):
    # Create Context Menus for Registers and
    # assign them to the clicked signal
    for i in range(1, 10):
        cm = RegisterMenu(MWin, i)
        setattr(MWin, 'CM_Register' + str(i), cm)
        pb = getattr(MWin, 'PB_Register' + str(i))
        pb.setContextMenuPolicy(_Qt.CustomContextMenu)
        pb.setMenu(cm)
        pb.clicked.connect(pb.showMenu)


class _Signal2Slots:
    def __init__(self, MWin):
        self.MWin = MWin
        self.MWin.PyDMCB_OrbitMode.valueChanged.connect(
                self.PyDMCB_OrbitMode_2_OfflineOrbit)

    def PyDMCB_OrbitMode_2_OfflineOrbit(self, int_):
        if int_:
            self.MWin.LB_OfflineOrbit.setDisabled()
            self.MWin.CB_OfflineOrbit.setDisabled()
        else:
            self.MWin.LB_OfflineOrbit.setEnabled()
            self.MWin.CB_OfflineOrbit.setEnabled()


if __name__ == '__main__':
    app = _PyDMApplication()
    main_win = main()
    main_win.show()
    _sys.exit(app.exec_())
