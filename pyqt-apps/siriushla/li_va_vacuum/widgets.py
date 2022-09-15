from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGroupBox
from qtpy.QtGui import QPainter, QBrush, QPen, QColor

class LedLegend(QWidget):
    """."""

    def drawSingleLed(self, painter, color, x, width):
        size = [self.width()-1, self.height()-1]
        painter.setBrush(
            QBrush(color, Qt.SolidPattern))
        painter.drawRect(size[0]*x/100, 0, size[0]*width/100, size[1])
        return painter

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        self.drawSingleLed(painter, QColor(self.color), 0, 100)
        painter.end()

    def __init__(self, parent=None, color='#FFFFFF'):
        """."""
        super().__init__(parent=parent)

        size = [12, 12]
        self.color = color
        self.setMinimumWidth(size[0])
        self.setMaximumWidth(size[0]+10)
        self.setMinimumHeight(size[1])
        self.setMaximumHeight(size[1]+10)

class QGroupBoxButton(QGroupBox):
    """."""

    def __init__(self, parent=None, title=""):
        """."""
        super().__init__(parent=parent)
        self.setTitle(title)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        child = self.childAt(event.pos())
        if not child:
            child = self
        self.clicked.emit()