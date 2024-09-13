"""SSA Currents Details."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QGroupBox, QHBoxLayout, QLabel, \
    QSizePolicy as QSzPlcy, QSpacerItem, QTabWidget, QVBoxLayout, QWidget

from ...widgets import SiriusDialog, SiriusLabel, SiriusLedState, SiriusSpinbox
from ..util import SEC_2_CHANNELS


class SSACurrentsDetails(SiriusDialog):
    """SSA Currents Details."""

    def __init__(self, parent, prefix='', section='', num='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.chs = SEC_2_CHANNELS[self.section]
        self.num = num
        self.system = system
        self.setObjectName(self.section+'App')
        self.curr_pvs = {}
        if self.section == 'SI':
            self.syst_dict = self.chs['SSACurr'][self.system]
            self.title = f'SSA 0{self.num} Currents Details'
        else:
            self.syst_dict = self.chs['SSACurr']
            self.title = 'SSA Currents Details'
        self.setWindowTitle(f'{self.section} {self.title}')
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

        wid_diag = QWidget(self)
        wid_diag.setLayout(self._setupDiagLay())
        dtls.addTab(wid_diag, 'Diagnostics')

        wid_graphs = QWidget(self)
        wid_graphs.setLayout(self._setupAlarmLay())
        dtls.addTab(wid_graphs, 'Alarm Limits')

        lay.addWidget(QLabel(
            f'<h4>{self.title}</h4>', alignment=Qt.AlignCenter))
        lay.addWidget(dtls)

    def _setupDiagLay(self):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(18)

        row = 0
        column = 0
        if self.section == 'SI':
            for i in range(1, 9):
                row_label = ''
                if column == 0:
                    row_label = 'left'
                elif column == 4:
                    row_label = 'right'

                lay.addLayout(self._setupHeatSinkLay(
                    i, self.syst_dict['HeatSink'], row_label), row, column)

                column += 1
                if column == 2:
                    if row == 0:
                        gbox_preamp = QGroupBox('Pre Amplifiers')
                        gbox_preamp.setLayout(self._setupPreAmpLay(self.syst_dict['PreAmp']))
                        lay.addWidget(gbox_preamp, row, column)
                    column += 1
                elif column == 5:
                    lay.addItem(QSpacerItem(
                        0, 9, QSzPlcy.Ignored, QSzPlcy.Fixed), row+1, 0)
                    column = 0
                    row += 2

            gbox_total = QGroupBox('Total Current')
            gbox_total.setLayout(self._setupTotalLay())
            lay.addWidget(gbox_total, 2, 2)
        else:
            for i in range(1, 7):
                row_label = ''
                if column == 0:
                    row_label = 'left'
                elif column == 6:
                    row_label = 'right'

                lay.addLayout(self._setupHeatSinkLay(
                    i, self.syst_dict['HeatSink'], row_label),
                    row, column, 2, 1)

                column += 1
                if column == 3:
                    # PreAmp
                    gbox_preamp = QGroupBox('Pre Amplifiers')
                    gbox_preamp.setLayout(self._setupPreAmpLay(self.syst_dict['PreAmp']))
                    lay.addWidget(gbox_preamp, row, column)

                    # Power
                    lay.addLayout(self._setupPowerLay(
                        self.syst_dict['Pwr']), row+1, column)

                    # Total Current
                    lb_total = SiriusLabel(
                        self, self.prefix+self.syst_dict['Total'])
                    lb_total.showUnits = True
                    lay_total = QHBoxLayout()
                    lay_total.addWidget(QLabel(
                        '<h4>Total Current</h4>', alignment=Qt.AlignCenter))
                    lay_total.addWidget(lb_total, alignment=Qt.AlignCenter)
                    lay.addLayout(lay_total, row+2, column)

                    column += 1

        return lay

    def _setupHeatSinkLay(self, hs_num, chs_dict, row_label=''):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        if self.section == 'SI':
            lay.addWidget(QLabel(
                f'<h4>Heat Sink {hs_num}</h4>', alignment=Qt.AlignCenter),
                0, 1, 1, 4)
            lay.addWidget(QLabel(
                '<h4>A</h4>', alignment=Qt.AlignCenter), 1, 1, 1, 2)
            lay.addWidget(QLabel(
                '<h4>B</h4>', alignment=Qt.AlignCenter), 1, 3, 1, 2)

            # Currents
            for i in range(1, 9):
                pv_a_1 = self._substitute_macros(
                    self.prefix+chs_dict['Curr'], hs_num, 'A', i, 1)
                pv_a_2 = self._substitute_macros(
                    self.prefix+chs_dict['Curr'], hs_num, 'A', i, 2)
                pv_b_1 = self._substitute_macros(
                    self.prefix+chs_dict['Curr'], hs_num, 'B', i, 1)
                pv_b_2 = self._substitute_macros(
                    self.prefix+chs_dict['Curr'], hs_num, 'A', i, 2)
                if i == 1:
                    self.curr_pvs[hs_num] = [pv_a_1, pv_a_2, pv_b_1, pv_b_2]
                else:
                    self.curr_pvs[hs_num].append(pv_a_1)
                    self.curr_pvs[hs_num].append(pv_a_2)
                    self.curr_pvs[hs_num].append(pv_b_1)
                    self.curr_pvs[hs_num].append(pv_b_2)

                lb_a_1 = SiriusLabel(self, pv_a_1)
                lb_a_1.showUnits = True
                lb_a_2 = SiriusLabel(self, pv_a_2)
                lb_a_2.showUnits = True
                lb_b_1 = SiriusLabel(self, pv_b_1)
                lb_b_1.showUnits = True
                lb_b_2 = SiriusLabel(self, pv_b_2)
                lb_b_2.showUnits = True

                if row_label == 'left':
                    lay.addWidget(QLabel(
                        f'M0{i}', alignment=Qt.AlignCenter), i+1, 0)
                elif row_label == 'right':
                    lay.addWidget(QLabel(
                        f'M0{i}', alignment=Qt.AlignCenter), i+1, 5)
                lay.addWidget(lb_a_1, i+1, 1)
                lay.addWidget(lb_a_2, i+1, 2)
                lay.addWidget(lb_b_1, i+1, 3)
                lay.addWidget(lb_b_2, i+1, 4)
                row = i+2

            # Power
            lay.addWidget(QLabel(
                '<h4>Power</h4>', alignment=Qt.AlignCenter), row, 1, 1, 4)
            column = 1
            for key, val in chs_dict.items():
                if key != 'Curr':
                    lb_pwr = SiriusLabel(
                        self, self._substitute_macros(self.prefix+val, hs_num))
                    lb_pwr.showUnits = True
                    lay.addWidget(QLabel(
                        f'<h4>{key}</h4>', alignment=Qt.AlignCenter),
                        row+1, column)
                    lay.addWidget(lb_pwr, row+2, column)
                    column += 1
        else:
            lay.addWidget(QLabel(
                f'<h4>Heat Sink {hs_num}</h4>', alignment=Qt.AlignCenter),
                0, 1, 1, 2)

            # Currents
            for i in range(1, 17):
                if i < 10:
                    m_num = f'0{i}'
                else:
                    m_num = i
                pv_curr_1 = self._substitute_macros(
                    self.prefix+chs_dict['Curr'],
                    hs_num, m_num=m_num, curr_num=1)
                pv_curr_2 = self._substitute_macros(
                    self.prefix+chs_dict['Curr'],
                    hs_num, m_num=m_num, curr_num=2)
                if i == 1:
                    self.curr_pvs[hs_num] = [pv_curr_1, pv_curr_2]
                else:
                    self.curr_pvs[hs_num].append(pv_curr_1)
                    self.curr_pvs[hs_num].append(pv_curr_2)

                lb_curr_1 = SiriusLabel(self, pv_curr_1)
                lb_curr_1.showUnits = True
                lb_curr_2 = SiriusLabel(self, pv_curr_2)
                lb_curr_2.showUnits = True

                if row_label == 'left':
                    lay.addWidget(QLabel(
                        f'M{m_num}', alignment=Qt.AlignCenter), i+1, 0)
                elif row_label == 'right':
                    lay.addWidget(QLabel(
                        f'M{m_num}', alignment=Qt.AlignCenter), i+1, 5)
                lay.addWidget(lb_curr_1, i+1, 1)
                lay.addWidget(lb_curr_2, i+1, 2)
                row = i+2

            # Power
            lay.addWidget(QLabel(
                '<h4>Power</h4>', alignment=Qt.AlignCenter), row, 1, 1, 2)
            column = 1
            for key, val in chs_dict.items():
                if key != 'Curr':
                    lb_pwr = SiriusLabel(
                        self, self._substitute_macros(self.prefix+val, hs_num))
                    lb_pwr.showUnits = True
                    lay.addWidget(QLabel(
                        f'<h4>{key}</h4>', alignment=Qt.AlignCenter),
                        row+1, column)
                    lay.addWidget(lb_pwr, row+2, column)
                    column += 1
                if column > 2:
                    row += 3
                    column = 1

        return lay

    def _setupPreAmpLay(self, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignVCenter)
        lay.setSpacing(9)

        row = 0
        column = 0
        if self.section == 'SI':
            for i in range(2, 9, 2):
                # Heat Sinks
                label = QLabel(
                    f'<h4>Heat Sink {i}</h4>', alignment=Qt.AlignCenter)
                label.setStyleSheet("min-width:6em;")
                lb_1 = SiriusLabel(self, self._substitute_macros(
                    self.prefix+chs_dict['HS'], i, curr_num='1'))
                lb_1.showUnits = True
                lb_2 = SiriusLabel(self, self._substitute_macros(
                    self.prefix+chs_dict['HS'], i, curr_num='2'))
                lb_2.showUnits = True

                lay.addWidget(label, row, column)
                lay.addWidget(lb_1, row+1, column)
                lay.addWidget(lb_2, row+2, column)

                column += 1
                if column == 1:
                    if row == 0:
                        # Pre Amp
                        label = QLabel(
                            '<h4>PreAmp</h4>', alignment=Qt.AlignCenter)
                        label.setStyleSheet("min-width:6em;")
                        lb_1 = SiriusLabel(self, self._substitute_macros(
                            self.prefix+chs_dict['PreAmp'], curr_num='1'))
                        lb_1.showUnits = True
                        lb_2 = SiriusLabel(self, self._substitute_macros(
                            self.prefix+chs_dict['PreAmp'], curr_num='2'))
                        lb_2.showUnits = True

                        lay.addWidget(label, row, column)
                        lay.addWidget(lb_1, row+1, column)
                        lay.addWidget(lb_2, row+2, column)
                        column += 1
                    else:
                        # TDK Source
                        label = QLabel(
                            '<h4>TDK Source</h4>', alignment=Qt.AlignCenter)
                        label.setStyleSheet("min-width:6em;")

                        lay.addWidget(label, row, column)
                        lay.addWidget(SiriusLedState(
                            self, self._substitute_macros(
                                self.prefix+chs_dict['TDK'])), row+1, column,
                                alignment=Qt.AlignCenter)
                        column += 1

                if column > 2:
                    row += 3
                    column = 0
        else:
            # Heat Sinks
            hs_nums = [1, 4, 3, 6]
            m_nums = ['01', '01', '17', '17']
            row = 0
            column = 0
            for i, hs_num in enumerate(hs_nums):
                lb_1 = SiriusLabel(self, self._substitute_macros(
                    self.prefix+chs_dict['HS'], hs_num=hs_num, m_num=m_nums[i],
                    curr_num='1'))
                lb_1.showUnits = True
                lb_2 = SiriusLabel(self, self._substitute_macros(
                    self.prefix+chs_dict['HS'], hs_num=hs_num, m_num=m_nums[i],
                    curr_num='2'))
                lb_2.showUnits = True

                lay.addWidget(QLabel(
                    f'<h4>Heat Sink {hs_num}</h4>',
                    alignment=Qt.AlignCenter), row, column, 1, 2)
                lay.addWidget(lb_1, row+1, column)
                lay.addWidget(lb_2, row+1, column+1)

                column += 2
                if column == 4:
                    row += 2
                    column = 0

            lay_dc = QHBoxLayout()
            lay_dc.addWidget(QLabel(
                '<h4>DC-DC Conv.</h4>', alignment=Qt.AlignCenter))
            lay_dc.addWidget(SiriusLedState(
                self, self.prefix+chs_dict['DC']), alignment=Qt.AlignCenter)
            lay.addItem(QSpacerItem(
                0, 9, QSzPlcy.Ignored, QSzPlcy.Fixed), row, 0)
            lay.addLayout(lay_dc, row+1, 1, 1, 2)

            #     column += 1
            #     if column == 1:
            #         if row == 0:
            #             # Pre Amp
            #             label = QLabel(
            #                 '<h4>PreAmp</h4>', alignment=Qt.AlignCenter)
            #             label.setStyleSheet("min-width:6em;")
            #             lb_1 = SiriusLabel(self, self._substitute_macros(
            #                 self.prefix+chs_dict['PreAmp'], curr_num='1'))
            #             lb_1.showUnits = True
            #             lb_2 = SiriusLabel(self, self._substitute_macros(
            #                 self.prefix+chs_dict['PreAmp'], curr_num='2'))
            #             lb_2.showUnits = True

            #             lay.addWidget(label, row, column)
            #             lay.addWidget(lb_1, row+1, column)
            #             lay.addWidget(lb_2, row+2, column)
            #             column += 1
            #         else:
            #             # TDK Source
            #             label = QLabel(
            #                 '<h4>TDK Source</h4>', alignment=Qt.AlignCenter)
            #             label.setStyleSheet("min-width:6em;")

            #             lay.addWidget(label, row, column)
            #             lay.addWidget(SiriusLedState(
            #                 self, self._substitute_macros(
            #                     self.prefix+chs_dict['TDK'])), row+1, column,
            #                     alignment=Qt.AlignCenter)
            #             column += 1

            #     if column > 2:
            #         row += 3

        return lay

    def _setupPowerLay(self, chs_dict):
        lay = QHBoxLayout()
        lay.setSpacing(9)

        for k, dic in chs_dict.items():
            gbox = QGroupBox(f'{k} Power')
            lay_pwr = QVBoxLayout()
            lay_pwr.setAlignment(Qt.AlignVCenter)
            lay_pwr.setSpacing(9)
            gbox.setLayout(lay_pwr)

            lb_fwd = SiriusLabel(self, self.prefix+dic['Fwd'])
            lb_fwd.showUnits = True
            lb_rev = SiriusLabel(self, self.prefix+dic['Rev'])
            lb_rev.showUnits = True

            lay_pwr.addWidget(QLabel('<h4>Forward</h4>'))
            lay_pwr.addWidget(lb_fwd)
            lay_pwr.addWidget(QLabel('<h4>Reverse</h4>'))
            lay_pwr.addWidget(lb_rev)

            lay.addWidget(gbox)

        return lay

    def _setupTotalLay(self):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignVCenter)
        lay.setSpacing(9)

        row = 0
        column = 0

        # Racks 1 to 4
        total_pvs = []
        for i in range(1, 5):
            total_pvs.append(self._substitute_macros(
                self.prefix+self.syst_dict['RacksTotal'], rack_num=i))
            lb_total = SiriusLabel(self, total_pvs[-1])
            lb_total.showUnits = True

            lay.addWidget(QLabel(
                f'<h4>Rack {i}</h4>', alignment=Qt.AlignCenter), row, column)
            lay.addWidget(lb_total, row+1, column)
            column += 2
            if column > 2:
                row += 2
                column = 0

        # Total
        sum_expr = '"ch[0] + '
        for i in range(1, 4):
            sum_expr += f'ch[{i}] + '
        sum_expr += 'ch[4]"'

        lb_total = SiriusLabel(self)
        lb_total.showUnits = True
        rule = ('[{"name": "TextRule", "property": "Text", ' +
                '"expression": ' + '"ch[0] + ch[1] + ch[2] + ch[3]", ' +
                '"channels": [')
        for pv in total_pvs:
            rule += ('{"channel": "' + pv + '", "trigger": true}, ')
        rule += ']}]'
        lb_total.rules = rule

        lay.addWidget(QLabel(
            '<h4>Total</h4>', alignment=Qt.AlignCenter), row, 1)
        lay.addWidget(lb_total, row+1, 1, alignment=Qt.AlignCenter)

        return lay

    def _setupAlarmLay(self):
        lay = QHBoxLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(18)

        # Offsets
        lay_off = QGridLayout()
        lay_off.setAlignment(Qt.AlignCenter)
        lay_off.setSpacing(9)
        gbox_off = QGroupBox('Offsets (dB)')
        gbox_off.setLayout(lay_off)

        row = 0
        for _, lst in self.syst_dict['Offsets'].items():
            lay_off.addWidget(QLabel(
                f'<h4>{lst[0]}</h4>', alignment=Qt.AlignCenter), row, 0)
            lay_off.addWidget(SiriusSpinbox(
                self, self._substitute_macros(self.prefix+lst[1])), row, 2)
            row += 1
        lay_off.addItem(QSpacerItem(
            27, 0, QSzPlcy.Fixed, QSzPlcy.Ignored), 0, 1)
        lay.addWidget(gbox_off)

        # Alarms
        lay_alarms = QGridLayout()
        lay_alarms.setAlignment(Qt.AlignVCenter)
        lay_alarms.setSpacing(9)
        gbox_alarms = QGroupBox('Alarms')
        gbox_alarms.setLayout(lay_alarms)

        column = 0
        for _, dic in self.syst_dict['Alarms'].items():
            lay_alarms.addWidget(QLabel(
                f'<h4>{dic["Label"]}</h4>', alignment=Qt.AlignCenter),
                0, column, 1, 2)
            row = 1
            for key, val in dic.items():
                if key != 'Label':
                    lay_alarms.addWidget(QLabel(
                        f'<h4>{key}</h4>', alignment=Qt.AlignCenter),
                        row, column)
                    lay_alarms.addWidget(SiriusSpinbox(
                        self, self._substitute_macros(self.prefix+val)),
                        row, column+1)
                    row += 1
            column += 2
        lay.addWidget(gbox_alarms)

        return lay

    def _substitute_macros(self, pv_name, hs_num='', letter='', m_num='',
    curr_num='', rack_num=''):
        pv_name = pv_name.replace('$(NB)', str(self.num))
        if hs_num:
            pv_name = pv_name.replace('$(hs_num)', str(hs_num))
        if letter:
            pv_name = pv_name.replace('$(letter)', str(letter))
        if m_num:
            pv_name = pv_name.replace('$(m_num)', str(m_num))
        if curr_num:
            pv_name = pv_name.replace('$(curr_num)', str(curr_num))
        if rack_num:
            pv_name = pv_name.replace('$(rack_num)', str(rack_num))
        return pv_name
