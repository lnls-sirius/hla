"""Define Controllers for the orbits displayed in the graphic."""

import numpy as _np
from qtpy.QtWidgets import QLabel, QGroupBox, QPushButton, QFormLayout, \
    QVBoxLayout, QHBoxLayout
from qtpy.QtCore import QSize
from pydm.widgets import PyDMPushButton
from siriushla.widgets import SiriusConnectionSignal, PyDMStateButton, \
        SiriusLedAlert
from siriuspy.csdevice.orbitcorr import OrbitCorrDev
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
        self.setup_ui()

    def setup_ui(self):
        hbl = QHBoxLayout(self)
        grp_bx = QGroupBox(self)
        hbl.addWidget(grp_bx)
        grp_bx.setTitle(self.acc + ' SOFB Control')

        vbl = QVBoxLayout(grp_bx)
        vbl.setContentsMargins(9, -1, -1, 9)

        # ####################################################################
        # ########################### STATUS #################################
        # ####################################################################
        btn = QPushButton('Open Status', grp_bx)
        Window = create_window_from_widget(
            StatusWidget, name='StatusWindow')
        _util.connect_window(
            btn, Window, self, prefix=self.prefix, acc=self.acc, is_orb=False)
        pdm_led = SiriusLedAlert(
            grp_bx, init_channel=self.prefix+'CorrStatus-Mon')
        pdm_led.setMinimumHeight(20)
        pdm_led.setMaximumHeight(40)
        hbl = QHBoxLayout()
        hbl.setSpacing(9)
        hbl.addWidget(btn)
        hbl.addWidget(pdm_led)
        vbl.addItem(hbl)

        vbl.addSpacing(40)
        # ####################################################################
        # ####################### Auto Correction ############################
        # ####################################################################
        rules = (
            '[{"name": "EnblRule", "property": "Enable", ' +
            '"expression": "ch[0] in (1, 3)", "channels": [{"channel": "' +
            self.prefix+'OrbitMode-Sts'+'", "trigger": true}]}]')
        lbl = QLabel('Enable Auto Correction', grp_bx)
        pdm_btn = PyDMStateButton(
            grp_bx, init_channel=self.prefix+'AutoCorr-Sel')
        pdm_btn.rules = rules
        pdm_btn.setMinimumHeight(20)
        pdm_btn.setMaximumHeight(40)
        hbl = QHBoxLayout()
        hbl.addWidget(lbl)
        hbl.addWidget(pdm_btn)
        vbl.addItem(hbl)

        lbl = QLabel('Frequency [Hz]', grp_bx)
        wid = self.create_pair(grp_bx, 'AutoCorrFreq')
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

        lbl = QLabel('Orbit Mode', grp_bx)
        lbl.setMinimumSize(QSize(50, 0))
        wid = self.create_pair_sel(grp_bx, 'OrbitMode')
        fbl.addRow(lbl, wid)

        lbl = QLabel('Correct:', grp_bx)
        lbl.setMinimumSize(QSize(50, 0))
        combo = OfflineOrbControl(
            self, self.prefix, self.ctrls, self.acc)
        combo.rules = (
            '[{"name": "EnblRule", "property": "Enable", ' +
            '"expression": "not ch[0]", "channels": [{"channel": "' +
            self.prefix+'OrbitMode-Sts'+'", "trigger": true}]}]')
        fbl.addRow(lbl, combo)

        lbl = QLabel('as diff to:', grp_bx)
        lbl.setMinimumSize(QSize(50, 0))
        combo = RefControl(self, self.prefix, self.ctrls, self.acc)
        fbl.addRow(lbl, combo)

        vbl.addSpacing(40)
        # ####################################################################
        # ######################## Kicks Configs. ############################
        # ####################################################################
        wid = KicksConfigWidget(grp_bx, self.prefix, False)
        vbl.addWidget(wid)
        vbl.addSpacing(40)
        # ####################################################################
        # ###################### Manual Correction ###########################
        # ####################################################################
        grpbx = QGroupBox('Manual Correction', self)
        hbl = QHBoxLayout(grpbx)
        hbl.setSpacing(9)
        vbl.addWidget(grpbx)

        rules = (
            '[{"name": "EnblRule", "property": "Enable", ' +
            '"expression": "not ch[0]", "channels": [{"channel": "' +
            self.prefix+'AutoCorr-Sts'+'", "trigger": true}]}]')
        pdm_pbtn = PyDMPushButton(
            grpbx, 'Calculate Kicks', pressValue=1,
            init_channel=self.prefix+'CalcCorr-Cmd')
        pdm_pbtn.rules = rules
        rules = (
            '[{"name": "EnblRule", "property": "Enable", ' +
            '"expression": "ch[1] and not ch[0]", ' +
            '"channels": [' +
            '{"channel": "'+self.prefix+'AutoCorr-Sts'+'", "trigger": true},' +
            '{"channel": "'+self.prefix+'OrbitMode-Sel'+'", "trigger": true}' +
            ']}]')
        pdm_pbtn2 = PyDMPushButton(
            grpbx, 'Apply All',
            pressValue=OrbitCorrDev.ApplyCorr.All,
            init_channel=self.prefix+'ApplyCorr-Cmd')
        pdm_pbtn2.rules = rules
        vbl2 = QVBoxLayout()
        vbl2.addWidget(pdm_pbtn)
        vbl2.addWidget(pdm_pbtn2)

        pdm_pbtn = PyDMPushButton(
            grpbx, 'Apply CH',
            pressValue=OrbitCorrDev.ApplyCorr.CH,
            init_channel=self.prefix+'ApplyCorr-Cmd')
        pdm_pbtn.rules = rules
        pdm_pbtn2 = PyDMPushButton(
            grpbx, 'Apply CV',
            pressValue=OrbitCorrDev.ApplyCorr.CV,
            init_channel=self.prefix+'ApplyCorr-Cmd')
        pdm_pbtn2.rules = rules
        pdm_pbtn3 = PyDMPushButton(
            grpbx, 'Apply RF',
            pressValue=OrbitCorrDev.ApplyCorr.RF,
            init_channel=self.prefix+'ApplyCorr-Cmd')
        pdm_pbtn3.rules = rules
        vbl3 = QVBoxLayout()
        vbl3.setSpacing(9)
        vbl3.addWidget(pdm_pbtn)
        vbl3.addWidget(pdm_pbtn2)
        vbl3.addWidget(pdm_pbtn3)
        hbl.addItem(vbl2)
        hbl.addItem(vbl3)

        vbl.addSpacing(40)
        # ####################################################################
        # ###################### Detailed Configurations #####################
        # ####################################################################
        grpbx = QGroupBox('Detailed Configurations', self)
        vbl.addWidget(grpbx)
        vbl2 = QVBoxLayout(grpbx)
        vbl2.setSpacing(9)
        Window = create_window_from_widget(
            RespMatWidget, name='RespMatWindow')
        btn = QPushButton('Response Matrix', grpbx)
        vbl2.addWidget(btn)
        _util.connect_window(
            btn, Window, grpbx, prefix=self.prefix, acc=self.acc)
        Window = create_window_from_widget(
            KicksConfigWidget, name='KicksConfigWindow')
        btn = QPushButton('Correctors', grpbx)
        vbl2.addWidget(btn)
        _util.connect_window(
            btn, Window, grpbx, prefix=self.prefix, show_details=True)
        Window = create_window_from_widget(
            AcqControlWidget, name='AcqControlWindow')
        btn = QPushButton('Orbit Acquisition', grpbx)
        _util.connect_window(
            btn, Window, grpbx, prefix=self.prefix, acc=self.acc)
        vbl2.addWidget(btn)


class RefControl(BaseCombo):
    def __init__(self, parent, prefix, ctrls, acc='SI'):
        setpoint = dict()
        readback = dict()
        setpoint['x'] = SiriusConnectionSignal(prefix+'OrbitRefX-SP')
        setpoint['y'] = SiriusConnectionSignal(prefix+'OrbitRefY-SP')
        readback['x'] = SiriusConnectionSignal(prefix+'OrbitRefX-RB')
        readback['y'] = SiriusConnectionSignal(prefix+'OrbitRefY-RB')
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
        setpoint['x'] = SiriusConnectionSignal(prefix+'OrbitOfflineX-SP')
        setpoint['y'] = SiriusConnectionSignal(prefix+'OrbitOfflineY-SP')
        readback['x'] = SiriusConnectionSignal(prefix+'OrbitOfflineX-RB')
        readback['y'] = SiriusConnectionSignal(prefix+'OrbitOfflineY-RB')
        super().__init__(parent, ctrls, setpoint, readback, acc)


def _main():
    app = SiriusApplication()
    win = SiriusDialog()
    hbl = QHBoxLayout(win)
    prefix = 'ca://' + pref+'SI-Glob:AP-SOFB:'
    pvs = [
        'OrbitSmoothX-Mon', 'OrbitSmoothY-Mon',
        'OrbitOfflineX-RB', 'OrbitOfflineY-RB',
        'OrbitRefX-RB', 'OrbitRefY-RB']
    chans = []
    for pv in pvs:
        chans.append(SiriusConnectionSignal(prefix+pv))
    win._channels = chans
    ctrls = {
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
                'getvalue': chans[5].getvalue}}}
    wid = SOFBControl(win, prefix, ctrls)
    hbl.addWidget(wid)
    win.resize(QSize(200, 1200))
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    from siriuspy.envars import vaca_prefix as pref
    import sys
    _main()
