"""."""

import numpy as np

from qtpy.QtCore import QSize
from qtpy.QtWidgets import QHBoxLayout, \
    QSizePolicy, QWidget, QDialog

from pydm.widgets.base import PyDMWidget

from siriushla.widgets import SiriusLedAlert, QLed, \
    SiriusConnectionSignal as _ConnSignal, \
    SelectionMatrixWidget as SelectionWidget


class AllowedBucketsMatrix(SelectionWidget, PyDMWidget):
    """Create the Selection Matrices for BPMs and Correctors."""

    def __init__(self, parent, device):
        """Initialize the matrix data of the specified dev."""

        # initialize SelectionWidget
        SelectionWidget.__init__(
            self, parent=parent, title="Allowed Buckets",
            has_bothplanes=False
        )

        # initialize PyDMWidget
        init_channel = device.substitute(propty='BucketListAllowedMask-RB')
        PyDMWidget.__init__(self, init_channel=init_channel)

        self.pv_sp = _ConnSignal(init_channel.replace('-RB', '-SP'))

        # connect signals and slots
        self.applyChangesClicked.connect(self.send_value)

    def sizeHint(self):
        """Return the base size of the widget."""
        return QSize(1800, 1200)

    # --- SelectionWidget specific methods ---

    def get_headers(self):
        top_headers = [f'{i+1:02d}' for i in range(32)]
        mima = zip(list(range(1, 864, 32)), list(range(32, 865, 32)))
        side_headers = [f'{i:03d}-{j:03d}' for i, j in mima]
        return top_headers, side_headers

    def get_widgets(self):
        widgets = list()
        sz_polc = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        for idx in range(864):
            wid = QWidget(self.parent())
            led = SiriusLedAlert()
            led.setParent(wid)
            led.setSizePolicy(sz_polc)
            led.setToolTip(f'{idx+1:03d}')
            hbl = QHBoxLayout(wid)
            hbl.setContentsMargins(0, 0, 0, 0)
            hbl.addWidget(led)
            widgets.append(wid)
        return widgets

    def get_positions(self):
        top_headers, side_headers = self.headers
        ltop = len(top_headers)
        positions = [divmod(idx, ltop) for idx in range(864)]
        return positions

    # --- PyDMWidget specific methods ---

    def send_value(self):
        if self.value is None:
            return
        value = self.value.copy()
        for i in range(value.size):
            wid = self.widgets[i]
            led = wid.findChild(QLed)
            if led.isSelected():
                value[i] = not value[i]
                led.setSelected(False)
        self.pv_sp.send_value_signal[np.ndarray].emit(value)

    def value_changed(self, new_val):
        if not isinstance(new_val, np.ndarray):
            return

        super(AllowedBucketsMatrix, self).value_changed(new_val)

        _, side_header_wids = self.header_widgets
        for i, wid in enumerate(self.widgets):
            led = wid.findChild(QLed)
            if i < self.value.size:
                wid.setVisible(True)
                led.state = not self.value[i]
            else:
                wid.setVisible(False)
        rsize = self.value.size / len(self.widgets)
        ini = int(len(side_header_wids) * rsize)
        for i, head in enumerate(side_header_wids):
            head.setVisible(i < ini)
        # self.adjustSize()
        parent = self.parent()
        while parent is not None:
            # parent.adjustSize()
            if isinstance(parent, QDialog):
                break
            parent = parent.parent()

    def connection_changed(self, new_conn):
        super(AllowedBucketsMatrix, self).connection_changed(new_conn)
        for wid in self.widgets:
            led = wid.findChild(QLed)
            led.setEnabled(new_conn)

    def _setupUi(self):
        super(AllowedBucketsMatrix, self)._setupUi(
            side_header_size_em=4, top_header_size_em=2
        )
