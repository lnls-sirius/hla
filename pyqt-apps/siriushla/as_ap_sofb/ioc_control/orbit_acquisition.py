"""Define Controllers for the orbits displayed in the graphic."""

from qtpy.QtWidgets import QLabel, QGroupBox, QSpacerItem, QFormLayout, \
                QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton
from qtpy.QtCore import Qt
from pydm.widgets import PyDMLabel, PyDMPushButton
from siriushla.util import connect_window
from siriushla.widgets import SiriusLedAlert
from siriushla.widgets.windows import create_window_from_widget

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

        lbl = QLabel('General Configurations', self)
        lbl.setAlignment(Qt.AlignCenter)
        if self.isring:
            gdl.addWidget(lbl, 0, 0, 1, 2)
        else:
            gdl.addWidget(lbl, 0, 0)

        vbl = QVBoxLayout()
        gdl.addItem(vbl, 1, 0)

        grp_bx = QGroupBox('Orbit Mode', self)
        vbl.addWidget(grp_bx)
        vbl.addSpacing(20)
        fbl = QFormLayout(grp_bx)
        wid = self.create_pair_sel(grp_bx, 'OrbitMode')
        fbl.addRow(wid)

        grp_bx = QGroupBox('Acquisition Rates', self)
        lbl.setAlignment(Qt.AlignCenter)
        vbl.addWidget(grp_bx)
        vbl.addSpacing(20)
        fbl = QFormLayout(grp_bx)
        lbl = QLabel('Orbit [Hz]', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'OrbitAcqRate')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Kicks [Hz]', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'KickAcqRate')
        fbl.addRow(lbl, wid)

        vbl = QVBoxLayout()
        if self.isring:
            gdl.addItem(vbl, 1, 1)
        else:
            gdl.addItem(vbl, 2, 0)

        grp_bx = QGroupBox('Number of Orbits for Smoothing', self)
        lbl.setAlignment(Qt.AlignCenter)
        vbl.addWidget(grp_bx)
        vbl.addSpacing(20)
        fbl = QFormLayout(grp_bx)
        wid = self.create_pair(grp_bx, 'OrbitSmoothNPnts')
        fbl.addWidget(wid)
        pdm_btn = PyDMPushButton(
            init_channel=self.prefix+'OrbitSmoothReset-Cmd',
            pressValue=1,
            label='Reset Buffer')
        fbl.addWidget(pdm_btn)

        if self.isring:
            grp_bx = QGroupBox('MultiTurn Acquisition', self)
            lbl.setAlignment(Qt.AlignCenter)
            vbl.addWidget(grp_bx)
            vbl.addSpacing(20)
            fbl = QFormLayout(grp_bx)
            lbl = QLabel('Index', grp_bx)
            wid = self.create_pair(grp_bx, 'OrbitMultiTurnIdx')
            fbl.addRow(lbl, wid)
            lbl = QLabel('Time [ms]', grp_bx)
            pdm_lbl = PyDMLabel(
                grp_bx, init_channel=self.prefix+'OrbitMultiTurnIdxTime-Mon')
            pdm_lbl.setAlignment(Qt.AlignCenter)
            fbl.addRow(lbl, pdm_lbl)

        lbl = QLabel('Triggered Acquisition Configurations', self)
        lbl.setAlignment(Qt.AlignCenter)
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
        if self.isring:
            lbl = QLabel('Acquistion Channel', grp_bx)
            lbl.setAlignment(Qt.AlignCenter)
            wid = self.create_pair_sel(grp_bx, 'OrbitTrigAcqChan')
            fbl.addRow(lbl, wid)
        lbl = QLabel('Acquistion Trigger', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair_sel(grp_bx, 'OrbitTrigAcqTrigger')
        fbl.addRow(lbl, wid)
        if self.isring:
            lbl = QLabel('Number of Shots', grp_bx)
            lbl.setAlignment(Qt.AlignCenter)
            wid = self.create_pair(grp_bx, 'OrbitTrigNrShots')
            fbl.addRow(lbl, wid)
        lbl = QLabel('Number of SamplesPre', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'OrbitTrigNrSamplesPre')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Number of SamplesPost', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'OrbitTrigNrSamplesPost')
        fbl.addRow(lbl, wid)
        if self.isring:
            lbl = QLabel('Downsampling', grp_bx)
            lbl.setAlignment(Qt.AlignCenter)
            wid = self.create_pair(grp_bx, 'OrbitTrigDownSample')
            fbl.addRow(lbl, wid)

        fbl.addItem(QSpacerItem(20, 20))
        lbl = QLabel('Control Acquisition:', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        fbl.addRow(lbl)
        gdl2 = QGridLayout()
        fbl.addRow(gdl2)
        pdm_btn1 = PyDMPushButton(
            grp_bx, label='Start',
            init_channel=self.prefix+'OrbitTrigAcqCtrl-Sel',
            pressValue=self._csorb.OrbitAcqCtrl.Start)
        pdm_btn2 = PyDMPushButton(
            grp_bx, label='Stop',
            init_channel=self.prefix+'OrbitTrigAcqCtrl-Sel',
            pressValue=self._csorb.OrbitAcqCtrl.Stop)
        pdm_btn3 = PyDMPushButton(
            grp_bx, label='Abort',
            init_channel=self.prefix+'OrbitTrigAcqCtrl-Sel',
            pressValue=self._csorb.OrbitAcqCtrl.Abort)
        pdmlbl = PyDMLabel(
            grp_bx, init_channel=self.prefix+'OrbitTrigAcqCtrl-Sts')
        pdmlbl.setAlignment(Qt.AlignCenter)
        gdl2.addWidget(pdm_btn1, 0, 0)
        gdl2.addWidget(pdm_btn2, 0, 1)
        gdl2.addWidget(pdm_btn3, 1, 0)
        gdl2.addWidget(pdmlbl, 1, 1)

        btn = QPushButton('Open Status', grp_bx)
        Window = create_window_from_widget(
            StatusWidget, name='StatusWindow')
        connect_window(
            btn, Window, self, prefix=self.prefix, acc=self.acc, is_orb=True)
        pdm_led = SiriusLedAlert(
            grp_bx, init_channel=self.prefix+'OrbitStatus-Mon')
        pdm_led.setMinimumHeight(20)
        pdm_led.setMaximumHeight(40)
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
        if self.isring:
            lbl = QLabel('Channel', grp_bx)
            lbl.setAlignment(Qt.AlignCenter)
            wid = self.create_pair_sel(grp_bx, 'OrbitTrigDataChan')
            fbl.addRow(lbl, wid)
        lbl = QLabel('Selection', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair_sel(grp_bx, 'OrbitTrigDataSel')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Threshold', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'OrbitTrigDataThres')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Hysteresis', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'OrbitTrigDataHyst')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Polarity', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair_sel(grp_bx, 'OrbitTrigDataPol')
        fbl.addRow(lbl, wid)

        grp_bx = QGroupBox('External Trigger Parameter', self)
        vbl.addWidget(grp_bx)
        vbl.addSpacing(20)
        fbl = QFormLayout(grp_bx)
        lbl = QLabel('Duration [ms]', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'OrbitTrigExtDuration')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Initial Delay [us]', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair(grp_bx, 'OrbitTrigExtDelay')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Event Source', grp_bx)
        lbl.setAlignment(Qt.AlignCenter)
        wid = self.create_pair_sel(grp_bx, 'OrbitTrigExtEvtSrc')
        fbl.addRow(lbl, wid)


def _main():
    app = SiriusApplication()
    win = SiriusDialog()
    hbl = QHBoxLayout(win)
    prefix = 'ca://' + pref+'SI-Glob:AP-SOFB:'
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
