"""Define Controllers for the orbits displayed in the graphic."""

from qtpy.QtWidgets import QLabel, QGroupBox, QSpacerItem, QFormLayout, \
                QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QWidget
from qtpy.QtCore import Qt
from pydm.widgets import PyDMLabel, PyDMPushButton
from siriushla.util import connect_window
from siriushla.widgets import SiriusLedAlert
from siriushla.widgets.windows import create_window_from_widget
from siriushla.as_ti_control import HLTriggerDetailed as _HLTriggerDetailed

from siriushla.as_ap_sofb.ioc_control.base import BaseWidget
from siriushla.as_ap_sofb.ioc_control.status import StatusWidget


class AcqControlWidget(BaseWidget):

    def __init__(self, parent, prefix, acc='SI'):
        super().__init__(parent, prefix, acc)
        self.setupui()

    def setupui(self):
        gdl = QGridLayout(self)
        gdl.setHorizontalSpacing(40)
        gdl.setVerticalSpacing(20)

        lbl = QLabel('General Configurations', self, alignment=Qt.AlignCenter)
        if self.isring:
            gdl.addWidget(lbl, 0, 0, 1, 2)
        else:
            gdl.addWidget(lbl, 0, 0)

        vbl = QVBoxLayout()
        gdl.addItem(vbl, 1, 0)

        grp_bx = QGroupBox('SOFB Mode', self)
        vbl.addWidget(grp_bx)
        vbl.addSpacing(20)
        fbl = QFormLayout(grp_bx)
        wid = self.create_pair_sel(grp_bx, 'SOFBMode')
        fbl.addRow(wid)
        lbl = QLabel('Extend Ring', grp_bx, alignment=Qt.AlignCenter)
        lbl.setStyleSheet("""min-width:4.5em; max-width:4.5em;""")
        wid = self.create_pair(grp_bx, 'RingSize')
        fbl.addRow(lbl, wid)

        grp_bx = QGroupBox('Orbit Smoothing Control', self)
        vbl.addWidget(grp_bx)
        vbl.addSpacing(20)
        fbl = QFormLayout(grp_bx)
        lbl = QLabel('Method', grp_bx, alignment=Qt.AlignCenter)
        lbl.setStyleSheet("""min-width:4.5em; max-width:4.5em;""")
        wid = self.create_pair_sel(grp_bx, 'SmoothMethod')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Num. Pts.', grp_bx, alignment=Qt.AlignCenter)
        lbl.setStyleSheet("""min-width:4.5em; max-width:4.5em;""")
        wid = self.create_pair(grp_bx, 'SmoothNrPts')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Buffer Size', grp_bx, alignment=Qt.AlignCenter)
        lbl.setStyleSheet("""min-width:4.5em; max-width:4.5em;""")
        pdm_lbl = PyDMLabel(grp_bx, init_channel=self.prefix+'BufferCount-Mon')
        pdm_btn = PyDMPushButton(
            init_channel=self.prefix+'SmoothReset-Cmd',
            pressValue=1,
            label='Reset Buffer')
        hbl = QHBoxLayout()
        hbl.addWidget(pdm_lbl)
        hbl.addWidget(pdm_btn)
        fbl.addRow(lbl, hbl)

        grp_bx = QGroupBox('Acquisition Rates', self)
        vbl.addWidget(grp_bx)
        vbl.addSpacing(20)
        fbl = QFormLayout(grp_bx)
        lbl = QLabel('Orbit [Hz]', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'OrbAcqRate')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Kicks [Hz]', grp_bx, alignment=Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'KickAcqRate')
        fbl.addRow(lbl, wid)

        vbl = QVBoxLayout()
        if self.isring:
            gdl.addItem(vbl, 1, 1)
        else:
            gdl.addItem(vbl, 2, 0)

        if self.isring:
            grp_bx = QGroupBox('MultiTurn Acquisition', self)
            vbl.addWidget(grp_bx)
            vbl.addSpacing(20)
            fbl = QFormLayout(grp_bx)
            lbl = QLabel('Downsampling', grp_bx, alignment=Qt.AlignCenter)
            lbl.setStyleSheet("""min-width:10em; max-width:10em;""")
            wid = self.create_pair(grp_bx, 'MTurnDownSample')
            fbl.addRow(lbl, wid)
            lbl = QLabel('Index', grp_bx, alignment=Qt.AlignCenter)
            lbl.setStyleSheet("""min-width:4.5em; max-width:4.5em;""")
            wid = self.create_pair(grp_bx, 'MTurnIdx')
            fbl.addRow(lbl, wid)
            lbl = QLabel('Time [ms]', grp_bx, alignment=Qt.AlignCenter)
            lbl.setStyleSheet("""min-width:4.5em; max-width:4.5em;""")
            pdm_lbl = PyDMLabel(
                grp_bx, init_channel=self.prefix+'MTurnIdxTime-Mon')
            pdm_lbl.setAlignment(Qt.AlignCenter)
            fbl.addRow(lbl, pdm_lbl)
            lbl = QLabel('TbT Sync', grp_bx, alignment=Qt.AlignCenter)
            lbl.setStyleSheet("""min-width:4.5em; max-width:4.5em;""")
            wid = self.create_pair_sel(grp_bx, 'MTurnSyncTim')
            fbl.addRow(lbl, wid)
            lbl = QLabel('TbT Mask', grp_bx, alignment=Qt.AlignCenter)
            lbl.setStyleSheet("""min-width:4.5em; max-width:4.5em;""")
            wid = self.create_pair_sel(grp_bx, 'MTurnUseMask')
            fbl.addRow(lbl, wid)
            lbl = QLabel('Mask Begin', grp_bx, alignment=Qt.AlignCenter)
            lbl.setStyleSheet("""min-width:4.5em; max-width:4.5em;""")
            wid = self.create_pair(grp_bx, 'MTurnMaskSplBeg')
            fbl.addRow(lbl, wid)
            lbl = QLabel('Mask End', grp_bx, alignment=Qt.AlignCenter)
            lbl.setStyleSheet("""min-width:4.5em; max-width:4.5em;""")
            wid = self.create_pair(grp_bx, 'MTurnMaskSplEnd')
            fbl.addRow(lbl, wid)

        grp_bx = QGroupBox('SinglePass Acquisition', self)
        vbl.addWidget(grp_bx)
        vbl.addSpacing(20)
        fbl = QFormLayout(grp_bx)
        lbl = QLabel('Position', grp_bx, alignment=Qt.AlignCenter)
        lbl.setStyleSheet("""min-width:4.5em; max-width:4.5em;""")
        wid = self.create_pair_sel(grp_bx, 'SPassMethod')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Avg Turns', grp_bx, alignment=Qt.AlignCenter)
        lbl.setStyleSheet("""min-width:4.5em; max-width:4.5em;""")
        wid = self.create_pair(grp_bx, 'SPassAvgNrTurns')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Mask Begin', grp_bx, alignment=Qt.AlignCenter)
        lbl.setStyleSheet("""min-width:4.5em; max-width:4.5em;""")
        wid = self.create_pair(grp_bx, 'SPassMaskSplBeg')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Mask End', grp_bx, alignment=Qt.AlignCenter)
        lbl.setStyleSheet("""min-width:4.5em; max-width:4.5em;""")
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
        lbl.setStyleSheet("""min-width:4.5em; max-width:4.5em;""")
        fbl.addRow(lbl, wid)
        lbl = QLabel('Use BG', grp_bx, alignment=Qt.AlignCenter)
        lbl.setStyleSheet("""min-width:4.5em; max-width:4.5em;""")
        wid = self.create_pair_sel(grp_bx, 'SPassUseBg')
        fbl.addRow(lbl, wid)

        lbl = QLabel('Triggered Acquisition Configurations',
                     self, alignment=Qt.AlignCenter)
        if self.isring:
            gdl.addWidget(lbl, 2, 0, 1, 2)
        else:
            gdl.addWidget(lbl, 3, 0)

        vbl = QVBoxLayout()
        if self.isring:
            gdl.addItem(vbl, 3, 0)
        else:
            gdl.addItem(vbl, 4, 0)

        grp_bx = QGroupBox('Common Parameters', self)
        vbl.addWidget(grp_bx)
        vbl.addSpacing(20)
        fbl = QFormLayout(grp_bx)
        lbl = QLabel('Acquistion Channel', grp_bx, alignment=Qt.AlignCenter)
        lbl.setStyleSheet("""min-width:10em; max-width:10em;""")
        wid = self.create_pair_sel(grp_bx, 'TrigAcqChan')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Acquistion Trigger', grp_bx, alignment=Qt.AlignCenter)
        lbl.setStyleSheet("""min-width:10em; max-width:10em;""")
        wid = self.create_pair_sel(grp_bx, 'TrigAcqTrigger')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Repeat', grp_bx, alignment=Qt.AlignCenter)
        lbl.setStyleSheet("""min-width:10em; max-width:10em;""")
        wid = self.create_pair_sel(grp_bx, 'TrigAcqRepeat')
        fbl.addRow(lbl, wid)
        if self.isring:
            lbl = QLabel('Nr of Shots', grp_bx, alignment=Qt.AlignCenter)
            lbl.setStyleSheet("""min-width:10em; max-width:10em;""")
            wid = self.create_pair(grp_bx, 'TrigNrShots')
            fbl.addRow(lbl, wid)
        lbl = QLabel('Nr of SamplesPre', grp_bx, alignment=Qt.AlignCenter)
        lbl.setStyleSheet("""min-width:10em; max-width:10em;""")
        wid = self.create_pair(grp_bx, 'TrigNrSamplesPre')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Nr of SamplesPost', grp_bx, alignment=Qt.AlignCenter)
        lbl.setStyleSheet("""min-width:10em; max-width:10em;""")
        wid = self.create_pair(grp_bx, 'TrigNrSamplesPost')
        fbl.addRow(lbl, wid)

        fbl.addItem(QSpacerItem(20, 20))
        lbl = QLabel('Control Acquisition:', grp_bx, alignment=Qt.AlignCenter)
        fbl.addRow(lbl)
        gdl2 = QGridLayout()
        fbl.addRow(gdl2)
        pdm_btn1 = PyDMPushButton(
            grp_bx, label='Start',
            init_channel=self.prefix+'TrigAcqCtrl-Sel',
            pressValue=self._csorb.TrigAcqCtrl.Start)
        pdm_btn2 = PyDMPushButton(
            grp_bx, label='Stop',
            init_channel=self.prefix+'TrigAcqCtrl-Sel',
            pressValue=self._csorb.TrigAcqCtrl.Stop)
        pdm_btn3 = PyDMPushButton(
            grp_bx, label='Abort',
            init_channel=self.prefix+'TrigAcqCtrl-Sel',
            pressValue=self._csorb.TrigAcqCtrl.Abort)
        pdmlbl = PyDMLabel(
            grp_bx, init_channel=self.prefix+'TrigAcqCtrl-Sts')
        pdmlbl.setAlignment(Qt.AlignCenter)
        gdl2.addWidget(pdm_btn1, 0, 0)
        gdl2.addWidget(pdm_btn2, 0, 1)
        gdl2.addWidget(pdm_btn3, 1, 0)
        gdl2.addWidget(pdmlbl, 1, 1)

        btn = QPushButton('Open Status', grp_bx)
        Window = create_window_from_widget(StatusWidget, title='Status')
        connect_window(
            btn, Window, self, prefix=self.prefix, acc=self.acc, is_orb=True)
        pdm_led = SiriusLedAlert(
            grp_bx, init_channel=self.prefix+'OrbStatus-Mon')
        hbl = QHBoxLayout()
        hbl.setContentsMargins(5, 30, 5, 0)
        hbl.setSpacing(9)
        hbl.addWidget(btn)
        hbl.addWidget(pdm_led)
        fbl.addRow(hbl)

        vbl = QVBoxLayout()
        if self.isring:
            gdl.addItem(vbl, 3, 1)
        else:
            gdl.addItem(vbl, 5, 0)

        grp_bx = QGroupBox('Data-Driven Trigger Parameters', self)
        vbl.addWidget(grp_bx)
        vbl.addSpacing(20)
        fbl = QFormLayout(grp_bx)
        lbl = QLabel('Channel', grp_bx, alignment=Qt.AlignCenter)
        lbl.setStyleSheet("""min-width:5em; max-width:5em;""")
        wid = self.create_pair_sel(grp_bx, 'TrigDataChan')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Selection', grp_bx, alignment=Qt.AlignCenter)
        lbl.setStyleSheet("""min-width:5em; max-width:5em;""")
        wid = self.create_pair_sel(grp_bx, 'TrigDataSel')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Threshold', grp_bx, alignment=Qt.AlignCenter)
        lbl.setStyleSheet("""min-width:5em; max-width:5em;""")
        wid = self.create_pair(grp_bx, 'TrigDataThres')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Hysteresis', grp_bx, alignment=Qt.AlignCenter)
        lbl.setStyleSheet("""min-width:5em; max-width:5em;""")
        wid = self.create_pair(grp_bx, 'TrigDataHyst')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Polarity', grp_bx, alignment=Qt.AlignCenter)
        lbl.setStyleSheet("""min-width:5em; max-width:5em;""")
        wid = self.create_pair_sel(grp_bx, 'TrigDataPol')
        fbl.addRow(lbl, wid)

        pref = self.prefix.prefix + self._csorb.TRIGGER_ACQ_NAME + ':'
        grp_bx = QGroupBox('External Trigger Parameter', self)
        vbl.addWidget(grp_bx)
        vbl.addSpacing(20)
        fbl = QFormLayout(grp_bx)
        lbl = QLabel('Duration [us]', grp_bx, alignment=Qt.AlignCenter)
        lbl.setStyleSheet("""min-width:7em; max-width:7em;""")
        wid = self.create_pair(grp_bx, 'Duration', prefix=pref)
        fbl.addRow(lbl, wid)
        lbl = QLabel('Delay [us]', grp_bx, alignment=Qt.AlignCenter)
        lbl.setStyleSheet("""min-width:7em; max-width:7em;""")
        wid = self.create_pair(grp_bx, 'Delay', prefix=pref)
        fbl.addRow(lbl, wid)
        lbl = QLabel('Source', grp_bx, alignment=Qt.AlignCenter)
        lbl.setStyleSheet("""min-width:7em; max-width:7em;""")
        wid = self.create_pair_sel(grp_bx, 'Src', prefix=pref)
        fbl.addRow(lbl, wid)
        btn = QPushButton('Open Trigger Window', grp_bx)
        win = create_window_from_widget(
            _HLTriggerDetailed, title=self._csorb.TRIGGER_ACQ_NAME)
        connect_window(btn, win, grp_bx, prefix=pref)
        fbl.addRow(btn)


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
