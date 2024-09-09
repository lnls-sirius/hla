"""SSA Currents Details."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QLabel, QSizePolicy as QSzPlcy, \
    QSpacerItem, QTabWidget, QVBoxLayout, QWidget, QGroupBox

from ...widgets import SiriusDialog, SiriusLabel
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

        # wid_graphs = QWidget(self)
        # wid_graphs.setLayout(self._setupGraphsLay())
        # dtls.addTab(wid_graphs, 'Graphs')

        lay.addWidget(QLabel(
            f'<h4>{self.title}</h4>', alignment=Qt.AlignCenter))
        lay.addWidget(dtls)

    def _setupDiagLay(self):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(18)

        row = 0
        column = 0
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
                else:
                    gbox_total = QGroupBox('Total Current')
                    gbox_total.setLayout(self._setupTotalLay(self.syst_dict['Total']))
                    lay.addWidget(gbox_total, row, column)
                column += 1
            elif column == 5:
                lay.addItem(QSpacerItem(
                    0, 9, QSzPlcy.Ignored, QSzPlcy.Fixed), row+1, 0)
                column = 0
                row += 2

        return lay

    def _setupHeatSinkLay(self, hs_num, chs_dict, row_label=''):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        lay.addWidget(QLabel(
            f'<h4>Heat Sink {hs_num}</h4>', alignment=Qt.AlignCenter),
            0, 1, 1, 4)
        lay.addWidget(QLabel(
            '<h4>A</h4>', alignment=Qt.AlignCenter), 1, 1, 1, 2)
        lay.addWidget(QLabel(
            '<h4>B</h4>', alignment=Qt.AlignCenter), 1, 3, 1, 2)

        for i in range(1, 9):
            base_pv = self.prefix+chs_dict['Curr']
            lb_a_1 = SiriusLabel(self, self._substitute_macros(
                base_pv, hs_num, 'A', i, 1))
            lb_a_1.showUnits = True
            lb_a_2 = SiriusLabel(self, self._substitute_macros(
                base_pv, hs_num, 'A', i, 2))
            lb_a_2.showUnits = True
            lb_b_1 = SiriusLabel(self, self._substitute_macros(
                base_pv, hs_num, 'B', i, 1))
            lb_b_1.showUnits = True
            lb_b_2 = SiriusLabel(self, self._substitute_macros(
                base_pv, hs_num, 'B', i, 2))
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

        return lay

    def _setupPreAmpLay(self, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        return lay

    def _setupTotalLay(self, chs_dict):
        lay = QGridLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(9)

        return lay

    def _substitute_macros(self, pv_name, hs_num='', letter='', m_num='', curr_num=''):
        pv_name = pv_name.replace('$(NB)', str(self.num))
        if hs_num:
            pv_name = pv_name.replace('$(hs_num)', str(hs_num))
        if letter:
            pv_name = pv_name.replace('$(letter)', str(letter))
        if m_num:
            pv_name = pv_name.replace('$(m_num)', str(m_num))
        if curr_num:
            pv_name = pv_name.replace('$(curr_num)', str(curr_num))
        return pv_name
