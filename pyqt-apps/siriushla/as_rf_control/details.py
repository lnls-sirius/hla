"""Detail windows."""

from pyqtgraph import BarGraphItem, PlotWidget
from pydm.widgets import PyDMEnumComboBox
from qtpy.QtCore import Qt, QTimer
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QCheckBox, QComboBox, QFormLayout, QGridLayout, \
    QGroupBox, QHBoxLayout, QLabel, QSizePolicy as QSzPlcy, QSpacerItem, \
    QTabWidget, QVBoxLayout, QWidget, QFrame

from ..widgets import DetachableTabWidget, PyDMLedMultiChannel, \
    PyDMStateButton, SiriusConnectionSignal as _ConnSignal, SiriusDialog, \
    SiriusLabel, SiriusLedAlert, SiriusSpinbox, SiriusTimePlot, \
    SiriusWaveformPlot, SiriusLedState, SiriusLineEdit, SiriusScaleIndicator, \
    SiriusEnumComboBox, SiriusPushButton

from .util import SEC_2_CHANNELS


class CavityStatusDetails(SiriusDialog):
    """Cavity Status Datails."""

    def __init__(self, parent=None, prefix='', section=''):
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section.upper()
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section + 'App')
        self.setWindowTitle(self.section + ' Cavity Detailed Status')
        self._setupUi()

    def _setupUi(self):
        lay_temp1 = QFormLayout()
        lay_temp1.setHorizontalSpacing(9)
        lay_temp1.setVerticalSpacing(9)
        lay_temp1.setLabelAlignment(Qt.AlignRight)
        lay_temp1.setFormAlignment(Qt.AlignTop)
        lb_temp1 = QLabel('Cell and Coupler\nTemperatures\nPT100', self)
        lb_temp1.setStyleSheet(
            'font-weight:bold; qproperty-alignment:AlignCenter;')
        lay_temp1.addRow(lb_temp1)
        lims = self.chs['Cav Sts']['Temp']['Cells Limits']
        tooltip = 'Interlock limits: \nMin: ' + str(lims[0]) + \
            '°C, Max: '+str(lims[1])+'°C'
        for idx, cell in enumerate(self.chs['Cav Sts']['Temp']['Cells']):
            lbl = SiriusLabel(self, self.prefix+cell[0])
            lbl.showUnits = True
            lbl.setStyleSheet('min-width:3.5em; max-width:3.5em;')
            led = PyDMLedMultiChannel(
                self,
                {self.prefix+cell[0]: {'comp': 'wt', 'value': lims},
                 self.prefix+cell[0].replace('T-Mon', 'TUp-Mon'): 0,
                 self.prefix+cell[0].replace('T-Mon', 'TDown-Mon'): 0})
            led.setToolTip(tooltip)
            hbox = QHBoxLayout()
            hbox.setAlignment(Qt.AlignLeft)
            hbox.addWidget(lbl)
            hbox.addWidget(led)
            lay_temp1.addRow('Cell '+str(idx + 1)+': ', hbox)
        ch_coup = self.chs['Cav Sts']['Temp']['Coupler'][0]
        lims_coup = self.chs['Cav Sts']['Temp']['Coupler Limits']
        lb_coup = SiriusLabel(self, self.prefix+ch_coup)
        lb_coup.setStyleSheet('min-width:3.5em; max-width:3.5em;')
        lb_coup.showUnits = True
        led_coup = PyDMLedMultiChannel(
            self,
            {self.prefix+ch_coup: {'comp': 'wt', 'value': lims_coup},
             self.prefix+ch_coup.replace('T-Mon', 'TUp-Mon'): 0,
             self.prefix+ch_coup.replace('T-Mon', 'TDown-Mon'): 0})
        led_coup.setToolTip(
            'Interlock limits: \n'
            'Min: '+str(lims_coup[0])+'°C, Max: '+str(lims_coup[1])+'°C')
        hb_coup = QHBoxLayout()
        hb_coup.setAlignment(Qt.AlignLeft)
        hb_coup.addWidget(lb_coup)
        hb_coup.addWidget(led_coup)
        lay_temp1.addRow('Coupler: ', hb_coup)

        lay_temp2 = QFormLayout()
        lay_temp2.setHorizontalSpacing(9)
        lay_temp2.setVerticalSpacing(9)
        lay_temp2.setLabelAlignment(Qt.AlignRight)
        lay_temp2.setFormAlignment(Qt.AlignTop | Qt.AlignHCenter)
        lb_temp2 = QLabel('Cell\nTemperatures\nThermostats', self)
        lb_temp2.setStyleSheet(
            'font-weight:bold; qproperty-alignment:AlignCenter;')
        lay_temp2.addRow(lb_temp2)
        for idx, cell in enumerate(self.chs['Cav Sts']['Temp']['Cells']):
            led = SiriusLedAlert(self)
            led.setToolTip('Interlock limits:\nMax: 60°C')
            led.channel = self.prefix+cell[0].replace('T-Mon', 'Tms-Mon')
            lay_temp2.addRow('Cell '+str(idx + 1)+': ', led)

        lay_dtemp = QFormLayout()
        lay_dtemp.setHorizontalSpacing(9)
        lay_dtemp.setVerticalSpacing(9)
        lay_dtemp.setLabelAlignment(Qt.AlignRight)
        lay_dtemp.setFormAlignment(Qt.AlignTop | Qt.AlignHCenter)
        lb_dtemp = QLabel('Disc\nTemperatures\nThermostats', self)
        lb_dtemp.setStyleSheet(
            'font-weight:bold; qproperty-alignment:AlignCenter;')
        lay_dtemp.addRow(lb_dtemp)
        for idx, disc in enumerate(self.chs['Cav Sts']['Temp']['Discs']):
            led = SiriusLedAlert(self)
            led.setToolTip('Interlock limits:\nMax: 60°C')
            led.channel = self.prefix+disc
            lay_dtemp.addRow('Disc '+str(idx)+': ', led)

        lay_flwrt = QFormLayout()
        lay_flwrt.setHorizontalSpacing(9)
        lay_flwrt.setVerticalSpacing(9)
        lay_flwrt.setLabelAlignment(Qt.AlignRight)
        lay_flwrt.setFormAlignment(Qt.AlignTop)
        lb_flwrf = QLabel('Flow Switches', self)
        lb_flwrf.setStyleSheet(
            'font-weight:bold; qproperty-alignment:AlignCenter;')
        lay_flwrt.addRow(lb_flwrf)
        for flwsw, pvn in self.chs['Cav Sts']['FlwRt'].items():
            led = SiriusLedAlert(self, self.prefix+pvn)
            lay_flwrt.addRow(flwsw+': ', led)

        self.led_couppressure = SiriusLedAlert(
            self, self.prefix+self.chs['Cav Sts']['Vac']['Coupler ok'])
        self.led_pressure = SiriusLedAlert(self)
        self.led_pressure.setToolTip('Interlock limits:\nMax: 5e-7mBar')
        self.led_pressure.channel = \
            self.prefix+self.chs['Cav Sts']['Vac']['Cells ok']
        lay_vac = QFormLayout()
        lay_vac.setHorizontalSpacing(9)
        lay_vac.setVerticalSpacing(9)
        lay_vac.setLabelAlignment(Qt.AlignRight)
        lay_vac.setFormAlignment(Qt.AlignTop)
        lb_vac = QLabel('Vacuum', self)
        lb_vac.setStyleSheet(
            'font-weight:bold; qproperty-alignment:AlignCenter;')
        lay_flwrt.addRow(lb_vac)
        lay_vac.addRow('Pressure Sensor: ', self.led_couppressure)
        lay_vac.addRow('Vacuum: ', self.led_pressure)

        lbl = QLabel('Cavity - Detailed Status', self)
        lbl.setStyleSheet(
            'font-weight:bold; qproperty-alignment:AlignCenter;')
        lay = QGridLayout(self)
        lay.setHorizontalSpacing(30)
        lay.setVerticalSpacing(20)
        lay.addWidget(lbl, 0, 0, 1, 4)
        lay.addLayout(lay_temp1, 1, 0, 2, 1)
        lay.addLayout(lay_temp2, 1, 1, 2, 1)
        lay.addLayout(lay_dtemp, 1, 2, 2, 1)
        lay.addLayout(lay_flwrt, 1, 3)
        lay.addLayout(lay_vac, 2, 3)

        self.setStyleSheet("""
            SiriusLabel{
                qproperty-alignment: AlignLeft;
            }
            QLed{
                max-width: 1.29em;
            }
            .QLabel{
                max-height:4em;
                qproperty-alignment: AlignRight;
            }""")


class TransmLineStatusDetails(SiriusDialog):
    """Transmission Line Status Details."""

    def __init__(self, parent=None, prefix='', section=''):
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section.upper()
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section + 'App')
        self.setWindowTitle(self.section + ' Transm. Line Detailed Status')
        self._setupUi()

    def _setupUi(self):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(15)

        self.title = QLabel(
            '<h4>Transm. Line - Detailed Status</h4>',
            self, alignment=Qt.AlignHCenter)
        lay.addWidget(self.title, 0, 0, 1, 4)
        lay.addItem(QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Fixed), 1, 0)

        offset = 0
        if self.section == 'SI':
            for key, chs_dict in self.chs['TL Sts'].items():
                self._setupDetails(lay, key, chs_dict, offset)
                offset += 2
        else:
            self._setupDetails(lay, None, self.chs['TL Sts'], offset)

    def _setupDetails(self, lay, key, chs_dict, offset):
        row = 2
        if key:
            lay.addWidget(QLabel(
                f'<h4>{key}<h4>', self,
                alignment=Qt.AlignRight), row, offset)
            row += 1

        for widget_id, pvname in chs_dict['label_led'].items():
            wid = QWidget()
            hlay = QHBoxLayout()
            wid.setLayout(hlay)
            hlay.setContentsMargins(0, 0, 0, 0)

            si_lbl_wid = SiriusLabel(
                self, self.prefix+pvname['label'])
            si_lbl_wid.showUnits = True
            si_lbl_wid.setMaximumWidth(100)
            si_lbl_wid.setStyleSheet('qproperty-alignment: AlignLeft;')
            hlay.addWidget(si_lbl_wid)

            si_led_wid = SiriusLedAlert(
                self, self.prefix+pvname['led'])
            hlay.addWidget(si_led_wid)

            lay.addWidget(QLabel(
                widget_id, self, alignment=Qt.AlignRight), row, offset)
            lay.addWidget(wid, row, offset+1)
            row += 1

        wid = QWidget()
        hlay = QHBoxLayout()
        wid.setLayout(hlay)
        hlay.setContentsMargins(0, 0, 0, 0)

        lb_circtin = SiriusLabel(
            self, self.prefix+chs_dict['Circulator Temp. In']['label'])
        lb_circtin.showUnits = True
        lb_circtin.setStyleSheet('qproperty-alignment: AlignLeft;')
        hlay.addWidget(lb_circtin)

        si_led_wid = PyDMLedMultiChannel(
            self, chs_dict['Circulator Temp. In']['led'])
        hlay.addWidget(si_led_wid)

        lay.addWidget(QLabel(
            'Circulator T In: ', self, alignment=Qt.AlignRight), row, offset)
        lay.addWidget(wid, row, offset + 1)
        row += 1

        for widget_id, pvname in chs_dict['label'].items():
            if not ((self.section == 'BO') and ('Combiner' == widget_id)):
                si_lbl_wid = SiriusLabel(
                    self, self.prefix+pvname)
                si_lbl_wid.showUnits = True
                si_lbl_wid.setStyleSheet('qproperty-alignment: AlignLeft;')
                lay.addWidget(QLabel(
                    widget_id, self, alignment=Qt.AlignRight), row, offset)
                lay.addWidget(si_lbl_wid, row, offset+1)
                row += 1

        lay.addItem(QSpacerItem(
            0, 10, QSzPlcy.Ignored, QSzPlcy.Fixed), row, offset)
        row += 1

        for widget_id, pvname in chs_dict['led'].items():
            if not ((self.section == 'BO') and ('Detector Load' in widget_id)):
                si_led_wid = SiriusLedAlert(
                    self, self.prefix+pvname)
                lay.addWidget(QLabel(
                    f'{widget_id}: ', self, alignment=Qt.AlignRight),
                    row, offset)
                lay.addWidget(si_led_wid, row, offset+1)
                row += 1

        self.setStyleSheet("""
            SiriusLabel{
                qproperty-alignment: AlignLeft;
            }
            QLed{
                max-width: 1.29em;
            }""")


class LLRFInterlockDetails(SiriusDialog):
    """LLRF Interlock Details."""

    def __init__(self, parent, prefix='', section=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        self.setWindowTitle(self.section+' LLRF Interlock Details')
        self._setupUi()

    def _setupUi(self):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setHorizontalSpacing(25)
        lay.setVerticalSpacing(15)

        self.title = QLabel(
            '<h4>LLRF Interlock Details</h4>', self,
            alignment=Qt.AlignCenter)
        lay.addWidget(self.title, 0, 0, 1, 3)

        if self.section == 'SI':
            offset = 1
            for key, chs_dict in self.chs['LLRF Intlk Details'].items():
                self._setupDetails(lay, key, chs_dict, offset)
                offset += 2
        else:
            self._setupDetails(lay, None, self.chs['LLRF Intlk Details'], 1)

    def _setupDetails(self, lay, key, chs_dict, offset):
        if key:
            lay.addWidget(QLabel(
                f'<h4>LLRF {key}</h4>', self,
                alignment=Qt.AlignLeft), offset, 0)

        # inputs
        col = 0
        for name, dic in chs_dict['Inputs'].items():
            gbox = QGroupBox(name, self)
            lay_intlk = QGridLayout(gbox)
            lay_intlk.setAlignment(Qt.AlignTop)
            lay_intlk.setHorizontalSpacing(9)
            lay_intlk.setVerticalSpacing(0)

            icol = 0
            for key in dic['Status']:
                desc = QLabel(key, self, alignment=Qt.AlignCenter)
                desc.setStyleSheet('QLabel{min-width:1em; max-width:2.5em;}')
                lay_intlk.addWidget(desc, 0, icol)
                icol += 1

            labels = dic['Labels']
            for idx, label in enumerate(labels):
                irow, icol = idx+1, 0
                for key, pvn in dic['Status'].items():
                    led = SiriusLedAlert(self, self.prefix+pvn, bit=idx)
                    led.shape = led.Square
                    if key != 'Mon':
                        led.offColor = led.DarkRed
                    lay_intlk.addWidget(led, irow, icol)
                    icol += 1
                lbl = QLabel(label, self)
                lbl.setStyleSheet('QLabel{min-width:12em;}')
                lay_intlk.addWidget(lbl, irow, icol)

            lay.addWidget(gbox, offset+1, col)
            col += 1

        # timestamps
        gbox_time = QGroupBox('Timestamps', self)
        lay_time = QGridLayout(gbox_time)
        lay_time.setAlignment(Qt.AlignTop)
        lay_time.setHorizontalSpacing(9)
        lay_time.setVerticalSpacing(9)
        for idx, pvn in chs_dict['Timestamps'].items():
            irow = int(idx)-1
            desc = QLabel('Interlock '+idx, self, alignment=Qt.AlignCenter)
            desc.setStyleSheet('QLabel{min-width:6em;}')
            lbl = SiriusLabel(self, self.prefix+pvn)
            lbl.showUnits = True
            lay_time.addWidget(desc, irow, 0)
            lay_time.addWidget(lbl, irow, 1)
        lay.addWidget(gbox_time, offset+1, col)


class BarGraph(PlotWidget):
    """Bar Graph."""

    def __init__(self, channels=list(), xLabels=list(), yLabel='', title=''):
        """Init."""
        super().__init__()
        self._channels = list()
        for chn in channels:
            self._channels.append(_ConnSignal(chn))
        self._xLabels = xLabels
        self._yLabel = yLabel

        self.showGrid(x=True, y=True)
        self.setBackground('w')
        self.setXRange(min=-0.5, max=len(xLabels)-0.5)
        self.setTitle(title)
        self.setLabel('left', text=self._yLabel)
        self.getAxis('left').setStyle(
            autoExpandTextSpace=False, tickTextWidth=30)
        self.getAxis('bottom').setTicks(
            [[(i, l) for i, l in enumerate(self._xLabels)]])

        self._baritems = dict()
        for idx, lbl in enumerate(self._xLabels):
            baritem = BarGraphItem(
                x=[idx, ], width=1, height=0, brush='b')
            self.addItem(baritem)
            self._baritems[idx] = baritem

        self._timer = QTimer()
        self._timer.timeout.connect(self._update_graph)
        self._timer.setInterval(500)  # ms
        self._timer.start()

    def _update_graph(self):
        wave = list()
        for idx, chn in enumerate(self._channels):
            value = chn.value if chn.value is not None else 0
            wave.append(value)
            self._baritems[idx].setOpts(height=value)


class TempMonitor(SiriusDialog):
    """Temperature Profile Monitor."""

    def __init__(self, parent=None, prefix='', section=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        self.setWindowTitle('RF Temperature Monitor')
        self._setupUi()

    def _setupUi(self):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setHorizontalSpacing(25)
        lay.setVerticalSpacing(15)

        self.title = QLabel(
            '<h3>RF Temperature Monitor</h3>', self,
            alignment=Qt.AlignCenter)
        lay.addWidget(self.title, 0, 0)

        if len(self.chs['TempMon']) == 1:
            dettab = QTabWidget(self)
        else:
            dettab = DetachableTabWidget(self)
        dettab.setObjectName(self.section+'Tab')
        for dettabtitle, dtcontent in self.chs['TempMon'].items():
            if dettabtitle == 'Power (Water)':
                labels = list(dtcontent.keys())
                channels = [self.prefix+ch for ch in dtcontent.values()]
                wid = BarGraph(
                    channels=channels, xLabels=labels, yLabel='Power [kW]',
                    title=dettabtitle)
            else:
                wid = QTabWidget()
                for tabtitle, content in dtcontent.items():
                    labels = list(content.keys())
                    channels = [self.prefix+ch for ch in content.values()]
                    ylabel = 'Temperature [°C]' \
                        if 'temp' in dettabtitle.lower() \
                        else 'Diss. Power [kW]'
                    tabwid = BarGraph(
                        channels=channels, xLabels=labels,
                        yLabel=ylabel, title=dettabtitle)
                    wid.addTab(tabwid, tabtitle)
            dettab.addTab(wid, dettabtitle)
        lay.addWidget(dettab, 1, 0)


class FDLMonitor(SiriusDialog):
    """Fast Data Logger Monitor."""

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


class SlowLoopErrorDetails(SiriusDialog):
    """Slow Loop Control Error Details."""
    def __init__(self, parent=None, prefix='', section=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        self.setWindowTitle('Slow Loop Control Error Details')
        self._setupUi()

    def _setupUi(self):
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(20)

        self.title = QLabel(
            '<h3>Slow Loop Control Error Details</h3>', self,
            alignment=Qt.AlignCenter)
        lay.addWidget(self.title)

        if self.section == 'SI':
            for key, chs_dict in self.chs['SL']['ErrDtls'].items():
                self._setupDetails(lay, key, chs_dict)
        else:
            self._setupDetails(lay, None, self.chs['SL']['ErrDtls'])

    def _setupDetails(self, lay, key, chs_dict):
        if key:
            lay.addItem(QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Fixed))
            lay.addWidget(QLabel(
                f'<h4>LLRF {key}</h4>', self, alignment=Qt.AlignCenter))

        lay_llrf = QHBoxLayout()
        lay_llrf.setAlignment(Qt.AlignTop)
        lay_llrf.setSpacing(0)

        lay_table = QGridLayout()
        lay_table.setAlignment(Qt.AlignVCenter)
        lay_table.setSpacing(9)
        lay_table.addWidget(QLabel(
            '<h4>Reference<h4>', self, alignment=Qt.AlignCenter), 1, 0)
        lay_table.addWidget(QLabel(
            '<h4>Input</h4>', self, alignment=Qt.AlignCenter), 2, 0)
        lay_table.addWidget(QLabel(
            '<h4>Error</h4>', self, alignment=Qt.AlignCenter), 3, 0)

        # I
        lb_iref = SiriusLabel(self, self.prefix+chs_dict['IRef'])
        lb_iref.showUnits = True
        lb_iinp = SiriusLabel(self, self.prefix+chs_dict['IInp'])
        lb_iinp.showUnits = True
        lb_ierr = SiriusLabel(self, self.prefix+chs_dict['IErr'])
        lb_ierr.showUnits = True
        lay_table.addWidget(QLabel(
            '<h4>I</h4>', self, alignment=Qt.AlignCenter), 0, 1)
        lay_table.addWidget(lb_iref, 1, 1)
        lay_table.addWidget(lb_iinp, 2, 1)
        lay_table.addWidget(lb_ierr, 3, 1)

        # Q
        lb_qref = SiriusLabel(self, self.prefix+chs_dict['QRef'])
        lb_qref.showUnits = True
        lb_qinp = SiriusLabel(self, self.prefix+chs_dict['QInp'])
        lb_qinp.showUnits = True
        lb_qerr = SiriusLabel(self, self.prefix+chs_dict['QErr'])
        lb_qerr.showUnits = True
        lay_table.addWidget(QLabel(
            '<h4>Q</h4>', self, alignment=Qt.AlignCenter), 0, 2)
        lay_table.addWidget(lb_qref, 1, 2)
        lay_table.addWidget(lb_qinp, 2, 2)
        lay_table.addWidget(lb_qerr, 3, 2)

        lay_llrf.addLayout(lay_table)
        lay_llrf.addItem(QSpacerItem(15, 0, QSzPlcy.Fixed, QSzPlcy.Ignored))

        # Graphs
        self.setupGraphFasor(lay_llrf, chs_dict)
        self.setupGraphTime(lay_llrf, key, "Amp")
        self.setupGraphTime(lay_llrf, key, "Phs")

        lay.addLayout(lay_llrf)

    def setupGraphFasor(self, lay_llrf, chs_dict):
        graph_iq = SiriusWaveformPlot(
            parent=self, background=QColor(255, 255, 255))
        graph_iq.setStyleSheet('min-height: 15em; min-width: 20em;')
        graph_iq.maxRedrawRate = 2
        graph_iq.mouseEnabledX = True
        graph_iq.setShowXGrid(True)
        graph_iq.setShowYGrid(True)
        graph_iq.setShowLegend(True)
        graph_iq.setAutoRangeX(False)
        graph_iq.setAutoRangeY(False)
        graph_iq.setAxisColor(QColor(0, 0, 0))
        axx = graph_iq.plotItem.getAxis('right')
        axx.setVisible(True)
        axx.setTicks([])
        axx.setWidth(0)
        axx = graph_iq.plotItem.getAxis('top')
        axx.setVisible(True)
        axx.setTicks([])
        axx.setHeight(0)

        lbl_axis = ["Q", "I"]
        channels = {
            'Input': {
                'X': self.prefix+chs_dict['IInp'],
                'Y': self.prefix+chs_dict['QInp']
            },
            'Reference': {
                'X': self.prefix+chs_dict['IRef'],
                'Y': self.prefix+chs_dict['QRef']
            }
        }
        graph_iq.setMinXRange(-1.0)
        graph_iq.setMaxXRange(1.0)
        graph_iq.setMinYRange(-1.0)
        graph_iq.setMaxYRange(1.0)

        graph_iq.setYLabels([lbl_axis[0]])
        graph_iq.setXLabels([lbl_axis[1]])
        graph_iq.setPlotTitle("I & Q Fasor")

        opts = dict(
            y_channel=channels['Input']['Y'],
            x_channel=channels['Input']['X'],
            name='Input',
            color='red',
            redraw_mode=2,
            lineStyle=1,
            lineWidth=3,
            symbol='o',
            symbolSize=10)
        graph_iq.addChannel(**opts)

        opts = dict(
            y_channel=channels['Reference']['Y'],
            x_channel=channels['Reference']['X'],
            name='Reference',
            color='blue',
            redraw_mode=2,
            lineStyle=1,
            lineWidth=3,
            symbol='o',
            symbolSize=10)
        graph_iq.addChannel(**opts)

        lay_llrf.addWidget(graph_iq)

    def setupGraphTime(self, lay_llrf, key, mode):
        graph = SiriusTimePlot(self)
        graph.setStyleSheet('min-height:15em;min-width:20em;max-height:15em;')
        graph.timeSpan = 120
        graph.maxRedrawRate = 2
        graph.setShowXGrid(True)
        graph.setShowYGrid(True)
        graph.backgroundColor = QColor(255, 255, 255)
        graph.setShowLegend(True)
        graph.setAxisColor(QColor(0, 0, 0))
        graph.setXLabels(["Time"])
        axx = graph.plotItem.getAxis('right')
        axx.setVisible(True)
        axx.setTicks([])
        axx.setWidth(0)
        axx = graph.plotItem.getAxis('top')
        axx.setVisible(True)
        axx.setTicks([])
        axx.setHeight(0)

        chs_dict = self.chs['SL']['Over']
        if self.section == 'SI':
            chs_dict = chs_dict[key]

        if mode == 'Amp':
            title = 'Amplitude'
            channels = {
                'Input': self.prefix+chs_dict['AInp'],
                'Reference': self.prefix+chs_dict['ARef']
            }
        else:
            title = 'Phase'
            channels = {
                'Input': self.prefix+chs_dict['PInp'],
                'Reference': self.prefix+chs_dict['PRef']
            }

        graph.setPlotTitle(title)
        graph.setYLabels([title])

        opts = dict(
            y_channel=channels['Input'],
            name='Input',
            color='red',
            lineStyle=1,
            lineWidth=3)
        graph.addYChannel(**opts)

        opts = dict(
            y_channel=channels['Reference'],
            name='Reference',
            color='blue',
            lineStyle=1,
            lineWidth=3)
        graph.addYChannel(**opts)

        lay_llrf.addWidget(graph)


class SlowLoopParametersDetails(SiriusDialog):
    """Slow Loop Control Parameters Details."""
    def __init__(self, parent=None, prefix='', section=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        self.setWindowTitle('Slow Loop Control Parameters Details')
        self._setupUi()

    def _setupUi(self):
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(20)

        self.title = QLabel(
            '<h3>Slow Loop Control Parameters Details</h3>', self,
            alignment=Qt.AlignCenter
        )
        lay.addWidget(self.title)

        if self.section == 'SI':
            for key, chs_dict in self.chs['SL']['Params'].items():
                self._setupDetails(lay, key, chs_dict)
        else:
            self._setupDetails(lay, None, self.chs['SL']['Params'])

    def _setupDetails(self, lay, key, chs_dict):
        if key:
            lay.addItem(QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Fixed))
            lay.addWidget(QLabel(
                f'<h4>LLRF {key}</h4>', self, alignment=Qt.AlignLeft))

        lay_llrf = QGridLayout()
        lay_llrf.setAlignment(Qt.AlignTop)
        lay_llrf.setHorizontalSpacing(9)
        lay_llrf.setVerticalSpacing(9)

        cb_inpsel = PyDMEnumComboBox(
            self, self.prefix+chs_dict['Inp']+'-Sel')
        lb_inpsel = SiriusLabel(
            self, self.prefix+chs_dict['Inp']+'-Sts')
        sb_pilimit = SiriusSpinbox(
            self, self.prefix+chs_dict['PIL']+'-SP')
        lb_pilimit = SiriusLabel(
            self, self.prefix+chs_dict['PIL']+'-RB')
        sb_ki = SiriusSpinbox(
            self, self.prefix+chs_dict['KI']+'-SP')
        lb_ki = SiriusLabel(
            self, self.prefix+chs_dict['KI']+'-RB')
        sb_kp = SiriusSpinbox(
            self, self.prefix+chs_dict['KP']+'-SP')
        lb_kp = SiriusLabel(
            self, self.prefix+chs_dict['KP']+'-RB')

        lay_llrf.addWidget(
            QLabel('<h4>SP/RB</h4>', self, alignment=Qt.AlignCenter),
            0, 2, 1, 2)
        lay_llrf.addWidget(
            QLabel('<h4>PI Limit</h4>', self, alignment=Qt.AlignCenter),
            1, 0, 1, 2)
        lay_llrf.addWidget(
            QLabel('<h4>Ki</h4>', self, alignment=Qt.AlignCenter), 2, 0, 1, 2)
        lay_llrf.addWidget(
            QLabel('<h4>Kp</h4>', self, alignment=Qt.AlignCenter), 3, 0, 1, 2)
        lay_llrf.addWidget(sb_pilimit, 1, 2, alignment=Qt.AlignRight)
        lay_llrf.addWidget(lb_pilimit, 1, 3, alignment=Qt.AlignLeft)
        lay_llrf.addWidget(sb_ki, 2, 2, alignment=Qt.AlignRight)
        lay_llrf.addWidget(lb_ki, 2, 3, alignment=Qt.AlignLeft)
        lay_llrf.addWidget(sb_kp, 3, 2, alignment=Qt.AlignRight)
        lay_llrf.addWidget(lb_kp, 3, 3, alignment=Qt.AlignLeft)

        lay_input = QGridLayout()
        lay_input.addWidget(
            QLabel('<h4>Loop Input</h4>', self, alignment=Qt.AlignCenter),
            1, 0, 1, 2)
        lay_input.addWidget(cb_inpsel, 2, 0, alignment=Qt.AlignRight)
        lay_input.addWidget(lb_inpsel, 2, 1, alignment=Qt.AlignLeft)
        lay_input.setRowStretch(0, 2)
        lay_input.setRowStretch(3, 2)
        lay_llrf.addLayout(lay_input, 1, 4, 3, 2)
        lay.addLayout(lay_llrf)


class ADCDACDetails(SiriusDialog):
    """Details for ADCs and DACs."""

    def __init__(self, parent=None, prefix='', section='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.system = system
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        title = 'ADCs and DACs Details'
        title += (f' - {self.system}' if self.section == 'SI' else '')
        self.setWindowTitle(title)
        if self.section == 'SI':
            self.syst_dict = self.chs['ADCs and DACs'][self.system]
        else:
            self.syst_dict = self.chs['ADCs and DACs']
        self._setupUi()

    def _setupUi(self):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)


        row = 0
        for key, val in self.syst_dict.items():
            if key == 'ADC Enable' or key == 'DAC Enable':
                pb_enbl = PyDMStateButton(
                    self, self.prefix+val[1]+'-Sel')
                led_enbl = SiriusLedState(
                    self, self.prefix+val[1])
                lay.addWidget(QLabel(val[0]), row, 0, 1, 2)
                lay.addWidget(pb_enbl, row, 2)
                lay.addWidget(led_enbl, row, 3)
            else:
                lb_value = SiriusLabel(self, self.prefix+val[1]+'-RB')
                lb_value.showUnits = True
                lay.addWidget(QLabel(key), row, 0)
                lay.addWidget(QLabel(val[0]), row, 1)
                lay.addWidget(lb_value, row, 2)
                lay.addWidget(
                    SiriusLineEdit(self, self.prefix+val[1]+'-SP'), row, 3)
            row += 1


class HardwareDetails(SiriusDialog):
    """Details related to the hardware."""

    def __init__(self, parent=None, prefix='', section='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.system = system
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        title = 'Hardware Details'
        title += (f' - {self.system}' if self.section == 'SI' else '')
        self.setWindowTitle(title)
        if self.section == 'SI':
            self.syst_dict = self.chs['Hardware'][self.system]
        else:
            self.syst_dict = self.chs['Hardware']
        self._setupUi()

    def _setupUi(self):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setHorizontalSpacing(18)
        lay.setVerticalSpacing(9)

        # FPGA Temps
        gbox_fpga = QGroupBox('FPGA Temps', self)
        self._setupLabelsLayout(gbox_fpga, True, self.syst_dict['FPGA'])

        # Mo1000 Temps
        gbox_mo1000 = QGroupBox('Mo1000 Temps', self)
        self._setupLabelsLayout(gbox_mo1000, False, self.syst_dict['Mo1000'])

        # Mi125 Temps
        gbox_mi125 = QGroupBox('Mi125 Temps', self)
        self._setupLabelsLayout(gbox_mi125, False, self.syst_dict['Mi125'])

        # GPIO
        gbox_gpio = QGroupBox('GPIO', self)
        self._setupLabelsLayout(gbox_gpio, False, self.syst_dict['GPIO'])

        # Clock Src and PLL
        frame_pll = QFrame(self)
        frame_pll.setFrameStyle(QFrame.Box)
        frame_pll.setObjectName('frame_pll')
        frame_pll.setStyleSheet("""
            #frame_pll{
                border: 2px solid gray;}
        """)
        lay_pll = QGridLayout(frame_pll)
        lay_pll.setSpacing(9)
        lay_pll.setSpacing(Qt.AlignTop)
        pb_clock = PyDMStateButton(
            self, self.prefix+self.syst_dict['Clock Src'])
        led_pll = SiriusLedState(self, self.prefix+self.syst_dict['PLL'])
        pb_init = PyDMStateButton(
            self, self.prefix+self.syst_dict['FPGA Init'])
        lay_pll.addWidget(QLabel('Clock Src'), 0, 0)
        lay_pll.addWidget(pb_clock, 0, 2)
        lay_pll.addWidget(QLabel('PLL'), 1, 0)
        lay_pll.addWidget(led_pll, 1, 1)
        lay_pll.addWidget(pb_init, 1, 2)

        # Cavity Type
        frame_type = QFrame(self)
        frame_type.setFrameStyle(QFrame.Box)
        frame_type.setObjectName('frame_type')
        frame_type.setStyleSheet("""
            #frame_type{
                border: 2px solid gray;}
        """)
        lay_type = QGridLayout(frame_type)
        lay_type.setSpacing(9)
        lay_type.setSpacing(Qt.AlignTop)
        lay_type.addWidget(QLabel('Cavity Type'), 0, 0)
        lay_type.addWidget(SiriusLabel(
            self, self.prefix+self.syst_dict['Cav Type']), 0, 1)

        # Errors
        gbox_err = QGroupBox('Errors', self)
        lay_err = QGridLayout(gbox_err)
        lay_err.setSpacing(9)
        lay_err.setAlignment(Qt.AlignTop)
        labels = ['EAPI', 'Mo1000', 'Mi125', 'SysMon',
            'GPIO', 'VCXO', 'Loops', 'RecPlay']
        self._setupByteMonitor(
            lay_err, True, labels, self.prefix+self.syst_dict['Errors'])

        # Internal Errors
        gbox_interr = QGroupBox('Internal Errors', self)
        lay_interr = QGridLayout(gbox_interr)
        lay_interr.setSpacing(9)
        lay_interr.setAlignment(Qt.AlignTop)
        labels = ['Loop Set', 'Loop Get', 'Loop Set Inconsistency',
            'Phs Ref Inconsistency', 'Amd Ref Inconsistency', 'Diag Get']
        self._setupByteMonitor(lay_interr, True, labels,
            self.prefix+self.syst_dict['Int. Errors'])

        # Init
        gbox_init = QGroupBox('Init', self)
        lay_init = QGridLayout(gbox_init)
        lay_init.setSpacing(9)
        lay_init.setAlignment(Qt.AlignTop)
        labels = ['GPIO', 'DACS', 'Mo1000', 'Mi125', 'Intercore FIFO', 'FPGA',
            'Cav Type', 'Double Write', 'Initial Settings', 'Disable Cavity B']
        self._setupByteMonitor(
            lay_init, False, labels, self.prefix+self.syst_dict['Init'])

        # Versions
        gbox_vers = QGroupBox('Versions', self)
        self._setupLabelsLayout(gbox_vers, False, self.syst_dict['Versions'])

        lay_vbox = QVBoxLayout()
        lay_vbox.setSpacing(9)
        lay_vbox.addWidget(gbox_mo1000)
        lay_vbox.addWidget(gbox_mi125)
        lay_vbox.addWidget(gbox_gpio)
        lay_vbox.addWidget(frame_pll)
        lay_vbox.addWidget(frame_type)

        lay.addWidget(gbox_fpga, 0, 0)
        lay.addWidget(gbox_vers, 1, 0, 1, 5)
        lay.addLayout(lay_vbox, 0, 1)
        lay.addWidget(gbox_err, 0, 2)
        lay.addWidget(gbox_interr, 0, 3)
        lay.addWidget(gbox_init, 0, 4)

    def _setupLabelsLayout(self, gbox, isFPGA, chs_dict):
        lay = QGridLayout(gbox)
        lay.setSpacing(9)
        lay.setAlignment(Qt.AlignTop)
        row = 0
        for key, val in chs_dict.items():
            lb_value = SiriusLabel(self, self.prefix+val)
            lb_value.showUnits = True
            lay.addWidget(QLabel(key, alignment=Qt.AlignRight), row, 0)
            lay.addWidget(lb_value, row, 1)
            row += 1
            if isFPGA and key.split()[-1] == 'Min':
                scale = SiriusScaleIndicator(self, self.prefix+val)
                lay.addWidget(scale, row, 1)
                row += 1

    def _setupByteMonitor(self, lay, isAlert, labels, pv):
        for bit in range(len(labels)):
            if isAlert:
                led = SiriusLedAlert(self, pv, bit)
            else:
                led = SiriusLedState(self, pv, bit)
            lay.addWidget(led, bit, 0)
            lay.addWidget(QLabel(labels[bit]), bit, 1)


class LoopsDetails(SiriusDialog):
    """IQ and Polar loops details."""

    def __init__(self, parent=None, prefix='', section='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.system = system
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        title = 'Loops Details'
        title += (f' - {self.system}' if self.section == 'SI' else '')
        self.setWindowTitle(title)
        if self.section == 'SI':
            self.syst_dict = self.chs['Loops'][self.system]
        else:
            self.syst_dict = self.chs['Loops']
        self._setupUi()

    def _setupUi(self):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        dtls = QTabWidget(self)
        dtls.setObjectName(self.section+'Tab')
        dtls.setStyleSheet(
            "#"+self.section+'Tab'+"::pane {"
            "    border-left: 2px solid gray;"
            "    border-bottom: 2px solid gray;"
            "    border-right: 2px solid gray;}")

        wid_controls = QWidget(self)
        wid_controls.setLayout(self._loopsControlLayout(self.syst_dict['Control']))
        dtls.addTab(wid_controls, 'Loops Control')

        wid_iq = QWidget(self)
        wid_iq.setLayout(self._iqLoopsLayout(self.syst_dict['Rect']))
        dtls.addTab(wid_iq, 'IQ Loops')

        lay.addWidget(dtls, 1, 0)

    def _loopsControlLayout(self, chs_dict):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        # Amp Loop Ref
        self._setupLabelEdit(lay, chs_dict, '24', 0, 0)

        # Phase Loop Ref
        self._setupLabelEdit(lay, chs_dict, '25', 1, 0)

        # Voltage Inc. Rate
        lb_vinc = SiriusLabel(self, self.prefix+chs_dict['29'][1]+'-RB',
            alignment=Qt.AlignRight)
        lb_vinc.showUnits = True
        lay.addWidget(QLabel('29'), 2, 0)
        lay.addWidget(QLabel(chs_dict['29'][0]), 2, 1)
        lay.addWidget(SiriusEnumComboBox(
            self, self.prefix+chs_dict['29'][1]+'-SP'),
            2, 2, alignment=Qt.AlignRight)
        lay.addWidget(lb_vinc, 2, 3)

        # Phase Inc. Rate
        lb_pinc = SiriusLabel(self, self.prefix+chs_dict['28'][1]+'-RB',
            alignment=Qt.AlignRight)
        lb_pinc.showUnits = True
        lay.addWidget(QLabel('28'), 3, 0)
        lay.addWidget(QLabel(chs_dict['28'][0]), 3, 1)
        lay.addWidget(SiriusEnumComboBox(
            self, self.prefix+chs_dict['28'][1]+'-SP'),
            3, 2, alignment=Qt.AlignRight)
        lay.addWidget(lb_pinc, 3, 3)

        # Look Reference
        pb_lookref = SiriusPushButton(
            self, self.prefix+chs_dict['106'][1])
        pb_lookref.setText('OFF')
        lay.addWidget(QLabel('106'), 4, 0)
        lay.addWidget(QLabel(chs_dict['106'][0]), 4, 1)
        lay.addWidget(pb_lookref, 4, 2, alignment=Qt.AlignRight)

        # Rect/Polar Mode Select
        lay.addWidget(QLabel('114'), 5, 0)
        lay.addWidget(QLabel(chs_dict['114'][0]), 5, 1)
        lay.addWidget(SiriusEnumComboBox(
            self, self.prefix+chs_dict['114'][1]),
            5, 2, alignment=Qt.AlignRight)

        # Quadrant Selection
        lay.addWidget(QLabel('107'), 6, 0)
        lay.addWidget(QLabel(chs_dict['107'][0]), 6, 1)
        lay.addWidget(SiriusEnumComboBox(
            self, self.prefix+chs_dict['107'][1]),
            6, 2, alignment=Qt.AlignRight)

        lay.addItem(QSpacerItem(40, 0, QSzPlcy.Fixed, QSzPlcy.Ignored), 0, 4)

        # Amp Ref Min (mV)
        self._setupLabelEdit(lay, chs_dict, '26', 0, 5)

        # Phase Ref Min
        self._setupLabelEdit(lay, chs_dict, '27', 1, 5)

        # Open Loop Gain
        self._setupLabelEdit(lay, chs_dict, '30', 2, 5)

        # Phase Correction Control
        lay.addWidget(QLabel('31'), 3, 5)
        lay.addWidget(QLabel(chs_dict['31'][0]), 3, 6)
        lay.addWidget(PyDMStateButton(
            self, self.prefix+chs_dict['31'][1]+'-Sel'), 3, 7)
        lay.addWidget(SiriusLedState(
            self, self.prefix+chs_dict['31'][1]+'-Sts'),
            3, 8, alignment=Qt.AlignHCenter)

        # Phase Correct Error
        lb_80 = SiriusLabel(self, self.prefix+chs_dict['80'][1],
            alignment=Qt.AlignRight)
        lb_80.showUnits = True
        lay.addWidget(QLabel('80'), 4, 5)
        lay.addWidget(QLabel(chs_dict['80'][0]), 4, 6)
        lay.addWidget(lb_80, 4, 8)

        # Phase Correct Control
        lb_81 = SiriusLabel(self, self.prefix+chs_dict['81'][1],
            alignment=Qt.AlignRight)
        lb_81.showUnits = True
        lay.addWidget(QLabel('81'), 5, 5)
        lay.addWidget(QLabel(chs_dict['81'][0]), 5, 6)
        lay.addWidget(lb_81, 5, 8)

        # Fwd Min Amp & Phs
        self._setupLabelEdit(lay, chs_dict, '125', 6, 5)

        # Equations (row = 7, column = 8)
        # pb_eq = QPushButton(
        #     qta.icon('fa5s.external-link-alt'), ' Equations', self)
        # connect_window(
        #     pq_eq, EquationsDetails, parent=self,
        #     prefix=self.prefix, section=self.section, system=self.system)

        return lay

    def _setupLabelEdit(self, lay, chs_dict, key, row, column):
        label = SiriusLabel(self, self.prefix+chs_dict[key][1]+'-RB')
        label.showUnits = True

        lay.addWidget(QLabel(key), row, column)
        lay.addWidget(QLabel(chs_dict[key][0]), row, column+1)
        lay.addWidget(SiriusLineEdit(
            self, self.prefix+chs_dict[key][1]+'-SP'), row, column+2)
        lay.addWidget(label, row, column+3, alignment=Qt.AlignRight)

    def _iqLoopsLayout(self, chs_dict):
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        rect_title_lay = QHBoxLayout()
        rect_title_lay.addWidget(QLabel(
            '<h3>Rect Loops</h3>', alignment=Qt.AlignCenter))
        rect_title_lay.addWidget(SiriusLedState(
            self, self.prefix+chs_dict['General']['RectMode']))

        rect_lay = self._statisticsLayout(chs_dict['General'], True)

        sl_lay = QVBoxLayout()
        sl_lay.setAlignment(Qt.AlignTop)
        sl_lay.addLayout(self._slowControlLayout(chs_dict['Slow']['Control']))
        sl_lay.addItem(QSpacerItem(0, 20, QSzPlcy.Ignored, QSzPlcy.Fixed))
        sl_lay.addLayout(self._statisticsLayout(chs_dict['Slow'], False))
        gbox_sl = QGroupBox('Slow Loop', self)
        gbox_sl.setLayout(sl_lay)

        # fl_lay = QVBoxLayout()
        # fl_lay.setAlignment(Qt.AlignTop)
        # fl_lay.addLayout(self._fastControlLayout(chs_dict['Fast']['Control']))
        # fl_lay.addLayout(self._statisticsLayout(chs_dict['Fast'], False))
        # gbox_fl = QGroupBox('Fast Loop', self)
        # gbox_fl.setLayout(fl_lay)

        lay.addLayout(rect_title_lay)
        lay.addItem(QSpacerItem(0, 20, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addLayout(rect_lay)
        lay.addWidget(gbox_sl)
        lay.addWidget(fl_lay)

        return lay

    def _statisticsLayout(self, chs_dict, isRect):
        lay = QGridLayout()
        lay.setHorizontalSpacing(18)

        lay.addWidget(QLabel(
            'In-Phase', alignment=Qt.AlignCenter), 0, 2)
        lay.addWidget(QLabel(
            'Quadrature', alignment=Qt.AlignCenter), 0, 3)
        if isRect:
            lay.addWidget(QLabel(
                'Amp', alignment=Qt.AlignCenter), 0, 4, 1, 4)
            lay.addWidget(QLabel(
                'Phase', alignment=Qt.AlignCenter), 0, 8)
        else:
            lay.addWidget(QLabel(
                'Amp', alignment=Qt.AlignCenter), 0, 4)
            lay.addWidget(QLabel(
                'Phase', alignment=Qt.AlignCenter), 0, 5)

        row = 1
        for key, dic in chs_dict.items():
            if key != 'RectMode' and key != 'Control':
                lay.addWidget(QLabel(
                    key, alignment=Qt.AlignCenter), row, 0)
                lay.addWidget(QLabel(
                    dic['Label'], alignment=Qt.AlignLeft), row, 1)
                column = 2
                for k, val in dic.items():
                    if k != 'Label' and val != '-':
                        lb = SiriusLabel(self, self.prefix+val)
                        lb.showUnits = True
                        lay.addWidget(lb, row, column)
                        column += 1
                    elif val == '-':
                        lay.addWidget(QLabel(
                            '-', alignment=Qt.AlignCenter), row, column)
                        column += 1
                row += 1

        return lay

    def _slowControlLayout(self, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)

        # Enable
        lay.addWidget(QLabel('100', alignment=Qt.AlignCenter), 1, 0)
        lay.addWidget(QLabel(chs_dict['100'][0]), 1, 1)
        lay.addWidget(PyDMStateButton(
            self, self.prefix+chs_dict['100'][1]+'-Sel'), 1, 2)
        lay.addWidget(SiriusLedState(
            self, self.prefix+chs_dict['100'][1]+'-Sts'),
            1, 3, alignment=Qt.AlignHCenter)

        # Input Selection
        lb_inpsel = SiriusLabel(self, self.prefix+chs_dict['110'][1]+'-Sts')
        lb_inpsel.showUnits = True
        lay.addWidget(QLabel('110', alignment=Qt.AlignCenter), 2, 0)
        lay.addWidget(QLabel(chs_dict['110'][0]), 2, 1)
        lay.addWidget(SiriusEnumComboBox(
            self, self.prefix+chs_dict['110'][1]+'-Sel'),
            2, 2, alignment=Qt.AlignRight)
        lay.addWidget(lb_inpsel, 2, 3)

        # PI Limit, Ki and Kp
        keys = ['13', '1', '0']
        row = 2
        column = 4
        max_column = 7
        for i in range(len(keys)):
            lb = SiriusLabel(self, self.prefix+chs_dict[keys[i]][1]+'-RB')
            lb.showUnits = True
            lay.addWidget(QLabel(
                keys[i], alignment=Qt.AlignCenter), row, column)
            lay.addWidget(QLabel(chs_dict[keys[i]][0]), row, column+1)
            lay.addWidget(SiriusLineEdit(
                self, self.prefix+chs_dict[keys[i]][1]+'-SP'), row, column+2)
            lay.addWidget(lb, row, column+3, alignment=Qt.AlignRight)
            column += 4
            if column > max_column:
                row += 1
                column = 0

        return lay
