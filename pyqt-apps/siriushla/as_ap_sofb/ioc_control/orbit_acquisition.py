"""Define Controllers for the orbits displayed in the graphic."""

from qtpy.QtWidgets import QLabel, QGroupBox, QFormLayout, \
    QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QTabWidget
from qtpy.QtCore import Qt
import qtawesome as qta
from pydm.widgets import PyDMLabel, PyDMPushButton
from siriushla.util import connect_window
from siriushla.widgets import SiriusLedAlert, SiriusSpinbox, PyDMStateButton, \
    SiriusLedState
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_ti_control import HLTriggerDetailed as _HLTriggerDetailed

from siriushla.as_ap_sofb.ioc_control.base import BaseWidget
from siriushla.as_ap_sofb.ioc_control.status import StatusWidget


class AcqControlWidget(BaseWidget):

    def __init__(self, parent, prefix, acc='SI'):
        super().__init__(parent, prefix, acc)
        self.setupui()
        name = acc + 'App'
        self.setObjectName(name)
        self.setStyleSheet("#"+name+"{min-width:20em; min-height:58em;}")

    def setupui(self):
        vbl = QVBoxLayout(self)
        vbl.setSpacing(10)

        grp_bx = self._get_sofbmode_grpbx()
        vbl.addWidget(grp_bx)
        vbl.addStretch()

        tabw = QTabWidget(self)
        grp_bx = self._get_orbit_smoothing_grpbx()
        tabw.addTab(grp_bx, 'Smoothing')
        grp_bx = self._get_acqrates_grpbx()
        tabw.addTab(grp_bx, 'Acq. Rates')
        vbl.addWidget(tabw)
        vbl.addStretch()

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
        grp_bx = self._get_trigext_params_grpbx()
        tabw.addTab(grp_bx, 'External Trigger')
        grp_bx = self._get_trigdata_params_grpbx()
        tabw.addTab(grp_bx, 'Data-Driven Trigger')
        vbl.addWidget(tabw)

    def _get_sofbmode_grpbx(self):
        grp_bx = QGroupBox('SOFB Mode', self)
        fbl = QFormLayout(grp_bx)
        wid = self.create_pair_sel(grp_bx, 'SOFBMode')
        fbl.addRow(wid)
        if self.isring:
            lbl = QLabel('Extend Ring', grp_bx, alignment=Qt.AlignCenter)
            wid = self.create_pair(grp_bx, 'RingSize')
            fbl.addRow(lbl, wid)
        return grp_bx

    def _get_acqrates_grpbx(self):
        grp_bx = QWidget(self)
        hbl = QHBoxLayout(grp_bx)
        fbl = QFormLayout()
        hbl.addItem(fbl)
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
        vbl.addItem(hbl)
        spt = PyDMStateButton(
            wid, init_channel=self.prefix+'SyncWithInjection-Sel')
        rdb = SiriusLedState(
            wid, init_channel=self.prefix+'SyncWithInjection-Sts')
        hbl.addWidget(spt)
        hbl.addWidget(rdb)
        return grp_bx

    def _get_orbit_smoothing_grpbx(self):
        grp_bx = QWidget(self)
        fbl = QFormLayout(grp_bx)
        lbl = QLabel('Method', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair_sel(grp_bx, 'SmoothMethod')
        fbl.addRow(lbl, wid)

        lbl = QLabel('Num. Pts.', grp_bx, alignment=Qt.AlignCenter)
        stp = SiriusSpinbox(grp_bx, init_channel=self.prefix+'SmoothNrPts-SP')
        stp.showStepExponent = False
        rdb = PyDMLabel(grp_bx, init_channel=self.prefix+'SmoothNrPts-RB')
        rdb.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        slsh = QLabel('/', grp_bx, alignment=Qt.AlignCenter)
        slsh.setStyleSheet('min-width:0.7em; max-width:0.7em;')
        cnt = PyDMLabel(grp_bx, init_channel=self.prefix+'BufferCount-Mon')
        cnt.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        cnt.setToolTip('Current Buffer Size')
        rst = PyDMPushButton(
            grp_bx, init_channel=self.prefix+'SmoothReset-Cmd', pressValue=1)
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
        fbl.addRow(lbl, hbl)
        return grp_bx

    def _get_acq_commom_params_grpbx(self):
        grp_bx = QGroupBox('Common Parameters', self)
        fbl = QFormLayout(grp_bx)
        lbl = QLabel('Channel Rate', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair_sel(grp_bx, 'TrigAcqChan')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Trigger Type', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair_sel(grp_bx, 'TrigAcqTrigger')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Repeat', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair_sel(grp_bx, 'TrigAcqRepeat')
        fbl.addRow(lbl, wid)
        if self.isring:
            lbl = QLabel('Nr of Shots', grp_bx, alignment=Qt.AlignCenter)
            wid = self.create_pair(grp_bx, 'TrigNrShots')
            fbl.addRow(lbl, wid)
        lbl = QLabel('SamplesPre', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'TrigNrSamplesPre')
        fbl.addRow(lbl, wid)
        lbl = QLabel('SamplesPost', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'TrigNrSamplesPost')
        fbl.addRow(lbl, wid)

        lbl = QLabel('Acquisition:', grp_bx, alignment=Qt.AlignCenter)
        strt = PyDMPushButton(
            grp_bx, label='',
            init_channel=self.prefix+'TrigAcqCtrl-Sel',
            pressValue=self._csorb.TrigAcqCtrl.Start)
        strt.setToolTip('Start Acquisition')
        strt.setIcon(qta.icon('fa5s.play'))
        strt.setObjectName('strt')
        strt.setStyleSheet(
            '#strt{min-width:25px; max-width:25px; icon-size:20px;}')
        stop = PyDMPushButton(
            grp_bx, label='',
            init_channel=self.prefix+'TrigAcqCtrl-Sel',
            pressValue=self._csorb.TrigAcqCtrl.Stop)
        stop.setToolTip('Stop Acquisition')
        stop.setIcon(qta.icon('fa5s.stop'))
        stop.setObjectName('stop')
        stop.setStyleSheet(
            '#stop{min-width:25px; max-width:25px; icon-size:20px;}')
        abrt = PyDMPushButton(
            grp_bx, label='',
            init_channel=self.prefix+'TrigAcqCtrl-Sel',
            pressValue=self._csorb.TrigAcqCtrl.Abort)
        abrt.setToolTip('Abort Acquisition')
        abrt.setIcon(qta.icon('fa5s.ban'))
        abrt.setObjectName('abrt')
        abrt.setStyleSheet(
            '#abrt{min-width:25px; max-width:25px; icon-size:20px;}')

        pdmlbl = PyDMLabel(
            grp_bx, init_channel=self.prefix+'TrigAcqCtrl-Sts')
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
            grp_bx, init_channel=self.prefix+'TrigAcqConfig-Cmd', pressValue=1)
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
            sts, Window, grp_bx, prefix=self.prefix, acc=self.acc, is_orb=True)

        pdm_led = SiriusLedAlert(
            grp_bx, init_channel=self.prefix+'OrbStatus-Mon')

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

    def _get_trigext_params_grpbx(self):
        grp_bx = QWidget(self)
        pref = self.prefix.prefix + self._csorb.TRIGGER_ACQ_NAME + ':'
        fbl = QFormLayout(grp_bx)
        lbl = QLabel('Duration [us]', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'Duration', prefix=pref)
        fbl.addRow(lbl, wid)
        lbl = QLabel('Delay [us]', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'Delay', prefix=pref)
        fbl.addRow(lbl, wid)
        lbl = QLabel('Source', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair_sel(grp_bx, 'Src', prefix=pref)
        fbl.addRow(lbl, wid)
        btn = QPushButton('', grp_bx)
        btn.setToolTip('Open Trigger Window')
        btn.setObjectName('btn')
        btn.setIcon(qta.icon('fa5s.ellipsis-h'))
        btn.setStyleSheet(
            '#btn{min-width:25px;max-width:25px;icon-size:20px;}')
        win = create_window_from_widget(
            _HLTriggerDetailed, title=self._csorb.TRIGGER_ACQ_NAME)
        connect_window(btn, win, grp_bx, prefix=pref)
        hbl = QHBoxLayout()
        hbl.addStretch()
        hbl.addWidget(btn)
        fbl.addRow(hbl)
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
        lbl = QLabel('Time [ms]', grp_bx, alignment=Qt.AlignCenter)
        pdm_lbl = PyDMLabel(
            grp_bx, init_channel=self.prefix+'MTurnIdxTime-Mon')
        pdm_lbl.setAlignment(Qt.AlignCenter)
        fbl.addRow(lbl, pdm_lbl)
        lbl = QLabel('TbT Sync', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair_sel(grp_bx, 'MTurnSyncTim')
        fbl.addRow(lbl, wid)
        lbl = QLabel('TbT Mask', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair_sel(grp_bx, 'MTurnUseMask')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Mask Begin', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'MTurnMaskSplBeg')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Mask End', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'MTurnMaskSplEnd')
        fbl.addRow(lbl, wid)
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
        lbl = QLabel('Mask End', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'SPassMaskSplEnd')
        fbl.addRow(lbl, wid)
        wid = QWidget(grp_bx)
        hbl = QHBoxLayout(wid)
        pdm_btn1 = PyDMPushButton(
            init_channel=self.prefix+'SPassBgCtrl-Cmd',
            pressValue=0, label='Acquire')
        pdm_btn2 = PyDMPushButton(
            init_channel=self.prefix+'SPassBgCtrl-Cmd',
            pressValue=1, label='Reset')
        pdm_lbl = PyDMLabel(wid, init_channel=self.prefix+'SPassBgSts-Mon')
        hbl.addWidget(pdm_btn1)
        hbl.addWidget(pdm_btn2)
        hbl.addWidget(pdm_lbl)
        lbl = QLabel('BG acq.:', grp_bx, alignment=Qt.AlignCenter)
        fbl.addRow(lbl, wid)
        lbl = QLabel('Use BG', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair_sel(grp_bx, 'SPassUseBg')
        fbl.addRow(lbl, wid)
        return grp_bx


def _main():
    app = SiriusApplication()
    win = SiriusDialog()
    hbl = QHBoxLayout(win)
    prefix = pref+'SI-Glob:AP-SOFB:'
    wid = AcqControlWidget(win, prefix)
    hbl.addWidget(wid)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    from siriushla.sirius_application import SiriusApplication
    from siriushla.widgets import SiriusDialog
    from siriuspy.envars import vaca_prefix as pref
    import sys
    _main()
