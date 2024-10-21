"""Transmission Line Status Details."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGridLayout, QHBoxLayout, QLabel, \
    QSizePolicy as QSzPlcy, QSpacerItem, QWidget

from ...widgets import PyDMLedMultiChannel, SiriusDialog, SiriusLabel, \
    SiriusLedAlert
from ..util import DEFAULT_STYLESHEET, SEC_2_CHANNELS


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
        self.setStyleSheet(DEFAULT_STYLESHEET)
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(15)

        self.title = QLabel(
            '<h4>Transm. Line - Detailed Status</h4>',
            self, alignment=Qt.AlignHCenter)
        lay.addWidget(self.title, 0, 0, 1, 4)
        lay.addItem(QSpacerItem(0, 10, QSzPlcy.Ignored, QSzPlcy.Fixed), 1, 0)

        offset = 0
        if self.section == 'SI':
            for key, chs_dict in self.chs['TL Sts'].items():
                self._setupDetails(lay, key, chs_dict, offset)
                offset += 2
        else:
            self._setupDetails(lay, None, self.chs['TL Sts'], offset)

    def _setupDetails(self, lay, key, chs_dict, offset):
        row = 2
        if key:
            lay.addWidget(QLabel(
                f'<h4>{key}<h4>', self,
                alignment=Qt.AlignRight), row, offset)
            row += 1

        for widget_id, pvname in chs_dict['label_led'].items():
            wid = QWidget()
            hlay = QHBoxLayout()
            wid.setLayout(hlay)
            hlay.setContentsMargins(0, 0, 0, 0)

            si_lbl_wid = SiriusLabel(
                self, self.prefix+pvname['label'])
            si_lbl_wid.showUnits = True
            si_lbl_wid.setMaximumWidth(100)
            si_lbl_wid.setStyleSheet('qproperty-alignment: AlignLeft;')
            hlay.addWidget(si_lbl_wid)

            si_led_wid = SiriusLedAlert(
                self, self.prefix+pvname['led'])
            hlay.addWidget(si_led_wid)

            lay.addWidget(QLabel(
                widget_id, self, alignment=Qt.AlignRight), row, offset)
            lay.addWidget(wid, row, offset+1)
            row += 1

        wid = QWidget()
        hlay = QHBoxLayout()
        wid.setLayout(hlay)
        hlay.setContentsMargins(0, 0, 0, 0)

        lb_circtin = SiriusLabel(
            self, self.prefix+chs_dict['Circulator Temp. In']['label'])
        lb_circtin.showUnits = True
        lb_circtin.setStyleSheet('qproperty-alignment: AlignLeft;')
        hlay.addWidget(lb_circtin)

        si_led_wid = PyDMLedMultiChannel(
            self, chs_dict['Circulator Temp. In']['led'])
        hlay.addWidget(si_led_wid)

        lay.addWidget(QLabel(
            'Circulator T In: ', self, alignment=Qt.AlignRight), row, offset)
        lay.addWidget(wid, row, offset + 1)
        row += 1

        for widget_id, pvname in chs_dict['label'].items():
            if not (self.section == 'BO'):
                si_lbl_wid = SiriusLabel(
                    self, self.prefix+pvname)
                si_lbl_wid.showUnits = True
                si_lbl_wid.setStyleSheet('qproperty-alignment: AlignLeft;')
                lay.addWidget(QLabel(
                    widget_id, self, alignment=Qt.AlignRight), row, offset)
                lay.addWidget(si_lbl_wid, row, offset+1)
                row += 1

        lay.addItem(QSpacerItem(
            0, 10, QSzPlcy.Ignored, QSzPlcy.Fixed), row, offset)
        row += 1

        for widget_id, pvname in chs_dict['led'].items():
            if not ((self.section == 'BO') and ('Detector Load' in widget_id)):
                si_led_wid = SiriusLedAlert(
                    self, self.prefix+pvname)
                lay.addWidget(QLabel(
                    f'{widget_id}: ', self, alignment=Qt.AlignRight),
                    row, offset)
                lay.addWidget(si_led_wid, row, offset+1)
                row += 1

        self.setStyleSheet("""
            SiriusLabel{
                qproperty-alignment: AlignLeft;
            }
            QLed{
                max-width: 1.29em;
            }""")
