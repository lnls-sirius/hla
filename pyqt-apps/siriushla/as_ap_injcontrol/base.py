
import os as _os

from qtpy.QtCore import Qt, Slot
from qtpy.QtSvg import QSvgWidget
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QWidget, \
    QLabel, QPushButton, QCheckBox, QSizePolicy as QSzPlcy, QGroupBox, \
    QButtonGroup, QMenuBar
from pydm.widgets import PyDMLabel, PyDMEnumComboBox

from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX

from siriushla import util
from siriushla.widgets import SiriusMainWindow, PyDMLed, \
    SiriusLedState, PyDMLinEditScrollbar
from siriushla.as_di_scrns import SiriusScrnView
from siriushla.as_ps_control import PSDetailWindow
from siriushla.as_pu_control import PUDetailWindow


class BaseWindow(SiriusMainWindow):
    """Base class."""

    def __init__(self, parent=None, prefix=_VACA_PREFIX):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self._curr_dir = _os.path.abspath(_os.path.dirname(__file__))

    def _setupUi(self):
        # menubar
        self.menubar = QMenuBar(self)
        self.menubar.setNativeMenuBar(False)
        self.setMenuBar(self.menubar)
        self.menu = self.menubar.addMenu("Open...")
        self._setupMenu()

        # auxiliar diagnostics widget
        self.auxdig_wid = None
        self._setupDiagWidget()

        # lattice widget
        self.lattice_wid = QSvgWidget(
            _os.path.join(self._curr_dir, self.SVG_FILE))

        # screens view widget (create only one ScrnView)
        self._scrns_wids_dict = dict()
        self._currScrn = 0
        scrn_wid = SiriusScrnView(
            parent=self, prefix=self.prefix,
            device=self._scrns[self._currScrn])
        scrn_wid.setVisible(True)
        self._scrns_wids_dict[self._currScrn] = scrn_wid
        self.scrns_wid = QWidget()
        lay_scrns = QGridLayout(self.scrns_wid)
        lay_scrns.addWidget(scrn_wid)

        # correction widget
        self.corr_wid = QGroupBox('Screens and Correctors Panel')
        self._scrns_sel_bg = QButtonGroup(parent=self.corr_wid)
        self._scrns_sel_bg.setExclusive(True)
        self._setupScrnsCorrsWidget()

        vlay1 = QVBoxLayout()
        if self.auxdig_wid:
            vlay1.addWidget(self.auxdig_wid)
        vlay1.addWidget(self.scrns_wid)
        vlay2 = QVBoxLayout()
        vlay2.addWidget(self.lattice_wid)
        vlay2.addWidget(self.corr_wid)

        cw = QWidget()
        lay = QHBoxLayout(cw)
        lay.addLayout(vlay1)
        lay.addLayout(vlay2)
        self.setCentralWidget(cw)

    def _setupMenu(self):
        raise NotImplementedError

    def _setupScrnsCorrsWidget(self):
        raise NotImplementedError

    def _setupDiagWidget(self):
        raise NotImplementedError

    @Slot()
    def _setScrnWidget(self):
        scrn_obj = self._scrns_wids_dict[self._currScrn]
        scrn_obj.setVisible(False)

        sender = self.sender()
        self._currScrn = self._scrns_sel_bg.id(sender)

        if self._currScrn not in self._scrns_wids_dict.keys():
            scrn_obj = SiriusScrnView(
                parent=self, prefix=self.prefix,
                device=self._scrns[self._currScrn])
            self.scrns_wid.layout().addWidget(scrn_obj, 2, 0)
            self._scrns_wids_dict[self._currScrn] = scrn_obj
        else:
            scrn_obj = self._scrns_wids_dict[self._currScrn]

        self._scrns_wids_dict[self._currScrn].setVisible(True)

    def _create_headerline(self, labels):
        """Create and return a headerline."""
        hl = QWidget()
        hl.setLayout(QHBoxLayout())
        hl.layout().setContentsMargins(0, 9, 0, 0)

        glay = None
        for text, width in labels:
            if not width:
                if glay:
                    hl.layout().addLayout(glay)
                hl.layout().addStretch()
                glay = QGridLayout()
                glay.setAlignment(Qt.AlignCenter)
                glay.setContentsMargins(0, 0, 0, 0)
                c = 0
            else:
                label = QLabel(text, self)
                label.setStyleSheet("""
                    min-width:valueem; min-height:1.29em; max-height:1.29em;
                    font-weight:bold; qproperty-alignment: AlignCenter;
                    """.replace('value', str(width)))
                glay.addWidget(label, 0, c)
                c += 1
        return hl

    def _create_scrn_summwidget(self, scrn_device, scrn_idx):
        """Create and return a screen detail widget."""
        cb_scrn = QCheckBox(scrn_device.get_nickname(dev=True), self)
        self._scrns_sel_bg.addButton(cb_scrn)
        self._scrns_sel_bg.setId(cb_scrn, scrn_idx)
        if scrn_idx == self._currScrn:
            cb_scrn.setChecked(True)
        cb_scrn.clicked.connect(self._setScrnWidget)
        cb_scrn.setStyleSheet("""
            min-width:6.5em; max-width:6.5em; font-weight:bold;""")

        led_camenbl = SiriusLedState(self, scrn_device.substitute(
            prefix=self.prefix, propty='CamEnbl-Sts'))
        led_camenbl.setStyleSheet("min-width:3.2em; max-width:3.2em;")

        cb_scrntype = PyDMEnumComboBox(self, scrn_device.substitute(
            prefix=self.prefix, propty='ScrnType-Sel'))
        cb_scrntype.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Fixed)
        cb_scrntype.setStyleSheet("min-width:4.5em;max-width:4.5em;")

        lb_scrntype = PyDMLabel(self, scrn_device.substitute(
            prefix=self.prefix, propty='ScrnType-Sts'))
        lb_scrntype.setStyleSheet("min-width:4.5em; max-width:4.5em;")
        lb_scrntype.setAlignment(Qt.AlignCenter)

        led_scrntype = PyDMLed(self, scrn_device.substitute(
            prefix=self.prefix, propty='ScrnType-Sts'),
            color_list=[PyDMLed.LightGreen, PyDMLed.Red, PyDMLed.Red,
                        PyDMLed.Yellow])
        led_scrntype.shape = 2
        led_scrntype.setStyleSheet("""min-width:4.5em; max-width:4.5em;""")

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setAlignment(Qt.AlignCenter)
        lay.addWidget(cb_scrn, 1, 1)
        lay.addWidget(led_camenbl, 1, 2)
        lay.addWidget(cb_scrntype, 1, 3)
        lay.addWidget(lb_scrntype, 1, 4)
        lay.addWidget(led_scrntype, 2, 4)
        return wid

    def _create_corr_summwidget(self, corr):
        """Create and return a corrector detail widget."""
        wid = QWidget()
        wid.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Maximum)
        lay = QGridLayout(wid)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setAlignment(Qt.AlignCenter)

        propty_sp = 'Current-SP' if corr.sec == 'LI' else 'Kick-SP'
        propty_mon = propty_sp.replace('SP', 'Mon')

        led = SiriusLedState(self, corr.substitute(
            prefix=self.prefix, propty='PwrState-Sts'))
        led.setStyleSheet("max-width:1.29em;")
        lay.addWidget(led, 1, 1)

        nickname = corr.get_nickname(sec=corr.sec == 'LI', dev=True)
        pb = QPushButton(nickname, self)
        if corr.dis == 'PU':
            util.connect_window(
                pb, PUDetailWindow, parent=self, devname=corr)
        else:
            util.connect_window(
                pb, PSDetailWindow, parent=self, psname=corr)
        pb.setStyleSheet("""
            min-width:6em; max-width:6em; min-height:1.29em;""")
        lay.addWidget(pb, 1, 2)

        sp_kick = PyDMLinEditScrollbar(
            parent=self, channel=corr.substitute(
                prefix=self.prefix, propty=propty_sp))
        sp_kick.layout.setContentsMargins(0, 0, 0, 0)
        sp_kick.layout.setSpacing(3)
        sp_kick.setSizePolicy(QSzPlcy.Fixed, QSzPlcy.Maximum)
        sp_kick.sp_lineedit.setStyleSheet("""
            min-width:4em; max-width:4em; min-height:1.29em;""")
        sp_kick.sp_lineedit.setAlignment(Qt.AlignCenter)
        sp_kick.sp_lineedit.setSizePolicy(
            QSzPlcy.Minimum, QSzPlcy.Minimum)
        sp_kick.sp_lineedit.precisionFromPV = False
        sp_kick.sp_lineedit.precision = 1
        sp_kick.sp_scrollbar.setStyleSheet("""max-width:4em;""")
        sp_kick.sp_scrollbar.limitsFromPV = True
        lay.addWidget(sp_kick, 1, 3, 2, 1)

        lb_kick = PyDMLabel(
            self, corr.substitute(prefix=self.prefix, propty=propty_mon))
        lb_kick.setStyleSheet("""
            min-width:5em; max-width:5em; min-height:1.29em;""")
        lb_kick.showUnits = True
        lb_kick.precisionFromPV = False
        lb_kick.precision = 1
        lb_kick.setAlignment(Qt.AlignCenter)
        lay.addWidget(lb_kick, 1, 4)
        return wid
