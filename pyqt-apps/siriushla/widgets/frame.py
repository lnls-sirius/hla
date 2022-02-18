"""Sirius Frame."""

from qtpy.QtCore import Property
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QHBoxLayout
from pydm.widgets.frame import PyDMFrame


class _BaseFrame(PyDMFrame):
    """Sirius Base Frame."""

    LightGreen = QColor(0, 255, 0)
    MediumGreen = QColor(25, 156, 109)
    DarkGreen = QColor(20, 80, 10)
    Yellow = QColor(255, 254, 122)
    DarkYellow = QColor(255, 255, 0)
    Red = QColor(255, 0, 0)
    MediumBlue = QColor(15, 102, 255)
    LightBlue = QColor(142, 183, 255)
    LightViolet = QColor(204, 179, 255)
    LightSalmon = QColor(255, 179, 179)
    Salmon = QColor(255, 105, 97)
    Lavender = QColor(151, 122, 196)
    DarkCyan = QColor(95, 131, 184)
    LightGray = QColor(229, 228, 226)
    Gray = QColor(90, 90, 90)
    DarkGray = QColor(132, 136, 132)
    Magenta = QColor('magenta')

    def __init__(self, parent=None, init_channel=None,
                 color_list=None, is_float=True):
        """Init."""
        super().__init__(parent, init_channel)
        self._border_color = _BaseFrame.LightGray
        self._border_width = 4
        self._is_float = is_float
        self.stateColors = color_list

        lay = QHBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)
        self.setObjectName('frame')

    @Property(int)
    def borderWidth(self):
        """
        Border width in pixels.

        Returns
        -------
        use : int
            The width in use
        """
        return self._border_width

    @borderWidth.setter
    def borderWidth(self, new_val):
        """
        Border width in pixels.

        Parameters
        ----------
        new_val : int
            The new width to use
        """
        if self._border_width != new_val:
            self._border_width = new_val
            self.layout().setContentsMargins(
                new_val, new_val, new_val, new_val)

    @Property(QColor)
    def offColor(self):
        """
        Border off color.

        Returns
        -------
        color : QColor
            The color in use
        """
        return self._stateColors[0]

    @offColor.setter
    def offColor(self, new_val):
        """
        Border off color.

        Parameters
        ----------
        new_val : QColor
            The new color to use
        """
        if self._stateColors[0] != new_val:
            self._stateColors[0] = new_val
            self._update_border_color()

    @Property(QColor)
    def onColor(self):
        """
        Border on color.

        Returns
        -------
        color : QColor
            The color in use
        """
        return self._stateColors[1]

    @onColor.setter
    def onColor(self, new_val):
        """
        Border on color.

        Parameters
        ----------
        new_val : QColor
            The new color to use
        """
        if self._stateColors[1] != new_val:
            self._stateColors[1] = new_val
            self._update_border_color()

    @Property(list)
    def stateColors(self):
        """
        State color list property.

        Returns
        -------
        use : list of QColors
            State colors in use
        """
        return list(self._stateColors)

    @stateColors.setter
    def stateColors(self, new_colors):
        """
        State color list property.

        Parameters
        ----------
        new_colors : list of QColors
            The new state colors to use
        """
        if not isinstance(new_colors, (list, tuple)) or len(new_colors) < 2:
            return
        self._stateColors = list(new_colors)
        self._update_border_color()

    def _update_border_color(self):
        """Must be defined in derived object, must call _update_style_sheet."""
        raise NotImplementedError

    def _update_style_sheet(self):
        stylesheet = '#frame{background-color: '
        stylesheet += self._border_color.name()
        stylesheet += '; border-radius: 0px;}'

        self.setStyleSheet(stylesheet)

    def add_widget(self, widget):
        self.layout().addWidget(widget)


class SiriusFrame(_BaseFrame):
    """Sirius Frame."""

    default_colorlist = [_BaseFrame.LightGreen, _BaseFrame.Red]

    def __init__(self, parent=None, init_channel=None,
                 color_list=None, is_float=True):
        """Init."""
        color_list = color_list or SiriusFrame.default_colorlist
        super().__init__(
            parent=parent, init_channel=init_channel,
            color_list=color_list, is_float=is_float)

    def _update_border_color(self):
        if self.value is None or not hasattr(self, '_is_float') or \
                not hasattr(self, '_stateColors'):
            return
        if not self._is_float:
            ind = self.value % len(self._stateColors)
            self._border_color = self._stateColors[ind]
        else:
            self._border_color = self._stateColors[1] if self.value else \
                self._stateColors[0]

        self._update_style_sheet()

    def value_changed(self, new_value):
        super().value_changed(new_value)
        self._update_border_color()


class SiriusAlarmFrame(_BaseFrame):
    """Sirius Alarm Frame."""

    default_colorlist = [
        _BaseFrame.LightGreen, _BaseFrame.DarkYellow, _BaseFrame.Red,
        _BaseFrame.Magenta, _BaseFrame.LightGray]

    def __init__(self, parent=None, init_channel=None):
        """Init."""
        super().__init__(
            parent=parent, init_channel=init_channel,
            color_list=SiriusAlarmFrame.default_colorlist,
            is_float=False)

    def _update_border_color(self):
        if not hasattr(self, '_stateColors'):
            return
        idx = 0 if self._alarm_state == _BaseFrame.ALARM_NONE else \
            1 if self._alarm_state == _BaseFrame.ALARM_MINOR else \
            2 if self._alarm_state == _BaseFrame.ALARM_MAJOR else \
            3 if self._alarm_state == _BaseFrame.ALARM_INVALID else 4
        self._border_color = self._stateColors[idx]

        self._update_style_sheet()

    def alarm_severity_changed(self, new_value):
        super().alarm_severity_changed(new_value)
        self._update_border_color()
