"""Interface to handle general status."""

import numpy as _np
import logging as _log

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGroupBox, QGridLayout, QLabel

from pydm.widgets.base import PyDMWidget

from siriuspy.envars import VACA_PREFIX
from siriuspy.diagsys.psdiag.csdev import get_ps_diag_status_labels
from siriuspy.diagsys.pudiag.csdev import get_pu_diag_status_labels
from siriuspy.diagsys.lidiag.csdev import get_li_diag_status_labels
from siriuspy.diagsys.rfdiag.csdev import get_rf_diag_status_labels
from siriuspy.namesys import SiriusPVName
from siriuspy.util import get_bit

from siriushla.sirius_application import SiriusApplication
from siriushla.widgets import PyDMLed
from siriushla.widgets.dialog.pv_status_dialog import StatusDetailDialog
from siriushla.util import run_newprocess
from .util import get_label2devices, get_dev2sub_labels, get_col2dev_count, \
    get_sec2dev_laypos


class PSMonitor(QWidget):
    """PS Monitor."""

    def __init__(self, parent=None, prefix=VACA_PREFIX,
                 get_label2devices_method=None,
                 get_dev2sublabels_method=None,
                 get_col2devcount_method=None,
                 get_sec2devlaypos_method=None):
        """Init."""
        super().__init__(parent)
        self._prefix = prefix
        self.get_label2devices = \
            get_label2devices_method or get_label2devices
        self.get_dev2sub_labels = \
            get_dev2sublabels_method or get_dev2sub_labels
        self.get_col2dev_count = \
            get_col2devcount_method or get_col2dev_count
        self.get_sec2dev_laypos = \
            get_sec2devlaypos_method or get_sec2dev_laypos
        self.setObjectName('ASApp')
        self._setupUi()

    def _setupUi(self):
        self.title = QLabel('<h2>PS & PU</h2>',
                            alignment=Qt.AlignCenter)
        self.title.setStyleSheet('max-height:1.29em;')

        layout = QGridLayout(self)
        layout.setHorizontalSpacing(12)

        layout.addWidget(self.title, 0, 0, 1, 2)
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

        row, col = 0, 0
        for label, devices in self.get_label2devices(sec).items():
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
                    for text in self.get_dev2sub_labels(label):
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
                led = MyLed(self, self._prefix+name+':DiagStatus-Mon', name)
                grid.addWidget(led, aux_row, aux_col)
                aux_row, aux_col = update_gridpos(
                    aux_row, aux_col, self.get_col2dev_count(sec, label),
                    offset)
            row, col, rowc, colc = self.get_sec2dev_laypos(sec, label)
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


class MyLed(PyDMLed):
    """Monitor Led."""

    default_colorlist = [PyDMLed.LightGreen, PyDMLed.Yellow, PyDMLed.Red]

    def __init__(self, parent=None, init_channel=None, init_tooltip='', **kws):
        super().__init__(parent, **kws)
        self.setToolTip(init_tooltip)
        self.channel = init_channel

        self.pvname = SiriusPVName(self.channels()[0].address)
        dev = self.pvname.device_name

        self.labels = list()
        if self.pvname.dis == 'PS':
            self.labels = get_ps_diag_status_labels(dev)
        elif self.pvname.dis == 'PU':
            self.labels = get_pu_diag_status_labels()
        elif self.pvname.sec == 'LI':
            self.labels = get_li_diag_status_labels(dev)
        elif self.pvname.dis == 'RF':
            self.labels = get_rf_diag_status_labels(dev)

        self.dc_command = ''
        if dev.dis == 'PS':
            self.dc_command = ['sirius-hla-as-ps-detail.py', dev]
        elif dev.dis == 'PU':
            self.dc_command = ['sirius-hla-as-pu-detail.py', dev]
        elif dev.dis == 'RF':
            if dev.sec == 'LI':
                self.dc_command = 'sirius-hla-li-rf-llrf.py'
            else:
                sec = self.pvname.sec.lower()
                self.dc_command = 'sirius-hla-'+sec+'-rf-control.py'
        elif dev.dis == 'EG':
            self.dc_command = 'sirius-hla-li-eg-control.py'

    def mouseDoubleClickEvent(self, _):
        """Reimplement mouseDoubleClickEvent."""
        if self.dc_command:
            run_newprocess(self.dc_command)

    def mousePressEvent(self, event):
        """Reimplement mousePressEvent."""
        if event.button() == Qt.RightButton and self.labels:
            self.msg = StatusDetailDialog(
                parent=self.parent(), pvname=self.pvname,
                labels=self.labels)
            self.msg.open()
        super().mousePressEvent(event)

    def value_changed(self, new_val):
        PyDMWidget.value_changed(self, new_val)
        if new_val is None:
            return
        if isinstance(new_val, _np.ndarray):
            _log.warning('PyDMLed received a numpy array to ' +
                         self.channel+' ('+str(new_val)+')!')
            return

        bits_set = [text for bit, text in enumerate(self.labels)
                    if get_bit(int(new_val), bit)]
        state = 0 if len(bits_set) == 0 \
            else 1 if len(bits_set) == 1 and \
            bits_set[0] == 'Alarms' else 2
        self.setState(state)


if __name__ == '__main__':
    import sys

    app = SiriusApplication()
    window = PSMonitor()
    window.show()
    sys.exit(app.exec_())
