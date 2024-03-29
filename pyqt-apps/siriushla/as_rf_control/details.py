"""Detail windows."""

from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import QFormLayout, QLabel, QSpacerItem, QTabWidget, \
    QSizePolicy as QSzPlcy, QGridLayout, QHBoxLayout, QGroupBox, QWidget

from pyqtgraph import PlotWidget, BarGraphItem

from ..widgets import SiriusDialog, SiriusLedAlert, \
    PyDMLedMultiChannel, SiriusConnectionSignal as _ConnSignal, \
    DetachableTabWidget, SiriusLabel
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
        lay = QFormLayout(self)
        lay.setLabelAlignment(Qt.AlignRight)
        lay.addRow(QLabel('<h4>Transm. Line - Detailed Status</h4>'))
        lay.addItem(QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Fixed))

        for widget_id, pvname in self.chs['TL Sts']['label_led'].items():
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

            lay.addRow(widget_id, wid)

        wid = QWidget()
        hlay = QHBoxLayout()
        wid.setLayout(hlay)
        hlay.setContentsMargins(0, 0, 0, 0)

        lb_circtin = SiriusLabel(
            self, self.prefix+self.chs['TL Sts']['Circulator Temp. In']['label'])
        lb_circtin.showUnits = True
        lb_circtin.setStyleSheet('qproperty-alignment: AlignLeft;')
        hlay.addWidget(lb_circtin)

        si_led_wid = PyDMLedMultiChannel(
            self, self.chs['TL Sts']['Circulator Temp. In']['led'])
        hlay.addWidget(si_led_wid)

        lay.addRow('Circulator T In: ', wid)

        for widget_id, pvname in self.chs['TL Sts']['label'].items():
            if not ((self.section == 'BO') and ('Combiner' == widget_id)):
                si_lbl_wid = SiriusLabel(
                    self, self.prefix+pvname)
                si_lbl_wid.showUnits = True
                si_lbl_wid.setStyleSheet('qproperty-alignment: AlignLeft;')
                lay.addRow(widget_id, si_lbl_wid)

        lay.addItem(QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Fixed))

        for widget_id, pvname in self.chs['TL Sts']['led'].items():
            if not ((self.section == 'BO') and ('Detector Load' in widget_id)):
                si_led_wid = SiriusLedAlert(
                    self, self.prefix+pvname)
                lay.addRow(widget_id + ": ", si_led_wid)

        self.setStyleSheet("""
            SiriusLabel{
                qproperty-alignment: AlignLeft;
            }
            QLed{
                max-width: 1.29em;
            }
            .QLabel{
                max-height:2em;
                qproperty-alignment: AlignRight;
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

        # inputs
        col = 0
        for name, dic in self.chs['LLRF Intlk Details']['Inputs'].items():
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

            lay.addWidget(gbox, 1, col)
            col += 1

        # timestamps
        gbox_time = QGroupBox('Timestamps', self)
        lay_time = QGridLayout(gbox_time)
        lay_time.setAlignment(Qt.AlignTop)
        lay_time.setHorizontalSpacing(9)
        lay_time.setVerticalSpacing(9)
        for idx, pvn in self.chs['LLRF Intlk Details']['Timestamps'].items():
            irow = int(idx)-1
            desc = QLabel('Interlock '+idx, self, alignment=Qt.AlignCenter)
            desc.setStyleSheet('QLabel{min-width:6em;}')
            lbl = SiriusLabel(self, self.prefix+pvn)
            lbl.showUnits = True
            lay_time.addWidget(desc, irow, 0)
            lay_time.addWidget(lbl, irow, 1)
        lay.addWidget(gbox_time, 1, col)


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
