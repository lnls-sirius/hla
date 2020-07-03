"""BbB Timing Module."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, \
    QGroupBox

from pydm.widgets import PyDMLabel, PyDMSpinbox, PyDMEnumComboBox

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriushla.widgets import SiriusFrame


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
        self._ld_timing = QLabel(
            '<h3>Timing</h3>', self, alignment=Qt.AlignCenter)

        # Feedback Timing
        self._ld_adcdelay = QLabel('ADC Delay [ps]', self)
        self._sb_adcdelay = PyDMSpinbox(self, self.dev_pref+':TADC')
        self._sb_adcdelay.showStepExponent = False
        self._ld_dacdelay = QLabel('DAC Delay [ps]', self)
        self._sb_dacdelay = PyDMSpinbox(self, self.dev_pref+':TDAC')
        self._sb_dacdelay.showStepExponent = False
        self._ld_outdelay = QLabel('Output Delay', self)
        self._sb_outdelay = PyDMSpinbox(self, self.dev_pref+':DELAY')
        self._sb_outdelay.showStepExponent = False

        gbox_fbti = QGroupBox('Feedback Timing', self)
        lay_fbti = QGridLayout(gbox_fbti)
        lay_fbti.addWidget(self._ld_adcdelay, 0, 0)
        lay_fbti.addWidget(self._sb_adcdelay, 0, 1)
        lay_fbti.addWidget(self._ld_dacdelay, 1, 0)
        lay_fbti.addWidget(self._sb_dacdelay, 1, 1)
        lay_fbti.addWidget(self._ld_outdelay, 2, 0)
        lay_fbti.addWidget(self._sb_outdelay, 2, 1)

        # Timing Control
        self._ld_clkrst = QLabel('Clock Reset', self)
        self._cb_clkrst = PyDMEnumComboBox(self, self.dev_pref+':CLKRST')
        self._ld_fidsigoff = QLabel('FID Signal Offset [ps]', self)
        self._sb_fidsigoff = PyDMSpinbox(self, self.dev_pref+':OFF_FIDS')
        self._sb_fidsigoff.showStepExponent = False
        self._ld_fiddelay = QLabel('Fiducial Delay', self)
        self._sb_fiddelay = PyDMSpinbox(self, self.dev_pref+':FID_DELAY')
        self._sb_fiddelay.showStepExponent = False
        self._fr_fiddelay = SiriusFrame(self, self.dev_pref+':FID_DELAY_SUBWR')
        self._fr_fiddelay.add_widget(self._sb_fiddelay)

        gbox_tictrl = QGroupBox('Timing Control', self)
        lay_tictrl = QGridLayout(gbox_tictrl)
        lay_tictrl.addWidget(self._ld_clkrst, 0, 0)
        lay_tictrl.addWidget(self._cb_clkrst, 0, 1)
        lay_tictrl.addWidget(self._ld_fidsigoff, 1, 0)
        lay_tictrl.addWidget(self._sb_fidsigoff, 1, 1)
        lay_tictrl.addWidget(self._ld_fiddelay, 2, 0)
        lay_tictrl.addWidget(self._fr_fiddelay, 2, 1)

        # Frequency counters
        self._ld_fcntch0 = QLabel('Input Clock', self)
        self._lb_fcntch0 = PyDMLabel(self, self.dev_pref+':FREQ_CNT_CH0')
        self._lb_fcntch0.showUnits = True
        self._ld_fcntch1 = QLabel('ACLK (RF/2)', self)
        self._lb_fcntch1 = PyDMLabel(self, self.dev_pref+':FREQ_CNT_CH1')
        self._lb_fcntch1.showUnits = True
        self._ld_fcntch2 = QLabel('ACLK3 (RF/3)', self)
        self._lb_fcntch2 = PyDMLabel(self, self.dev_pref+':FREQ_CNT_CH2')
        self._lb_fcntch2.showUnits = True
        self._ld_fcntch3 = QLabel('DAC Clock', self)
        self._lb_fcntch3 = PyDMLabel(self, self.dev_pref+':FREQ_CNT_CH3')
        self._lb_fcntch3.showUnits = True
        self._ld_fcntch4 = QLabel('RF/4 Processing Clock', self)
        self._lb_fcntch4 = PyDMLabel(self, self.dev_pref+':FREQ_CNT_CH4')
        self._lb_fcntch4.showUnits = True

        gbox_fcnts = QGroupBox('Frequency counters', self)
        lay_fcnts = QGridLayout(gbox_fcnts)
        lay_fcnts.addWidget(self._ld_fcntch0, 0, 0)
        lay_fcnts.addWidget(self._lb_fcntch0, 0, 1)
        lay_fcnts.addWidget(self._ld_fcntch1, 1, 0)
        lay_fcnts.addWidget(self._lb_fcntch1, 1, 1)
        lay_fcnts.addWidget(self._ld_fcntch2, 2, 0)
        lay_fcnts.addWidget(self._lb_fcntch2, 2, 1)
        lay_fcnts.addWidget(self._ld_fcntch3, 3, 0)
        lay_fcnts.addWidget(self._lb_fcntch3, 3, 1)
        lay_fcnts.addWidget(self._ld_fcntch4, 4, 0)
        lay_fcnts.addWidget(self._lb_fcntch4, 4, 1)

        lay = QGridLayout(self)
        lay.addWidget(self._ld_timing, 0, 0, 1, 2)
        lay.addWidget(gbox_fbti, 1, 0)
        lay.addWidget(gbox_tictrl, 1, 1)
        lay.addWidget(gbox_fcnts, 2, 0, 1, 2)

        self.setStyleSheet("SiriusFrame{max-height: 1.8em;}")
