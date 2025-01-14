"""Main module of the Application Interface."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QDockWidget, QSizePolicy, QVBoxLayout, \
    QPushButton, QHBoxLayout, QMenu, QMenuBar, QAction
import qtawesome as qta

from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.sofb.csdev import SOFBFactory

from .. import util as _util
from ..widgets import SiriusMainWindow
from ..widgets import PyDMLogLabel
from ..widgets.windows import create_window_from_widget
from ..as_di_bpms import SelectBPMs

from .orbit_register import OrbitRegisters
from .graphics import OrbitWidget
from .ioc_control import SOFBControl, DriveControl


class MainWindow(SiriusMainWindow):
    def __init__(self, parent=None, prefix='', acc='SI'):
        super().__init__(parent=parent)
        self.prefix = prefix
        self.device = _PVName(acc + '-Glob:AP-SOFB')
        self.devpref = self.device.substitute(prefix=prefix)
        self._csorb = SOFBFactory.create(acc)
        self.setupui()
        self.setObjectName(acc+'App')
        self.setWindowIcon(
            qta.icon('fa5s.hammer', color=_util.get_appropriate_color(acc)))

    @property
    def acc(self):
        return self._csorb.acc

    @property
    def acc_idx(self):
        return self._csorb.acc_idx

    @property
    def isring(self):
        return self._csorb.isring

    def setupui(self):
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle(self.acc + " - SOFB")
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
        chans, ctr = OrbitWidget.get_default_ctrls(
            self.device, self.prefix, self.acc)
        self._channels = chans
        ctrls.update(ctr)
        return OrbitWidget(self, self.device, self.prefix, ctrls, self.acc)

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
        wid.setObjectName('doc_OrbReg')
        wid.setStyleSheet("#doc_OrbReg{min-width:20em; min-height:14em;}")

        wid_cont = OrbitRegisters(self, self.device, self.prefix, self.acc, 7)
        wid.setWidget(wid_cont)
        self.orb_regtr = wid_cont
        return wid

    def _create_ioc_controllers(self):
        docwid = QDockWidget(self)
        docwid.setWindowTitle("IOC Control")
        sz_pol = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sz_pol.setVerticalStretch(1)
        docwid.setSizePolicy(sz_pol)
        docwid.setFloating(False)
        docwid.setFeatures(QDockWidget.AllDockWidgetFeatures)
        docwid.setAllowedAreas(Qt.AllDockWidgetAreas)

        ctrls = self.orb_regtr.get_registers_control()
        wid = SOFBControl(self, self.device, ctrls, self.prefix, self.acc)
        docwid.setWidget(wid)
        return docwid

    def _create_log_docwidget(self):
        docwid = QDockWidget(self)
        docwid.setWindowTitle('IOC Log')
        sz_pol = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        docwid.setSizePolicy(sz_pol)
        docwid.setFloating(False)
        docwid.setObjectName('doc_IOCLog')
        docwid.setStyleSheet("#doc_IOCLog{min-width:20em; min-height:30em;}")
        wid_cont = QWidget()
        docwid.setWidget(wid_cont)
        vbl = QVBoxLayout(wid_cont)
        vbl.setContentsMargins(0, 0, 0, 0)
        pdm_log = PyDMLogLabel(
            wid_cont, init_channel=self.devpref.substitute(propty='Log-Mon'))
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
            ("&SOFB Control", "SOFB Control", '', True, self.sofb_control),
            ("IOC &Log", "IOC Log", '', True, self.ioc_log),
            ("&Registers", "Orbit Registers", '', True, self.orbit_regist))
        self.setMenuBar(menubar)
        for name, tool, short, check, doc in actions:
            action = QAction(name, self)
            action.setToolTip(tool)
            action.setShortcut(short)
            action.setCheckable(check)
            action.setChecked(check)
            action.setEnabled(True)
            action.setVisible(True)
            action.toggled.connect(doc.setVisible)
            doc.visibilityChanged.connect(action.setChecked)
            menuopen.addAction(action)
        menubar.addAction(menuopen.menuAction())

        if self.acc == 'SI':
            actdrive = QAction('Drive Control', menubar)
            Window = create_window_from_widget(
                DriveControl, title='Drive Control')
            _util.connect_window(
                actdrive, Window, parent=self, device=self.device,
                prefix=self.prefix, acc=self.acc)
            menubar.addAction(actdrive)

        actbpm = QAction('Show BPM List', menubar)
        Window = create_window_from_widget(SelectBPMs, title='BPM List')
        _util.connect_window(
            actbpm, Window, self, prefix=self.prefix,
            bpm_list=self._csorb.bpm_names)
        menubar.addAction(actbpm)

        if self.isring:
            acttrajfit = QAction('Open Traj. Fit', menubar)
            _util.connect_newprocess(
                acttrajfit,
                [f'sirius-hla-{self.acc.lower()}-ap-trajfit.py', ])
            menubar.addAction(acttrajfit)
