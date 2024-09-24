"""Advanced details about cavity ramps."""

import qtawesome as qta
from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QGridLayout, QGroupBox, QLabel, QPushButton, \
    QSizePolicy as QSzPlcy, QSpacerItem, QTabWidget, QVBoxLayout, QWidget

from ...util import connect_window
from ...widgets import PyDMStateButton, SiriusDialog, SiriusLabel, \
    SiriusLedState, SiriusSpinbox, SiriusTimePlot
from ..util import SEC_2_CHANNELS
from .limits import LimitsDetails


class RampsDetails(SiriusDialog):
    """Advanced details about cavity ramps."""

    def __init__(self, parent=None, prefix='', section='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.system = system
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        self.title = 'Cavity Ramps Details'
        self.title += (f' - {self.system}' if self.section == 'SI' else '')
        self.setWindowTitle(self.title)
        if self.section == 'SI':
            self.syst_dict = self.chs['RampDtls'][self.system]
        else:
            self.syst_dict = self.chs['RampDtls']
        self._setupUi()

    def _setupUi(self):
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignTop)
        dtls = QTabWidget(self)
        dtls.setObjectName(self.section+'Tab')
        dtls.setStyleSheet(
            "#"+self.section+'Tab'+"::pane {"
            "    border-left: 2px solid gray;"
            "    border-bottom: 2px solid gray;"
            "    border-right: 2px solid gray;}")

        wid_controls = QWidget(self)
        wid_controls.setLayout(
            self._rampsControlLayout(self.syst_dict['Control']))
        dtls.addTab(wid_controls, 'Ramps Control')

        wid_top = QWidget(self)
        wid_top.setLayout(
            self._diagnosticsRampLayout(self.syst_dict['Diagnostics']))
        dtls.addTab(wid_top, 'Ramp Diagnostics')

        lay.addWidget(QLabel(
            f'<h4>{self.title}</h4>', alignment=Qt.AlignCenter))
        lay.addWidget(dtls)

    def _rampsControlLayout(self, chs_dict):
        lay = QGridLayout()
        lay.setSpacing(9)

        # General
        lay_gen = QGridLayout()
        lay_gen.setAlignment(Qt.AlignTop)
        lay_gen.setSpacing(9)
        gbox_gen = QGroupBox('General')
        gbox_gen.setLayout(lay_gen)

        # # Ramp Enable
        lay_gen.addWidget(QLabel('Ramp Enable'), 0, 1)
        lay_gen.addWidget(PyDMStateButton(
            self, self.prefix+chs_dict['Ramp Enable']+'-Sel'), 0, 2)
        lay_gen.addWidget(SiriusLedState(
            self, self.prefix+chs_dict['Ramp Enable']+'-Sts'),
            0, 3, alignment=Qt.AlignHCenter)

        # # Ramp Down Disable
        lay_gen.addWidget(QLabel('Ramp Down Disable'), 1, 1)
        lay_gen.addWidget(PyDMStateButton(
            self, self.prefix+chs_dict['Ramp Down Disable']+'-Sel'), 1, 2)
        lay_gen.addWidget(SiriusLedState(
            self, self.prefix+chs_dict['Ramp Down Disable']+'-Sts'),
            1, 3, alignment=Qt.AlignHCenter)

        # # Ramp Ready
        lay_gen.addWidget(QLabel('533', alignment=Qt.AlignCenter), 2, 0)
        lay_gen.addWidget(QLabel(chs_dict['533'][0]), 2, 1)
        lay_gen.addWidget(SiriusLedState(
            self, self.prefix+chs_dict['533'][1]),
            2, 3, alignment=Qt.AlignCenter)

        # # Ramp Increase Rate and Top
        self._setupTextInputLine(lay_gen, chs_dict, '360', 3)
        self._setupLabelLine(lay_gen, chs_dict, '536', 4)

        # # Limits
        pb_limit = QPushButton(
            qta.icon('fa5s.external-link-alt'), ' Limits', self)
        connect_window(
            pb_limit, LimitsDetails, parent=self, prefix=self.prefix,
            section=self.section, system=self.system, which='Ramp')
        pb_limit.setStyleSheet('min-width:8em')
        lay_gen.addWidget(pb_limit, 5, 1)

        # Graph
        graph_amp = SiriusTimePlot(self)
        graph_amp.setStyleSheet(
            'min-height:15em;min-width:20em;max-height:40em')
        graph_amp.maxRedrawRate = 2
        graph_amp.setShowXGrid(True)
        graph_amp.setShowYGrid(True)
        graph_amp.setShowLegend(True)
        graph_amp.setAutoRangeX(True)
        graph_amp.setAutoRangeY(True)
        graph_amp.setBackgroundColor(QColor(255, 255, 255))
        graph_amp.setTimeSpan(1800)
        graph_amp.maxRedrawRate = 2

        addrs = ['536', '184', '164']
        for addr in addrs:
            graph_amp.addYChannel(
                y_channel=self.prefix+chs_dict[addr][1],
                color=chs_dict[addr][2], name=chs_dict[addr][0],
                lineStyle=Qt.SolidLine, lineWidth=1)

        # Times
        lay_times = QGridLayout()
        lay_times.setAlignment(Qt.AlignTop)
        lay_times.setSpacing(9)
        gbox_times = QGroupBox('Times')
        gbox_times.setLayout(lay_times)

        # # T1 to T4
        addrs = ['356', '357', '358', '359']
        self.pvs = []
        for i in range(len(addrs)):
            self._setupTextInputLine(lay_times, chs_dict, addrs[i], i)

        # # Total
        total_channels = []
        for addr in addrs:
            total_channels.append(self.prefix+chs_dict[addr][1]+'-RB')

        lb_total = SiriusLabel(self)
        lb_total.precisionFromPV = False
        lb_total.precision = 2
        lb_total.showUnits = True
        rule = ('[{"name": "TextRule", "property": "Text", ' +
                '"expression":"ch[0] + ch[1] + ch[2] + ch[3]", ' +
                '"channels":[')
        for i, pv in enumerate(total_channels):
            rule += ('{"channel": "' + pv + '", "trigger": true}')
            if i != 3:
                rule += ', '
        rule += ']}]'
        lb_total.rules = rule

        lay_times.addWidget(QLabel('Total'), len(addrs)+1, 1)
        lay_times.addWidget(lb_total, len(addrs)+1, 2, alignment=Qt.AlignCenter)
        lay_times.addWidget(QLabel(
            '/410', alignment=Qt.AlignCenter), len(addrs)+1, 3)

        # Top
        lay_top = QGridLayout()
        lay_top.setAlignment(Qt.AlignTop)
        lay_top.setSpacing(9)
        gbox_top = QGroupBox('Top Ramp')
        gbox_top.setLayout(lay_top)

        self._setupLabelLine(lay_top, chs_dict, '164', 9)
        self._setupTextInputLine(lay_top, chs_dict, '362 mV', 10)
        self._setupTextInputLine(lay_top, chs_dict, '362 Vgap', 11)
        self._setupTextInputLine(lay_top, chs_dict, '364', 12)

        # Bot
        lay_bot = QGridLayout()
        lay_bot.setAlignment(Qt.AlignTop)
        lay_bot.setSpacing(9)
        gbox_bot = QGroupBox('Bottom Ramp')
        gbox_bot.setLayout(lay_bot)

        self._setupLabelLine(lay_bot, chs_dict, '184', 13)
        self._setupTextInputLine(lay_bot, chs_dict, '361 mV', 14)
        self._setupTextInputLine(lay_bot, chs_dict, '361 Vgap', 15)
        self._setupTextInputLine(lay_bot, chs_dict, '363', 16)

        # Slopes
        lay_slopes = QGridLayout()
        lay_slopes.setAlignment(Qt.AlignTop)
        lay_slopes.setSpacing(9)
        gbox_slopes = QGroupBox('Slopes')
        gbox_slopes.setLayout(lay_slopes)

        self._setupTextInputLine(lay_slopes, chs_dict, '365', 18)
        self._setupTextInputLine(lay_slopes, chs_dict, '366', 19)
        self._setupTextInputLine(lay_slopes, chs_dict, '367', 20)
        self._setupTextInputLine(lay_slopes, chs_dict, '368', 21)

        lay.addWidget(gbox_gen, 0, 0)
        lay.addWidget(graph_amp, 1, 0, 3, 1)
        lay.addWidget(gbox_times, 0, 2)
        lay.addWidget(gbox_top, 1, 2)
        lay.addWidget(gbox_bot, 2, 2)
        lay.addWidget(gbox_slopes, 3, 2)

        return lay

    def _setupTextInputLine(self, lay, chs_dict, key, row):
        label = SiriusLabel(self, self.prefix+chs_dict[key][1]+'-RB')
        label.showUnits = True

        lay.addWidget(QLabel(key.split()[0], alignment=Qt.AlignCenter), row, 0)
        lay.addWidget(QLabel(chs_dict[key][0]), row, 1)
        lay.addWidget(SiriusSpinbox(
            self, self.prefix+chs_dict[key][1]+'-SP'), row, 2)
        lay.addWidget(label, row, 3, alignment=Qt.AlignCenter)

    def _setupLabelLine(self, lay, chs_dict, key, row):
        label = SiriusLabel(self, self.prefix+chs_dict[key][1])
        label.showUnits = True

        lay.addWidget(QLabel(key, alignment=Qt.AlignCenter), row, 0)
        lay.addWidget(QLabel(chs_dict[key][0]), row, 1)
        lay.addWidget(label, row, 3, alignment=Qt.AlignCenter)

    def _diagnosticsRampLayout(self, chs_dict):
        lay = QVBoxLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(20)

        lb_addrs_top = ['163', '162'] if self.section == 'BO' else ['162']
        lb_addrs_bot = ['183'] if self.section == 'BO' else []
        led_addrs = ['531']

        gbox_top = QGroupBox('Top Ramp', self)
        gbox_top.setLayout(self._topOrBotRampLayout(
            chs_dict['Top'], lb_addrs_top, led_addrs))
        gbox_bot = QGroupBox('Bottom Ramp', self)
        gbox_bot.setLayout(self._topOrBotRampLayout(
            chs_dict['Bot'], lb_addrs_bot, led_addrs))

        lay.addWidget(gbox_top)
        lay.addWidget(gbox_bot)

        return lay

    def _topOrBotRampLayout(self, chs_dict, lb_addrs, led_addrs):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setVerticalSpacing(9)
        lay.setHorizontalSpacing(18)

        row = 0
        for addr in lb_addrs:
            lb = SiriusLabel(self, self.prefix+chs_dict[addr]['PV'])
            lb.showUnits = True
            lay.addWidget(QLabel(addr, alignment=Qt.AlignCenter), row, 0)
            lay.addWidget(QLabel(
                chs_dict[addr]['Label'],
                alignment=Qt.AlignLeft | Qt.AlignVCenter), row, 1)
            lay.addWidget(lb, row, 2)
            row += 1

        alt_row = 0
        column = 4 if lb_addrs != [] else 0
        for addr in led_addrs:
            lay.addWidget(QLabel(
                addr, alignment=Qt.AlignCenter), alt_row, column)
            lay.addWidget(QLabel(
                chs_dict[addr]['Label'],
                alignment=Qt.AlignLeft | Qt.AlignVCenter), alt_row, column+1)
            lay.addWidget(SiriusLedState(
                self, self.prefix+chs_dict[addr]['PV']),
                alt_row, column+2, alignment=Qt.AlignCenter)
            alt_row += 1

        lay.addItem(QSpacerItem(0, 15, QSzPlcy.Ignored, QSzPlcy.Fixed), row, 0)
        lay.addWidget(QLabel('In-Phase', alignment=Qt.AlignCenter), row+1, 2)
        lay.addWidget(QLabel('Quadrature', alignment=Qt.AlignCenter), row+1, 3)
        lay.addWidget(QLabel('Amp', alignment=Qt.AlignCenter), row+1, 4)
        lay.addWidget(QLabel('Phase', alignment=Qt.AlignCenter), row+1, 5)
        lay.addItem(QSpacerItem(
            12, 0, QSzPlcy.Fixed, QSzPlcy.Ignored), row+1, 6)
        lay.addWidget(QLabel(
            'Power', alignment=Qt.AlignCenter), row+1, 7, 1, 2)
        row += 2

        for key, dic in chs_dict.items():
            if key not in lb_addrs and key not in led_addrs:
                lay.addWidget(QLabel(
                    key, alignment=Qt.AlignHCenter), row, 0)
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
                            '-', alignment=Qt.AlignHCenter), row, column)
                        column += 1
                    if column == 6:
                        column += 1
                row += 1

        return lay
