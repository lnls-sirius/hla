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
from siriushla.as_ap_sofb.ioc_control.base import BaseWidget, BaseCombo, \
    CALabel


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

        main_wid = self.get_main_widget(tabw)
        tabw.addTab(main_wid, 'Main')

        wid = AcqControlWidget(tabw, prefix=self.prefix, acc=self.acc)
        tabw.addTab(wid, 'Orbit')

    def get_main_widget(self, parent):
        """."""
        main_wid = QWidget(parent)
        vbl = QVBoxLayout()
        main_wid.setLayout(vbl)

        orb_wid = self.get_orbit_widget(main_wid)
        corr_wid = self.get_correction_widget(main_wid)
        mat_wid = RespMatWidget(main_wid, self.prefix, self.acc)

        vbl.setContentsMargins(0, 0, 0, 0)
        vbl.addWidget(orb_wid)
        vbl.addStretch()
        vbl.addWidget(corr_wid)
        vbl.addStretch()
        vbl.addWidget(mat_wid)
        return main_wid

    def get_orbit_widget(self, parent):
        """."""
        orb_wid = QGroupBox('Orbit', parent)
        orb_wid.setObjectName('grp')
        orb_wid.setStyleSheet('#grp{min-height: 10em; max-height: 12em;}')
        orb_wid.setLayout(QGridLayout())

        conf = PyDMPushButton(
            orb_wid, init_channel=self.prefix+'TrigAcqConfig-Cmd',
            pressValue=1)
        conf.setToolTip('Refresh Configurations')
        conf.setIcon(qta.icon('fa5s.sync'))
        conf.setObjectName('conf')
        conf.setStyleSheet(
            '#conf{min-width:25px; max-width:25px; icon-size:20px;}')

        sts = QPushButton('', orb_wid)
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
            sts, window, orb_wid, prefix=self.prefix, acc=self.acc,
            is_orb=True)

        pdm_led = SiriusLedAlert(
            orb_wid, init_channel=self.prefix+'OrbStatus-Mon')

        lbl = QLabel('Status:', orb_wid)
        hbl = QHBoxLayout()
        hbl.setSpacing(9)
        hbl.addStretch()
        hbl.addWidget(lbl)
        hbl.addWidget(pdm_led)
        hbl.addWidget(sts)
        hbl.addWidget(conf)
        orb_wid.layout().addItem(hbl, 0, 0, 1, 2)

        lbl = QLabel('SOFB Mode', orb_wid)
        wid = self.create_pair_sel(orb_wid, 'SOFBMode')
        orb_wid.layout().addWidget(lbl, 1, 0, alignment=Qt.AlignVCenter)
        orb_wid.layout().addWidget(wid, 1, 1)

        lbl = CALabel('OfflineOrb:', orb_wid)
        combo = OfflineOrbControl(self, self.prefix, self.ctrls, self.acc)
        rules = (
            '[{"name": "EnblRule", "property": "Visible", ' +
            '"expression": "not ch[0]", "channels": [{"channel": "' +
            self.prefix+'SOFBMode-Sts'+'", "trigger": true}]}]')
        combo.rules = rules
        lbl.rules = rules
        orb_wid.layout().addWidget(lbl, 2, 0, alignment=Qt.AlignVCenter)
        orb_wid.layout().addWidget(combo, 2, 1, alignment=Qt.AlignBottom)

        lbl = QLabel('RefOrb:', orb_wid)
        combo = RefControl(self, self.prefix, self.ctrls, self.acc)
        lbl2 = QLabel('', orb_wid)
        combo.configname.connect(lbl2.setText)
        vbl_ref = QVBoxLayout()
        vbl_ref.addWidget(combo)
        vbl_ref.addWidget(lbl2)
        orb_wid.layout().addWidget(lbl, 3, 0, alignment=Qt.AlignVCenter)
        orb_wid.layout().addLayout(vbl_ref, 3, 1)

        lbl = QLabel('Num. Pts.', orb_wid)
        stp = SiriusSpinbox(orb_wid, init_channel=self.prefix+'SmoothNrPts-SP')
        stp.showStepExponent = False
        rdb = PyDMLabel(orb_wid, init_channel=self.prefix+'SmoothNrPts-RB')
        rdb.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        slsh = QLabel('/', orb_wid, alignment=Qt.AlignCenter)
        slsh.setStyleSheet('min-width:0.7em; max-width:0.7em;')
        cnt = PyDMLabel(orb_wid, init_channel=self.prefix+'BufferCount-Mon')
        cnt.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        cnt.setToolTip('Current Buffer Size')
        rst = PyDMPushButton(
            orb_wid, init_channel=self.prefix+'SmoothReset-Cmd', pressValue=1)
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
        orb_wid.layout().addWidget(lbl, 4, 0, alignment=Qt.AlignVCenter)
        orb_wid.layout().addItem(hbl, 4, 1)
        orb_wid.layout().setColumnStretch(1, 2)
        return orb_wid

    def get_correction_widget(self, parent):
        """."""
        corr_wid = QGroupBox('Correction', parent)
        corr_wid.setLayout(QVBoxLayout())

        lbl = QLabel('Auto Correction State:', corr_wid)
        wid = self.create_pair_butled(corr_wid, 'LoopState')
        hbl = QHBoxLayout()
        hbl.addWidget(lbl)
        hbl.addWidget(wid)
        corr_wid.layout().addLayout(hbl)

        corr_tab = QTabWidget(corr_wid)
        corr_wid.layout().addWidget(corr_tab)

        auto_wid = self.get_auto_correction_widget(corr_tab)
        corr_tab.addTab(auto_wid, 'Automatic')

        man_wid = self.get_manual_correction_widget(corr_tab)
        corr_tab.addTab(man_wid, 'Manual')

        kicks_wid = KicksConfigWidget(parent, self.prefix, self.acc)
        corr_tab.addTab(kicks_wid, 'Kicks Config')

        hbl = kicks_wid.get_status_widget(corr_wid)
        corr_wid.layout().addLayout(hbl)
        return corr_wid

    def get_manual_correction_widget(self, parent):
        """."""
        man_wid = QWidget(parent)
        man_wid.setObjectName('grp')
        gdl = QGridLayout(man_wid)
        gdl.setSpacing(9)

        calc = PyDMPushButton(
            man_wid, '', pressValue=1,
            init_channel=self.prefix+'CalcDelta-Cmd')
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
            self.prefix+'LoopState-Sts'+'", "trigger": true}]}]')
        calc.rules = rules

        exp = 'ch[0] in (1, 2, 3)'
        ch = ''
        if self.isring:
            exp = 'ch[1] in (1, 2, 3) and not ch[0]'
            ch = '{"channel": "' + self.prefix + \
                'LoopState-Sts", "trigger": true},'
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
                man_wid, ' '+itm, pressValue=val,
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
        vlay = QVBoxLayout()
        vlay.addStretch()
        gdl.addLayout(vlay, 2, 0)

        return man_wid

    def get_auto_correction_widget(self, parent):
        """."""
        auto_wid = QWidget(parent)
        vbl2 = QVBoxLayout(auto_wid)

        tabw = QTabWidget(auto_wid)
        vbl2.addWidget(tabw)

        gpbx = QWidget(tabw)
        gpbx_lay = QVBoxLayout(gpbx)
        tabw.addTab(gpbx, 'Main')

        fbl = QFormLayout()
        fbl.setHorizontalSpacing(9)
        gpbx_lay.addLayout(fbl)

        lbl = QLabel('Freq. [Hz]', gpbx)
        wid = self.create_pair(gpbx, 'LoopFreq')
        fbl.addRow(lbl, wid)

        lbl = QLabel('Max. Orb. Distortion', gpbx)
        wid = self.create_pair(gpbx, 'LoopMaxOrbDistortion')
        fbl.addRow(lbl, wid)

        gpbx = QWidget(tabw)
        gpbx_lay = QGridLayout(gpbx)
        gpbx_lay.setSpacing(1)
        tabw.addTab(gpbx, 'PID')

        hbl = QHBoxLayout()
        hbl.addWidget(QLabel('Use PID:'))
        wid = self.create_pair_butled(gpbx, 'LoopUsePID')
        hbl.addWidget(wid)
        hbl.addStretch()
        hbl.addWidget(QLabel('Reset PID ref'))
        wid = PyDMPushButton(
            gpbx, init_channel=self.prefix+'LoopPIDRstRef-Cmd')
        wid.pressValue = 1
        wid.setToolTip('Reset PID reference')
        wid.setIcon(qta.icon('fa5s.sync'))
        hbl.addWidget(wid)
        gpbx_lay.addLayout(hbl, 0, 0, 1, 4 if self.acc == 'SI' else 3)

        gpbx_lay.addWidget(QLabel('CH', gpbx), 2, 0)
        gpbx_lay.addWidget(QLabel('CV', gpbx), 3, 0)
        tmpl = self.prefix + 'LoopPID{:s}{:s}-SP'
        for i, k in enumerate(('Kp', 'Ki', 'Kd'), 1):
            gpbx_lay.addWidget(
                QLabel(k, gpbx), 1, i, alignment=Qt.AlignCenter)
            spbx = SiriusSpinbox(wid, init_channel=tmpl.format(k, 'CH'))
            spbx.showStepExponent = False
            gpbx_lay.addWidget(spbx, 2, i)
            spbx = SiriusSpinbox(wid, init_channel=tmpl.format(k, 'CV'))
            spbx.showStepExponent = False
            gpbx_lay.addWidget(spbx, 3, i)
            if self.acc == 'SI':
                spbx = SiriusSpinbox(wid, init_channel=tmpl.format(k, 'RF'))
                spbx.showStepExponent = False
                gpbx_lay.addWidget(spbx, 4, i)
        if self.acc == 'SI':
            gpbx_lay.addWidget(QLabel('RF', gpbx), 4, 0)

        return auto_wid


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
