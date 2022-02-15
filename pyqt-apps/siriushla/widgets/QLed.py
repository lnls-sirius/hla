"""QLed module.

Based on Robert Kent's LED Widget for the PyQt Framework, available on
https://pypi.python.org/pypi/QLed or https://github.com/jazzycamel/QLed.
"""

import os as _os
from colorsys import rgb_to_hls, hls_to_rgb
from qtpy.QtWidgets import QApplication, QWidget, QGridLayout, \
                            QStyleOption, QFrame
from qtpy.QtGui import QPainter, QColor
from qtpy.QtCore import Signal, Qt, QSize, QTimer, QByteArray, \
                        QRectF, Property, Q_ENUMS, QFile
from qtpy.QtSvg import QSvgRenderer


class ShapeMap:
    """Shape enum mapping class."""

    Circle = 1
    Round = 2
    Square = 3
    Triangle = 4


class QLed(QFrame, ShapeMap):
    """QLed class."""

    ShapeMap = ShapeMap
    Q_ENUMS(ShapeMap)

    abspath = _os.path.abspath(_os.path.dirname(__file__))
    shapesdict = dict()
    f = QFile(_os.path.join(abspath, 'resources/led_shapes/circle.svg'))
    if f.open(QFile.ReadOnly):
        shapesdict[ShapeMap.Circle] = str(f.readAll(), 'utf-8')
    f.close()
    f = QFile(_os.path.join(abspath, 'resources/led_shapes/round.svg'))
    if f.open(QFile.ReadOnly):
        shapesdict[ShapeMap.Round] = str(f.readAll(), 'utf-8')
    f.close()
    f = QFile(_os.path.join(abspath, 'resources/led_shapes/square.svg'))
    if f.open(QFile.ReadOnly):
        shapesdict[ShapeMap.Square] = str(f.readAll(), 'utf-8')
    f.close()
    f = QFile(_os.path.join(abspath, 'resources/led_shapes/triangle.svg'))
    if f.open(QFile.ReadOnly):
        shapesdict[ShapeMap.Triangle] = str(f.readAll(), 'utf-8')
    f.close()

    Green = QColor(15, 105, 0)
    Red = QColor(207, 0, 0)
    Gray = QColor(90, 90, 90)
    SelColor = QColor(0, 0, 0)
    NotSelColor1 = QColor(251, 244, 252)
    NotSelColor2 = QColor(173, 173, 173)

    clicked = Signal()
    selected = Signal(bool)

    def __init__(self, parent=None, **kwargs):
        """Class constructor."""
        super().__init__(parent, **kwargs)
        self.m_state = 0
        self.m_stateColors = [self.Red, self.Green]

        self.m_dsblColor = self.Gray
        self.m_shape = self.ShapeMap.Circle

        self._pressed = False
        self._isselected = False
        self.renderer = QSvgRenderer()

    def getState(self):
        """Value property getter."""
        return self.m_state

    def setState(self, value):
        """Value property setter."""
        self.m_state = value
        self.update()

    state = Property(bool, getState, setState)

    def getOnColor(self):
        """On color property getter."""
        return self.m_stateColors[1]

    def setOnColor(self, newColor):
        """On color property setter."""
        self.m_stateColors[1] = newColor
        self.update()

    onColor = Property(QColor, getOnColor, setOnColor)

    def getOffColor(self):
        """Off color property getter."""
        return self.m_stateColors[0]

    def setOffColor(self, newColor):
        """Off color property setter."""
        self.m_stateColors[0] = newColor
        self.update()

    offColor = Property(QColor, getOffColor, setOffColor)

    @property
    def stateColors(self):
        """Color list property getter."""
        return list(self.m_stateColors)

    @stateColors.setter
    def stateColors(self, new_colors):
        """Color list property setter."""
        if not isinstance(new_colors, (list, tuple)) or\
                len(new_colors) < 2 or not isinstance(new_colors[0], QColor):
            return
        self.m_stateColors = list(new_colors)

    def getDsblColor(self):
        """Disabled color property getter."""
        return self.m_dsblColor

    def setDsblColor(self, newColor):
        """Disabled color property setter."""
        self.m_dsblColor = newColor
        self.update()

    dsblColor = Property(QColor, getDsblColor, setDsblColor)

    def getShape(self):
        """Shape property getter."""
        return self.m_shape

    def setShape(self, newShape):
        """Shape property setter."""
        self.m_shape = newShape
        self.update()

    shape = Property(ShapeMap, getShape, setShape)

    def sizeHint(self):
        """Return the base size of the widget according to shape."""
        if self.m_shape == self.ShapeMap.Triangle:
            return QSize(48, 36)
        elif self.m_shape == self.ShapeMap.Round:
            return QSize(72, 36)
        return QSize(36, 36)

    def adjust(self, r, g, b):
        """Adjust the color to set on svg code."""
        def normalise(x):
            return x/255.0

        def denormalise(x):
            if x <= 1:
                return int(x*255.0)
            else:
                return 255.0

        (h, l, s) = rgb_to_hls(normalise(r), normalise(g), normalise(b))
        (nr, ng, nb) = hls_to_rgb(h, l*1.5, s)

        return (denormalise(nr), denormalise(ng), denormalise(nb))

    def getRGBfromQColor(self, qcolor):
        """Convert QColors to a tupple of rgb colors to set on svg code."""
        redhex = qcolor.red()
        greenhex = qcolor.green()
        bluehex = qcolor.blue()
        return (redhex, greenhex, bluehex)

    def paintEvent(self, event):
        """Handle appearence of the widget on state updates."""
        self.style().unpolish(self)
        self.style().polish(self)
        option = QStyleOption()
        option.initFrom(self)

        h = option.rect.height()
        w = option.rect.width()
        if self.m_shape in (self.ShapeMap.Triangle, self.ShapeMap.Round):
            aspect = (4/3.0) if self.m_shape == self.ShapeMap.Triangle else 2.0
            ah = w/aspect
            aw = w
            if ah > h:
                ah = h
                aw = h*aspect
            x = abs(aw-w)/2.0
            y = abs(ah-h)/2.0
            bounds = QRectF(x, y, aw, ah)
        else:
            size = min(w, h)
            x = abs(size-w)/2.0
            y = abs(size-h)/2.0
            bounds = QRectF(x, y, size, size)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        ind = self.m_state % len(self.m_stateColors)
        dark_r, dark_g, dark_b = self.getRGBfromQColor(self.m_stateColors[ind])
        if not self.isEnabled():
            dark_r, dark_g, dark_b = self.getRGBfromQColor(self.m_dsblColor)

        sel1_r, sel1_g, sel1_b = self.getRGBfromQColor(self.SelColor)
        sel2_r, sel2_g, sel2_b = self.getRGBfromQColor(self.SelColor)
        opc = '1.000'
        if not self.isSelected():
            sel1_r, sel1_g, sel1_b = self.getRGBfromQColor(self.NotSelColor1)
            sel2_r, sel2_g, sel2_b = self.getRGBfromQColor(self.NotSelColor2)
            opc = '0.145'

        dark_str = "rgb(%d,%d,%d)" % (dark_r, dark_g, dark_b)
        light_str = "rgb(%d,%d,%d)" % self.adjust(dark_r, dark_g, dark_b)
        sel1_str = "rgb(%d,%d,%d)" % (sel1_r, sel1_g, sel1_b)
        sel2_str = "rgb(%d,%d,%d)" % (sel2_r, sel2_g, sel2_b)

        shape_bytes = bytes(self.shapesdict[self.m_shape] % (
            sel1_str, opc, sel2_str, dark_str, light_str), 'utf-8')

        self.renderer.load(QByteArray(shape_bytes))
        self.renderer.render(painter, bounds)

    def mousePressEvent(self, event):
        """Handle mouse press event."""
        self._pressed = True
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release event."""
        if self._pressed:
            self._pressed = False
            self.clicked.emit()
        super().mouseReleaseEvent(event)

    def toggleValue(self):
        """Toggle value property."""
        self.m_state = 0 if self.m_state else 1
        self.update()

    def isSelected(self):
        """Return selected state of object."""
        return self._isselected

    def setSelected(self, sel):
        """Configure selected state of object."""
        self._isselected = bool(sel)
        self.selected.emit(self._isselected)
        self.update()


if __name__ == "__main__":
    from sys import argv, exit

    class Test(QWidget):
        """Test class."""

        def __init__(self, parent=None):
            """Test class constructor."""
            QWidget.__init__(self, parent)

            self.setWindowTitle("QLed Test")

            _l = QGridLayout()
            self.setLayout(_l)

            colorsdict = {'Red': QColor(207, 0, 0),
                          'Green': QColor(15, 105, 0),
                          'Yellow': QColor(210, 205, 0),
                          'Orange': QColor(218, 70, 21),
                          'Purple': QColor(135, 0, 131),
                          'Blue': QColor(0, 3, 154)}

            self.leds = []
            for row, shape in enumerate(QLed.shapesdict.keys()):
                for col, color in enumerate(colorsdict.keys()):
                    led = QLed(self)
                    led.setOnColor(colorsdict[color])
                    led.setOffColor(QColor(90, 90, 90))
                    led.setShape(shape)
                    _l.addWidget(led, row, col, Qt.AlignCenter)
                    self.leds.append(led)

            self.toggleLeds()

        def toggleLeds(self):
            """Toggle leds state."""
            for led in self.leds:
                led.toggleValue()
            QTimer.singleShot(1000, self.toggleLeds)

    a = QApplication(argv)
    t = Test()
    t.show()
    t.raise_()
    exit(a.exec_())
