"""Advanced detail windows."""

import qtawesome as qta
from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QGridLayout, QGroupBox, QHBoxLayout, QLabel, \
    QSizePolicy as QSzPlcy, QSpacerItem, QTabWidget, QVBoxLayout, \
    QWidget, QPushButton

from ..util import connect_window
from ..widgets import PyDMStateButton, SiriusDialog, SiriusLabel, \
    SiriusLedAlert, SiriusLedState, SiriusSpinbox, SiriusScaleIndicator, \
    SiriusEnumComboBox, SiriusPushButton, SiriusTimePlot, SiriusLineEdit

from .util import SEC_2_CHANNELS


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
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignTop)
        dtls = QTabWidget(self)
        dtls.setObjectName(self.section+'Tab')
        dtls.setStyleSheet(
            "#"+self.section+'Tab'+"::pane {"
            "    border-left: 2px solid gray;"
            "    border-bottom: 2px solid gray;"
            "    border-right: 2px solid gray;}")

        wid_input = QWidget(self)
        wid_input.setLayout(self._rfInputLayout(self.syst_dict['Input']))
        dtls.addTab(wid_input, 'RF Inputs')

        wid_controls = QWidget(self)
        wid_controls.setLayout(
            self._controlsLayout(self.syst_dict['Control']))
        dtls.addTab(wid_controls, 'Controls')

        lay.addWidget(QLabel(
            '<h4>Advanced ADCs and DACs Details</h4>',
            alignment=Qt.AlignCenter))
        lay.addWidget(dtls)

    def _rfInputLayout(self, chs_dict):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setVerticalSpacing(9)
        lay.setHorizontalSpacing(18)

        lay.addWidget(QLabel(
            'In-Phase', alignment=Qt.AlignCenter), 0, 2)
        lay.addWidget(QLabel(
            'Quadrature', alignment=Qt.AlignCenter), 0, 3)
        lay.addWidget(QLabel(
            'Amp', alignment=Qt.AlignCenter), 0, 4, 1, 4)
        lay.addWidget(QLabel(
            'Phase', alignment=Qt.AlignCenter), 0, 8)

        row = 1
        for key, dic in chs_dict.items():
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

    def _controlsLayout(self, chs_dict):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        for k, sub_dict in chs_dict.items():
            row = 1
            if k == 'ADC':
                offset = 0
            else:
                offset = 5

            for key, val in sub_dict.items():
                if key == 'Enable':
                    pb_enbl = PyDMStateButton(
                        self, self.prefix+val[1]+'-Sel')
                    led_enbl = SiriusLedState(
                        self, self.prefix+val[1])
                    lay.addWidget(QLabel(val[0]), row, offset, 1, 2)
                    lay.addWidget(pb_enbl, row, offset+2)
                    lay.addWidget(led_enbl, row, offset+3,
                        alignment=Qt.AlignCenter)
                else:
                    lb_value = SiriusLabel(self, self.prefix+val[1]+'-RB')
                    lb_value.showUnits = True
                    lay.addWidget(QLabel(key), row, offset)
                    lay.addWidget(QLabel(val[0]), row, offset+1)
                    lay.addWidget(
                        SiriusSpinbox(self, self.prefix+val[1]+'-SP'),
                        row, offset+2)
                    lay.addWidget(lb_value, row, offset+3)
                row += 1

        lay.addItem(QSpacerItem(20, 0, QSzPlcy.Fixed, QSzPlcy.Ignored), 1, 4)

        return lay


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

        lay.addWidget(QLabel(
            '<h4>Advanced Hardware Details</h4>',
            alignment=Qt.AlignCenter), 0, 0, 1, 5)

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

        # Clock Src, Loop Trigger and PLL
        gbox_pll = QGroupBox(self)
        lay_pll = QGridLayout(gbox_pll)
        lay_pll.setSpacing(9)
        lay_pll.setAlignment(Qt.AlignTop)

        pb_clock = PyDMStateButton(
            self, self.prefix+self.syst_dict['Clock Src'])
        pb_trig = SiriusPushButton(
            self, self.prefix+self.syst_dict['Loop Trigger'], 'Loop Trigger')
        pb_trig.setStyleSheet('min-width: 6em')
        led_pll = SiriusLedState(self, self.prefix+self.syst_dict['PLL'])
        pb_init = PyDMStateButton(
            self, self.prefix+self.syst_dict['FPGA Init'])
        lay_pll.addWidget(QLabel(
            'Clock Src', alignment=Qt.AlignRight | Qt.AlignVCenter), 0, 0)
        lay_pll.addWidget(pb_clock, 0, 1)
        lay_pll.addWidget(QLabel(
            'Loop Trigger', alignment=Qt.AlignRight | Qt.AlignVCenter), 1, 0)
        lay_pll.addWidget(pb_trig, 1, 1)
        lay_pll.addWidget(QLabel(
            'PLL', alignment=Qt.AlignRight | Qt.AlignVCenter), 2, 0)
        lay_pll.addWidget(pb_init, 2, 1)
        lay_pll.addWidget(led_pll, 2, 2)

        # Cavity Type
        gbox_type = QGroupBox(self)
        lay_type = QGridLayout(gbox_type)
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
        pb_clear = SiriusPushButton(
            self, self.prefix+self.syst_dict['Int. Err. Clear'])
        pb_clear.setText('Clear')
        lay_interr.addWidget(pb_clear, len(labels)+1, 0)

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
        lay_vbox.addWidget(gbox_pll)
        lay_vbox.addWidget(gbox_type)

        lay.addWidget(gbox_fpga, 1, 0)
        lay.addWidget(gbox_vers, 2, 0, 1, 5)
        lay.addLayout(lay_vbox, 1, 1)
        lay.addWidget(gbox_err, 1, 2)
        lay.addWidget(gbox_interr, 1, 3)
        lay.addWidget(gbox_init, 1, 4)

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
            lay.addWidget(led, bit, 0, alignment=Qt.AlignHCenter)
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
            self._loopsControlLayout(self.syst_dict['Control']))
        dtls.addTab(wid_controls, 'Loops Control')

        wid_iq = QWidget(self)
        wid_iq.setLayout(self._specificLoopsLayout('Rect'))
        dtls.addTab(wid_iq, 'IQ Loops')

        wid_polar = QWidget(self)
        wid_polar.setLayout(self._specificLoopsLayout('Polar'))
        dtls.addTab(wid_polar, 'Polar Loops')

        lay.addWidget(QLabel(
            '<h4>Advanced Loops Details</h4>', alignment=Qt.AlignCenter))
        lay.addWidget(dtls)

    def _loopsControlLayout(self, chs_dict):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        # Amp Loop Ref
        self._setupLabelEdit(lay, chs_dict, '24 mV', 0, 0)
        self._setupLabelEdit(lay, chs_dict, '24 VGap', 1, 0)

        # Phase Loop Ref
        self._setupLabelEdit(lay, chs_dict, '25', 2, 0)

        # Voltage Inc. Rate
        lb_vinc = SiriusLabel(self, self.prefix+chs_dict['29'][1]+'-RB',
            alignment=Qt.AlignCenter)
        lb_vinc.showUnits = True
        lay.addWidget(QLabel('29'), 3, 0)
        lay.addWidget(QLabel(chs_dict['29'][0]), 3, 1)
        lay.addWidget(SiriusEnumComboBox(
            self, self.prefix+chs_dict['29'][1]+'-SP'),
            3, 2, alignment=Qt.AlignRight)
        lay.addWidget(lb_vinc, 3, 3)

        # # Phase Inc. Rate
        lb_pinc = SiriusLabel(self, self.prefix+chs_dict['28'][1]+'-RB',
            alignment=Qt.AlignCenter)
        lb_pinc.showUnits = True
        lay.addWidget(QLabel('28'), 4, 0)
        lay.addWidget(QLabel(chs_dict['28'][0]), 4, 1)
        lay.addWidget(SiriusEnumComboBox(
            self, self.prefix+chs_dict['28'][1]+'-SP'),
            4, 2, alignment=Qt.AlignRight)
        lay.addWidget(lb_pinc, 4, 3)

        # Look Reference
        pb_lookref = SiriusPushButton(
            self, self.prefix+chs_dict['106'][1])
        pb_lookref.setText('OFF')
        lay.addWidget(QLabel('106'), 5, 0)
        lay.addWidget(QLabel(chs_dict['106'][0]), 5, 1)
        lay.addWidget(pb_lookref, 5, 2, alignment=Qt.AlignRight)

        # # Rect/Polar Mode Select
        lay.addWidget(QLabel('114'), 6, 0)
        lay.addWidget(QLabel(chs_dict['114'][0]), 6, 1)
        lay.addWidget(SiriusEnumComboBox(
            self, self.prefix+chs_dict['114'][1]+'-Sel'),
            6, 2, alignment=Qt.AlignRight)
        lay.addWidget(SiriusLabel(self, self.prefix+chs_dict['114'][1]+'-Sts',
            alignment=Qt.AlignCenter), 6, 3)

        # Quadrant Selection
        lay.addWidget(QLabel('107'), 7, 0)
        lay.addWidget(QLabel(chs_dict['107'][0]), 7, 1)
        lay.addWidget(SiriusEnumComboBox(
            self, self.prefix+chs_dict['107'][1]+'-Sel'),
            7, 2, alignment=Qt.AlignRight)
        lay.addWidget(SiriusLabel(self, self.prefix+chs_dict['107'][1]+'-Sts',
            alignment=Qt.AlignCenter), 7, 3)

        # Equations
        pb_eq = QPushButton(
            qta.icon('fa5s.external-link-alt'), ' Equations', self)
        connect_window(
            pb_eq, EquationsDetails, parent=self,
            prefix=self.prefix, section=self.section, system=self.system)
        pb_eq.setStyleSheet('min-width:8em')
        lay.addWidget(pb_eq, 9, 1)

        # Limits
        pb_limit = QPushButton(
            qta.icon('fa5s.external-link-alt'), ' Limits', self)
        connect_window(
            pb_limit, LimitsDetails, parent=self, prefix=self.prefix,
            section=self.section, system=self.system, which='Loop')
        pb_limit.setStyleSheet('min-width:8em')
        lay.addWidget(pb_limit, 9, 2)

        lay.addItem(QSpacerItem(0, 9, QSzPlcy.Ignored, QSzPlcy.Fixed), 8, 0)
        lay.addItem(QSpacerItem(40, 0, QSzPlcy.Fixed, QSzPlcy.Ignored), 0, 4)

        # Amp Ref Min
        self._setupLabelEdit(lay, chs_dict, '26 mV', 0, 5)
        self._setupLabelEdit(lay, chs_dict, '26 VGap', 1, 5)

        # Phase Ref Min
        self._setupLabelEdit(lay, chs_dict, '27', 2, 5)

        # Open Loop Gain
        self._setupLabelEdit(lay, chs_dict, '30', 3, 5)

        # Phase Correction Control
        lay.addWidget(QLabel('31'), 4, 5)
        lay.addWidget(QLabel(chs_dict['31'][0]), 4, 6)
        lay.addWidget(PyDMStateButton(
            self, self.prefix+chs_dict['31'][1]+'-Sel'), 4, 7)
        lay.addWidget(SiriusLedState(
            self, self.prefix+chs_dict['31'][1]+'-Sts'),
            4, 8, alignment=Qt.AlignHCenter)

        # Phase Correct Error
        lb_80 = SiriusLabel(self, self.prefix+chs_dict['80'][1],
            alignment=Qt.AlignCenter)
        lb_80.showUnits = True
        lay.addWidget(QLabel('80'), 5, 5)
        lay.addWidget(QLabel(chs_dict['80'][0]), 5, 6)
        lay.addWidget(lb_80, 5, 8)

        # Phase Correct Control
        lb_81 = SiriusLabel(self, self.prefix+chs_dict['81'][1],
            alignment=Qt.AlignCenter)
        lb_81.showUnits = True
        lay.addWidget(QLabel('81'), 6, 5)
        lay.addWidget(QLabel(chs_dict['81'][0]), 6, 6)
        lay.addWidget(lb_81, 6, 8)

        # Fwd Min Amp & Phs
        self._setupLabelEdit(lay, chs_dict, '125', 7, 5)

        return lay

    def _setupLabelEdit(self, lay, chs_dict, key, row, column):
        label = SiriusLabel(self, self.prefix+chs_dict[key][1]+'-RB')
        label.showUnits = True

        lay.addWidget(QLabel(key.split()[0]), row, column)
        lay.addWidget(QLabel(chs_dict[key][0]), row, column+1)
        lay.addWidget(SiriusSpinbox(
            self, self.prefix+chs_dict[key][1]+'-SP'), row, column+2)
        lay.addWidget(label, row, column+3, alignment=Qt.AlignCenter)

    def _specificLoopsLayout(self, rect_or_polar):
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)
        chs_dict = self.syst_dict[rect_or_polar]

        if rect_or_polar == 'Rect':
            extra_addr = '30'
            grp_1 = 'Slow'
            grp_1_addrs = ['100', '110', '13', '1', '0']
            grp_2 = 'Fast'
            grp_2_addrs = ['115', '111', '124', '119', '118']
        else:
            extra_addr = '527'
            grp_1 = 'Amp'
            grp_1_addrs = ['116', '112', '121', '120']
            grp_2 = 'Phase'
            grp_2_addrs = ['117', '113', '123', '122']

        title_lay = QHBoxLayout()
        title_lay.addWidget(QLabel(
            f'<h3>{rect_or_polar} Loops</h3>', alignment=Qt.AlignCenter))
        title_lay.addWidget(SiriusLedState(
            self, self.prefix+self.syst_dict['Control']['Mode']))

        rect_lay = self._statisticsLayout(
            self.syst_dict, True, rect_or_polar, extra_addr)

        grp_1_lay = QVBoxLayout()
        grp_1_lay.setAlignment(Qt.AlignTop)
        grp_1_lay.addLayout(
            self._controlLayout(chs_dict[grp_1]['Control'], grp_1_addrs))
        grp_1_lay.addItem(QSpacerItem(0, 20, QSzPlcy.Ignored, QSzPlcy.Fixed))
        grp_1_lay.addLayout(self._statisticsLayout(chs_dict[grp_1], False))
        gbox_grp_1 = QGroupBox(f'{grp_1} Loop', self)
        gbox_grp_1.setLayout(grp_1_lay)

        grp_2_lay = QVBoxLayout()
        grp_2_lay.setAlignment(Qt.AlignTop)
        grp_2_lay.addLayout(
            self._controlLayout(chs_dict[grp_2]['Control'], grp_2_addrs))
        grp_2_lay.addItem(QSpacerItem(0, 20, QSzPlcy.Ignored, QSzPlcy.Fixed))
        grp_2_lay.addLayout(self._statisticsLayout(chs_dict[grp_2], False))
        gbox_grp_2 = QGroupBox(f'{grp_2} Loop', self)
        gbox_grp_2.setLayout(grp_2_lay)

        lay.addLayout(title_lay)
        lay.addItem(QSpacerItem(0, 20, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addLayout(rect_lay)
        lay.addWidget(gbox_grp_1)
        lay.addWidget(gbox_grp_2)

        return lay

    def _statisticsLayout(self, chs_dict, is_top_section, rect_or_polar='', extra_addr=''):
        lay = QGridLayout()
        lay.setHorizontalSpacing(18)

        lay.addWidget(QLabel(
            'In-Phase', alignment=Qt.AlignCenter), 0, 2)
        lay.addWidget(QLabel(
            'Quadrature', alignment=Qt.AlignCenter), 0, 3)
        if is_top_section:
            lay.addWidget(QLabel(
                'Amp', alignment=Qt.AlignCenter), 0, 4, 1, 4)
            lay.addWidget(QLabel(
                'Phase', alignment=Qt.AlignCenter), 0, 8)
        else:
            lay.addWidget(QLabel(
                'Amp', alignment=Qt.AlignCenter), 0, 4)
            lay.addWidget(QLabel(
                'Phase', alignment=Qt.AlignCenter), 0, 5)

        rows_dict = chs_dict
        if rect_or_polar != '' and extra_addr != '':
            rows_dict = chs_dict['General'].copy()
            rows_dict[extra_addr] = self.syst_dict[rect_or_polar][extra_addr]
        row = 1
        for key, dic in rows_dict.items():
            if key != 'Control':
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

    def _controlLayout(self, chs_dict, addrs):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)

        # Enable
        lay.addWidget(QLabel(addrs[0], alignment=Qt.AlignCenter), 1, 0)
        lay.addWidget(QLabel(chs_dict[addrs[0]][0]), 1, 1)
        lay.addWidget(PyDMStateButton(
            self, self.prefix+chs_dict[addrs[0]][1]+'-Sel'), 1, 2)
        lay.addWidget(SiriusLedState(
            self, self.prefix+chs_dict[addrs[0]][1]+'-Sts'),
            1, 3, alignment=Qt.AlignHCenter)

        # Input Selection
        if len(addrs) == 5:
            row = 2
            column = 0
        else:
            row = 1
            column = 4
        max_column = 7

        lb_inpsel = SiriusLabel(self, self.prefix+chs_dict[addrs[1]][1]+'-Sts')
        lb_inpsel.showUnits = True
        lay.addWidget(QLabel(addrs[1], alignment=Qt.AlignCenter), row, column)
        lay.addWidget(QLabel(chs_dict[addrs[1]][0]), row, column+1)
        lay.addWidget(SiriusEnumComboBox(
            self, self.prefix+chs_dict[addrs[1]][1]+'-Sel'),
            row, column+2, alignment=Qt.AlignRight)
        lay.addWidget(lb_inpsel, row, column+3)

        column += 4
        if column > max_column:
            row += 1
            column = 0

        # PI Limit (if exists), Ki and Kp
        keys = addrs[2:]
        for i in range(len(keys)):
            lb = SiriusLabel(self, self.prefix+chs_dict[keys[i]][1]+'-RB')
            lb.showUnits = True
            lay.addWidget(QLabel(
                keys[i], alignment=Qt.AlignCenter), row, column)
            lay.addWidget(QLabel(chs_dict[keys[i]][0]), row, column+1)
            lay.addWidget(SiriusSpinbox(
                self, self.prefix+chs_dict[keys[i]][1]+'-SP'), row, column+2)
            lay.addWidget(lb, row, column+3)
            column += 4
            if column > max_column:
                row += 1
                column = 0

        return lay


class RampsDetails(SiriusDialog):
    """Details about cavity ramps."""

    def __init__(self, parent=None, prefix='', section='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.system = system
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        title = 'Ramps Details'
        title += (f' - {self.system}' if self.section == 'SI' else '')
        self.setWindowTitle(title)
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
            '<h4>Advanced Cavity Ramps Details</h4>',
            alignment=Qt.AlignCenter))
        lay.addWidget(dtls)

    def _rampsControlLayout(self, chs_dict):
        lay = QGridLayout()
        lay.setSpacing(9)

        # General
        lay_gen = QGridLayout(self)
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
        lay_times = QGridLayout(self)
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
        lb_total = SiriusLabel(self)
        rule = ('[{"name": "TextRule", "property": "Text", ' +
                '"expression": "ch[0] + ch[1] + ch[2] + ch[4]", ' +
                '"channels": [')
        for i in range(len(addrs)):
            rule += ('{"channel": ' +
                self.prefix+chs_dict[addrs[i]][1]+'-RB"' +
                ', "trigger": true}')

        rule += ']}]'
        lb_total.rules = rule

        lay_times.addWidget(QLabel('Total'), len(addrs)+1, 1)
        lay_times.addWidget(lb_total, len(addrs)+1, 2)
        lay_times.addWidget(QLabel(
            '/410', alignment=Qt.AlignCenter), len(addrs)+1, 3)

        # Top
        lay_top = QGridLayout(self)
        lay_top.setAlignment(Qt.AlignTop)
        lay_top.setSpacing(9)
        gbox_top = QGroupBox('Top Ramp')
        gbox_top.setLayout(lay_top)

        self._setupLabelLine(lay_top, chs_dict, '164', 9)
        self._setupTextInputLine(lay_top, chs_dict, '362 mV', 10)
        self._setupTextInputLine(lay_top, chs_dict, '362 Vgap', 11)
        self._setupTextInputLine(lay_top, chs_dict, '364', 12)

        # Bot
        lay_bot = QGridLayout(self)
        lay_bot.setAlignment(Qt.AlignTop)
        lay_bot.setSpacing(9)
        gbox_bot = QGroupBox('Bottom Ramp')
        gbox_bot.setLayout(lay_bot)

        self._setupLabelLine(lay_bot, chs_dict, '184', 13)
        self._setupTextInputLine(lay_bot, chs_dict, '361 mV', 14)
        self._setupTextInputLine(lay_bot, chs_dict, '361 Vgap', 15)
        self._setupTextInputLine(lay_bot, chs_dict, '363', 16)

        # Slopes
        lay_slopes = QGridLayout(self)
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

        gbox_top = QGroupBox('Top Ramp', self)
        gbox_top.setLayout(self._topOrBotRampLayout(
            chs_dict['Top'], ['163', '162'], ['531']))
        gbox_bot = QGroupBox('Bottom Ramp', self)
        gbox_bot.setLayout(self._topOrBotRampLayout(
            chs_dict['Bot'], ['183'], ['531']))

        lay.addWidget(gbox_top)
        lay.addWidget(gbox_bot)

        return lay

    def _topOrBotRampLayout(self, chs_dict, lb_addrs, led_addrs):
        lay = QGridLayout(self)
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
        for addr in led_addrs:
            lay.addWidget(QLabel(addr, alignment=Qt.AlignCenter), alt_row, 4)
            lay.addWidget(QLabel(
                chs_dict[addr]['Label'],
                alignment=Qt.AlignLeft | Qt.AlignVCenter), alt_row, 5)
            lay.addWidget(SiriusLedState(
                self, self.prefix+chs_dict[addr]['PV']),
                alt_row, 6, alignment=Qt.AlignCenter)
            alt_row += 1

        lay.addItem(QSpacerItem(0, 15, QSzPlcy.Ignored, QSzPlcy.Fixed), row, 0)
        lay.addWidget(QLabel(
            'In-Phase', alignment=Qt.AlignCenter), row+1, 2)
        lay.addWidget(QLabel(
            'Quadrature', alignment=Qt.AlignCenter), row+1, 3)
        lay.addWidget(QLabel(
            'Amp', alignment=Qt.AlignCenter), row+1, 5)
        lay.addWidget(QLabel(
            'Phase', alignment=Qt.AlignCenter), row+1, 7)
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
                row += 1

        return lay


class EquationsDetails(SiriusDialog):
    """."""

    def __init__(self, parent=None, prefix='', section='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.system = system
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        title = 'Equations'
        title += (f' - {self.system}' if self.section == 'SI' else '')
        self.setWindowTitle(title)
        if self.section == 'SI':
            self.syst_dict = self.chs['Loops'][self.system]['Equations']
        else:
            self.syst_dict = self.chs['Loops']['Equations']
        self._setupUi()

    def _setupUi(self):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        lay.addWidget(QLabel(
            '<h4>Equations Details</h4>',
            alignment=Qt.AlignCenter), 0, 0, 1, 3)

        row = 1
        column = 0
        for key, dic in self.syst_dict.items():
            if key != 'VGap' and key != 'Rsh':
                gbox = QGroupBox(key)
                gbox.setLayout(self._genericStatisticsLayout(dic))

                lay.addWidget(gbox, row, column)

                column += 1
                if column == 3:
                    column = 0
                    row += 1
        
        gbox_vgap = QGroupBox('VGap')
        gbox_vgap.setLayout(self._vgapLayout(self.syst_dict['VGap']))
        lay.addWidget(gbox_vgap, row, column)
        column += 1
        if column == 3:
            column = 0
            row += 1

        # Rsh
        lay_extra = QGridLayout()
        lay_extra.setVerticalSpacing(12)

        lb_rsh = SiriusLabel(self, self.prefix+self.syst_dict['Rsh'])
        lb_rsh.showUnits = True

        lay_extra.addItem(
            QSpacerItem(0, 18, QSzPlcy.Ignored, QSzPlcy.Fixed), 0, 0)
        lay_extra.addWidget(QLabel(
            'C4*F^4 + C3*F^3 + C2*F^2 + C1*F + C0',
            alignment=Qt.AlignCenter), 1, 0, 1, 2)
        lay_extra.addWidget(QLabel(
            'Rsh (Ohm)', alignment=Qt.AlignRight | Qt.AlignVCenter),
            2, 0)
        lay_extra.addWidget(lb_rsh, 2, 1, alignment=Qt.AlignCenter)

        lay.addLayout(lay_extra, row, column, alignment=Qt.AlignHCenter)

    def _genericStatisticsLayout(self, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        # Header
        labels = ['C0', 'C1', 'C2', 'C3', 'C4', 'OFS']
        for i in range(len(labels)):
            lay.addWidget(QLabel(
                labels[i], alignment=Qt.AlignCenter), 0, i+1)

        # Body
        row = 1
        for key, val in chs_dict.items():
            if key != 'OFS':
                lay.addWidget(QLabel(key, alignment=Qt.AlignCenter), row, 0)
                lay.addWidget(SiriusLabel(
                    self, self.prefix+val+'-RB'), row, 1, 1, len(labels)-1)

                if key != 'OLG':
                    lay.addWidget(SiriusLabel(
                        self, self.prefix+chs_dict['OFS']+'-RB'),
                        row, len(labels), alignment=Qt.AlignCenter)
                else:
                    lay.addWidget(QLabel(
                        '-', alignment=Qt.AlignCenter), row, len(labels))

                row += 1

        return lay

    def _vgapLayout(self, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        # Headers
        labels = ['C0', 'C1', 'C2', 'C3', 'C4']
        for i in range(len(labels)):
            lay.addWidget(QLabel(labels[i], alignment=Qt.AlignCenter), 0, i)
            lay.addWidget(QLabel(labels[i], alignment=Qt.AlignCenter), 2, i)

        # Bodies
        for i in range(len(labels)):
            lay.addWidget(SiriusLabel(
                self, self.prefix+chs_dict['Hw to Amp']+f'{i}-RB'), 1, i)
            lay.addWidget(SiriusLabel(
                self, self.prefix+chs_dict['Hw to Amp']+f'{i}-RB'), 3, i)

        return lay


class AutoStartDetails(SiriusDialog):
    """."""

    def __init__(self, parent=None, prefix='', section='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.system = system
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        title = 'Auto Start Details'
        title += (f' - {self.system}' if self.section == 'SI' else '')
        self.setWindowTitle(title)
        if self.section == 'SI':
            self.syst_dict = self.chs['AutoStart'][self.system]
        else:
            self.syst_dict = self.chs['AutoStart']
        self._setupUi()

    def _setupUi(self):
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        # General
        gbox_gen = QGroupBox('General')
        gen_lay = QGridLayout()
        gbox_gen.setLayout(gen_lay)

        # # Enable
        self._setupButtonLed(gen_lay, '22', 0)

        # # Start
        gen_lay.addWidget(QLabel('23'), 1, 0)
        gen_lay.addWidget(QLabel(self.syst_dict['23'][0]), 1, 1)
        gen_lay.addWidget(SiriusEnumComboBox(
            self, self.prefix+self.syst_dict['23'][1]+'-Sel'),
            1, 2, alignment=Qt.AlignRight)
        gen_lay.addWidget(SiriusLabel(
            self, self.prefix+self.syst_dict['23'][1]+'-Sts',
            alignment=Qt.AlignCenter), 1, 3)

        # # EPS
        self._setupButtonLed(gen_lay, '400', 2)

        # # Bypass
        self._setupButtonLed(gen_lay, '401', 3)

        # Diagnostics
        gbox_diag = QGroupBox('Diagnostics')
        diag_lay = QGridLayout()
        gbox_diag.setLayout(diag_lay)

        # # State Start
        lb_state = SiriusLabel(self, self.syst_dict['Diag']['500'][1])
        lb_state.showUnits = True
        diag_lay.addWidget(QLabel('500'), 0, 0)
        diag_lay.addWidget(QLabel(self.syst_dict['Diag']['500'][0]), 0, 1)
        diag_lay.addWidget(lb_state, 0, 2)

        # # LEDs
        row = 1
        for key in self.syst_dict['Diag'].keys():
            if key != '500':
                self._setupLabelLed(
                    diag_lay, key, self.syst_dict['Diag'], row, key == '401')
                row += 1

        lay.addWidget(QLabel(
            '<h4>Advanced Auto Start Details</h4>', alignment=Qt.AlignCenter))
        lay.addWidget(gbox_gen)
        lay.addWidget(gbox_diag)

    def _setupButtonLed(self, lay, key, row):
        lay.addWidget(QLabel(key), row, 0)
        lay.addWidget(QLabel(self.syst_dict[key][0]), row, 1)
        lay.addWidget(PyDMStateButton(
            self, self.prefix+self.syst_dict[key][1]+'-Sel'),
            row, 2, alignment=Qt.AlignCenter)
        lay.addWidget(SiriusLedState(
            self, self.prefix+self.syst_dict[key][1]+'-Sts'),
            row, 3, alignment=Qt.AlignCenter)

    def _setupLabelLed(self, lay, key, chs_dict, row, is_alert):
        if is_alert:
            led = SiriusLedAlert(self, self.prefix+chs_dict[key][1])
        else:
            led = SiriusLedState(self, self.prefix+chs_dict[key][1])

        lay.addWidget(QLabel(key), row, 0)
        lay.addWidget(QLabel(chs_dict[key][0]), row, 1)
        lay.addWidget(led, row, 2, alignment=Qt.AlignCenter)


class ConditioningDetails(SiriusDialog):
    """."""

    def __init__(self, parent=None, prefix='', section='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.system = system
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        title = 'Conditioning Details'
        title += (f' - {self.system}' if self.section == 'SI' else '')
        self.setWindowTitle(title)
        if self.section == 'SI':
            self.syst_dict = self.chs['Conditioning'][self.system]
        else:
            self.syst_dict = self.chs['Conditioning']
        self._setupUi()

    def _setupUi(self):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)
        lay.addWidget(QLabel(
            '<h4>Advanced Conditioning Details</h4>',
            alignment=Qt.AlignCenter), 0, 0, 1, 4)

        # Pulse Enable
        self._setupLedState(lay, '200', 1, True)

        # Auto Cond Enable
        self._setupLedState(lay, '201', 2, True)

        # Cond Freq
        self._setupLabelEdit(lay, '204', 3)

        # Cond Freq Diag
        lb_condfreq = SiriusLabel(self, self.prefix+self.syst_dict['540'][1])
        lb_condfreq.showUnits = True
        lay.addWidget(QLabel('540'), 4, 0)
        lay.addWidget(QLabel(self.syst_dict['540'][0]), 4, 1)
        lay.addWidget(lb_condfreq, 4, 3, alignment=Qt.AlignCenter)

        # Duty Cycle
        self._setupLabelEdit(lay, '205', 5)

        # Duty Cycle RB
        lb_condfreq = SiriusLabel(self, self.prefix+self.syst_dict['530'][1])
        lb_condfreq.showUnits = True
        lay.addWidget(QLabel('530'), 6, 0)
        lay.addWidget(QLabel(self.syst_dict['530'][0]), 6, 1)
        lay.addWidget(lb_condfreq, 6, 3, alignment=Qt.AlignCenter)

        relay_keys = [
            'CGC Fast Relay', 'Relay Setpoint RB', 'Relay Hysteria RB']
        row = 7
        for key in relay_keys:
            lb_relay = SiriusLabel(
                self, self.prefix+self.syst_dict['Relay'][key]+'-RB')
            lb_relay.showUnits = True

            lay.addWidget(QLabel(key), row, 1)
            if key.split()[-1] != 'RB':
                lay.addWidget(SiriusSpinbox(
                    self, self.prefix+self.syst_dict['Relay'][key]+'-SP'),
                    row, 2)
            lay.addWidget(lb_relay, row, 3)
            row += 1

        # Vacuum
        self._setupLedState(lay, '79', row, False)

    def _setupLedState(self, lay, key, row, has_button):
        lay.addWidget(QLabel(key), row, 0)
        lay.addWidget(QLabel(self.syst_dict[key][0]), row, 1)

        ending = ''
        if has_button:
            lay.addWidget(PyDMStateButton(
                self, self.prefix+self.syst_dict[key][1]+'-Sel'),
                row, 2, alignment=Qt.AlignCenter)
            ending = '-Sts'

        lay.addWidget(SiriusLedState(
            self, self.prefix+self.syst_dict[key][1]+ending),
            row, 3, alignment=Qt.AlignCenter)

    def _setupLabelEdit(self, lay, key, row):
        label = SiriusLabel(self, self.prefix+self.syst_dict[key][1]+'-RB')
        label.showUnits = True

        lay.addWidget(QLabel(key), row, 0)
        lay.addWidget(QLabel(self.syst_dict[key][0]), row, 1)
        lay.addWidget(SiriusSpinbox(
            self, self.prefix+self.syst_dict[key][1]+'-SP'), row, 2)
        lay.addWidget(label, row, 3, alignment=Qt.AlignCenter)


class TuningDetails(SiriusDialog):
    """Advanced details related to tuning and plungers."""

    def __init__(self, parent=None, prefix='', section='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.system = system
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        title = 'Tuning Details'
        title += (f' - {self.system}' if self.section == 'SI' else '')
        self.setWindowTitle(title)
        if self.section == 'SI':
            self.syst_dict = self.chs['TunDtls'][self.system]
        else:
            self.syst_dict = self.chs['TunDtls']
        self._setupUi()

    def _setupUi(self):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)
        lay.addWidget(QLabel(
            '<h4>Advanced Tuning Details</h4>',
            alignment=Qt.AlignCenter), 0, 0, 1, 3)

        gbox_gen = QGroupBox('General')
        gbox_gen.setLayout(self._generalLayout(self.syst_dict['General']))
        lay.addWidget(gbox_gen, 1, 0)

        gbox_drv = QGroupBox('Drivers')
        gbox_drv.setLayout(self._driversLayout(self.syst_dict['Drivers']))
        lay.addWidget(gbox_drv, 1, 1)

        auto_man = QTabWidget(self)
        auto_man.setObjectName(self.section+'Tab')
        auto_man.setStyleSheet(
            "#"+self.section+'Tab'+"::pane {"
            "    border-left: 2px solid gray;"
            "    border-bottom: 2px solid gray;"
            "    border-right: 2px solid gray;}")

        wid_man = QWidget(self)
        wid_man.setLayout(self._manualLayout(self.syst_dict['Manual']))
        auto_man.addTab(wid_man, 'Manual')

        wid_auto = QWidget(self)
        wid_auto.setLayout(self._autoLayout(self.syst_dict['Auto']))
        auto_man.addTab(wid_auto, 'Auto')

        lay.addWidget(auto_man, 1, 2)

    def _generalLayout(self, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        # Amplitudes and Phase Angles
        row = 0
        keys = ['34', '19', '33', '18']
        for key in keys:
            lb = SiriusLabel(self, self.prefix+chs_dict[key][1])
            self._setupAddrLabel(lay, chs_dict, key, row)
            lay.addWidget(lb, row, 3)
            row += 1

        # Tuning Fwd Min
        self._setupAddrLabel(lay, chs_dict, '307', row)
        lay.addWidget(SiriusLedState(
            self, self.prefix+chs_dict['307'][1]),
            row, 3, alignment=Qt.AlignCenter)
        row += 1

        # Pulses Freq
        lb_freq = SiriusLabel(self, self.prefix+chs_dict['303'][1]+'-RB')
        lb_freq.showUnits = True
        self._setupAddrLabel(lay, chs_dict, '303', row)
        lay.addWidget(SiriusEnumComboBox(
            self, self.prefix+chs_dict['303'][1]+'-SP'),
            row, 2, alignment=Qt.AlignCenter)
        lay.addWidget(lb_freq, row, 3, alignment=Qt.AlignCenter)

        return lay

    def _driversLayout(self, chs_dict):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        if self.section == 'SI':
            supplies = ['5V', '24V']
        else:
            supplies = ['5V', '48V']
        row = 0
        for sup in supplies:
            lb_volt = SiriusLabel(self, self.prefix+chs_dict[sup][0])
            lb_volt.showUnit = True
            lb_curr = SiriusLabel(self, self.prefix+chs_dict[sup][1])
            lb_curr.showUnit = True
            lay.addWidget(QLabel(f'{sup} Supply'), row, 0)
            lay.addWidget(lb_volt, row, 1)
            lay.addWidget(lb_curr, row, 2)
            row += 1

        lay.addWidget(QLabel('Drivers'), row, 0)
        lay.addWidget(PyDMStateButton(
            self, self.prefix+chs_dict['Enable']+'-Sel'),
            row, 1, alignment=Qt.AlignCenter)
        lay.addWidget(SiriusLedState(
            self, self.prefix+chs_dict['Enable']+'-Sts'),
            row, 2, alignment=Qt.AlignCenter)
        row += 1

        drivers = ['1', '2']
        for d in drivers:
            gbox = QGroupBox(f'Driver {d}')
            gbox_lay = QGridLayout()
            gbox.setLayout(gbox_lay)

            lb_status = SiriusLabel(self, self.prefix+chs_dict[d][0])
            lb_status.showUnits = True

            gbox_lay.addWidget(QLabel('Status'), 0, 0)
            gbox_lay.addWidget(lb_status, 0, 1)
            gbox_lay.addWidget(QLabel('Fault'), 1, 0)
            gbox_lay.addWidget(SiriusLedAlert(
                self, self.prefix+chs_dict[d][1]),
                1, 1, alignment=Qt.AlignCenter)

            lay.addWidget(gbox, row, 0, 1, 3)
            row += 1

        return lay

    def _manualLayout(self, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        # Number of Pulses
        lb_num = SiriusLabel(self, self.prefix+chs_dict['302'][1]+'-RB')
        lb_num.showUnits = True
        self._setupAddrLabel(lay, chs_dict, '302', 0)
        lay.addWidget(SiriusSpinbox(
            self, self.prefix+chs_dict['302'][1]+'-SP'), 0, 2)
        lay.addWidget(lb_num, 0, 3, alignment=Qt.AlignCenter)

        # Move and Move Dir
        keys = ['306', '305']
        if self.section == 'BO':
            keys.extend(['315', '314'])

        row = 1
        for key in keys:
            self._setupAddrLabel(lay, chs_dict, key, row)
            self._setupButtonLed(lay, chs_dict, key, row)
            row += 1

        # Tuning Reset
        self._setupAddrLabel(lay, chs_dict, '307', row)
        pb_reset = SiriusPushButton(
            label='', icon=qta.icon('fa5s.sync'), releaseValue=0,
            parent=self, init_channel=self.prefix+chs_dict['307'][1])
        pb_reset.setStyleSheet(
            'min-width:25px; max-width:25px; icon-size:20px;')
        lay.addWidget(pb_reset, row, 2, alignment=Qt.AlignCenter)
        row += 1

        # Manual Up/Down
        keys = ['302 Man', '303 Man']
        if self.section == 'BO':
            keys.extend(['315 Man', '316 Man'])

        for key in keys:
            self._setupAddrLabel(lay, chs_dict, key, row)
            lay.addWidget(SiriusLedState(
                self, self.prefix+chs_dict[key][1]),
                row, 3, alignment=Qt.AlignCenter)
            row += 1

        return lay

    def _autoLayout(self, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        # Pos Enable
        self._setupAddrLabel(lay, chs_dict, '301', 0)
        self._setupButtonLed(lay, chs_dict, '301', 0)

        # Tuning Margins, Forward Min and Delay
        keys = ['309', '310', '308', '311']
        row = 1
        for key in keys:
            label = SiriusLabel(self, self.prefix+chs_dict[key][1]+'-RB')
            label.showUnits = True
            self._setupAddrLabel(lay, chs_dict, key, row)
            lay.addWidget(SiriusSpinbox(
                self, self.prefix+chs_dict[key][1]+'-SP'), row, 2)
            lay.addWidget(label, row, 3)
            row += 1

        # Trigger Enable
        lb_trig = SiriusLabel(self, self.prefix+chs_dict['313'][1]+'-Sts')
        lb_trig.showUnits = True
        self._setupAddrLabel(lay, chs_dict, '313', row)
        lay.addWidget(SiriusEnumComboBox(
            self, self.prefix+chs_dict['313'][1]+'-Sel'),
            row, 2, alignment=Qt.AlignCenter)
        lay.addWidget(lb_trig, row, 3, alignment=Qt.AlignCenter)
        row += 1

        # Filter Enable
        self._setupAddrLabel(lay, chs_dict, '312', row)
        self._setupButtonLed(lay, chs_dict, '312', row)
        row += 1

        # On Top Ramp
        self._setupAddrLabel(lay, chs_dict, '316', row)
        self._setupButtonLed(lay, chs_dict, '316', row)

        return lay

    def _setupAddrLabel(self, lay, chs_dict, addr, row):
        lay.addWidget(QLabel(addr.split()[0]), row, 0)
        lay.addWidget(QLabel(chs_dict[addr][0]), row, 1)

    def _setupButtonLed(self, lay, chs_dict, addr, row):
        lay.addWidget(PyDMStateButton(
            self, self.prefix+chs_dict[addr][1]+'-Sel'), row, 2)
        lay.addWidget(SiriusLedState(
            self, self.prefix+chs_dict[addr][1]+'-Sts'),
            row, 3, alignment=Qt.AlignCenter)


class AdvancedInterlockDetails(SiriusDialog):
    """Advanced details related to interlocks."""

    def __init__(self, parent=None, prefix='', section='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.system = system
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        title = 'Advanced Interlock Details'
        title += (f' - {self.system}' if self.section == 'SI' else '')
        self.setWindowTitle(title)
        if self.section == 'SI':
            self.syst_dict = self.chs['AdvIntlk'][self.system]
        else:
            self.syst_dict = self.chs['AdvIntlk']
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
        wid_diag.setLayout(
            self._diagnosticsLayout(self.syst_dict['Diagnostics']))
        dtls.addTab(wid_diag, 'Diagnostics')

        wid_bypass = QWidget(self)
        wid_bypass.setLayout(self._bypassLayout(self.syst_dict['Bypass']))
        dtls.addTab(wid_bypass, 'Interlock Bypass')

        lay.addWidget(QLabel(
            '<h4>Advanced Interlock Details</h4>', alignment=Qt.AlignCenter))
        lay.addWidget(dtls)

    def _diagnosticsLayout(self, chs_dict):
        lay = QHBoxLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        # General
        gbox_gen = QGroupBox()
        gbox_gen.setLayout(self._genDiagLayout(chs_dict['General']))

        # Levels
        gbox_lvls = QGroupBox('Levels')
        lay_lvls = QGridLayout()
        lay_lvls.setAlignment(Qt.AlignTop)
        lay_lvls.setSpacing(9)
        gbox_lvls.setLayout(lay_lvls)

        row = 0
        for key, val in chs_dict['Levels'].items():
            lb = SiriusLabel(self, self.prefix+val+'-RB')
            lb.showUnits = True
            lay_lvls.addWidget(QLabel(f'Limit {key}'), row, 0)
            lay_lvls.addItem(QSpacerItem(
                9, 0, QSzPlcy.Fixed, QSzPlcy.Ignored), row, 1)
            lay_lvls.addWidget(SiriusSpinbox(
                self, self.prefix+val+'-SP'), row, 2)
            lay_lvls.addWidget(lb, row, 3)
            row += 1

        # GPIO Inputs
        gbox_inp = QGroupBox('GPIO Inputs')
        lay_inp = QGridLayout()
        lay_inp.setAlignment(Qt.AlignTop)
        lay_inp.setSpacing(9)
        gbox_inp.setLayout(lay_inp)

        labels = ['LLRF1', 'LLRF2', 'PLC', 'RF On State', 'Vacuum In',
            'End Sw Up 1', 'End Sw Dw 1', 'VCXO Power', 'VCXO Ref',
            'VCXO Locked', 'Spare', 'End Sw Up 2', 'End Sw Dw 2']
        self._setupByteMonitor(lay_inp, labels, chs_dict['GPIO']['Inp'])
        lay_inp.addWidget(SiriusLabel(
            self, self.prefix+chs_dict['GPIO']['Inp']),
            0, 0, 1, 2, alignment=Qt.AlignCenter)

        # GPIO Interlock
        gbox_intlk = QGroupBox('GPIO Interlock')
        lay_intlk = QGridLayout()
        lay_intlk.setAlignment(Qt.AlignTop)
        lay_intlk.setSpacing(9)
        gbox_intlk.setLayout(lay_intlk)

        labels = ['LLRF 2 Standby', 'Pin Diode', 'FDL Trigger', 'PLC',
            'Ext LLRF']
        self._setupByteMonitor(
            lay_intlk, labels, self.prefix+chs_dict['GPIO']['Intlk'])
        lay_intlk.addWidget(SiriusLabel(
            self, self.prefix+chs_dict['GPIO']['Intlk']),
            0, 0, 1, 2, alignment=Qt.AlignCenter)

        # GPIO Outputs
        gbox_out = QGroupBox('GPIO Outputs')
        lay_out = QGridLayout()
        lay_out.setAlignment(Qt.AlignTop)
        lay_out.setSpacing(9)
        gbox_out.setLayout(lay_out)

        labels = ['Pulse', 'TTL1 Dir PLA', 'TTL2 Pulse PLA', 'TTL3 Dir PLB',
            'TTL4 Pulse PLB', 'Ilk PLC', 'Ilk PinSw', 'VCXO En', 'VCXO Clk',
            'VCXO Data', 'Ilk LLRF']
        self._setupByteMonitor(
            lay_out, labels, self.prefix+chs_dict['GPIO']['Out'])
        lay_out.addWidget(SiriusLabel(
            self, self.prefix+chs_dict['GPIO']['Out']),
            0, 0, 1, 2, alignment=Qt.AlignCenter)

        lay.addWidget(gbox_gen)
        lay.addWidget(gbox_lvls)
        lay.addWidget(gbox_inp)
        lay.addWidget(gbox_intlk)
        lay.addWidget(gbox_out)

        return lay

    def _genDiagLayout(self, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        # Interlocks Delay
        lb_dly = SiriusLabel(self, self.prefix+chs_dict['Delay']+'-RB')
        lb_dly.showUnits = True

        lay.addWidget(QLabel('Interlocks Delay'), 0, 0)
        lay.addWidget(SiriusSpinbox(
            self, self.prefix+chs_dict['Delay']+'-SP'), 0, 1)
        lay.addWidget(lb_dly, 0, 2)

        # HW Interlock
        lay.addWidget(QLabel('HW Interlock'), 1, 0)
        lay.addWidget(SiriusLedAlert(
            self, self.prefix+chs_dict['HW']), 1, 2, alignment=Qt.AlignCenter)

        # Manual Interlock, End Switches and Logic Inversions
        keys = ['Manual', 'EndSw', 'Beam Inv', 'Vacuum Inv']
        row = 3
        for key in keys:
            lay.addWidget(QLabel(chs_dict[key][0]), row, 0)
            lay.addWidget(PyDMStateButton(
                self, self.prefix+chs_dict[key][1]+'-Sel'), row, 1)
            lay.addWidget(SiriusLedState(
                self, self.prefix+chs_dict[key][1]+'-Sts'),
                row, 2, alignment=Qt.AlignCenter)
            row += 1

        return lay

    def _setupByteMonitor(self, lay, labels, channel):
        for bit in range(len(labels)):
            lay.addWidget(QLabel(labels[bit]), bit+1, 0)
            lay.addWidget(SiriusLedState(
                self, channel, bit), bit+1, 1, alignment=Qt.AlignCenter)

    def _bypassLayout(self, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        labels = ['Diagnostics', 'Ext LLRF', 'Tx PLC', 'FDL Trigger',
            'Pin Diode', 'Loops Standby']

        column = 2
        for lb in labels:
            lay.addWidget(QLabel(
                lb, alignment=Qt.AlignCenter), 0, column)
            column += 2

        for i in range(1, column):
            if i % 2 == 0 or i == 1:
                lay.setColumnStretch(i, 1)
        lay.setColumnMinimumWidth(1, 120)

        row = 1
        for key, val in chs_dict.items():
            lay.addWidget(QLabel(key.split()[0]), row, 0)
            lay.addWidget(QLabel(val[0]), row, 1)
            column = 2
            for bit in range(len(labels)):
                lay_state = QHBoxLayout()
                pb = PyDMStateButton(self, self.prefix+val[1]+'-Sel', bit=bit)
                lay_state.addWidget(pb, alignment=Qt.AlignRight)
                lay_state.addWidget(SiriusLedState(
                    self, self.prefix+val[1]+'-Sts', bit),
                    alignment=Qt.AlignLeft)
                lay.addLayout(lay_state, row, column)
                lay.addItem(QSpacerItem(
                    9, 0, QSzPlcy.Ignored, QSzPlcy.Fixed), row, column+1)
                column += 2
            lay.addWidget(SiriusPushButton(
                self, self.prefix+val[1]+'-Sel', 'All Zero', releaseValue=0),
                row, column)
            lay.addWidget(SiriusPushButton(
                self, self.prefix+val[1]+'-Sel', 'All One', releaseValue=63),
                row, column+1)
            row += 1

        return lay


class LimitsDetails(SiriusDialog):
    """Loop and Ramp Limits details."""

    def __init__(self, parent=None, prefix='', section='', system='', which=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.system = system
        self.which = which
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        title = f'{self.which} Limits Details'
        title += (f' - {self.system}' if self.section == 'SI' else '')
        self.setWindowTitle(title)
        if self.which == 'Loop':
            key = 'Loops'
        else:
            key = 'RampDtls'
        if self.section == 'SI':
            self.syst_dict = self.chs[key][self.system]['Control']['Limits']
        else:
            self.syst_dict = self.chs[key]['Control']['Limits']
        self._setupUi()

    def _setupUi(self):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)
        lay.addWidget(QLabel(
            f'<h4>{self.which} Limits Details</h4>', alignment=Qt.AlignCenter),
            0, 0, 1, 4)

        row = 1
        for key, val in self.syst_dict.items():
            lb_val = SiriusLabel(self, self.prefix+val[1]+'-RB')
            lb_val.showUnits = True

            lay.addWidget(QLabel(key), row, 0)
            lay.addWidget(QLabel(val[0]), row, 1, alignment=Qt.AlignCenter)
            lay.addWidget(SiriusSpinbox(
                self, self.prefix+val[1]+'-SP'), row, 2)
            lay.addWidget(lb_val, row, 3)

            self._setupMaxMinEdit(lay, val[1], row+1, True)
            self._setupMaxMinEdit(lay, val[1], row+2, False)

            row += 3

    def _setupMaxMinEdit(self, lay, pv, row, is_max):
        if is_max:
            label = 'MAX'
            ending = '-SP.DRVH'
        else:
            label = 'MIN'
            ending = '-SP.DRVL'

        lb = SiriusLabel(self, self.prefix+pv+ending)
        lb.showUnits = True

        lay.addWidget(QLabel(label, alignment=Qt.AlignCenter), row, 1)
        lay.addWidget(SiriusLineEdit(self, self.prefix+pv+ending), row, 2)
        lay.addWidget(lb, row, 3)
