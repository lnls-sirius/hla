"""BbB Coefficients Module."""

import numpy as _np
from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, QPushButton, \
    QGroupBox, QSpacerItem, QSizePolicy as QSzPlcy, QTabWidget
import qtawesome as qta

from pydm.widgets import PyDMLabel, PyDMSpinbox, PyDMEnumComboBox, \
    PyDMLineEdit, PyDMPushButton

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from ..util import connect_window
from ..widgets import SiriusLedAlert, SiriusDialog, SiriusLabel, \
    PyDMStateButton, SiriusLedState
from .custom_widgets import WfmGraph


class Label(SiriusLabel):

    def value_changed(self, new_value):
        if isinstance(new_value, _np.ndarray):
            new_value = new_value[0]
        return super().value_changed(new_value)


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
        gbox_feedback = self._setupFBSettingsWidget()
        gbox_coefview = self._setupCoefficientsViewWidget()
        gbox_coefedit = self._setupCoefficientsEditWidget()

        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        lay.setVerticalSpacing(9)
        lay.setHorizontalSpacing(15)
        lay.addWidget(gbox_coefedit, 0, 0, 1, 2)
        lay.addWidget(gbox_feedback, 1, 0)
        if not self.dev_pref.endswith('-L'):
            gbox_bun_clean = self._setupBCSettingsWidget()
            lay.addWidget(gbox_bun_clean, 1, 1)

        lay.addWidget(gbox_coefview, 0, 2, 2, 1)
        lay.setColumnStretch(0, 2)
        lay.setColumnStretch(2, 1)

    def _setupCoefficientsEditWidget(self, parent=None):
        wid = QGroupBox('Edit Coefficients', parent or self)

        self._le_coefdesc = PyDMLineEdit(self, self.dev_pref+':DESC_COEFF')
        self._graph_coefs = WfmGraph(wid)
        self._graph_coefs.add_scatter_curve(
            ychannel=self.dev_pref+':COEFF', lineStyle=Qt.SolidLine)

        self._graph_fftmag = WfmGraph(wid)
        self._graph_fftmag.setObjectName('graph')
        self._graph_fftmag.setStyleSheet('#graph{min-height: 12em;}')
        self._graph_fftmag.setLabel('left', text='Magnitude [dB]')
        self._graph_fftmag.setLabel('bottom', text='Fractional Freq.')
        self._graph_fftmag.add_scatter_curve(
            ychannel=self.dev_pref+':FTF_MAG',
            xchannel=self.dev_pref+':FTF_FREQ',
            color=QColor('blue'), lineWidth=2, lineStyle=Qt.SolidLine,
            symbolSize=4)
        self._graph_fftmag.add_scatter_curve(
            ychannel=self.dev_pref+':FTF_GTUNE',
            xchannel=self.dev_pref+':FTF_FTUNE',
            name='Tune', color=QColor('red'))

        self._graph_fftphs = WfmGraph(wid)
        self._graph_fftphs.setLabel('left', text='Phase [°]')
        self._graph_fftphs.setLabel('bottom', text='Fractional Freq.')
        self._graph_fftphs.add_scatter_curve(
            ychannel=self.dev_pref+':FTF_PHASE',
            xchannel=self.dev_pref+':FTF_FREQ',
            color=QColor('blue'), lineWidth=2, lineStyle=Qt.SolidLine,
            symbolSize=4)
        self._graph_fftphs.add_scatter_curve(
            ychannel=self.dev_pref+':FTF_PTUNE',
            xchannel=self.dev_pref+':FTF_FTUNE',
            name='Tune', color=QColor('red'))

        self._ld_fractune = QLabel(
            '<h4> Marker:</h4>', wid, alignment=Qt.AlignLeft|Qt.AlignVCenter)
        self._ld_ftval = QLabel(
            'Frequency [0-1]', wid, alignment=Qt.AlignRight|Qt.AlignVCenter)
        self._sb_ftval = PyDMSpinbox(wid, self.dev_pref+':FTF_TUNE')
        self._sb_ftval.showStepExponent = False
        self._ld_ftgain = QLabel(
            'Gain [dB]', wid, alignment=Qt.AlignRight|Qt.AlignVCenter)
        self._lb_ftgain = Label(wid, self.dev_pref+':FTF_GTUNE')
        self._lb_ftgain.precisionFromPV = False
        self._lb_ftgain.precision = 2
        self._ld_ftphs = QLabel(
            'Phase [°]', wid, alignment=Qt.AlignRight|Qt.AlignVCenter)
        self._lb_ftphs = Label(wid, self.dev_pref+':FTF_PTUNE')
        self._lb_ftphs.precisionFromPV = False
        self._lb_ftphs.precision = 2

        lay_genft = QGridLayout()
        lay_genft.setVerticalSpacing(6)
        lay_genft.setHorizontalSpacing(9)
        lay_genft.addWidget(self._ld_fractune, 0, 0)
        lay_genft.addWidget(self._ld_ftval, 0, 2)
        lay_genft.addWidget(self._sb_ftval, 0, 3)
        lay_genft.addWidget(self._ld_ftgain, 0, 5)
        lay_genft.addWidget(self._lb_ftgain, 0, 6)
        lay_genft.addWidget(self._ld_ftphs, 0, 8)
        lay_genft.addWidget(self._lb_ftphs, 0, 9)
        lay_genft.setRowStretch(1, 2)
        lay_genft.setRowStretch(4, 2)
        lay_genft.setRowStretch(7, 2)
        lay_genft.setRowStretch(10, 2)

        coef_edit_wid = self._setupCoeffSettingsWidget()

        lay = QGridLayout(wid)
        lay.setVerticalSpacing(15)
        lay.addWidget(coef_edit_wid, 0, 0, 2, 1)
        lay.addWidget(self._le_coefdesc, 0, 1)
        lay.addWidget(self._graph_coefs, 1, 1)
        lay.addWidget(self._graph_fftmag, 2, 0)
        lay.addWidget(self._graph_fftphs, 2, 1)
        lay.addLayout(lay_genft, 3, 0, 1, 2)
        return wid

    def _setupCoeffSettingsWidget(self):
        self._ld_coefchoo = QLabel('Choose Set', self, alignment=Qt.AlignRight)
        self._cb_coefchoo = PyDMEnumComboBox(self, self.dev_pref+':LDSET')

        self._pb_coefload = PyDMPushButton(
            parent=self, label='Apply Set', icon=qta.icon('mdi.upload'),
            init_channel=self.dev_pref+':BO_CPCOEFF', pressValue=1)
        self._pb_coefload.setStyleSheet("icon-size:20px;")
        self._pb_coefvrfy = PyDMPushButton(
            parent=self, label='Verify Set',
            icon=qta.icon('mdi.check-circle-outline'),
            init_channel=self.dev_pref+':BO_CVERIFY', pressValue=1)
        self._pb_coefvrfy.setStyleSheet("icon-size:20px;")

        self._ld_gen = QLabel(
            '<h4>Generate Coefficients</h4>', self, alignment=Qt.AlignCenter)
        self._ld_gengain = QLabel(
            'Gain [0-1]', self, alignment=Qt.AlignRight)
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

        wid = QWidget(self)
        lay_genset = QGridLayout(wid)
        lay_genset.setVerticalSpacing(6)
        lay_genset.setHorizontalSpacing(9)
        lay_genset.addWidget(self._ld_gen, 0, 1, 1, 2)
        lay_genset.addWidget(self._ld_gengain, 1, 1)
        lay_genset.addWidget(self._sb_gengain, 1, 2)
        lay_genset.addWidget(self._ld_genphs, 2, 1)
        lay_genset.addWidget(self._sb_genphs, 2, 2)
        lay_genset.addWidget(self._ld_genfreq, 3, 1)
        lay_genset.addWidget(self._sb_genfreq, 3, 2)
        lay_genset.addWidget(self._ld_genntap, 4, 1)
        lay_genset.addWidget(self._sb_genntap, 4, 2)
        lay_genset.addWidget(self._ld_coefchoo, 5, 1)
        lay_genset.addWidget(self._cb_coefchoo, 5, 2)
        lay = QGridLayout()
        lay_genset.addLayout(lay, 6, 1, 1, 2)
        lay.addWidget(self._pb_coefload, 0, 0)
        lay.addWidget(self._pb_coefvrfy, 0, 2)
        lay.setColumnStretch(1, 2)
        lay_genset.setRowStretch(7, 2)
        lay_genset.setColumnStretch(0, 2)
        lay_genset.setColumnStretch(3, 2)
        return wid

    def _setupFBSettingsWidget(self):
        gbox_settings = QGroupBox('FeedBack Settings', self)

        self._ld_fbpatt = QLabel('Feedback Mask', self)
        self._le_fbpatt = PyDMLineEdit(self, self.dev_pref+':FB_PATTERN')

        self._ld_cfpatt = QLabel('Alternate Mask', self)
        self._le_cfpatt = PyDMLineEdit(self, self.dev_pref+':CF_PATTERN')

        self._ld_alter_inuse = QLabel('Alternate Set In Use', self)
        self._led_alter_inuse = SiriusLedState(
            self, self.dev_pref+':CF_PATTERN_SUB.VALB')

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

        lay_patt = QGridLayout()
        lay_patt.addWidget(self._ld_fbpatt, 0, 0)
        lay_patt.addWidget(self._le_fbpatt, 0, 1)
        lay_patt.addWidget(self._ld_cfpatt, 1, 0)
        lay_patt.addWidget(self._le_cfpatt, 1, 1)
        lay_patt.addWidget(self._ld_alter_inuse, 2, 0)
        lay_patt.addWidget(self._led_alter_inuse, 2, 1)

        lay = QGridLayout(gbox_settings)
        lay.addWidget(self._ld_fbenbl, 0, 1)
        lay.addWidget(self._pb_fbenbl, 0, 2)
        lay.addWidget(self._ld_downspl, 0, 4)
        lay.addWidget(self._sb_downspl, 0, 5)
        lay.addWidget(self._ld_coefsel, 1, 1)
        lay.addWidget(self._cb_coefsel, 1, 2)
        lay.addWidget(self._ld_sftgain, 1, 4)
        lay.addWidget(self._sb_sftgain, 1, 5)
        lay.addWidget(self._ld_satthrs, 2, 1)
        lay.addWidget(self._sb_satthrs, 2, 2)
        lay.addLayout(lay_patt, 4, 1, 1, 5)
        lay.setColumnStretch(0, 3)
        lay.setColumnStretch(6, 3)
        lay.setColumnStretch(3, 2)
        lay.setRowStretch(3, 2)
        lay.setRowStretch(5, 3)

        return gbox_settings

    def _setupBCSettingsWidget(self):
        gbox_settings = QGroupBox('Bunch Cleaning Settings', self)

        self._ld_bcenbl = QLabel('Enable', self)
        self._cb_bcenbl = PyDMStateButton(self, self.dev_pref+':CLEAN_ENABLE')

        self._ld_bcrenbl = QLabel('Prior Settings', self)
        self._cb_bcrenbl = PyDMEnumComboBox(
            self, self.dev_pref+':CLEAN_RENABLE')

        self._ld_bcamp = QLabel('Amplitude', self)
        self._sb_bcamp = PyDMSpinbox(self, self.dev_pref+':CLEAN_AMPL')
        self._sb_bcamp.showStepExponent = False

        self._ld_bctune = QLabel('Tune', self)
        self._sb_bctune = PyDMSpinbox(self, self.dev_pref+':CLEAN_TUNE')
        self._sb_bctune.showStepExponent = False

        self._ld_bcpatt = QLabel('Bunch Clean Mask', self)
        self._le_bcpatt = PyDMLineEdit(self, self.dev_pref+':CLEAN_PATTERN')

        lay_clean = QGridLayout(gbox_settings)
        lay_clean.addWidget(self._ld_bcenbl, 0, 0)
        lay_clean.addWidget(self._cb_bcenbl, 0, 1)
        lay_clean.addWidget(self._ld_bcrenbl, 1, 0)
        lay_clean.addWidget(self._cb_bcrenbl, 1, 1)
        lay_clean.addWidget(self._ld_bcamp, 0, 3)
        lay_clean.addWidget(self._sb_bcamp, 0, 4)
        lay_clean.addWidget(self._ld_bctune, 1, 3)
        lay_clean.addWidget(self._sb_bctune, 1, 4)
        lay = QGridLayout()
        lay.addWidget(self._ld_bcpatt, 0, 0)
        lay.addWidget(self._le_bcpatt, 0, 1)
        lay_clean.addLayout(lay, 3, 0, 1, 5)
        lay_clean.setColumnStretch(2, 2)
        return gbox_settings

    def _setupCoefficientsViewWidget(self):
        self._ld_coef0 = QLabel('<h4>Set 0</h4>', self)
        self._ld_coef0.setStyleSheet('max-width: 3em;')
        self._lb_coef0 = PyDMLabel(self, self.dev_pref+':DESC_CSET0')
        self._lb_coef0.setStyleSheet('background-color: #DCDCDC;')
        self._led_coef0 = SiriusLedAlert(self, self.dev_pref+':CVERIFY.C')
        self._led_coef0.setStyleSheet(
            'min-width: 1.29em; max-width: 1.29em;')

        self._graph_coef0 = WfmGraph(self)
        self._graph_coef0.add_scatter_curve(
            ychannel=self.dev_pref+':CSET0',
            lineStyle=Qt.SolidLine)

        self._ld_coef1 = QLabel('<h4>Set 1</h4>', self)
        self._ld_coef1.setStyleSheet('max-width: 3em;')
        self._lb_coef1 = PyDMLabel(self, self.dev_pref+':DESC_CSET1')
        self._lb_coef1.setStyleSheet('background-color: #DCDCDC;')
        self._led_coef1 = SiriusLedAlert(self, self.dev_pref+':CVERIFY.D')
        self._led_coef1.setStyleSheet(
            'min-width: 1.29em; max-width: 1.29em;')

        self._graph_coef1 = WfmGraph(self)
        self._graph_coef1.add_scatter_curve(
            ychannel=self.dev_pref+':CSET1',
            lineStyle=Qt.SolidLine)

        self._ld_coef2 = QLabel('<h4>Set 2</h4>', self)
        self._ld_coef2.setStyleSheet('max-width: 3em;')
        self._lb_coef2 = PyDMLabel(self, self.dev_pref+':DESC_CSET2')
        self._lb_coef2.setStyleSheet('background-color: #DCDCDC;')
        self._led_coef2 = SiriusLedAlert(self, self.dev_pref+':CVERIFY.G')
        self._led_coef2.setStyleSheet(
            'min-width: 1.29em; max-width: 1.29em;')

        self._graph_coef2 = WfmGraph(self)
        self._graph_coef2.add_scatter_curve(
            ychannel=self.dev_pref+':CSET2',
            lineStyle=Qt.SolidLine)

        self._ld_coef3 = QLabel('<h4>Set 3</h4>', self)
        self._ld_coef3.setStyleSheet('max-width: 3em;')
        self._lb_coef3 = PyDMLabel(self, self.dev_pref+':DESC_CSET3')
        self._lb_coef3.setStyleSheet('background-color: #DCDCDC;')
        self._led_coef3 = SiriusLedAlert(self, self.dev_pref+':CVERIFY.H')
        self._led_coef3.setStyleSheet(
            'min-width: 1.29em; max-width: 1.29em;')

        self._graph_coef3 = WfmGraph(self)
        self._graph_coef3.add_scatter_curve(
            ychannel=self.dev_pref+':CSET3',
            lineStyle=Qt.SolidLine)

        gbox_coefview = QGroupBox('Coefficient Sets View', self)
        gbox_coefview.setLayout(QGridLayout())
        tab_coefview = QTabWidget(gbox_coefview)
        gbox_coefview.layout().addWidget(tab_coefview, 0, 0)

        norm_wid = QWidget(tab_coefview)
        tab_coefview.addTab(norm_wid, 'Normal')
        lay_norm = QGridLayout(norm_wid)
        lay_norm.addWidget(self._ld_coef0, 0, 0)
        lay_norm.addWidget(self._lb_coef0, 0, 1)
        lay_norm.addWidget(self._led_coef0, 0, 2)
        lay_norm.addWidget(self._graph_coef0, 1, 0, 1, 3)
        lay_norm.addWidget(self._ld_coef1, 2, 0)
        lay_norm.addWidget(self._lb_coef1, 2, 1)
        lay_norm.addWidget(self._led_coef1, 2, 2)
        lay_norm.addWidget(self._graph_coef1, 3, 0, 1, 3)

        alter_wid = QWidget(tab_coefview)
        tab_coefview.addTab(alter_wid, 'Alternate')
        lay_alter = QGridLayout(alter_wid)
        lay_alter.addWidget(self._ld_coef2, 0, 3)
        lay_alter.addWidget(self._lb_coef2, 0, 4)
        lay_alter.addWidget(self._led_coef2, 0, 5)
        lay_alter.addWidget(self._graph_coef2, 1, 3, 1, 3)
        lay_alter.addWidget(self._ld_coef3, 2, 3)
        lay_alter.addWidget(self._lb_coef3, 2, 4)
        lay_alter.addWidget(self._led_coef3, 2, 5)
        lay_alter.addWidget(self._graph_coef3, 3, 3, 1, 3)
        return gbox_coefview
