"""Advanced loops details, including Polar and IQ loops."""

import qtawesome as qta
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QGroupBox, QHBoxLayout, QLabel, \
    QPushButton, QSizePolicy as QSzPlcy, QSpacerItem, QTabWidget, \
    QVBoxLayout, QWidget

from ...util import connect_window
from ...widgets import PyDMStateButton, SiriusDialog, SiriusEnumComboBox, \
    SiriusLabel, SiriusLedState, SiriusPushButton, SiriusSpinbox
from ..custom_widgets import RFTitleFrame
from ..util import DEFAULT_STYLESHEET, SEC_2_CHANNELS
from .limits import LimitsDetails


class LoopsDetails(SiriusDialog):
    """Advanced loops details, including Polar and IQ loops."""

    def __init__(self, parent=None, prefix='', section='', system=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.prefix += ('-' if prefix and not prefix.endswith('-') else '')
        self.section = section
        self.system = system
        self.chs = SEC_2_CHANNELS[self.section]
        self.setObjectName(self.section+'App')
        self.title = 'Loops Details'
        self.title += (f' - {self.system}' if self.section == 'SI' else '')
        self.setWindowTitle(self.title)
        if self.section == 'SI':
            self.syst_dict = self.chs['Loops'][self.system]
        else:
            self.syst_dict = self.chs['Loops']
        self._setupUi()

    def _setupUi(self):
        self.setStyleSheet(DEFAULT_STYLESHEET)
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignTop)

        title_frame = RFTitleFrame(self, self.system)
        lay_title = QVBoxLayout(title_frame)
        lay_title.addWidget(QLabel(
            f'<h4>{self.title}</h4>', alignment=Qt.AlignCenter))

        dtls = QTabWidget(self)
        dtls.setObjectName(self.section+'Tab')
        dtls.setStyleSheet(
            "#"+self.section+'Tab'+"::pane {"
            "    border-left: 2px solid gray;"
            "    border-bottom: 2px solid gray;"
            "    border-right: 2px solid gray;}")

        wid_controls = QWidget(self)
        wid_controls.setLayout(self._loopsControlLayout())
        dtls.addTab(wid_controls, 'Loops Control')

        wid_iq = QWidget(self)
        wid_iq.setLayout(self._specificLoopsLayout('Rect'))
        dtls.addTab(wid_iq, 'IQ Loops')

        wid_polar = QWidget(self)
        wid_polar.setLayout(self._specificLoopsLayout('Polar'))
        dtls.addTab(wid_polar, 'Polar Loops')

        lay.addWidget(title_frame)
        lay.addWidget(dtls)

    def _loopsControlLayout(self):
        lay = QVBoxLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        gbox_gen = QGroupBox('General Controls')
        gbox_gen.setLayout(self._setupGeneralControlsLayout(self.syst_dict['Control']))

        gbox_cond = QGroupBox('Conditioning')
        gbox_cond.setLayout(self._setupConditioningLayout(self.syst_dict['Conditioning']))

        lay.addWidget(gbox_gen)
        lay.addWidget(gbox_cond)

        return lay

    def _setupGeneralControlsLayout(self, chs_dict):
        lay = QGridLayout()
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
        lay.addWidget(QLabel('29', alignment=Qt.AlignCenter), 3, 0)
        lay.addWidget(QLabel(chs_dict['29'][0]), 3, 1)
        lay.addWidget(SiriusEnumComboBox(
            self, self.prefix+chs_dict['29'][1]+'-SP'),
            3, 2, alignment=Qt.AlignRight)
        lay.addWidget(lb_vinc, 3, 3)

        # # Phase Inc. Rate
        lb_pinc = SiriusLabel(self, self.prefix+chs_dict['28'][1]+'-RB',
            alignment=Qt.AlignCenter)
        lb_pinc.showUnits = True
        lay.addWidget(QLabel('28', alignment=Qt.AlignCenter), 4, 0)
        lay.addWidget(QLabel(chs_dict['28'][0]), 4, 1)
        lay.addWidget(SiriusEnumComboBox(
            self, self.prefix+chs_dict['28'][1]+'-SP'),
            4, 2, alignment=Qt.AlignRight)
        lay.addWidget(lb_pinc, 4, 3)

        # Look Reference
        lay.addWidget(QLabel('106', alignment=Qt.AlignCenter), 5, 0)
        lay.addWidget(QLabel(chs_dict['106'][0]), 5, 1)
        lay.addWidget(SiriusPushButton(
            self, self.prefix+chs_dict['106'][1],
            'OFF', pressValue=1, releaseValue=0),
            5, 2, alignment=Qt.AlignRight)
        lay.addWidget(SiriusLedState(
            self, self.prefix+chs_dict['106'][1]),
            5, 3, alignment=Qt.AlignCenter)

        # # Rect/Polar Mode Select
        lay.addWidget(QLabel('114', alignment=Qt.AlignCenter), 6, 0)
        lay.addWidget(QLabel(chs_dict['114'][0]), 6, 1)
        lay.addWidget(SiriusEnumComboBox(
            self, self.prefix+chs_dict['114'][1]+'-Sel'),
            6, 2, alignment=Qt.AlignRight)
        lay.addWidget(SiriusLabel(self, self.prefix+chs_dict['114'][1]+'-Sts',
            alignment=Qt.AlignCenter), 6, 3)

        # Quadrant Selection
        lay.addWidget(QLabel('107', alignment=Qt.AlignCenter), 7, 0)
        lay.addWidget(QLabel(chs_dict['107'][0]), 7, 1)
        lay.addWidget(SiriusEnumComboBox(
            self, self.prefix+chs_dict['107'][1]+'-Sel'),
            7, 2, alignment=Qt.AlignRight)
        lay.addWidget(SiriusLabel(self, self.prefix+chs_dict['107'][1]+'-Sts',
            alignment=Qt.AlignCenter), 7, 3)

        # Limits
        pb_limit = QPushButton(
            qta.icon('fa5s.external-link-alt'), ' Limits', self)
        connect_window(
            pb_limit, LimitsDetails, parent=self, prefix=self.prefix,
            section=self.section, system=self.system, which='Loop')
        pb_limit.setStyleSheet('min-width:8em')
        lay.addWidget(pb_limit, 9, 1)

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
        lay.addWidget(QLabel('31', alignment=Qt.AlignCenter), 4, 5)
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
        lay.addWidget(QLabel('80', alignment=Qt.AlignCenter), 5, 5)
        lay.addWidget(QLabel(chs_dict['80'][0]), 5, 6)
        lay.addWidget(lb_80, 5, 8)

        # Phase Correct Control
        lb_81 = SiriusLabel(self, self.prefix+chs_dict['81'][1],
            alignment=Qt.AlignCenter)
        lb_81.showUnits = True
        lay.addWidget(QLabel('81', alignment=Qt.AlignCenter), 6, 5)
        lay.addWidget(QLabel(chs_dict['81'][0]), 6, 6)
        lay.addWidget(lb_81, 6, 8)

        # Fwd Min Amp & Phs
        self._setupLabelEdit(lay, chs_dict, '125', 7, 5)

        return lay

    def _setupConditioningLayout(self, chs_dict):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        # Pulse Enable
        self._setupLedState(lay, chs_dict, '200', 0, True)

        # Auto Cond Enable
        self._setupLedState(lay, chs_dict, '201', 1, True)

        # Vacuum
        self._setupLedState(lay, chs_dict, '79', 2, False)

        # Duty Cycle
        self._setupLabelEdit(lay, chs_dict, '202', 0, 4)

        # Duty Cycle RB
        lb_condfreq = SiriusLabel(self, self.prefix+chs_dict['530'][1])
        lb_condfreq.showUnits = True
        lay.addWidget(QLabel('530', alignment=Qt.AlignCenter), 1, 4)
        lay.addWidget(QLabel(chs_dict['530'][0]), 1, 5)
        lay.addWidget(lb_condfreq, 1, 7, alignment=Qt.AlignCenter)

        row = 2
        if self.section == 'BO':
            relay_keys = [
                'CGC Fast Relay', 'Relay Setpoint RB', 'Relay Hysteria RB']
            for key in relay_keys:
                lb_relay = SiriusLabel(
                    self, self.prefix+chs_dict['Relay'][key]+'-RB')
                lb_relay.showUnits = True

                lay.addWidget(QLabel(key), row, 5)
                if key.split()[-1] != 'RB':
                    lay.addWidget(SiriusSpinbox(
                        self, self.prefix+chs_dict['Relay'][key]+'-SP'),
                        row, 6)
                lay.addWidget(lb_relay, row, 7)
                row += 1

        return lay

    def _setupLabelEdit(self, lay, chs_dict, key, row, column):
        label = SiriusLabel(self, self.prefix+chs_dict[key][1]+'-RB')
        label.showUnits = True

        lay.addWidget(QLabel(
            key.split()[0], alignment=Qt.AlignCenter), row, column)
        lay.addWidget(QLabel(chs_dict[key][0]), row, column+1)
        lay.addWidget(SiriusSpinbox(
            self, self.prefix+chs_dict[key][1]+'-SP'), row, column+2)
        lay.addWidget(label, row, column+3, alignment=Qt.AlignCenter)

    def _setupLedState(self, lay, chs_dict, key, row, has_button):
        lay.addWidget(QLabel(key, alignment=Qt.AlignCenter), row, 0)
        lay.addWidget(QLabel(chs_dict[key][0]), row, 1)

        ending = ''
        if has_button:
            lay.addWidget(PyDMStateButton(
                self, self.prefix+chs_dict[key][1]+'-Sel'),
                row, 2, alignment=Qt.AlignCenter)
            ending = '-Sts'

        lay.addWidget(SiriusLedState(
            self, self.prefix+chs_dict[key][1]+ending),
            row, 3, alignment=Qt.AlignCenter)

    def _specificLoopsLayout(self, rect_or_polar):
        lay = QVBoxLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)
        chs_dict = self.syst_dict[rect_or_polar]

        if rect_or_polar == 'Rect':
            extra_addr = '30' if self.section == 'SI' else ''
            grp_dict = {
                'Slow': ['100', '110', '13', '1', '0'],
                'Fast': ['115', '111', '124', '119', '118']
            }
        else:
            extra_addr = '527'
            grp_dict = {
                'Amp': ['116', '112', '121', '120'],
                'Phase': ['117', '113', '123', '122']
            }

        title_lay = QHBoxLayout()
        title_lay.addWidget(QLabel(
            f'<h3>{rect_or_polar} Loops</h3>', alignment=Qt.AlignCenter))
        title_lay.addWidget(SiriusLedState(
            self, self.prefix+self.syst_dict['Control']['Mode']))

        rect_lay = self._statisticsLayout(
            self.syst_dict, True, rect_or_polar, extra_addr)

        grps = QTabWidget(self)
        grps.setObjectName(self.section+'Tab')
        grps.setStyleSheet(
            "#"+self.section+'Tab'+"::pane {"
            "    border-left: 2px solid gray;"
            "    border-bottom: 2px solid gray;"
            "    border-right: 2px solid gray;}")

        for grp_name, addrs in grp_dict.items():
            grp_lay = QVBoxLayout()
            grp_lay.setAlignment(Qt.AlignTop)
            grp_lay.addLayout(
                self._controlLayout(chs_dict[grp_name]['Control'], addrs))
            grp_lay.addItem(QSpacerItem(0, 20, QSzPlcy.Ignored, QSzPlcy.Fixed))
            grp_lay.addLayout(
                self._statisticsLayout(chs_dict[grp_name], False))
            wid_grp = QWidget()
            wid_grp.setLayout(grp_lay)
            grps.addTab(wid_grp, f'{grp_name} Loop')

        lay.addLayout(title_lay)
        lay.addItem(QSpacerItem(0, 20, QSzPlcy.Ignored, QSzPlcy.Fixed))
        lay.addLayout(rect_lay)
        lay.addWidget(grps)

        return lay

    def _statisticsLayout(self, chs_dict, is_top_section, rect_or_polar='', extra_addr=''):
        lay = QGridLayout()
        lay.setHorizontalSpacing(18)

        lay.addWidget(QLabel(
            'In-Phase', alignment=Qt.AlignCenter), 0, 2)
        lay.addWidget(QLabel(
            'Quadrature', alignment=Qt.AlignCenter), 0, 3)
        lay.addWidget(QLabel(
            'Amp', alignment=Qt.AlignCenter), 0, 4)
        lay.addWidget(QLabel(
            'Phase', alignment=Qt.AlignCenter), 0, 5)
        if is_top_section:
            lay.addItem(QSpacerItem(
                24, 0, QSzPlcy.Fixed, QSzPlcy.Ignored), 0, 6)
            lay.addWidget(QLabel(
                'Power', alignment=Qt.AlignCenter), 0, 7, 1, 2)

        rows_dict = chs_dict
        if rect_or_polar != '':
            rows_dict = chs_dict['General'].copy()
            if extra_addr != '':
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
                    if column == 6:
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
