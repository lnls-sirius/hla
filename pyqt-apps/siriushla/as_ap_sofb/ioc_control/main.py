"""Define Controllers for the orbits displayed in the graphic."""

import numpy as _np
from qtpy.QtWidgets import QLabel, QGroupBox, QPushButton, QFormLayout, \
    QVBoxLayout, QHBoxLayout
from pydm.widgets import PyDMPushButton
from siriushla.widgets import SiriusConnectionSignal, PyDMStateButton, \
        SiriusLedAlert
from siriushla.widgets.windows import create_window_from_widget
import siriushla.util as _util

from siriushla.as_ap_sofb.ioc_control.status import StatusWidget
from siriushla.as_ap_sofb.ioc_control.kicks_config import KicksConfigWidget
from siriushla.as_ap_sofb.ioc_control.orbit_acquisition import AcqControlWidget
from siriushla.as_ap_sofb.ioc_control.respmat import RespMatWidget
from siriushla.as_ap_sofb.ioc_control.base import BaseWidget, BaseCombo


class SOFBControl(BaseWidget):

    def __init__(self, parent, prefix, ctrls, acc='SI'):
        super().__init__(parent, prefix, acc=acc)
        self.ctrls = ctrls
        self.setupui()
        self.setObjectName('SOFBControl')
        self.setStyleSheet("""
            #SOFBControl{
                min-width:18em;
                min-height:48em;
            }""")

    def setupui(self):
        hbl = QHBoxLayout(self)
        grp_bx = QGroupBox(self)
        hbl.addWidget(grp_bx)
        grp_bx.setTitle(self.acc + ' SOFB Control')

        vbl = QVBoxLayout(grp_bx)
        vbl.setContentsMargins(9, -1, -1, 9)

        # ####################################################################
        # ########################### STATUS #################################
        # ####################################################################
        btn = QPushButton('Correctors Status', grp_bx)
        Window = create_window_from_widget(
            StatusWidget, title='Correctors Status')
        _util.connect_window(
            btn, Window, self, prefix=self.prefix, acc=self.acc, is_orb=False)
        pdm_led = SiriusLedAlert(
            grp_bx, init_channel=self.prefix+'CorrStatus-Mon')
        hbl = QHBoxLayout()
        hbl.setSpacing(9)
        hbl.addWidget(btn)
        hbl.addWidget(pdm_led)
        vbl.addItem(hbl)

        btn = QPushButton('Orbit Status', grp_bx)
        Window = create_window_from_widget(StatusWidget, title='Orbit Status')
        _util.connect_window(
            btn, Window, self, prefix=self.prefix, acc=self.acc, is_orb=True)
        pdm_led = SiriusLedAlert(
            grp_bx, init_channel=self.prefix+'OrbStatus-Mon')
        hbl = QHBoxLayout()
        hbl.setSpacing(9)
        hbl.addWidget(btn)
        hbl.addWidget(pdm_led)
        vbl.addItem(hbl)

        vbl.addSpacing(40)
        # ####################################################################
        # ####################### Auto Correction ############################
        # ####################################################################
        if self.isring:
            rules = (
                '[{"name": "EnblRule", "property": "Enable", ' +
                '"expression": "ch[0] in (1, )", "channels": [{"channel": "' +
                self.prefix+'SOFBMode-Sts'+'", "trigger": true}]}]')
            lbl = QLabel('Closed Loop Status', grp_bx)
            pdm_btn = PyDMStateButton(
                grp_bx, init_channel=self.prefix+'ClosedLoop-Sel')
            pdm_btn.rules = rules
            hbl = QHBoxLayout()
            hbl.addWidget(lbl)
            hbl.addWidget(pdm_btn)
            vbl.addItem(hbl)

            lbl = QLabel('Frequency [Hz]', grp_bx)
            wid = self.create_pair(grp_bx, 'ClosedLoopFreq')
            fbl = QFormLayout()
            fbl.setHorizontalSpacing(9)
            fbl.addRow(lbl, wid)
            vbl.addItem(fbl)

            vbl.addSpacing(40)
        # ####################################################################
        # ########################## Orbit PVs ###############################
        # ####################################################################
        fbl = QFormLayout()
        fbl.setSpacing(9)
        vbl.addItem(fbl)

        lbl = QLabel('SOFB Mode', grp_bx)
        wid = self.create_pair_sel(grp_bx, 'SOFBMode')
        fbl.addRow(lbl, wid)

        lbl = QLabel('Correct:', grp_bx)
        combo = OfflineOrbControl(
            self, self.prefix, self.ctrls, self.acc)
        combo.rules = (
            '[{"name": "EnblRule", "property": "Enable", ' +
            '"expression": "not ch[0]", "channels": [{"channel": "' +
            self.prefix+'SOFBMode-Sts'+'", "trigger": true}]}]')
        fbl.addRow(lbl, combo)

        lbl = QLabel('as diff to:', grp_bx)
        combo = RefControl(self, self.prefix, self.ctrls, self.acc)
        fbl.addRow(lbl, combo)

        vbl.addSpacing(40)
        # ####################################################################
        # ######################## Kicks Configs. ############################
        # ####################################################################
        wid = KicksConfigWidget(grp_bx, self.prefix, self.acc, False)
        vbl.addWidget(wid)
        vbl.addSpacing(40)
        # ####################################################################
        # ###################### Manual Correction ###########################
        # ####################################################################
        grpbx = QGroupBox('Manual Correction', self)
        hbl = QHBoxLayout(grpbx)
        hbl.setSpacing(9)
        vbl.addWidget(grpbx)

        vbl2 = QVBoxLayout()
        hbl.addItem(vbl2)
        vbl2.setSpacing(9)
        pdm_pbtn = PyDMPushButton(
            grpbx, 'Calculate Kicks', pressValue=1,
            init_channel=self.prefix+'CalcDelta-Cmd')
        if self.isring:
            rules = (
                '[{"name": "EnblRule", "property": "Enable", ' +
                '"expression": "not ch[0]", "channels": [{"channel": "' +
                self.prefix+'ClosedLoop-Sts'+'", "trigger": true}]}]')
            pdm_pbtn.rules = rules
        vbl2.addWidget(pdm_pbtn)

        exp = 'ch[0] in (1, 3)'
        ch = ''
        if self.isring:
            exp = 'ch[1] in (1, 3) and not ch[0]'
            ch = '{"channel": "' + self.prefix + \
                'ClosedLoop-Sts", "trigger": true},'
        rules = (
            '[{"name": "EnblRule", "property": "Enable", ' +
            '"expression": "'+exp+'", "channels": ['+ch +
            '{"channel": "'+self.prefix+'SOFBMode-Sts", "trigger": true}]}]')

        pdm_pbtn = PyDMPushButton(
            grpbx, 'Apply All',
            pressValue=self._csorb.ApplyDelta.All,
            init_channel=self.prefix+'ApplyDelta-Cmd')
        pdm_pbtn.rules = rules
        vbl2.addWidget(pdm_pbtn)

        vbl3 = QVBoxLayout()
        hbl.addItem(vbl3)
        vbl3.setSpacing(9)
        pdm_pbtn = PyDMPushButton(
            grpbx, 'Apply CH',
            pressValue=self._csorb.ApplyDelta.CH,
            init_channel=self.prefix+'ApplyDelta-Cmd')
        pdm_pbtn.rules = rules
        vbl3.addWidget(pdm_pbtn)
        pdm_pbtn = PyDMPushButton(
            grpbx, 'Apply CV',
            pressValue=self._csorb.ApplyDelta.CV,
            init_channel=self.prefix+'ApplyDelta-Cmd')
        pdm_pbtn.rules = rules
        vbl3.addWidget(pdm_pbtn)
        if self.isring:
            pdm_pbtn = PyDMPushButton(
                grpbx, 'Apply RF',
                pressValue=self._csorb.ApplyDelta.RF,
                init_channel=self.prefix+'ApplyDelta-Cmd')
            pdm_pbtn.rules = rules
            vbl3.addWidget(pdm_pbtn)

        vbl.addSpacing(40)
        # ####################################################################
        # ###################### Detailed Configurations #####################
        # ####################################################################
        grpbx = QGroupBox('Detailed Configurations', self)
        vbl.addWidget(grpbx)
        vbl2 = QVBoxLayout(grpbx)
        vbl2.setSpacing(9)
        Window = create_window_from_widget(
            RespMatWidget, title='Response Matrix')
        btn = QPushButton('Response Matrix', grpbx)
        vbl2.addWidget(btn)
        _util.connect_window(
            btn, Window, grpbx, prefix=self.prefix, acc=self.acc)
        Window = create_window_from_widget(
            KicksConfigWidget, title='Correctors')
        btn = QPushButton('Correctors', grpbx)
        vbl2.addWidget(btn)
        _util.connect_window(
            btn, Window, grpbx, prefix=self.prefix, acc=self.acc,
            show_details=True)
        Window = create_window_from_widget(
            AcqControlWidget, title='Orbit Acquisition')
        btn = QPushButton('Orbit Acquisition', grpbx)
        _util.connect_window(
            btn, Window, grpbx, prefix=self.prefix, acc=self.acc)
        vbl2.addWidget(btn)


class RefControl(BaseCombo):
    def __init__(self, parent, prefix, ctrls, acc='SI'):
        setpoint = dict()
        readback = dict()
        setpoint['x'] = SiriusConnectionSignal(prefix+'RefOrbX-SP')
        setpoint['y'] = SiriusConnectionSignal(prefix+'RefOrbY-SP')
        readback['x'] = SiriusConnectionSignal(prefix+'RefOrbX-RB')
        readback['y'] = SiriusConnectionSignal(prefix+'RefOrbY-RB')
        super().__init__(parent, ctrls, setpoint, readback, acc)

    def _selection_changed(self, text):
        sigs = dict()
        if text.lower().startswith('zero'):
            for pln in ('x', 'y'):
                if self.orbits[pln] is not None:
                    self.orbits[pln] *= 0
                    self.setpoint[pln].send_value_signal[_np.ndarray].emit(
                        self.orbits[pln])
        super()._selection_changed(text, sigs)

    def setup_ui(self):
        super().setup_ui(['Zero', ])


class OfflineOrbControl(BaseCombo):
    def __init__(self, parent, prefix, ctrls, acc='SI'):
        setpoint = dict()
        readback = dict()
        setpoint['x'] = SiriusConnectionSignal(prefix+'OfflineOrbX-SP')
        setpoint['y'] = SiriusConnectionSignal(prefix+'OfflineOrbY-SP')
        readback['x'] = SiriusConnectionSignal(prefix+'OfflineOrbX-RB')
        readback['y'] = SiriusConnectionSignal(prefix+'OfflineOrbY-RB')
        super().__init__(parent, ctrls, setpoint, readback, acc)


def _main():
    app = SiriusApplication()
    win = SiriusDialog()
    hbl = QHBoxLayout(win)
    prefix = pref+'SI-Glob:AP-SOFB:'
    pvs = [
        'SlowOrbX-Mon', 'SlowOrbY-Mon',
        'OfflineOrbX-RB', 'OfflineOrbY-RB',
        'RefOrbX-RB', 'RefOrbY-RB']
    chans = []
    for pv in pvs:
        chans.append(SiriusConnectionSignal(prefix+pv))
    win._channels = chans
    ctrls = {
        'SlowOrb': {
            'x': {
                'signal': chans[0].new_value_signal,
                'getvalue': chans[0].getvalue},
            'y': {
                'signal': chans[1].new_value_signal,
                'getvalue': chans[1].getvalue}},
        'OfflineOrb': {
            'x': {
                'signal': chans[2].new_value_signal,
                'getvalue': chans[2].getvalue},
            'y': {
                'signal': chans[3].new_value_signal,
                'getvalue': chans[3].getvalue}},
        'RefOrb': {
            'x': {
                'signal': chans[4].new_value_signal,
                'getvalue': chans[4].getvalue},
            'y': {
                'signal': chans[5].new_value_signal,
                'getvalue': chans[5].getvalue}}}
    wid = SOFBControl(win, prefix, ctrls)
    hbl.addWidget(wid)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    from siriuspy.envars import vaca_prefix as pref
    import sys
    _main()
