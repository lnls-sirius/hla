"""BbB Acquisition Module."""

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, \
    QGroupBox, QTabWidget, QVBoxLayout, QSizePolicy as QSzPlcy, \
    QSpacerItem

from pydm.widgets import PyDMLabel, PyDMSpinbox, PyDMEnumComboBox, \
    PyDMLineEdit

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriushla.widgets import SiriusFrame
from .custom_widgets import WfmGraph


class _BbBAcqBase(QTabWidget):
    """BbB Acquisition Base Widget."""

    TYPE = ''

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        self.setObjectName('SIApp')
        self._prefix = prefix
        self._device = device
        self.dev_pref = prefix + device
        self._setupUi()

    def _setupUi(self):
        self.addTab(self._setupControlsWidget(), 'Controls')
        self.addTab(self._setupWaveformsWidget(), 'Waveforms')

    def _setupControlsWidget(self):
        self._ld_growenbl = QLabel('Grow/Damp Enable', self)
        self._cb_growenbl = PyDMEnumComboBox(self, self.dev_pref+':GDEN')

        self._ld_down = QLabel('Rec. Downsample ', self)
        self._sb_down = PyDMSpinbox(
            self, self.dev_pref+':'+self.TYPE+'_REC_DS')
        self._sb_down.showStepExponent = False

        self._ld_rawdata = QLabel('Raw Data', self)
        self._cb_rawdata = PyDMEnumComboBox(
            self, self.dev_pref+':'+self.TYPE+'_DUMP')

        self._ld_acqtime = QLabel('Acquisition Time [ms]', self)
        self._sb_acqtime = PyDMSpinbox(
            self, self.dev_pref+':'+self.TYPE+'_ACQTIME')
        self._sb_acqtime.showStepExponent = False

        self._ld_holdoff = QLabel('Hold-Off Time [ms]', self)
        self._sb_holdoff = PyDMSpinbox(
            self, self.dev_pref+':'+self.TYPE+'_HOLDTIME')
        self._sb_holdoff.showStepExponent = False

        self._ld_posttrg = QLabel('Post Trigger [ms]', self)
        self._sb_posttrg = PyDMSpinbox(
            self, self.dev_pref+':'+self.TYPE+'_POSTTIME')
        self._sb_posttrg.showStepExponent = False
        self._fr_posttrg = SiriusFrame(
            self, self.dev_pref+':'+self.TYPE+'_POSTREG_SUBWR')
        self._fr_posttrg.add_widget(self._sb_posttrg)

        self._ld_growtime = QLabel('Growth Time [ms]', self)
        self._sb_growtime = PyDMSpinbox(
            self, self.dev_pref+':'+self.TYPE+'_GDTIME')
        self._sb_growtime.showStepExponent = False
        self._fr_growtime = SiriusFrame(
            self, self.dev_pref+':'+self.TYPE+'_GDREG_SUBWR')
        self._fr_growtime.add_widget(self._sb_growtime)

        self._ld_acqlen = QLabel('Acquisition Length', self)
        self._lb_acqlen = PyDMLabel(
            self, self.dev_pref+':'+self.TYPE+'_ACQ_TURNS')
        self._lb_acqlen.showUnits = True

        self._ld_psttrglen = QLabel('Post Trigger Length', self)
        self._lb_psttrglen = PyDMLabel(
            self, self.dev_pref+':'+self.TYPE+'_POST_TURNS')
        self._lb_psttrglen.showUnits = True

        gbox_dtacq = QGroupBox('Data Acquisition', self)
        lay_dtacq = QGridLayout(gbox_dtacq)
        lay_dtacq.addWidget(self._ld_growenbl, 0, 0)
        lay_dtacq.addWidget(self._cb_growenbl, 0, 1)
        lay_dtacq.addWidget(self._ld_down, 1, 0)
        lay_dtacq.addWidget(self._sb_down, 1, 1)
        lay_dtacq.addWidget(self._ld_rawdata, 2, 0)
        lay_dtacq.addWidget(self._cb_rawdata, 2, 1)
        lay_dtacq.addWidget(self._ld_acqtime, 3, 0)
        lay_dtacq.addWidget(self._sb_acqtime, 3, 1)
        lay_dtacq.addWidget(self._ld_holdoff, 4, 0)
        lay_dtacq.addWidget(self._sb_holdoff, 4, 1)
        lay_dtacq.addWidget(self._ld_posttrg, 5, 0)
        lay_dtacq.addWidget(self._fr_posttrg, 5, 1)
        lay_dtacq.addWidget(self._ld_growtime, 6, 0)
        lay_dtacq.addWidget(self._fr_growtime, 6, 1)
        lay_dtacq.addWidget(self._ld_acqlen, 7, 0)
        lay_dtacq.addWidget(self._lb_acqlen, 7, 1)
        lay_dtacq.addWidget(self._ld_psttrglen, 8, 0)
        lay_dtacq.addWidget(self._lb_psttrglen, 8, 1)

        self._ld_acqtyp = QLabel(
            '<h4>Acq Type</h4>', self, alignment=Qt.AlignCenter)
        self._cb_acqtyp = PyDMEnumComboBox(
            self, self.dev_pref+':'+self.TYPE+'_POSTSEL')

        gbox_acqtyp = QGroupBox(self)
        lay_acqtyp = QVBoxLayout(gbox_acqtyp)
        lay_acqtyp.addWidget(self._ld_acqtyp)
        lay_acqtyp.addWidget(self._cb_acqtyp)

        self._ld_trgexten = QLabel('Internal/External', self)
        self._cb_trgexten = PyDMEnumComboBox(
            self, self.dev_pref+':'+self.TYPE+'_EXTEN')

        self._ld_trginsel = QLabel('Selection', self)
        self._cb_trginsel = PyDMEnumComboBox(
            self, self.dev_pref+':'+self.TYPE+'_TRIG_IN_SEL')

        self._ld_trgarm = QLabel('Arm', self)
        self._cb_trgarm = PyDMEnumComboBox(
            self, self.dev_pref+':'+self.TYPE+'_ARM')

        self._ld_trgbrarm = QLabel('Auto re-arm', self)
        self._cb_trgbrarm = PyDMEnumComboBox(
            self, self.dev_pref+':'+self.TYPE+'_BR_ARM')

        self._ld_rst = QLabel('Arm Mon.', self)
        self._lb_armmon = PyDMLabel(
            self, self.dev_pref+':'+self.TYPE+'_ARM_MON')
        self._lb_rst1 = PyDMLabel(
            self, self.dev_pref+':'+self.TYPE+'_CAP_TRIG1')
        self._lb_rst2 = PyDMLabel(
            self, self.dev_pref+':'+self.TYPE+'_CAP_TRIG2')

        gbox_trig = QGroupBox('Trigger', self)
        lay_trig = QGridLayout(gbox_trig)
        lay_trig.setAlignment(Qt.AlignTop)
        lay_trig.addWidget(self._ld_trgexten, 0, 0)
        lay_trig.addWidget(self._cb_trgexten, 0, 1, 1, 3)
        lay_trig.addWidget(self._ld_trginsel, 1, 0)
        lay_trig.addWidget(self._cb_trginsel, 1, 1, 1, 3)
        lay_trig.addWidget(self._ld_trgarm, 2, 0)
        lay_trig.addWidget(self._cb_trgarm, 2, 1, 1, 3)
        lay_trig.addWidget(self._ld_trgbrarm, 3, 0)
        lay_trig.addWidget(self._cb_trgbrarm, 3, 1, 1, 3)
        lay_trig.addWidget(self._ld_rst, 4, 0)
        lay_trig.addWidget(self._lb_armmon, 4, 1)
        lay_trig.addWidget(self._lb_rst1, 4, 2)
        lay_trig.addWidget(self._lb_rst2, 4, 3)
        gbox_trig.setSizePolicy(QSzPlcy.Preferred, QSzPlcy.Expanding)

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(gbox_dtacq, 0, 0, 2, 1)
        lay.addWidget(gbox_acqtyp, 0, 1)
        lay.addWidget(gbox_trig, 1, 1)
        lay.addItem(QSpacerItem(
            10, 10, QSzPlcy.MinimumExpanding, QSzPlcy.MinimumExpanding), 2, 2)

        wid.setStyleSheet("SiriusFrame{max-height: 1.8em;}")

        return wid

    def _setupWaveformsWidget(self):
        self._graph_mean = WfmGraph(self)
        self._graph_mean.setPlotTitle('Mean')
        self._graph_mean.getAxis('bottom').setLabel('Bunch number')
        self._graph_mean.getAxis('left').setLabel('CNT')
        self._graph_mean.add_scatter_curve(
            self.dev_pref+':'+self.TYPE+'_MEAN', color=QColor('red'))

        self._graph_maxrms = WfmGraph(self)
        self._graph_maxrms.setPlotTitle('Max RMS Channel (filtered)')
        self._graph_maxrms.getAxis('bottom').setLabel('Time (ms)')
        self._graph_maxrms.getAxis('left').setLabel('CNT')
        self._graph_maxrms.add_scatter_curve(
            self.dev_pref+':'+self.TYPE+'_MAXRMS', color=QColor('blue'))

        self._graph_rms = WfmGraph(self)
        self._graph_rms.setPlotTitle('RMS')
        self._graph_rms.getAxis('bottom').setLabel('Bunch number')
        self._graph_rms.getAxis('left').setLabel('CNT')
        self._graph_rms.add_scatter_curve(
            self.dev_pref+':'+self.TYPE+'_RMS', color=QColor('green'))

        self._graph_avgspe = WfmGraph(self)
        self._graph_avgspe.setPlotTitle('Average spectrum')
        self._graph_avgspe.getAxis('bottom').setLabel('Frequency (kHz)')
        self._graph_avgspe.getAxis('left').setLabel('dB')
        self._graph_avgspe.add_scatter_curve(
            self.dev_pref+':'+self.TYPE+'_SPEC', color=QColor('blue'))
        self._graph_avgspe.add_marker(
            name='Marker 1',
            x_channel=self.dev_pref+':'+self.TYPE+'_PEAKFREQ1',
            y_channel=self.dev_pref+':'+self.TYPE+'_PEAK1',
            color=QColor('red'), symbol='o')
        self._graph_avgspe.add_marker(
            name='Marker 2',
            x_channel=self.dev_pref+':'+self.TYPE+'_PEAKFREQ2',
            y_channel=self.dev_pref+':'+self.TYPE+'_PEAK2',
            color=QColor('magenta'), symbol='s')

        lay_graph = QGridLayout()
        lay_graph.setContentsMargins(9, 9, 9, 9)
        lay_graph.addWidget(self._graph_mean, 0, 0)
        lay_graph.addWidget(self._graph_maxrms, 0, 1)
        lay_graph.addWidget(self._graph_rms, 1, 0)
        lay_graph.addWidget(self._graph_avgspe, 1, 1)

        self._ld_acqenbl = QLabel('Acq. Enable', self)
        self._cb_acqenbl = PyDMEnumComboBox(
            self, self.dev_pref+':'+self.TYPE+'_ACQ_EN')

        self._ld_acqsing = QLabel('Acq. Mode', self)
        self._cb_acqsing = PyDMEnumComboBox(
            self, self.dev_pref+':'+self.TYPE+'_ACQ_SINGLE')

        self._ld_mean = QLabel(
            'Mean', self, alignment=Qt.AlignCenter)
        self._lb_mean = PyDMLabel(self, self.dev_pref+':'+self.TYPE+'_MEANVAL')

        self._ld_rms = QLabel(
            'RMS', self, alignment=Qt.AlignCenter)
        self._lb_rms = PyDMLabel(self, self.dev_pref+':'+self.TYPE+'_RMSVAL')

        self._ld_ampp2p = QLabel(
            'Amp P-P', self, alignment=Qt.AlignCenter)
        self._lb_ampp2p = PyDMLabel(
            self, self.dev_pref+':'+self.TYPE+'_AMP_PP')

        self._ld_maxrms = QLabel(
            'Max RMS', self, alignment=Qt.AlignCenter)
        self._lb_maxrms = PyDMLabel(
            self, self.dev_pref+':'+self.TYPE+'_MAXRMSVAL')

        self._ld_bunpatt = QLabel('Bunch\npattern', self)
        self._le_bunpatt = PyDMLineEdit(
            self, self.dev_pref+':'+self.TYPE+'_ACQ_PATTERN')

        self._ld_avg = QLabel('Sample Avg', self)
        self._sb_avg = PyDMSpinbox(self, self.dev_pref+':'+self.TYPE+'_SP_AVG')
        self._sb_avg.showStepExponent = False

        gbox_acqctrl = QGroupBox('Acquisition control', self)
        lay_acqctrl = QGridLayout(gbox_acqctrl)
        lay_acqctrl.addWidget(self._ld_acqenbl, 0, 0)
        lay_acqctrl.addWidget(self._cb_acqenbl, 0, 1)
        lay_acqctrl.addWidget(self._ld_acqsing, 1, 0)
        lay_acqctrl.addWidget(self._cb_acqsing, 1, 1)
        lay_acqctrl.addWidget(self._ld_avg, 2, 0)
        lay_acqctrl.addWidget(self._sb_avg, 2, 1)
        lay_acqctrl.addItem(
            QSpacerItem(15, 1, QSzPlcy.Fixed, QSzPlcy.Ignored), 0, 2, 3, 1)
        lay_acqctrl.addWidget(self._ld_mean, 0, 3)
        lay_acqctrl.addWidget(self._lb_mean, 0, 4)
        lay_acqctrl.addWidget(self._ld_ampp2p, 0, 5)
        lay_acqctrl.addWidget(self._lb_ampp2p, 0, 6)
        lay_acqctrl.addWidget(self._ld_rms, 1, 3)
        lay_acqctrl.addWidget(self._lb_rms, 1, 4)
        lay_acqctrl.addWidget(self._ld_maxrms, 1, 5)
        lay_acqctrl.addWidget(self._lb_maxrms, 1, 6)
        lay_acqctrl.addWidget(self._ld_bunpatt, 2, 3)
        lay_acqctrl.addWidget(self._le_bunpatt, 2, 4, 1, 3)

        # Markers
        self._ld_mk1 = QLabel('1', self, alignment=Qt.AlignCenter)
        self._ld_mk2 = QLabel('2', self, alignment=Qt.AlignCenter)
        self._ld_span = QLabel('Span (kHz)', self, alignment=Qt.AlignCenter)
        self._ld_mode = QLabel('Mode', self, alignment=Qt.AlignCenter)
        self._ld_val = QLabel('Value', self, alignment=Qt.AlignCenter)
        self._ld_freq = QLabel('Freq', self, alignment=Qt.AlignCenter)

        self._le_low1 = PyDMLineEdit(
            self, self.dev_pref+':'+self.TYPE+'_SP_LOW1')
        self._le_high1 = PyDMLineEdit(
            self, self.dev_pref+':'+self.TYPE+'_SP_HIGH1')
        self._cb_mode1 = PyDMEnumComboBox(
            self, self.dev_pref+':'+self.TYPE+'_SP_SEARCH1')
        self._lb_peak1 = PyDMLabel(self, self.dev_pref+':'+self.TYPE+'_PEAK1')
        self._lb_peak1.showUnits = True
        self._lb_pfrq1 = PyDMLabel(
            self, self.dev_pref+':'+self.TYPE+'_PEAKFREQ1')
        self._lb_pfrq1.showUnits = True

        self._le_low2 = PyDMLineEdit(
            self, self.dev_pref+':'+self.TYPE+'_SP_LOW2')
        self._le_high2 = PyDMLineEdit(
            self, self.dev_pref+':'+self.TYPE+'_SP_HIGH2')
        self._cb_mode2 = PyDMEnumComboBox(
            self, self.dev_pref+':'+self.TYPE+'_SP_SEARCH2')
        self._lb_peak2 = PyDMLabel(self, self.dev_pref+':'+self.TYPE+'_PEAK2')
        self._lb_peak2.showUnits = True
        self._lb_pfrq2 = PyDMLabel(
            self, self.dev_pref+':'+self.TYPE+'_PEAKFREQ2')
        self._lb_pfrq2.showUnits = True

        gbox_mark = QGroupBox('Markers', self)
        lay_mark = QGridLayout(gbox_mark)
        lay_mark.addWidget(self._ld_span, 0, 1, 1, 2)
        lay_mark.addWidget(self._ld_mode, 0, 3)
        lay_mark.addWidget(self._ld_val, 0, 4)
        lay_mark.addWidget(self._ld_freq, 0, 5)
        lay_mark.addWidget(self._ld_mk1, 1, 0)
        lay_mark.addWidget(self._le_low1, 1, 1)
        lay_mark.addWidget(self._le_high1, 1, 2)
        lay_mark.addWidget(self._cb_mode1, 1, 3)
        lay_mark.addWidget(self._lb_peak1, 1, 4)
        lay_mark.addWidget(self._lb_pfrq1, 1, 5)
        lay_mark.addWidget(self._ld_mk2, 2, 0)
        lay_mark.addWidget(self._le_low2, 2, 1)
        lay_mark.addWidget(self._le_high2, 2, 2)
        lay_mark.addWidget(self._cb_mode2, 2, 3)
        lay_mark.addWidget(self._lb_peak2, 2, 4)
        lay_mark.addWidget(self._lb_pfrq2, 2, 5)

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


class BbBAcqSB(QTabWidget):
    """BbB SB Acquisition Widget."""

    def __init__(self, parent=None, prefix=_vaca_prefix, device=''):
        """Init."""
        super().__init__(parent)
        self.setObjectName('SIApp')
        self._prefix = prefix
        self._device = device
        self.dev_pref = prefix + device
        self._setupUi()

    def _setupUi(self):
        self.addTab(self._setupControlsWidget(), 'Controls')
        self.addTab(self._setupWaveformsWidget(), 'Waveforms')

    def _setupControlsWidget(self):
        self._ld_acqtime = QLabel('Acquisition Time [ms]', self)
        self._sb_acqtime = PyDMSpinbox(self, self.dev_pref+':SB_ACQTIME')
        self._sb_acqtime.showStepExponent = False

        self._ld_bunid = QLabel('Bunch Number', self)
        self._sb_bunid = PyDMSpinbox(self, self.dev_pref+':SB_BUNCH_ID')
        self._sb_bunid.showStepExponent = False

        self._ld_acqsmpl = QLabel('Acq Samples', self)
        self._lb_acqsmpl = PyDMLabel(self, self.dev_pref+':SB_ACQ_SAMPLES')

        self._ld_currbun = QLabel('Current Bunch', self)
        self._lb_currbun = PyDMLabel(self, self.dev_pref+':SB_RAW_BUNCH_ID')

        gbox_dtacq = QGroupBox('Data Acquisition', self)
        lay_dtacq = QGridLayout(gbox_dtacq)
        lay_dtacq.addWidget(self._ld_acqtime, 0, 0)
        lay_dtacq.addWidget(self._sb_acqtime, 0, 1)
        lay_dtacq.addWidget(self._ld_bunid, 1, 0)
        lay_dtacq.addWidget(self._sb_bunid, 1, 1)
        lay_dtacq.addWidget(self._ld_acqsmpl, 2, 0)
        lay_dtacq.addWidget(self._lb_acqsmpl, 2, 1)
        lay_dtacq.addWidget(self._ld_currbun, 3, 0)
        lay_dtacq.addWidget(self._lb_currbun, 3, 1)

        self._ld_trgexten = QLabel('Internal/External', self)
        self._cb_trgexten = PyDMEnumComboBox(self, self.dev_pref+':SB_EXTEN')

        self._ld_trginsel = QLabel('Selection', self)
        self._cb_trginsel = PyDMEnumComboBox(
            self, self.dev_pref+':SB_TRIG_IN_SEL')

        self._ld_trgarm = QLabel('Arm', self)
        self._cb_trgarm = PyDMEnumComboBox(self, self.dev_pref+':SB_ARM')

        self._ld_trgbrarm = QLabel('Auto re-arm', self)
        self._cb_trgbrarm = PyDMEnumComboBox(self, self.dev_pref+':SB_BR_ARM')

        self._ld_armmon = QLabel('Arm Mon.', self)
        self._lb_armmon = PyDMLabel(self, self.dev_pref+':SB_ARM_MON')

        gbox_trig = QGroupBox('Trigger', self)
        lay_trig = QGridLayout(gbox_trig)
        lay_trig.addWidget(self._ld_trgexten, 0, 0)
        lay_trig.addWidget(self._cb_trgexten, 0, 1)
        lay_trig.addWidget(self._ld_trginsel, 1, 0)
        lay_trig.addWidget(self._cb_trginsel, 1, 1)
        lay_trig.addWidget(self._ld_trgarm, 2, 0)
        lay_trig.addWidget(self._cb_trgarm, 2, 1)
        lay_trig.addWidget(self._ld_trgbrarm, 3, 0)
        lay_trig.addWidget(self._cb_trgbrarm, 3, 1)
        lay_trig.addWidget(self._ld_armmon, 4, 0)
        lay_trig.addWidget(self._lb_armmon, 4, 1)

        self._ld_phtrkctrl = QLabel(
            '<h4>Controls</h4>', self, alignment=Qt.AlignCenter)

        self._ld_bunnr = QLabel('Bunch Number', self)
        self._sb_bunnr = PyDMSpinbox(self, self.dev_pref+':SB_BUNCH_ID')
        self._sb_bunnr.showStepExponent = False

        self._ld_gain = QLabel('Gain', self)
        self._sb_gain = PyDMSpinbox(self, self.dev_pref+':PHTRK_GAIN')
        self._sb_gain.showStepExponent = False

        self._ld_sp = QLabel('Setpoint [deg]', self)
        self._sb_sp = PyDMSpinbox(self, self.dev_pref+':PHTRK_SETPT')
        self._sb_sp.showStepExponent = False

        self._ld_range = QLabel('Range [kHz]', self)
        self._sb_range = PyDMSpinbox(self, self.dev_pref+':PHTRK_RANGE')
        self._sb_range.showStepExponent = False

        self._ld_dec = QLabel('Decimation', self)
        self._sb_dec = PyDMSpinbox(self, self.dev_pref+':PHTRK_DECIM')
        self._sb_dec.showStepExponent = False

        self._ld_rate = QLabel('Rate', self)
        self._lb_rate = PyDMLabel(self, self.dev_pref+':PHTRK_RATE')
        self._lb_rate.showUnits = True

        self._ld_bw = QLabel('Bandwidth', self)
        self._lb_bw = PyDMLabel(self, self.dev_pref+':PHTRK_BANDWIDTH')
        self._lb_bw.showUnits = True

        self._ld_loopctrl = QLabel('Loop Control', self)
        self._cb_loopctrl = PyDMEnumComboBox(
            self, self.dev_pref+':PHTRK_LOOPCTRL')

        lay_phtrkctrl = QGridLayout()
        lay_phtrkctrl.addWidget(self._ld_phtrkctrl, 0, 0, 1, 2)
        lay_phtrkctrl.addWidget(self._ld_bunnr, 1, 0)
        lay_phtrkctrl.addWidget(self._sb_bunnr, 1, 1)
        lay_phtrkctrl.addWidget(self._ld_gain, 2, 0)
        lay_phtrkctrl.addWidget(self._sb_gain, 2, 1)
        lay_phtrkctrl.addWidget(self._ld_sp, 3, 0)
        lay_phtrkctrl.addWidget(self._sb_sp, 3, 1)
        lay_phtrkctrl.addWidget(self._ld_range, 4, 0)
        lay_phtrkctrl.addWidget(self._sb_range, 4, 1)
        lay_phtrkctrl.addWidget(self._ld_dec, 5, 0)
        lay_phtrkctrl.addWidget(self._sb_dec, 5, 1)
        lay_phtrkctrl.addWidget(self._ld_rate, 6, 0)
        lay_phtrkctrl.addWidget(self._lb_rate, 6, 1)
        lay_phtrkctrl.addWidget(self._ld_bw, 7, 0)
        lay_phtrkctrl.addWidget(self._lb_bw, 7, 1)
        lay_phtrkctrl.addWidget(self._ld_loopctrl, 8, 0)
        lay_phtrkctrl.addWidget(self._cb_loopctrl, 8, 1)

        self._ld_phtrkdata = QLabel(
            '<h4>Data</h4>', self, alignment=Qt.AlignCenter)

        self._ld_mag = QLabel('Magnitude', self)
        self._lb_mag = PyDMLabel(self, self.dev_pref+':PHTRK_MAG')
        self._lb_mag.showUnits = True

        self._ld_trgain = QLabel('Transfer Gain', self)
        self._lb_trgain = PyDMLabel(self, self.dev_pref+':PHTRK_TFGAIN')
        self._lb_trgain.showUnits = True

        self._ld_nshift = QLabel('Normalizing Shift', self)
        self._lb_nshift = PyDMLabel(self, self.dev_pref+':PHTRK_SHIFT')

        self._ld_phase = QLabel('Phase', self)
        self._lb_phase = PyDMLabel(self, self.dev_pref+':PHTRK_PHASE')
        self._lb_phase.showUnits = True

        self._ld_error = QLabel('Error', self)
        self._lb_error = PyDMLabel(self, self.dev_pref+':PHTRK_ERROR')
        self._lb_error.showUnits = True

        self._ld_trfreq = QLabel('Tracking Frequency', self)
        self._lb_trfreq = PyDMLabel(self, self.dev_pref+':PHTRK_FREQ')
        self._lb_trfreq.showUnits = True

        self._ld_trtune = QLabel('Tracking Tune', self)
        self._lb_trtune = PyDMLabel(self, self.dev_pref+':PHTRK_TUNE')

        lay_phtrkdata = QGridLayout()
        lay_phtrkdata.addWidget(self._ld_phtrkdata, 0, 0, 1, 2)
        lay_phtrkdata.addWidget(self._ld_mag, 1, 0)
        lay_phtrkdata.addWidget(self._lb_mag, 1, 1)
        lay_phtrkdata.addWidget(self._ld_trgain, 2, 0)
        lay_phtrkdata.addWidget(self._lb_trgain, 2, 1)
        lay_phtrkdata.addWidget(self._ld_nshift, 3, 0)
        lay_phtrkdata.addWidget(self._lb_nshift, 3, 1)
        lay_phtrkdata.addWidget(self._ld_phase, 4, 0)
        lay_phtrkdata.addWidget(self._lb_phase, 4, 1)
        lay_phtrkdata.addWidget(self._ld_error, 5, 0)
        lay_phtrkdata.addWidget(self._lb_error, 5, 1)
        lay_phtrkdata.addWidget(self._ld_trfreq, 6, 0)
        lay_phtrkdata.addWidget(self._lb_trfreq, 6, 1)
        lay_phtrkdata.addWidget(self._ld_trtune, 7, 0)
        lay_phtrkdata.addWidget(self._lb_trtune, 7, 1)

        gbox_phtrk = QGroupBox('Phase Tracking', self)
        lay_phtrk = QGridLayout(gbox_phtrk)
        lay_phtrk.setHorizontalSpacing(20)
        lay_phtrk.addLayout(lay_phtrkctrl, 0, 0)
        lay_phtrk.addLayout(lay_phtrkdata, 0, 1)

        gbox_phtrk.setStyleSheet("""
            PyDMLabel{
                min-width: 6em; max-width: 6em;
            }""")

        wid = QWidget()
        lay = QGridLayout(wid)
        lay.addWidget(gbox_dtacq, 0, 0)
        lay.addWidget(gbox_trig, 0, 1)
        lay.addWidget(gbox_phtrk, 1, 0, 1, 2)
        lay.addItem(QSpacerItem(
            10, 10, QSzPlcy.MinimumExpanding, QSzPlcy.MinimumExpanding), 2, 2)
        return wid

    def _setupWaveformsWidget(self):
        self._graph_bunsig = WfmGraph(self)
        self._graph_bunsig.setPlotTitle('Bunch Signal')
        self._graph_bunsig.getAxis('bottom').setLabel('Time (ms)')
        self._graph_bunsig.getAxis('left').setLabel('CNT')
        self._graph_bunsig.add_scatter_curve(
            self.dev_pref+':SB_RAW', color=QColor('blue'))

        self._graph_mag = WfmGraph(self)
        self._graph_mag.setPlotTitle('Magnitude')
        self._graph_mag.getAxis('bottom').setLabel('Frequency (kHz)')
        self._graph_mag.getAxis('left').setLabel('dB')
        self._graph_mag.add_scatter_curve(
            self.dev_pref+':SB_MAG', color=QColor('blue'))
        self._graph_mag.add_marker(
            self.dev_pref+':SB_PEAKFREQ1',
            self.dev_pref+':SB_PEAK1',
            name='Mag', color=QColor('magenta'), symbol='o')

        self._graph_phs = WfmGraph(self)
        self._graph_phs.setPlotTitle('Phase')
        self._graph_phs.getAxis('bottom').setLabel('Frequency (kHz)')
        self._graph_phs.getAxis('left').setLabel('deg')
        self._graph_phs.add_scatter_curve(
            self.dev_pref+':SB_PHASE', color=QColor('blue'))
        self._graph_phs.add_marker(
            self.dev_pref+':SB_PEAKFREQ1',
            self.dev_pref+':SB_PHASE1',
            name='Phs', color=QColor('magenta'), symbol='o')

        self._ld_tfenbl = QLabel('Transfer Function Enable', self)
        self._cb_tfenbl = PyDMEnumComboBox(self, self.dev_pref+':SB_TF_ENABLE')

        self._ld_nrptsfft = QLabel('Number of points for FFT/Window', self)
        self._cb_nrptsfft = PyDMEnumComboBox(self, self.dev_pref+':SB_NFFT')

        self._ld_fftovlap = QLabel('Overlap (Autolimited to NFFT/2)', self)
        self._cb_fftovlap = PyDMEnumComboBox(
            self, self.dev_pref+':SB_NOVERLAP')

        self._ld_delaycal = QLabel('Delay Cal [ns]', self)
        self._le_delaycal = PyDMLineEdit(self, self.dev_pref+':SB_DEL_CAL')

        self._ld_avg = QLabel('Averaging', self)
        self._sb_avg = PyDMSpinbox(self, self.dev_pref+':SB_SP_AVG')
        self._sb_avg.showStepExponent = False

        gbox_fftsett = QGroupBox(self)
        lay_fftsett = QGridLayout(gbox_fftsett)
        lay_fftsett.addWidget(self._ld_tfenbl, 0, 0)
        lay_fftsett.addWidget(self._cb_tfenbl, 0, 1)
        lay_fftsett.addWidget(self._ld_nrptsfft, 1, 0)
        lay_fftsett.addWidget(self._cb_nrptsfft, 1, 1)
        lay_fftsett.addWidget(self._ld_fftovlap, 2, 0)
        lay_fftsett.addWidget(self._cb_fftovlap, 2, 1)
        lay_fftsett.addWidget(self._ld_delaycal, 3, 0)
        lay_fftsett.addWidget(self._le_delaycal, 3, 1)
        lay_fftsett.addWidget(self._ld_avg, 4, 0)
        lay_fftsett.addWidget(self._sb_avg, 4, 1)

        lay_graph = QGridLayout()
        lay_graph.addWidget(self._graph_bunsig, 0, 0)
        lay_graph.addWidget(self._graph_mag, 0, 1)
        lay_graph.addWidget(gbox_fftsett, 1, 0)
        lay_graph.addWidget(self._graph_phs, 1, 1)

        self._ld_acqenbl = QLabel('Acq. Enable', self)
        self._cb_acqenbl = PyDMEnumComboBox(self, self.dev_pref+':SB_ACQ_EN')

        self._ld_acqsing = QLabel('Acq. Mode', self)
        self._cb_acqsing = PyDMEnumComboBox(
            self, self.dev_pref+':SB_ACQ_SINGLE')

        self._ld_mean = QLabel('Mean', self, alignment=Qt.AlignCenter)
        self._lb_mean = PyDMLabel(self, self.dev_pref+':SB_MEANVAL')

        self._ld_rms = QLabel('RMS', self, alignment=Qt.AlignCenter)
        self._lb_rms = PyDMLabel(self, self.dev_pref+':SB_RMSVAL')

        self._ld_ampp2p = QLabel('Amp P-P', self, alignment=Qt.AlignCenter)
        self._lb_ampp2p = PyDMLabel(self, self.dev_pref+':SB_AMP_PP')

        self._ld_bunid = QLabel('Bunch ID', self, alignment=Qt.AlignCenter)
        self._lb_bunid = PyDMLabel(self, self.dev_pref+':SB_RAW_BUNCH_ID')

        gbox_acqctrl = QGroupBox('Acquisition control', self)
        lay_acqctrl = QGridLayout(gbox_acqctrl)
        lay_acqctrl.addWidget(self._ld_acqenbl, 0, 0)
        lay_acqctrl.addWidget(self._cb_acqenbl, 0, 1)
        lay_acqctrl.addWidget(self._ld_acqsing, 1, 0)
        lay_acqctrl.addWidget(self._cb_acqsing, 1, 1)
        lay_acqctrl.addItem(
            QSpacerItem(15, 1, QSzPlcy.Fixed, QSzPlcy.Ignored), 0, 2, 2, 1)
        lay_acqctrl.addWidget(self._ld_mean, 0, 3)
        lay_acqctrl.addWidget(self._lb_mean, 0, 4)
        lay_acqctrl.addWidget(self._ld_ampp2p, 0, 5)
        lay_acqctrl.addWidget(self._lb_ampp2p, 0, 6)
        lay_acqctrl.addWidget(self._ld_rms, 1, 3)
        lay_acqctrl.addWidget(self._lb_rms, 1, 4)
        lay_acqctrl.addWidget(self._ld_bunid, 1, 5)
        lay_acqctrl.addWidget(self._lb_bunid, 1, 6)

        # Marker
        self._ld_mkspan = QLabel('Span (kHz)', self, alignment=Qt.AlignCenter)
        self._le_mklow = PyDMLineEdit(self, self.dev_pref+':SB_SP_LOW1')
        self._le_mkhigh = PyDMLineEdit(self, self.dev_pref+':SB_SP_HIGH1')

        self._ld_mkmode = QLabel('Mode', self, alignment=Qt.AlignCenter)
        self._cb_mkmode = PyDMEnumComboBox(
            self, self.dev_pref+':SB_SP_SEARCH1')

        self._ld_mkfreq = QLabel('Frequency', self, alignment=Qt.AlignCenter)
        self._lb_mkfreq = PyDMLabel(self, self.dev_pref+':SB_PEAKFREQ1')
        self._lb_mkfreq.showUnits = True

        self._ld_mkmag = QLabel('Magnitude', self, alignment=Qt.AlignCenter)
        self._lb_mkmag = PyDMLabel(self, self.dev_pref+':SB_PEAK1')
        self._lb_mkmag.showUnits = True

        self._ld_mkphs = QLabel('Phase', self, alignment=Qt.AlignCenter)
        self._lb_mkphs = PyDMLabel(self, self.dev_pref+':SB_PHASE1')
        self._lb_mkphs.showUnits = True

        gbox_mk = QGroupBox('Marker', self)
        lay_mk = QGridLayout(gbox_mk)
        lay_mk.addWidget(self._ld_mkspan, 0, 0, 1, 2)
        lay_mk.addWidget(self._ld_mkmode, 0, 2)
        lay_mk.addWidget(self._ld_mkfreq, 0, 3)
        lay_mk.addWidget(self._ld_mkmag, 0, 4)
        lay_mk.addWidget(self._ld_mkphs, 0, 5)
        lay_mk.addWidget(self._le_mklow, 1, 0)
        lay_mk.addWidget(self._le_mkhigh, 1, 1)
        lay_mk.addWidget(self._cb_mkmode, 1, 2)
        lay_mk.addWidget(self._lb_mkfreq, 1, 3)
        lay_mk.addWidget(self._lb_mkmag, 1, 4)
        lay_mk.addWidget(self._lb_mkphs, 1, 5)

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


if __name__ == '__main__':
    """Run Example."""
    import sys
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()
    w = BbBAcqBRAM(
        prefix=_vaca_prefix, device='SI-Glob:DI-BbBProc-H')
    w.show()
    sys.exit(app.exec_())
