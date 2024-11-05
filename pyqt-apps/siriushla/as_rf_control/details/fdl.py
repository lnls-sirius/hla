"""Fast Data Logger Monitor and additional details."""

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QCheckBox, QComboBox, QGridLayout, QGroupBox, \
    QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ...widgets import PyDMStateButton, SiriusDialog, SiriusLabel, \
    SiriusLedAlert, SiriusLedState, SiriusLineEdit, SiriusPushButton, \
    SiriusSpinbox, SiriusWaveformPlot
from ..custom_widgets import RFTitleFrame
from ..util import DEFAULT_STYLESHEET, SEC_2_CHANNELS


class FDLDetails(SiriusDialog):
    """Fast Data Logger Monitor and additional details."""

    def __init__(self, parent=None, prefix='', section='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.system = system
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        self.title = 'FDL Monitor Details'
        self.title += (f' - {self.system}' if self.section == 'SI' else '')
        if self.section == 'SI':
            self.syst_dict = self.chs['FDL'][self.system]
        else:
            self.syst_dict = self.chs['FDL']
        self.setWindowTitle(self.title)
        self.curves_amp = dict()
        self.curves_phs = dict()
        self._setupUi()

    def _setupUi(self):
        self.setStyleSheet(DEFAULT_STYLESHEET)
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignTop)

        title_frame = RFTitleFrame(self, self.system)
        lay_title = QHBoxLayout(title_frame)
        lay_title.addWidget(QLabel(
            f'<h4>{self.title}</h4>', alignment=Qt.AlignCenter))

        controls = QGroupBox('Controls', self)
        controls.setLayout(self._controlsLayout())

        graphs = QGroupBox('Graphs', self)
        graphs.setLayout(self._graphsLayout())

        lay.addWidget(title_frame)
        lay.addWidget(controls)
        lay.addWidget(graphs)

    def _controlsLayout(self):
        lay = QGridLayout()
        lay.setVerticalSpacing(4)
        lay.setHorizontalSpacing(15)

        # First line
        self.lb_mode = SiriusLabel(self, self.prefix + self.syst_dict['Mode'])
        self.led_swtrig = SiriusLedAlert(
            self, self.prefix + self.syst_dict['SW Trig'])
        self.bt_swtrig = SiriusPushButton(
            self, self.prefix + self.syst_dict['Trig'], 'Force',
            pressValue=1, releaseValue=0)

        lay.addWidget(QLabel(
            '<h4>Perseus FDL Mode:</h4>', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter),
            0, 0)
        lay.addWidget(self.lb_mode, 0, 1)
        lay.addWidget(QLabel(
            '<h4>Force FDL Trigger (SW Interlock):</h4>', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter),
            0, 3)
        lay.addWidget(self.bt_swtrig, 0, 4)
        lay.addWidget(self.led_swtrig, 0, 5)

        # Second line
        self.lb_processing = SiriusLabel(
            self, self.prefix + self.syst_dict['Processing'])
        self.led_hwtrig = SiriusLedAlert(
            self, self.prefix + self.syst_dict['HW Trig'])

        lay.addWidget(QLabel(
            '<h4>IOC FDL Status:</h4>', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter),
            1, 0)
        lay.addWidget(self.lb_processing, 1, 1)
        lay.addWidget(QLabel(
            '<h4>Hardware Interlock:</h4>', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter),
            1, 3)
        lay.addWidget(self.led_hwtrig, 1, 5)

        # Third line
        self.bt_rearm = PyDMStateButton(
            self, self.prefix + self.syst_dict['Rearm']+'-Sel')
        self.led_rearm = SiriusLedState(
            self, self.prefix + self.syst_dict['Rearm']+'-Sts')
        self.led_raw = SiriusLedState(
            self, self.prefix + self.syst_dict['Raw']+'-Sts')
        self.bt_raw = PyDMStateButton(
            self, self.prefix + self.syst_dict['Raw']+'-Sel')

        lay.addWidget(QLabel(
            '<h4>FDL Rearm:</h4>', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter),
             2, 0)
        lay.addWidget(self.bt_rearm, 2, 1)
        lay.addWidget(self.led_rearm, 2, 2, alignment=Qt.AlignCenter)
        lay.addWidget(QLabel(
            '<h4>FDL ADCs Raw Data:</h4>', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter),
            2, 3)
        lay.addWidget(self.bt_raw, 2, 4)
        lay.addWidget(self.led_raw, 2, 5)

        # Fourth line
        self.sb_qty = SiriusSpinbox(
            self, self.prefix + self.syst_dict['Qty'] + '-SP')
        self.lb_qty_sp = SiriusLabel(
            self, self.prefix + self.syst_dict['Qty'] + '-SP')
        self.lb_qty_rb = SiriusLabel(
            self, self.prefix + self.syst_dict['Qty'] + '-RB')

        qty_lay_sp = QHBoxLayout()
        qty_lay_sp.addWidget(self.sb_qty)
        qty_lay_sp.addWidget(self.lb_qty_sp)
        qty_lay_rb = QHBoxLayout()
        qty_lay_rb.setSpacing(1)
        qty_lay_rb.addWidget(QLabel(
            '<h4>Qty:</h4>', alignment=Qt.AlignRight | Qt.AlignVCenter))
        qty_lay_rb.addWidget(self.lb_qty_rb)

        self.lb_size = SiriusLabel(
            self, self.prefix + self.syst_dict['Size'])
        self.lb_size.showUnits = True
        self.lb_duration = SiriusLabel(
            self, self.prefix + self.syst_dict['Duration'])
        self.lb_duration.showUnits = True
        size_dur_lay = QHBoxLayout()
        size_dur_lay.addWidget(QLabel(
            '<h4>Size:</h4>', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter))
        size_dur_lay.addWidget(self.lb_size)
        size_dur_lay.addWidget(QLabel(
            '<h4>Duration:</h4>', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter))
        size_dur_lay.addWidget(self.lb_duration)

        lay.addWidget(QLabel(
            '<h4>FDL Frame QTY:</h4>', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter),
            3, 0)
        lay.addLayout(qty_lay_sp, 3, 1)
        lay.addLayout(qty_lay_rb, 3, 2)
        lay.addLayout(size_dur_lay, 3, 3)

        # Fifth line
        self.sb_delay_sample = SiriusLineEdit(
            self, self.prefix + self.syst_dict['Delay'] + '-SP')
        self.lb_delay_sample = SiriusLabel(
            self, self.prefix + self.syst_dict['Delay'] + '-RB')
        self.sb_delay_us = SiriusLineEdit(
            self, self.prefix + self.syst_dict['Delay'] + 'Time-SP')
        self.lb_delay_us = SiriusLabel(
            self, self.prefix + self.syst_dict['Delay'] + 'Time-RB')
        sb_unit = QComboBox()
        sb_unit.addItems(['Choose a unit', 'Sample units', 'us'])
        sb_unit.setMaximumWidth(120)
        sb_unit.currentTextChanged.connect(self._handle_unit_change)

        delay_lay = QGridLayout()
        delay_lay.addWidget(self.sb_delay_sample, 0, 0)
        delay_lay.addWidget(self.lb_delay_sample, 0, 1)
        delay_lay.addWidget(self.sb_delay_us, 0, 0)
        delay_lay.addWidget(self.lb_delay_us, 0, 1)

        self.sb_delay_us.setVisible(False)
        self.lb_delay_us.setVisible(False)
        self.sb_delay_sample.setVisible(False)
        self.lb_delay_sample.setVisible(False)

        lay.addWidget(QLabel(
            '<h4>Trigger Delay:</h4>', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter),
            4, 0)
        lay.addWidget(sb_unit, 4, 1)
        lay.addLayout(delay_lay, 4, 2)

        return lay

    def _graphsLayout(self):
        lay = QVBoxLayout()

        self.amp_graph = self.setupPlot()
        self.amp_graph.setObjectName('amp_graph')
        self.amp_graph.setStyleSheet(
            '#amp_graph{min-height:15em;min-width:21em;max-height:15em;}')

        self.phase_graph = self.setupPlot()
        self.phase_graph.setObjectName('phase_graph')
        self.phase_graph.setStyleSheet(
            '#phase_graph{min-height:15em;min-width:21em;max-height:15em;}')

        checks_wid = QWidget()
        self.hbox_checks = QHBoxLayout(checks_wid)
        for idx in range(len(self.syst_dict['Signals'])):
            self.setupCurve(
                self.syst_dict['Signals'][idx],
                self.prefix + self.syst_dict['Time'],
                idx)

        lay.addWidget(checks_wid)
        lay.addWidget(QLabel('<h4>Amplitude</h4>'))
        lay.addWidget(self.amp_graph)
        lay.addWidget(QLabel('<h4>Phase</h4>'))
        lay.addWidget(self.phase_graph)

        return lay

    def setupPlot(self):
        graph = SiriusWaveformPlot(
            parent=self, background=QColor(255, 255, 255))
        graph.maxRedrawRate = 2
        graph.setShowXGrid(True)
        graph.setShowYGrid(True)
        graph.setShowLegend(False)
        graph.setAutoRangeX(True)
        graph.setAutoRangeY(True)
        graph.setAxisColor(QColor(0, 0, 0))

        return graph

    def setupCurve(self, signal, timebase, idx):
        cid = signal[0]
        color = self.prefix + signal[3]

        if signal[1]:
            chn_amp = self.prefix + signal[1]
            self.amp_graph.addChannel(
                y_channel=chn_amp,
                x_channel=timebase,
                redraw_mode=2, name=cid, color=color,
                lineStyle=Qt.SolidLine, lineWidth=1
            )
            self.curves_amp[cid] = self.amp_graph.curveAtIndex(idx)
        if signal[2]:
            chn_phs = self.prefix + signal[2]
            self.phase_graph.addChannel(
                y_channel=chn_phs,
                x_channel=timebase,
                redraw_mode=2, name=cid, color=color,
                lineStyle=Qt.SolidLine, lineWidth=1
            )
            self.curves_phs[cid] = self.phase_graph.curveAtIndex(idx)

        cbx = QCheckBox(cid, self)
        cbx.setChecked(True)
        cbx.setObjectName(cid)
        cbx.setStyleSheet('color:' + color + ';')
        cbx.stateChanged.connect(self._handle_curves_visibility)
        self.hbox_checks.addWidget(cbx)

    def _handle_curves_visibility(self, state):
        name = self.sender().objectName()

        amp_curve = self.curves_amp.get(name)
        if amp_curve:
            amp_curve.setVisible(state)

        phs_curve = self.curves_phs.get(name)
        if phs_curve:
            phs_curve.setVisible(state)

    def _handle_unit_change(self, text):
        self.sb_delay_sample.setVisible(text == 'Sample units')
        self.lb_delay_sample.setVisible(text == 'Sample units')
        self.sb_delay_us.setVisible(text == 'us')
        self.lb_delay_us.setVisible(text == 'us')
