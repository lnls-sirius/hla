"""LLRF Interlock Details."""

import qtawesome as qta
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QGroupBox, QLabel, QPushButton, \
    QScrollArea, QVBoxLayout, QWidget

from ...util import connect_window
from ...widgets import SiriusDialog, SiriusLabel, SiriusLedAlert
from ..advanced_details import AdvancedInterlockDetails
from ..util import DEFAULT_STYLESHEET, SEC_2_CHANNELS


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
        self.setStyleSheet(DEFAULT_STYLESHEET)
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignTop)

        self.title = QLabel(
            '<h4>LLRF Interlock Details</h4>', self,
            alignment=Qt.AlignCenter)
        lay.addWidget(self.title)

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
        lay_scr.setHorizontalSpacing(25)
        lay_scr.setVerticalSpacing(9)

        if self.section == 'SI':
            offset = 1
            for key, chs_dict in self.chs['LLRF Intlk Details'].items():
                self._setupDetails(lay_scr, chs_dict, offset, key)
                offset += 3
        else:
            self._setupDetails(lay_scr, self.chs['LLRF Intlk Details'], 1)

    def _setupDetails(self, lay, chs_dict, offset, system=''):
        if system:
            lay.addWidget(QLabel(
                f'<h4>LLRF {system}</h4>', self,
                alignment=Qt.AlignLeft), offset, 0)

        # inputs
        col = 0
        for name, dic in chs_dict['Inputs'].items():
            gbox = QGroupBox(name, self)
            lay_intlk = QGridLayout(gbox)
            lay_intlk.setAlignment(Qt.AlignTop)
            lay_intlk.setHorizontalSpacing(0)
            lay_intlk.setVerticalSpacing(0)

            icol = 0
            for key in dic['Status']:
                desc = QLabel(key, self, alignment=Qt.AlignCenter)
                desc.setStyleSheet('QLabel{min-width:2.5em; max-width:2.5em;}')
                lay_intlk.addWidget(desc, 0, icol, alignment=Qt.AlignCenter)
                icol += 1

            labels = dic['Labels']
            for idx, label in enumerate(labels):
                irow, icol = idx+1, 0
                for key, pvn in dic['Status'].items():
                    led = SiriusLedAlert(self, self.prefix+pvn, bit=idx)
                    led.shape = led.Square
                    if key != 'Mon':
                        led.offColor = led.DarkRed
                    lay_intlk.addWidget(led, irow, icol,
                        alignment=Qt.AlignHCenter)
                    icol += 1
                lbl = QLabel(label, self)
                lbl.setStyleSheet('QLabel{min-width:12em;}')
                lay_intlk.addWidget(lbl, irow, icol)

            lay.addWidget(gbox, offset+1, col, 2, 1)
            col += 1

        # timestamps
        gbox_time = QGroupBox('Timestamps', self)
        lay_time = QGridLayout(gbox_time)
        lay_time.setAlignment(Qt.AlignTop)
        lay_time.setHorizontalSpacing(9)
        lay_time.setVerticalSpacing(9)
        for idx, pvn in chs_dict['Timestamps'].items():
            irow = int(idx)-1
            desc = QLabel('Interlock '+idx, self, alignment=Qt.AlignCenter)
            desc.setStyleSheet('QLabel{min-width:6em;}')
            lbl = SiriusLabel(self, self.prefix+pvn)
            lbl.showUnits = True
            lay_time.addWidget(desc, irow, 0)
            lay_time.addWidget(lbl, irow, 1)
        lay.addWidget(gbox_time, offset+1, col)

        # advanced details
        pb_dtls = QPushButton(
            qta.icon('fa5s.external-link-alt'), ' Advanced Details', self)
        pb_dtls.setStyleSheet("min-width: 9em;")
        connect_window(
            pb_dtls, AdvancedInterlockDetails, parent=self,
            prefix=self.prefix, section=self.section, system=system)
        lay.addWidget(pb_dtls, offset+2, col, alignment=Qt.AlignCenter)
