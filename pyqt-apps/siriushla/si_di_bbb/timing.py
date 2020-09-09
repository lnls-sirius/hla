"""BbB Timing Module."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, \
    QGroupBox
from pydm.widgets import PyDMLabel, PyDMSpinbox, PyDMEnumComboBox

from siriuspy.envars import VACA_PREFIX as _vaca_prefix

from ..widgets import SiriusFrame


class BbBTimingWidget(QWidget):
    """BbB Timing Settings Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        self.setObjectName('SIApp')
        self._prefix = prefix
        self._device = device
        self.dev_pref = prefix + device
        self._setupUi()

    def _setupUi(self):
        ld_timing = QLabel(
            '<h3>Timing</h3>', self, alignment=Qt.AlignCenter)

        # Feedback Timing
        ld_adcdelay = QLabel('ADC Delay [ps]', self)
        sb_adcdelay = PyDMSpinbox(self, self.dev_pref+':TADC')
        sb_adcdelay.showStepExponent = False
        ld_dacdelay = QLabel('DAC Delay [ps]', self)
        sb_dacdelay = PyDMSpinbox(self, self.dev_pref+':TDAC')
        sb_dacdelay.showStepExponent = False
        ld_outdelay = QLabel('Output Delay', self)
        sb_outdelay = PyDMSpinbox(self, self.dev_pref+':DELAY')
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
        cb_clkrst = PyDMEnumComboBox(self, self.dev_pref+':CLKRST')
        ld_fidsigoff = QLabel('FID Signal Offset [ps]', self)
        sb_fidsigoff = PyDMSpinbox(self, self.dev_pref+':OFF_FIDS')
        sb_fidsigoff.showStepExponent = False
        ld_fiddelay = QLabel('Fiducial Delay', self)
        sb_fiddelay = PyDMSpinbox(self, self.dev_pref+':FID_DELAY')
        sb_fiddelay.showStepExponent = False
        fr_fiddelay = SiriusFrame(self, self.dev_pref+':FID_DELAY_SUBWR')
        fr_fiddelay.add_widget(sb_fiddelay)

        gbox_tictrl = QGroupBox('Timing Control', self)
        lay_tictrl = QGridLayout(gbox_tictrl)
        lay_tictrl.addWidget(ld_clkrst, 0, 0)
        lay_tictrl.addWidget(cb_clkrst, 0, 1)
        lay_tictrl.addWidget(ld_fidsigoff, 1, 0)
        lay_tictrl.addWidget(sb_fidsigoff, 1, 1)
        lay_tictrl.addWidget(ld_fiddelay, 2, 0)
        lay_tictrl.addWidget(fr_fiddelay, 2, 1)

        # Frequency counters
        ld_fcntch0 = QLabel('Input Clock', self)
        lb_fcntch0 = PyDMLabel(self, self.dev_pref+':FREQ_CNT_CH0')
        lb_fcntch0.showUnits = True
        ld_fcntch1 = QLabel('ACLK (RF/2)', self)
        lb_fcntch1 = PyDMLabel(self, self.dev_pref+':FREQ_CNT_CH1')
        lb_fcntch1.showUnits = True
        ld_fcntch2 = QLabel('ACLK3 (RF/3)', self)
        lb_fcntch2 = PyDMLabel(self, self.dev_pref+':FREQ_CNT_CH2')
        lb_fcntch2.showUnits = True
        ld_fcntch3 = QLabel('DAC Clock', self)
        lb_fcntch3 = PyDMLabel(self, self.dev_pref+':FREQ_CNT_CH3')
        lb_fcntch3.showUnits = True
        ld_fcntch4 = QLabel('RF/4 Processing Clock', self)
        lb_fcntch4 = PyDMLabel(self, self.dev_pref+':FREQ_CNT_CH4')
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
