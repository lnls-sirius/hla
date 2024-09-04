"""Fast Data Logger Monitor and additional details."""

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QCheckBox, QComboBox, QGridLayout, QGroupBox, \
    QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ...widgets import PyDMStateButton, SiriusDialog, SiriusLabel, \
    SiriusLedAlert, SiriusSpinbox, SiriusWaveformPlot


class FDLDetails(SiriusDialog):
    """Fast Data Logger Monitor and additional details."""

    def __init__(self, parent=None, prefix='', section='', chs=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.chs = chs
        self.setObjectName(self.section+'App')
        self.setWindowTitle('FDL Monitor')
        self.curves_amp = dict()
        self.curves_phs = dict()
        self._setupUi()

    def _setupUi(self):
        wid = QWidget(self)
        wid.setMinimumSize(820, 800)
        lay = QVBoxLayout(wid)
        lay.setAlignment(Qt.AlignTop)

        if self.section == 'SI':
            title = QLabel(
                f"<h4>LLRF {self.chs['Name']} FDL</h4>", self,
                alignment=Qt.AlignCenter)
        else:
            title = QLabel("<h4>LLRF FDL</h4>", self, alignment=Qt.AlignCenter)
        lay.addWidget(title)

        controls = QGroupBox('Controls', self)
        controls.setLayout(self._controlsLayout())

        graphs = QGroupBox('Graphs', self)
        graphs.setLayout(self._graphsLayout())

        lay.addWidget(controls)
        lay.addWidget(graphs)

    def _controlsLayout(self):
        lay = QGridLayout()
        lay.setVerticalSpacing(4)
        lay.setHorizontalSpacing(15)

        # First line
        self.lb_mode = SiriusLabel(self, self.prefix + self.chs['Mode'])
        self.led_swtrig = SiriusLedAlert(
            self, self.prefix + self.chs['SW Trig'])
        self.bt_swtrig = PyDMStateButton(
            self, self.prefix + self.chs['Trig'])

        lay.addWidget(QLabel(
            '<h4>Perseus FDL Mode:</h4>', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter),
            0, 0)
        lay.addWidget(self.lb_mode, 0, 1)
        lay.addWidget(QLabel(
            '<h4>Force FDL Trigger (SW Interlock):</h4>', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter),
            0, 2)
        lay.addWidget(self.bt_swtrig, 0, 3)
        lay.addWidget(self.led_swtrig, 0, 4)

        # Second line
        self.lb_processing = SiriusLabel(
            self, self.prefix + self.chs['Processing'])
        self.led_hwtrig = SiriusLedAlert(
            self, self.prefix + self.chs['HW Trig'])

        lay.addWidget(QLabel(
            '<h4>IOC FDL Status:</h4>', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter),
            1, 0)
        lay.addWidget(self.lb_processing, 1, 1)
        lay.addWidget(QLabel(
            '<h4>Hardware Interlock:</h4>', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter),
            1, 2)
        lay.addWidget(self.led_hwtrig, 1, 4)

        # Third line
        self.bt_rearm = PyDMStateButton(
            self, self.prefix + self.chs['Rearm'])
        self.led_rearm = SiriusLedAlert(
            self, self.prefix + self.chs['Rearm'])
        self.led_raw = SiriusLedAlert(
            self, self.prefix + self.chs['Raw']+'-Sts')
        self.bt_raw = PyDMStateButton(
            self, self.prefix + self.chs['Raw']+'-Sel')

        rearm_lay = QHBoxLayout()
        rearm_lay.addWidget(self.bt_rearm)
        rearm_lay.addWidget(self.led_rearm)

        lay.addWidget(QLabel(
            '<h4>FDL Rearm:</h4>', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter),
             2, 0)
        lay.addLayout(rearm_lay, 2, 1)
        lay.addWidget(QLabel(
            '<h4>FDL ADCs Raw Data:</h4>', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter),
            2, 2)
        lay.addWidget(self.bt_raw, 2, 3)
        lay.addWidget(self.led_raw, 2, 4)

        # Fourth line
        self.sb_qty = SiriusSpinbox(
            self, self.prefix + self.chs['Qty'] + 'SP')
        self.lb_qty = SiriusLabel(
            self, self.prefix + self.chs['Qty'] + 'RB')
        qty_lay = QHBoxLayout()
        qty_lay.addWidget(self.sb_qty)
        qty_lay.addWidget(self.lb_qty)

        self.lb_size = SiriusLabel(
            self, self.prefix + self.chs['Size'])
        self.lb_size._show_units = True
        self.lb_duration = SiriusLabel(
            self, self.prefix + self.chs['Duration'])
        self.lb_duration._show_units = True
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
        lay.addLayout(qty_lay, 3, 1)
        lay.addLayout(size_dur_lay, 3, 2)

        # Fifth line
        self.sb_delay_sample = SiriusSpinbox(
            self, self.prefix + self.chs['Delay'] + '-SP')
        self.lb_delay_sample = SiriusLabel(
            self, self.prefix + self.chs['Delay'] + '-RB')
        self.sb_delay_us = SiriusSpinbox(
            self, self.prefix + self.chs['Delay'] + 'Time-SP')
        self.lb_delay_us = SiriusLabel(
            self, self.prefix + self.chs['Delay'] + 'Time-RB')
        sb_unit = QComboBox()
        sb_unit.addItems(['Choose a unit', 'Sample units', 'us'])
        sb_unit.setMaximumWidth(120)
        sb_unit.currentTextChanged.connect(self._handle_unit_change)

        delay_lay = QHBoxLayout()
        delay_lay.addWidget(self.sb_delay_sample)
        delay_lay.addWidget(self.lb_delay_sample)
        delay_lay.addWidget(self.sb_delay_us)
        delay_lay.addWidget(self.lb_delay_us)

        self.sb_delay_us.setVisible(False)
        self.lb_delay_us.setVisible(False)
        self.sb_delay_sample.setVisible(False)
        self.lb_delay_sample.setVisible(False)

        lay.addWidget(QLabel(
            '<h4>Trigger Delay:</h4>', self,
            alignment=Qt.AlignRight | Qt.AlignVCenter),
            4, 0
        )
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
        for idx in range(len(self.chs['Signals'])):
            self.setupCurve(
                self.chs['Signals'][idx],
                self.prefix + self.chs['Time'],
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
