"""Sirius Frame."""

from qtpy.QtCore import Property
from qtpy.QtWidgets import QHBoxLayout
from pydm.widgets.frame import PyDMFrame


class SiriusFrame(PyDMFrame):
    """Sirius Frame."""

    LightGreen = (0, 255, 0)
    DarkGreen = (20, 80, 10)
    Red = (255, 0, 0)
    Gray = (90, 90, 90)

    def __init__(self, parent=None, init_channel=None, use_border=True,
                 off_color='', on_color=''):
        """Init."""
        super().__init__(parent, init_channel)

        self._border_off_color = \
            SiriusFrame.LightGreen if not off_color else off_color
        self._border_on_color = SiriusFrame.Red if not on_color else on_color
        self._border_width = 4
        self._border_color = SiriusFrame.Gray

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

    @Property(str)
    def offColor(self):
        """
        Border off color.

        Returns
        -------
        color : string
            The color in use
        """
        return self._border_off_color

    @offColor.setter
    def offColor(self, new_val):
        """
        Border off color.

        Parameters
        ----------
        new_val : string
            The new color to use
        """
        if self._border_off_color != new_val:
            self._border_off_color = new_val
            self._set_border()

    @Property(str)
    def onColor(self):
        """
        Border on color.

        Returns
        -------
        color : string
            The color in use
        """
        return self._border_on_color

    @onColor.setter
    def onColor(self, new_val):
        """
        Border on color.

        Parameters
        ----------
        new_val : string
            The new color to use
        """
        if self._border_on_color != new_val:
            self._border_on_color = new_val
            self._set_border()

    def _set_border(self):
        self._border_color = self._border_on_color \
            if self.value else self._border_off_color

        stylesheet = '#frame{background-color: rgb'
        stylesheet += str(self._border_color)
        stylesheet += '; border-radius: 0px;}'

        self.setStyleSheet(stylesheet)

    def value_changed(self, new_value):
        super().value_changed(new_value)
        self._set_border()

    def add_widget(self, widget):
        self.layout().addWidget(widget)
