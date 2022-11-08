""" Contains the special widgets used in the windows """
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGroupBox
from qtpy.QtGui import QPainter, QBrush, QPen, QColor
from ..widgets import PyDMLedMultiChannel


class LedLegend(QWidget):
    """ Drawing of a Led for the Legend """

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

    def getShape(self, painter, pos, size):
        """ Draw different shapes of led """
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

    def drawSingleLed(self, painter, color, pos_x, width):
        """ Draw a single Led"""
        own_size = [self.width()-1, self.height()-1]
        pos = [own_size[0]*pos_x/100, 0]
        size = [own_size[0]*width/100, own_size[1]]
        painter.setBrush(
            QBrush(color, Qt.SolidPattern))
        painter = self.getShape(painter, pos, size)
        return painter

    def paintEvent(self, event):
        """ Called to paint led on the window """
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        self.drawSingleLed(painter, QColor(self.color), 0, 100)
        painter.end()


class PyDMLedMultiIncosistencyDetector(PyDMLedMultiChannel):
    """ Drawing of a Led for the Legend """

    LightGreen = QColor(0, 140, 0)
    Yellow = QColor(210, 205, 0)
    Red = QColor(207, 0, 0)

    def __init__(
        self, parent=None, channels2values=dict(),
        color_list=[Red, LightGreen, Yellow]):
            """."""
            super().__init__(
                parent=parent,
                channels2values=channels2values,
                color_list=color_list)

    def _update_statuses(self):
        first_pv = list(self._address2status.keys())[0]
        final_state = self._address2status[first_pv]
        if not self._connected:
            final_state = 2
        else:
            for status in self._address2status.values():
                if status != final_state:
                    final_state = 2
                    break
        self.setState(final_state)


class QGroupBoxButton(QGroupBox):
    """ A clickable GroupBox """

    def __init__(self, parent=None, title=""):
        """."""
        super().__init__(parent=parent)
        self.setTitle(title)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        """ Emit a clicked function in the GroupBox """
        child = self.childAt(event.pos())
        if not child:
            child = self
        self.clicked.emit()
