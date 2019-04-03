"""Interface to handle general status."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGroupBox, QGridLayout, QLabel

from siriuspy.envars import vaca_prefix
from siriuspy.search.ps_search import PSSearch
from siriuspy.namesys import Filter

from siriushla.sirius_application import SiriusApplication
from siriushla.widgets import SiriusMainWindow, \
    PyDMLedMultiChannel

from siriushla.as_ps_diag.util import LINAC_PS, sec2label, \
    lips2labels, asps2labels, sips2labels


class PSMonitor(SiriusMainWindow):
    """Power Supplies Monitor."""

    def __init__(self, parent=None, prefix=vaca_prefix):
        """Init."""
        super().__init__(parent)
        self._prefix = prefix
        self.setWindowTitle('Power Supplies Monitor')
        self._setupUi()

    def _setupUi(self):
        cw = QWidget()
        layout = QGridLayout()
        layout.setHorizontalSpacing(15)

        for sec in sec2label.keys():
            if sec == 'LI':
                status = self._make_magnets_groupbox(sec)
                layout.addWidget(status, 1, 0, 2, 1)
            else:
                status = self._make_magnets_groupbox(sec)
                if sec == 'TB':
                    layout.addWidget(status, 1, 1)
                elif sec == 'BO':
                    layout.addWidget(status, 1, 2, 2, 1)
                elif sec == 'TS':
                    layout.addWidget(status, 2, 1)
                elif sec == 'SI':
                    layout.addWidget(status, 1, 3, 2, 1)
        cw.setLayout(layout)
        self.setCentralWidget(cw)

    def _make_magnets_groupbox(self, sec):
        status = QGroupBox(sec2label[sec], self)
        status_lay = QGridLayout()
        status_lay.setAlignment(Qt.AlignTop)
        if sec == 'SI':
            status_lay.setVerticalSpacing(20)
            status_lay.setHorizontalSpacing(20)
        status.setStyleSheet("""QLabel{max-height: 1.5em;}""")
        status.setLayout(status_lay)
        col_count = 10

        def get_ps2labels_dict(sec):
            if sec == 'LI':
                return lips2labels
            elif sec == 'SI':
                return sips2labels
            else:
                return asps2labels

        def get_psnames(sec, f):
            if sec == 'LI':
                return Filter.process_filters(LINAC_PS, filters={'dis': f})
            elif sec == 'SI':
                return PSSearch.get_psnames(filters=f)
            else:
                return PSSearch.get_psnames(filters={'sec': sec, 'dev': f})

        def get_ch2vals(sec, name):
            if sec == 'LI':
                return {self._prefix+name+':setpwm': 1,
                        self._prefix+name+':interlock': {'value': 55,
                                                         'comp': 'lt'}}
            else:
                return {self._prefix+name+':DiagStatus-Mon': 0}

        def update_gridpos(row, col):
            new_col = 0 if col == col_count-1 else col+1
            new_row = row+1 if new_col == 0 else row
            return [new_row, new_col]

        def get_si_secpos(label):
            if 'Dipole' in label:
                return (0, 0, 1, 1)
            elif 'Skew' in label:
                return (3, 0, 3, 1)
            elif 'Quad' in label:
                return (1, 0, 1, 1)
            elif 'Sext' in label:
                return (2, 0, 1, 1)
            elif 'Slow Hor' in label:
                return (0, 1, 3, 1)
            elif 'Fast Hor' in label:
                return (3, 1, 3, 1)
            elif 'Slow Ver' in label:
                return (0, 2, 3, 1)
            elif 'Fast Ver' in label:
                return (3, 2, 3, 1)
            elif 'Trims' in label:
                return (0, 3, 6, 1)

        row, col = 0, 0
        for key, value in get_ps2labels_dict(sec).items():
            label = key if sec == 'SI' else value
            ps = value if sec == 'SI' else key
            psnames = get_psnames(sec, ps)
            if not psnames:
                continue
            if sec != 'SI':
                status_lay.addWidget(QLabel(label, self),
                                     row, col, 1, col_count)
                row += 1
                for name in psnames:
                    led = PyDMLedMultiChannel(self, get_ch2vals(sec, name))
                    led.setObjectName(name)
                    led.setToolTip(name)
                    status_lay.addWidget(led, row, col)
                    row, col = update_gridpos(row, col)
                row, col = row+1, 0
            else:
                grid = QGridLayout()
                grid.setVerticalSpacing(6)
                grid.setHorizontalSpacing(6)
                grid.addWidget(QLabel(label, self), 0, 0, 1, 5)
                aux_row, aux_col = 1, 0
                for name in psnames:
                    led = PyDMLedMultiChannel(self, get_ch2vals(sec, name))
                    led.setObjectName(name)
                    led.setToolTip(name)
                    grid.addWidget(led, aux_row, aux_col)
                    aux_row, aux_col = update_gridpos(aux_row, aux_col)
                row, col, rowc, colc = get_si_secpos(label)
                status_lay.addLayout(grid, row, col, rowc, colc,
                                     alignment=Qt.AlignTop)

        return status


if __name__ == '__main__':
    import sys

    app = SiriusApplication()
    window = PSMonitor()
    window.show()
    sys.exit(app.exec_())
