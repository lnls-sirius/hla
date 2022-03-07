"""Create the Selection Matrices for BPMs and Correctors."""

from functools import partial as _part

import numpy as np

from qtpy.QtWidgets import QGridLayout, QHBoxLayout, QLabel, \
    QSizePolicy, QScrollArea, QWidget, QPushButton, QDialog, QTabWidget
from qtpy.QtCore import Qt, QRect, QPoint, Signal
from qtpy.QtGui import QBrush, QColor, QPainter

from pydm.widgets.base import PyDMWidget

from siriushla.widgets import SiriusLedAlert, QLed, \
    SiriusConnectionSignal as _ConnSignal
from siriushla.as_ap_sofb.ioc_control.base import BaseObject, BaseWidget


class SelectionWidget(QWidget):
    """Widget to perform component selection.

    Parameters
    ----------
    title: str, optional
        Selection widget title.
    has_bothplanes: bool, optional
        Whether to show button to send sendBothPlanes signal. Default: False.
    parent : QWidget, optional
        The parent widget for the SelectionWidget.

    Signals
    -------
    applyChangesClicked:
        emitted when "Apply Changes" button is clicked
    applyBothPlanesClicked:
        emitted when "Apply Both Planes" button is clicked
    """

    applyChangesClicked = Signal()
    applyBothPlanesClicked = Signal()

    def __init__(self, parent=None, title='', has_bothplanes=False):
        """Init."""
        super().__init__(parent)

        self.title = title
        self.has_bothplanes = has_bothplanes

        self.begin = QPoint()
        self.end = QPoint()

        self._top_headers, self._side_headers = self.get_headers()
        self._widgets = self.get_widgets()
        self._positions = self.get_positions()
        self._top_header_wids, self._side_header_wids = list(), list()
        self._setupUi()

    def _setupUi(self):
        lay = QGridLayout(self)

        lab = QLabel(self.title, self, alignment=Qt.AlignCenter)
        lab.setStyleSheet("font-weight: bold;")
        lay.addWidget(lab, 0, 0, 1, 1)

        # scroll area + widgets matrix
        scr_ar = QScrollArea(self)
        scr_ar_wid = QWidget()
        scr_ar_wid.setObjectName('scrollarea')
        scr_ar_wid.setStyleSheet(
            '#scrollarea {background-color: transparent;}')
        scr_ar.setWidgetResizable(True)
        scr_ar.setWidget(scr_ar_wid)
        lay.addWidget(scr_ar, 1, 0, 1, 1)

        glay = QGridLayout(scr_ar_wid)
        glay.setContentsMargins(0, 0, 0, 0)
        for i, head in enumerate(self._top_headers):
            head_wid = QPushButton(head, self)
            head_wid.setStyleSheet('min-width:2em;')
            head_wid.clicked.connect(
                _part(self.selectWidgetsAt, i, isrow=False))
            self._top_header_wids.append(head_wid)
            glay.addWidget(head_wid, 0, i+1)
        for i, head in enumerate(self._side_headers):
            head_wid = QPushButton(head, self)
            head_wid.setStyleSheet('min-width:2em;')
            head_wid.clicked.connect(
                _part(self.selectWidgetsAt, i, isrow=True))
            self._side_header_wids.append(head_wid)
            glay.addWidget(head_wid, i+1, 0)
        for i, wid in enumerate(self._widgets):
            pos = self._positions[i]
            glay.addWidget(wid, pos[0]+1, pos[1]+1)

        # action buttons
        self.btn_unsel_all = QPushButton('Undo Selection')
        self.btn_unsel_all.clicked.connect(self.undoItemsSelection)
        self.btn_dsbl_all = QPushButton('Disable All')
        self.btn_dsbl_all.clicked.connect(_part(self.toogleAllItems, False))
        self.btn_enbl_all = QPushButton('Enable All')
        self.btn_enbl_all.clicked.connect(_part(self.toogleAllItems, True))
        self.btn_send = QPushButton('Apply Changes')
        self.btn_send.clicked.connect(self.applyChangesClicked.emit)
        if self.has_bothplanes:
            self.btn_send_otpl = QPushButton('Apply Both Planes')
            self.btn_send_otpl.clicked.connect(
                self.applyBothPlanesClicked.emit)

        hlay = QHBoxLayout()
        hlay.addStretch()
        hlay.addWidget(self.btn_unsel_all)
        hlay.addStretch()
        hlay.addWidget(self.btn_dsbl_all)
        hlay.addStretch()
        hlay.addWidget(self.btn_enbl_all)
        hlay.addStretch()
        hlay.addWidget(self.btn_send)
        hlay.addStretch()
        if self.has_bothplanes:
            hlay.addWidget(self.btn_send_otpl)
        lay.addLayout(hlay, 2, 0, 1, 1)

        lay.setSizeConstraint(lay.SetMinimumSize)

    def paintEvent(self, _):
        """Paint event to draw selection rectangle."""
        if self.begin == self.end:
            return
        qp = QPainter(self)
        br = QBrush(QColor(100, 10, 10, 40))
        qp.setBrush(br)
        qp.drawRect(QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        """Mouse press event."""
        self.begin = event.pos()
        self.end = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        """Mouse move event."""
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        """Mouse release event."""
        self.end = event.pos()
        self.selectItems()
        self.begin = event.pos()
        self.update()

    def selectItems(self):
        """Select items."""
        for i, wid in enumerate(self._widgets):
            if not wid.isVisible():
                continue
            led = wid.findChild(QLed)
            if not led:
                continue
            pos = led.mapTo(self, led.pos())
            sz = led.size()
            x1 = pos.x()+sz.width()/2 > self.begin.x()
            x2 = pos.x()+sz.width()/2 > self.end.x()
            y1 = pos.y()+sz.height()/2 > self.begin.y()
            y2 = pos.y()+sz.height()/2 > self.end.y()
            if x1 != x2 and y1 != y2:
                led.toggleSelected()

    def undoItemsSelection(self):
        for wid in self._widgets:
            led = wid.findChild(QLed)
            if not led:
                continue
            led.setSelected(False)

    def toogleAllItems(self, value):
        for wid in self._widgets:
            led = wid.findChild(QLed)
            if not led:
                continue
            if not (bool(led.state) != value):
                led.setSelected(True)

    def selectWidgetsAt(self, idx, isrow=False):
        for i, wid in enumerate(self._widgets):
            row, col = self._positions[i]
            led = wid.findChild(QLed)
            if not led:
                continue
            if isrow and row == idx:
                led.toggleSelected()
            if not isrow and col == idx:
                led.toggleSelected()

    # --- properties ---

    @property
    def headers(self):
        """Return top and side header text lists, respectively."""
        return self._top_headers, self._side_headers

    @property
    def header_widgets(self):
        """Return top and side header widget lists, respectively."""
        return self._top_header_wids, self._side_header_wids

    @property
    def widgets(self):
        """Return widget list."""
        return self._widgets

    @property
    def positions(self):
        """Return widget position list."""
        return self._positions

    # --- specific methods, should be implemented in derivation ---

    def get_headers(self):
        """
        Should be implemented in class derivation.

        Return
        ------
        top_headers: tuple or list
            A list of strings for top headers of the selection matrix widget.
        side_headers: tuple or list
            A list of strings for side headers of the selection matrix widget.
        """
        raise NotImplementedError

    def get_widgets(self):
        """
        Should be implemented in class derivation.

        Return
        ------
        widgets: tuple or list
            A tuple or list of widgets to be put in matrix.
        """
        raise NotImplementedError

    def get_positions(self):
        """
        Should be implemented in class derivation.

        Return
        ------
        positions: tuple or list
            A tuple or list of layout positions for each widget
            returned by get_widgets.
        """
        raise NotImplementedError


class SingleSelMatrix(BaseObject, SelectionWidget, PyDMWidget):
    """Create the Selection Matrices for BPMs and Correctors."""

    def __init__(self, parent, dev, device, prefix='', acc='SI'):
        """Initialize the matrix data of the specified dev."""

        # initialize BaseObject
        BaseObject.__init__(self, device, prefix=prefix, acc=acc)
        self.dev = dev
        max_rz = self._csorb.MAX_RINGSZ
        bpms = np.array(self._csorb.bpm_pos)
        bpm_pos = [bpms + i*self._csorb.circum for i in range(max_rz)]
        bpm_pos = np.hstack(bpm_pos)
        bpm_name = self._csorb.bpm_names * max_rz
        bpm_nknm = self._csorb.bpm_nicknames * max_rz
        self.devpos = {
            'BPMX': bpm_pos,
            'BPMY': bpm_pos,
            'CH': self._csorb.ch_pos,
            'CV': self._csorb.cv_pos}
        self.devotpl = {
            'BPMX': 'BPMY', 'BPMY': 'BPMX', 'CH': 'CV', 'CV': 'CH'}
        self.devnames = {
            'BPMX': (bpm_name, bpm_nknm),
            'BPMY': (bpm_name, bpm_nknm),
            'CH': (self._csorb.ch_names, self._csorb.ch_nicknames),
            'CV': (self._csorb.cv_names, self._csorb.cv_nicknames)}

        # initialize SelectionWidget
        SelectionWidget.__init__(
            self, parent=parent, title=dev + "List",
            has_bothplanes=dev.lower().startswith('bpm'))

        # initialize PyDMWidget
        init_channel = self.devpref.substitute(propty=self.dev+'EnblList-RB')
        PyDMWidget.__init__(self, init_channel=init_channel)

        self.pv_sp = _ConnSignal(init_channel.replace('-RB', '-SP'))
        self.pv_otpl = _ConnSignal(self.devpref.substitute(
            propty=self.devotpl[self.dev]+'EnblList-SP'))

        # connect signals and slots
        self.applyChangesClicked.connect(self.send_value)
        self.applyBothPlanesClicked.connect(_part(self.send_value, other=True))

    # --- SelectionWidget specific methods ---

    def get_headers(self):
        _, nicks = self.devnames[self.dev]
        if self.acc == 'BO':
            top_headers = ['{0:02d}'.format(i) for i in range(1, 11)]
            if self.dev.startswith('C'):
                top_headers = top_headers[::2]
            side_headers = [
                '01-10', '11-20', '21-30', '31-40', '41-50', '01-10']
            if nicks[-1][:2] != '01':
                side_headers = side_headers[:-1]
        elif self.acc == 'SI':
            top_headers = sorted({nick[2:] for nick in nicks})
            top_headers = top_headers[-2:] + top_headers[:-2]
            side_headers = sorted({nick[:2] for nick in nicks})
            side_headers.append(side_headers[0])
        else:
            top_headers = nicks
            side_headers = [' ']
        if self.dev.lower().startswith('bpm'):
            side_headers *= self._csorb.MAX_RINGSZ
        return top_headers, side_headers

    def get_widgets(self):
        widgets = list()
        sz_polc = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        for idx in range(len(self.devnames[self.dev][0])):
            wid = QWidget(self.parent())
            led = SiriusLedAlert()
            led.setParent(wid)
            led.setSizePolicy(sz_polc)
            led.clicked.connect(led.toggleSelected)
            tooltip = self.devnames[self.dev][1][idx]
            tooltip += '; Pos = {0:5.1f} m'.format(self.devpos[self.dev][idx])
            led.setToolTip(tooltip)
            hbl = QHBoxLayout(wid)
            hbl.addWidget(led)
            widgets.append(wid)
        return widgets

    def get_positions(self):
        top_headers, side_headers = self.headers
        positions = list()
        for idx in range(len(self.devnames[self.dev][0])):
            _, nicks = self.devnames[self.dev]
            rsize, hsize, i = len(nicks), len(side_headers), 0
            if self.dev.lower().startswith('bpm'):
                rsize //= self._csorb.MAX_RINGSZ
                hsize //= self._csorb.MAX_RINGSZ
                i = (idx // rsize) * hsize
            if self.acc == 'BO':
                sec = int(nicks[idx][:2])
                j = ((sec-1) % 10) + 1
                j = top_headers.index('{0:02d}'.format(j))
                if not (idx+1) % rsize and sec == 1:
                    i += hsize - 1
                else:
                    i += (sec-1) // 10
            elif self.acc == 'SI':
                j = top_headers.index(nicks[idx][2:])
                if not (idx+1) % rsize:
                    i += hsize-1
                else:
                    i += ((idx % rsize) + 1) // len(top_headers)
            else:
                j = idx
            positions.append((i, j))
        return positions

    # --- PyDMWidget specific methods ---

    def send_value(self, other=False):
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
        if other:
            self.pv_otpl.send_value_signal[np.ndarray].emit(value)

    def value_changed(self, new_val):
        super(SingleSelMatrix, self).value_changed(new_val)
        _, side_header_wids = self.header_widgets
        for i, wid in enumerate(self.widgets):
            led = wid.findChild(QLed)
            if i < self.value.size:
                led.setVisible(True)
                led.state = not self.value[i]
            else:
                led.setVisible(False)
        rsize = self.value.size / len(self.widgets)
        ini = int(len(side_header_wids) * rsize)
        for i, head in enumerate(side_header_wids):
            head.setVisible(i < ini)
        self.adjustSize()
        parent = self.parent()
        while parent is not None:
            parent.adjustSize()
            if isinstance(parent, QDialog):
                break
            parent = parent.parent()

    def connection_changed(self, new_conn):
        super(SingleSelMatrix, self).connection_changed(new_conn)
        for wid in self.widgets:
            led = wid.findChild(QLed)
            led.setEnabled(new_conn)


class SelectionMatrix(BaseWidget):

    def __init__(self, parent, device, prefix='', acc='SI'):
        super().__init__(parent, device, prefix=prefix, acc=acc)
        tab = QTabWidget(self)
        hbl = QHBoxLayout(self)
        hbl.addWidget(tab)
        hbl.setContentsMargins(0, 0, 0, 0)

        for dev in ('BPMX', 'BPMY', 'CH', 'CV'):
            wid = SingleSelMatrix(
                tab, dev, self.device, prefix=self.prefix, acc=self.acc)
            tab.addTab(wid, dev)
