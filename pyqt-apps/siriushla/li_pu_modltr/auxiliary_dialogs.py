"""Modulator auxiliary dialogs."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QGridLayout, QHBoxLayout, \
    QPushButton, QWidget, QVBoxLayout, QFrame

from pydm.widgets import PyDMPushButton

from siriuspy.envars import VACA_PREFIX
from siriuspy.namesys import SiriusPVName as _PVName

from ..widgets import SiriusDialog, SiriusLedState


class ModIntlkDetailDialog(SiriusDialog):
    """Modulator Interlock Details."""

    def __init__(self, parent=None, device='', prefix=VACA_PREFIX):
        """Init."""
        super().__init__(parent)
        self._prefix = prefix
        self._device = _PVName(device)
        self._mod_prefix = self._device.substitute(prefix=prefix)

        self.setWindowTitle('Modulator Interlock Details')
        self.setObjectName('LIApp')

        self._setupUi()

    def _setupUi(self):
        self.title = QLabel(
            '<h2>'+self._device.device_name+'</h2>', self,
            alignment=Qt.AlignCenter)

        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.addWidget(self.title, 0, 0, 1, 2)
        lay.addWidget(self._setupModSignalWidget(), 1, 0)
        lay.addWidget(self._setupExtIntlkSignalWidget(), 1, 1)

        self.setStyleSheet("""
            QLed{
                min-width: 1.29em; max-width: 1.29em;
            }""")

    def _setupModSignalWidget(self):
        self.lb_modsig = QLabel(
            '<h3>Modulator Signal</h3>', self, alignment=Qt.AlignCenter)
        self.lb_modsig.setStyleSheet('QLabel{min-height: 2em;}')

        gb_sig1 = QFrame(self)
        gb_sig1.setStyleSheet("""
            .QFrame{
                border-top: 2px solid gray;
                border-bottom: 1px solid gray;
                border-left: 2px solid gray;
                border-right: 2px solid gray;
            }""")
        lay_sig1 = QGridLayout(gb_sig1)
        signals = [
            'PFN_Cab_Temp', 'Tail_Clipper', 'EOLC1_Clipper', 'Thy_Fan',
            'CPS_Clipper', 'EOLC2_Clipper', 'Thy_Temp', 'Door_Interlock',
            'Ground_Rod', 'PFN_Cab_Fan', 'Thy_Trig_G1', 'Thy_Trig_G2',
            'Discharge_switch']
        for idx, sig in enumerate(signals):
            row = idx // 3
            col = idx % 3
            led = SiriusLedState(self, self._mod_prefix+':'+sig)
            led.offColor = led.Red
            lbl = QLabel(sig)
            hbox = QHBoxLayout()
            hbox.addWidget(led)
            hbox.addWidget(lbl)
            lay_sig1.addLayout(hbox, row, col)

        led_kly_nd = SiriusLedState(
            self, self._mod_prefix+':Kly_Heat_power')
        led_kly_nd.offColor = led_kly_nd.Red
        lbl_kly_nd = QLabel('Kly_Heat_power')
        hb_kly_nd = QHBoxLayout()
        hb_kly_nd.addWidget(led_kly_nd)
        hb_kly_nd.addWidget(lbl_kly_nd)
        led_kly_ov = SiriusLedState(self, self._mod_prefix+':Kly_F_Over')
        led_kly_ov.offColor = led_kly_ov.Red
        lbl_kly_ov = QLabel('Kly_F_Over')
        hb_kly_ov = QHBoxLayout()
        hb_kly_ov.addWidget(led_kly_ov)
        hb_kly_ov.addWidget(lbl_kly_ov)
        led_kly_un = SiriusLedState(self, self._mod_prefix+':Kly_F_Under')
        led_kly_un.offColor = led_kly_un.Red
        lbl_kly_un = QLabel('Kly_F_Under')
        hb_kly_un = QHBoxLayout()
        hb_kly_un.addWidget(led_kly_un)
        hb_kly_un.addWidget(lbl_kly_un)
        gb_sig2 = QFrame(self)
        gb_sig2.setStyleSheet("""
            .QFrame{
                border-top: 1px solid gray;
                border-bottom: 1px solid gray;
                border-left: 2px solid gray;
                border-right: 2px solid gray;
            }""")
        lay_sig2 = QGridLayout(gb_sig2)
        lay_sig2.addLayout(hb_kly_nd, 0, 0, 2, 1)
        lay_sig2.addLayout(hb_kly_ov, 0, 1)
        lay_sig2.addLayout(hb_kly_un, 1, 1)

        led_thy_nd = SiriusLedState(
            self, self._mod_prefix+':Thy_Heat_power')
        led_thy_nd.offColor = led_thy_nd.Red
        lbl_thy_nd = QLabel('Thy_Heat_power')
        hb_thy_nd = QHBoxLayout()
        hb_thy_nd.addWidget(led_thy_nd)
        hb_thy_nd.addWidget(lbl_thy_nd)
        led_thy_f = SiriusLedState(
            self, self._mod_prefix+':Thy_Filament_power')
        led_thy_f.offColor = led_thy_f.Red
        lbl_thy_f = QLabel('Thy_F_power')
        hb_thy_f = QHBoxLayout()
        hb_thy_f.addWidget(led_thy_f)
        hb_thy_f.addWidget(lbl_thy_f)
        led_thy_fo = SiriusLedState(self, self._mod_prefix+':Thy_F_Over')
        led_thy_fo.offColor = led_thy_fo.Red
        lbl_thy_fo = QLabel('Thy_F_Over')
        hb_thy_fo = QHBoxLayout()
        hb_thy_fo.addWidget(led_thy_fo)
        hb_thy_fo.addWidget(lbl_thy_fo)
        led_thy_fu = SiriusLedState(self, self._mod_prefix+':Thy_F_Under')
        led_thy_fu.offColor = led_thy_fu.Red
        lbl_thy_fu = QLabel('Thy_F_Under')
        hb_thy_fu = QHBoxLayout()
        hb_thy_fu.addWidget(led_thy_fu)
        hb_thy_fu.addWidget(lbl_thy_fu)
        led_thy_h = SiriusLedState(self, self._mod_prefix+':Thy_H_power')
        led_thy_h.offColor = led_thy_h.Red
        lbl_thy_h = QLabel('Thy_H_power')
        hb_thy_h = QHBoxLayout()
        hb_thy_h.addWidget(led_thy_h)
        hb_thy_h.addWidget(lbl_thy_h)
        led_thy_ho = SiriusLedState(self, self._mod_prefix+':Thy_H_Over')
        led_thy_ho.offColor = led_thy_ho.Red
        lbl_thy_ho = QLabel('Thy_H_Over')
        hb_thy_ho = QHBoxLayout()
        hb_thy_ho.addWidget(led_thy_ho)
        hb_thy_ho.addWidget(lbl_thy_ho)
        led_thy_hu = SiriusLedState(self, self._mod_prefix+':Thy_H_Under')
        led_thy_hu.offColor = led_thy_hu.Red
        lbl_thy_hu = QLabel('Thy_H_Under')
        hb_thy_hu = QHBoxLayout()
        hb_thy_hu.addWidget(led_thy_hu)
        hb_thy_hu.addWidget(lbl_thy_hu)
        gb_sig3 = QFrame(self)
        gb_sig3.setStyleSheet("""
            .QFrame{
                border-top: 1px solid gray;
                border-bottom: 1px solid gray;
                border-left: 2px solid gray;
                border-right: 2px solid gray;
            }""")
        lay_sig3 = QGridLayout(gb_sig3)
        lay_sig3.addLayout(hb_thy_nd, 0, 0, 4, 1)
        lay_sig3.addLayout(hb_thy_f, 0, 1, 2, 1)
        lay_sig3.addLayout(hb_thy_fo, 0, 2)
        lay_sig3.addLayout(hb_thy_fu, 1, 2)
        lay_sig3.addLayout(hb_thy_h, 2, 1, 2, 1)
        lay_sig3.addLayout(hb_thy_ho, 2, 2)
        lay_sig3.addLayout(hb_thy_hu, 3, 2)

        led_bias_nd = SiriusLedState(
            self, self._mod_prefix+':Bias_power')
        led_bias_nd.offColor = led_bias_nd.Red
        lbl_bias_nd = QLabel('Bias_power')
        hb_bias_nd = QHBoxLayout()
        hb_bias_nd.addWidget(led_bias_nd)
        hb_bias_nd.addWidget(lbl_bias_nd)
        led_bias_ov = SiriusLedState(self, self._mod_prefix+':Bias_Over')
        led_bias_ov.offColor = led_bias_ov.Red
        lbl_bias_ov = QLabel('Bias_Over')
        hb_bias_ov = QHBoxLayout()
        hb_bias_ov.addWidget(led_bias_ov)
        hb_bias_ov.addWidget(lbl_bias_ov)
        led_bias_un = SiriusLedState(self, self._mod_prefix+':Bias_Under')
        led_bias_un.offColor = led_bias_un.Red
        lbl_bias_un = QLabel('Bias_Under')
        hb_bias_un = QHBoxLayout()
        hb_bias_un.addWidget(led_bias_un)
        hb_bias_un.addWidget(lbl_bias_un)
        gb_sig4 = QFrame(self)
        gb_sig4.setStyleSheet("""
            .QFrame{
                border-top: 1px solid gray;
                border-bottom: 1px solid gray;
                border-left: 2px solid gray;
                border-right: 2px solid gray;
            }""")
        lay_sig4 = QGridLayout(gb_sig4)
        lay_sig4.addLayout(hb_bias_nd, 0, 0, 2, 1)
        lay_sig4.addLayout(hb_bias_ov, 0, 1)
        lay_sig4.addLayout(hb_bias_un, 1, 1)

        led_cps_nd = SiriusLedState(
            self, self._mod_prefix+':CPS_ALL')
        led_cps_nd.offColor = led_cps_nd.Red
        lbl_cps_nd = QLabel('CPS_ALL')
        hb_cps_nd = QHBoxLayout()
        hb_cps_nd.addWidget(led_cps_nd)
        hb_cps_nd.addWidget(lbl_cps_nd)
        led_cpsflt = SiriusLedState(self, self._mod_prefix+':CPS_Fault')
        led_cpsflt.offColor = led_cpsflt.Red
        lbl_cpsflt = QLabel('CPS_Fault')
        hb_cpsflt = QHBoxLayout()
        hb_cpsflt.addWidget(led_cpsflt)
        hb_cpsflt.addWidget(lbl_cpsflt)
        led_cpsilk = SiriusLedState(self, self._mod_prefix+':CPS_lock')
        led_cpsilk.offColor = led_cpsilk.Red
        lbl_cpsilk = QLabel('CPS_Interlock')
        hb_cpsilk = QHBoxLayout()
        hb_cpsilk.addWidget(led_cpsilk)
        hb_cpsilk.addWidget(lbl_cpsilk)
        led_cpsmns = SiriusLedState(self, self._mod_prefix+':CPS_Mains')
        led_cpsmns.offColor = led_cpsmns.Red
        lbl_cpsmns = QLabel('CPS_Mains')
        hb_cpsmns = QHBoxLayout()
        hb_cpsmns.addWidget(led_cpsmns)
        hb_cpsmns.addWidget(lbl_cpsmns)
        led_cpsonoff = SiriusLedState(self, self._mod_prefix+':CPS_ON_OFF')
        led_cpsonoff.offColor = led_cpsonoff.Red
        lbl_cpsonoff = QLabel('CPS_ON_OFF')
        hb_cpsonoff = QHBoxLayout()
        hb_cpsonoff.addWidget(led_cpsonoff)
        hb_cpsonoff.addWidget(lbl_cpsonoff)
        led_cpsilkin = SiriusLedState(
            self, self._mod_prefix+':CPS_Interlock_Input')
        led_cpsilkin.offColor = led_cpsilkin.Red
        lbl_cpsilkin = QLabel('CPS_Interlock_Input')
        hb_cpsilkin = QHBoxLayout()
        hb_cpsilkin.addWidget(led_cpsilkin)
        hb_cpsilkin.addWidget(lbl_cpsilkin)
        gb_sig5 = QFrame(self)
        gb_sig5.setStyleSheet("""
            .QFrame{
                border-top: 1px solid gray;
                border-bottom: 2px solid gray;
                border-left: 2px solid gray;
                border-right: 2px solid gray;
            }""")
        lay_sig5 = QGridLayout(gb_sig5)
        lay_sig5.addLayout(hb_cps_nd, 0, 0, 5, 1)
        lay_sig5.addLayout(hb_cpsflt, 0, 1)
        lay_sig5.addLayout(hb_cpsilk, 1, 1)
        lay_sig5.addLayout(hb_cpsmns, 2, 1)
        lay_sig5.addLayout(hb_cpsonoff, 3, 1)
        lay_sig5.addLayout(hb_cpsilkin, 4, 1)

        wid = QWidget(self)
        lay = QVBoxLayout(wid)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(0)
        lay.addWidget(self.lb_modsig)
        lay.addWidget(gb_sig1)
        lay.addWidget(gb_sig2)
        lay.addWidget(gb_sig3)
        lay.addWidget(gb_sig4)
        lay.addWidget(gb_sig5)
        return wid

    def _setupExtIntlkSignalWidget(self):
        self.lb_extsig = QLabel(
            '<h3>External Interlock Signal</h3>', self,
            alignment=Qt.AlignCenter)
        self.lb_extsig.setStyleSheet('QLabel{min-height: 2em;}')

        lbl_lvilk = QLabel(
            '<h4>LV_Interlock</h4>', self, alignment=Qt.AlignCenter)
        led_lvilk = SiriusLedState(self, self._mod_prefix+':LV_Interlock')
        led_lvilk.offColor = led_lvilk.Red

        lbl_lv1 = QLabel('1.Ti_Pump_pow')
        led_lv1 = SiriusLedState(self, self._mod_prefix+':Ti_Pump_pow')
        led_lv1.offColor = led_lv1.Red

        lbl_lv2 = QLabel('2.')
        led_lv2 = SiriusLedState(self, self._mod_prefix+':LV_reserved1')
        led_lv2.offColor = led_lv2.Red

        lbl_lv3 = QLabel('3.')
        led_lv3 = SiriusLedState(self, self._mod_prefix+':LV_reserved2')
        led_lv3.offColor = led_lv3.Red

        lbl_lv4 = QLabel('4.')
        led_lv4 = SiriusLedState(self, self._mod_prefix+':LV_reserved3')
        led_lv4.offColor = led_lv4.Red

        wid_lvilk = QFrame(self)
        wid_lvilk.setStyleSheet("""
            .QFrame{
                border-top: 2px solid gray;
                border-bottom: 2px solid gray;
                border-left: 2px solid gray;
                border-right: 1px solid gray;
            }""")
        lay_lvilk = QGridLayout(wid_lvilk)
        lay_lvilk.setAlignment(Qt.AlignTop)
        lay_lvilk.addWidget(led_lvilk, 0, 0, 1, 2, alignment=Qt.AlignCenter)
        lay_lvilk.addWidget(lbl_lvilk, 1, 0, 1, 2)
        lay_lvilk.addWidget(led_lv1, 2, 0)
        lay_lvilk.addWidget(lbl_lv1, 2, 1)
        lay_lvilk.addWidget(led_lv2, 3, 0)
        lay_lvilk.addWidget(lbl_lv2, 3, 1)
        lay_lvilk.addWidget(led_lv3, 4, 0)
        lay_lvilk.addWidget(lbl_lv3, 4, 1)
        lay_lvilk.addWidget(led_lv4, 5, 0)
        lay_lvilk.addWidget(lbl_lv4, 5, 1)

        lbl_hvilk = QLabel(
            '<h4>HV_Interlock</h4>', self, alignment=Qt.AlignCenter)
        led_hvilk = SiriusLedState(self, self._mod_prefix+':HV_Interlock')
        led_hvilk.offColor = led_hvilk.Red

        lbl_hv1 = QLabel('1.Oil_tank_w')
        led_hv1 = SiriusLedState(self, self._mod_prefix+':Oil_tank_w')
        led_hv1.offColor = led_hv1.Red

        lbl_hv2 = QLabel('2.Collector_w')
        led_hv2 = SiriusLedState(self, self._mod_prefix+':Collector_w')
        led_hv2.offColor = led_hv2.Red

        lbl_hv3 = QLabel('3.PPS')
        led_hv3 = SiriusLedState(self, self._mod_prefix+':PPS')
        led_hv3.offColor = led_hv3.Red

        lbl_hv4 = QLabel('4.Focus_pow')
        led_hv4 = SiriusLedState(self, self._mod_prefix+':Focus_pow')
        led_hv4.offColor = led_hv4.Red

        lbl_hv5 = QLabel('5.')
        led_hv5 = SiriusLedState(self, self._mod_prefix+':HV_reserved2')
        led_hv5.offColor = led_hv5.Red

        lbl_hv6 = QLabel('6.')
        led_hv6 = SiriusLedState(self, self._mod_prefix+':HV_reserved3')
        led_hv6.offColor = led_hv6.Red

        wid_hvilk = QFrame(self)
        wid_hvilk.setStyleSheet("""
            .QFrame{
                border-top: 2px solid gray;
                border-bottom: 2px solid gray;
                border-left: 1px solid gray;
                border-right: 1px solid gray;
            }""")
        lay_hvilk = QGridLayout(wid_hvilk)
        lay_hvilk.setAlignment(Qt.AlignTop)
        lay_hvilk.addWidget(led_hvilk, 0, 0, 1, 2, alignment=Qt.AlignCenter)
        lay_hvilk.addWidget(lbl_hvilk, 1, 0, 1, 2)
        lay_hvilk.addWidget(led_hv1, 2, 0)
        lay_hvilk.addWidget(lbl_hv1, 2, 1)
        lay_hvilk.addWidget(led_hv2, 3, 0)
        lay_hvilk.addWidget(lbl_hv2, 3, 1)
        lay_hvilk.addWidget(led_hv3, 4, 0)
        lay_hvilk.addWidget(lbl_hv3, 4, 1)
        lay_hvilk.addWidget(led_hv4, 5, 0)
        lay_hvilk.addWidget(lbl_hv4, 5, 1)
        lay_hvilk.addWidget(led_hv5, 6, 0)
        lay_hvilk.addWidget(lbl_hv5, 6, 1)
        lay_hvilk.addWidget(led_hv6, 7, 0)
        lay_hvilk.addWidget(lbl_hv6, 7, 1)

        lbl_trilk = QLabel(
            '<h4>TR_Interlock</h4>', self, alignment=Qt.AlignCenter)
        led_trilk = SiriusLedState(self, self._mod_prefix+':TR_Interlock')
        led_trilk.offColor = led_trilk.Red

        lbl_tr1 = QLabel('1.Waveguide_w')
        led_tr1 = SiriusLedState(self, self._mod_prefix+':Waveguide_w')
        led_tr1.offColor = led_tr1.Red

        lbl_tr2 = QLabel('2.')
        led_tr2 = SiriusLedState(self, self._mod_prefix+':Wave_window_w')
        led_tr2.offColor = led_tr2.Red

        lbl_tr3 = QLabel('3.MPS')
        led_tr3 = SiriusLedState(self, self._mod_prefix+':MPS')
        led_tr3.offColor = led_tr3.Red

        lbl_tr4 = QLabel('4.')
        led_tr4 = SiriusLedState(self, self._mod_prefix+':TR_reserved2')
        led_tr4.offColor = led_tr4.Red

        lbl_tr5 = QLabel('5.')
        led_tr5 = SiriusLedState(self, self._mod_prefix+':TR_reserved3')
        led_tr5.offColor = led_tr5.Red

        lbl_tr6 = QLabel('6.')
        led_tr6 = SiriusLedState(self, self._mod_prefix+':TR_reserved4')
        led_tr6.offColor = led_tr6.Red

        lbl_tr7 = QLabel('7.')
        led_tr7 = SiriusLedState(self, self._mod_prefix+':TR_reserved5')
        led_tr7.offColor = led_tr7.Red

        lbl_tr8 = QLabel('8.')
        led_tr8 = SiriusLedState(self, self._mod_prefix+':TR_reserved6')
        led_tr8.offColor = led_tr8.Red

        wid_trilk = QFrame(self)
        wid_trilk.setStyleSheet("""
            .QFrame{
                border-top: 2px solid gray;
                border-bottom: 2px solid gray;
                border-left: 1px solid gray;
                border-right: 2px solid gray;
            }""")
        lay_trilk = QGridLayout(wid_trilk)
        lay_trilk.setAlignment(Qt.AlignTop)
        lay_trilk.addWidget(led_trilk, 0, 0, 1, 2, alignment=Qt.AlignCenter)
        lay_trilk.addWidget(lbl_trilk, 1, 0, 1, 2)
        lay_trilk.addWidget(led_tr1, 2, 0)
        lay_trilk.addWidget(lbl_tr1, 2, 1)
        lay_trilk.addWidget(led_tr2, 3, 0)
        lay_trilk.addWidget(lbl_tr2, 3, 1)
        lay_trilk.addWidget(led_tr3, 4, 0)
        lay_trilk.addWidget(lbl_tr3, 4, 1)
        lay_trilk.addWidget(led_tr4, 5, 0)
        lay_trilk.addWidget(lbl_tr4, 5, 1)
        lay_trilk.addWidget(led_tr5, 6, 0)
        lay_trilk.addWidget(lbl_tr5, 6, 1)
        lay_trilk.addWidget(led_tr6, 7, 0)
        lay_trilk.addWidget(lbl_tr6, 7, 1)
        lay_trilk.addWidget(led_tr7, 8, 0)
        lay_trilk.addWidget(lbl_tr7, 8, 1)
        lay_trilk.addWidget(led_tr8, 9, 0)
        lay_trilk.addWidget(lbl_tr8, 9, 1)

        wid = QWidget(self)
        lay = QGridLayout(wid)
        lay.setVerticalSpacing(0)
        lay.setHorizontalSpacing(0)
        lay.setAlignment(Qt.AlignTop)
        lay.addWidget(self.lb_extsig, 0, 0, 1, 3)
        lay.addWidget(wid_lvilk, 1, 0)
        lay.addWidget(wid_hvilk, 1, 1)
        lay.addWidget(wid_trilk, 1, 2)
        return wid


class ModEmerStopDialog(SiriusDialog):
    """Modulator Emergency Stop Window."""

    def __init__(self, parent=None, device='', prefix=VACA_PREFIX):
        """Init."""
        super().__init__(parent)
        self.setObjectName('LIApp')
        self._prefix = prefix
        self._device = _PVName(device)
        self._mod_prefix = self._device.substitute(prefix=prefix)

        self.setWindowTitle(
            self._device.dev+' '+self._device.idx+' - Emergency Stop')
        self._setupUi()

    def _setupUi(self):
        self._lb_desc = QLabel(
            '<h3>Are you sure to Poweroff '+self._device.dev+' ' +
            self._device.idx+'?</h3>')

        self._pb_yes = PyDMPushButton(
            self, label='YES', pressValue=1,
            init_channel=self._mod_prefix + ':EMER_STOP')
        self._pb_yes.setObjectName('yes')
        self._pb_yes.setStyleSheet('#yes{background-color:red;}')

        self._pb_exit = QPushButton('EXIT', self)
        self._pb_exit.clicked.connect(self.close)

        lay = QGridLayout(self)
        lay.setHorizontalSpacing(20)
        lay.setVerticalSpacing(20)
        lay.addWidget(self._lb_desc, 0, 0, 1, 2)
        lay.addWidget(self._pb_yes, 1, 0, alignment=Qt.AlignCenter)
        lay.addWidget(self._pb_exit, 1, 1, alignment=Qt.AlignCenter)
