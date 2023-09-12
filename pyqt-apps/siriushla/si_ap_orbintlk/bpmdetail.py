"""Individual BPM Orbit Interlock Window."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGridLayout, QLabel, QGroupBox, \
    QSpacerItem, QSizePolicy as QSzPlc

import qtawesome as qta

from pydm.widgets import PyDMPushButton

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy.namesys import SiriusPVName

from ..widgets import SiriusMainWindow, SiriusLedState, SiriusLabel, \
    PyDMStateButton, SiriusLedAlert, SiriusSpinbox, SiriusLineEdit
from .base import BaseObject


class BPMOrbIntlkDetailWindow(BaseObject, SiriusMainWindow):
    """Individual BPM Orbit Interlock Window."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        BaseObject.__init__(self, prefix)
        SiriusMainWindow.__init__(self, parent)

        self.prefix = prefix
        self.device = SiriusPVName(device)
        self.devpref = self.device.substitute(prefix=prefix)

        self.setObjectName(self.device.sec+'App')
        self.setWindowTitle(device+' Orbit Interlock Control Window')

        self._setupUi()

        self.setFocusPolicy(Qt.StrongFocus)

    def _setupUi(self):
        wid = QWidget(self)
        self.setCentralWidget(wid)
        lay = QGridLayout(wid)

        title = QLabel(
            '<h3>' + self.device + ' Orbit Interlock Control</h3>',
            self, alignment=Qt.AlignCenter)
        lay.addWidget(title, 0, 0, 1, 2)

        try:
            down, up = self.get_down_up_bpms(self.device)
            other = down if self.device == up else up
            titlehelp = QLabel(
                '<h3>(also refers to ' + other + ')</h3>',
                self, alignment=Qt.AlignCenter)
            lay.addWidget(titlehelp, 1, 0, 1, 2)
        except ValueError:
            pass

        # General Interlock
        self._gb_gen = QGroupBox('General Interlock')
        lay_gen = self._setupIntlkGenLayout()
        self._gb_gen.setLayout(lay_gen)
        lay.addWidget(self._gb_gen, 2, 0, 1, 2)

        # Position Interlock
        self._gb_pos = QGroupBox('Position Interlock')
        lay_pos = self._setupIntlkTypeLayout('Pos')
        self._gb_pos.setLayout(lay_pos)
        lay.addWidget(self._gb_pos, 3, 0)

        # Angulation Interlock
        self._gb_ang = QGroupBox('Angulation Interlock')
        lay_ang = self._setupIntlkTypeLayout('Ang')
        self._gb_ang.setLayout(lay_ang)
        lay.addWidget(self._gb_ang, 3, 1)

    def _setupIntlkGenLayout(self):
        self._ld_genenbl = QLabel(
            'Enable: ', self, alignment=Qt.AlignRight | Qt.AlignBottom)
        self._sb_genenbl = PyDMStateButton(
            self, self.devpref.substitute(propty='IntlkEn-Sel'))
        self._led_genenbl = SiriusLedState(
            self, self.devpref.substitute(propty='IntlkEn-Sts'))

        self._ld_genclr = QLabel(
            'Reset: ', self, alignment=Qt.AlignRight | Qt.AlignBottom)
        self._bt_genclr = PyDMPushButton(
            self,
            init_channel=self.devpref.substitute(propty='IntlkClr-Cmd'),
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
        self._le_minsumlim = SiriusLineEdit(
            self, self.devpref.substitute(propty='IntlkLmtMinSum-SP'))
        self._le_minsumlim.setStyleSheet('QLineEdit{max-width: 12em;}')
        self._lb_minsumlim = SiriusLabel(
            self, self.devpref.substitute(propty='IntlkLmtMinSum-RB'))
        self._lb_minsumlim.displayFormat = SiriusLabel.Exponential
        self._lb_minsumlim.precisionFromPV = False
        self._lb_minsumlim.precision = 16
        self._lb_minsumlim.showUnits = True

        lay = QGridLayout()
        lay.setAlignment(Qt.AlignCenter)
        lay.addWidget(self._ld_genenbl, 0, 0)
        lay.addWidget(self._sb_genenbl, 0, 1)
        lay.addWidget(self._led_genenbl, 0, 2, alignment=Qt.AlignLeft)
        lay.addWidget(self._ld_genclr, 1, 0)
        lay.addWidget(self._bt_genclr, 1, 1, alignment=Qt.AlignCenter)
        lay.addWidget(self._ld_intlkinst, 2, 0)
        lay.addWidget(self._led_intlkinst, 2, 1)
        lay.addWidget(self._ld_intlkltc, 3, 0)
        lay.addWidget(self._led_intlkltc, 3, 1)
        lay.addItem(QSpacerItem(1, 15, QSzPlc.Ignored, QSzPlc.Fixed), 4, 0)
        lay.addWidget(self._ld_minsumenbl, 5, 0)
        lay.addWidget(self._sb_minsumenbl, 5, 1)
        lay.addWidget(self._led_minsumenbl, 5, 2, alignment=Qt.AlignLeft)
        lay.addWidget(self._ld_minsumlim, 6, 0)
        lay.addWidget(self._le_minsumlim, 6, 1)
        lay.addWidget(self._lb_minsumlim, 6, 2)
        return lay

    def _setupIntlkTypeLayout(self, intlk):
        unit = 'nm'

        ld_valx = QLabel(
            intlk+'. X ['+unit+']: ', self,
            alignment=Qt.AlignRight | Qt.AlignBottom)
        lb_valx = SiriusLabel(
            self, self.devpref.substitute(propty='Intlk'+intlk+'X-Mon'))
        ld_valy = QLabel(
            intlk+'. Y ['+unit+']: ', self,
            alignment=Qt.AlignRight | Qt.AlignBottom)
        lb_valy = SiriusLabel(
            self, self.devpref.substitute(propty='Intlk'+intlk+'Y-Mon'))

        ld_enbl = QLabel(
            'Enable: ', self, alignment=Qt.AlignRight | Qt.AlignBottom)
        sb_enbl = PyDMStateButton(
            self, self.devpref.substitute(propty='Intlk'+intlk+'En-Sel'))
        led_enbl = SiriusLedState(
            self, self.devpref.substitute(propty='Intlk'+intlk+'En-Sts'))

        ld_clr = QLabel(
            'Reset: ', self, alignment=Qt.AlignRight | Qt.AlignBottom)
        bt_clr = PyDMPushButton(
            self, init_channel=self.devpref.substitute(
                propty='Intlk'+intlk+'Clr-Cmd'), pressValue=1)
        bt_clr.setIcon(qta.icon('fa5s.sync'))
        bt_clr.setObjectName('clr')
        bt_clr.setStyleSheet(
            '#clr{min-width:25px; max-width:25px; icon-size:20px;}')

        ld_minx = QLabel(
            'Min.X Thres.['+unit+']: ', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter)
        sb_minx = SiriusSpinbox(
            self, self.devpref.substitute(propty='IntlkLmt'+intlk+'MinX-SP'))
        sb_minx.limitsFromChannel = False
        sb_minx.setMinimum(-1e9)
        sb_minx.setMaximum(+1e9)
        lb_minx = SiriusLabel(
            self, self.devpref.substitute(propty='IntlkLmt'+intlk+'MinX-RB'))

        ld_maxx = QLabel(
            'Max.X Thres.['+unit+']: ', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter)
        sb_maxx = SiriusSpinbox(
            self, self.devpref.substitute(propty='IntlkLmt'+intlk+'MaxX-SP'))
        sb_maxx.limitsFromChannel = False
        sb_maxx.setMinimum(-1e9)
        sb_maxx.setMaximum(+1e9)
        lb_maxx = SiriusLabel(
            self, self.devpref.substitute(propty='IntlkLmt'+intlk+'MaxX-RB'))

        ld_miny = QLabel(
            'Min.Y Thres.['+unit+']: ', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter)
        sb_miny = SiriusSpinbox(
            self, self.devpref.substitute(propty='IntlkLmt'+intlk+'MinY-SP'))
        sb_miny.limitsFromChannel = False
        sb_miny.setMinimum(-1e9)
        sb_miny.setMaximum(+1e9)
        lb_miny = SiriusLabel(
            self, self.devpref.substitute(propty='IntlkLmt'+intlk+'MinY-RB'))

        ld_maxy = QLabel(
            'Max.Y Thres.['+unit+']: ', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter)
        sb_maxy = SiriusSpinbox(
            self, self.devpref.substitute(propty='IntlkLmt'+intlk+'MaxY-SP'))
        sb_maxy.limitsFromChannel = False
        sb_maxy.setMinimum(-1e9)
        sb_maxy.setMaximum(+1e9)
        lb_maxy = SiriusLabel(
            self, self.devpref.substitute(propty='IntlkLmt'+intlk+'MaxY-RB'))

        ld_leglow = QLabel(
            'Lower', self, alignment=Qt.AlignCenter)
        ld_leghigh = QLabel(
            'Upper', self, alignment=Qt.AlignCenter)

        ld_leginst = QLabel(
            '<h4>Instantaneous</h4>', self, alignment=Qt.AlignCenter)
        ld_leginst_any = QLabel(
            'X or Y', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        led_inst_anylow = SiriusLedAlert(
            self, self.devpref.substitute(propty='Intlk'+intlk+'Lower-Mon'))
        led_inst_anyhigh = SiriusLedAlert(
            self, self.devpref.substitute(propty='Intlk'+intlk+'Upper-Mon'))
        ld_leginst_x = QLabel(
            'X', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        led_inst_xlow = SiriusLedAlert(
            self, self.devpref.substitute(propty='Intlk'+intlk+'LowerX-Mon'))
        led_inst_xhigh = SiriusLedAlert(
            self, self.devpref.substitute(propty='Intlk'+intlk+'UpperX-Mon'))
        ld_leginst_y = QLabel(
            'Y', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        led_inst_ylow = SiriusLedAlert(
            self, self.devpref.substitute(propty='Intlk'+intlk+'LowerY-Mon'))
        led_inst_yhigh = SiriusLedAlert(
            self, self.devpref.substitute(propty='Intlk'+intlk+'UpperY-Mon'))

        ld_legltc = QLabel(
            '<h4>Latch</h4>', self, alignment=Qt.AlignCenter)
        ld_legltc_any = QLabel(
            'X or Y', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        led_ltc_anylow = SiriusLedAlert(
            self, self.devpref.substitute(
                propty='Intlk'+intlk+'LowerLtc-Mon'))
        led_ltc_anyhigh = SiriusLedAlert(
            self, self.devpref.substitute(
                propty='Intlk'+intlk+'UpperLtc-Mon'))
        ld_legltc_x = QLabel(
            'X', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        led_ltc_xlow = SiriusLedAlert(
            self, self.devpref.substitute(
                propty='Intlk'+intlk+'LowerLtcX-Mon'))
        led_ltc_xhigh = SiriusLedAlert(
            self, self.devpref.substitute(
                propty='Intlk'+intlk+'UpperLtcX-Mon'))
        ld_legltc_y = QLabel(
            'Y', self, alignment=Qt.AlignRight | Qt.AlignVCenter)
        led_ltc_ylow = SiriusLedAlert(
            self, self.devpref.substitute(
                propty='Intlk'+intlk+'LowerLtcY-Mon'))
        led_ltc_yhigh = SiriusLedAlert(
            self, self.devpref.substitute(
                propty='Intlk'+intlk+'UpperLtcY-Mon'))

        lay_mon = QGridLayout()
        lay_mon.setAlignment(Qt.AlignCenter)
        lay_mon.addWidget(ld_leglow, 0, 1)
        lay_mon.addWidget(ld_leghigh, 0, 2)
        lay_mon.addWidget(ld_leginst, 1, 0)
        lay_mon.addWidget(ld_leginst_any, 2, 0)
        lay_mon.addWidget(led_inst_anylow, 2, 1)
        lay_mon.addWidget(led_inst_anyhigh, 2, 2)
        lay_mon.addWidget(ld_leginst_x, 3, 0)
        lay_mon.addWidget(led_inst_xlow, 3, 1)
        lay_mon.addWidget(led_inst_xhigh, 3, 2)
        lay_mon.addWidget(ld_leginst_y, 4, 0)
        lay_mon.addWidget(led_inst_ylow, 4, 1)
        lay_mon.addWidget(led_inst_yhigh, 4, 2)
        lay_mon.addWidget(ld_legltc, 5, 0)
        lay_mon.addWidget(ld_legltc_any, 6, 0)
        lay_mon.addWidget(led_ltc_anylow, 6, 1)
        lay_mon.addWidget(led_ltc_anyhigh, 6, 2)
        lay_mon.addWidget(ld_legltc_x, 7, 0)
        lay_mon.addWidget(led_ltc_xlow, 7, 1)
        lay_mon.addWidget(led_ltc_xhigh, 7, 2)
        lay_mon.addWidget(ld_legltc_y, 8, 0)
        lay_mon.addWidget(led_ltc_ylow, 8, 1)
        lay_mon.addWidget(led_ltc_yhigh, 8, 2)

        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.addWidget(ld_valx, 0, 0)
        lay.addWidget(lb_valx, 0, 1)
        lay.addWidget(ld_valy, 1, 0)
        lay.addWidget(lb_valy, 1, 1)
        lay.addWidget(ld_enbl, 2, 0)
        lay.addWidget(sb_enbl, 2, 1)
        lay.addWidget(led_enbl, 2, 2)
        lay.addWidget(ld_clr, 3, 0)
        lay.addWidget(bt_clr, 3, 1, alignment=Qt.AlignCenter)
        lay.addWidget(ld_minx, 4, 0)
        lay.addWidget(sb_minx, 4, 1)
        lay.addWidget(lb_minx, 4, 2)
        lay.addWidget(ld_maxx, 5, 0)
        lay.addWidget(sb_maxx, 5, 1)
        lay.addWidget(lb_maxx, 5, 2)
        lay.addWidget(ld_miny, 6, 0)
        lay.addWidget(sb_miny, 6, 1)
        lay.addWidget(lb_miny, 6, 2)
        lay.addWidget(ld_maxy, 7, 0)
        lay.addWidget(sb_maxy, 7, 1)
        lay.addWidget(lb_maxy, 7, 2)
        lay.addItem(QSpacerItem(1, 15, QSzPlc.Ignored, QSzPlc.Fixed), 8, 0)
        lay.addLayout(lay_mon, 9, 0, 1, 3)
        return lay
