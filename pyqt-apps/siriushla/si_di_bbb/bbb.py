"""BbB Control Module."""

from functools import partial as _part

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QTabWidget, QWidget, QGridLayout, \
    QGroupBox, QSpacerItem, QSizePolicy as QSzPlcy, QRadioButton, \
    QVBoxLayout, QStackedWidget, QPushButton, QHBoxLayout
import qtawesome as qta

from pydm.widgets import PyDMLabel, PyDMSpinbox, PyDMEnumComboBox

from siriuspy.envars import VACA_PREFIX as _vaca_prefix

from siriushla.util import connect_window
from siriushla.widgets.windows import create_window_from_widget
from siriushla.widgets import SiriusMainWindow, SiriusLedAlert, \
    PyDMStateButton, PyDMLedMultiChannel
from .acquisition import BbBAcqSRAM, BbBAcqBRAM, BbBAcqSB
from .coefficients import BbBCoefficientsWidget
from .devices import BbBMainDevicesWidget, BbBInfoWidget, \
    BbBSlowDACsWidget, BbBADCWidget, BbBPwrAmpsWidget, BbBMasksWidget
from .drive import BbBDriveSettingsWidget
from .environment import BbBEnvironmMonWidget
from .timing import BbBTimingWidget
from .util import get_bbb_icon


class BbBControlWindow(SiriusMainWindow):
    """BbB Control Window."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        super().__init__(parent)
        self.prefix = prefix
        self.device = device
        self.dev_pref = prefix + device
        self.setWindowTitle(device+' Control Window')
        self.setObjectName('SIApp')
        self.setWindowIcon(get_bbb_icon())
        self._setupUi()

    def _setupUi(self):
        self._label = QLabel(
            '<h3>'+self.device+' Control Window</h3>',
            self, alignment=Qt.AlignCenter)

        self._main_wid = QWidget(self)
        lay = QGridLayout(self._main_wid)
        lay.addWidget(BbBMainSettingsWidget(
            self._main_wid, self.prefix, self.device, resume=False), 0, 1)
        lay.addWidget(BbBInfoWidget(self, self.prefix, self.device), 0, 2)
        lay.setColumnStretch(0, 3)
        lay.setColumnStretch(3, 3)
        lay.setRowStretch(1, 3)

        self._coeff_wid = BbBCoefficientsWidget(
            self, self.prefix, self.device)

        self._drive_wid = BbBDriveSettingsWidget(
            self, self.prefix, self.device)

        self._sram_wid = BbBAcqSRAM(
            self, self.prefix, self.device)

        self._bram_wid = BbBAcqBRAM(
            self, self.prefix, self.device)

        self._sb_wid = BbBAcqSB(
            self, self.prefix, self.device)

        self._mask_wid = BbBMasksWidget(self, self.prefix, self.device)

        self._timing_wid = BbBTimingWidget(self, self.prefix, self.device)
        self._pwr_amp_wid = BbBPwrAmpsWidget(self, self.prefix, self.device)

        self._env_wid = BbBEnvironmMonWidget(self, self.prefix, self.device)

        self._dac_wid = BbBSlowDACsWidget(self, self.prefix, self.device)
        self._adc_wid = BbBADCWidget(self, self.prefix, self.device)
        self._devs_wid = BbBMainDevicesWidget(self, self.prefix, self.device)

        self._advanced_wid = QWidget(self)
        lay = QGridLayout(self._advanced_wid)
        lay.addWidget(self._devs_wid, 1, 1, 1, 3)
        lay.addWidget(self._adc_wid, 3, 1)
        lay.addWidget(self._dac_wid, 3, 3)
        lay.setColumnStretch(0, 3)
        lay.setColumnStretch(2, 3)
        lay.setColumnStretch(4, 3)
        lay.setRowStretch(0, 3)
        lay.setRowStretch(2, 3)
        lay.setRowStretch(4, 3)

        self._tab = QTabWidget(self)
        self._tab.setObjectName('SITab')
        self._tab.addTab(self._main_wid, 'Main')
        self._tab.addTab(self._sram_wid, 'SRAM')
        self._tab.addTab(self._bram_wid, 'BRAM')
        self._tab.addTab(self._mask_wid, 'Masks')
        self._tab.addTab(self._coeff_wid, 'Coefficients')
        self._tab.addTab(self._drive_wid, 'Drive')
        self._tab.addTab(self._sb_wid, 'Tune Tracking')
        self._tab.addTab(self._pwr_amp_wid, 'Pwr. Amps.')
        self._tab.addTab(self._timing_wid, 'Timing')
        self._tab.addTab(self._advanced_wid, 'Advanced Conf.')
        self._tab.addTab(self._env_wid, 'Environment')
        self._tab.setCurrentIndex(1)

        cw = QWidget(self)
        self.setCentralWidget(cw)
        lay = QGridLayout(cw)
        lay.addWidget(self._label, 0, 0)
        lay.addWidget(self._tab, 1, 0)

    def _handle_devices_visibility(self, idx, checked):
        if checked:
            self._dev_stack.setCurrentIndex(idx)


class BbBMainSettingsWidget(QWidget):
    """BbB Main Senttings Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device='',
                 resume=True):
        """Init."""
        super().__init__(parent)
        self.setObjectName('SIApp')
        self._prefix = prefix
        self._device = device
        self.dev_pref = prefix + device
        typ2label = {
            'H': 'Horizontal',
            'V': 'Vertical',
            'L': 'Longitudinal'}
        self._label = typ2label[self._device[-1]]
        self._is_resumed = resume
        self._setupUi()

    def _setupUi(self):
        self._fbsett_wid = self._setupFeedbackSettings()
        self._status_wid = self._setupStatusWidget()

        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        if self._is_resumed:
            self._led_gensts = SiriusLedAlert(self, self.dev_pref+':ERRSUM')
            dev_label = QLabel('<h3>'+self._label+'</h3>',
                               self, alignment=Qt.AlignCenter)
            self.pb_detail = QPushButton(qta.icon('fa5s.ellipsis-v'), '', self)
            self.pb_detail.setObjectName('dtls')
            self.pb_detail.setStyleSheet(
                '#dtls{min-width:20px;max-width:20px;icon-size:15px;}')
            hbox_label = QHBoxLayout()
            hbox_label.setContentsMargins(0, 0, 0, 0)
            hbox_label.addWidget(self._led_gensts, alignment=Qt.AlignLeft)
            hbox_label.addWidget(dev_label)
            hbox_label.addWidget(self.pb_detail, alignment=Qt.AlignRight)
            hbox_label.setStretch(0, 1)
            hbox_label.setStretch(1, 10)
            hbox_label.setStretch(2, 1)

            gbox = QGroupBox(self)
            lay_box = QGridLayout(gbox)
            lay_box.setVerticalSpacing(15)
            lay_box.addLayout(hbox_label, 0, 0)
            lay_box.addWidget(self._fbsett_wid, 1, 0)
            lay_box.addWidget(self._status_wid, 2, 0)

            lay.setContentsMargins(0, 0, 0, 0)
            lay.addWidget(gbox)
        else:
            lay.addWidget(self._fbsett_wid, 0, 0)
            lay.addWidget(self._status_wid, 0, 1)

    def _setupFeedbackSettings(self):
        self._ld_fbenbl = QLabel('Enable', self)
        self._pb_fbenbl = PyDMStateButton(self, self.dev_pref+':FBCTRL')

        self._ld_coefsel = QLabel('Coeficient Set', self)
        self._cb_coefsel = PyDMEnumComboBox(self, self.dev_pref+':SETSEL')

        self._ld_sftgain = QLabel('Shift Gain', self)
        self._sb_sftgain = PyDMSpinbox(self, self.dev_pref+':SHIFTGAIN')
        self._sb_sftgain.showStepExponent = False

        self._ld_downspl = QLabel('Downsampling', self)
        self._sb_downspl = PyDMSpinbox(self, self.dev_pref+':PROC_DS')
        self._sb_downspl.showStepExponent = False

        self._ld_satthrs = QLabel('Sat. Threshold [%]', self)
        self._sb_satthrs = PyDMSpinbox(self, self.dev_pref+':SAT_THRESHOLD')
        self._sb_satthrs.showStepExponent = False

        lay = QGridLayout()
        lay.addWidget(self._ld_fbenbl, 1, 0)
        lay.addWidget(self._pb_fbenbl, 1, 1)
        lay.addWidget(self._ld_coefsel, 2, 0)
        lay.addWidget(self._cb_coefsel, 2, 1)
        lay.addWidget(self._ld_sftgain, 3, 0)
        lay.addWidget(self._sb_sftgain, 3, 1)
        lay.addWidget(self._ld_downspl, 4, 0)
        lay.addWidget(self._sb_downspl, 4, 1)
        lay.addWidget(self._ld_satthrs, 5, 0)
        lay.addWidget(self._sb_satthrs, 5, 1)

        if self._is_resumed:
            wid = QWidget()
            wid.setLayout(lay)
            fb_label = QLabel('<h4>Feedback Settings</h4>',
                              self, alignment=Qt.AlignCenter)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setVerticalSpacing(12)
            lay.addWidget(fb_label, 0, 0, 1, 2)
        else:
            wid = QGroupBox('Feedback Settings', self)
            wid.setLayout(lay)

            self._ld_gensts = QLabel('Setup Status', self)
            self._led_gensts = SiriusLedAlert(self, self.dev_pref+':ERRSUM')
            lay.addWidget(self._ld_gensts, 6, 0)
            lay.addWidget(self._led_gensts, 6, 1)
        return wid

    def _setupStatusWidget(self):
        if self._is_resumed:
            self._ld_status = QLabel('<h4>Status</h4>', self)

            chs2vals = {
                self.dev_pref+':CLKMISS': 0,
                self.dev_pref+':PLL_UNLOCK': 0,
                self.dev_pref+':DCM_UNLOCK': 0,
                self.dev_pref+':ADC_OVR': 0,
                self.dev_pref+':SAT': 0,
                self.dev_pref+':FID_ERR': 0,
            }
            self._led_status = PyDMLedMultiChannel(self, chs2vals)
            self._led_status.setStyleSheet(
                'min-width:1.29em; max-width:1.29em;')
            wind = create_window_from_widget(
                BbBStatusWidget, title='BbB Status Details')
            connect_window(
                self._led_status, wind, resume=True,
                parent=self, signal=self._led_status.clicked,
                prefix=self._prefix, device=self._device)

            wid = QWidget()
            lay = QGridLayout(wid)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.addWidget(self._ld_status, 0, 0)
            lay.addWidget(self._led_status, 0, 1)
        else:
            status = BbBStatusWidget(self, self._prefix, self._device)

            wid = QGroupBox('Status', self)
            lay = QGridLayout(wid)
            lay.addWidget(status, 0, 0)
        return wid


class BbBStatusWidget(QWidget):

    def __init__(self, parent=None, prefix=_vaca_prefix, device='',
                 resume=False):
        """Init."""
        super().__init__(parent)
        self.setObjectName('SIApp')
        self._prefix = prefix
        self._device = device
        self.dev_pref = prefix + device
        self._is_resumed = resume
        self._setupUi()

    def _setupUi(self):
        self._ld_clkmis = QLabel('Clock missing', alignment=Qt.AlignCenter)
        self._led_clkmis = SiriusLedAlert(self, self.dev_pref+':CLKMISS')
        self._lb_clkmis = PyDMLabel(self, self.dev_pref+':CLKMISS_COUNT')

        self._ld_pllulk = QLabel('PLL Unlocked', alignment=Qt.AlignCenter)
        self._led_pllulk = SiriusLedAlert(
            self, self.dev_pref+':PLL_UNLOCK')
        self._lb_pllulk = PyDMLabel(
            self, self.dev_pref+':PLL_UNLOCK_COUNT')

        self._ld_dcmulk = QLabel('DCM unlocked', alignment=Qt.AlignCenter)
        self._led_dcmulk = SiriusLedAlert(
            self, self.dev_pref+':DCM_UNLOCK')
        self._lb_dcmulk = PyDMLabel(
            self, self.dev_pref+':DCM_UNLOCK_COUNT')

        self._ld_avcovr = QLabel('AVC Overrange', alignment=Qt.AlignCenter)
        self._led_avcovr = SiriusLedAlert(self, self.dev_pref+':ADC_OVR')
        self._lb_avcovr = PyDMLabel(self, self.dev_pref+':ADC_OVR_COUNT')

        self._ld_outsat = QLabel(
            'Output satured', alignment=Qt.AlignCenter)
        self._led_outsat = SiriusLedAlert(self, self.dev_pref+':SAT')
        self._lb_outsat = PyDMLabel(self, self.dev_pref+':SAT_COUNT')

        self._ld_fiderr = QLabel(
            'Fiducial Error', alignment=Qt.AlignCenter)
        self._led_fiderr = SiriusLedAlert(self, self.dev_pref+':FID_ERR')
        self._lb_fiderr = PyDMLabel(self, self.dev_pref+':FID_ERR_COUNT')

        self._ld_intvl = QLabel('Interval [s]', alignment=Qt.AlignCenter)
        self._lb_intvl = PyDMLabel(self, self.dev_pref+':RST_COUNT')
        self._cb_intvl = PyDMEnumComboBox(self, self.dev_pref+':CNTRST')

        lay = QGridLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        if self._is_resumed:
            lay.addWidget(QLabel('<h3>Status</h3>', self,
                                 alignment=Qt.AlignCenter), 0, 0, 1, 3)
            lay.addItem(
                QSpacerItem(1, 10, QSzPlcy.Ignored, QSzPlcy.Fixed), 1, 0)
        lay.addWidget(QLabel('<h4>Description</h4>', self,
                             alignment=Qt.AlignCenter), 2, 1)
        lay.addWidget(QLabel('<h4>Count</h4>', self,
                             alignment=Qt.AlignCenter), 2, 2)
        lay.addWidget(self._led_clkmis, 3, 0)
        lay.addWidget(self._ld_clkmis, 3, 1)
        lay.addWidget(self._lb_clkmis, 3, 2)
        lay.addWidget(self._led_pllulk, 4, 0)
        lay.addWidget(self._ld_pllulk, 4, 1)
        lay.addWidget(self._lb_pllulk, 4, 2)
        lay.addWidget(self._led_dcmulk, 5, 0)
        lay.addWidget(self._ld_dcmulk, 5, 1)
        lay.addWidget(self._lb_dcmulk, 5, 2)
        lay.addWidget(self._led_avcovr, 6, 0)
        lay.addWidget(self._ld_avcovr, 6, 1)
        lay.addWidget(self._lb_avcovr, 6, 2)
        lay.addWidget(self._led_outsat, 7, 0)
        lay.addWidget(self._ld_outsat, 7, 1)
        lay.addWidget(self._lb_outsat, 7, 2)
        lay.addWidget(self._led_fiderr, 8, 0)
        lay.addWidget(self._ld_fiderr, 8, 1)
        lay.addWidget(self._lb_fiderr, 8, 2)
        lay.addItem(
            QSpacerItem(1, 10, QSzPlcy.Ignored, QSzPlcy.Fixed), 8, 0)
        lay.addWidget(self._ld_intvl, 9, 0)
        lay.addWidget(self._lb_intvl, 9, 1)
        lay.addWidget(self._cb_intvl, 9, 2)


if __name__ == '__main__':
    """Run Example."""
    import sys
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()
    w = BbBControlWindow(
        prefix=_vaca_prefix, device='SI-Glob:DI-BbBProc-H')
    w.show()
    sys.exit(app.exec_())
