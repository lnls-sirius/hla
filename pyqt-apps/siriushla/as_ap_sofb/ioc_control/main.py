"""Define Controllers for the orbits displayed in the graphic."""

import numpy as _np
from qtpy.QtWidgets import QLabel, QGroupBox, QPushButton, QFormLayout, \
    QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QTabWidget
from qtpy.QtCore import Qt
import qtawesome as qta

from pydm.widgets import PyDMPushButton, PyDMLabel

from siriushla.widgets import SiriusConnectionSignal, \
    SiriusLedAlert, SiriusSpinbox
from siriushla.widgets.windows import create_window_from_widget
import siriushla.util as _util

from siriushla.as_ap_sofb.ioc_control.status import StatusWidget
from siriushla.as_ap_sofb.ioc_control.kicks_config import KicksConfigWidget
from siriushla.as_ap_sofb.ioc_control.orbit_acquisition import AcqControlWidget
from siriushla.as_ap_sofb.ioc_control.respmat import RespMatWidget
from siriushla.as_ap_sofb.ioc_control.base import BaseWidget, BaseCombo


class SOFBControl(BaseWidget):
    """."""

    def __init__(self, parent, prefix, ctrls, acc='SI'):
        """."""
        super().__init__(parent, prefix, acc=acc)
        self.ctrls = ctrls
        self.setupui()

    def setupui(self):
        """."""
        vbl = QVBoxLayout(self)
        vbl.setContentsMargins(0, 0, 0, 0)
        tabw = QTabWidget(self)
        vbl.addWidget(tabw)

        mainwid = QWidget(tabw)
        mainwid.setLayout(self.get_mainvbl(mainwid))
        tabw.addTab(mainwid, 'Main')

        wid = AcqControlWidget(tabw, prefix=self.prefix, acc=self.acc)
        tabw.addTab(wid, 'Orbit')

    def get_mainvbl(self, parent):
        """."""
        vbl = QVBoxLayout()
        vbl.setContentsMargins(0, 0, 0, 0)
        vbl.setSpacing(10)

        # ####################################################################
        # ########################## Orbit PVs ###############################
        # ####################################################################
        grpbx = QGroupBox('Orbit', parent)
        grpbx.setObjectName('grp')
        grpbx.setStyleSheet('#grp{min-height: 10em; max-height: 12em;}')
        fbl = QGridLayout(grpbx)
        vbl.addWidget(grpbx)

        conf = PyDMPushButton(
            grpbx, init_channel=self.prefix+'TrigAcqConfig-Cmd', pressValue=1)
        conf.setToolTip('Refresh Configurations')
        conf.setIcon(qta.icon('fa5s.sync'))
        conf.setObjectName('conf')
        conf.setStyleSheet(
            '#conf{min-width:25px; max-width:25px; icon-size:20px;}')

        sts = QPushButton('', grpbx)
        sts.setIcon(qta.icon('fa5s.list-ul'))
        sts.setToolTip('Open Detailed Status View')
        sts.setObjectName('sts')
        sts.setStyleSheet(
            '#sts{min-width:25px; max-width:25px; icon-size:20px;}')
        icon = qta.icon(
            'fa5s.hammer', color=_util.get_appropriate_color(self.acc))
        window = create_window_from_widget(
            StatusWidget, title='Orbit Status', icon=icon)
        _util.connect_window(
            sts, window, grpbx, prefix=self.prefix, acc=self.acc, is_orb=True)

        pdm_led = SiriusLedAlert(
            grpbx, init_channel=self.prefix+'OrbStatus-Mon')

        lbl = QLabel('Status:', grpbx)
        hbl = QHBoxLayout()
        hbl.setSpacing(9)
        hbl.addStretch()
        hbl.addWidget(lbl)
        hbl.addWidget(pdm_led)
        hbl.addWidget(sts)
        hbl.addWidget(conf)
        fbl.addItem(hbl, 0, 0, 1, 2)

        lbl = QLabel('SOFB Mode', grpbx)
        wid = self.create_pair_sel(grpbx, 'SOFBMode')
        fbl.addWidget(lbl, 1, 0, alignment=Qt.AlignVCenter)
        fbl.addWidget(wid, 1, 1)

        lbl = QLabel('OfflineOrb:', grpbx)
        combo = OfflineOrbControl(self, self.prefix, self.ctrls, self.acc)
        combo.rules = (
            '[{"name": "EnblRule", "property": "Enable", ' +
            '"expression": "not ch[0]", "channels": [{"channel": "' +
            self.prefix+'SOFBMode-Sts'+'", "trigger": true}]}]')
        fbl.addWidget(lbl, 2, 0, alignment=Qt.AlignVCenter)
        fbl.addWidget(combo, 2, 1, alignment=Qt.AlignBottom)

        lbl = QLabel('RefOrb:', grpbx)
        combo = RefControl(self, self.prefix, self.ctrls, self.acc)
        lbl2 = QLabel('', grpbx)
        combo.configname.connect(lbl2.setText)
        vbl_ref = QVBoxLayout()
        vbl_ref.addWidget(combo)
        vbl_ref.addWidget(lbl2)
        fbl.addWidget(lbl, 3, 0, alignment=Qt.AlignVCenter)
        fbl.addLayout(vbl_ref, 3, 1)

        lbl = QLabel('Num. Pts.', grpbx)
        stp = SiriusSpinbox(grpbx, init_channel=self.prefix+'SmoothNrPts-SP')
        stp.showStepExponent = False
        rdb = PyDMLabel(grpbx, init_channel=self.prefix+'SmoothNrPts-RB')
        rdb.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        slsh = QLabel('/', grpbx, alignment=Qt.AlignCenter)
        slsh.setStyleSheet('min-width:0.7em; max-width:0.7em;')
        cnt = PyDMLabel(grpbx, init_channel=self.prefix+'BufferCount-Mon')
        cnt.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        cnt.setToolTip('Current Buffer Size')
        rst = PyDMPushButton(
            grpbx, init_channel=self.prefix+'SmoothReset-Cmd', pressValue=1)
        rst.setToolTip('Reset Buffer')
        rst.setIcon(qta.icon('mdi.delete-empty'))
        rst.setObjectName('rst')
        rst.setStyleSheet(
            '#rst{min-width:25px; max-width:25px; icon-size:20px;}')
        hbl = QHBoxLayout()
        hbl.addWidget(stp)
        hbl.addWidget(cnt)
        hbl.addWidget(slsh)
        hbl.addWidget(rdb)
        hbl.addWidget(rst)
        fbl.addWidget(lbl, 4, 0, alignment=Qt.AlignVCenter)
        fbl.addItem(hbl, 4, 1)
        fbl.setColumnStretch(1, 2)

        # ####################################################################
        # ######################## Kicks Configs. ############################
        # ####################################################################
        wid = KicksConfigWidget(parent, self.prefix, self.acc)
        wid.layout().setContentsMargins(0, 0, 0, 0)
        vbl.addWidget(wid)

        # ####################################################################
        # ###################### Manual Correction ###########################
        # ####################################################################
        grpbx = QGroupBox('Manual Correction', parent)
        grpbx.setObjectName('grp')
        grpbx.setStyleSheet('#grp{min-height: 70px; max-height: 70px;}')
        gdl = QGridLayout(grpbx)
        gdl.setSpacing(9)
        vbl.addWidget(grpbx)

        calc = PyDMPushButton(
            grpbx, '', pressValue=1, init_channel=self.prefix+'CalcDelta-Cmd')
        calc.setIcon(qta.icon('mdi.calculator-variant'))
        calc.setToolTip('Calculate Kicks')
        calc.setObjectName('button')
        calc.setStyleSheet('#button {\
            min-height: 45px; min-width: 45px;\
            max-height: 45px; max-width: 45px;\
            icon-size: 40px;}')
        rules = (
            '[{"name": "EnblRule", "property": "Enable", ' +
            '"expression": "not ch[0]", "channels": [{"channel": "' +
            self.prefix+'ClosedLoop-Sts'+'", "trigger": true}]}]')
        calc.rules = rules

        exp = 'ch[0] in (1, 2, 3)'
        ch = ''
        if self.isring:
            exp = 'ch[1] in (1, 2, 3) and not ch[0]'
            ch = '{"channel": "' + self.prefix + \
                'ClosedLoop-Sts", "trigger": true},'
        rules = (
            '[{"name": "EnblRule", "property": "Enable", ' +
            '"expression": "'+exp+'", "channels": ['+ch +
            '{"channel": "'+self.prefix+'SOFBMode-Sts", "trigger": true}]}]')

        lst = [
            ('All', self._csorb.ApplyDelta.All),
            ('CH', self._csorb.ApplyDelta.CH),
            ('CV', self._csorb.ApplyDelta.CV)]
        if self.acc == 'SI':
            lst.append(('RF', self._csorb.ApplyDelta.RF))
        btns = dict()
        for itm, val in lst:
            btn = PyDMPushButton(
                grpbx, ' '+itm, pressValue=val,
                init_channel=self.prefix+'ApplyDelta-Cmd')
            btn.rules = rules
            btn.setIcon(qta.icon('fa5s.hammer'))
            btn.setToolTip('Apply ' + itm)
            btn.setObjectName('button')
            btn.setStyleSheet('#button {\
                min-height: 25px; min-width: 45px;\
                max-height: 25px;\
                icon-size: 20px;}')
            btns[itm] = btn

        gdl.addWidget(calc, 0, 0, 2, 1)
        gdl.addWidget(btns['CH'], 0, 1)
        gdl.addWidget(btns['CV'], 0, 2)
        if self.acc == 'SI':
            gdl.addWidget(btns['RF'], 0, 3)
            gdl.addWidget(btns['All'], 1, 1, 1, 3)
        else:
            gdl.addWidget(btns['All'], 1, 1, 1, 2)
        gdl.setColumnMinimumWidth(0, 60)

        # ####################################################################
        # ####################### Auto Correction ############################
        # ####################################################################
        grpbx = QGroupBox('Auto Correction', parent)
        grpbx.setObjectName('grp')
        grpbx.setStyleSheet('#grp{min-height: 5em; max-height: 5em;}')
        vbl2 = QVBoxLayout(grpbx)
        vbl.addWidget(grpbx)

        lbl = QLabel('State', grpbx)
        wid = self.create_pair_butled(grpbx, 'ClosedLoop')
        hbl = QHBoxLayout()
        hbl.addWidget(lbl)
        hbl.addWidget(wid)
        vbl2.addItem(hbl)

        lbl = QLabel('Freq. [Hz]', grpbx)
        wid = self.create_pair(grpbx, 'ClosedLoopFreq')
        fbl = QFormLayout()
        fbl.setHorizontalSpacing(9)
        fbl.addRow(lbl, wid)
        vbl2.addItem(fbl)

        # ####################################################################
        # ###################### Response Matrix #####################
        # ####################################################################
        wid = RespMatWidget(parent, self.prefix, self.acc)
        wid.layout().setContentsMargins(0, 0, 0, 0)
        vbl.addWidget(wid)

        return vbl


class RefControl(BaseCombo):
    """."""

    def __init__(self, parent, prefix, ctrls, acc='SI'):
        """."""
        setpoint = dict()
        readback = dict()
        setpoint['x'] = SiriusConnectionSignal(prefix+'RefOrbX-SP')
        setpoint['y'] = SiriusConnectionSignal(prefix+'RefOrbY-SP')
        readback['x'] = SiriusConnectionSignal(prefix+'RefOrbX-RB')
        readback['y'] = SiriusConnectionSignal(prefix+'RefOrbY-RB')
        super().__init__(parent, ctrls, setpoint, readback, acc)

    def _selection_changed(self, text):
        sigs = dict()
        if text.lower().startswith('bba_orb'):
            data = self._client.get_config_value('bba_orb')
            for pln in ('x', 'y'):
                self.orbits[pln] = _np.array(data[pln])
                self.setpoint[pln].send_value_signal[_np.ndarray].emit(
                    self.orbits[pln])
        elif text.lower().startswith('ref_orb'):
            data = self._client.get_config_value('ref_orb')
            for pln in ('x', 'y'):
                self.orbits[pln] = _np.array(data[pln])
                self.setpoint[pln].send_value_signal[_np.ndarray].emit(
                    self.orbits[pln])
        super()._selection_changed(text, sigs)

    def setup_ui(self):
        """."""
        if self.acc == 'SI':
            super().setup_ui(['bba_orb', 'ref_orb'])
        else:
            super().setup_ui()


class OfflineOrbControl(BaseCombo):
    """."""

    def __init__(self, parent, prefix, ctrls, acc='SI'):
        """."""
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
    from siriuspy.envars import VACA_PREFIX as pref
    import sys
    _main()
