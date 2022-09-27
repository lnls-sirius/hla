from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGroupBox
from qtpy.QtGui import QPainter, QBrush, QPen, QColor
from pydm.widgets import PyDMPushButton

class LedLegend(QWidget):
    """."""

    def getShape(self, painter, pos, size):
        if self.shape == 1:
            painter.drawEllipse(
                pos[0], pos[1], size[0], size[1])
        elif self.shape == 2:
            painter.drawRoundedRect(
                pos[0], pos[1], size[0], size[1], 3, 15)
        elif self.shape == 3:
            painter.drawRect(
                pos[0], pos[1], size[0], size[1])
        return painter

    def drawSingleLed(self, painter, color, x, width):
        own_size = [self.width()-1, self.height()-1] 
        pos = [own_size[0]*x/100, 0]
        size = [own_size[0]*width/100, own_size[1]]
        painter.setBrush(
            QBrush(color, Qt.SolidPattern))
        painter = self.getShape(painter, pos, size)
        return painter

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        self.drawSingleLed(painter, QColor(self.color), 0, 100)
        painter.end()

    def __init__(self, parent=None, shape=1, color='#FFFFFF'):
        """."""
        super().__init__(parent=parent)

        if shape != 2:  
            size = [12, 12]
        else:
            size = [25, 10]
        self.color = color
        self.shape = shape
        self.setMinimumWidth(size[0])
        self.setMaximumWidth(size[0]+10)
        self.setMinimumHeight(size[1])
        self.setMaximumHeight(size[1]+10)

class QGroupBoxButton(QGroupBox):
    """."""

    def mousePressEvent(self, event):
        child = self.childAt(event.pos())
        if not child:
            child = self
        self.clicked.emit()

    def __init__(self, parent=None, title=""):
        """."""
        super().__init__(parent=parent)
        self.setTitle(title)
        self.setMouseTracking(True)

class OnOffBtn(PyDMPushButton):

    def __init__(self, parent=None, init_channel=None, label=''):
        super().__init__(parent, init_channel=init_channel, label=label, pressValue=0)

    def value_changed(self, new_value):
        """Redefine value_changed."""
        if new_value == 1:
            self.setChecked(True)
            self.pressValue = 0
        else:
            self.setChecked(False)
            self.pressValue = 1

        return super().value_changed(new_value)
