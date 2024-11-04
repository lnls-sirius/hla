"""Advanced details related to interlocks."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QGroupBox, QHBoxLayout, QLabel, \
    QScrollArea, QSizePolicy as QSzPlcy, QSpacerItem, QTabWidget, \
    QVBoxLayout, QWidget

from ...widgets import PyDMStateButton, SiriusDialog, SiriusLabel, \
    SiriusLedAlert, SiriusLedState, SiriusLineEdit, SiriusPushButton, \
    SiriusSpinbox
from ..util import DEFAULT_STYLESHEET, SEC_2_CHANNELS


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
        self.title = 'Advanced Interlock Details'
        self.title += (f' - {self.system}' if self.section == 'SI' else '')
        self.setWindowTitle(self.title)
        if self.section == 'SI':
            self.syst_dict = self.chs['AdvIntlk'][self.system]
        else:
            self.syst_dict = self.chs['AdvIntlk']
        self._setupUi()

    def _setupUi(self):
        self.setStyleSheet(DEFAULT_STYLESHEET)
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

        wid_dyn = QWidget(self)
        wid_dyn.setLayout(
            self._dynamicInterlockLayout(self.syst_dict['Dynamic']))
        dtls.addTab(wid_dyn, 'Dynamic Interlock')

        wid_bypass = QWidget(self)
        wid_bypass.setLayout(self._bypassLayout(self.syst_dict['Bypass']))
        dtls.addTab(wid_bypass, 'Interlock Bypass')

        lay.addWidget(QLabel(
            f'<h4>{self.title}</h4>', alignment=Qt.AlignCenter))
        lay.addWidget(dtls)

    def _diagnosticsLayout(self, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        # General
        gbox_gen = QGroupBox('General Controls')
        gbox_gen.setLayout(self._genDiagLayout(chs_dict['General']))

        # Levels
        gbox_lvls = QGroupBox('Levels')
        lay_lvls = QGridLayout()
        lay_lvls.setAlignment(Qt.AlignTop)
        lay_lvls.setSpacing(9)
        gbox_lvls.setLayout(lay_lvls)

        row = 0
        for key, val in chs_dict['Levels'].items():
            if key.split()[-1] == 'Extra':
                label = QLabel(f'Limit {key[:-len("Extra")]}')
            else:
                label = QLabel(f'Limit {key}')
            lb = SiriusLabel(self, self.prefix+val+'-RB')
            lb.showUnits = True
            lb_w = SiriusLabel(self, self.prefix+val+'W-Mon')
            lb_w.showUnits = True
            lay_lvls.addWidget(label, row, 0)
            lay_lvls.addItem(QSpacerItem(
                9, 0, QSzPlcy.Fixed, QSzPlcy.Ignored), row, 1)
            lay_lvls.addWidget(SiriusSpinbox(
                self, self.prefix+val+'-SP'), row, 2)
            lay_lvls.addWidget(lb, row, 3)
            lay_lvls.addWidget(lb_w, row, 4)
            row += 1
            if key == 'RevSSA4 (RF In 12)':
                lay_lvls.addItem(QSpacerItem(
                    0, 18, QSzPlcy.Ignored, QSzPlcy.Fixed), row, 0)
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

        lay.addWidget(gbox_lvls, 0, 0)
        lay.addWidget(gbox_inp, 0, 1)
        lay.addWidget(gbox_intlk, 0, 2)
        lay.addWidget(gbox_out, 0, 3)
        lay.addWidget(gbox_gen, 1, 0, 1, 2)

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
        keys = ['Manual', 'EndSw', 'Beam Inv',
            'Vacuum Inv', 'SSA Bypass', 'Bypass']
        row = 2
        column = 0
        for key in keys:
            lay.addWidget(QLabel(chs_dict[key][0]), row, column)
            lay.addWidget(PyDMStateButton(
                self, self.prefix+chs_dict[key][1]+'-Sel'), row, column+1)
            lay.addWidget(SiriusLedState(
                self, self.prefix+chs_dict[key][1]+'-Sts'),
                row, column+2, alignment=Qt.AlignCenter)
            row += 1
            if row == 4:
                row = 0
                column += 3

        return lay

    def _setupByteMonitor(self, lay, labels, channel):
        for bit in range(len(labels)):
            lay.addWidget(QLabel(labels[bit]), bit+1, 0)
            lay.addWidget(SiriusLedState(
                self, channel, bit), bit+1, 1, alignment=Qt.AlignCenter)

    def _dynamicInterlockLayout(self, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        # Current
        lb_curr = SiriusLabel(self, self.prefix+chs_dict['Curr'])
        lb_curr.showUnits = True
        lb_delta = SiriusLabel(self, self.prefix+chs_dict['Curr Delta']+'-RB')
        lb_delta.showUnits = True

        lay.addWidget(QLabel(
            '<h4>Readback</h4>', alignment=Qt.AlignCenter), 0, 1)
        lay.addWidget(QLabel(
            '<h4>Delta</h4>', alignment=Qt.AlignCenter), 0, 2, 1, 2)
        lay.addWidget(QLabel(
            '<h4>Current</h4>',
            alignment=Qt.AlignRight | Qt.AlignVCenter), 1, 0)
        lay.addWidget(lb_curr, 1, 1, alignment=Qt.AlignCenter)
        lay.addWidget(SiriusLineEdit(
            self, self.prefix+chs_dict['Curr Delta']+'-SP'),
            1, 2, alignment=Qt.AlignCenter)
        lay.addWidget(lb_delta, 1, 3, alignment=Qt.AlignCenter)
        lay.addItem(QSpacerItem(0, 20, QSzPlcy.Ignored, QSzPlcy.Fixed), 2, 0)

        # Rev Cav, Fwd Cav and Quench Cond 1 Ratio
        # # Header
        lay.addWidget(QLabel(
            '<h4>Readback</h4>', alignment=Qt.AlignCenter), 3, 1)
        lay.addWidget(QLabel(
            '<h4>Enable</h4>', alignment=Qt.AlignCenter), 3, 2)
        lay.addWidget(QLabel(
            '<h4>Coeff</h4>', alignment=Qt.AlignCenter), 3, 3, 1, 2)
        lay.addWidget(QLabel(
            '<h4>Offset</h4>', alignment=Qt.AlignCenter), 3, 5, 1, 2)

        # # Body
        keys = ['Fwd Cav', 'Rev Cav', 'Quench']
        row = 4
        for key in keys:
            chs = chs_dict[key]

            lb_value = SiriusLabel(self, self.prefix+chs['Value'])
            lb_value.showUnits = True
            lb_coeff = SiriusLabel(self, self.prefix+chs['Coeff']+'-RB')
            lb_coeff.showUnits = True
            lb_ofs = SiriusLabel(self, self.prefix+chs['Offset']+'-RB')
            lb_ofs.showUnits = True

            lay_enable = QHBoxLayout()
            lay_enable.addWidget(PyDMStateButton(
                self, self.prefix+chs['Enable']+'-Sel'),
                alignment=Qt.AlignCenter)
            lay_enable.addWidget(SiriusLedState(
                self, self.prefix+chs['Enable']+'-Sts'),
                alignment=Qt.AlignCenter)

            lay.addWidget(QLabel(f'<h4>{chs["Label"]}</h4>',
                alignment=Qt.AlignRight | Qt.AlignVCenter), row, 0)
            lay.addWidget(lb_value, row, 1)
            lay.addLayout(lay_enable, row, 2)
            lay.addWidget(SiriusLineEdit(
                self, self.prefix+chs['Coeff']+'-SP'),
                row, 3, alignment=Qt.AlignCenter)
            lay.addWidget(lb_coeff, row, 4, alignment=Qt.AlignCenter)
            lay.addWidget(SiriusLineEdit(
                self, self.prefix+chs['Offset']+'-SP'),
                row, 5, alignment=Qt.AlignCenter)
            lay.addWidget(lb_ofs, row, 6, alignment=Qt.AlignCenter)

            row += 1

        lay.addItem(QSpacerItem(0, 20, QSzPlcy.Ignored, QSzPlcy.Fixed), row, 0)
        lay.addWidget(QLabel(
            "Out = Coef * Current + Offset",
            alignment=Qt.AlignCenter), row+1, 0, 1, 2)
        row += 2

        return lay

    def _bypassLayout(self, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)
        scarea = QScrollArea(self)
        scarea.setSizeAdjustPolicy(scarea.AdjustToContents)
        scarea.setWidgetResizable(True)
        scr_ar_wid = QWidget()
        scarea.setWidget(scr_ar_wid)
        scr_ar_wid.setObjectName('scrollarea')
        scr_ar_wid.setStyleSheet(
            '#scrollarea {background-color: transparent;}')
        lay.addWidget(scarea)

        lay_scr = QGridLayout(scr_ar_wid)
        lay_scr.setSpacing(9)

        lbs_header = ['Diagnostics', 'Ext LLRF', 'Tx PLC', 'FDL Trigger',
            'Pin Diode', 'Loops Standby']

        column = 2
        for lb in lbs_header:
            label = QLabel(lb, alignment=Qt.AlignCenter)
            label.setStyleSheet('min-width: 8em')
            lay_scr.addWidget(label, 0, column)
            column += 2

        for i in range(1, column):
            if i % 2 == 0 or i == 1:
                lay_scr.setColumnStretch(i, 1)
        lay_scr.setColumnMinimumWidth(1, 120)

        row = 1
        for key, val in chs_dict.items():
            lay_scr.addWidget(QLabel(key.split()[0]), row, 0)
            lay_scr.addWidget(QLabel(val[0]), row, 1)
            column = 2
            for bit in reversed(range(len(lbs_header))):
                lay_state = QHBoxLayout()
                pb = PyDMStateButton(self, self.prefix+val[1]+'-Sel', bit=bit)
                lay_state.addWidget(pb, alignment=Qt.AlignRight)
                lay_state.addWidget(SiriusLedState(
                    self, self.prefix+val[1]+'-Sts', bit),
                    alignment=Qt.AlignLeft)
                lay_scr.addLayout(lay_state, row, column)
                lay_scr.addItem(QSpacerItem(
                    9, 0, QSzPlcy.Ignored, QSzPlcy.Fixed), row, column+1)
                column += 2
            lay_scr.addWidget(SiriusPushButton(
                self, self.prefix+val[1]+'-Sel', 'All Zero', releaseValue=0),
                row, column)
            lay_scr.addWidget(SiriusPushButton(
                self, self.prefix+val[1]+'-Sel', 'All One', releaseValue=63),
                row, column+1)
            row += 1

        return lay
