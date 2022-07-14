"""Detail windows."""

from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import QFormLayout, QLabel, QSpacerItem, QTabWidget, \
    QSizePolicy as QSzPlcy, QGridLayout, QHBoxLayout, QGroupBox

from pyqtgraph import PlotWidget, BarGraphItem

from pydm.widgets import PyDMLabel

from ..widgets import SiriusDialog, SiriusLedAlert, \
    PyDMLedMultiChannel, SiriusConnectionSignal as _ConnSignal, \
    DetachableTabWidget
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
            lbl = PyDMLabel(self, self.prefix+cell[0])
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
        lb_coup = PyDMLabel(self, self.prefix+ch_coup)
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

        self.led_hdflwrt1 = SiriusLedAlert(
            self, self.prefix+self.chs['Cav Sts']['FlwRt'][0])
        self.led_hdflwrt2 = SiriusLedAlert(
            self, self.prefix+self.chs['Cav Sts']['FlwRt'][1])
        self.led_hdflwrt3 = SiriusLedAlert(
            self, self.prefix+self.chs['Cav Sts']['FlwRt'][2])
        lay_flwrt = QFormLayout()
        lay_flwrt.setHorizontalSpacing(9)
        lay_flwrt.setVerticalSpacing(9)
        lay_flwrt.setLabelAlignment(Qt.AlignRight)
        lay_flwrt.setFormAlignment(Qt.AlignTop)
        lb_flwrf = QLabel('Flow Switches', self)
        lb_flwrf.setStyleSheet(
            'font-weight:bold; qproperty-alignment:AlignCenter;')
        lay_flwrt.addRow(lb_flwrf)
        lay_flwrt.addRow('Flow Switch 1: ', self.led_hdflwrt1)
        lay_flwrt.addRow('Flow Switch 2: ', self.led_hdflwrt2)
        lay_flwrt.addRow('Flow Switch 3: ', self.led_hdflwrt3)

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
            PyDMLabel{
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
        self.lb_circtin = PyDMLabel(
            self, self.prefix+self.chs['TL Sts']['Circ TIn'])
        self.lb_circtin.showUnits = True
        self.lb_circtin.setStyleSheet('qproperty-alignment: AlignLeft;')
        self.lb_circtout = PyDMLabel(
            self, self.prefix+self.chs['TL Sts']['Circ TOut'])
        self.lb_circtout.showUnits = True
        self.lb_circtout.setStyleSheet('qproperty-alignment: AlignLeft;')
        self.led_circarc = SiriusLedAlert(
            self, self.prefix+self.chs['TL Sts']['Circ Arc'])
        if self.section == 'SI':
            self.led_loadarc = SiriusLedAlert(
                self, self.prefix+self.chs['TL Sts']['Load Arc'])
        self.led_circflwrt = SiriusLedAlert(
            self, self.prefix+self.chs['TL Sts']['Circ FlwRt'])
        self.led_loadflwrt = SiriusLedAlert(
            self, self.prefix+self.chs['TL Sts']['Load FlwRt'])
        self.led_circintlkop = SiriusLedAlert(
            self, self.prefix+self.chs['TL Sts']['Circ Intlk'])

        lay = QFormLayout(self)
        lay.setLabelAlignment(Qt.AlignRight)
        lay.addRow(QLabel('<h4>Transm. Line - Detailed Status</h4>'))
        lay.addItem(QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addRow('Circulator T In: ', self.lb_circtin)
        lay.addRow('Circulator T Out: ', self.lb_circtout)
        lay.addItem(QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addRow('Circulator Arc Detector: ', self.led_circarc)
        if self.section == 'SI':
            lay.addRow('Load Arc Detector: ', self.led_loadarc)
        lay.addRow('Circulator Flow: ', self.led_circflwrt)
        lay.addRow('Load Flow: ', self.led_loadflwrt)
        lay.addRow('Circulator Intlk: ', self.led_circintlkop)

        self.setStyleSheet("""
            PyDMLabel{
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
            lbl = PyDMLabel(self, self.prefix+pvn)
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
