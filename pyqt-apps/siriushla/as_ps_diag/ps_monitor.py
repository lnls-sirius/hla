"""Interface to handle general status."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGroupBox, QGridLayout, QLabel

from siriuspy.envars import vaca_prefix
from siriuspy.search import PSSearch
from siriuspy.csdevice.pwrsupply import Const as _PSc
from siriuspy.namesys import SiriusPVName

from siriushla.sirius_application import SiriusApplication
from siriushla.widgets import SiriusMainWindow, PyDMLedMultiChannel
from siriushla.util import run_newprocess, get_appropriate_color, \
    get_monitor_icon

from siriushla.as_ps_diag.util import lips2filters, asps2filters, sips2filters


class PSMonitor(SiriusMainWindow):
    """Power Supplies Monitor."""

    def __init__(self, parent=None, prefix=vaca_prefix):
        """Init."""
        super().__init__(parent)
        self._prefix = prefix
        self.setWindowTitle('PS Monitor')
        self.setObjectName('ASApp')
        cor = get_appropriate_color(section='AS')
        self.setWindowIcon(get_monitor_icon('mdi.car-battery', cor))
        self._setupUi()

    def _setupUi(self):
        cw = QWidget()
        layout = QGridLayout()
        layout.setHorizontalSpacing(15)

        for sec in ['LI', 'TB', 'BO', 'TS', 'SI']:
            status = self._make_magnets_groupbox(sec)
            if sec == 'LI':
                layout.addWidget(status, 1, 0)
            elif sec == 'TB':
                layout.addWidget(status, 2, 0)
            elif sec == 'BO':
                layout.addWidget(status, 1, 1)
            elif sec == 'TS':
                layout.addWidget(status, 2, 1)
            elif sec == 'SI':
                layout.addWidget(status, 1, 2, 2, 1)
        cw.setLayout(layout)
        self.setCentralWidget(cw)

    def _make_magnets_groupbox(self, sec):
        status = QGroupBox(sec, self)
        status_lay = QGridLayout()
        status_lay.setAlignment(Qt.AlignTop)
        if sec == 'SI':
            status_lay.setVerticalSpacing(20)
            status_lay.setHorizontalSpacing(20)
        status.setStyleSheet("""QLabel{max-height: 1.5em;}""")
        status.setLayout(status_lay)

        def get_ps2labels_dict(sec):
            if sec == 'LI':
                return lips2filters
            elif sec == 'SI':
                return sips2filters
            else:
                return asps2filters

        def get_psnames(sec, f):
            if sec != 'SI':
                f['sec'] = sec
            return PSSearch.get_psnames(filters=f)

        def get_ch2vals(sec, name):
            if sec == 'LI':
                return {self._prefix+name+':rdpwm': 1,
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
                if 'Sept' in name:
                    del ch2vals[self._prefix+name+':Intlk8-Mon']
                return ch2vals

            else:
                return {self._prefix+name+':DiagStatus-Mon': 0}

        def update_gridpos(row, col):
            new_col = 0 if col == col_count-1 else col+1
            new_row = row+1 if new_col == 0 else row
            return [new_row, new_col]

        def get_si_secpos(label):
            if 'B' in label:
                return (0, 0, 2, 1)
            elif 'QS' in label:
                return (4, 0, 1, 3)
            elif 'Q' in label:
                return (0, 1, 2, 1)
            elif 'S' in label:
                return (0, 2, 2, 1)
            elif 'PM' in label:
                return (1, 0, 1, 1)
            elif 'CH' in label:
                return (2, 0, 1, 3)
            elif 'CV' in label:
                return (3, 0, 1, 3)
            elif 'Trims' in label:
                return (5, 0, 1, 3)
            # elif 'FCH' in label:
            #     return (3, 1, 3, 1)
            # elif 'FCV' in label:
            #     return (3, 2, 3, 1)

        def get_col_count(sec, label):
            if 'QS' in label:
                return 8 if sec != 'SI' else 30
            elif 'CH' in label:
                return 8 if sec != 'SI' else 30
            elif 'CV' in label:
                return 8 if sec != 'SI' else 30
            elif 'Trims' in label:
                return 8 if sec != 'SI' else 30
            else:
                return 8

        row, col = 0, 0
        for label, ps in get_ps2labels_dict(sec).items():
            psnames = get_psnames(sec, ps)
            col_count = get_col_count(sec, label)
            if not psnames:
                continue
            if sec != 'SI':
                status_lay.addWidget(QLabel(label, self),
                                     row, col, 1, col_count)
                row += 1
                for name in psnames:
                    led = MyLed(self, get_ch2vals(sec, name))
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
                    led = MyLed(self, get_ch2vals(sec, name))
                    led.setObjectName(name)
                    led.setToolTip(name)
                    grid.addWidget(led, aux_row, aux_col)
                    aux_row, aux_col = update_gridpos(aux_row, aux_col)
                row, col, rowc, colc = get_si_secpos(label)
                status_lay.addLayout(grid, row, col, rowc, colc,
                                     alignment=Qt.AlignTop)
        if sec == 'SI':
            status_lay.setColumnStretch(0, 1)
            status_lay.setColumnStretch(1, 1)
            status_lay.setColumnStretch(2, 1)

        return status


class MyLed(PyDMLedMultiChannel):

    def mouseDoubleClickEvent(self, ev):
        dev = SiriusPVName(self.objectName())
        if dev.dis == 'PS' and dev.sec != 'LI':
            run_newprocess(['sirius-hla-as-ps-detail.py', dev])
        elif dev.dis == 'PU':
            run_newprocess(['sirius-hla-as-pu-detail.py', dev])


if __name__ == '__main__':
    import sys

    app = SiriusApplication()
    window = PSMonitor()
    window.show()
    sys.exit(app.exec_())
