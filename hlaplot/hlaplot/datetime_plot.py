"""
DateTimePlot
    Class for embedding matplotlib datetime plots in Qt GUI.

Afonso Haruo Carnielli Mukai (FAC - LNLS)

2013-11-27: v0.1
"""

import datetime as _datetime
import matplotlib.dates as _dates
import matplotlib.ticker as _ticker
from . import color_conversion as _color_conversion
from . import custom_plot as _custom_plot
from . import datetime_line as _datetime_line


DEFAULT_BACKGROUND_COLOR = _color_conversion.DEFAULT_BACKGROUND_COLOR
DEFAULT_AXIS_BACKGROUND_COLOR = _color_conversion.DEFAULT_AXIS_BACKGROUND_COLOR
DEFAULT_AXIS_ELEMENTS_COLOR = _color_conversion.DEFAULT_AXIS_ELEMENTS_COLOR


class TickerNameError(Exception):
    pass


class DateTimePlot(_custom_plot.CustomPlot):

    """Embed a datetime plot in PyQt."""

    def __init__(self,
                 background_color=DEFAULT_BACKGROUND_COLOR,
                 axis_background_color=DEFAULT_AXIS_BACKGROUND_COLOR,
                 axis_elements_color=DEFAULT_AXIS_ELEMENTS_COLOR,
                 autoscale=True,
                 x_axis_extra_spacing=_datetime.timedelta(seconds=0),
                 y_axis_extra_spacing=0.0,
                 interval=_datetime.timedelta(hours=1),
                 show_interval=True):

        self.super = super(DateTimePlot, self)
        self.super.__init__(background_color=background_color,
                            axis_background_color=axis_background_color,
                            axis_elements_color=axis_elements_color,
                            autoscale=autoscale,
                            axes_extra_spacing=y_axis_extra_spacing)

        self._figure.autofmt_xdate(rotation=0)
        self._interval = interval
        self._show_interval = show_interval

        self.x_axis_extra_spacing = x_axis_extra_spacing
        self.set_ticker()

        self.x_ticks_label_format = '%H:%M'
        self.datetime_coord_format = '%H:%M:%S'

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, value):
        self._interval = value

    @property
    def show_interval(self):
        return self._show_interval

    @show_interval.setter
    def show_interval(self, value):
        self._show_interval = value

    @property
    def ticker(self):
        return (self._ticker, self._num_ticks)

    @property
    def x_ticks_label_format(self):
        return self._x_ticks_label_format

    @x_ticks_label_format.setter
    def x_ticks_label_format(self, format_string):
        """
        format_string -- a strftime() format string. Examples:
            '%H:%M:%S' -- time
            '%H:%M:%S.%f' -- time with with microseconds
            '%d/%m/%Y' -- date
        """
        self._x_ticks_label_format = format_string
        formatter = _dates.DateFormatter(format_string)
        self._axes.xaxis.set_major_formatter(formatter)

    @property
    def x_tick_label_rotation(self):
        tick_labels = self._axes.get_xticklabels()
        return tick_labels[0].get_rotation()

    @x_tick_label_rotation.setter
    def x_tick_label_rotation(self, angle):
        self._figure.autofmt_xdate(rotation=angle)

    @property
    def datetime_coord_format(self):
        return self._datetime_coord_format

    @datetime_coord_format.setter
    def datetime_coord_format(self, format_string):
        """
        format_string -- a strftime() format string
        """
        date_formatter = _dates.DateFormatter(format_string)
        self._axes.format_xdata = date_formatter
        self._datetime_coord_format = format_string

    def add_line(self, name, max_data_len=1000):
        line, = self._axes.plot_date(x=[], y=[], xdate=True)
        self._lines[name] = _datetime_line.DateTimeLine(line, max_data_len)

    def clear(self):
        for name in self._lines:
            self.line(name).clear()

    def set_ticker(self, name='linear', num_ticks=3):
        """
        name -- 'dynamic', 'linear'
        num_ticks -- number of ticks
        Raises TickerNameError if name is not valid.
        """
        if name == 'linear':
            ticker = _ticker.LinearLocator(numticks=num_ticks)
        elif name == 'dynamic':
            ticker = _ticker.MaxNLocator(nbins=num_ticks+1)
        else:
            raise TickerNameError
        self._axes.xaxis.set_major_locator(ticker)

    def _find_axis_min_and_max(self, axis):
        if axis == 'y':
            result = self.super._find_axis_min_and_max(axis)
        else:
            minimum, maximum = self._find_axis_lines_mins_and_maxs(axis)
            min_, max_ = self._get_min_max_or_now_if_empty(minimum, maximum)
            if self._show_interval:
                min_, max_ = self._resize_to_interval(min_, max_)
            result = self._return_unit_hour_interval_if_equal(min_, max_)
        return result

    def _get_min_max_or_now_if_empty(self, min_, max_):
        if len(min_) > 0:
            new_min = min(min_)
            new_max = min(max_)
        else:
            new_min = _datetime.datetime.now()
            new_max = new_min

        return (new_min, new_max)

    def _resize_to_interval(self, min_, max_):
        new_min = min_
        new_max = max_
        if max_- min_ < self._interval:
            new_max = min_ + self._interval
        else:
            new_min = max_ - self._interval
        return (new_min, new_max)

    def _return_unit_hour_interval_if_equal(self, min_, max_):
        if min_ == max_:
            new_min = max_ - _datetime.timedelta(hours=1)
        else:
            new_min = min_
        new_max = max_

        return (new_min, new_max)

    def _calculate_new_bounds_for_axis(self, bounds, axis):
        if axis == 'x':
            new_min, new_max = self._calculate_new_datetime_bounds(bounds)
            return (new_min, new_max)
        else:
            s = super(DateTimePlot, self)
            return s._calculate_new_bounds_for_axis(bounds, 'y')

    def _calculate_new_datetime_bounds(self, bounds):
        bounds_datetime = self._convert_if_floats_to_datetime(bounds)
        extra_spacing = self._select_axis_extra_spacing('x')
        new_min = bounds_datetime[0] - extra_spacing.min
        new_max = bounds_datetime[1] + extra_spacing.max
        return (new_min, new_max)

    def _convert_if_floats_to_datetime(self, values):
        if isinstance(values[0], _datetime.datetime):
            values_datetime = values
        else:
            values_datetime = _dates.num2date(values)
        return values_datetime
