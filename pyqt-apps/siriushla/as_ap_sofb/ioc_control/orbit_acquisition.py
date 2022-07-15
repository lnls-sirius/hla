"""Define Controllers for the orbits displayed in the graphic."""

from qtpy.QtWidgets import QLabel, QGroupBox, QFormLayout, \
    QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QTabWidget, QCheckBox
from qtpy.QtCore import Qt
import qtawesome as qta
from pydm.widgets import PyDMPushButton
from siriushla.util import connect_window
from siriushla.widgets import SiriusLedAlert, SiriusLabel
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_ti_control import HLTriggerSimple as _HLTriggerSimple

from siriushla.as_ap_sofb.ioc_control.base import BaseWidget
from siriushla.as_ap_sofb.ioc_control.status import StatusWidget


class AcqControlWidget(BaseWidget):

    def __init__(self, parent, device, prefix='', acc='SI'):
        super().__init__(parent, device, prefix=prefix, acc=acc)
        self.setupui()
        name = acc + 'App'
        self.setObjectName(name)
        self.setStyleSheet("#"+name+"{min-width:20em; min-height:40em;}")

    def setupui(self):
        vbl = QVBoxLayout(self)

        self.details = QCheckBox('Details', self)
        vbl.addWidget(self.details, alignment=Qt.AlignRight)

        grp_bx = self._get_acq_commom_params_grpbx()
        vbl.addWidget(grp_bx)
        vbl.addStretch()

        tabw = QTabWidget(self)
        grp_bx = self._get_single_pass_acq_grpbx()
        tabw.addTab(grp_bx, 'SinglePass')
        if self.isring:
            grp_bx = self._get_multturn_acq_grpbx()
            tabw.addTab(grp_bx, 'MultiTurn')
            tabw.setCurrentIndex(1)
        vbl.addWidget(tabw)
        vbl.addStretch()

        tabw = QTabWidget(self)
        self._set_detailed(tabw)
        grp_bx = _HLTriggerSimple(
            parent=tabw, device=self._csorb.trigger_acq_name,
            prefix=self.prefix, src=True)
        tabw.addTab(grp_bx, 'External Trigger')
        grp_bx = self._get_trigdata_params_grpbx()
        tabw.addTab(grp_bx, 'Data-Driven Trigger')
        vbl.addWidget(tabw)

    def _set_detailed(self, wids):
        if not isinstance(wids, (list, tuple)):
            wids = [wids]

        for wid in wids:
            wid.setVisible(False)
            self.details.stateChanged.connect(wid.setVisible)

    def _get_acq_commom_params_grpbx(self):
        grp_bx = QGroupBox('Common Parameters', self)
        fbl = QFormLayout(grp_bx)

        lbl = QLabel('Non-linear Corr.', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair_butled(grp_bx, 'PolyCalibration')
        fbl.addRow(lbl, wid)
        self._set_detailed([lbl, wid])

        lbl = QLabel('Channel Rate', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair_sel(grp_bx, 'TrigAcqChan')
        fbl.addRow(lbl, wid)

        lbl = QLabel('Trigger Type', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair_sel(grp_bx, 'TrigAcqTrigger')
        fbl.addRow(lbl, wid)
        self._set_detailed([lbl, wid])

        lbl = QLabel('Repeat', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair_butled(grp_bx, 'TrigAcqRepeat')
        fbl.addRow(lbl, wid)
        self._set_detailed([lbl, wid])

        if self.isring:
            lbl = QLabel('Nr of Shots', grp_bx, alignment=Qt.AlignCenter)
            wid = self.create_pair(grp_bx, 'TrigNrShots')
            fbl.addRow(lbl, wid)
            self._set_detailed([lbl, wid])

        lbl = QLabel('SamplesPre', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'TrigNrSamplesPre')
        fbl.addRow(lbl, wid)
        lbl = QLabel('SamplesPost', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'TrigNrSamplesPost')
        fbl.addRow(lbl, wid)

        lbl = QLabel('Acquisition:', grp_bx, alignment=Qt.AlignCenter)
        strt = PyDMPushButton(
            grp_bx, label='',
            init_channel=self.devpref.substitute(propty='TrigAcqCtrl-Sel'),
            pressValue=self._csorb.TrigAcqCtrl.Start)
        strt.setToolTip('Start Acquisition')
        strt.setIcon(qta.icon('fa5s.play'))
        strt.setObjectName('strt')
        strt.setStyleSheet(
            '#strt{min-width:25px; max-width:25px; icon-size:20px;}')
        stop = PyDMPushButton(
            grp_bx, label='',
            init_channel=self.devpref.substitute(propty='TrigAcqCtrl-Sel'),
            pressValue=self._csorb.TrigAcqCtrl.Stop)
        stop.setToolTip('Stop Acquisition')
        stop.setIcon(qta.icon('fa5s.stop'))
        stop.setObjectName('stop')
        stop.setStyleSheet(
            '#stop{min-width:25px; max-width:25px; icon-size:20px;}')
        abrt = PyDMPushButton(
            grp_bx, label='',
            init_channel=self.devpref.substitute(propty='TrigAcqCtrl-Sel'),
            pressValue=self._csorb.TrigAcqCtrl.Abort)
        abrt.setToolTip('Abort Acquisition')
        abrt.setIcon(qta.icon('fa5s.ban'))
        abrt.setObjectName('abrt')
        abrt.setStyleSheet(
            '#abrt{min-width:25px; max-width:25px; icon-size:20px;}')

        pdmlbl = SiriusLabel(
            grp_bx, self.devpref.substitute(propty='TrigAcqCtrl-Sts'))
        pdmlbl.setObjectName('pdmlbl')
        pdmlbl.setStyleSheet(
            '#pdmlbl{min-width:6em; max-width:6em;}')
        pdmlbl.setAlignment(Qt.AlignCenter)
        hbl = QHBoxLayout()
        fbl.addRow(hbl)
        hbl.addStretch()
        hbl.addWidget(lbl)
        hbl.addWidget(strt)
        hbl.addWidget(stop)
        hbl.addWidget(abrt)
        hbl.addWidget(pdmlbl)

        conf = PyDMPushButton(
            grp_bx, pressValue=1,
            init_channel=self.devpref.substitute(propty='TrigAcqConfig-Cmd'))
        conf.setToolTip('Resend Configurations')
        conf.setIcon(qta.icon('fa5s.sync'))
        conf.setObjectName('conf')
        conf.setStyleSheet(
            '#conf{min-width:25px; max-width:25px; icon-size:20px;}')

        sts = QPushButton('', grp_bx)
        sts.setIcon(qta.icon('fa5s.list-ul'))
        sts.setToolTip('Open Detailed Status View')
        sts.setObjectName('sts')
        sts.setStyleSheet(
            '#sts{min-width:25px; max-width:25px; icon-size:20px;}')
        Window = create_window_from_widget(
            StatusWidget, title='Orbit Status')
        connect_window(
            sts, Window, grp_bx, device=self.device,
            prefix=self.prefix, acc=self.acc, is_orb=True)

        pdm_led = SiriusLedAlert(
            grp_bx, self.devpref.substitute(propty='OrbStatus-Mon'))

        lbl = QLabel('Status:', grp_bx)
        hbl = QHBoxLayout()
        hbl.setSpacing(9)
        hbl.addStretch()
        hbl.addWidget(lbl)
        hbl.addWidget(pdm_led)
        hbl.addWidget(sts)
        hbl.addWidget(conf)
        fbl.addRow(hbl)

        return grp_bx

    def _get_trigdata_params_grpbx(self):
        grp_bx = QWidget(self)
        fbl = QFormLayout(grp_bx)
        lbl = QLabel('Channel', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair_sel(grp_bx, 'TrigDataChan')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Selection', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair_sel(grp_bx, 'TrigDataSel')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Threshold', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'TrigDataThres')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Hysteresis', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'TrigDataHyst')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Polarity', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair_sel(grp_bx, 'TrigDataPol')
        fbl.addRow(lbl, wid)
        return grp_bx

    def _get_multturn_acq_grpbx(self):
        grp_bx = QWidget(self)
        fbl = QFormLayout(grp_bx)
        lbl = QLabel('Downsampling', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'MTurnDownSample')
        fbl.addRow(lbl, wid)

        lbl = QLabel('Index', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'MTurnIdx')
        fbl.addRow(lbl, wid)

        lbl = QLabel('Index Time', grp_bx, alignment=Qt.AlignCenter)
        wid = QWidget(grp_bx)
        pdm_lbl = SiriusLabel(
            wid, self.devpref.substitute(propty='MTurnIdxTime-Mon'))
        pdm_lbl.showUnits = True
        pdm_lbl.setAlignment(Qt.AlignCenter)
        conf = PyDMPushButton(
            wid, pressValue=1,
            init_channel=self.devpref.substitute(propty='MTurnAcquire-Cmd'))
        conf.setToolTip('Update MTurn PVs')
        conf.setIcon(qta.icon('fa5s.sync'))
        conf.setObjectName('conf')
        conf.setStyleSheet(
            '#conf{min-width:25px; max-width:25px; icon-size:20px;}')
        hbl = QHBoxLayout(wid)
        hbl.addWidget(pdm_lbl)
        hbl.addWidget(conf)
        fbl.addRow(lbl, wid)

        lbl = QLabel('TbT Sync', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair_butled(grp_bx, 'MTurnSyncTim')
        fbl.addRow(lbl, wid)
        self._set_detailed([lbl, wid])

        lbl = QLabel('TbT Mask', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair_butled(grp_bx, 'MTurnUseMask')
        fbl.addRow(lbl, wid)
        self._set_detailed([lbl, wid])

        lbl = QLabel('Mask Begin', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'MTurnMaskSplBeg')
        fbl.addRow(lbl, wid)
        self._set_detailed([lbl, wid])

        lbl = QLabel('Mask End', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'MTurnMaskSplEnd')
        fbl.addRow(lbl, wid)
        self._set_detailed([lbl, wid])
        return grp_bx

    def _get_single_pass_acq_grpbx(self):
        grp_bx = QWidget(self)
        fbl = QFormLayout(grp_bx)
        lbl = QLabel('Avg Turns', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'SPassAvgNrTurns')
        fbl.addRow(lbl, wid)

        lbl = QLabel('Mask Begin', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'SPassMaskSplBeg')
        fbl.addRow(lbl, wid)
        self._set_detailed([lbl, wid])

        lbl = QLabel('Mask End', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'SPassMaskSplEnd')
        fbl.addRow(lbl, wid)
        self._set_detailed([lbl, wid])

        wid = QWidget(grp_bx)
        self._set_detailed(wid)
        hbl = QHBoxLayout(wid)
        pdm_btn1 = PyDMPushButton(
            init_channel=self.devpref.substitute(propty='SPassBgCtrl-Cmd'),
            pressValue=0, label='Acquire')
        pdm_btn2 = PyDMPushButton(
            init_channel=self.devpref.substitute(propty='SPassBgCtrl-Cmd'),
            pressValue=1, label='Reset')
        pdm_lbl = SiriusLabel(
            wid, self.devpref.substitute(propty='SPassBgSts-Mon'))
        hbl.addWidget(pdm_btn1)
        hbl.addWidget(pdm_btn2)
        hbl.addWidget(pdm_lbl)
        lbl = QLabel('BG acq.:', grp_bx, alignment=Qt.AlignCenter)
        fbl.addRow(lbl, wid)
        lbl = QLabel('Use BG', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair_butled(grp_bx, 'SPassUseBg')
        fbl.addRow(lbl, wid)
        return grp_bx
