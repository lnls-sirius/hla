"""Main module of the Application Interface."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QDockWidget, QSizePolicy, QVBoxLayout, \
    QPushButton, QHBoxLayout, QMenu, QMenuBar, QAction, QStatusBar
from siriuspy.envars import vaca_prefix as LL_PREF
from siriuspy.csdevice.orbitcorr import SOFBFactory
from siriushla import util
from siriushla.widgets import SiriusMainWindow
from siriushla.widgets import PyDMLogLabel
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_ap_sofb.orbit_register import OrbitRegisters
from siriushla.as_ap_sofb.graphics import OrbitWidget
from siriushla.as_ap_sofb.ioc_control import SOFBControl
from siriushla.as_di_bpms import SelectBPMs


class MainWindow(SiriusMainWindow):
    def __init__(self, prefix, acc='SI'):
        super().__init__()
        self.prefix = prefix + acc + '-Glob:AP-SOFB:'
        self._csorb = SOFBFactory.create(acc)
        self.setupui()

    @property
    def acc(self):
        return self._csorb.acc

    @property
    def acc_idx(self):
        return self._csorb.acc_idx

    @property
    def isring(self):
        return self._csorb.isring()

    def setupui(self):
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle("Slow Orbit Feedback System")
        self.setDocumentMode(False)
        self.setDockNestingEnabled(True)

        self.ioc_log = self._create_log_docwidget()
        self.orbit_regist = self._create_orbit_registers()
        self.sofb_control = self._create_ioc_controllers()

        self.addDockWidget(Qt.LeftDockWidgetArea, self.ioc_log)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.orbit_regist)
        self.addDockWidget(Qt.RightDockWidgetArea, self.sofb_control)

        mwid = self._create_central_widget()
        self.setCentralWidget(mwid)

        self._create_menus()

    def _create_central_widget(self):
        ctrls = self.orb_regtr.get_registers_control()
        chans, ctr = OrbitWidget.get_default_ctrls(self.prefix, self.isring)
        self._channels = chans
        ctrls.update(ctr)
        return OrbitWidget(self, self.prefix, ctrls, self.acc)

    def _create_orbit_registers(self):
        # Create Context Menus for Registers and
        # assign them to the clicked signal
        wid = QDockWidget(self)
        wid.setWindowTitle("Orbit Registers")
        sz_pol = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sz_pol.setVerticalStretch(1)
        wid.setSizePolicy(sz_pol)
        wid.setFloating(False)
        wid.setFeatures(QDockWidget.AllDockWidgetFeatures)
        wid.setAllowedAreas(Qt.AllDockWidgetAreas)
        wid.setObjectName('doc_OrgReg')
        wid.setStyleSheet("""
            #doc_OrgReg{
                min-width:20em;
                min-height:14em;}""")

        wid_cont = OrbitRegisters(self, self.prefix, self.acc, 5)
        wid.setWidget(wid_cont)
        self.orb_regtr = wid_cont
        return wid

    def _create_ioc_controllers(self):
        docwid = QDockWidget(self)
        docwid.setWindowTitle("SOFB Control")
        sz_pol = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sz_pol.setVerticalStretch(1)
        docwid.setSizePolicy(sz_pol)
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
        docwid.setSizePolicy(sz_pol)
        docwid.setFloating(False)
        docwid.setObjectName('doc_IOCLog')
        docwid.setStyleSheet("""
            #doc_IOCLog{
                min-width:20em;
                min-height:34em;}""")
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
        menubar.setNativeMenuBar(False)

        menuopen = QMenu('Open', menubar)
        actions = (
            ("&SOFB Control", "SOFB Control", '', True),
            ("IOC &Log", "IOC Log", '', True),
            ("Orbit &Registers", "Orbit Registers", '', True))
        self.setMenuBar(menubar)
        for name, tool, short, check in actions:
            action = QAction(name, self)
            action.setToolTip(tool)
            action.setShortcut(short)
            action.setCheckable(check)
            action.setChecked(check)
            action.setEnabled(True)
            action.setVisible(True)
            action.toggled.connect(self.deal_with_action)
            menuopen.addAction(action)
        menubar.addAction(menuopen.menuAction())

        actbpm = QAction('Show BPM List', menubar)
        Window = create_window_from_widget(SelectBPMs, title='BPM List')
        util.connect_window(
            actbpm, Window, self, bpm_list=self._csorb.BPM_NAMES)
        menubar.addAction(actbpm)

        statusbar = QStatusBar(self)
        statusbar.setEnabled(True)
        self.setStatusBar(statusbar)

    def deal_with_action(self, boo):
        action = self.sender()
        if 'SOFB' in action.text():
            self.sofb_control.setVisible(boo)
        if 'IOC' in action.text():
            self.ioc_log.setVisible(boo)
        if 'Orbit' in action.text():
            self.orbit_regist.setVisible(boo)


if __name__ == '__main__':
    import sys as _sys
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()
    main_win = MainWindow(LL_PREF, 'SI')
    main_win.show()
    _sys.exit(app.exec_())
