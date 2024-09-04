"""Slow Loop Control Parameters Details."""

from pydm.widgets import PyDMEnumComboBox
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QLabel, QSizePolicy as QSzPlcy, \
    QSpacerItem, QVBoxLayout

from ...widgets import SiriusDialog, SiriusLabel, SiriusSpinbox
from ..util import SEC_2_CHANNELS


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
