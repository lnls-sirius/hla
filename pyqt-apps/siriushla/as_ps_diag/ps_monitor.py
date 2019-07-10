"""Interface to handle general status."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGroupBox, QGridLayout, QLabel

from siriuspy.envars import vaca_prefix
from siriuspy.search import PSSearch
from siriuspy.csdevice.pwrsupply import Const as _PSc

from siriushla.sirius_application import SiriusApplication
from siriushla.widgets import SiriusMainWindow, \
    PyDMLedMultiChannel

from siriushla.as_ps_diag.util import sec2label, \
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
            status = self._make_magnets_groupbox(sec)
            if sec == 'LI':
                layout.addWidget(status, 1, 0, 2, 1)
            elif sec == 'TB':
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
            if sec == 'SI':
                return PSSearch.get_psnames(filters=f)
            else:
                return PSSearch.get_psnames(filters={'sec': sec, 'dev': f})

        def get_ch2vals(sec, name):
            if sec == 'LI':
                return {self._prefix+name+':setpwm': 1,
                        self._prefix+name+':interlock': {'value': 55,
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
                if 'InjSept' in name:
                    del ch2vals[self._prefix+name+':Intlk8-Mon']
                return ch2vals

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
            # TODO: adjust to add pulsed magnets when using TS and SI

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
