
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QHBoxLayout
from qtpy.QtGui import QPainter, QBrush, QPen, QColor
from ..widgets import PyDMLedMultiChannel

class SquareLed(QWidget):
    """."""

    def drawSingleLed(self, painter, color, x, width):
        size = [self.width()-1, self.height()-1]
        painter.setBrush(
            QBrush(color, Qt.SolidPattern))
        painter.drawRect(size[0]*x/100, 0, size[0]*width/100, size[1])
        return painter

    def drawDoubleLed(self, painter):
        color_pri = QColor(self.color[0])
        color_sec = QColor(self.color[1])
        self.drawSingleLed(painter, color_pri, 0, 50)
        self.drawSingleLed(painter, color_sec, 50, 50)
        return painter

    def drawStaticLed(self):
        painter = QPainter(self)

        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))

        if self.isList:
            self.drawDoubleLed(painter)
        else:
            color_pri = QColor(self.color)
            self.drawSingleLed(painter, color_pri, 0, 100)

        painter.end()

    def setPyDMLed(self):
        # widget = PyDMLedMultiConnection
        return widget

    def paintEvent(self, event):
        if not self.isPyDM:
            self.drawStaticLed()

    def __init__(self, parent=None, color='#FFFFFF', isPyDM=True):
        """."""
        super().__init__(parent=parent)

        self.isList = isinstance(color, list)
        self.isPyDM = isPyDM
        self.color = color
        min_width=10
        min_height=10
        if self.isList:
            min_width=20

        if self.isPyDM:
            self.setWidget(self.setPyDMLed())

        self.setMinimumWidth(min_width)
        self.setMaximumWidth(min_width+10)
        self.setMinimumHeight(min_height)
        self.setMaximumHeight(min_width+10)
