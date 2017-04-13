
from . import color_conversion as _color_conversion


class CustomLine(object):

    """
    Keep a matplotlib line and allow access to data and options.

    Properties:
    x: array
    y: array
    color: RGBA tuple [0,255] or 'red', 'green', 'blue' ...
    marker_fill: 'full', 'none'
    line_style: '-', '--', '-.', ':', 'None'
    line_width: value in points
    marker: '.', 'o', '^', 's', 'x', 'None'
    marker_face_color: RGBA tuple [0,255] or 'red', 'green', 'blue' ...
    marker_size: value in points
    """

    def __init__(self, line):
        """line -- a matplotlib Line2D"""
        self.line = line

    @property
    def x(self):
        return self._get_x()

    @x.setter
    def x(self, array):
        self._set_x(array)

    @property
    def y(self):
        return self._get_y()

    @y.setter
    def y(self, array):
        self._set_y(array)

    @property
    def color(self):
        color = self.line.get_color()
        return _color_conversion.denormalize_color(color)

    @color.setter
    def color(self, color):
        new_color = _color_conversion.normalize_color(color)
        self.line.set_color(new_color)

    @property
    def line_style(self):
        return self.line.get_linestyle()

    @line_style.setter
    def line_style(self, style):
        self.line.set_linestyle(style)

    @property
    def line_width(self):
        return self.line.get_linewidth()

    @line_width.setter
    def line_width(self, style):
        self.line.set_linewidth(style)

    @property
    def marker(self):
        return self.line.get_marker()

    @marker.setter
    def marker(self, marker):
        self.line.set_marker(marker)

    @property
    def marker_fill(self):
        return self.line.get_fillstyle()

    @marker_fill.setter
    def marker_fill(self, style):
        self.line.set_fillstyle(style)

    @property
    def marker_edge_color(self):
        color = self.line.get_markeredgecolor()
        return _color_conversion.denormalize_color(color)

    @marker_edge_color.setter
    def marker_edge_color(self, color):
        new_color = _color_conversion.normalize_color(color)
        self.line.set_markeredgecolor(new_color)

    @property
    def marker_face_color(self):
        color = self.line.get_markerfacecolor()
        return _color_conversion.denormalize_color(color)

    @marker_face_color.setter
    def marker_face_color(self, color):
        new_color = _color_conversion.normalize_color(color)
        self.line.set_markerfacecolor(new_color)

    @property
    def marker_size(self):
        return self.line.get_markersize()

    @marker_size.setter
    def marker_size(self, size):
        self.line.set_markersize(size)

    def _get_x(self):
        return self.line.get_xdata()

    def _set_x(self, array):
        self.line.set_xdata(array)

    def _get_y(self):
        return self.line.get_ydata()

    def _set_y(self, array):
        self.line.set_ydata(array)
