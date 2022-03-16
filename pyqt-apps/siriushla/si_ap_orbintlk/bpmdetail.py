"""Individual BPM Orbit Interlock Window."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGridLayout, QLabel, QGroupBox, \
    QSpacerItem, QSizePolicy as QSzPlc

import qtawesome as qta

from pydm.widgets import PyDMPushButton, PyDMLabel

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy.namesys import SiriusPVName

from ..widgets import SiriusMainWindow, SiriusLedState, \
    PyDMStateButton, SiriusLedAlert, SiriusSpinbox
from .base import BaseObject


class BPMOrbIntlkDetailWindow(BaseObject, SiriusMainWindow):
    """Individual BPM Orbit Interlock Window."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        BaseObject.__init__(self)
        SiriusMainWindow.__init__(self, parent)

        self.prefix = prefix
        self.device = SiriusPVName(device)
        self.devpref = self.device.substitute(prefix=prefix)

        self.setObjectName('SIApp')
        self.setWindowTitle(device+' Orbit Interlock Control Window')

        self._setupUi()

        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        wid = QWidget(self)
        self.setCentralWidget(wid)

        title = QLabel(
            '<h3>' + self.device + ' Orbit Interlock Control</h3>',
            self, alignment=Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold;")

        # General Interlock
        self._gb_gen = QGroupBox('General Interlock')
        lay_gen = self._setupIntlkGenLayout()
        self._gb_gen.setLayout(lay_gen)

        # Translation Interlock
        self._gb_trans = QGroupBox('Translation Interlock')
        lay_trans = self._setupIntlkTypeLayout('Trans')
        self._gb_trans.setLayout(lay_trans)

        # Angulation Interlock
        self._gb_ang = QGroupBox('Angulation Interlock')
        lay_ang = self._setupIntlkTypeLayout('Ang')
        self._gb_ang.setLayout(lay_ang)

        lay = QGridLayout(wid)
        lay.addWidget(title, 0, 0, 1, 2)
        lay.addWidget(self._gb_gen, 1, 0, 1, 2)
        lay.addWidget(self._gb_trans, 2, 0)
        lay.addWidget(self._gb_ang, 2, 1)

    def _setupIntlkGenLayout(self):
        self._ld_genenbl = QLabel(
            'Enable: ', self, alignment=Qt.AlignRight | Qt.AlignBottom)
        self._sb_genenbl = PyDMStateButton(
            self, self.devpref.substitute(propty='IntlkEn-Sel'))
        self._led_genenbl = SiriusLedState(
            self, self.devpref.substitute(propty='IntlkEn-Sts'))

        self._ld_genclr = QLabel(
            'Clear: ', self, alignment=Qt.AlignRight | Qt.AlignBottom)
        self._bt_genclr = PyDMPushButton(
            self,
            init_channel=self.devpref.substitute(propty='IntlkClr-Sel'),
            pressValue=1)
        self._bt_genclr.setIcon(qta.icon('fa5s.sync'))
        self._bt_genclr.setObjectName('clr')
        self._bt_genclr.setStyleSheet(
            '#clr{min-width:25px; max-width:25px; icon-size:20px;}')

        self._ld_intlkinst = QLabel(
            'Intantaneous Interlock: ', self,
            alignment=Qt.AlignRight | Qt.AlignBottom)
        self._led_intlkinst = SiriusLedAlert(
            self, self.devpref.substitute(propty='Intlk-Mon'))

        self._ld_intlkltc = QLabel(
            'Latch Interlock: ', self,
            alignment=Qt.AlignRight | Qt.AlignBottom)
        self._led_intlkltc = SiriusLedAlert(
            self, self.devpref.substitute(propty='IntlkLtc-Mon'))

        self._ld_minsumenbl = QLabel(
            'Min.Sum.Thres. Enable: ', self,
            alignment=Qt.AlignRight | Qt.AlignBottom)
        self._ld_minsumenbl.setToolTip(
            'If enabled, enable interlock only if minimum sum'
            ' threshold is exceeded.')
        self._sb_minsumenbl = PyDMStateButton(
            self, self.devpref.substitute(propty='IntlkMinSumEn-Sel'))
        self._led_minsumenbl = SiriusLedState(
            self, self.devpref.substitute(propty='IntlkMinSumEn-Sts'))

        self._ld_minsumlim = QLabel(
            'Min.Sum.Thres.[sum count]: ', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter)
        self._sb_minsumlim = SiriusSpinbox(
            self, self.devpref.substitute(propty='IntlkLmtMinSum-SP'))
        self._sb_minsumlim.showStepExponent = False
        self._sb_minsumlim.limitsFromChannel = False
        self._sb_minsumlim.setMinimum(-1e12)
        self._sb_minsumlim.setMaximum(+1e12)
        self._lb_minsumlim = PyDMLabel(
            self, self.devpref.substitute(propty='IntlkLmtMinSum-RB'))

        lay = QGridLayout()
        lay.setAlignment(Qt.AlignCenter)
        lay.addWidget(self._ld_genenbl, 0, 0)
        lay.addWidget(self._sb_genenbl, 0, 1)
        lay.addWidget(self._led_genenbl, 0, 2)
        lay.addWidget(self._ld_genclr, 1, 0)
        lay.addWidget(self._bt_genclr, 1, 1, alignment=Qt.AlignCenter)
        lay.addWidget(self._ld_intlkinst, 2, 0)
        lay.addWidget(self._led_intlkinst, 2, 1)
        lay.addWidget(self._ld_intlkltc, 3, 0)
        lay.addWidget(self._led_intlkltc, 3, 1)
        lay.addItem(QSpacerItem(1, 15, QSzPlc.Ignored, QSzPlc.Fixed), 4, 0)
        lay.addWidget(self._ld_minsumenbl, 5, 0)
        lay.addWidget(self._sb_minsumenbl, 5, 1)
        lay.addWidget(self._led_minsumenbl, 5, 2)
        lay.addWidget(self._ld_minsumlim, 6, 0)
        lay.addWidget(self._sb_minsumlim, 6, 1)
        lay.addWidget(self._lb_minsumlim, 6, 2)
        return lay

    def _setupIntlkTypeLayout(self, intlk):
        unit = 'rad.nm' if 'ang' in intlk.lower() else 'nm'

        ld_enbl = QLabel(
            'Enable: ', self, alignment=Qt.AlignRight | Qt.AlignBottom)
        sb_enbl = PyDMStateButton(
            self, self.devpref.substitute(propty='Intlk'+intlk+'En-Sel'))
        led_enbl = SiriusLedState(
            self, self.devpref.substitute(propty='Intlk'+intlk+'En-Sts'))

        ld_clr = QLabel(
            'Clear: ', self, alignment=Qt.AlignRight | Qt.AlignBottom)
        bt_clr = PyDMPushButton(
            self, init_channel=self.devpref.substitute(
                propty='Intlk'+intlk+'Clr-Sel'), pressValue=1)
        bt_clr.setIcon(qta.icon('fa5s.sync'))
        bt_clr.setObjectName('clr')
        bt_clr.setStyleSheet(
            '#clr{min-width:25px; max-width:25px; icon-size:20px;}')

        ld_minx = QLabel(
            'Min.X Thres.['+unit+']: ', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter)
        sb_minx = SiriusSpinbox(
            self, self.devpref.substitute(propty='IntlkLmt'+intlk+'MinX-SP'))
        sb_minx.showStepExponent = False
        sb_minx.limitsFromChannel = False
        sb_minx.setMinimum(-1e9)
        sb_minx.setMaximum(+1e9)
        lb_minx = PyDMLabel(
            self, self.devpref.substitute(propty='IntlkLmt'+intlk+'MinX-RB'))

        ld_maxx = QLabel(
            'Max.X Thres.['+unit+']: ', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter)
        sb_maxx = SiriusSpinbox(
            self, self.devpref.substitute(propty='IntlkLmt'+intlk+'MaxX-SP'))
        sb_maxx.showStepExponent = False
        sb_maxx.limitsFromChannel = False
        sb_maxx.setMinimum(-1e9)
        sb_maxx.setMaximum(+1e9)
        lb_maxx = PyDMLabel(
            self, self.devpref.substitute(propty='IntlkLmt'+intlk+'MaxX-RB'))

        ld_miny = QLabel(
            'Min.Y Thres.['+unit+']: ', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter)
        sb_miny = SiriusSpinbox(
            self, self.devpref.substitute(propty='IntlkLmt'+intlk+'MinY-SP'))
        sb_miny.showStepExponent = False
        sb_miny.limitsFromChannel = False
        sb_miny.setMinimum(-1e9)
        sb_miny.setMaximum(+1e9)
        lb_miny = PyDMLabel(
            self, self.devpref.substitute(propty='IntlkLmt'+intlk+'MinY-RB'))

        ld_maxy = QLabel(
            'Max.Y Thres.['+unit+']: ', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter)
        sb_maxy = SiriusSpinbox(
            self, self.devpref.substitute(propty='IntlkLmt'+intlk+'MaxY-SP'))
        sb_maxy.showStepExponent = False
        sb_maxy.limitsFromChannel = False
        sb_maxy.setMinimum(-1e9)
        sb_maxy.setMaximum(+1e9)
        lb_maxy = PyDMLabel(
            self, self.devpref.substitute(propty='IntlkLmt'+intlk+'MaxY-RB'))

        ld_leglow = QLabel(
            'Smaller', self, alignment=Qt.AlignCenter)
        ld_leghigh = QLabel(
            'Bigger', self, alignment=Qt.AlignCenter)

        ld_legmask = QLabel(
            '<h4>Masked By Enable</h4>', self, alignment=Qt.AlignCenter)
        ld_legmask_any = QLabel(
            'X or Y', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        led_mask_anylow = SiriusLedAlert(
            self, self.devpref.substitute(propty='Intlk'+intlk+'Smaller-Mon'))
        led_mask_anyhigh = SiriusLedAlert(
            self, self.devpref.substitute(propty='Intlk'+intlk+'Bigger-Mon'))

        ld_leginst = QLabel(
            '<h4>Instantaneous</h4>', self, alignment=Qt.AlignCenter)
        ld_leginst_any = QLabel(
            'X or Y', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        led_inst_anylow = SiriusLedAlert(
            self, self.devpref.substitute(
                propty='Intlk'+intlk+'SmallerAny-Mon'))
        led_inst_anyhigh = SiriusLedAlert(
            self, self.devpref.substitute(
                propty='Intlk'+intlk+'BiggerAny-Mon'))
        ld_leginst_x = QLabel(
            'X', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        led_inst_xlow = SiriusLedAlert(
            self, self.devpref.substitute(propty='Intlk'+intlk+'SmallerX-Mon'))
        led_inst_xhigh = SiriusLedAlert(
            self, self.devpref.substitute(propty='Intlk'+intlk+'BiggerX-Mon'))
        ld_leginst_y = QLabel(
            'Y', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        led_inst_ylow = SiriusLedAlert(
            self, self.devpref.substitute(propty='Intlk'+intlk+'SmallerY-Mon'))
        led_inst_yhigh = SiriusLedAlert(
            self, self.devpref.substitute(propty='Intlk'+intlk+'BiggerY-Mon'))

        ld_legltc = QLabel(
            '<h4>Latch</h4>', self, alignment=Qt.AlignCenter)
        ld_legltc_any = QLabel(
            'X or Y', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        led_ltc_anylow = SiriusLedAlert(
            self, self.devpref.substitute(
                propty='Intlk'+intlk+'SmallerLtc-Mon'))
        led_ltc_anyhigh = SiriusLedAlert(
            self, self.devpref.substitute(
                propty='Intlk'+intlk+'BiggerLtc-Mon'))
        ld_legltc_x = QLabel(
            'X', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        led_ltc_xlow = SiriusLedAlert(
            self, self.devpref.substitute(
                propty='Intlk'+intlk+'SmallerLtcX-Mon'))
        led_ltc_xhigh = SiriusLedAlert(
            self, self.devpref.substitute(
                propty='Intlk'+intlk+'BiggerLtcX-Mon'))
        ld_legltc_y = QLabel(
            'Y', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        led_ltc_ylow = SiriusLedAlert(
            self, self.devpref.substitute(
                propty='Intlk'+intlk+'SmallerLtcY-Mon'))
        led_ltc_yhigh = SiriusLedAlert(
            self, self.devpref.substitute(
                propty='Intlk'+intlk+'BiggerLtcY-Mon'))

        lay_mon = QGridLayout()
        lay_mon.setAlignment(Qt.AlignCenter)
        lay_mon.addWidget(ld_leglow, 0, 1)
        lay_mon.addWidget(ld_leghigh, 0, 2)
        lay_mon.addWidget(ld_legmask, 1, 0)
        lay_mon.addWidget(ld_legmask_any, 2, 0)
        lay_mon.addWidget(led_mask_anylow, 2, 1)
        lay_mon.addWidget(led_mask_anyhigh, 2, 2)
        lay_mon.addWidget(ld_leginst, 3, 0)
        lay_mon.addWidget(ld_leginst_any, 4, 0)
        lay_mon.addWidget(led_inst_anylow, 4, 1)
        lay_mon.addWidget(led_inst_anyhigh, 4, 2)
        lay_mon.addWidget(ld_leginst_x, 5, 0)
        lay_mon.addWidget(led_inst_xlow, 5, 1)
        lay_mon.addWidget(led_inst_xhigh, 5, 2)
        lay_mon.addWidget(ld_leginst_y, 6, 0)
        lay_mon.addWidget(led_inst_ylow, 6, 1)
        lay_mon.addWidget(led_inst_yhigh, 6, 2)
        lay_mon.addWidget(ld_legltc, 7, 0)
        lay_mon.addWidget(ld_legltc_any, 8, 0)
        lay_mon.addWidget(led_ltc_anylow, 8, 1)
        lay_mon.addWidget(led_ltc_anyhigh, 8, 2)
        lay_mon.addWidget(ld_legltc_x, 9, 0)
        lay_mon.addWidget(led_ltc_xlow, 9, 1)
        lay_mon.addWidget(led_ltc_xhigh, 9, 2)
        lay_mon.addWidget(ld_legltc_y, 10, 0)
        lay_mon.addWidget(led_ltc_ylow, 10, 1)
        lay_mon.addWidget(led_ltc_yhigh, 10, 2)

        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.addWidget(ld_enbl, 0, 0)
        lay.addWidget(sb_enbl, 0, 1)
        lay.addWidget(led_enbl, 0, 2)
        lay.addWidget(ld_clr, 1, 0)
        lay.addWidget(bt_clr, 1, 1, alignment=Qt.AlignCenter)
        lay.addWidget(ld_minx, 2, 0)
        lay.addWidget(sb_minx, 2, 1)
        lay.addWidget(lb_minx, 2, 2)
        lay.addWidget(ld_maxx, 3, 0)
        lay.addWidget(sb_maxx, 3, 1)
        lay.addWidget(lb_maxx, 3, 2)
        lay.addWidget(ld_miny, 4, 0)
        lay.addWidget(sb_miny, 4, 1)
        lay.addWidget(lb_miny, 4, 2)
        lay.addWidget(ld_maxy, 5, 0)
        lay.addWidget(sb_maxy, 5, 1)
        lay.addWidget(lb_maxy, 5, 2)
        lay.addItem(QSpacerItem(1, 15, QSzPlc.Ignored, QSzPlc.Fixed), 6, 0)
        lay.addLayout(lay_mon, 7, 0, 1, 3)
        return lay
