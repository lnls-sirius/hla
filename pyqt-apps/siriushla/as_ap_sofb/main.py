"""Main module of the Application Interface."""

import sys as _sys
import os as _os
from qtpy.QtCore import Qt, QSize, QRect
from qtpy.QtWidgets import QWidget, QDockWidget, QSizePolicy, QVBoxLayout, \
    QPushButton, QHBoxLayout, QMenu, QMenuBar, QAction, QStatusBar
from siriushla.widgets import SiriusMainWindow
from siriuspy.envars import vaca_prefix as LL_PREF
from siriushla.widgets import PyDMLogLabel
from siriushla.sirius_application import SiriusApplication

from siriushla.as_ap_sofb.orbit_register import OrbitRegisters
from siriushla.as_ap_sofb.graphics import OrbitWidget
from siriushla.as_ap_sofb.ioc_control import SOFBControl

_dir = _os.path.dirname(_os.path.abspath(__file__))
UI_FILE = _os.path.sep.join([_dir, 'SOFBMain.ui'])


class MainWindow(SiriusMainWindow):
    def __init__(self, prefix, acc='SI'):
        super().__init__()
        if not prefix.startswith('ca://'):
            prefix = 'ca://' + prefix
        self.prefix = prefix + acc + '-Glob:AP-SOFB:'
        self.acc = acc
        self.setupui()

    def setupui(self):
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle("Slow Orbit Feedback System")
        self.resize(2890, 1856)
        self.setDocumentMode(False)
        self.setDockNestingEnabled(True)

        logwid = self._create_log_docwidget()
        orbreg = self._create_orbit_registers()
        wid = self._create_ioc_controllers()

        self.addDockWidget(Qt.DockWidgetArea(8), logwid)
        self.addDockWidget(Qt.DockWidgetArea(8), orbreg)
        self.addDockWidget(Qt.DockWidgetArea(2), wid)

        mwid = self._create_central_widget()
        self.setCentralWidget(mwid)

        self._create_menus()

    def _create_central_widget(self):
        ctrls = self.orb_regtr.get_registers_control()
        chans, ctr = OrbitWidget.get_default_ctrls(self.prefix)
        self._channels = chans
        ctrls.update(ctr)
        return OrbitWidget(self, self.prefix, ctrls, self.acc)

    def _create_orbit_registers(self):
        # Create Context Menus for Registers and
        # assign them to the clicked signal
        wid = QDockWidget(self)
        wid.setWindowTitle("Orbit Registers")
        sz_pol = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sz_pol.setHorizontalStretch(0)
        sz_pol.setVerticalStretch(1)
        sz_pol.setHeightForWidth(wid.sizePolicy().hasHeightForWidth())
        wid.setSizePolicy(sz_pol)
        wid.setFloating(False)
        wid.setFeatures(QDockWidget.AllDockWidgetFeatures)
        wid.setAllowedAreas(Qt.AllDockWidgetAreas)

        wid_cont = OrbitRegisters(self, self.prefix, self.acc, 5)
        wid.setWidget(wid_cont)
        self.orb_regtr = wid_cont
        return wid

    def _create_ioc_controllers(self):
        docwid = QDockWidget(self)
        docwid.setWindowTitle("SOFB Control")
        sz_pol = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sz_pol.setHorizontalStretch(0)
        sz_pol.setVerticalStretch(1)
        sz_pol.setHeightForWidth(docwid.sizePolicy().hasHeightForWidth())
        docwid.setSizePolicy(sz_pol)
        docwid.setMinimumSize(QSize(350, 788))
        docwid.setFloating(False)
        docwid.setFeatures(QDockWidget.AllDockWidgetFeatures)
        wid2 = QWidget(docwid)
        docwid.setWidget(wid2)

        vbl = QVBoxLayout(wid2)
        ctrls = self.orb_regtr.get_registers_control()
        wid = SOFBControl(wid2, self.prefix, ctrls, self.acc)
        vbl.addWidget(wid)
        return docwid

    def _create_log_docwidget(self):
        docwid = QDockWidget(self)
        docwid.setWindowTitle('IOC Log')
        sz_pol = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sz_pol.setHorizontalStretch(0)
        sz_pol.setVerticalStretch(0)
        sz_pol.setHeightForWidth(docwid.sizePolicy().hasHeightForWidth())
        docwid.setSizePolicy(sz_pol)
        docwid.setFloating(False)
        docwid.setMinimumWidth(600)
        wid_cont = QWidget()
        docwid.setWidget(wid_cont)
        vbl = QVBoxLayout(wid_cont)
        vbl.setContentsMargins(0, 0, 0, 0)
        pdm_log = PyDMLogLabel(wid_cont, init_channel=self.prefix+'Log-Mon')
        pdm_log.setAlternatingRowColors(True)
        pdm_log.maxCount = 2000
        vbl.addWidget(pdm_log)
        hbl = QHBoxLayout()
        vbl.addLayout(hbl)
        hbl.addStretch()
        pbtn = QPushButton('Clear Log', wid_cont)
        pbtn.clicked.connect(pdm_log.clear)
        hbl.addWidget(pbtn)
        hbl.addStretch()
        return docwid

    def _create_menus(self):
        menubar = QMenuBar(self)
        menubar.setGeometry(QRect(0, 0, 2290, 19))
        menuopen = QMenu('Open', menubar)

        self.setMenuBar(menubar)
        action = QAction("Correction &Parameters", self)
        action.setCheckable(True)
        action.setChecked(True)
        action.setEnabled(True)
        action.setVisible(True)
        menuopen.addAction(action)

        action = QAction("IOC &Log", self)
        action.setToolTip("IOC Log")
        action.setCheckable(True)
        action.setChecked(True)
        action.setEnabled(True)
        action.setVisible(True)
        menuopen.addAction(action)

        action = QAction("Orbit &Registers", self)
        action.setCheckable(True)
        action.setChecked(True)
        action.setEnabled(True)
        action.setVisible(True)
        menuopen.addAction(action)

        action = QAction("&Open All", self)
        action.setToolTip("Open all dockable windows")
        action.setShortcut("Alt+O")
        action.setChecked(False)
        action.setEnabled(True)
        action.setVisible(True)
        menuopen.addAction(action)

        action = QAction("&Close All", self)
        action.setShortcut("Alt+C")
        action.setEnabled(True)
        action.setVisible(True)
        menuopen.addAction(action)

        menubar.addAction(menuopen.menuAction())

        statusbar = QStatusBar(self)
        statusbar.setEnabled(True)
        self.setStatusBar(statusbar)


def main(prefix=None):
    """Return Main window of the interface."""
    ll_pref = prefix or LL_PREF
    main_win = MainWindow(ll_pref, 'SI')
    return main_win


def _main():
    app = SiriusApplication()
    _util.set_style(app)
    main_win = main()
    main_win.show()
    _sys.exit(app.exec_())


if __name__ == '__main__':
    import siriushla.util as _util
    _main()
