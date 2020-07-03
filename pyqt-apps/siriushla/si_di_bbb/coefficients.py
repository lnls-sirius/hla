"""BbB Coefficients Module."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, QPushButton, \
    QGroupBox, QSpacerItem, QSizePolicy as QSzPlcy
import qtawesome as qta

from pydm.widgets import PyDMLabel, PyDMSpinbox, PyDMEnumComboBox, \
    PyDMLineEdit, PyDMPushButton

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriushla.util import connect_window
from siriushla.widgets import SiriusLedAlert
from .auxiliary_dialogs import CoeffFFTView
from .custom_widgets import WfmGraph


class BbBCoefficientsWidget(QWidget):
    """BbB Coefficients Settings Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        self.setObjectName('SIApp')
        self._prefix = prefix
        self._device = device
        self.dev_pref = prefix + device
        self._setupUi()

    def _setupUi(self):
        self._ld_coeff = QLabel(
            '<h3>Coefficients Settings</h3>', self, alignment=Qt.AlignCenter)
        gbox_settings = self._setupSettingsWidget()
        gbox_patt = self._setupPatternsControlWidget()
        gbox_coefview = self._setupCoefficientsViewWidget()

        self._coef_expert_widgets_list = [
            self._ld_coefvrfy, self._pb_coefvrfy,
            self._ld_cfpatt, self._le_cfpatt, self._ld_alternt,
            self._ld_coef2, self._lb_coef2, self._led_coef2, self._graph_coef2,
            self._ld_coef3, self._lb_coef3, self._led_coef3, self._graph_coef3]
        for widget in self._coef_expert_widgets_list:
            widget.setVisible(False)

        self._pb_expert = QPushButton('Show Expert Settings', self)
        self._pb_expert.clicked.connect(self._handle_coef_expwid_visibility)

        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        lay.setVerticalSpacing(9)
        lay.setHorizontalSpacing(15)
        lay.addItem(
            QSpacerItem(10, 1, QSzPlcy.MinimumExpanding, QSzPlcy.Fixed), 0, 0)
        lay.addWidget(self._ld_coeff, 0, 1, 1, 2)
        lay.addWidget(gbox_settings, 1, 1)
        lay.addWidget(gbox_coefview, 1, 2, 2, 1)
        lay.addWidget(gbox_patt, 2, 1)
        lay.addWidget(self._pb_expert, 3, 1, 1, 2, alignment=Qt.AlignLeft)
        lay.addItem(
            QSpacerItem(10, 1, QSzPlcy.MinimumExpanding, QSzPlcy.Fixed), 3, 3)

    def _setupSettingsWidget(self):
        self._ld_coefdesc = QLabel(
            '<h4>Coefficients</h4>', self, alignment=Qt.AlignLeft)
        self._le_coefdesc = PyDMLineEdit(self, self.dev_pref+':DESC_COEFF')

        self._ld_coefchoo = QLabel('Choose Set', self, alignment=Qt.AlignRight)
        self._cb_coefchoo = PyDMEnumComboBox(self, self.dev_pref+':LDSET')

        self._ld_coefload = QLabel('Load Set', self, alignment=Qt.AlignRight)
        self._pb_coefload = PyDMPushButton(
            parent=self, label='', icon=qta.icon('mdi.upload'),
            init_channel=self.dev_pref+':BO_CPCOEFF')
        self._pb_coefload.setObjectName('load')
        self._pb_coefload.setStyleSheet(
            "#load{min-width:25px; max-width:25px; icon-size:20px;}")

        self._ld_coefvrfy = QLabel('Verify Set', self, alignment=Qt.AlignRight)
        self._pb_coefvrfy = PyDMPushButton(
            parent=self, label='', icon=qta.icon('mdi.check-circle-outline'),
            init_channel=self.dev_pref+':BO_CVERIFY')
        self._pb_coefvrfy.setObjectName('vrfy')
        self._pb_coefvrfy.setStyleSheet(
            "#vrfy{min-width:25px; max-width:25px; icon-size:20px;}")

        self._graph_coefs = WfmGraph(self)
        self._graph_coefs.add_scatter_curve(self.dev_pref+':COEFF')

        gbox_settings = QGroupBox('Settings', self)
        lay_coef = QGridLayout()
        lay_coef.setVerticalSpacing(6)
        lay_coef.setHorizontalSpacing(9)
        lay_coef.addWidget(self._ld_coefdesc, 0, 0)
        lay_coef.addWidget(self._le_coefdesc, 1, 0, 1, 3)
        lay_coef.addItem(QSpacerItem(
            1, 10, QSzPlcy.Ignored, QSzPlcy.Fixed), 2, 0)
        lay_coef.addWidget(self._graph_coefs, 3, 0, 5, 1)
        lay_coef.addWidget(self._ld_coefchoo, 3, 1)
        lay_coef.addWidget(self._cb_coefchoo, 3, 2)
        lay_coef.addItem(QSpacerItem(
            1, 6, QSzPlcy.Ignored, QSzPlcy.Fixed), 4, 1)
        lay_coef.addWidget(self._ld_coefload, 5, 1)
        lay_coef.addWidget(self._pb_coefload, 5, 2)
        lay_coef.addItem(QSpacerItem(
            1, 6, QSzPlcy.Ignored, QSzPlcy.Fixed), 6, 1)
        lay_coef.addWidget(self._ld_coefvrfy, 7, 1)
        lay_coef.addWidget(self._pb_coefvrfy, 7, 2)

        self._ld_gen = QLabel(
            '<h4>Generate Coefficients</h4>', self, alignment=Qt.AlignLeft)
        self._pb_fftview = QPushButton('See FFT', self)
        connect_window(
            self._pb_fftview, CoeffFFTView,
            parent=self, prefix=self._prefix, device=self._device)
        self._ld_gengain = QLabel('Gain [0-1]', self, alignment=Qt.AlignRight)
        self._sb_gengain = PyDMSpinbox(self, self.dev_pref+':FLT_GAIN')
        self._sb_gengain.showStepExponent = False
        self._ld_genphs = QLabel('Phase [°]', self, alignment=Qt.AlignRight)
        self._sb_genphs = PyDMSpinbox(self, self.dev_pref+':FLT_PHASE')
        self._sb_genphs.showStepExponent = False
        self._ld_genfreq = QLabel(
            'Frequency [0-1]', self, alignment=Qt.AlignRight)
        self._sb_genfreq = PyDMSpinbox(self, self.dev_pref+':FLT_FREQ')
        self._sb_genfreq.showStepExponent = False
        self._ld_genntap = QLabel(
            'Number of taps', self, alignment=Qt.AlignRight)
        self._sb_genntap = PyDMSpinbox(self, self.dev_pref+':FLT_TAPS')
        self._sb_genntap.showStepExponent = False

        lay_genset = QGridLayout()
        lay_genset.setVerticalSpacing(6)
        lay_genset.setHorizontalSpacing(9)
        lay_genset.addWidget(self._ld_gengain, 0, 0)
        lay_genset.addWidget(self._sb_gengain, 0, 1)
        lay_genset.addWidget(self._ld_genphs, 1, 0)
        lay_genset.addWidget(self._sb_genphs, 1, 1)
        lay_genset.addWidget(self._ld_genfreq, 2, 0)
        lay_genset.addWidget(self._sb_genfreq, 2, 1)
        lay_genset.addWidget(self._ld_genntap, 3, 0)
        lay_genset.addWidget(self._sb_genntap, 3, 1)

        self._ld_fractune = QLabel(
            '<h4> • Fractional Tune</h4>', self, alignment=Qt.AlignLeft)
        self._ld_ftval = QLabel('Value', self, alignment=Qt.AlignRight)
        self._sb_ftval = PyDMSpinbox(self, self.dev_pref+':FTF_TUNE')
        self._sb_ftval.showStepExponent = False
        self._ld_ftgain = QLabel('Gain [dB]', self, alignment=Qt.AlignRight)
        self._lb_ftgain = PyDMLabel(self, self.dev_pref+':FTF_GTUNE')
        self._ld_ftphs = QLabel('Phase [°]', self, alignment=Qt.AlignRight)
        self._lb_ftphs = PyDMLabel(self, self.dev_pref+':FTF_PTUNE')

        lay_genft = QGridLayout()
        lay_genft.setVerticalSpacing(6)
        lay_genft.setHorizontalSpacing(9)
        lay_genft.addWidget(self._ld_fractune, 0, 0, 1, 2)
        lay_genft.addWidget(self._ld_ftval, 1, 0)
        lay_genft.addWidget(self._sb_ftval, 1, 1)
        lay_genft.addWidget(self._ld_ftgain, 2, 0)
        lay_genft.addWidget(self._lb_ftgain, 2, 1)
        lay_genft.addWidget(self._ld_ftphs, 3, 0)
        lay_genft.addWidget(self._lb_ftphs, 3, 1)

        lay_gen = QGridLayout()
        lay_gen.setVerticalSpacing(6)
        lay_gen.setHorizontalSpacing(15)
        lay_gen.addWidget(self._ld_gen, 0, 0, 1, 2)
        lay_gen.addWidget(self._pb_fftview, 0, 1, alignment=Qt.AlignRight)
        lay_gen.addLayout(lay_genset, 1, 0)
        lay_gen.addLayout(lay_genft, 1, 1)

        lay_settings = QGridLayout(gbox_settings)
        lay_settings.setVerticalSpacing(15)
        lay_settings.setHorizontalSpacing(15)
        lay_settings.addLayout(lay_coef, 0, 0)
        lay_settings.addLayout(lay_gen, 1, 0)
        return gbox_settings

    def _setupPatternsControlWidget(self):
        self._ld_fbpatt = QLabel(
            'Feedback\npattern', self, alignment=Qt.AlignRight)
        self._le_fbpatt = PyDMLineEdit(self, self.dev_pref+':FB_PATTERN')

        self._ld_cfpatt = QLabel(
            'Alternate\npattern', self, alignment=Qt.AlignRight)
        self._le_cfpatt = PyDMLineEdit(self, self.dev_pref+':CF_PATTERN')

        self._ld_bc = QLabel('<h4> • Bunch Cleaning</h4>', self,
                             alignment=Qt.AlignLeft)
        self._ld_bcenbl = QLabel('Enable', self, alignment=Qt.AlignRight)
        self._cb_bcenbl = PyDMEnumComboBox(
            self, self.dev_pref+':CLEAN_ENABLE')

        self._ld_bcrenbl = QLabel(
            'Prior Settings', self, alignment=Qt.AlignRight)
        self._cb_bcrenbl = PyDMEnumComboBox(
            self, self.dev_pref+':CLEAN_RENABLE')

        self._ld_bcamp = QLabel('Amplitude', self, alignment=Qt.AlignRight)
        self._sb_bcamp = PyDMSpinbox(self, self.dev_pref+':CLEAN_AMPL')
        self._sb_bcamp.showStepExponent = False

        self._ld_bctune = QLabel('Tune', self, alignment=Qt.AlignRight)
        self._sb_bctune = PyDMSpinbox(self, self.dev_pref+':CLEAN_TUNE')
        self._sb_bctune.showStepExponent = False

        self._ld_bcpatt = QLabel(
            'Clean Pattern', self, alignment=Qt.AlignRight)
        self._le_bcpatt = PyDMLineEdit(self, self.dev_pref+':CLEAN_PATTERN')

        gbox_patt = QGroupBox(self)
        lay_patt = QGridLayout(gbox_patt)
        lay_patt.setAlignment(Qt.AlignTop)
        lay_patt.setVerticalSpacing(6)
        lay_patt.setHorizontalSpacing(9)
        lay_patt.addWidget(self._ld_fbpatt, 0, 0)
        lay_patt.addWidget(self._le_fbpatt, 0, 1, 1, 3)
        lay_patt.addWidget(self._ld_cfpatt, 1, 0)
        lay_patt.addWidget(self._le_cfpatt, 1, 1, 1, 3)
        lay_patt.addItem(QSpacerItem(
            1, 6, QSzPlcy.Ignored, QSzPlcy.Fixed), 2, 0)
        lay_patt.addWidget(self._ld_bc, 3, 0, 1, 4)
        lay_patt.addWidget(self._ld_bcenbl, 4, 0)
        lay_patt.addWidget(self._cb_bcenbl, 4, 1)
        lay_patt.addWidget(self._ld_bcrenbl, 4, 2)
        lay_patt.addWidget(self._cb_bcrenbl, 4, 3)
        lay_patt.addWidget(self._ld_bcamp, 5, 0)
        lay_patt.addWidget(self._sb_bcamp, 5, 1)
        lay_patt.addWidget(self._ld_bctune, 5, 2)
        lay_patt.addWidget(self._sb_bctune, 5, 3)
        lay_patt.addWidget(self._ld_bcpatt, 6, 0)
        lay_patt.addWidget(self._le_bcpatt, 6, 1, 1, 3)
        return gbox_patt

    def _setupCoefficientsViewWidget(self):
        self._ld_norm = QLabel('Normal', self, alignment=Qt.AlignCenter)
        self._ld_alternt = QLabel('Alternate', self, alignment=Qt.AlignCenter)

        self._ld_coef0 = QLabel('Set 0', self)
        self._ld_coef0.setStyleSheet('max-width: 3em;')
        self._lb_coef0 = PyDMLabel(self, self.dev_pref+':DESC_CSET0')
        self._lb_coef0.setStyleSheet('background-color: #DCDCDC;')
        self._led_coef0 = SiriusLedAlert(self, self.dev_pref+':CVERIFY.C')
        self._led_coef0.setStyleSheet(
            'min-width: 1.29em; max-width: 1.29em;')

        self._graph_coef0 = WfmGraph(self)
        self._graph_coef0.add_scatter_curve(self.dev_pref+':CSET0')

        self._ld_coef1 = QLabel('Set 1', self)
        self._ld_coef1.setStyleSheet('max-width: 3em;')
        self._lb_coef1 = PyDMLabel(self, self.dev_pref+':DESC_CSET1')
        self._lb_coef1.setStyleSheet('background-color: #DCDCDC;')
        self._led_coef1 = SiriusLedAlert(self, self.dev_pref+':CVERIFY.D')
        self._led_coef1.setStyleSheet(
            'min-width: 1.29em; max-width: 1.29em;')

        self._graph_coef1 = WfmGraph(self)
        self._graph_coef1.add_scatter_curve(self.dev_pref+':CSET1')

        self._ld_coef2 = QLabel('Set 2', self)
        self._ld_coef2.setStyleSheet('max-width: 3em;')
        self._lb_coef2 = PyDMLabel(self, self.dev_pref+':DESC_CSET2')
        self._lb_coef2.setStyleSheet('background-color: #DCDCDC;')
        self._led_coef2 = SiriusLedAlert(self, self.dev_pref+':CVERIFY.G')
        self._led_coef2.setStyleSheet(
            'min-width: 1.29em; max-width: 1.29em;')

        self._graph_coef2 = WfmGraph(self)
        self._graph_coef2.add_scatter_curve(self.dev_pref+':CSET2')

        self._ld_coef3 = QLabel('Set 3', self)
        self._ld_coef3.setStyleSheet('max-width: 3em;')
        self._lb_coef3 = PyDMLabel(self, self.dev_pref+':DESC_CSET3')
        self._lb_coef3.setStyleSheet('background-color: #DCDCDC;')
        self._led_coef3 = SiriusLedAlert(self, self.dev_pref+':CVERIFY.H')
        self._led_coef3.setStyleSheet(
            'min-width: 1.29em; max-width: 1.29em;')

        self._graph_coef3 = WfmGraph(self)
        self._graph_coef3.add_scatter_curve(self.dev_pref+':CSET3')

        gbox_coefview = QGroupBox('Coefficient Sets View', self)
        lay_coefview = QGridLayout(gbox_coefview)
        lay_coefview.addWidget(self._ld_norm, 0, 0, 1, 2)
        lay_coefview.addWidget(self._ld_coef0, 1, 0)
        lay_coefview.addWidget(self._lb_coef0, 1, 1)
        lay_coefview.addWidget(self._led_coef0, 1, 2)
        lay_coefview.addWidget(self._graph_coef0, 2, 0, 1, 3)
        lay_coefview.addItem(QSpacerItem(
            1, 9, QSzPlcy.Fixed, QSzPlcy.Fixed), 3, 0)
        lay_coefview.addWidget(self._ld_coef1, 4, 0)
        lay_coefview.addWidget(self._lb_coef1, 4, 1)
        lay_coefview.addWidget(self._led_coef1, 4, 2)
        lay_coefview.addWidget(self._graph_coef1, 5, 0, 1, 3)
        lay_coefview.addWidget(self._ld_alternt, 0, 2, 1, 2)
        lay_coefview.addWidget(self._ld_coef2, 1, 3)
        lay_coefview.addWidget(self._lb_coef2, 1, 4)
        lay_coefview.addWidget(self._led_coef2, 1, 5)
        lay_coefview.addWidget(self._graph_coef2, 2, 3, 1, 3)
        lay_coefview.addWidget(self._ld_coef3, 4, 3)
        lay_coefview.addWidget(self._lb_coef3, 4, 4)
        lay_coefview.addWidget(self._led_coef3, 4, 5)
        lay_coefview.addWidget(self._graph_coef3, 5, 3, 1, 3)
        return gbox_coefview

    def _handle_coef_expwid_visibility(self):
        visi = self._coef_expert_widgets_list[0].isVisible()
        for widget in self._coef_expert_widgets_list:
            widget.setVisible(not visi)

        txt = ('Hide' if not visi else 'Show') + ' Expert Settings'
        self._pb_expert.setText(txt)
