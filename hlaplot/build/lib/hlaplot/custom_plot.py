"""
CustomPlot
    Class for embedding matplotlib plots in Qt GUI.

Afonso Haruo Carnielli Mukai (FAC - LNLS)

2013-11-21: v0.1
"""

import sys as _sys
import matplotlib.backends.backend_qt5agg as _backend_qt5agg
import matplotlib.figure as _figure
from . import color_conversion as _color_conversion
from . import custom_line as _custom_line


DEFAULT_BACKGROUND_COLOR = _color_conversion.DEFAULT_BACKGROUND_COLOR
DEFAULT_AXIS_BACKGROUND_COLOR = _color_conversion.DEFAULT_AXIS_BACKGROUND_COLOR
DEFAULT_AXIS_ELEMENTS_COLOR = _color_conversion.DEFAULT_AXIS_ELEMENTS_COLOR


class LineNameException(Exception):
    pass


class AxisNameError(Exception):
    pass


class _XY:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class _MinMax:
    def __init__(self, minimum=0, maximum=0):
        self.min = minimum
        self.max = maximum


class CustomPlot(_backend_qt5agg.FigureCanvasQTAgg):

    """Embed a plot in PyQt."""

    def __init__(self,
                 background_color=DEFAULT_BACKGROUND_COLOR,
                 axis_background_color=DEFAULT_AXIS_BACKGROUND_COLOR,
                 axis_elements_color=DEFAULT_AXIS_ELEMENTS_COLOR,
                 autoscale=True,
                 axes_extra_spacing=0.0):

        if _sys.version_info.major == 2:
            self._return_unicode_string = self._return_unicode_string_python2
        else:
            self._return_unicode_string = self._return_unicode_string_python3

        self._autoscale = _XY()
        self._axes_extra_spacing = _XY(_MinMax(), _MinMax())

        self._lines = {}
        self._figure = _figure.Figure()
        super(CustomPlot, self).__init__(self._figure)

        self.set_spacing()

        self.background_color = background_color

        # (line, column, subplot)
        self._axes = self._figure.add_subplot(1, 1, 1)
        self.axis_background_color = axis_background_color
        self.axis_elements_color = axis_elements_color
        self._axes.autoscale(enable=False)

        self.xy_autoscale = autoscale

        self.x_axis_extra_spacing = axes_extra_spacing
        self.y_axis_extra_spacing = axes_extra_spacing

        self.y_ticks_side = 'left'

        self._x_grid_on = False
        self._y_grid_on = False

    @property
    def background_color(self):
        normalized_color = self.figure.get_facecolor()
        return _color_conversion.denormalize_color(normalized_color)

    @background_color.setter
    def background_color(self, color):
        normalized_color = _color_conversion.normalize_color(color)
        self.figure.set_facecolor(normalized_color)

    @property
    def axis_background_color(self):
        normalized_color = self._axes.get_axis_bgcolor()
        return _color_conversion.denormalize_color(normalized_color)

    @axis_background_color.setter
    def axis_background_color(self, color):
        normalized_color = _color_conversion.normalize_color(color)
        self._axes.set_axis_bgcolor(normalized_color)

    @property
    def axis_elements_color(self):
        normalized_color = self._axis_elements_color
        return _color_conversion.denormalize_color(normalized_color)

    @axis_elements_color.setter
    def axis_elements_color(self, color):
        normalized_color = _color_conversion.normalize_color(color)

        for pos in ['top', 'bottom', 'left', 'right']:
            self._axes.spines[pos].set_color(normalized_color)
        self._axes.tick_params(axis='x', colors=normalized_color)
        self._axes.tick_params(axis='y', colors=normalized_color)
        self._axes.xaxis.label.set_color(normalized_color)
        self._axes.yaxis.label.set_color(normalized_color)
        self._axes.title.set_color(normalized_color)
        self._axis_elements_color = normalized_color

    @property
    def title(self):
        return self._axes.get_title()

    @title.setter
    def title(self, title):
        new_title = self._return_unicode_string(title)
        self._axes.set_title(new_title)

    @property
    def x_label(self):
        return self._axes.get_xlabel()

    @x_label.setter
    def x_label(self, label):
        new_label = self._return_unicode_string(label)
        self._axes.set_xlabel(new_label)

    @property
    def y_label(self):
        return self._axes.get_ylabel()

    @y_label.setter
    def y_label(self, label):
        new_label = self._return_unicode_string(label)
        self._axes.set_ylabel(new_label)

    @property
    def x_axis(self):
        return self._axes.get_xbound()

    @x_axis.setter
    def x_axis(self, bounds):
        self._axes.set_xbound(*bounds)

    @property
    def y_axis(self):
        return self._axes.get_ybound()

    @y_axis.setter
    def y_axis(self, bounds):
        self._axes.set_ybound(*bounds)

    @property
    def x_autoscale(self):
        return self._autoscale.x

    @x_autoscale.setter
    def x_autoscale(self, value):
        self._autoscale.x = value

    @property
    def y_autoscale(self):
        return self._autoscale.y

    @y_autoscale.setter
    def y_autoscale(self, value):
        self._autoscale.y = value

    @property
    def xy_autoscale(self):
        autoscale = self._autoscale.x and self._autoscale.y
        return autoscale

    @xy_autoscale.setter
    def xy_autoscale(self, value):
        self._autoscale.x = value
        self._autoscale.y = value

    @property
    def x_axis_extra_spacing(self):
        return self._get_axis_extra_spacing('x')

    @x_axis_extra_spacing.setter
    def x_axis_extra_spacing(self, value):
        self._set_axis_extra_spacing('x', value)

    @property
    def y_axis_extra_spacing(self):
        return self._get_axis_extra_spacing('y')

    @y_axis_extra_spacing.setter
    def y_axis_extra_spacing(self, value):
        self._set_axis_extra_spacing('y', value)

    @property
    def x_scale(self):
        return self._axes.get_xscale()

    @x_scale.setter
    def x_scale(self, scale):
        """scale -- 'linear', 'log'"""
        self._axes.set_xscale(scale)

    @property
    def y_scale(self):
        return self._axes.get_yscale()

    @y_scale.setter
    def y_scale(self, scale):
        """scale -- 'linear', 'log'"""
        self._axes.set_yscale(scale)

    @property
    def y_ticks_side(self):
        return self._y_ticks_side

    @y_ticks_side.setter
    def y_ticks_side(self, side):
        if side == 'left':
            self._axes.yaxis.tick_left()
            self._y_ticks_side = side
        elif side == 'right':
            self._axes.yaxis.tick_right()
            self._y_ticks_side = side

    @property
    def x_tick_label_rotation(self):
        tick_labels = self._axes.get_xticklabels()
        return tick_labels[0].get_rotation()

    @x_tick_label_rotation.setter
    def x_tick_label_rotation(self, angle):
        tick_labels = self._axes.get_xticklabels()
        for label in tick_labels:
            label.set_rotation(angle)

    def show_x_grid(self, color='black', line_style='--', line_width=0.5):
        self._show_grid('x', color, line_style, line_width)

    def show_y_grid(self, color='black', line_style='--', line_width=0.5):
        self._show_grid('y', color, line_style, line_width)

    def hide_x_grid(self):
        if self._x_grid_on:
            self._hide_grid('x')

    def hide_y_grid(self):
        if self._y_grid_on:
            self._hide_grid('y')

    def add_line(self, name):
        """Add new line for presenting (x,y) data"""
        line, = self._axes.plot([])
        self._lines[name] = _custom_line.CustomLine(line)

    def remove_line(self, name):
        self._check_lines_has_key(name)
        self._axes.lines.remove(self._lines[name].line)
        self._lines.pop(name)

    def line(self, name):
        self._check_lines_has_key(name)
        return self._lines[name]

    def update_plot(self):
        if self.x_autoscale:
            self._scale_bounds('x')
        if self.y_autoscale:
            self._scale_bounds('y')
        self._figure.canvas.draw()

    def set_spacing(self, left=0.10, bottom=0.10, right=0.90, top=0.85):
        self._figure.subplots_adjust(left=left,
                                     bottom=bottom,
                                     right=right,
                                     top=top)

    def fill(self, name, color=None):
        self.remove_fill()
        self._check_lines_has_key(name)
        line = self._lines[name]
        x = self._get_line_data_from_axis(line, 'x')
        y = self._get_line_data_from_axis(line, 'y')
        if color is None:
            color = line.color
        else:
            color = _color_conversion.normalize_color(color)
        self._axes.fill_between(x, y, color=color)

    def remove_fill(self):
        for collection in (self._axes.collections):
            self._axes.collections.remove(collection)

    def _check_lines_has_key(self, key):
        if not key in self._lines:
            raise LineNameException

    def _select_axis_extra_spacing(self, axis):
        if axis  == 'x':
            return self._axes_extra_spacing.x
        elif axis  == 'y':
            return self._axes_extra_spacing.y
        else:
            raise AxisNameError

    def _get_axis_extra_spacing(self, axis):
        spacing = self._select_axis_extra_spacing(axis)
        v_min = spacing.min
        v_max = spacing.max
        return (v_min, v_max)

    def _set_axis_extra_spacing(self, axis, value):
        spacing = self._select_axis_extra_spacing(axis)
        if isinstance(value, tuple):
            spacing.min = value[0]
            spacing.max = value[1]
        else:
            spacing.min = value
            spacing.max = value

    def _scale_bounds(self, axis):
        bounds = self._find_axis_min_and_max(axis)
        new_bounds = self._calculate_new_bounds_for_axis(bounds, axis)
        if axis == 'x':
            self.x_axis = new_bounds
        elif axis == 'y':
            self.y_axis = new_bounds
        else:
            raise AxisNameError

    def _find_axis_min_and_max(self, axis):
        """
        Find min and max values for selected axis.
        Returns 0.0 and 1.0 if axis is empty.
        axis -- 'x' or 'y'
        """
        if axis != 'x' and axis != 'y':
            raise AxisNameError
        minimum, maximum = self._find_axis_lines_mins_and_maxs(axis)
        min_ = self._return_min_or_zero_if_empty(minimum)
        max_ = self._return_max_or_one_if_empty(maximum)
        (new_min, new_max) = self._return_unit_interval_if_equal(min_, max_)

        return (new_min, new_max)

    def _find_axis_lines_mins_and_maxs(self, axis):
        minimum = []
        maximum = []
        for name in self._lines:
            line = self._lines[name]
            data = self._get_line_data_from_axis(line, axis)
            if len(data) > 0:
                minimum.append(min(data))
                maximum.append(max(data))
        return minimum, maximum

    def _get_line_data_from_axis(self, line, axis):
        if axis == 'x':
            return line.x
        elif axis == 'y':
            return line.y
        else:
            raise AxisNameError

    def _calculate_new_bounds_for_axis(self, current_bounds, axis):
        delta = current_bounds[1] - current_bounds[0]
        extra_spacing = self._select_axis_extra_spacing(axis)
        new_min = current_bounds[0] - extra_spacing.min*delta
        new_max = current_bounds[1] + extra_spacing.max*delta
        return (new_min, new_max)

    def _return_min_or_zero_if_empty(self, values):
        if len(values) == 0:
            return 0.0
        else:
            return min(values)

    def _return_max_or_one_if_empty(self, values):
        if len(values) == 0:
            return 1.0
        else:
            return max(values)

    def _return_unit_interval_if_equal(self, minimum, maximum):
        if minimum == maximum:
            new_minimum = minimum - 0.5
            new_maximum = maximum + 0.5
        else:
            new_minimum = minimum
            new_maximum = maximum

        return (new_minimum, new_maximum)

    def _show_grid(self, axis, color='black', line_style='--', line_width=0.5):
        """
        axis -- 'x', 'y'
        """
        args = self._put_args_in_dict(color, line_style, line_width)
        if axis == 'x':
            self._axes.xaxis.grid(**args)
            self._x_grid_on = True
        elif axis == 'y':
            self._axes.yaxis.grid(**args)
            self._y_grid_on = True
        else:
            raise AxisNameError

    def _hide_grid(self, axis):
        """
        axis -- 'x', 'y'
        """
        if axis == 'x':
            self._axes.xaxis.grid()
            self._x_grid_on = False
        elif axis == 'y':
            self._axes.yaxis.grid()
            self._y_grid_on = False
        else:
            raise AxisNameError

    def _put_args_in_dict(self, color, line_style, line_width):
        args = {}
        args['color'] = color
        args['linestyle'] = line_style
        args['linewidth'] = line_width
        return args

    def _return_unicode_string_python2(self, string):
        return unicode(string, encoding='utf-8')

    def _return_unicode_string_python3(self, string):
        return string
