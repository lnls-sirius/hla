"""BbB Coefficients Module."""

import numpy as _np
from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, QGroupBox, QTabWidget
import qtawesome as qta
from pydm.widgets import PyDMLabel, PyDMSpinbox, PyDMEnumComboBox, \
    PyDMLineEdit, PyDMPushButton

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy.namesys import SiriusPVName as _PVName

from ..widgets import SiriusLedAlert, SiriusLabel, PyDMStateButton, \
    SiriusLedState
from .custom_widgets import WfmGraph
from .util import set_bbb_color


class Label(SiriusLabel):
    """."""

    def value_changed(self, new_value):
        """."""
        if isinstance(new_value, _np.ndarray):
            new_value = new_value[0]
        return super().value_changed(new_value)


class BbBCoefficientsWidget(QWidget):
    """BbB Coefficients Settings Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        set_bbb_color(self, device)
        self._prefix = prefix
        self._device = _PVName(device)
        self.dev_pref = self._device.substitute(prefix=prefix)
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

        le_coefdesc = PyDMLineEdit(self, self.dev_pref+':DESC_COEFF')
        graph_coefs = WfmGraph(wid)
        graph_coefs.add_scatter_curve(
            ychannel=self.dev_pref+':COEFF', lineStyle=Qt.SolidLine)

        graph_fftmag = WfmGraph(wid)
        graph_fftmag.setObjectName('graph')
        graph_fftmag.setStyleSheet('#graph{min-height: 12em;}')
        graph_fftmag.setLabel('left', text='Magnitude [dB]')
        graph_fftmag.setLabel('bottom', text='Fractional Freq.')
        graph_fftmag.add_scatter_curve(
            ychannel=self.dev_pref+':FTF_MAG',
            xchannel=self.dev_pref+':FTF_FREQ',
            color=QColor('blue'), lineWidth=2, lineStyle=Qt.SolidLine,
            symbolSize=4)
        graph_fftmag.add_scatter_curve(
            ychannel=self.dev_pref+':FTF_GTUNE',
            xchannel=self.dev_pref+':FTF_FTUNE',
            name='Tune', color=QColor('red'))

        graph_fftphs = WfmGraph(wid)
        graph_fftphs.setLabel('left', text='Phase [°]')
        graph_fftphs.setLabel('bottom', text='Fractional Freq.')
        graph_fftphs.add_scatter_curve(
            ychannel=self.dev_pref+':FTF_PHASE',
            xchannel=self.dev_pref+':FTF_FREQ',
            color=QColor('blue'), lineWidth=2, lineStyle=Qt.SolidLine,
            symbolSize=4)
        graph_fftphs.add_scatter_curve(
            ychannel=self.dev_pref+':FTF_PTUNE',
            xchannel=self.dev_pref+':FTF_FTUNE',
            name='Tune', color=QColor('red'))

        ld_fractune = QLabel(
            '<h4> Marker:</h4>', wid, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        ld_ftval = QLabel(
            'Frequency [0-1]', wid, alignment=Qt.AlignRight | Qt.AlignVCenter)
        sb_ftval = PyDMSpinbox(wid, self.dev_pref+':FTF_TUNE')
        sb_ftval.showStepExponent = False
        ld_ftgain = QLabel(
            'Gain [dB]', wid, alignment=Qt.AlignRight | Qt.AlignVCenter)
        lb_ftgain = Label(wid, self.dev_pref+':FTF_GTUNE')
        lb_ftgain.precisionFromPV = False
        lb_ftgain.precision = 2
        ld_ftphs = QLabel(
            'Phase [°]', wid, alignment=Qt.AlignRight | Qt.AlignVCenter)
        lb_ftphs = Label(wid, self.dev_pref+':FTF_PTUNE')
        lb_ftphs.precisionFromPV = False
        lb_ftphs.precision = 2

        lay_genft = QGridLayout()
        lay_genft.setVerticalSpacing(6)
        lay_genft.setHorizontalSpacing(9)
        lay_genft.addWidget(ld_fractune, 0, 0)
        lay_genft.addWidget(ld_ftval, 0, 2)
        lay_genft.addWidget(sb_ftval, 0, 3)
        lay_genft.addWidget(ld_ftgain, 0, 5)
        lay_genft.addWidget(lb_ftgain, 0, 6)
        lay_genft.addWidget(ld_ftphs, 0, 8)
        lay_genft.addWidget(lb_ftphs, 0, 9)
        lay_genft.setRowStretch(1, 2)
        lay_genft.setRowStretch(4, 2)
        lay_genft.setRowStretch(7, 2)
        lay_genft.setRowStretch(10, 2)

        coef_edit_wid = self._setupCoeffSettingsWidget()

        lay = QGridLayout(wid)
        lay.setVerticalSpacing(15)
        lay.addWidget(coef_edit_wid, 0, 0, 2, 1)
        lay.addWidget(le_coefdesc, 0, 1)
        lay.addWidget(graph_coefs, 1, 1)
        lay.addWidget(graph_fftmag, 2, 0)
        lay.addWidget(graph_fftphs, 2, 1)
        lay.addLayout(lay_genft, 3, 0, 1, 2)
        return wid

    def _setupCoeffSettingsWidget(self):
        ld_coefchoo = QLabel('Choose Set', self, alignment=Qt.AlignRight)
        cb_coefchoo = PyDMEnumComboBox(self, self.dev_pref+':LDSET')

        pb_coefload = PyDMPushButton(
            parent=self, label='Apply Set', icon=qta.icon('mdi.upload'),
            init_channel=self.dev_pref+':BO_CPCOEFF', pressValue=1)
        pb_coefload.setStyleSheet("icon-size:20px;")
        pb_coefvrfy = PyDMPushButton(
            parent=self, label='Verify Set',
            icon=qta.icon('mdi.check-circle-outline'),
            init_channel=self.dev_pref+':BO_CVERIFY', pressValue=1)
        pb_coefvrfy.setStyleSheet("icon-size:20px;")

        ld_gen = QLabel(
            '<h4>Generate Coefficients</h4>', self, alignment=Qt.AlignCenter)
        ld_gengain = QLabel(
            'Gain [0-1]', self, alignment=Qt.AlignRight)
        sb_gengain = PyDMSpinbox(self, self.dev_pref+':FLT_GAIN')
        sb_gengain.showStepExponent = False
        ld_genphs = QLabel('Phase [°]', self, alignment=Qt.AlignRight)
        sb_genphs = PyDMSpinbox(self, self.dev_pref+':FLT_PHASE')
        sb_genphs.showStepExponent = False
        ld_genfreq = QLabel(
            'Frequency [0-1]', self, alignment=Qt.AlignRight)
        sb_genfreq = PyDMSpinbox(self, self.dev_pref+':FLT_FREQ')
        sb_genfreq.showStepExponent = False
        ld_genntap = QLabel(
            'Number of taps', self, alignment=Qt.AlignRight)
        sb_genntap = PyDMSpinbox(self, self.dev_pref+':FLT_TAPS')
        sb_genntap.showStepExponent = False

        wid = QWidget(self)
        lay_genset = QGridLayout(wid)
        lay_genset.setVerticalSpacing(6)
        lay_genset.setHorizontalSpacing(9)
        lay_genset.addWidget(ld_gen, 0, 1, 1, 2)
        lay_genset.addWidget(ld_gengain, 1, 1)
        lay_genset.addWidget(sb_gengain, 1, 2)
        lay_genset.addWidget(ld_genphs, 2, 1)
        lay_genset.addWidget(sb_genphs, 2, 2)
        lay_genset.addWidget(ld_genfreq, 3, 1)
        lay_genset.addWidget(sb_genfreq, 3, 2)
        lay_genset.addWidget(ld_genntap, 4, 1)
        lay_genset.addWidget(sb_genntap, 4, 2)
        lay_genset.addWidget(ld_coefchoo, 5, 1)
        lay_genset.addWidget(cb_coefchoo, 5, 2)
        lay = QGridLayout()
        lay_genset.addLayout(lay, 6, 1, 1, 2)
        lay.addWidget(pb_coefload, 0, 0)
        lay.addWidget(pb_coefvrfy, 0, 2)
        lay.setColumnStretch(1, 2)
        lay_genset.setRowStretch(7, 2)
        lay_genset.setColumnStretch(0, 2)
        lay_genset.setColumnStretch(3, 2)
        return wid

    def _setupFBSettingsWidget(self):
        gbox_settings = QGroupBox('FeedBack Settings', self)

        ld_fbpatt = QLabel('Feedback Mask', self)
        le_fbpatt = PyDMLineEdit(self, self.dev_pref+':FB_PATTERN')

        ld_cfpatt = QLabel('Alternate Mask', self)
        le_cfpatt = PyDMLineEdit(self, self.dev_pref+':CF_PATTERN')

        ld_alter_inuse = QLabel('Alternate Set In Use', self)
        led_alter_inuse = SiriusLedState(
            self, self.dev_pref+':CF_PATTERN_SUB.VALB')

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

        lay_patt = QGridLayout()
        lay_patt.addWidget(ld_fbpatt, 0, 0)
        lay_patt.addWidget(le_fbpatt, 0, 1)
        lay_patt.addWidget(ld_cfpatt, 1, 0)
        lay_patt.addWidget(le_cfpatt, 1, 1)
        lay_patt.addWidget(ld_alter_inuse, 2, 0)
        lay_patt.addWidget(led_alter_inuse, 2, 1)

        lay = QGridLayout(gbox_settings)
        lay.addWidget(ld_fbenbl, 0, 1)
        lay.addWidget(pb_fbenbl, 0, 2)
        lay.addWidget(ld_downspl, 0, 4)
        lay.addWidget(sb_downspl, 0, 5)
        lay.addWidget(ld_coefsel, 1, 1)
        lay.addWidget(cb_coefsel, 1, 2)
        lay.addWidget(ld_sftgain, 1, 4)
        lay.addWidget(sb_sftgain, 1, 5)
        lay.addWidget(ld_satthrs, 2, 1)
        lay.addWidget(sb_satthrs, 2, 2)
        lay.addLayout(lay_patt, 4, 1, 1, 5)
        lay.setColumnStretch(0, 3)
        lay.setColumnStretch(6, 3)
        lay.setColumnStretch(3, 2)
        lay.setRowStretch(3, 2)
        lay.setRowStretch(5, 3)

        return gbox_settings

    def _setupBCSettingsWidget(self):
        gbox_settings = QGroupBox('Bunch Cleaning Settings', self)

        ld_bcenbl = QLabel('Enable', self)
        cb_bcenbl = PyDMStateButton(self, self.dev_pref+':CLEAN_ENABLE')

        ld_bcamp = QLabel('Amplitude', self)
        sb_bcamp = PyDMSpinbox(self, self.dev_pref+':CLEAN_AMPL')
        sb_bcamp.showStepExponent = False
        lb_svamp = PyDMLabel(self, self.dev_pref+':CLEAN_SAVE_AMPL')

        ld_bctune = QLabel('Tune', self)
        sb_bctune = PyDMSpinbox(self, self.dev_pref+':CLEAN_TUNE')
        sb_bctune.showStepExponent = False
        lb_svfreq = PyDMLabel(self, self.dev_pref+':CLEAN_SAVE_FREQ')

        ld_bcspan = QLabel('Span', self)
        le_bcspan = PyDMLineEdit(self, self.dev_pref+':CLEAN_SPAN')
        lb_svspan = PyDMLabel(self, self.dev_pref+':CLEAN_SAVE_SPAN')

        ld_bcper = QLabel('Period', self)
        le_bcper = PyDMLineEdit(self, self.dev_pref+':CLEAN_PERIOD')
        lb_svper = PyDMLabel(self, self.dev_pref+':CLEAN_SAVE_PERIOD')

        ld_bcpatt = QLabel('Mask', self)
        le_bcpatt = PyDMLineEdit(self, self.dev_pref+':CLEAN_PATTERN')

        lay_clean = QGridLayout(gbox_settings)
        lay_clean.addWidget(QLabel('SAVED VALS.'), 0, 2)

        lay_clean.addWidget(ld_bcamp, 1, 0)
        lay_clean.addWidget(sb_bcamp, 1, 1)
        lay_clean.addWidget(lb_svamp, 1, 2)
        lay_clean.addWidget(ld_bctune, 2, 0)
        lay_clean.addWidget(sb_bctune, 2, 1)
        lay_clean.addWidget(lb_svfreq, 2, 2)
        lay_clean.addWidget(ld_bcspan, 3, 0)
        lay_clean.addWidget(le_bcspan, 3, 1)
        lay_clean.addWidget(lb_svspan, 3, 2)
        lay_clean.addWidget(ld_bcper, 4, 0)
        lay_clean.addWidget(le_bcper, 4, 1)
        lay_clean.addWidget(lb_svper, 4, 2)
        lay_clean.addWidget(ld_bcenbl, 5, 0)
        lay_clean.addWidget(cb_bcenbl, 5, 1)
        lay = QGridLayout()
        lay.addWidget(ld_bcpatt, 0, 0)
        lay.addWidget(le_bcpatt, 0, 1)
        lay_clean.addLayout(lay, 6, 0, 1, 3)
        return gbox_settings

    def _setupCoefficientsViewWidget(self):
        ld_coef0 = QLabel('<h4>Set 0</h4>', self)
        ld_coef0.setStyleSheet('max-width: 3em;')
        lb_coef0 = PyDMLabel(self, self.dev_pref+':DESC_CSET0')
        lb_coef0.setStyleSheet('background-color: #DCDCDC;')
        led_coef0 = SiriusLedAlert(self, self.dev_pref+':CVERIFY.C')
        led_coef0.setStyleSheet(
            'min-width: 1.29em; max-width: 1.29em;')

        graph_coef0 = WfmGraph(self)
        graph_coef0.add_scatter_curve(
            ychannel=self.dev_pref+':CSET0', lineStyle=Qt.SolidLine)

        ld_coef1 = QLabel('<h4>Set 1</h4>', self)
        ld_coef1.setStyleSheet('max-width: 3em;')
        lb_coef1 = PyDMLabel(self, self.dev_pref+':DESC_CSET1')
        lb_coef1.setStyleSheet('background-color: #DCDCDC;')
        led_coef1 = SiriusLedAlert(self, self.dev_pref+':CVERIFY.D')
        led_coef1.setStyleSheet(
            'min-width: 1.29em; max-width: 1.29em;')

        graph_coef1 = WfmGraph(self)
        graph_coef1.add_scatter_curve(
            ychannel=self.dev_pref+':CSET1', lineStyle=Qt.SolidLine)

        ld_coef2 = QLabel('<h4>Set 2</h4>', self)
        ld_coef2.setStyleSheet('max-width: 3em;')
        lb_coef2 = PyDMLabel(self, self.dev_pref+':DESC_CSET2')
        lb_coef2.setStyleSheet('background-color: #DCDCDC;')
        led_coef2 = SiriusLedAlert(self, self.dev_pref+':CVERIFY.G')
        led_coef2.setStyleSheet(
            'min-width: 1.29em; max-width: 1.29em;')

        graph_coef2 = WfmGraph(self)
        graph_coef2.add_scatter_curve(
            ychannel=self.dev_pref+':CSET2', lineStyle=Qt.SolidLine)

        ld_coef3 = QLabel('<h4>Set 3</h4>', self)
        ld_coef3.setStyleSheet('max-width: 3em;')
        lb_coef3 = PyDMLabel(self, self.dev_pref+':DESC_CSET3')
        lb_coef3.setStyleSheet('background-color: #DCDCDC;')
        led_coef3 = SiriusLedAlert(self, self.dev_pref+':CVERIFY.H')
        led_coef3.setStyleSheet('min-width: 1.29em; max-width: 1.29em;')

        graph_coef3 = WfmGraph(self)
        graph_coef3.add_scatter_curve(
            ychannel=self.dev_pref+':CSET3', lineStyle=Qt.SolidLine)

        gbox_coefview = QGroupBox('Coefficient Sets View', self)
        gbox_coefview.setLayout(QGridLayout())
        tab_coefview = QTabWidget(gbox_coefview)
        gbox_coefview.layout().addWidget(tab_coefview, 0, 0)

        norm_wid = QWidget(tab_coefview)
        tab_coefview.addTab(norm_wid, 'Normal')
        lay_norm = QGridLayout(norm_wid)
        lay_norm.addWidget(ld_coef0, 0, 0)
        lay_norm.addWidget(lb_coef0, 0, 1)
        lay_norm.addWidget(led_coef0, 0, 2)
        lay_norm.addWidget(graph_coef0, 1, 0, 1, 3)
        lay_norm.addWidget(ld_coef1, 2, 0)
        lay_norm.addWidget(lb_coef1, 2, 1)
        lay_norm.addWidget(led_coef1, 2, 2)
        lay_norm.addWidget(graph_coef1, 3, 0, 1, 3)

        alter_wid = QWidget(tab_coefview)
        tab_coefview.addTab(alter_wid, 'Alternate')
        lay_alter = QGridLayout(alter_wid)
        lay_alter.addWidget(ld_coef2, 0, 3)
        lay_alter.addWidget(lb_coef2, 0, 4)
        lay_alter.addWidget(led_coef2, 0, 5)
        lay_alter.addWidget(graph_coef2, 1, 3, 1, 3)
        lay_alter.addWidget(ld_coef3, 2, 3)
        lay_alter.addWidget(lb_coef3, 2, 4)
        lay_alter.addWidget(led_coef3, 2, 5)
        lay_alter.addWidget(graph_coef3, 3, 3, 1, 3)
        return gbox_coefview
