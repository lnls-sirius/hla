"""QDoubleScrollBar module."""

import logging

from qtpy.QtWidgets import QInputDialog, QScrollBar, QMenu, QToolTip
from qtpy.QtCore import Qt, Signal, Slot, Property, QPoint

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class QDoubleScrollBar(QScrollBar):
    """A QScrollBar that handles float values."""

    rangeChanged = Signal(float, float)
    sliderMoved = Signal(float)
    valueChanged = Signal(float)

    def __init__(self, orientation=Qt.Horizontal, parent=None):
        """Init."""
        self._decimals = 0
        self._scale = 1
        super(QDoubleScrollBar, self).__init__(orientation, parent)
        super().rangeChanged.connect(self._intercept_rangeChanged)
        super().sliderMoved.connect(self._intercept_sliderMoved)
        super().valueChanged.connect(self._intercept_valueChanged)

        menu = QMenu(self)
        ac = menu.addAction('Set Single Step')
        ac.triggered.connect(self.dialogSingleStep)
        ac = menu.addAction('Set Page Step')
        ac.triggered.connect(self.dialogPageStep)
        menu.addSeparator()
        ac = menu.addAction("Left edge")
        ac.triggered.connect(lambda: self.triggerAction(self.SliderToMinimum))
        ac = menu.addAction("Right edge")
        ac.triggered.connect(lambda: self.triggerAction(self.SliderToMaximum))
        self.contextMenu = menu

    @Slot(bool)
    def dialogSingleStep(self, value):
        """Show dialog to set singleStep."""
        mini = 1/self._scale
        maxi = (self.maximum - self.minimum)/10
        d, okPressed = QInputDialog.getDouble(self, "Single Step",
                                              "Single Step:", self.singleStep,
                                              mini, maxi, self._decimals)
        if okPressed:
            self.setSingleStep(d)

    def dialogPageStep(self, value):
        """Show dialog to set pageStep."""
        mini = 10/self._scale
        maxi = (self.maximum - self.minimum)
        d, okPressed = QInputDialog.getDouble(self, "Page Step", "Page Step:",
                                              self.pageStep,
                                              mini, maxi, self._decimals)
        if okPressed:
            self.setPageStep(d)

    def contextMenuEvent(self, ev):
        """Show context menu."""
        self.contextMenu.exec_(ev.globalPos())

    def getDecimals(self):
        """Return decimals."""
        return self._decimals

    def setDecimals(self, value):
        """Set decimals."""
        mini = self.getMinimum()
        maxi = self.getMaximum()
        sgstep = self.getSingleStep()
        pgstep = self.getPageStep()
        val = self.getValue()
        slpos = self.getSliderPosition()

        self._decimals = value
        self._scale = 10**value
        self.setMinimum(mini)
        self.setMaximum(maxi)
        self.setSingleStep(sgstep)
        self.setPageStep(pgstep)
        self.setValue(val)
        self.setSliderPosition(slpos)

    decimals = Property(int, getDecimals, setDecimals)

    def getMinimum(self):
        """Return minimum value."""
        return super().minimum()/self._scale

    def setMinimum(self, value):
        """Set minimum value."""
        try:
            mini = round(value*self._scale)
            mini = min(mini, 2**31-1)
            mini = max(-2**31, mini)
            super().setMinimum(mini)
        except OverflowError as e:
            logging.warning(str(e), '(value=' + str(value) + ')')

    minimum = Property(float, getMinimum, setMinimum)

    def getMaximum(self):
        """Return maximum value."""
        return super().maximum()/self._scale

    def setMaximum(self, value):
        """Set maximum value."""
        try:
            maxi = round(value*self._scale)
            maxi = min(maxi, 2**31-1)
            maxi = max(-2**31, maxi)
            super().setMaximum(maxi)
        except OverflowError as e:
            logging.warning(str(e), '(value=' + str(value) + ')')

    maximum = Property(float, getMaximum, setMaximum)

    def getSingleStep(self):
        """Get single step."""
        return super().singleStep()/self._scale

    def setSingleStep(self, value):
        """Set single step."""
        val = round(value*self._scale)
        rang = super().maximum() - super().minimum()
        if not val:
            super().setSingleStep(1)
        elif val > round(rang/10):
            super().setSingleStep(round(rang/10))
        else:
            super().setSingleStep(val)

    singleStep = Property(float, getSingleStep, setSingleStep)

    def getPageStep(self):
        """Get page step."""
        return super().pageStep()/self._scale

    def setPageStep(self, value):
        """Set page step."""
        val = round(value*self._scale)
        rang = super().maximum() - super().minimum()
        if val < 10:
            super().setPageStep(10)
        elif val > round(rang):
            super().setPageStep(round(rang))
        else:
            super().setPageStep(val)

    pageStep = Property(float, getPageStep, setPageStep)

    def getValue(self):
        """Get value."""
        return super().value()/self._scale

    @Slot(float)
    def setValue(self, value):
        """Set value."""
        if value is None:
            return
        try:
            val = round(value*self._scale)
            val = min(val, 2**31-1)
            val = max(-2**31, val)
            super().setValue(val)
        except OverflowError as e:
            logging.warning(str(e), '(value=' + str(value) + ')')

    value = Property(float, getValue, setValue)

    def getSliderPosition(self):
        """Get slider position."""
        return super().sliderPosition()/self._scale

    def setSliderPosition(self, value):
        """Set slider position."""
        pos = round(value*self._scale)
        pos = min(pos, 2**31-1)
        pos = max(-2**31, pos)
        super().setSliderPosition(pos)

    sliderPosition = Property(float, getSliderPosition, setSliderPosition)

    def keyPressEvent(self, event):
        """Reimplement keyPressEvent."""
        singlestep = self.getSingleStep()
        pagestep = self.getPageStep()
        ctrl_hold = self.app.queryKeyboardModifiers() == Qt.ControlModifier
        if ctrl_hold and (event.key() == Qt.Key_Left):
            self.setSingleStep(10*singlestep)
            self.setPageStep(10*pagestep)
            self._show_step_tooltip()
        elif ctrl_hold and (event.key() == Qt.Key_Right):
            self.setSingleStep(0.1*singlestep)
            self.setPageStep(0.1*pagestep)
            self._show_step_tooltip()
        else:
            super().keyPressEvent(event)

    def _show_step_tooltip(self):
        QToolTip.showText(
            self.mapToGlobal(
                QPoint(self.x()+self.width()/2, self.y()-2*self.height())),
            'Single step: '+str(self.singleStep) +
            '\nPage step: '+str(self.pageStep),
            self, self.rect(), 1000)

    @Slot(float, float)
    def setRange(self, mini, maxi):
        """Set range."""
        mini = max(-2**31, round(mini/self._scale))
        maxi = min(round(maxi*self._scale), 2**31-1)
        super().setRange(mini, maxi)

    @Slot(int, int)
    def _intercept_rangeChanged(self, mini, maxi):
        self.rangeChanged.emit(mini/self._scale, maxi/self._scale)

    @Slot(int)
    def _intercept_sliderMoved(self, value):
        self.sliderMoved.emit(value/self._scale)

    @Slot(int)
    def _intercept_valueChanged(self, value):
        self.valueChanged.emit(value/self._scale)
