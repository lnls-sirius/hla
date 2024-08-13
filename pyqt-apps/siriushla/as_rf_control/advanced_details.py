"""Advanced detail windows."""

from epics import PV
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QGroupBox, QHBoxLayout, QLabel, \
    QSizePolicy as QSzPlcy, QSpacerItem, QTabWidget, QVBoxLayout, \
    QWidget, QFrame

from ..widgets import PyDMStateButton, SiriusDialog, SiriusLabel, \
    SiriusLedAlert, SiriusLedState, SiriusLineEdit, SiriusScaleIndicator, \
    SiriusEnumComboBox, SiriusPushButton

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
                lay.addWidget(
                    SiriusLineEdit(self, self.prefix+val[1]+'-SP'), row, 2)
                lay.addWidget(lb_value, row, 3)
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
        wid_controls.setLayout(
            self._loopsControlLayout(self.syst_dict['Control']))
        dtls.addTab(wid_controls, 'Loops Control')

        wid_iq = QWidget(self)
        wid_iq.setLayout(self._specificLoopsLayout('Rect'))
        dtls.addTab(wid_iq, 'IQ Loops')

        wid_polar = QWidget(self)
        wid_polar.setLayout(self._specificLoopsLayout('Polar'))
        dtls.addTab(wid_polar, 'Polar Loops')

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
            self, self.prefix+chs_dict['114'][1]+'-Sel'),
            5, 2, alignment=Qt.AlignRight)
        lay.addWidget(SiriusLabel(self, self.prefix+chs_dict['114'][1]+'-Sts',
            alignment=Qt.AlignRight), 5, 3)

        # Quadrant Selection
        lay.addWidget(QLabel('107'), 6, 0)
        lay.addWidget(QLabel(chs_dict['107'][0]), 6, 1)
        lay.addWidget(SiriusEnumComboBox(
            self, self.prefix+chs_dict['107'][1]+'-Sel'),
            6, 2, alignment=Qt.AlignRight)
        lay.addWidget(SiriusLabel(self, self.prefix+chs_dict['107'][1]+'-Sts',
            alignment=Qt.AlignRight), 6, 3)

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
            lay.addWidget(SiriusLineEdit(
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
            self.syst_dict = self.chs['Ramps'][self.system]
        else:
            self.syst_dict = self.chs['Ramps']
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
        wid_controls.setLayout(
            self._rampsControlLayout(self.syst_dict['Controls']))
        dtls.addTab(wid_controls, 'Ramps Control')

        wid_top = QWidget(self)
        wid_top.setLayout(
            self._diagnosticsRampLayout(self.syst_dict['Diagnostics']))
        dtls.addTab(wid_top, 'Ramp Diagnostics')

        lay.addWidget(dtls, 1, 0)

    def _rampsControlLayout(self, chs_dict):
        lay = QHBoxLayout()
        lay.setSpacing(9)

        lay_cntrls = QGridLayout(self)
        lay_cntrls.setAlignment(Qt.AlignTop)
        lay_cntrls.setSpacing(9)

        # Ramp Enable
        lay_cntrls.addWidget(QLabel('Ramp Enable'), 0, 1)
        lay_cntrls.addWidget(PyDMStateButton(
            self, self.prefix+chs_dict['Ramp Enable']+'-Sel'), 0, 2)
        lay_cntrls.addWidget(SiriusLedState(
            self, self.prefix+chs_dict['Ramp Enable']+'-Sts'),
            0, 3, alignment=Qt.AlignHCenter)

        # Ramp Down Disable
        lay_cntrls.addWidget(QLabel('Ramp Down Disable'), 1, 1)
        lay_cntrls.addWidget(PyDMStateButton(
            self, self.prefix+chs_dict['Ramp Down Disable']+'-Sel'), 1, 2)
        lay_cntrls.addWidget(SiriusLedState(
            self, self.prefix+chs_dict['Ramp Down Disable']+'-Sts'),
            1, 3, alignment=Qt.AlignHCenter)

        # T1 to T4
        addrs = ['356', '357', '358', '359']
        self.pvs = []
        for i in range(len(addrs)):
            self._setupTextInputLine(lay_cntrls, chs_dict, addrs[i], i+2)

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

        lay_cntrls.addWidget(QLabel('Total'), 6, 1)
        lay_cntrls.addWidget(lb_total, 6, 2)
        lay_cntrls.addWidget(QLabel('/410', alignment=Qt.AlignCenter), 6, 3)

        # Ramp Increase Rate
        self._setupTextInputLine(lay_cntrls, chs_dict, '360', 7)

        # Top
        self._setupCentralLabelLine(lay_cntrls, chs_dict, '164', 8)
        self._setupTextInputLine(lay_cntrls, chs_dict, '362 mV', 9)
        self._setupTextInputLine(lay_cntrls, chs_dict, '362 Vgap', 10)
        self._setupTextInputLine(lay_cntrls, chs_dict, '364', 11)

        # Bot
        self._setupCentralLabelLine(lay_cntrls, chs_dict, '184', 12)
        self._setupTextInputLine(lay_cntrls, chs_dict, '361 mV', 13)
        self._setupTextInputLine(lay_cntrls, chs_dict, '361 Vgap', 14)
        self._setupTextInputLine(lay_cntrls, chs_dict, '363', 15)

        # Ramp Top and Ready
        self._setupCentralLabelLine(lay_cntrls, chs_dict, '536', 16)
        lay_cntrls.addWidget(QLabel('533'), 17, 0)
        lay_cntrls.addWidget(QLabel(chs_dict['533'][0]), 17, 1)
        lay_cntrls.addWidget(SiriusLedState(
            self, self.prefix+chs_dict['533'][1]),
            17, 2, 17, 3, alignment=Qt.AlignTop | Qt.AlignHCenter)

        # Slopes
        self._setupTextInputLine(lay_cntrls, chs_dict, '365', 18)
        self._setupTextInputLine(lay_cntrls, chs_dict, '366', 19)
        self._setupTextInputLine(lay_cntrls, chs_dict, '367', 20)
        self._setupTextInputLine(lay_cntrls, chs_dict, '368', 21)

        lay.addLayout(lay_cntrls)

        return lay

    def _setupTextInputLine(self, lay, chs_dict, key, row):
        label = SiriusLabel(self, self.prefix+chs_dict[key][1]+'-RB')
        label.showUnits = True

        lay.addWidget(QLabel(key.split()[0]), row, 0)
        lay.addWidget(QLabel(chs_dict[key][0]), row, 1)
        lay.addWidget(SiriusLineEdit(
            self, self.prefix+chs_dict[key][1]+'-SP'), row, 2)
        lay.addWidget(label, row, 3, alignment=Qt.AlignRight)

    def _setupCentralLabelLine(self, lay, chs_dict, key, row):
        label = SiriusLabel(self, self.prefix+chs_dict[key][1])
        label.showUnits = True

        lay.addWidget(QLabel(key), row, 0)
        lay.addWidget(QLabel(chs_dict[key][0]), row, 1)
        lay.addWidget(label, row, 2, row, 3,
            alignment=Qt.AlignTop | Qt.AlignHCenter)

    def _diagnosticsRampLayout(self, chs_dict):
        lay = QVBoxLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(20)

        gbox_top = QGroupBox('Top Ramp', self)
        gbox_top.setLayout(self._topOrBotRampLayout(
            chs_dict['Top'], ['162', '163'], ['531']))
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
                    chs_dict[addr]['Label'], alignment=Qt.AlignLeft), row, 1)
                lay.addWidget(lb, row, 2)
                row += 1

        for addr in led_addrs:
            lay.addWidget(QLabel(addr, alignment=Qt.AlignCenter), row, 0)
            lay.addWidget(QLabel(
                chs_dict[addr]['Label'], alignment=Qt.AlignLeft), row, 1)
            lay.addWidget(SiriusLedState(
                self, self.prefix+chs_dict[addr]['PV']),
                row, 2, alignment=Qt.AlignCenter)
            row += 1

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
