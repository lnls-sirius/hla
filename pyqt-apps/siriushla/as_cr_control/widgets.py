import typing
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPolygon, QColor, \
    QBrush, QFont
from PyQt5.QtCore import Qt, QPoint

class PolygonWidget(QWidget):
    def __init__(self, text, color, parent):
        super().__init__()
        self.text = text
        self.color = color
        self.par = parent
        self.hei = 2
        self.wid = 6.75
        self.full_width = parent.width() * self.wid / 100
        self.full_height = parent.height() * self.hei / 100

    def resizeEvent(self, a0):
        self.full_width = self.par.width() * self.wid / 100
        self.full_height = self.par.height() * self.hei / 100
        return super().resizeEvent(a0)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        polygon = QPolygon([
            QPoint(self.full_width/10,0),
            QPoint(0,self.full_height/2),
            QPoint(self.full_width/10,self.full_height),
            QPoint(self.full_width-self.full_width/10,self.full_height),
            QPoint(self.full_width,self.full_height/2),
            QPoint(self.full_width-self.full_width/10,0)
        ])
        fill_color = QColor(self.color)
        painter.setBrush(QBrush(fill_color))
        painter.drawPolygon(polygon)

        text_font = QFont("Arial", 9)
        painter.setFont(text_font)
        text_color = QColor(255, 255, 255)
        painter.setPen(QColor(text_color))

        center_x = sum(p.x() for p in polygon) / polygon.size()
        center_y = sum(p.y() for p in polygon) / polygon.size()

        text_rect = painter.boundingRect(
            0, 0, self.full_width, self.full_height,
            Qt.AlignCenter, self.text)
        text_x = center_x - text_rect.width() / 2
        text_y = center_y - text_rect.height() / 2

        painter.drawText(
            text_x, text_y, text_rect.width(), text_rect.height(),
            Qt.AlignCenter, self.text)

        super().paintEvent(event)

class RotatedQLabel(QWidget):
    def __init__(self, text, rotation) -> None:
        super().__init__()
        self.text = text
        self.rotation = rotation

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(Qt.black)
        painter.translate(self.width()/2, self.height()/2)
        painter.rotate(self.rotation)
        painter.drawText(0, 0, self.text)
        painter.end()
