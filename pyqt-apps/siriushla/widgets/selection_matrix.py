"""Selection Widget."""

from functools import partial as _part

from qtpy.QtWidgets import QGridLayout, QHBoxLayout, QLabel, \
    QScrollArea, QWidget, QPushButton, QSizePolicy as QSzPol
from qtpy.QtCore import Qt, QRect, QPoint, Signal
from qtpy.QtGui import QBrush, QColor, QPainter

from siriushla.widgets.led import SiriusLedAlert

from .QLed import QLed


class SelectionMatrixWidget(QWidget):
    """Widget to perform component selection.

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget for the SelectionMatrixWidget.
    title: str, optional
        Widget title.
    has_bothplanes: bool, optional
        Whether to show button to send applyBothPlanesClicked signal.
        Default: False.
    toggle_all_false_text: string, optional
        Text to be dislayed in toggleAllItems to False button.
        Default: 'Disable All'.
    show_toggle_all_false: bool, optional
        Whether to show button to send toggleAllItems to False.
        Default: True.
    toggle_all_true_text: string, optional
        Text to be dislayed in toggleAllItems to True button.
        Default: 'Enable All'.
    show_toggle_all_true: bool, optional
        Whether to show button to send toggleAllItems to True.
        Default: True.
    use_scroll: bool, optional
        Whether to use or not QScrollArea.
        Default: True.

    Signals
    -------
    applyChangesClicked:
        emitted when "Apply Changes" button is clicked
    applyBothPlanesClicked:
        emitted when "Apply Both Planes" button is clicked
    """

    applyChangesClicked = Signal()
    applyBothPlanesClicked = Signal()

    def __init__(
            self, parent=None, title='', has_bothplanes=False,
            toggle_all_false_text='Disable All', show_toggle_all_false=True,
            toggle_all_true_text='Enable All', show_toggle_all_true=True,
            use_scroll=True):
        """Init."""
        super().__init__(parent)

        self.title = title
        self.has_bothplanes = has_bothplanes
        self.toggle_all_false_text = toggle_all_false_text
        self.show_toggle_all_false = show_toggle_all_false
        self.toggle_all_true_text = toggle_all_true_text
        self.show_toggle_all_true = show_toggle_all_true
        self.use_scroll = use_scroll

        self.begin = QPoint()
        self.end = QPoint()

        self._top_headers, self._side_headers = self.get_headers()
        self._widgets = self.get_widgets()
        self._positions = self.get_positions()
        self._top_header_wids, self._side_header_wids = list(), list()
        self._setupUi()

    def _setupUi(self):
        lay = QGridLayout(self)

        if self.title:
            lab = QLabel(self.title, self, alignment=Qt.AlignCenter)
            lab.setStyleSheet("font-weight: bold;")
            lay.addWidget(lab, 0, 0, 1, 1)

        # scroll area + widgets matrix
        scr_ar_wid = QWidget()
        scr_ar_wid.setObjectName('scrollarea')
        scr_ar_wid.setStyleSheet(
            '#scrollarea {background-color: transparent;}')
        if self.use_scroll:
            scr_ar = QScrollArea(self)
            scr_ar.setWidget(scr_ar_wid)
            scr_ar.setWidgetResizable(True)
            scr_ar.setSizeAdjustPolicy(scr_ar.AdjustToContents)
            lay.addWidget(scr_ar, 1, 0, 1, 1)
        else:
            scr_ar_wid.setSizePolicy(QSzPol.Maximum, QSzPol.Maximum)
            lay.addWidget(scr_ar_wid, 1, 0, 1, 1)

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
            led = wid.findChild(QLed)
            if not led:
                continue
            led.clicked.connect(led.toggleSelected)

        # action buttons
        hlay = QHBoxLayout()
        hlay.addStretch()

        self.btn_unsel_all = QPushButton('Undo Selection')
        self.btn_unsel_all.setDefault(True)
        self.btn_unsel_all.clicked.connect(self.undoItemsSelection)
        hlay.addWidget(self.btn_unsel_all)
        hlay.addStretch()

        self.btn_dsbl_all = QPushButton(self.toggle_all_false_text)
        self.btn_dsbl_all.clicked.connect(_part(self.toggleAllItems, False))
        self.btn_dsbl_all.setVisible(self.show_toggle_all_false)
        hlay.addWidget(self.btn_dsbl_all)
        if self.show_toggle_all_false:
            hlay.addStretch()

        self.btn_enbl_all = QPushButton(self.toggle_all_true_text)
        self.btn_enbl_all.clicked.connect(_part(self.toggleAllItems, True))
        self.btn_enbl_all.setVisible(self.show_toggle_all_true)
        hlay.addWidget(self.btn_enbl_all)
        if self.show_toggle_all_true:
            hlay.addStretch()

        self.btn_send = QPushButton('Apply Changes')
        self.btn_send.clicked.connect(self.applyChangesClicked.emit)
        hlay.addWidget(self.btn_send)
        hlay.addStretch()

        if self.has_bothplanes:
            self.btn_send_otpl = QPushButton('Apply Both Planes')
            self.btn_send_otpl.clicked.connect(
                self.applyBothPlanesClicked.emit)
            hlay.addWidget(self.btn_send_otpl)
            hlay.addStretch()

        lay.addLayout(hlay, 2, 0, 1, 1)

        lay.setSizeConstraint(lay.SetMinimumSize)

    def paintEvent(self, _):
        """Paint event to draw selection rectangle."""
        if self.begin == self.end:
            return
        painter = QPainter(self)
        brush = QBrush(QColor(100, 10, 10, 40))
        painter.setBrush(brush)
        painter.drawRect(QRect(self.begin, self.end))

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
        for wid in self._widgets:
            if not wid.isVisible():
                continue
            led = wid.findChild(QLed)
            if not led:
                continue
            pos = led.mapTo(self, led.pos())
            _sz = led.size()
            _x1 = pos.x()+_sz.width()/2 > self.begin.x()
            _x2 = pos.x()+_sz.width()/2 > self.end.x()
            _y1 = pos.y()+_sz.height()/2 > self.begin.y()
            _y2 = pos.y()+_sz.height()/2 > self.end.y()
            if _x1 != _x2 and _y1 != _y2:
                led.toggleSelected()

    def undoItemsSelection(self):
        """Undo items selection."""
        for wid in self._widgets:
            led = wid.findChild(QLed)
            if not led:
                continue
            led.setSelected(False)

    def toggleAllItems(self, value):
        """Toggle all items."""
        for wid in self._widgets:
            led = wid.findChild(QLed)
            if not led:
                continue
            new_sel = (bool(led.state) != value)
            if isinstance(led, SiriusLedAlert):
                if not new_sel:
                    led.setSelected(True)
            else:
                if new_sel:
                    led.setSelected(True)

    def selectWidgetsAt(self, idx, isrow=False):
        """Select widgets at idx (row or column)."""
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
