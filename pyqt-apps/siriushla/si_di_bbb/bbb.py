"""BbB Control Module."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QTabWidget, QWidget, QGridLayout, \
    QGroupBox, QSpacerItem, QSizePolicy as QSzPlcy, QPushButton, QHBoxLayout
import qtawesome as qta
from pydm.widgets import PyDMLabel, PyDMSpinbox, PyDMEnumComboBox, \
    PyDMPushButton

from siriuspy.envars import VACA_PREFIX as _vaca_prefix

from ..util import connect_window
from ..widgets.windows import create_window_from_widget
from ..widgets import SiriusMainWindow, SiriusLedAlert, PyDMStateButton, \
    PyDMLedMultiChannel, DetachableTabWidget

from .acquisition import BbBAcqSRAM, BbBAcqBRAM, BbBAcqSB
from .coefficients import BbBCoefficientsWidget
from .advanced_settings import BbBAdvancedSettingsWidget
from .pwr_amps import BbBPwrAmpsWidget
from .masks import BbBMasksWidget
from .drive import BbBDriveSettingsWidget
from .environment import BbBEnvironmMonWidget
from .timing import BbBTimingWidget
from .util import get_bbb_icon


class BbBControlWindow(SiriusMainWindow):
    """BbB Control Window."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """."""
        super().__init__(parent)
        self.prefix = prefix
        self.device = device
        self.dev_pref = prefix + device
        self.setWindowTitle(device+' Control Window')
        self.setObjectName('SIApp')
        self.setWindowIcon(get_bbb_icon())
        self._setupUi()

    def _setupUi(self):
        label = QLabel(
            '<h3>'+self.device+' Control Window</h3>', self,
            alignment=Qt.AlignCenter)

        main_wid = BbBMainSettingsWidget(
            self, self.prefix, self.device, resume=False)
        coeff_wid = BbBCoefficientsWidget(self, self.prefix, self.device)
        drive_wid = BbBDriveSettingsWidget(self, self.prefix, self.device)
        sram_wid = BbBAcqSRAM(self, self.prefix, self.device)
        bram_wid = BbBAcqBRAM(self, self.prefix, self.device)
        sb_wid = BbBAcqSB(self, self.prefix, self.device)
        mask_wid = BbBMasksWidget(self, self.prefix, self.device)
        timing_wid = BbBTimingWidget(self, self.prefix, self.device)
        pwr_amp_wid = BbBPwrAmpsWidget(self, self.prefix, self.device)
        env_wid = BbBEnvironmMonWidget(self, self.prefix, self.device)
        advanced_wid = BbBAdvancedSettingsWidget(
            self, self.prefix, self.device)

        tab = DetachableTabWidget(self)
        tab.setObjectName('SIApp')
        tab.addTab(main_wid, 'Main')
        tab.addTab(sram_wid, 'SRAM')
        tab.addTab(bram_wid, 'BRAM')
        tab.addTab(mask_wid, 'Masks')
        tab.addTab(coeff_wid, 'Coefficients')
        tab.addTab(drive_wid, 'Drive')
        tab.addTab(sb_wid, 'Tune Tracking')
        tab.addTab(pwr_amp_wid, 'Pwr. Amps.')
        tab.addTab(timing_wid, 'Timing')
        tab.addTab(advanced_wid, 'Advanced Conf.')
        tab.addTab(env_wid, 'Environment')
        tab.setCurrentIndex(1)

        cw = QWidget(self)
        self.setCentralWidget(cw)
        lay = QGridLayout(cw)
        lay.addWidget(label, 0, 0)
        lay.addWidget(tab, 1, 0)


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
        fbsett_wid = self._setupFeedbackSettings()
        status_wid = self._setupStatusWidget()

        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        if self._is_resumed:
            led_gensts = SiriusLedAlert(self, self.dev_pref+':ERRSUM')
            dev_label = QLabel(
                '<h3>'+self._label+'</h3>', self, alignment=Qt.AlignCenter)
            self.pb_detail = QPushButton(qta.icon('fa5s.ellipsis-v'), '', self)
            self.pb_detail.setObjectName('dtls')
            self.pb_detail.setStyleSheet(
                '#dtls{min-width:20px;max-width:20px;icon-size:15px;}')
            hbox_label = QHBoxLayout()
            hbox_label.setContentsMargins(0, 0, 0, 0)
            hbox_label.addWidget(led_gensts, alignment=Qt.AlignLeft)
            hbox_label.addWidget(dev_label)
            hbox_label.addWidget(self.pb_detail, alignment=Qt.AlignRight)
            hbox_label.setStretch(0, 1)
            hbox_label.setStretch(1, 10)
            hbox_label.setStretch(2, 1)

            gbox = QGroupBox(self)
            lay_box = QGridLayout(gbox)
            lay_box.setVerticalSpacing(15)
            lay_box.addLayout(hbox_label, 0, 0)
            lay_box.addWidget(fbsett_wid, 1, 0)
            lay_box.addWidget(status_wid, 2, 0)

            lay.setContentsMargins(0, 0, 0, 0)
            lay.addWidget(gbox)
        else:
            info_wid = BbBInfoWidget(self, self._prefix, self._device)
            lay.addWidget(fbsett_wid, 0, 1)
            lay.addWidget(status_wid, 0, 2)
            lay.addWidget(info_wid, 0, 3)
            lay.setColumnStretch(0, 3)
            lay.setColumnStretch(4, 3)
            lay.setRowStretch(1, 3)

    def _setupFeedbackSettings(self):
        ld_fbenbl = QLabel('Enable', self)
        pb_fbenbl = PyDMStateButton(self, self.dev_pref+':FBCTRL')

        ld_coefsel = QLabel('Coeficient Set', self)
        cb_coefsel = PyDMEnumComboBox(self, self.dev_pref+':SETSEL')

        ld_sftgain = QLabel('Shift Gain', self)
        sb_sftgain = PyDMSpinbox(self, self.dev_pref+':SHIFTGAIN')
        sb_sftgain.showStepExponent = False

        ld_downspl = QLabel('Downsampling', self)
        sb_downspl = PyDMSpinbox(self, self.dev_pref+':PROC_DS')
        sb_downspl.showStepExponent = False

        ld_satthrs = QLabel('Sat. Threshold [%]', self)
        sb_satthrs = PyDMSpinbox(self, self.dev_pref+':SAT_THRESHOLD')
        sb_satthrs.showStepExponent = False

        lay = QGridLayout()
        lay.addWidget(ld_fbenbl, 1, 0)
        lay.addWidget(pb_fbenbl, 1, 1)
        lay.addWidget(ld_coefsel, 2, 0)
        lay.addWidget(cb_coefsel, 2, 1)
        lay.addWidget(ld_sftgain, 3, 0)
        lay.addWidget(sb_sftgain, 3, 1)
        lay.addWidget(ld_downspl, 4, 0)
        lay.addWidget(sb_downspl, 4, 1)
        lay.addWidget(ld_satthrs, 5, 0)
        lay.addWidget(sb_satthrs, 5, 1)

        if self._is_resumed:
            wid = QWidget()
            wid.setLayout(lay)
            fb_label = QLabel(
                '<h4>Feedback Settings</h4>', self, alignment=Qt.AlignCenter)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setVerticalSpacing(12)
            lay.addWidget(fb_label, 0, 0, 1, 2)
        else:
            wid = QGroupBox('Feedback Settings', self)
            wid.setLayout(lay)

            ld_gensts = QLabel('Setup Status', self)
            led_gensts = SiriusLedAlert(self, self.dev_pref+':ERRSUM')
            lay.addWidget(ld_gensts, 6, 0)
            lay.addWidget(led_gensts, 6, 1)
        return wid

    def _setupStatusWidget(self):
        if self._is_resumed:
            ld_status = QLabel('<h4>Status</h4>', self)

            chs2vals = {
                self.dev_pref+':CLKMISS': 0,
                self.dev_pref+':PLL_UNLOCK': 0,
                self.dev_pref+':DCM_UNLOCK': 0,
                self.dev_pref+':ADC_OVR': 0,
                self.dev_pref+':SAT': 0,
                self.dev_pref+':FID_ERR': 0,
            }
            led_status = PyDMLedMultiChannel(self, chs2vals)
            led_status.setStyleSheet('min-width:1.29em; max-width:1.29em;')
            wind = create_window_from_widget(
                BbBStatusWidget, title='BbB Status Details')
            connect_window(
                led_status, wind, resume=True,
                parent=self, signal=led_status.clicked,
                prefix=self._prefix, device=self._device)

            wid = QWidget()
            lay = QGridLayout(wid)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.addWidget(ld_status, 0, 0)
            lay.addWidget(led_status, 0, 1)
        else:
            status = BbBStatusWidget(self, self._prefix, self._device)
            wid = QGroupBox('Status', self)
            lay = QGridLayout(wid)
            lay.addWidget(status, 0, 0)
        return wid


class BbBStatusWidget(QWidget):
    """."""

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
        ld_clkmis = QLabel('Clock missing', alignment=Qt.AlignCenter)
        led_clkmis = SiriusLedAlert(self, self.dev_pref+':CLKMISS')
        lb_clkmis = PyDMLabel(self, self.dev_pref+':CLKMISS_COUNT')

        ld_pllulk = QLabel('PLL Unlocked', alignment=Qt.AlignCenter)
        led_pllulk = SiriusLedAlert(self, self.dev_pref+':PLL_UNLOCK')
        lb_pllulk = PyDMLabel(self, self.dev_pref+':PLL_UNLOCK_COUNT')

        ld_dcmulk = QLabel('DCM unlocked', alignment=Qt.AlignCenter)
        led_dcmulk = SiriusLedAlert(self, self.dev_pref+':DCM_UNLOCK')
        lb_dcmulk = PyDMLabel(self, self.dev_pref+':DCM_UNLOCK_COUNT')

        ld_avcovr = QLabel('AVC Overrange', alignment=Qt.AlignCenter)
        led_avcovr = SiriusLedAlert(self, self.dev_pref+':ADC_OVR')
        lb_avcovr = PyDMLabel(self, self.dev_pref+':ADC_OVR_COUNT')

        ld_outsat = QLabel('Output satured', alignment=Qt.AlignCenter)
        led_outsat = SiriusLedAlert(self, self.dev_pref+':SAT')
        lb_outsat = PyDMLabel(self, self.dev_pref+':SAT_COUNT')

        ld_fiderr = QLabel('Fiducial Error', alignment=Qt.AlignCenter)
        led_fiderr = SiriusLedAlert(self, self.dev_pref+':FID_ERR')
        lb_fiderr = PyDMLabel(self, self.dev_pref+':FID_ERR_COUNT')

        ld_intvl = QLabel('Interval [s]', alignment=Qt.AlignCenter)
        lb_intvl = PyDMLabel(self, self.dev_pref+':RST_COUNT')
        pb_intvl = PyDMPushButton(
            self, init_channel=self.dev_pref+':CNTRST', pressValue=1)
        pb_intvl.setText('Reset')
        pb_intvl.setToolTip('Reset Counts')
        pb_intvl.setIcon(qta.icon('fa5s.sync'))
        pb_intvl.setObjectName('conf')

        lay = QGridLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        if self._is_resumed:
            lay.addWidget(
                QLabel('<h3>Status</h3>', self, alignment=Qt.AlignCenter),
                0, 0, 1, 3)
            lay.addItem(
                QSpacerItem(1, 10, QSzPlcy.Ignored, QSzPlcy.Fixed), 1, 0)
        lay.addWidget(
            QLabel('<h4>Description</h4>', self, alignment=Qt.AlignCenter),
            2, 1)
        lay.addWidget(
            QLabel('<h4>Count</h4>', self, alignment=Qt.AlignCenter), 2, 2)
        lay.addWidget(led_clkmis, 3, 0)
        lay.addWidget(ld_clkmis, 3, 1)
        lay.addWidget(lb_clkmis, 3, 2)
        lay.addWidget(led_pllulk, 4, 0)
        lay.addWidget(ld_pllulk, 4, 1)
        lay.addWidget(lb_pllulk, 4, 2)
        lay.addWidget(led_dcmulk, 5, 0)
        lay.addWidget(ld_dcmulk, 5, 1)
        lay.addWidget(lb_dcmulk, 5, 2)
        lay.addWidget(led_avcovr, 6, 0)
        lay.addWidget(ld_avcovr, 6, 1)
        lay.addWidget(lb_avcovr, 6, 2)
        lay.addWidget(led_outsat, 7, 0)
        lay.addWidget(ld_outsat, 7, 1)
        lay.addWidget(lb_outsat, 7, 2)
        lay.addWidget(led_fiderr, 8, 0)
        lay.addWidget(ld_fiderr, 8, 1)
        lay.addWidget(lb_fiderr, 8, 2)
        lay.addItem(QSpacerItem(1, 10, QSzPlcy.Ignored, QSzPlcy.Fixed), 8, 0)
        hlay = QHBoxLayout()
        lay.addLayout(hlay, 9, 0, 1, 3)
        hlay.addWidget(ld_intvl)
        hlay.addWidget(lb_intvl)
        hlay.addStretch()
        hlay.addWidget(pb_intvl)


class BbBInfoWidget(QGroupBox):
    """BbB Info Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        self.setObjectName('SIApp')
        self._prefix = prefix
        self._device = device
        self.dev_pref = prefix + device
        self._setupUi()

    def _setupUi(self):
        self.setTitle('System Information')

        ld_rffreq = QLabel('Nominal RF Frequency', self)
        lb_rffreq = PyDMLabel(self, self.dev_pref+':RF_FREQ')
        lb_rffreq.showUnits = True

        ld_hn = QLabel('Harmonic Number', self)
        lb_hn = PyDMLabel(self, self.dev_pref+':HARM_NUM')

        ld_gtwrvw = QLabel('Gateway Revision', self)
        lb_gtwrvw = PyDMLabel(self, self.dev_pref+':REVISION')

        ld_gtwtyp = QLabel('Gateway Type', self)
        lb_gtwtyp = PyDMLabel(self, self.dev_pref+':GW_TYPE')
        lb_gtwtyp.displayFormat = PyDMLabel.DisplayFormat.Hex

        ld_ipaddr = QLabel('IP Address', self)
        lb_ipaddr = PyDMLabel(self, self.dev_pref+':IP_ADDR')

        lay = QGridLayout(self)
        lay.setVerticalSpacing(15)
        lay.addWidget(ld_rffreq, 0, 0)
        lay.addWidget(lb_rffreq, 0, 1)
        lay.addWidget(ld_hn, 1, 0)
        lay.addWidget(lb_hn, 1, 1)
        lay.addWidget(ld_gtwrvw, 2, 0)
        lay.addWidget(lb_gtwrvw, 2, 1)
        lay.addWidget(ld_gtwtyp, 3, 0)
        lay.addWidget(lb_gtwtyp, 3, 1)
        lay.addWidget(ld_ipaddr, 4, 0)
        lay.addWidget(lb_ipaddr, 4, 1)

        self.setStyleSheet(
            "PyDMLabel{qproperty-alignment: AlignCenter;}")
