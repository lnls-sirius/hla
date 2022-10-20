"""BbB Timing Module."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, \
    QGroupBox
import qtawesome as qta

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy.namesys import SiriusPVName as _PVName

from ..widgets import SiriusFrame, SiriusSpinbox, SiriusLabel, \
    SiriusPushButton, SiriusSpinbox
from .util import set_bbb_color


class BbBTimingWidget(QWidget):
    """BbB Timing Settings Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        set_bbb_color(self, device)
        self._prefix = prefix
        self._device = _PVName(device)
        self.dev_pref = self._device.substitute(prefix=prefix)
        self._setupUi()

    def _setupUi(self):
        ld_timing = QLabel(
            '<h3>Timing</h3>', self, alignment=Qt.AlignCenter)

        # Feedback Timing
        ld_adcdelay = QLabel('ADC Delay [ps]', self)
        sb_adcdelay = SiriusSpinbox(self, self.dev_pref+':TADC')
        sb_adcdelay.showStepExponent = False
        ld_dacdelay = QLabel('DAC Delay [ps]', self)
        sb_dacdelay = SiriusSpinbox(self, self.dev_pref+':TDAC')
        sb_dacdelay.showStepExponent = False
        ld_outdelay = QLabel('Output Delay', self)
        sb_outdelay = SiriusSpinbox(self, self.dev_pref+':DELAY')
        sb_outdelay.showStepExponent = False

        gbox_fbti = QGroupBox('Feedback Timing', self)
        lay_fbti = QGridLayout(gbox_fbti)
        lay_fbti.addWidget(ld_adcdelay, 0, 0)
        lay_fbti.addWidget(sb_adcdelay, 0, 1)
        lay_fbti.addWidget(ld_dacdelay, 1, 0)
        lay_fbti.addWidget(sb_dacdelay, 1, 1)
        lay_fbti.addWidget(ld_outdelay, 2, 0)
        lay_fbti.addWidget(sb_outdelay, 2, 1)

        # Timing Control
        ld_clkrst = QLabel('Clock Reset', self)
        pb_clkrst = SiriusPushButton(
            self, init_channel=self.dev_pref+':CLKRST', pressValue=1,
            releaseValue=0)
        pb_clkrst.setText('Reset')
        pb_clkrst.setToolTip('Reset Clock')
        pb_clkrst.setIcon(qta.icon('fa5s.sync'))
        pb_clkrst.setObjectName('conf')

        ld_fidsigoff = QLabel('FID Signal Offset [ps]', self)
        sb_fidsigoff = SiriusSpinbox(self, self.dev_pref+':OFF_FIDS')
        sb_fidsigoff.showStepExponent = False
        sb_fidsigoff.limitsFromChannel = False
        sb_fidsigoff.setMinimum(0)
        sb_fidsigoff.setMaximum(3000)
        ld_fiddelay = QLabel('Fiducial Delay', self)
        sb_fiddelay = SiriusSpinbox(self, self.dev_pref+':FID_DELAY')
        sb_fiddelay.showStepExponent = False
        fr_fiddelay = SiriusFrame(self, self.dev_pref+':FID_DELAY_SUBWR')
        fr_fiddelay.add_widget(sb_fiddelay)

        gbox_tictrl = QGroupBox('Timing Control', self)
        lay_tictrl = QGridLayout(gbox_tictrl)
        lay_tictrl.addWidget(ld_clkrst, 0, 0)
        lay_tictrl.addWidget(pb_clkrst, 0, 1)
        lay_tictrl.addWidget(ld_fidsigoff, 1, 0)
        lay_tictrl.addWidget(sb_fidsigoff, 1, 1)
        lay_tictrl.addWidget(ld_fiddelay, 2, 0)
        lay_tictrl.addWidget(fr_fiddelay, 2, 1)

        # Frequency counters
        ld_fcntch0 = QLabel('Input Clock', self)
        lb_fcntch0 = SiriusLabel(self, self.dev_pref+':FREQ_CNT_CH0')
        lb_fcntch0.precisionFromPV = False
        lb_fcntch0.precision = 6
        lb_fcntch0.showUnits = True
        ld_fcntch1 = QLabel('ACLK (RF/2)', self)
        lb_fcntch1 = SiriusLabel(self, self.dev_pref+':FREQ_CNT_CH1')
        lb_fcntch1.precisionFromPV = False
        lb_fcntch1.precision = 6
        lb_fcntch1.showUnits = True
        ld_fcntch2 = QLabel('ACLK3 (RF/3)', self)
        lb_fcntch2 = SiriusLabel(self, self.dev_pref+':FREQ_CNT_CH2')
        lb_fcntch2.precisionFromPV = False
        lb_fcntch2.precision = 6
        lb_fcntch2.showUnits = True
        ld_fcntch3 = QLabel('DAC Clock', self)
        lb_fcntch3 = SiriusLabel(self, self.dev_pref+':FREQ_CNT_CH3')
        lb_fcntch3.precisionFromPV = False
        lb_fcntch3.precision = 6
        lb_fcntch3.showUnits = True
        ld_fcntch4 = QLabel('RF/4 Processing Clock', self)
        lb_fcntch4 = SiriusLabel(self, self.dev_pref+':FREQ_CNT_CH4')
        lb_fcntch4.precisionFromPV = False
        lb_fcntch4.precision = 6
        lb_fcntch4.showUnits = True

        gbox_fcnts = QGroupBox('Frequency counters', self)
        lay_fcnts = QGridLayout(gbox_fcnts)
        lay_fcnts.addWidget(ld_fcntch0, 0, 0)
        lay_fcnts.addWidget(lb_fcntch0, 0, 1)
        lay_fcnts.addWidget(ld_fcntch1, 1, 0)
        lay_fcnts.addWidget(lb_fcntch1, 1, 1)
        lay_fcnts.addWidget(ld_fcntch2, 2, 0)
        lay_fcnts.addWidget(lb_fcntch2, 2, 1)
        lay_fcnts.addWidget(ld_fcntch3, 3, 0)
        lay_fcnts.addWidget(lb_fcntch3, 3, 1)
        lay_fcnts.addWidget(ld_fcntch4, 4, 0)
        lay_fcnts.addWidget(lb_fcntch4, 4, 1)

        lay = QGridLayout(self)
        lay.addWidget(ld_timing, 0, 1, 1, 2)
        lay.addWidget(gbox_fbti, 1, 1)
        lay.addWidget(gbox_tictrl, 1, 2)
        lay.addWidget(gbox_fcnts, 2, 1, 1, 2)
        lay.setColumnStretch(0, 3)
        lay.setColumnStretch(3, 3)
        lay.setRowStretch(3, 3)

        self.setStyleSheet("SiriusFrame{max-height: 1.8em;}")
