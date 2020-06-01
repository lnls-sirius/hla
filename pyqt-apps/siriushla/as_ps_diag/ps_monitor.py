"""Interface to handle general status."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGroupBox, QGridLayout, QLabel

from siriuspy.envars import VACA_PREFIX
from siriuspy.search import PSSearch
from siriuspy.pwrsupply.csdev import Const as _PSc
from siriuspy.psdiag.csdev import ETypes as _Et
from siriuspy.namesys import SiriusPVName

from siriushla.sirius_application import SiriusApplication
from siriushla.widgets import SiriusMainWindow, PyDMLedMultiChannel
from siriushla.widgets.dialog.pv_status_dialog import StatusDetailDialog
from siriushla.util import run_newprocess, get_appropriate_color, \
    get_monitor_icon

from .util import lips2filters, asps2filters, bops2filters, sips2filters


class PSMonitor(SiriusMainWindow):
    """Power Supplies Monitor."""

    def __init__(self, parent=None, prefix=VACA_PREFIX):
        """Init."""
        super().__init__(parent)
        self._prefix = prefix
        self.setWindowTitle('PS Monitor')
        self.setObjectName('ASApp')
        cor = get_appropriate_color(section='AS')
        self.setWindowIcon(get_monitor_icon('mdi.car-battery', cor))
        self._setupUi()

    def _setupUi(self):
        label = QLabel('<h2>PS Monitor</h2>', alignment=Qt.AlignCenter)
        label.setStyleSheet('max-height:1.29em;')

        cw = QWidget()
        self.setCentralWidget(cw)

        layout = QGridLayout(cw)
        layout.setHorizontalSpacing(12)

        layout.addWidget(label, 0, 0, 1, 2)
        for sec in ['LI', 'TB', 'BO', 'TS', 'SI']:
            status = self._make_magnets_groupbox(sec)
            if sec == 'LI':
                layout.addWidget(status, 1, 0)
            elif sec == 'TB':
                layout.addWidget(status, 1, 1)
            elif sec == 'BO':
                layout.addWidget(status, 2, 0)
            elif sec == 'TS':
                layout.addWidget(status, 2, 1)
            elif sec == 'SI':
                layout.addWidget(status, 3, 0, 1, 2)

        self.setStyleSheet("""
            QLed {
                min-height: 1.1em; max-height: 1.1em;
                min-width: 1.1em; max-width: 1.1em;}
        """)

    def _make_magnets_groupbox(self, sec):
        status = QGroupBox(sec, self)
        status_lay = QGridLayout()
        status_lay.setAlignment(Qt.AlignTop)
        status_lay.setVerticalSpacing(14)
        status_lay.setHorizontalSpacing(16)
        status.setStyleSheet("""QLabel{max-height: 1.4em;}""")
        status.setLayout(status_lay)

        def get_ps2labels_dict(sec):
            if sec == 'LI':
                return lips2filters
            elif sec == 'SI':
                return sips2filters
            elif sec == 'BO':
                return bops2filters
            else:
                return asps2filters

        def get_psnames(sec, f):
            if sec != 'SI':
                f['sec'] = sec
            return PSSearch.get_psnames(filters=f)

        def get_ch2vals(sec, name):
            if sec == 'LI':
                return {self._prefix+name+':PwrState-Sts': 1,
                        self._prefix+name+':StatusIntlk-Mon': {'value': 55,
                                                               'comp': 'lt'}}
            elif name.dis == 'PU':
                ch2vals = {
                    self._prefix+name+':PwrState-Sts': _PSc.PwrStateSts.On,
                    self._prefix+name+':Pulse-Sts': _PSc.DsblEnbl.Enbl,
                    self._prefix+name+':Intlk1-Mon': 1,
                    self._prefix+name+':Intlk2-Mon': 1,
                    self._prefix+name+':Intlk3-Mon': 1,
                    self._prefix+name+':Intlk4-Mon': 1,
                    self._prefix+name+':Intlk5-Mon': 1,
                    self._prefix+name+':Intlk6-Mon': 1,
                    self._prefix+name+':Intlk7-Mon': 1,
                    self._prefix+name+':Intlk8-Mon': 1}
                if 'Sept' in name:
                    del ch2vals[self._prefix+name+':Intlk8-Mon']
                return ch2vals

            else:
                return {self._prefix+name+':DiagStatus-Mon': 0}

        def update_gridpos(row, col, col_count, offset=0):
            new_col = offset if col == offset+col_count-1 else col+1
            new_row = row+1 if new_col == offset else row
            return [new_row, new_col]

        def get_as_secpos(sec, label):
            sec2label2secpos = {
                'LI': {
                    'Lens': (0, 0, 1, 1),
                    'Q': (0, 1, 1, 1),
                    'Spect': (0, 2, 1, 1),
                    'CH/CV': (1, 0, 1, 2),
                    'Slnd': (2, 0, 1, 3),
                },
                'TB': {
                    'B': (0, 0, 1, 2),
                    'Q': (1, 0, 1, 4),
                    'PM': (0, 2, 1, 2),
                    'CH/CV': (2, 0, 1, 4),
                },
                'BO': {
                    'B': (0, 0, 1, 1),
                    'QS': (1, 1, 1, 1),
                    'Q': (0, 1, 1, 1),
                    'S': (1, 0, 1, 1),
                    'PM': (2, 0, 1, 1),
                    'CH': (0, 2, 3, 3),
                    'CV': (0, 5, 3, 3),
                },
                'TS': {
                    'B': (0, 0, 1, 2),
                    'Q': (1, 0, 1, 4),
                    'PM': (0, 2, 1, 2),
                    'CH/CV': (2, 0, 1, 4),
                },
                'SI': {
                    'B': (0, 1, 1, 1),
                    'PM': (0, 2, 1, 1),
                    'ID-CH': (0, 3, 1, 1),
                    'ID-CV': (0, 4, 1, 1),
                    'Q': (0, 5, 1, 1),
                    'S': (0, 6, 1, 1),
                    'QS': (1, 1, 1, 2),
                    'CH': (1, 3, 1, 2),
                    'CV': (1, 5, 1, 2),
                    'Trims': (1, 6, 1, 1),
                    # 'FCH': (3, 1, 1, 1),
                    # 'FCV': (3, 2, 1, 1),
                },
            }
            return sec2label2secpos[sec][label]

        def get_col_count(sec, label):
            if label == 'QS':
                return 4
            elif label == 'CH':
                return 5 if sec != 'SI' else 6
            elif label == 'CV':
                return 5 if sec != 'SI' else 8
            elif 'Trims' in label:
                return 14
            elif label == 'S':
                return 10 if sec != 'SI' else 14
            elif label == 'Q':
                return 10 if sec != 'SI' else 8
            elif label == 'CH/CV':
                return 20 if sec == 'BO' else 14
            elif label == 'Slnd':
                return 16
            elif label in ['ID-CH', 'ID-CV']:
                return 2
            else:
                return 10

        def get_sub_labels(label):
            sub2labels = {
                'QS': ('M1', 'M2', 'C1', 'C3'),
                'CH': ('M1', 'M2', 'C1', 'C2', 'C3', 'C4'),
                'CV': ('M1', 'M2', 'C1', 'C2', ' ', 'C3', ' ', 'C4'),
                'Trims': ('M1', ' ', ' ', 'M2', ' ', ' ', 'C1', ' ',
                          'C2', ' ', 'C3', ' ', 'C4', ' ')}
            return sub2labels[label]

        row, col = 0, 0
        for label, ps in get_ps2labels_dict(sec).items():
            psnames = get_psnames(sec, ps)
            if not psnames:
                continue
            grid = QGridLayout()
            grid.setVerticalSpacing(6)
            grid.setHorizontalSpacing(6)
            if sec != 'SI':
                if sec == 'BO' and label in ['CH', 'CV']:
                    grid.addWidget(QLabel(label, self), 0, 0)
                    for i in range(5):
                        lbh = QLabel('{0:02d}'.format(i*2+1),
                                     self, alignment=Qt.AlignCenter)
                        grid.addWidget(lbh, 0, i+1)
                        lbv = QLabel('{0:02d}'.format(i*10),
                                     self, alignment=Qt.AlignCenter)
                        grid.addWidget(lbv, i+1, 0)
                    aux_row, aux_col, offset = 1, 1, 1
                    if label == 'CV':
                        aux = psnames.pop(-1)
                        psnames.insert(0, aux)
                else:
                    grid.addWidget(QLabel(label, self), 0, 0, 1, 4)
                    aux_row, aux_col, offset = 1, 0, 0
                for name in psnames:
                    led = MyLed(self, get_ch2vals(sec, name))
                    led.setObjectName(name)
                    led.setToolTip(name)
                    grid.addWidget(led, aux_row, aux_col)
                    aux_row, aux_col = update_gridpos(
                        aux_row, aux_col, get_col_count(sec, label), offset)
                row, col, rowc, colc = get_as_secpos(sec, label)
                status_lay.addLayout(grid, row, col, rowc, colc,
                                     alignment=Qt.AlignTop)
            else:
                if 'ID' not in label:
                    aux = psnames.pop(-1)
                    psnames.insert(0, aux)
                if label == 'Trims':
                    aux = psnames.pop(-1)
                    psnames.insert(0, aux)
                aux_row, aux_col, offset = 2, 0, 0
                if label in ['QS', 'Trims']:
                    aux_col, offset = 1, (1 if label == 'QS' else 0)
                    for i in range(1, 21):
                        lb = QLabel('{0:02d}'.format(i), self)
                        grid.addWidget(lb, i+1, (0 if label == 'QS' else 15))
                if label in ['QS', 'CH', 'CV', 'Trims']:
                    i = 0
                    for text in get_sub_labels(label):
                        lbh = QLabel(text, self, alignment=Qt.AlignCenter)
                        grid.addWidget(lbh, 1, offset+i)
                        i += 1
                else:
                    aux_row, aux_col, offset = 1, 0, 0
                grid.addWidget(QLabel(label, self), 0, offset, 1, 4)
                for name in psnames:
                    if label == 'Trims' and aux_row in (2, 6, 10, 14, 18) \
                            and aux_col in (0, 3):
                        grid.addWidget(QLabel(''), aux_row, aux_col)
                        aux_col += 1
                    led = MyLed(self, get_ch2vals(sec, name))
                    led.setObjectName(name)
                    led.setToolTip(name)
                    grid.addWidget(led, aux_row, aux_col)
                    aux_row, aux_col = update_gridpos(
                        aux_row, aux_col, get_col_count(sec, label), offset)
                row, col, rowc, colc = get_as_secpos(sec, label)
                status_lay.addLayout(grid, row, col, rowc, colc,
                                     alignment=Qt.AlignTop)
        if sec == 'SI':
            status_lay.setColumnStretch(0, 1)
            status_lay.setColumnStretch(1, 4)
            status_lay.setColumnStretch(2, 6)
            status_lay.setColumnStretch(3, 8)
            status_lay.setColumnStretch(4, 14)

        return status


class MyLed(PyDMLedMultiChannel):

    def mouseDoubleClickEvent(self, _):
        """Reimplement mouseDoubleClickEvent."""
        dev = SiriusPVName(self.objectName())
        if dev.dis == 'PS':
            run_newprocess(['sirius-hla-as-ps-detail.py', dev])
        elif dev.dis == 'PU':
            run_newprocess(['sirius-hla-as-pu-detail.py', dev])

    def mousePressEvent(self, event):
        """Reimplement mousePressEvent."""
        pvn = SiriusPVName(self.channels()[0].address)
        if pvn.sec != 'LI' and pvn.dis == 'PS':
            if event.button() == Qt.RightButton:
                self.msg = StatusDetailDialog(
                    parent=self.parent(), pvname=pvn,
                    labels=_Et.DIAG_STATUS)
                self.msg.open()
        super().mousePressEvent(event)


if __name__ == '__main__':
    import sys

    app = SiriusApplication()
    window = PSMonitor()
    window.show()
    sys.exit(app.exec_())
