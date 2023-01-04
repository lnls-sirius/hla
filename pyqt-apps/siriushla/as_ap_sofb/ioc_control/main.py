"""Define Controllers for the orbits displayed in the graphic."""

import numpy as _np
from qtpy.QtWidgets import QLabel, QGroupBox, QPushButton, QFormLayout, \
    QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QTabWidget, QSpacerItem
from qtpy.QtCore import Qt
import qtawesome as qta

from pydm.widgets import PyDMPushButton

from siriuspy.namesys import SiriusPVName as _PVName

from ...widgets import SiriusConnectionSignal as _ConnSig, SiriusLabel, \
    SiriusLedAlert, SiriusSpinbox, PyDMStateButton, SiriusLedState
from ...widgets.windows import create_window_from_widget
from ... import util as _util

from .status import StatusWidget
from .kicks_config import KicksConfigWidget
from .orbit_acquisition import AcqControlWidget
from .respmat import RespMatWidget
from .base import BaseWidget, BaseCombo, CALabel


class SOFBControl(BaseWidget):
    """."""

    def __init__(self, parent, device, ctrls, prefix='', acc='SI'):
        """."""
        super().__init__(parent, device, prefix=prefix, acc=acc)
        self.ctrls = ctrls
        self.setupui()

    def setupui(self):
        """."""
        vbl = QVBoxLayout(self)
        tabw = QTabWidget(self)
        tabw.setObjectName(self.acc+'Tab')
        vbl.addWidget(tabw)

        main_wid = self.get_main_widget(tabw)
        tabw.addTab(main_wid, 'Main')

        wid = AcqControlWidget(
            tabw, self.device, prefix=self.prefix, acc=self.acc)
        tabw.addTab(wid, 'Trig. Acq. Control')

    def get_main_widget(self, parent):
        """."""
        main_wid = QWidget(parent)
        vbl = QVBoxLayout()
        main_wid.setLayout(vbl)

        tabw = QTabWidget(main_wid)
        tabw.setObjectName(self.acc+'Tab')
        orb_wid = self.get_orbit_widget(tabw)
        acqrt_wid = self.get_orbitdetails_widget(tabw)
        tabw.addTab(orb_wid, 'Orbit')
        tabw.addTab(acqrt_wid, 'Details')
        tabw.setStyleSheet("""
            #{0}Tab::pane {{
                border-left: 2px solid gray;
                border-bottom: 2px solid gray;
                border-right: 2px solid gray;
            }}
        """.format(self.acc))

        corr_wid = self.get_correction_widget(main_wid)
        mat_wid = RespMatWidget(main_wid, self.device, self.prefix, self.acc)

        vbl.addWidget(tabw)
        vbl.addStretch()
        vbl.addWidget(corr_wid)
        vbl.addStretch()
        vbl.addWidget(mat_wid)
        return main_wid

    def get_orbit_widget(self, parent):
        """."""
        orb_wid = QWidget(parent)
        orb_wid.setObjectName('grp')
        orb_wid.setStyleSheet('#grp{min-height: 11em; max-height: 15em;}')
        orb_wid.setLayout(QGridLayout())

        conf = PyDMPushButton(
            orb_wid, pressValue=1,
            init_channel=self.devpref.substitute(propty='TrigAcqConfig-Cmd'))
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
            sts, window, orb_wid, device=self.device,
            prefix=self.prefix, acc=self.acc, is_orb=True)

        pdm_led = SiriusLedAlert(
            orb_wid, self.devpref.substitute(propty='OrbStatus-Mon'))

        lbl = QLabel('Status:', orb_wid)
        hbl = QHBoxLayout()
        hbl.setSpacing(9)
        hbl.addStretch()
        hbl.addWidget(lbl)
        hbl.addWidget(pdm_led)
        hbl.addWidget(sts)
        hbl.addWidget(conf)
        orb_wid.layout().addLayout(hbl, 0, 0, 1, 2)

        lbl = QLabel('SOFB Mode', orb_wid)
        wid = self.create_pair_sel(orb_wid, 'SOFBMode')
        orb_wid.layout().addWidget(lbl, 1, 0, alignment=Qt.AlignVCenter)
        orb_wid.layout().addWidget(wid, 1, 1)

        lbl = QLabel('RefOrb:', orb_wid)
        combo = RefControl(
            self, self.device, self.ctrls, prefix=self.prefix, acc=self.acc)
        lbl2 = QLabel('', orb_wid)
        combo.configname.connect(lbl2.setText)
        vbl_ref = QVBoxLayout()
        vbl_ref.addWidget(combo)
        vbl_ref.addWidget(lbl2)
        orb_wid.layout().addWidget(lbl, 3, 0, alignment=Qt.AlignVCenter)
        orb_wid.layout().addLayout(vbl_ref, 3, 1)

        lbl = QLabel('Num. Pts.', orb_wid)
        stp = SiriusSpinbox(
            orb_wid, self.devpref.substitute(propty='SmoothNrPts-SP'))
        rdb = SiriusLabel(
            orb_wid, self.devpref.substitute(propty='SmoothNrPts-RB'))
        rdb.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        slsh = QLabel('/', orb_wid, alignment=Qt.AlignCenter)
        slsh.setStyleSheet('min-width:0.7em; max-width:0.7em;')
        cnt = SiriusLabel(
            orb_wid, self.devpref.substitute(propty='BufferCount-Mon'))
        cnt.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        cnt.setToolTip('Current Buffer Size')
        rst = PyDMPushButton(
            orb_wid, pressValue=1,
            init_channel=self.devpref.substitute(propty='SmoothReset-Cmd'))
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
        orb_wid.layout().addLayout(hbl, 4, 1)

        orb_wid.layout().setColumnStretch(1, 2)
        return orb_wid

    def get_orbitdetails_widget(self, parent):
        """."""
        grp_bx = QWidget(parent)
        grp_bx.setLayout(QVBoxLayout())

        lbl = CALabel('OfflineOrb:', grp_bx)
        combo = OfflineOrbControl(
            grp_bx, self.device, self.ctrls, prefix=self.prefix, acc=self.acc)
        rules = (
            '[{"name": "EnblRule", "property": "Visible", ' +
            '"expression": "not ch[0]", "channels": [{"channel": "' +
            self.devpref.substitute(propty='SOFBMode-Sts') +
            '", "trigger": true}]}]')
        combo.rules = rules
        lbl.rules = rules
        fbl = QFormLayout()
        grp_bx.layout().addLayout(fbl)
        fbl.addRow(lbl, combo)
        grp_bx.layout().addStretch()

        hbl = QHBoxLayout()
        grp_bx.layout().addLayout(hbl)
        fbl = QFormLayout()
        hbl.addLayout(fbl)
        lbl = QLabel('Orbit [Hz]', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'OrbAcqRate')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Kicks [Hz]', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'KickAcqRate')
        fbl.addRow(lbl, wid)

        wid = QWidget(grp_bx)
        wid.setStyleSheet('max-width:6em;')
        hbl.addWidget(wid)
        vbl = QVBoxLayout(wid)
        vbl.setContentsMargins(0, 0, 0, 0)
        lab = QLabel('Sync. Injection', wid, alignment=Qt.AlignCenter)
        vbl.addWidget(lab)
        hbl = QHBoxLayout()
        hbl.setContentsMargins(0, 0, 0, 0)
        vbl.addLayout(hbl)
        spt = PyDMStateButton(
            wid, self.devpref.substitute(propty='SyncWithInjection-Sel'))
        rdb = SiriusLedState(
            wid, self.devpref.substitute(propty='SyncWithInjection-Sts'))
        hbl.addWidget(spt)
        hbl.addWidget(rdb)
        grp_bx.layout().addStretch()

        fbl = QFormLayout()
        grp_bx.layout().addLayout(fbl)
        lbl = QLabel('Smooth Method', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair_sel(grp_bx, 'SmoothMethod')
        fbl.addRow(lbl, wid)
        if self.isring:
            lbl = QLabel('Extend Ring', grp_bx, alignment=Qt.AlignCenter)
            wid = self.create_pair(grp_bx, 'RingSize')
            fbl.addRow(lbl, wid)

        return grp_bx

    def get_correction_widget(self, parent):
        """."""
        corr_wid = QGroupBox('Correction', parent)
        lay = QVBoxLayout(corr_wid)
        lay.setContentsMargins(0, 0, 0, 0)

        if self.acc != 'BO':
            lbl = QLabel('Auto Correction State:', corr_wid)
            wid = self.create_pair_butled(corr_wid, 'LoopState')
            hbl = QHBoxLayout()
            hbl.setContentsMargins(6, 6, 6, 0)
            hbl.addWidget(lbl)
            hbl.addWidget(wid)
            lay.addLayout(hbl)

        corr_tab = QTabWidget(corr_wid)
        corr_tab.setObjectName(self.acc+'Tab')
        lay.addWidget(corr_tab)

        if self.acc != 'BO':
            auto_wid = self.get_auto_correction_widget(corr_tab)
            corr_tab.addTab(auto_wid, 'Loop')

        man_wid = self.get_manual_correction_widget(corr_tab)
        corr_tab.addTab(man_wid, 'Manual')

        kicks_wid = KicksConfigWidget(
            parent, self.device, prefix=self.prefix, acc=self.acc)
        corr_tab.addTab(kicks_wid, 'Kicks')

        if self.acc == 'SI':
            fofb_wid = self.get_fofb_widget(corr_tab)
            corr_tab.addTab(fofb_wid, 'FOFB')

        if self.acc != 'BO':
            hbl = kicks_wid.get_status_widget(corr_wid)
            hbl.setContentsMargins(6, 0, 6, 6)
            lay.addLayout(hbl)
        return corr_wid

    def get_fofb_widget(self, parent):
        """."""
        wid = QWidget(parent)
        wid.setObjectName('grp')
        gdl = QGridLayout(wid)
        gdl.setAlignment(Qt.AlignTop)

        headers = [
            'Description', 'Setpoint', 'Status', 'Monitor', '%']
        for col, text in enumerate(headers):
            lbl = QLabel(text, wid, alignment=Qt.AlignHCenter)
            lbl.setStyleSheet('QLabel{max-height: 1.2em;}')
            gdl.addWidget(lbl, 0, col)

        props = [
            'FOFBDownloadKicks', 'FOFBUpdateRefOrb',
            'FOFBNullSpaceProj', 'FOFBZeroDistortionAtBPMs']
        desc = [
            'Download Kicks', 'Update RefOrb',
            'Project in Kernel', 'Zero Distortion']
        vislist = list()
        for i, (prop, des) in enumerate(zip(props, desc)):
            lbl = QLabel(des, wid)
            spt = PyDMStateButton(
                wid, self.devpref.substitute(propty=prop+'-Sel'))
            rdb = SiriusLedState(
                wid, self.devpref.substitute(propty=prop+'-Sts'))
            mon = SiriusLedState(
                wid, self.devpref.substitute(propty=prop+'-Mon'))
            wids = [lbl, spt, rdb, mon]
            gdl.addWidget(lbl, i+1, 0)
            gdl.addWidget(spt, i+1, 1)
            gdl.addWidget(rdb, i+1, 2)
            gdl.addWidget(mon, i+1, 3)
            if prop in ['FOFBDownloadKicks', 'FOFBUpdateRefOrb']:
                sbp = SiriusSpinbox(
                    wid, self.devpref.substitute(propty=prop+'Perc-SP'))
                rbp = SiriusLabel(
                    wid, self.devpref.substitute(propty=prop+'Perc-RB'))
                rbp.showUnits = False
                gdl2 = QGridLayout()
                gdl2.setContentsMargins(0, 0, 0, 0)
                gdl2.addWidget(sbp, 0, 0)
                gdl2.addWidget(rbp, 1, 0)
                gdl.addLayout(gdl2, i+1, 4)
                wids.extend([sbp, rbp])
            if prop != 'FOFBDownloadKicks':
                vislist.extend(wids)
                for w in wids:
                    w.setVisible(False)

        btmore = QPushButton(qta.icon('fa5s.angle-down'), '', self)
        btmore.setToolTip('Show advanced SOFB <-> FOFB interaction options')
        btmore.setStyleSheet(
            'QPushButton{max-height:0.8em; max-width:1.6em;}')
        btmore.clicked.connect(self._handle_fofb_options_vis)
        btmore.visItems = vislist
        btmore.setFlat(True)
        gdl.addWidget(btmore, 5, 0, alignment=Qt.AlignLeft)

        return wid

    def get_manual_correction_widget(self, parent):
        """."""
        man_wid = QWidget(parent)
        man_wid.setObjectName('grp')
        gdl = QGridLayout(man_wid)
        gdl.setSpacing(9)

        calc = PyDMPushButton(
            man_wid, '', pressValue=1,
            init_channel=self.devpref.substitute(propty='CalcDelta-Cmd'))
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
            self.devpref.substitute(propty='LoopState-Sts') +
            '", "trigger": true}]}]')
        calc.rules = rules

        if self.acc == 'BO':
            gdl.addWidget(calc, 1, 1)
            gdl.setColumnStretch(0, 2)
            gdl.setColumnStretch(2, 2)
            gdl.setRowStretch(0, 2)
            gdl.setRowStretch(2, 2)
            return man_wid

        exp = 'ch[0] in (1, 2, 3)'
        ch = ''
        if self.isring:
            exp = 'ch[1] in (1, 2, 3) and not ch[0]'
            ch = '{"channel": "' + self.devpref.substitute(
                 propty='LoopState-Sts') + '", "trigger": true},'
        rules = (
            '[{"name": "EnblRule", "property": "Enable", ' +
            '"expression": "'+exp+'", "channels": ['+ch +
            '{"channel": "'+self.devpref.substitute(propty='SOFBMode-Sts') +
            '", "trigger": true}]}]')

        lst = [
            ('All', self._csorb.ApplyDelta.All),
            ('CH', self._csorb.ApplyDelta.CH),
            ('CV', self._csorb.ApplyDelta.CV)]
        if self.acc in {'SI', 'BO'}:
            lst.append(('RF', self._csorb.ApplyDelta.RF))
        btns = dict()
        for itm, val in lst:
            btn = PyDMPushButton(
                man_wid, ' '+itm, pressValue=val,
                init_channel=self.devpref.substitute(propty='ApplyDelta-Cmd'))
            btn.rules = rules
            btn.setIcon(qta.icon('fa5s.hammer'))
            btn.setToolTip('Apply ' + itm)
            btn.setObjectName('button')
            btn.setStyleSheet('#button {\
                min-height: 25px; min-width: 45px;\
                max-height: 25px;\
                icon-size: 20px;}')
            if self.acc == 'BO':
                btn.setVisible(False)
            btns[itm] = btn

        gdl.addWidget(calc, 0, 0, 2, 1)
        gdl.addWidget(btns['CH'], 0, 1)
        gdl.addWidget(btns['CV'], 0, 2)
        if self.acc in {'SI', 'BO'}:
            gdl.addWidget(btns['RF'], 0, 3)
            gdl.addWidget(btns['All'], 1, 1, 1, 3)
        else:
            gdl.addWidget(btns['All'], 1, 1, 1, 2)
        gdl.setColumnMinimumWidth(0, 60)

        grpbx = QWidget(man_wid)
        grpbx.setObjectName('gbx')
        if self.acc in {'SI', 'BO'}:
            planes = ('CH', 'CV', 'RF')
            gdl.addWidget(grpbx, 2, 0, 1, 4)
        else:
            planes = ('CH', 'CV')
            gdl.addWidget(grpbx, 2, 0, 1, 3)
        fbl = QFormLayout(grpbx)
        for pln in planes:
            lbl = QLabel(pln+' [%] ', grpbx)
            lbl.setObjectName('lbl')
            lbl.setStyleSheet('#lbl{min-height:1em;}')
            wid = self.create_pair(grpbx, 'ManCorrGain'+pln)
            wid.setObjectName('wid')
            wid.setStyleSheet('#wid{min-height:1.2em;}')
            if self.acc == 'BO':
                lbl.setVisible(False)
                wid.setVisible(False)
            fbl.addRow(lbl, wid)

        vlay = QVBoxLayout()
        vlay.addStretch()
        gdl.addLayout(vlay, 3, 0)
        return man_wid

    def get_auto_correction_widget(self, parent):
        """."""
        auto_wid = QWidget(parent)
        vbl2 = QVBoxLayout(auto_wid)

        tabw = QTabWidget(auto_wid)
        tabw.setObjectName(self.acc+'Tab')
        tabw.setStyleSheet("""
            #{0}Tab::pane {{
                border-left: 2px solid gray;
                border-bottom: 2px solid gray;
                border-right: 2px solid gray;
            }}""".format(self.acc))
        vbl2.addWidget(tabw)

        # Add Main Tab
        gpbx = QWidget(tabw)
        gpbx_lay = QVBoxLayout(gpbx)
        tabw.addTab(gpbx, 'Main')

        fbl = QFormLayout()
        fbl.setHorizontalSpacing(9)
        gpbx_lay.addLayout(fbl)

        lbl = QLabel('Freq. [Hz]', gpbx)
        wid = self.create_pair(gpbx, 'LoopFreq')
        fbl.addRow(lbl, wid)

        lbl = QLabel('Max. Orb. Distortion [um]', gpbx)
        wid = self.create_pair(gpbx, 'LoopMaxOrbDistortion')
        fbl.addRow(lbl, wid)

        wid = QWidget(gpbx)
        wid.setLayout(QHBoxLayout())
        pbtn = QPushButton('Loop Performance', wid)
        pbtn.setIcon(qta.icon('mdi.poll'))
        wid.layout().addStretch()
        wid.layout().addWidget(pbtn)
        icon = qta.icon(
            'fa5s.hammer', color=_util.get_appropriate_color(self.acc))
        wind = create_window_from_widget(
            PerformanceWidget, title='Loop Performance', icon=icon)
        _util.connect_window(
            pbtn, wind, self, device=self.device, prefix=self.prefix)
        fbl.addRow(wid)

        # Add PID Tab
        gpbx = QWidget(tabw)
        gpbx_lay = QGridLayout(gpbx)
        gpbx_lay.setSpacing(1)
        tabw.addTab(gpbx, 'PID')

        gpbx_lay.addWidget(QLabel('CH', gpbx), 1, 0)
        gpbx_lay.addWidget(QLabel('CV', gpbx), 2, 0)
        tmpl = 'LoopPID{:s}{:s}'
        pairs = []
        for i, k in enumerate(('Kp', 'Ki', 'Kd'), 1):
            gpbx_lay.addWidget(
                QLabel(k, gpbx), 0, i, alignment=Qt.AlignCenter)
            pair = self.create_pair(wid, tmpl.format(k, 'CH'), is_vert=True)
            pairs.append(pair)
            gpbx_lay.addWidget(pair, 1, i)
            pair = self.create_pair(wid, tmpl.format(k, 'CV'), is_vert=True)
            pairs.append(pair)
            gpbx_lay.addWidget(pair, 2, i)
            if self.acc in {'SI', 'BO'}:
                pair = self.create_pair(
                    wid, tmpl.format(k, 'RF'), is_vert=True)
                pairs.append(pair)
                gpbx_lay.addWidget(pair, 3, i)
        if self.acc in {'SI', 'BO'}:
            gpbx_lay.addWidget(QLabel('RF', gpbx), 3, 0)

        pbc = QPushButton('SP')
        pbc.setStyleSheet('max-width:2.2em;')
        gpbx_lay.addWidget(pbc, 0, 0)
        pbc.setCheckable(True)
        pbc.setChecked(False)
        pbc.toggled.connect(
            lambda x: pbc.setText('RB' if x else 'SP'))
        for pair in pairs:
            pair.rb_wid.setVisible(False)
            pbc.toggled.connect(pair.rb_wid.setVisible)
            pbc.toggled.connect(pair.sp_wid.setHidden)
        gpbx_lay.setRowStretch(4, 2)
        return auto_wid

    def _handle_fofb_options_vis(self):
        btn = self.sender()
        tooltip = btn.toolTip()
        vis = 'Hide' in tooltip
        if vis:
            tooltip = tooltip.replace('Hide', 'Show')
        else:
            tooltip = tooltip.replace('Show', 'Hide')
        iconname = 'fa5s.angle-down' if vis else 'fa5s.angle-up'
        btn.setIcon(qta.icon(iconname))
        btn.setToolTip(tooltip)
        for item in btn.visItems:
            item.setVisible(not vis)
        self.adjustSize()


class RefControl(BaseCombo):
    """."""

    def __init__(self, parent, device, ctrls, prefix='', acc='SI'):
        """."""
        setpoint = dict()
        readback = dict()
        basename = _PVName(device).substitute(prefix=prefix)
        setpoint['x'] = _ConnSig(basename.substitute(propty='RefOrbX-SP'))
        setpoint['y'] = _ConnSig(basename.substitute(propty='RefOrbY-SP'))
        readback['x'] = _ConnSig(basename.substitute(propty='RefOrbX-RB'))
        readback['y'] = _ConnSig(basename.substitute(propty='RefOrbY-RB'))
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

    def __init__(self, parent, device, ctrls, prefix='', acc='SI'):
        """."""
        setpoint = dict()
        readback = dict()
        basename = _PVName(device).substitute(prefix=prefix)
        setpoint['x'] = _ConnSig(basename.substitute(propty='OfflineOrbX-SP'))
        setpoint['y'] = _ConnSig(basename.substitute(propty='OfflineOrbY-SP'))
        readback['x'] = _ConnSig(basename.substitute(propty='OfflineOrbX-RB'))
        readback['y'] = _ConnSig(basename.substitute(propty='OfflineOrbY-RB'))
        super().__init__(parent, ctrls, setpoint, readback, acc)


class PerformanceWidget(QWidget):
    """."""

    def __init__(self, parent, device, prefix=''):
        """."""
        super().__init__(parent)
        self.prefix = prefix
        self.device = _PVName(device)
        self.setObjectName(self.device.sec+'App')
        self._setupui()

    def _setupui(self):
        def lamb(x):
            return self.device.substitute(prefix=self.prefix, propty=x)

        lbl_main = QLabel(
            '<h3>Loop Performance</h3>', self, alignment=Qt.AlignCenter)

        lbl_prnt = QLabel('Number of Iter. Between Updates', self)
        lbl_rate = QLabel('Effective Rate', self)
        slsh = QLabel('/', self, alignment=Qt.AlignCenter)
        slsh.setStyleSheet('min-width:0.7em; max-width:0.7em;')

        spb = SiriusSpinbox(self, lamb('LoopPrintEveryNumIters-SP'))
        ldrb = SiriusLabel(self, lamb('LoopPrintEveryNumIters-RB'))
        ldmon = SiriusLabel(self, lamb('LoopNumIters-Mon'))
        ld_rate = SiriusLabel(self, lamb('LoopEffectiveRate-Mon'))
        ld_rate.showUnits = True

        lay_niter = QGridLayout()
        lay_niter.addWidget(lbl_prnt, 0, 0, 1, 4, alignment=Qt.AlignCenter)
        lay_niter.addWidget(spb, 1, 0)
        lay_niter.addWidget(ldrb, 1, 1)
        lay_niter.addWidget(slsh, 1, 2)
        lay_niter.addWidget(ldmon, 1, 3)
        lay_niter.setColumnStretch(4, 3)
        lay_niter.addWidget(lbl_rate, 0, 5, alignment=Qt.AlignCenter)
        lay_niter.addWidget(ld_rate, 1, 5)

        lbl_iters = QLabel('Iterations [%]:', self)
        lbl_ok = QLabel('OK', self, alignment=Qt.AlignCenter)
        lbl_tout = QLabel('Timeout', self, alignment=Qt.AlignCenter)
        lbl_diff = QLabel('Diff', self, alignment=Qt.AlignCenter)
        ld_ok = SiriusLabel(self, lamb('LoopPerfItersOk-Mon'))
        ld_tout = SiriusLabel(self, lamb('LoopPerfItersTOut-Mon'))
        ld_diff = SiriusLabel(self, lamb('LoopPerfItersDiff-Mon'))
        lay_iters = QGridLayout()
        lay_iters.addWidget(lbl_iters, 1, 0)
        lay_iters.addWidget(lbl_ok, 0, 1)
        lay_iters.addWidget(lbl_tout, 0, 2)
        lay_iters.addWidget(lbl_diff, 0, 3)
        lay_iters.addWidget(ld_ok, 1, 1, alignment=Qt.AlignCenter)
        lay_iters.addWidget(ld_tout, 1, 2, alignment=Qt.AlignCenter)
        lay_iters.addWidget(ld_diff, 1, 3, alignment=Qt.AlignCenter)

        lbl_psd = QLabel('# of PSs with Diffs:', self)
        lbl_avg = QLabel('AVG', self, alignment=Qt.AlignCenter)
        lbl_std = QLabel('STD', self, alignment=Qt.AlignCenter)
        lbl_max = QLabel('MAX', self, alignment=Qt.AlignCenter)
        ld_avg = SiriusLabel(self, lamb('LoopPerfDiffNrPSAvg-Mon'))
        ld_std = SiriusLabel(self, lamb('LoopPerfDiffNrPSStd-Mon'))
        ld_max = SiriusLabel(self, lamb('LoopPerfDiffNrPSMax-Mon'))
        lay_psd = QGridLayout()
        lay_psd.addWidget(lbl_psd, 1, 0)
        lay_psd.addWidget(lbl_avg, 0, 1)
        lay_psd.addWidget(lbl_std, 0, 2)
        lay_psd.addWidget(lbl_max, 0, 3)
        lay_psd.addWidget(ld_avg, 1, 1, alignment=Qt.AlignCenter)
        lay_psd.addWidget(ld_std, 1, 2, alignment=Qt.AlignCenter)
        lay_psd.addWidget(ld_max, 1, 3, alignment=Qt.AlignCenter)

        lbl_tim = QLabel('Duration Statistics', self, alignment=Qt.AlignCenter)
        lbl_unt = QLabel('[ms]', self, alignment=Qt.AlignCenter)
        lbl_avg = QLabel('AVG', self, alignment=Qt.AlignCenter)
        lbl_std = QLabel('STD', self, alignment=Qt.AlignCenter)
        lbl_min = QLabel('MIN', self, alignment=Qt.AlignCenter)
        lbl_max = QLabel('MAX', self, alignment=Qt.AlignCenter)
        lbl_avg.setStyleSheet('min-width: 5em;')
        lbl_std.setStyleSheet('min-width: 5em;')
        lbl_min.setStyleSheet('min-width: 5em;')
        lbl_max.setStyleSheet('min-width: 5em;')
        lay_tim = QGridLayout()
        lay_tim.addWidget(lbl_tim, 0, 0, 1, 5)
        lay_tim.addWidget(lbl_unt, 1, 0)
        lay_tim.addWidget(lbl_avg, 1, 1)
        lay_tim.addWidget(lbl_std, 1, 2)
        lay_tim.addWidget(lbl_min, 1, 3)
        lay_tim.addWidget(lbl_max, 1, 4)

        labs = [
            'Get Orbit', 'Get Kick', 'Calculate', 'Process', 'Apply', 'Total']
        nms = ['GetO', 'GetK', 'Calc', 'Proc', 'App', 'Tot']
        for i, (nm, lab) in enumerate(zip(nms, labs)):
            lbl = QLabel(lab, self)
            lay_tim.addWidget(lbl, i+2, 0)
            for j, ld in enumerate(['Avg', 'Std', 'Min', 'Max']):
                ld_ = SiriusLabel(
                    self, lamb(f'LoopPerfTim{nm:s}{ld:s}-Mon'))
                lay_tim.addWidget(ld_, i+2, j+1, alignment=Qt.AlignCenter)

        lay = QGridLayout(self)
        lay.addLayout(lay_niter, 0, 0)
        lay.addItem(QSpacerItem(1, 20), 1, 0)
        lay.addWidget(lbl_main, 2, 0)
        lay.addItem(QSpacerItem(1, 20), 3, 0)
        lay.addLayout(lay_iters, 4, 0)
        lay.addItem(QSpacerItem(1, 20), 5, 0)
        lay.addLayout(lay_psd, 6, 0)
        lay.addItem(QSpacerItem(1, 20), 7, 0)
        lay.addLayout(lay_tim, 8, 0)
        lay.setRowStretch(1, 2)
        lay.setRowStretch(3, 2)
        lay.setRowStretch(5, 2)
        lay.setRowStretch(7, 2)
