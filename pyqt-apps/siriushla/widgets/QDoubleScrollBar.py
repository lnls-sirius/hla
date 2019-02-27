from qtpy.QtWidgets import QInputDialog, QScrollBar, QMenu, QToolTip
from qtpy.QtCore import Qt, Signal, Slot, Property, QPoint


class QDoubleScrollBar(QScrollBar):
    rangeChanged = Signal(float, float)
    sliderMoved = Signal(float)
    valueChanged = Signal(float)

    def __init__(self, orientation=Qt.Horizontal, parent=None):
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
        mini = 1/self._scale
        maxi = (self.maximum - self.minimum)/10
        d, okPressed = QInputDialog.getDouble(self, "Single Step",
                                              "Single Step:", self.singleStep,
                                              mini, maxi, self._decimals)
        if okPressed:
            self.setSingleStep(d)

    def dialogPageStep(self, value):
        mini = 10/self._scale
        maxi = (self.maximum - self.minimum)
        d, okPressed = QInputDialog.getDouble(self, "Page Step", "Page Step:",
                                              self.pageStep,
                                              mini, maxi, self._decimals)
        if okPressed:
            self.setPageStep(d)

    def contextMenuEvent(self, ev):
        self.contextMenu.exec_(ev.globalPos())

    def getDecimals(self):
        return self._decimals

    def setDecimals(self, value):
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
        return super().minimum()/self._scale

    def setMinimum(self, value):
        super().setMinimum(round(value*self._scale))
    minimum = Property(float, getMinimum, setMinimum)

    def getMaximum(self):
        return super().maximum()/self._scale

    def setMaximum(self, value):
        super().setMaximum(round(value*self._scale))
    maximum = Property(float, getMaximum, setMaximum)

    def getSingleStep(self):
        return super().singleStep()/self._scale

    def setSingleStep(self, value):
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
        return super().pageStep()/self._scale

    def setPageStep(self, value):
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
        return super().value()/self._scale

    @Slot(float)
    def setValue(self, value):
        if value is not None:
            super().setValue(round(value*self._scale))

    value = Property(float, getValue, setValue)

    def getSliderPosition(self):
        return super().sliderPosition()/self._scale

    def setSliderPosition(self, value):
        super().setSliderPosition(round(value*self._scale))

    sliderPosition = Property(float, getSliderPosition, setSliderPosition)

    def keyPressEvent(self, event):
        singlestep = self.getSingleStep()
        pagestep = self.getPageStep()
        ctrl_hold = self.app.queryKeyboardModifiers() == Qt.ControlModifier
        if ctrl_hold and (event.key() == Qt.Key_Right):
            self.setSingleStep(10*singlestep)
            self.setPageStep(10*pagestep)
            self._show_step_tooltip()
        elif ctrl_hold and (event.key() == Qt.Key_Left):
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
        super().setRange(round(mini/self._scale), round(maxi*self._scale))

    @Slot(int, int)
    def _intercept_rangeChanged(self, mini, maxi):
        self.rangeChanged.emit(mini/self._scale, maxi/self._scale)

    @Slot(int)
    def _intercept_sliderMoved(self, value):
        self.sliderMoved.emit(value/self._scale)

    @Slot(int)
    def _intercept_valueChanged(self, value):
        self.valueChanged.emit(value/self._scale)
