"""BbB Acquisition Module."""
import os as _os
from PyQt5.QtWidgets import QHBoxLayout

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor, QPixmap
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, QPushButton, \
    QGroupBox, QVBoxLayout, QSizePolicy as QSzPlcy, QSpacerItem
from pydm.widgets import PyDMLabel, PyDMSpinbox, PyDMEnumComboBox, \
    PyDMLineEdit

from siriuspy.envars import VACA_PREFIX as _vaca_prefix

from ..util import connect_window
from ..widgets import SiriusFrame, PyDMStateButton, SiriusLedState
from ..widgets.windows import create_window_from_widget

from .custom_widgets import WfmGraph
from .util import set_bbb_color, get_bbb_icon


class _BbBModalAnalysis(QWidget):
    """BbB Modal Analysis Widget."""

    def __init__(
            self, parent=None, prefix=_vaca_prefix, device='',
            acq_type='SRAM'):
        """Init."""
        super().__init__(parent)
        self._prefix = prefix
        self._device = device
        self.acq_type = acq_type
        self.dev_pref = prefix + device
        self.prop_pref = self.dev_pref + f':{acq_type:s}_'
        self.setObjectName('SIApp')
        self._setupUi()

    def _setupUi(self):
        gp_mode = WfmGraph(self)
        gp_mode.setStyleSheet('min-height: 10em;')
        gp_mode.setPlotTitle('Modal Amplitudes')
        gp_mode.getAxis('bottom').setLabel('Mode Number')
        gp_mode.getAxis('left').setLabel('CNT')
        gp_mode.add_scatter_curve(
            ychannel=self.prop_pref + 'MD_MODES',
            color=QColor('red'),
            lineStyle=Qt.SolidLine)

        gp_spec = WfmGraph(self)
        gp_spec.setStyleSheet('min-height: 10em;')
        gp_spec.setPlotTitle('Single Mode Spectrum')
        gp_spec.getAxis('bottom').setLabel('Frequency (kHz)')
        gp_spec.getAxis('left').setLabel('CNT')
        gp_spec.add_scatter_curve(
            ychannel=self.prop_pref+'MD_SPEC',
            xchannel=self.prop_pref+'FREQ',
            color=QColor('blue'),
            lineStyle=Qt.SolidLine)
        gp_spec.add_marker(
            name='Marker',
            xchannel=self.prop_pref+'MD_PEAKFREQ',
            ychannel=self.prop_pref+'MD_PEAK',
            color=QColor('red'), symbol='o')

        ld_enbl = QLabel('Acq. Enable', self)
        cb_enbl = PyDMStateButton(self, self.prop_pref+'MD_ENABLE')

        ld_sel = QLabel('Acq. Mode', self)
        cb_sel = PyDMEnumComboBox(self, self.prop_pref+'MD_SMODE')

        ld_sbnd = QLabel('Sideband', self, alignment=Qt.AlignRight)
        sb_sbnd = PyDMSpinbox(self, self.prop_pref+'MD_FTUNE')
        sb_sbnd.showStepExponent = False
        sb_sbnd.showUnits = True

        ld_span = QLabel('Span', self, alignment=Qt.AlignRight)
        sb_span = PyDMSpinbox(self, self.prop_pref+'MD_FSPAN')
        sb_span.showStepExponent = False
        sb_span.showUnits = True

        ld_mode = QLabel('Mode', self, alignment=Qt.AlignRight)
        sb_mode = PyDMSpinbox(self, self.prop_pref+'MD_MSEL')
        sb_mode.showStepExponent = False

        ld_avg = QLabel('Sample Avg', self, alignment=Qt.AlignRight)
        sb_avg = PyDMSpinbox(self, self.prop_pref+'MD_AVG')
        sb_avg.showStepExponent = False

        gb_ctrl = QGroupBox('Acquisition control', self)
        lay_ctrl = QGridLayout(gb_ctrl)
        lay_ctrl.addWidget(ld_enbl, 0, 0)
        lay_ctrl.addWidget(cb_enbl, 1, 0)
        lay_ctrl.addWidget(ld_sel, 2, 0)
        lay_ctrl.addWidget(cb_sel, 3, 0)
        lay_ctrl.addWidget(ld_sbnd, 0, 1)
        lay_ctrl.addWidget(sb_sbnd, 0, 2)
        lay_ctrl.addWidget(ld_span, 1, 1)
        lay_ctrl.addWidget(sb_span, 1, 2)
        lay_ctrl.addWidget(ld_mode, 2, 1)
        lay_ctrl.addWidget(sb_mode, 2, 2)
        lay_ctrl.addWidget(ld_avg, 3, 1)
        lay_ctrl.addWidget(sb_avg, 3, 2)

        # Markers
        ld_rng = QLabel('Range (kHz)', self, alignment=Qt.AlignCenter)
        le_low = PyDMLineEdit(self, self.prop_pref+'MD_SP_LOW')
        le_high = PyDMLineEdit(self, self.prop_pref+'MD_SP_HIGH')
        cb_mode = PyDMEnumComboBox(self, self.prop_pref+'MD_SP_SEARCH')

        ld_mnum = QLabel('Mode #', self, alignment=Qt.AlignRight)
        lb_mnum = PyDMLabel(self, self.prop_pref+'MD_MAXMODE')

        ld_mamp = QLabel('Mode Amp.', self, alignment=Qt.AlignRight)
        lb_mamp = PyDMLabel(self, self.prop_pref+'MD_MAXVAL')

        ld_peak = QLabel('Value', self, alignment=Qt.AlignRight)
        lb_peak = PyDMLabel(self, self.prop_pref+'MD_PEAK')

        ld_pfrq = QLabel('Freq', self, alignment=Qt.AlignRight)
        lb_pfrq = PyDMLabel(self, self.prop_pref+'MD_PEAKFREQ')
        lb_pfrq.showUnits = True

        ld_tune = QLabel('Tune', self, alignment=Qt.AlignRight)
        lb_tune = PyDMLabel(self, self.prop_pref+'MD_PEAKTUNE')

        gb_mark = QGroupBox('Marker', self)
        lay_mark = QGridLayout(gb_mark)
        lay_mark.addWidget(ld_rng, 0, 0)
        lay_mark.addWidget(le_low, 1, 0)
        lay_mark.addWidget(le_high, 2, 0)
        lay_mark.addWidget(cb_mode, 3, 0)
        lay_mark.addWidget(ld_mnum, 0, 1)
        lay_mark.addWidget(lb_mnum, 0, 2)
        lay_mark.addWidget(ld_mamp, 1, 1)
        lay_mark.addWidget(lb_mamp, 1, 2)
        lay_mark.addWidget(ld_peak, 2, 1)
        lay_mark.addWidget(lb_peak, 2, 2)
        lay_mark.addWidget(ld_pfrq, 3, 1)
        lay_mark.addWidget(lb_pfrq, 3, 2)
        lay_mark.addWidget(ld_tune, 4, 1)
        lay_mark.addWidget(lb_tune, 4, 2)

        ld_name = QLabel(
            '<h2>'+self.acq_type+' Modal Analysis</h2>', self,
            alignment=Qt.AlignCenter)

        self.setLayout(QHBoxLayout())
        wid = QWidget(self)
        self.layout().addWidget(wid)
        set_bbb_color(wid, self._device)
        lay = QGridLayout(wid)
        lay.addWidget(ld_name, 0, 0, 1, 2)
        lay.addWidget(gp_mode, 1, 0, 1, 2)
        lay.addWidget(gp_spec, 2, 0, 1, 2)
        lay.addWidget(gb_ctrl, 3, 0)
        lay.addWidget(gb_mark, 3, 1)
        lay.setRowStretch(1, 2)
        lay.setRowStretch(2, 2)


class _BbBAcqBase(QWidget):
    """BbB Acquisition Base Widget."""

    TYPE = ''

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        set_bbb_color(self, device)
        self._prefix = prefix
        self._device = device
        self.dev_pref = prefix + device
        self._setupUi()

    def _setupUi(self):
        ctrl_wid = self._setupControlsWidget()
        wfm_wid = self._setupWaveformsWidget()

        lay = QGridLayout(self)
        lay.addWidget(ctrl_wid, 0, 0)
        lay.addWidget(wfm_wid, 0, 1)

    def _setupControlsWidget(self):
        ld_growenbl = QLabel('Grow/Damp Enable', self)
        cb_growenbl = PyDMEnumComboBox(self, self.dev_pref+':GDEN')

        ld_down = QLabel('Rec. Downsample ', self)
        sb_down = PyDMSpinbox(self, self.dev_pref+':'+self.TYPE+'_REC_DS')
        sb_down.showStepExponent = False

        ld_rawdata = QLabel('Raw Data', self)
        cb_rawdata = PyDMStateButton(self, self.dev_pref+':'+self.TYPE+'_DUMP')

        ld_acqtime = QLabel('Acquisition Time', self)
        sb_acqtime = PyDMSpinbox(self, self.dev_pref+':'+self.TYPE+'_ACQTIME')
        sb_acqtime.showStepExponent = False
        sb_acqtime.showUnits = True

        ld_holdoff = QLabel('Hold-Off Time', self)
        sb_holdoff = PyDMSpinbox(self, self.dev_pref+':'+self.TYPE+'_HOLDTIME')
        sb_holdoff.showStepExponent = False
        sb_holdoff.showUnits = True

        ld_posttrg = QLabel('Post Trigger', self)
        sb_posttrg = PyDMSpinbox(self, self.dev_pref+':'+self.TYPE+'_POSTTIME')
        sb_posttrg.showStepExponent = False
        sb_posttrg.showUnits = True
        fr_posttrg = SiriusFrame(
            self, self.dev_pref+':'+self.TYPE+'_POSTREG_SUBWR')
        fr_posttrg.add_widget(sb_posttrg)

        ld_growtime = QLabel('Growth Time', self)
        sb_growtime = PyDMSpinbox(self, self.dev_pref+':'+self.TYPE+'_GDTIME')
        sb_growtime.showStepExponent = False
        sb_growtime.showUnits = True
        fr_growtime = SiriusFrame(
            self, self.dev_pref+':'+self.TYPE+'_GDREG_SUBWR')
        fr_growtime.add_widget(sb_growtime)

        ld_acqlen = QLabel('Acquisition Length', self)
        lb_acqlen = PyDMLabel(self, self.dev_pref+':'+self.TYPE+'_ACQ_TURNS')
        lb_acqlen.showUnits = True

        ld_psttrglen = QLabel('Post Trigger Length', self)
        lb_psttrglen = PyDMLabel(
            self, self.dev_pref+':'+self.TYPE+'_POST_TURNS')
        lb_psttrglen.showUnits = True

        bt_modal = QPushButton('Modal Analysis', self)

        window = create_window_from_widget(
            _BbBModalAnalysis, title='SRAM Modal Analysis',
            icon=get_bbb_icon(), is_main=True)
        connect_window(
            bt_modal, window, self, prefix=self._prefix,
            device=self._device, acq_type=self.TYPE)

        gbox_dtacq = QGroupBox('Data Acquisition', self)
        lay_dtacq = QGridLayout(gbox_dtacq)
        lay_dtacq.addWidget(ld_growenbl, 0, 0)
        lay_dtacq.addWidget(cb_growenbl, 0, 1)
        lay_dtacq.addWidget(ld_down, 1, 0)
        lay_dtacq.addWidget(sb_down, 1, 1)
        lay_dtacq.addWidget(ld_rawdata, 2, 0)
        lay_dtacq.addWidget(cb_rawdata, 2, 1)
        lay_dtacq.addWidget(ld_acqtime, 3, 0)
        lay_dtacq.addWidget(sb_acqtime, 3, 1)
        lay_dtacq.addWidget(ld_holdoff, 4, 0)
        lay_dtacq.addWidget(sb_holdoff, 4, 1)
        lay_dtacq.addWidget(ld_posttrg, 5, 0)
        lay_dtacq.addWidget(fr_posttrg, 5, 1)
        lay_dtacq.addWidget(ld_growtime, 6, 0)
        lay_dtacq.addWidget(fr_growtime, 6, 1)
        lay_dtacq.addWidget(ld_acqlen, 7, 0)
        lay_dtacq.addWidget(lb_acqlen, 7, 1)
        lay_dtacq.addWidget(ld_psttrglen, 8, 0)
        lay_dtacq.addWidget(lb_psttrglen, 8, 1)
        lay_dtacq.addWidget(bt_modal, 9, 0, 1, 2)

        ld_acqtyp = QLabel(
            '<h4>Acq Type</h4>', self, alignment=Qt.AlignCenter)
        cb_acqtyp = PyDMEnumComboBox(
            self, self.dev_pref+':'+self.TYPE+'_POSTSEL')

        gbox_acqtyp = QGroupBox(self)
        lay_acqtyp = QVBoxLayout(gbox_acqtyp)
        lay_acqtyp.addWidget(ld_acqtyp)
        lay_acqtyp.addWidget(cb_acqtyp)

        ld_trgexten = QLabel('Internal/External', self)
        cb_trgexten = PyDMEnumComboBox(
            self, self.dev_pref+':'+self.TYPE+'_HWTEN')

        ld_trginsel = QLabel('Selection', self)
        cb_trginsel = PyDMEnumComboBox(
            self, self.dev_pref+':'+self.TYPE+'_TRIG_IN_SEL')

        ld_trgarm = QLabel('Arm', self)
        cb_trgarm = PyDMStateButton(self, self.dev_pref+':'+self.TYPE+'_ARM')
        lb_armmon = SiriusLedState(
            self, self.dev_pref+':'+self.TYPE+'_ARM_MON')

        ld_trgbrarm = QLabel('Auto re-arm', self)
        cb_trgbrarm = PyDMStateButton(
            self, self.dev_pref+':'+self.TYPE+'_BR_ARM')

        ld_rst = QLabel('Trigger 1/2 Cap.:', self)
        lb_rst1 = PyDMLabel(self, self.dev_pref+':'+self.TYPE+'_CAP_TRIG1')
        lb_rst2 = PyDMLabel(self, self.dev_pref+':'+self.TYPE+'_CAP_TRIG2')

        gbox_trig = QGroupBox('Trigger', self)
        lay_trig = QGridLayout(gbox_trig)
        lay_trig.setAlignment(Qt.AlignTop)
        lay_trig.addWidget(ld_trgexten, 0, 0)
        lay_trig.addWidget(cb_trgexten, 0, 1, 1, 2)
        lay_trig.addWidget(ld_trginsel, 1, 0)
        lay_trig.addWidget(cb_trginsel, 1, 1, 1, 2)
        lay_trig.addWidget(ld_trgarm, 2, 0)
        lay_trig.addWidget(cb_trgarm, 2, 1)
        lay_trig.addWidget(lb_armmon, 2, 2)
        lay_trig.addWidget(ld_trgbrarm, 3, 0)
        lay_trig.addWidget(cb_trgbrarm, 3, 1)
        lay_trig.addWidget(ld_rst, 4, 0)
        lay_trig.addWidget(lb_rst1, 4, 1)
        lay_trig.addWidget(lb_rst2, 4, 2)
        lay_trig.setRowStretch(5, 2)

        pixmap = QPixmap(_os.path.join(
            _os.path.abspath(_os.path.dirname(__file__)), 'grow_damp.png'))
        img_wid = QLabel(self)
        img_wid.setPixmap(pixmap)
        img_wid.setScaledContents(True)

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(gbox_acqtyp, 0, 0)
        lay.addWidget(gbox_dtacq, 1, 0)
        lay.addWidget(gbox_trig, 2, 0)
        lay.addWidget(img_wid, 4, 0)
        lay.setRowStretch(3, 5)
        lay.setRowStretch(5, 5)

        wid.setStyleSheet("SiriusFrame{max-height: 1.8em;}")

        return wid

    def _setupWaveformsWidget(self):
        gp_mean = WfmGraph(self)
        gp_mean.setPlotTitle('Mean')
        gp_mean.getAxis('bottom').setLabel('Bunch number')
        gp_mean.getAxis('left').setLabel('CNT')
        gp_mean.add_scatter_curve(
            ychannel=self.dev_pref+':'+self.TYPE+'_MEAN',
            xchannel=self.dev_pref+':'+self.TYPE+'_XSC',
            color=QColor('red'),
            lineStyle=Qt.SolidLine)

        gp_maxrms = WfmGraph(self)
        gp_maxrms.setPlotTitle('Max RMS Channel (filtered)')
        gp_maxrms.getAxis('bottom').setLabel('Time (ms)')
        gp_maxrms.getAxis('left').setLabel('CNT')
        gp_maxrms.add_scatter_curve(
            ychannel=self.dev_pref+':'+self.TYPE+'_MAXRMS',
            xchannel=self.dev_pref+':'+self.TYPE+'_TSC',
            color=QColor('blue'),
            lineStyle=Qt.SolidLine)

        gp_rms = WfmGraph(self)
        gp_rms.setPlotTitle('RMS')
        gp_rms.getAxis('bottom').setLabel('Bunch number')
        gp_rms.getAxis('left').setLabel('CNT')
        gp_rms.add_scatter_curve(
            ychannel=self.dev_pref+':'+self.TYPE+'_RMS',
            xchannel=self.dev_pref+':'+self.TYPE+'_XSC',
            color=QColor('green'),
            lineStyle=Qt.SolidLine)

        gp_avgspe = WfmGraph(self)
        gp_avgspe.setPlotTitle('Average spectrum')
        gp_avgspe.getAxis('bottom').setLabel('Frequency (kHz)')
        gp_avgspe.getAxis('left').setLabel('dB')
        gp_avgspe.add_scatter_curve(
            ychannel=self.dev_pref+':'+self.TYPE+'_SPEC',
            xchannel=self.dev_pref+':'+self.TYPE+'_FREQ',
            color=QColor('blue'),
            lineStyle=Qt.SolidLine)
        gp_avgspe.add_marker(
            name='Marker 1',
            xchannel=self.dev_pref+':'+self.TYPE+'_PEAKFREQ1',
            ychannel=self.dev_pref+':'+self.TYPE+'_PEAK1',
            color=QColor('red'), symbol='o')
        gp_avgspe.add_marker(
            name='Marker 2',
            xchannel=self.dev_pref+':'+self.TYPE+'_PEAKFREQ2',
            ychannel=self.dev_pref+':'+self.TYPE+'_PEAK2',
            color=QColor('magenta'), symbol='s')

        lay_graph = QGridLayout()
        lay_graph.setContentsMargins(9, 9, 9, 9)
        lay_graph.addWidget(gp_mean, 0, 0)
        lay_graph.addWidget(gp_maxrms, 0, 1)
        lay_graph.addWidget(gp_rms, 1, 0)
        lay_graph.addWidget(gp_avgspe, 1, 1)

        ld_acqenbl = QLabel('Acq. Enable', self)
        cb_acqenbl = PyDMStateButton(
            self, self.dev_pref+':'+self.TYPE+'_ACQ_EN')

        ld_acqsing = QLabel('Acq. Mode', self)
        cb_acqsing = PyDMEnumComboBox(
            self, self.dev_pref+':'+self.TYPE+'_ACQ_SINGLE')

        ld_mean = QLabel('Mean', self, alignment=Qt.AlignCenter)
        lb_mean = PyDMLabel(self, self.dev_pref+':'+self.TYPE+'_MEANVAL')

        ld_rms = QLabel('RMS', self, alignment=Qt.AlignCenter)
        lb_rms = PyDMLabel(self, self.dev_pref+':'+self.TYPE+'_RMSVAL')

        ld_ampp2p = QLabel('Amp P-P', self, alignment=Qt.AlignCenter)
        lb_ampp2p = PyDMLabel(self, self.dev_pref+':'+self.TYPE+'_AMP_PP')

        ld_maxrms = QLabel('Max RMS', self, alignment=Qt.AlignCenter)
        lb_maxrms = PyDMLabel(self, self.dev_pref+':'+self.TYPE+'_MAXRMSVAL')

        ld_bunpatt = QLabel('Bunch\npattern', self)
        le_bunpatt = PyDMLineEdit(
            self, self.dev_pref+':'+self.TYPE+'_ACQ_PATTERN')

        ld_avg = QLabel('Sample Avg', self)
        sb_avg = PyDMSpinbox(self, self.dev_pref+':'+self.TYPE+'_SP_AVG')
        sb_avg.showStepExponent = False

        gbox_acqctrl = QGroupBox('Acquisition control', self)
        lay_acqctrl = QGridLayout(gbox_acqctrl)
        lay_acqctrl.addWidget(ld_acqenbl, 0, 0)
        lay_acqctrl.addWidget(cb_acqenbl, 0, 1)
        lay_acqctrl.addWidget(ld_acqsing, 1, 0)
        lay_acqctrl.addWidget(cb_acqsing, 1, 1)
        lay_acqctrl.addWidget(ld_avg, 2, 0)
        lay_acqctrl.addWidget(sb_avg, 2, 1)
        lay_acqctrl.addItem(
            QSpacerItem(15, 1, QSzPlcy.Fixed, QSzPlcy.Ignored), 0, 2, 3, 1)
        lay_acqctrl.addWidget(ld_mean, 0, 3)
        lay_acqctrl.addWidget(lb_mean, 0, 4)
        lay_acqctrl.addWidget(ld_ampp2p, 0, 5)
        lay_acqctrl.addWidget(lb_ampp2p, 0, 6)
        lay_acqctrl.addWidget(ld_rms, 1, 3)
        lay_acqctrl.addWidget(lb_rms, 1, 4)
        lay_acqctrl.addWidget(ld_maxrms, 1, 5)
        lay_acqctrl.addWidget(lb_maxrms, 1, 6)
        lay_acqctrl.addWidget(ld_bunpatt, 2, 3)
        lay_acqctrl.addWidget(le_bunpatt, 2, 4, 1, 3)

        # Markers
        ld_mk1 = QLabel('1', self, alignment=Qt.AlignCenter)
        ld_mk2 = QLabel('2', self, alignment=Qt.AlignCenter)
        ld_span = QLabel('Span (kHz)', self, alignment=Qt.AlignCenter)
        ld_mode = QLabel('Mode', self, alignment=Qt.AlignCenter)
        ld_val = QLabel('Value', self, alignment=Qt.AlignCenter)
        ld_pfrq = QLabel('Freq', self, alignment=Qt.AlignCenter)
        ld_tune = QLabel('Tune', self, alignment=Qt.AlignCenter)

        le_low1 = PyDMLineEdit(self, self.dev_pref+':'+self.TYPE+'_SP_LOW1')
        le_high1 = PyDMLineEdit(self, self.dev_pref+':'+self.TYPE+'_SP_HIGH1')
        cb_mode1 = PyDMEnumComboBox(
            self, self.dev_pref+':'+self.TYPE+'_SP_SEARCH1')
        lb_peak1 = PyDMLabel(self, self.dev_pref+':'+self.TYPE+'_PEAK1')
        lb_peak1.showUnits = True
        lb_pfrq1 = PyDMLabel(self, self.dev_pref+':'+self.TYPE+'_PEAKFREQ1')
        lb_pfrq1.showUnits = True
        lb_tune1 = PyDMLabel(self, self.dev_pref+':'+self.TYPE+'_PEAKTUNE1')

        le_low2 = PyDMLineEdit(self, self.dev_pref+':'+self.TYPE+'_SP_LOW2')
        le_high2 = PyDMLineEdit(self, self.dev_pref+':'+self.TYPE+'_SP_HIGH2')
        cb_mode2 = PyDMEnumComboBox(
            self, self.dev_pref+':'+self.TYPE+'_SP_SEARCH2')
        lb_peak2 = PyDMLabel(self, self.dev_pref+':'+self.TYPE+'_PEAK2')
        lb_peak2.showUnits = True
        lb_pfrq2 = PyDMLabel(self, self.dev_pref+':'+self.TYPE+'_PEAKFREQ2')
        lb_pfrq2.showUnits = True
        lb_tune2 = PyDMLabel(self, self.dev_pref+':'+self.TYPE+'_PEAKTUNE2')

        gbox_mark = QGroupBox('Markers', self)
        lay_mark = QGridLayout(gbox_mark)
        lay_mark.addWidget(ld_span, 0, 1, 1, 2)
        lay_mark.addWidget(ld_mode, 0, 3)
        lay_mark.addWidget(ld_val, 0, 4)
        lay_mark.addWidget(ld_pfrq, 0, 5)
        lay_mark.addWidget(ld_tune, 0, 6)
        lay_mark.addWidget(ld_mk1, 1, 0)
        lay_mark.addWidget(le_low1, 1, 1)
        lay_mark.addWidget(le_high1, 1, 2)
        lay_mark.addWidget(cb_mode1, 1, 3)
        lay_mark.addWidget(lb_peak1, 1, 4)
        lay_mark.addWidget(lb_pfrq1, 1, 5)
        lay_mark.addWidget(lb_tune1, 1, 6)
        lay_mark.addWidget(ld_mk2, 2, 0)
        lay_mark.addWidget(le_low2, 2, 1)
        lay_mark.addWidget(le_high2, 2, 2)
        lay_mark.addWidget(cb_mode2, 2, 3)
        lay_mark.addWidget(lb_peak2, 2, 4)
        lay_mark.addWidget(lb_pfrq2, 2, 5)
        lay_mark.addWidget(lb_tune2, 2, 6)

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addLayout(lay_graph, 0, 0, 1, 2)
        lay.addWidget(gbox_acqctrl, 1, 0)
        lay.addWidget(gbox_mark, 1, 1)
        lay.setRowStretch(0, 5)
        lay.setRowStretch(1, 1)
        lay.setColumnStretch(0, 1)
        lay.setColumnStretch(1, 1)
        return wid


class BbBAcqSRAM(_BbBAcqBase):
    """BbB SRAM Acquisition Widget."""

    TYPE = 'SRAM'


class BbBAcqBRAM(_BbBAcqBase):
    """BbB BRAM Acquisition Widget."""

    TYPE = 'BRAM'


class BbBAcqSB(QWidget):
    """BbB Tune Tracking Acquisition Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        set_bbb_color(self, device)
        self._prefix = prefix
        self._device = device
        self.dev_pref = prefix + device
        self._setupUi()

    def _setupUi(self):
        ctrl_wid = self._setupControlsWidget()
        wfm_wid = self._setupWaveformsWidget()
        lay = QGridLayout(self)
        lay.addWidget(ctrl_wid, 0, 0)
        lay.addWidget(wfm_wid, 0, 1)

    def _setupControlsWidget(self):
        ld_acqtime = QLabel('Acquisition Time [ms]', self)
        sb_acqtime = PyDMSpinbox(self, self.dev_pref+':SB_ACQTIME')
        sb_acqtime.showStepExponent = False

        ld_bunid = QLabel('Bunch Number', self)
        sb_bunid = PyDMSpinbox(self, self.dev_pref+':SB_BUNCH_ID')
        sb_bunid.showStepExponent = False

        ld_acqsmpl = QLabel('Acq Samples', self)
        lb_acqsmpl = PyDMLabel(self, self.dev_pref+':SB_ACQ_SAMPLES')

        ld_currbun = QLabel('Current Bunch', self)
        lb_currbun = PyDMLabel(self, self.dev_pref+':SB_RAW_BUNCH_ID')

        gbox_dtacq = QGroupBox('Data Acquisition', self)
        lay_dtacq = QGridLayout(gbox_dtacq)
        lay_dtacq.addWidget(ld_acqtime, 0, 0)
        lay_dtacq.addWidget(sb_acqtime, 0, 1)
        lay_dtacq.addWidget(ld_bunid, 1, 0)
        lay_dtacq.addWidget(sb_bunid, 1, 1)
        lay_dtacq.addWidget(ld_acqsmpl, 2, 0)
        lay_dtacq.addWidget(lb_acqsmpl, 2, 1)
        lay_dtacq.addWidget(ld_currbun, 3, 0)
        lay_dtacq.addWidget(lb_currbun, 3, 1)

        ld_trgexten = QLabel('Internal/External', self)
        cb_trgexten = PyDMEnumComboBox(self, self.dev_pref+':SB_EXTEN')

        ld_trginsel = QLabel('Selection', self)
        cb_trginsel = PyDMEnumComboBox(self, self.dev_pref+':SB_TRIG_IN_SEL')

        ld_trgarm = QLabel('Arm', self)
        cb_trgarm = PyDMStateButton(self, self.dev_pref+':SB_ARM')
        lb_armmon = SiriusLedState(self, self.dev_pref+':SB_ARM_MON')

        ld_trgbrarm = QLabel('Auto re-arm', self)
        cb_trgbrarm = PyDMStateButton(self, self.dev_pref+':SB_BR_ARM')

        gbox_trig = QGroupBox('Trigger', self)
        lay_trig = QGridLayout(gbox_trig)
        lay_trig.addWidget(ld_trgexten, 0, 0)
        lay_trig.addWidget(cb_trgexten, 0, 1, 1, 2)
        lay_trig.addWidget(ld_trginsel, 1, 0)
        lay_trig.addWidget(cb_trginsel, 1, 1, 1, 2)
        lay_trig.addWidget(ld_trgarm, 2, 0)
        lay_trig.addWidget(cb_trgarm, 2, 1)
        lay_trig.addWidget(lb_armmon, 2, 2)
        lay_trig.addWidget(ld_trgbrarm, 3, 0)
        lay_trig.addWidget(cb_trgbrarm, 3, 1)

        ld_phtrkctrl = QLabel(
            '<h4>Controls</h4>', self, alignment=Qt.AlignCenter)

        ld_bunnr = QLabel('Bunch Number', self)
        sb_bunnr = PyDMSpinbox(self, self.dev_pref+':SB_BUNCH_ID')
        sb_bunnr.showStepExponent = False

        ld_gain = QLabel('Gain', self)
        sb_gain = PyDMSpinbox(self, self.dev_pref+':PHTRK_GAIN')
        sb_gain.showStepExponent = False

        ld_sp = QLabel('Setpoint [deg]', self)
        sb_sp = PyDMSpinbox(self, self.dev_pref+':PHTRK_SETPT')
        sb_sp.showStepExponent = False

        ld_range = QLabel('Range [kHz]', self)
        sb_range = PyDMSpinbox(self, self.dev_pref+':PHTRK_RANGE')
        sb_range.showStepExponent = False

        ld_dec = QLabel('Decimation', self)
        sb_dec = PyDMSpinbox(self, self.dev_pref+':PHTRK_DECIM')
        sb_dec.showStepExponent = False

        ld_rate = QLabel('Rate', self)
        lb_rate = PyDMLabel(self, self.dev_pref+':PHTRK_RATE')
        lb_rate.showUnits = True

        ld_bw = QLabel('Bandwidth', self)
        lb_bw = PyDMLabel(self, self.dev_pref+':PHTRK_BANDWIDTH')
        lb_bw.showUnits = True

        ld_loopctrl = QLabel('Loop Control', self)
        cb_loopctrl = PyDMStateButton(self, self.dev_pref+':PHTRK_LOOPCTRL')

        ld_drv2 = QLabel('Use Drive 2', self)
        cb_drv2 = PyDMStateButton(self, self.dev_pref+':DRIVE2_TRACK')

        ld_mod = QLabel('Modulation', self)
        cb_mod = PyDMStateButton(self, self.dev_pref+':PHTRK_MOD')

        lay_phtrkctrl = QGridLayout()
        lay_phtrkctrl.addWidget(ld_phtrkctrl, 0, 0, 1, 2)
        lay_phtrkctrl.addWidget(ld_bunnr, 1, 0)
        lay_phtrkctrl.addWidget(sb_bunnr, 1, 1)
        lay_phtrkctrl.addWidget(ld_gain, 2, 0)
        lay_phtrkctrl.addWidget(sb_gain, 2, 1)
        lay_phtrkctrl.addWidget(ld_sp, 3, 0)
        lay_phtrkctrl.addWidget(sb_sp, 3, 1)
        lay_phtrkctrl.addWidget(ld_range, 4, 0)
        lay_phtrkctrl.addWidget(sb_range, 4, 1)
        lay_phtrkctrl.addWidget(ld_dec, 5, 0)
        lay_phtrkctrl.addWidget(sb_dec, 5, 1)
        lay_phtrkctrl.addWidget(ld_rate, 6, 0)
        lay_phtrkctrl.addWidget(lb_rate, 6, 1)
        lay_phtrkctrl.addWidget(ld_bw, 7, 0)
        lay_phtrkctrl.addWidget(lb_bw, 7, 1)
        lay_phtrkctrl.addWidget(ld_loopctrl, 8, 0)
        lay_phtrkctrl.addWidget(cb_loopctrl, 8, 1)
        lay_phtrkctrl.addWidget(ld_drv2, 9, 0)
        lay_phtrkctrl.addWidget(cb_drv2, 9, 1)
        lay_phtrkctrl.addWidget(ld_mod, 10, 0)
        lay_phtrkctrl.addWidget(cb_mod, 10, 1)

        ld_phtrkdata = QLabel(
            '<h4>Data</h4>', self, alignment=Qt.AlignCenter)

        ld_mag = QLabel('Magnitude', self)
        lb_mag = PyDMLabel(self, self.dev_pref+':PHTRK_MAG')
        lb_mag.showUnits = True

        ld_trgain = QLabel('Transfer Gain', self)
        lb_trgain = PyDMLabel(self, self.dev_pref+':PHTRK_TFGAIN')
        lb_trgain.showUnits = True

        ld_nshift = QLabel('Normalizing Shift', self)
        lb_nshift = PyDMLabel(self, self.dev_pref+':PHTRK_SHIFT')

        ld_phase = QLabel('Phase', self)
        lb_phase = PyDMLabel(self, self.dev_pref+':PHTRK_PHASE')
        lb_phase.showUnits = True

        ld_error = QLabel('Error', self)
        lb_error = PyDMLabel(self, self.dev_pref+':PHTRK_ERROR')
        lb_error.showUnits = True

        ld_trfreq = QLabel('Tracking Frequency', self)
        lb_trfreq = PyDMLabel(self, self.dev_pref+':PHTRK_FREQ0')
        lb_trfreq.showUnits = True

        ld_trtune = QLabel('Tracking Tune', self)
        lb_trtune = PyDMLabel(self, self.dev_pref+':PHTRK_TUNE')

        lay_phtrkdata = QGridLayout()
        lay_phtrkdata.addWidget(ld_phtrkdata, 0, 0, 1, 2)
        lay_phtrkdata.addWidget(ld_mag, 1, 0)
        lay_phtrkdata.addWidget(lb_mag, 1, 1)
        lay_phtrkdata.addWidget(ld_trgain, 2, 0)
        lay_phtrkdata.addWidget(lb_trgain, 2, 1)
        lay_phtrkdata.addWidget(ld_nshift, 3, 0)
        lay_phtrkdata.addWidget(lb_nshift, 3, 1)
        lay_phtrkdata.addWidget(ld_phase, 4, 0)
        lay_phtrkdata.addWidget(lb_phase, 4, 1)
        lay_phtrkdata.addWidget(ld_error, 5, 0)
        lay_phtrkdata.addWidget(lb_error, 5, 1)
        lay_phtrkdata.addWidget(ld_trfreq, 6, 0)
        lay_phtrkdata.addWidget(lb_trfreq, 6, 1)
        lay_phtrkdata.addWidget(ld_trtune, 7, 0)
        lay_phtrkdata.addWidget(lb_trtune, 7, 1)

        gbox_phtrk = QGroupBox('Phase Tracking', self)
        lay_phtrk = QGridLayout(gbox_phtrk)
        lay_phtrk.setHorizontalSpacing(20)
        lay_phtrk.addLayout(lay_phtrkctrl, 0, 0)
        lay_phtrk.addLayout(lay_phtrkdata, 1, 0)

        gbox_phtrk.setStyleSheet("""
            PyDMLabel{
                min-width: 6em; max-width: 6em;
            }""")

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.addWidget(gbox_dtacq, 0, 0)
        lay.addWidget(gbox_trig, 1, 0)
        lay.addWidget(gbox_phtrk, 2, 0)
        return wid

    def _setupWaveformsWidget(self):
        gp_bunsig = WfmGraph(self)
        gp_bunsig.setPlotTitle('Bunch Signal')
        gp_bunsig.getAxis('bottom').setLabel('Time (ms)')
        gp_bunsig.getAxis('left').setLabel('CNT')
        gp_bunsig.add_scatter_curve(
            ychannel=self.dev_pref+':SB_RAW',
            xchannel=self.dev_pref+':SB_TSC',
            color=QColor('blue'), lineStyle=Qt.SolidLine,
            nchannel=self.dev_pref+':SB_RAW_SAMPLES')

        gp_mag = WfmGraph(self)
        gp_mag.setPlotTitle('Magnitude')
        gp_mag.getAxis('bottom').setLabel('Frequency (kHz)')
        gp_mag.getAxis('left').setLabel('dB')
        gp_mag.add_scatter_curve(
            ychannel=self.dev_pref+':SB_MAG',
            xchannel=self.dev_pref+':SB_FREQ',
            color=QColor('blue'), lineStyle=Qt.SolidLine)
        gp_mag.add_marker(
            self.dev_pref+':SB_PEAKFREQ1',
            self.dev_pref+':SB_PEAK1',
            name='Mag', color=QColor('magenta'), symbol='o')

        gp_phs = WfmGraph(self)
        gp_phs.setPlotTitle('Phase')
        gp_phs.getAxis('bottom').setLabel('Frequency (kHz)')
        gp_phs.getAxis('left').setLabel('deg')
        gp_phs.add_scatter_curve(
            ychannel=self.dev_pref+':SB_PHASE',
            xchannel=self.dev_pref+':SB_FREQ',
            color=QColor('blue'), lineStyle=Qt.SolidLine)
        gp_phs.add_marker(
            self.dev_pref+':SB_PEAKFREQ1',
            self.dev_pref+':SB_PHASE1',
            name='Phs', color=QColor('magenta'), symbol='o')

        ld_tfenbl = QLabel('Transfer Function Enable', self)
        cb_tfenbl = PyDMEnumComboBox(self, self.dev_pref+':SB_TF_ENABLE')

        ld_nrptsfft = QLabel('Number of points for FFT/Window', self)
        cb_nrptsfft = PyDMEnumComboBox(self, self.dev_pref+':SB_NFFT')

        ld_fftovlap = QLabel('Overlap (Autolimited to NFFT/2)', self)
        cb_fftovlap = PyDMEnumComboBox(
            self, self.dev_pref+':SB_NOVERLAP')

        ld_delaycal = QLabel('Delay Cal [ns]', self)
        le_delaycal = PyDMLineEdit(self, self.dev_pref+':SB_DEL_CAL')

        ld_avg = QLabel('Averaging', self)
        sb_avg = PyDMSpinbox(self, self.dev_pref+':SB_SP_AVG')
        sb_avg.showStepExponent = False

        gbox_fftsett = QGroupBox(self)
        lay_fftsett = QGridLayout(gbox_fftsett)
        lay_fftsett.addWidget(ld_tfenbl, 0, 0)
        lay_fftsett.addWidget(cb_tfenbl, 0, 1)
        lay_fftsett.addWidget(ld_nrptsfft, 1, 0)
        lay_fftsett.addWidget(cb_nrptsfft, 1, 1)
        lay_fftsett.addWidget(ld_fftovlap, 2, 0)
        lay_fftsett.addWidget(cb_fftovlap, 2, 1)
        lay_fftsett.addWidget(ld_delaycal, 3, 0)
        lay_fftsett.addWidget(le_delaycal, 3, 1)
        lay_fftsett.addWidget(ld_avg, 4, 0)
        lay_fftsett.addWidget(sb_avg, 4, 1)

        lay_graph = QGridLayout()
        lay_graph.addWidget(gp_bunsig, 0, 0)
        lay_graph.addWidget(gp_mag, 0, 1)
        lay_graph.addWidget(gbox_fftsett, 1, 0)
        lay_graph.addWidget(gp_phs, 1, 1)

        ld_acqenbl = QLabel('Acq. Enable', self)
        cb_acqenbl = PyDMStateButton(self, self.dev_pref+':SB_ACQ_EN')

        ld_acqsing = QLabel('Acq. Mode', self)
        cb_acqsing = PyDMEnumComboBox(self, self.dev_pref+':SB_ACQ_SINGLE')

        ld_mean = QLabel('Mean', self, alignment=Qt.AlignCenter)
        lb_mean = PyDMLabel(self, self.dev_pref+':SB_MEANVAL')

        ld_rms = QLabel('RMS', self, alignment=Qt.AlignCenter)
        lb_rms = PyDMLabel(self, self.dev_pref+':SB_RMSVAL')

        ld_ampp2p = QLabel('Amp P-P', self, alignment=Qt.AlignCenter)
        lb_ampp2p = PyDMLabel(self, self.dev_pref+':SB_AMP_PP')

        ld_bunid = QLabel('Bunch ID', self, alignment=Qt.AlignCenter)
        lb_bunid = PyDMLabel(self, self.dev_pref+':SB_RAW_BUNCH_ID')

        gbox_acqctrl = QGroupBox('Acquisition control', self)
        lay_acqctrl = QGridLayout(gbox_acqctrl)
        lay_acqctrl.addWidget(ld_acqenbl, 0, 0)
        lay_acqctrl.addWidget(cb_acqenbl, 0, 1)
        lay_acqctrl.addWidget(ld_acqsing, 1, 0)
        lay_acqctrl.addWidget(cb_acqsing, 1, 1)
        lay_acqctrl.addItem(
            QSpacerItem(15, 1, QSzPlcy.Fixed, QSzPlcy.Ignored), 0, 2, 2, 1)
        lay_acqctrl.addWidget(ld_mean, 0, 3)
        lay_acqctrl.addWidget(lb_mean, 0, 4)
        lay_acqctrl.addWidget(ld_ampp2p, 0, 5)
        lay_acqctrl.addWidget(lb_ampp2p, 0, 6)
        lay_acqctrl.addWidget(ld_rms, 1, 3)
        lay_acqctrl.addWidget(lb_rms, 1, 4)
        lay_acqctrl.addWidget(ld_bunid, 1, 5)
        lay_acqctrl.addWidget(lb_bunid, 1, 6)

        # Marker
        ld_mkspan = QLabel('Span (kHz)', self, alignment=Qt.AlignCenter)
        le_mklow = PyDMLineEdit(self, self.dev_pref+':SB_SP_LOW1')
        le_mkhigh = PyDMLineEdit(self, self.dev_pref+':SB_SP_HIGH1')

        ld_mkmode = QLabel('Mode', self, alignment=Qt.AlignCenter)
        cb_mkmode = PyDMEnumComboBox(self, self.dev_pref+':SB_SP_SEARCH1')

        ld_mkfreq = QLabel('Frequency', self, alignment=Qt.AlignCenter)
        lb_mkfreq = PyDMLabel(self, self.dev_pref+':SB_PEAKFREQ1')
        lb_mkfreq.showUnits = True

        ld_mktune = QLabel('Tune', self, alignment=Qt.AlignCenter)
        lb_mktune = PyDMLabel(self, self.dev_pref+':SB_PEAKTUNE1')
        lb_mktune.showUnits = True

        ld_mkmag = QLabel('Magnitude', self, alignment=Qt.AlignCenter)
        lb_mkmag = PyDMLabel(self, self.dev_pref+':SB_PEAK1')
        lb_mkmag.showUnits = True

        ld_mkphs = QLabel('Phase', self, alignment=Qt.AlignCenter)
        lb_mkphs = PyDMLabel(self, self.dev_pref+':SB_PHASE1')
        lb_mkphs.showUnits = True

        lay = QGridLayout()
        lay.addWidget(ld_mkfreq, 1, 0)
        lay.addWidget(lb_mkfreq, 2, 0)
        lay.addWidget(ld_mktune, 1, 1)
        lay.addWidget(lb_mktune, 2, 1)
        lay.addWidget(ld_mkmag, 1, 2)
        lay.addWidget(lb_mkmag, 2, 2)
        lay.addWidget(ld_mkphs, 1, 3)
        lay.addWidget(lb_mkphs, 2, 3)
        lay.setRowStretch(0, 2)
        lay.setRowStretch(3, 2)

        gbox_mk = QGroupBox('Marker', self)
        lay_mk = QGridLayout(gbox_mk)
        lay_mk.addWidget(ld_mkmode, 0, 0)
        lay_mk.addWidget(cb_mkmode, 0, 1)
        lay_mk.addWidget(ld_mkspan, 1, 0, 1, 2)
        lay_mk.addWidget(le_mklow, 2, 0)
        lay_mk.addWidget(le_mkhigh, 2, 1)
        lay_mk.addLayout(lay, 0, 2, 3, 1)

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.addLayout(lay_graph, 0, 0, 1, 2)
        lay.addWidget(gbox_acqctrl, 1, 0)
        lay.addWidget(gbox_mk, 1, 1)
        lay.setRowStretch(0, 5)
        lay.setRowStretch(1, 1)
        lay.setColumnStretch(0, 1)
        lay.setColumnStretch(1, 1)
        return wid
