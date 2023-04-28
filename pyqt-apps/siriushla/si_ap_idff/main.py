"""Main window."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QGridLayout, QSizePolicy as QSzPlcy, \
    QWidget, QGroupBox, QVBoxLayout

from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.search import IDSearch
from siriuspy.idff.csdev import IDFFConst

from ..util import connect_window
from ..widgets import SiriusMainWindow, SiriusLabel, SiriusSpinbox, \
    PyDMStateButton, SiriusLedState, PyDMLogLabel
from ..as_ps_control.control_widget.ControlWidgetFactory import \
    ControlWidgetFactory
from ..as_ps_control import PSDetailWindow
from .custom_widgets import ConfigLineEdit
from .util import get_idff_icon


class IDFFWindow(SiriusMainWindow):
    """ID FF main window."""

    def __init__(self, parent=None, prefix='', idname=''):
        """Initialize."""
        super().__init__(parent)
        self.prefix = prefix or _VACA_PREFIX
        self.idname = idname
        self._const = IDFFConst(idname)
        self._idffdata = IDSearch.conv_idname_2_idff(self.idname)
        self.device = _PVName(self._const.idffname)
        self.dev_pref = self.device.substitute(prefix=prefix)
        self.setObjectName('IDApp')
        self.setWindowTitle(self.device)
        self.setWindowIcon(get_idff_icon())
        self._setupUi()
        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        self.title = QLabel(
            '<h2>' + self.idname + ' Feedforward Settings</h2>',
            alignment=Qt.AlignCenter)

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.addWidget(self.title, 0, 0, 1, 2)
        lay.addWidget(self._basicSettingsWidget(), 1, 0)
        lay.addWidget(self._idStatusWidget(), 2, 0)
        lay.addWidget(self._logWidget(), 3, 0)
        lay.addWidget(self._corrsMonitorWidget(), 1, 1, 3, 1)
        self.setCentralWidget(wid)

    def _basicSettingsWidget(self):
        ld_configname = QLabel(
            'Config. Name: ', self, alignment=Qt.AlignRight)
        self.le_configname = ConfigLineEdit(
            self, self.dev_pref.substitute(propty='ConfigName-SP'))
        self.le_configname.setStyleSheet('min-width:10em; max-width:10em;')
        self.lb_configname = SiriusLabel(
            self, self.dev_pref.substitute(propty='ConfigName-RB'))

        ld_loopstate = QLabel(
            'Loop State: ', self, alignment=Qt.AlignRight)
        self.sb_loopstate = PyDMStateButton(
            self, self.dev_pref.substitute(propty='LoopState-Sel'))
        self.lb_loopstate = SiriusLedState(
            self, self.dev_pref.substitute(propty='LoopState-Sts'))

        ld_loopfreq = QLabel(
            'Loop Freq.: ', self, alignment=Qt.AlignRight)
        self.sb_loopfreq = SiriusSpinbox(
            self, self.dev_pref.substitute(propty='LoopFreq-SP'))
        self.lb_loopfreq = SiriusLabel(
            self, self.dev_pref.substitute(propty='LoopFreq-RB'))

        ld_polar = QLabel(
            'Polarization: ', self, alignment=Qt.AlignRight)
        self.lb_polar = SiriusLabel(
            self, self.dev_pref.substitute(propty='Polarization-Mon'))

        gbox = QGroupBox('Settings', self)
        lay = QGridLayout(gbox)
        lay.addWidget(ld_configname, 0, 0)
        lay.addWidget(self.le_configname, 0, 1)
        lay.addWidget(self.lb_configname, 0, 2)
        lay.addWidget(ld_loopstate, 1, 0)
        lay.addWidget(self.sb_loopstate, 1, 1)
        lay.addWidget(self.lb_loopstate, 1, 2)
        lay.addWidget(ld_loopfreq, 2, 0)
        lay.addWidget(self.sb_loopfreq, 2, 1)
        lay.addWidget(self.lb_loopfreq, 2, 2)
        lay.addWidget(ld_polar, 3, 0)
        lay.addWidget(self.lb_polar, 3, 1, 1, 2)
        return gbox

    def _idStatusWidget(self):
        pparam = _PVName(self._idffdata['pparameter'])
        ld_pparam = QLabel(
            pparam.propty_name + ': ', self, alignment=Qt.AlignRight)
        self._lb_pparam = SiriusLabel(self, pparam, keep_unit=True)
        self._lb_pparam.showUnits = True

        kparam = _PVName(self._idffdata['kparameter'])
        ld_kparam = QLabel(
            kparam.propty_name + ': ', self, alignment=Qt.AlignRight)
        self._lb_kparam = SiriusLabel(self, kparam, keep_unit=True)
        self._lb_kparam.showUnits = True

        gbox = QGroupBox('ID Status', self)
        lay = QGridLayout(gbox)
        lay.addWidget(ld_pparam, 0, 0)
        lay.addWidget(self._lb_pparam, 0, 1)
        lay.addWidget(ld_kparam, 1, 0)
        lay.addWidget(self._lb_kparam, 1, 1)
        return gbox

    def _logWidget(self):
        self.log = PyDMLogLabel(
            self, init_channel=self.dev_pref.substitute(propty='Log-Mon'))
        self.log.setSizePolicy(
            QSzPlcy.MinimumExpanding, QSzPlcy.MinimumExpanding)
        self.log.setAlternatingRowColors(True)
        self.log.maxCount = 2000

        gbox = QGroupBox('Log', self)
        lay = QVBoxLayout(gbox)
        lay.addWidget(self.log)
        return gbox

    def _corrsMonitorWidget(self):
        widget = ControlWidgetFactory.factory(
            self, section='SI', device='corrector-idff',
            subsection=self.device.sub, orientation=Qt.Vertical)
        for wid in widget.get_summary_widgets():
            detail_bt = wid.get_detail_button()
            psname = detail_bt.text()
            if not psname:
                psname = detail_bt.toolTip()
            connect_window(detail_bt, PSDetailWindow, self, psname=psname)

        gbox = QGroupBox('Correctors', self)
        lay = QVBoxLayout(gbox)
        lay.setContentsMargins(3, 3, 3, 3)
        lay.addWidget(widget)
        return gbox
