"""Control of EVG Timing Device."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGridLayout, QLabel, QGroupBox
from siriushla.widgets import PyDMLed, PyDMLedMultiChannel
from .util import MPS_PREFIX, SEC_2_POS, SEC_2_STATUS


class MPSMonitor(QWidget):

    def __init__(self, parent=None, prefix=''):
        super().__init__(parent)
        self.prefix = prefix
        self.setWindowTitle('Linac MPS Monitor')
        self.setObjectName('LIApp')
        self._setupUi()

    def _setupUi(self):
        lay = QGridLayout(self)
        lay.setAlignment(Qt.AlignTop)

        lbl = QLabel('<h2>LI MPS</h2>', self)
        lay.addWidget(lbl, 0, 0, 1, 2)

        for sec, status in SEC_2_STATUS.items():
            gbox = QGroupBox(sec, self)
            grid = QGridLayout(gbox)
            if isinstance(status, dict):
                if 'Header' in status.keys():
                    for i, text in enumerate(status['Header']):
                        grid.addWidget(QLabel(text, self), 0, i+1,
                                       alignment=Qt.AlignCenter)
                    aux_row = 1
                    for text, ch_grp in status.items():
                        if text == 'Header':
                            continue
                        grid.addWidget(QLabel(text, self), aux_row, 0,
                                       alignment=Qt.AlignCenter)
                        for ch in ch_grp:
                            if not ch:
                                continue
                            aux_col = ch_grp.index(ch)
                            k = (MPS_PREFIX if 'RF' not in ch[0] else '')+ch[0]
                            ch2vals = {k: ch[1]}
                            led = PyDMLedMultiChannel(self)
                            led.set_channels2values(ch2vals)
                            grid.addWidget(led, aux_row, aux_col+1,
                                           alignment=Qt.AlignCenter)
                        aux_row += 1
                else:
                    aux_row = 0
                    for text, ch in status.items():
                        grid.addWidget(QLabel(text, self), aux_row, 0)
                        ch2vals = {MPS_PREFIX + ch[0]: ch[1]}
                        led = PyDMLedMultiChannel(self)
                        led.set_channels2values(ch2vals)
                        if 'Heartbeat' in text:
                            led.setOffColor(PyDMLed.Yellow)
                        grid.addWidget(led, aux_row, 1,
                                       alignment=Qt.AlignCenter)
                        aux_row += 1
            elif isinstance(status, list):
                for ch_grp in status:
                    aux_row = status.index(ch_grp)
                    for ch in ch_grp:
                        aux_col = ch_grp.index(ch)
                        ch2vals = {MPS_PREFIX + ch[0]: ch[1]}
                        led = PyDMLedMultiChannel(self)
                        led.set_channels2values(ch2vals)
                        grid.addWidget(led, aux_row, aux_col,
                                       alignment=Qt.AlignCenter)
            row, col, rowc, colc = SEC_2_POS[sec]
            lay.addWidget(gbox, row, col, rowc, colc)

            self.setStyleSheet("""
                QLabel { qproperty-alignment: AlignCenter; }
                QLed { min-width: 1.1em; max-width: 1.1em;
                       min-height: 1.1em; max-height: 1.1em; }
            """)
