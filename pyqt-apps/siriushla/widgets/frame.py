"""Sirius Frame."""

from qtpy.QtCore import Property
from qtpy.QtWidgets import QHBoxLayout
from pydm.widgets.frame import PyDMFrame


class SiriusFrame(PyDMFrame):
    """Sirius Frame."""

    LightGreen = (0, 255, 0)
    DarkGreen = (20, 80, 10)
    Yellow = (255, 255, 77)
    Red = (255, 0, 0)
    LightBlue = (179, 229, 255)
    LightViolet = (204, 179, 255)
    LightSalmon = (255, 179, 179)
    Gray = (90, 90, 90)
    default_colorlist = [LightGreen, Red]

    def __init__(self, parent=None, init_channel=None, use_border=True,
                 color_list=None, is_float=True):
        """Init."""
        super().__init__(parent, init_channel)
        self._border_color = SiriusFrame.Gray
        self._border_width = 4
        self.value = 0
        self._is_float = is_float
        self.stateColors = color_list or self.default_colorlist

        lay = QHBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)
        self.setObjectName('frame')

    @Property(bool)
    def borderWidth(self):
        """
        Border width in pixels.

        Returns
        -------
        use : bool
            The width in use
        """
        return self._border_width

    @borderWidth.setter
    def borderWidth(self, new_val):
        """
        Border width in pixels.

        Parameters
        ----------
        new_val : bool
            The new width to use
        """
        if self._border_width != new_val:
            self._border_width = new_val
            self.layout().setContentsMargins(
                new_val, new_val, new_val, new_val)

    @Property(tuple)
    def offColor(self):
        """
        Border off color.

        Returns
        -------
        color : string
            The color in use
        """
        return self._stateColors[0]

    @offColor.setter
    def offColor(self, new_val):
        """
        Border off color.

        Parameters
        ----------
        new_val : string
            The new color to use
        """
        if self._stateColors[0] != new_val:
            self._stateColors[0] = new_val
            self._set_border()

    @Property(tuple)
    def onColor(self):
        """
        Border on color.

        Returns
        -------
        color : string
            The color in use
        """
        return self._stateColors[1]

    @onColor.setter
    def onColor(self, new_val):
        """
        Border on color.

        Parameters
        ----------
        new_val : string
            The new color to use
        """
        if self._stateColors[1] != new_val:
            self._stateColors[1] = new_val
            self._set_border()

    @Property(list)
    def stateColors(self):
        """Color list property getter."""
        return list(self._stateColors)

    @stateColors.setter
    def stateColors(self, new_colors):
        """Color list property setter."""
        if not isinstance(new_colors, (list, tuple)) or len(new_colors) < 2:
            return
        self._stateColors = list(new_colors)

    def _set_border(self):
        if not self._is_float:
            ind = self.value % len(self._stateColors)
            self._border_color = self._stateColors[ind]
        else:
            self._border_color = self._stateColors[1] if self.value else\
                self._stateColors[0]

        stylesheet = '#frame{background-color: rgb'
        stylesheet += str(self._border_color)
        stylesheet += '; border-radius: 0px;}'

        self.setStyleSheet(stylesheet)

    def value_changed(self, new_value):
        super().value_changed(new_value)
        if self.value is not None:
            self._set_border()

    def add_widget(self, widget):
        self.layout().addWidget(widget)
