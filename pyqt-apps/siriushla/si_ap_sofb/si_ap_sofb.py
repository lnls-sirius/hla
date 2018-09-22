"""Main module of the Application Interface."""

import sys as _sys
import os as _os
from qtpy import uic as _uic
from qtpy.QtCore import Qt, QSize
from qtpy.QtWidgets import (
    QWidget, QDockWidget, QSizePolicy, QVBoxLayout, QPushButton)
from pydm.utilities.macro import substitute_in_file as _substitute_in_file
from siriuspy.envars import vaca_prefix as LL_PREF
from siriushla.widgets import SiriusConnectionSignal, PyDMLogLabel
from siriushla.sirius_application import SiriusApplication
from siriushla.si_ap_sofb.orbit_register import OrbitRegisters
from siriushla.si_ap_sofb.graphic_controller import OrbitWidget
from siriushla.si_ap_sofb.orbit_controllers import ControlOrbit
from siriushla.si_ap_sofb.sofb_controllers import ControlSOFB

_dir = _os.path.dirname(_os.path.abspath(__file__))
UI_FILE = _os.path.sep.join([_dir, 'SOFBMain.ui'])


def main(prefix=None):
    """Return Main window of the interface."""
    ll_pref = 'ca://' + (prefix or LL_PREF)
    prefix = ll_pref + 'SI-Glob:AP-SOFB:'
    tmp_file = _substitute_in_file(UI_FILE,
                                   {'PREFIX': prefix, 'LL_PREF': ll_pref})
    main_win = _uic.loadUi(tmp_file)

    _create_orbit_registers(main_win, prefix)
    _create_log_docwidget(main_win, prefix)
    _create_orbit_widget(main_win, prefix)
    _create_ioc_controllers(main_win, prefix)
    return main_win


def _create_orbit_registers(mwin, prefix):
    # Create Context Menus for Registers and
    # assign them to the clicked signal
    wid = QDockWidget(mwin)
    wid.setWindowTitle("Orbit Registers")
    sz_pol = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
    sz_pol.setHorizontalStretch(0)
    sz_pol.setVerticalStretch(1)
    sz_pol.setHeightForWidth(wid.sizePolicy().hasHeightForWidth())
    wid.setSizePolicy(sz_pol)
    wid.setFloating(False)
    wid.setFeatures(QDockWidget.AllDockWidgetFeatures)
    wid.setAllowedAreas(Qt.AllDockWidgetAreas)
    mwin.addDockWidget(Qt.DockWidgetArea(8), wid)

    wid_cont = OrbitRegisters(mwin, prefix, 9)
    wid.setWidget(wid_cont)
    mwin.orb_regtr = wid_cont


def _create_orbit_widget(main_win, prefix):
    # Define Behaviour of Orbit Visualization buttons
    ctrls = main_win.orb_regtr.get_registers_control()
    pvs = [
        'OrbitSmoothX-Mon', 'OrbitSmoothY-Mon',
        'OrbitOfflineX-RB', 'OrbitOfflineY-RB',
        'OrbitRefX-RB', 'OrbitRefY-RB']
    chans = []
    for pv in pvs:
        sig = SiriusConnectionSignal(prefix+pv)
        chans.append(sig)
    main_win._channels = chans
    ctrls.update({
        'Online Orbit': {
            'x': {
                'signal': chans[0].new_value_signal,
                'getvalue': chans[0].getvalue},
            'y': {
                'signal': chans[1].new_value_signal,
                'getvalue': chans[1].getvalue}},
        'Offline Orbit': {
            'x': {
                'signal': chans[2].new_value_signal,
                'getvalue': chans[2].getvalue},
            'y': {
                'signal': chans[3].new_value_signal,
                'getvalue': chans[3].getvalue}},
        'Reference Orbit': {
            'x': {
                'signal': chans[4].new_value_signal,
                'getvalue': chans[4].getvalue},
            'y': {
                'signal': chans[5].new_value_signal,
                'getvalue': chans[5].getvalue}}})
    orb_wid = OrbitWidget(main_win, prefix, ctrls, 3)
    main_win.tabWidget.addTab(orb_wid, 'Orbit')


def _create_ioc_controllers(main_win, prefix):
    wid = QDockWidget(main_win)
    wid.setWindowTitle("SOFB Control")
    sz_pol = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
    sz_pol.setHorizontalStretch(0)
    sz_pol.setVerticalStretch(1)
    sz_pol.setHeightForWidth(wid.sizePolicy().hasHeightForWidth())
    wid.setSizePolicy(sz_pol)
    wid.setMinimumSize(QSize(350, 788))
    wid.setFloating(False)
    wid.setFeatures(QDockWidget.AllDockWidgetFeatures)
    main_win.addDockWidget(Qt.DockWidgetArea(2), wid)
    wid2 = QWidget(wid)
    wid.setWidget(wid2)

    vbl = QVBoxLayout(wid2)
    ctrls = main_win.orb_regtr.get_registers_control()
    wid = ControlOrbit(wid2, prefix, ctrls)
    vbl.addWidget(wid)

    wid = ControlSOFB(wid2, prefix)
    vbl.addWidget(wid)


def _create_log_docwidget(main_win, prefix):
    wid = QDockWidget(main_win)
    main_win.addDockWidget(Qt.DockWidgetArea(8), wid)
    wid.setWindowTitle('IOC Log')
    sz_pol = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
    sz_pol.setHorizontalStretch(0)
    sz_pol.setVerticalStretch(0)
    sz_pol.setHeightForWidth(wid.sizePolicy().hasHeightForWidth())
    wid.setSizePolicy(sz_pol)
    wid.setFloating(False)
    wid_cont = QWidget()
    wid.setWidget(wid_cont)
    vbl = QVBoxLayout(wid_cont)
    vbl.setContentsMargins(0, 0, 0, 0)
    pdm_log = PyDMLogLabel(wid_cont, init_channel=prefix+'Log-Mon')
    pdm_log.setAlternatingRowColors(True)
    pdm_log.maxCount = 2000
    vbl.addWidget(pdm_log)
    pbtn = QPushButton('Clear', wid_cont)
    pbtn.clicked.connect(pdm_log.clear)
    vbl.addWidget(pbtn)


def _main():
    app = SiriusApplication()
    main_win = main()
    main_win.show()
    _sys.exit(app.exec_())


if __name__ == '__main__':
    _main()
