"""Interface to handle general status."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGroupBox, QGridLayout, QLabel

from siriuspy.envars import VACA_PREFIX
from siriuspy.diagsys.psdiag.csdev import get_ps_diag_status_labels
from siriuspy.diagsys.pudiag.csdev import get_pu_diag_status_labels
from siriuspy.diagsys.lidiag.csdev import get_li_diag_status_labels
from siriuspy.namesys import SiriusPVName

from siriushla.sirius_application import SiriusApplication
from siriushla.widgets import SiriusMainWindow, SiriusLedAlert
from siriushla.widgets.dialog.pv_status_dialog import StatusDetailDialog
from siriushla.util import run_newprocess, get_appropriate_color, \
    get_monitor_icon
from .util import get_label2devices


class ASMonitor(SiriusMainWindow):
    """AS Monitor."""

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
        label = QLabel('<h2>Sirius Monitor</h2>', alignment=Qt.AlignCenter)
        label.setStyleSheet('max-height:1.29em;')

        cw = QWidget()
        self.setCentralWidget(cw)

        layout = QGridLayout(cw)
        layout.setHorizontalSpacing(12)

        layout.addWidget(label, 0, 0, 1, 2)
        for sec in ['LI', 'TB', 'BO', 'TS', 'SI']:
            status = self._make_groupbox(sec)
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
        layout.setColumnStretch(0, 6)
        layout.setColumnStretch(1, 5)

        self.setStyleSheet("""
            QLed {
                min-height: 1.1em; max-height: 1.1em;
                min-width: 1.1em; max-width: 1.1em;}
        """)

    def _make_groupbox(self, sec):
        status = QGroupBox(sec, self)
        status_lay = QGridLayout()
        status_lay.setAlignment(Qt.AlignTop)
        status.setStyleSheet("QLabel{max-height: 1.4em;}")
        status.setLayout(status_lay)

        def update_gridpos(row, col, col_count, offset=0):
            new_col = offset if col == offset+col_count-1 else col+1
            new_row = row+1 if new_col == offset else row
            return [new_row, new_col]

        def get_as_secpos(sec, label):
            sec2label2secpos = {
                'LI': {
                    'Spect': (0, 0, 1, 1),
                    'Q': (0, 1, 1, 1),
                    'Lens': (0, 2, 1, 1),
                    'Egun': (0, 3, 1, 1),
                    'Slnd': (1, 0, 1, 3),
                    'RF': (1, 3, 1, 1),
                    'CH/CV': (2, 0, 1, 4),
                },
                'TB': {
                    'B': (0, 0, 1, 2),
                    'Q': (1, 0, 1, 4),
                    'PM': (0, 2, 1, 2),
                    'CH/CV': (2, 0, 1, 4),
                },
                'BO': {
                    'B': (0, 0, 1, 1),
                    'Q': (0, 1, 1, 1),
                    'S': (1, 0, 1, 1),
                    'QS': (1, 1, 1, 1),
                    'PM': (2, 0, 1, 1),
                    'RF': (2, 1, 1, 1),
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
                    'RF': (0, 7, 1, 1),
                    'QS': (1, 1, 1, 2),
                    'CH': (1, 3, 1, 2),
                    'CV': (1, 5, 1, 1),
                    'Trims': (1, 6, 1, 2),
                },
            }
            return sec2label2secpos[sec][label]

        def get_col_count(sec, label):
            if label == 'QS':
                return 5
            elif label == 'CH':
                return 5 if sec != 'SI' else 6
            elif label == 'CV':
                return 5 if sec != 'SI' else 8
            elif 'Trims' in label:
                return 14
            elif label == 'S':
                return 11
            elif label == 'Q':
                return 10 if sec != 'SI' else 6
            elif label == 'CH/CV':
                return 20 if sec == 'BO' else 14
            elif label == 'Slnd':
                return 11
            elif label in ['ID-CH', 'ID-CV']:
                return 2
            else:
                return 10

        def get_sub_labels(label):
            sub2labels = {
                'QS': ('M1', 'M2', 'C1', 'C2', 'C3'),
                'CH': ('M1', 'M2', 'C1', 'C2', 'C3', 'C4'),
                'CV': ('M1', 'M2', 'C1', 'C2', ' ', 'C3', ' ', 'C4'),
                'Trims': ('M1', ' ', ' ', 'M2', ' ', ' ', 'C1', ' ',
                          'C2', ' ', 'C3', ' ', 'C4', ' ')}
            return sub2labels[label]

        row, col = 0, 0
        for label, devices in get_label2devices(sec).items():
            if not devices:
                continue
            grid = QGridLayout()
            grid.setVerticalSpacing(6)
            grid.setHorizontalSpacing(6)
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
                    aux = devices.pop(-1)
                    devices.insert(0, aux)
            elif sec == 'SI':
                if 'ID' not in label:
                    aux = devices.pop(-1)
                    devices.insert(0, aux)
                if label == 'Trims':
                    aux = devices.pop(-1)
                    devices.insert(0, aux)
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
            else:
                grid.addWidget(QLabel(label, self), 0, 0, 1, 4)
                aux_row, aux_col, offset = 1, 0, 0
            for name in devices:
                if label == 'Trims' and aux_row in (2, 6, 10, 14, 18) \
                        and aux_col in (0, 3):
                    grid.addWidget(QLabel(''), aux_row, aux_col)
                    aux_col += 1
                led = MyLed(self)
                led.setObjectName(name)
                led.setToolTip(name)
                led.channel = self._prefix+name+':DiagStatus-Mon'
                grid.addWidget(led, aux_row, aux_col)
                aux_row, aux_col = update_gridpos(
                    aux_row, aux_col, get_col_count(sec, label), offset)
            row, col, rowc, colc = get_as_secpos(sec, label)
            status_lay.addLayout(grid, row, col, rowc, colc,
                                 alignment=Qt.AlignTop)

        if sec == 'LI':
            status_lay.setColumnStretch(0, 1)
            status_lay.setColumnStretch(1, 5)
            status_lay.setColumnStretch(2, 5)
            status_lay.setColumnStretch(3, 3)
            status_lay.setVerticalSpacing(14)
            status_lay.setHorizontalSpacing(20)
        elif sec == 'BO':
            status_lay.setColumnStretch(0, 3)
            status_lay.setColumnStretch(1, 3)
            status_lay.setColumnStretch(2, 6)
            status_lay.setColumnStretch(3, 6)
            status_lay.setVerticalSpacing(14)
            status_lay.setHorizontalSpacing(20)
        elif sec == 'SI':
            status_lay.setColumnStretch(0, 1)
            status_lay.setColumnStretch(1, 2)
            status_lay.setColumnStretch(2, 2)
            status_lay.setColumnStretch(3, 3)
            status_lay.setColumnStretch(4, 3)
            status_lay.setColumnStretch(5, 8)
            status_lay.setColumnStretch(6, 14)
            status_lay.setColumnStretch(7, 3)
            status_lay.setVerticalSpacing(12)
            status_lay.setHorizontalSpacing(12)
        else:
            status_lay.setVerticalSpacing(14)
            status_lay.setHorizontalSpacing(16)

        return status


class MyLed(SiriusLedAlert):

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
        if event.button() == Qt.RightButton:
            if pvn.dis == 'PS':
                labels = get_ps_diag_status_labels(pvn.device_name)
            elif pvn.dis == 'PU':
                labels = get_pu_diag_status_labels()
            elif pvn.sec == 'LI':
                labels = get_li_diag_status_labels(pvn.device_name)
            self.msg = StatusDetailDialog(
                parent=self.parent(), pvname=pvn, labels=labels)
            self.msg.open()
        super().mousePressEvent(event)


if __name__ == '__main__':
    import sys

    app = SiriusApplication()
    window = ASMonitor()
    window.show()
    sys.exit(app.exec_())
