"""
PositionLine
    Keep a matplotlib (position,y) line and related methods.

Afonso Haruo Carnielli Mukai (FAC - LNLS)

2013-12-10: v0.1
"""

import numpy as _numpy
from . import custom_line as _custom_line


class OutOfIntervalError(Exception):
    pass


class PositionLine(_custom_line.CustomLine):

    """
    Keep a matplotlib line for position data.
    """

    def __init__(self, line, interval_min, interval_max, interpolate=False):
        super(PositionLine, self).__init__(line)
        self._interval_min = interval_min
        self._interval_max = interval_max
        self._interpolate = interpolate

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, array):
        self._x = array

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, array):
        self._y = array

    def set_data_to_plot(self):
        if self._interpolate:
            new_x, new_y = self._interpolate_to_plot()
        else:
            new_x = self._x
            new_y = self._y

        self._set_x(new_x)
        self._set_y(new_y)

    def _interpolate_to_plot(self):
        self._check_x_array_in_interval()
        x_min_equal = min(self._x) == self._interval_min
        x_max_equal = max(self._x) == self._interval_max

        if not x_min_equal and not x_max_equal:
            new_x, new_y = self._get_data_with_interpolation()
        elif not x_min_equal and x_max_equal:
            new_x, new_y = self._get_data_with_copy_max_to_min()
        elif x_min_equal and not x_max_equal:
            new_x, new_y = self._get_data_with_copy_min_to_max()
        else:
            new_x = self._x
            new_y = self._y

        return (new_x, new_y)

    def _check_x_array_in_interval(self):
        x = self._x
        if min(x) < self._interval_min or max(x) > self._interval_max:
            raise OutOfIntervalError

    def _get_data_with_interpolation(self):
        y_value = self._calculate_interpolation()

        xi = self._interval_min
        xf = self._interval_max
        new_x = _numpy.array([], dtype=type(self._x[0]))
        new_x = _numpy.append(new_x, xi)
        new_x = _numpy.append(new_x, self._x)
        new_x = _numpy.append(new_x, xf)

        new_y = _numpy.array([], dtype=type(self._y[0]))
        new_y = _numpy.append(new_y, y_value)
        new_y = _numpy.append(new_y, self._y)
        new_y = _numpy.append(new_y, y_value)

        return (new_x, new_y)

    def _get_data_with_copy_max_to_min(self):
        xf = self._x[-1]
        new_x = _numpy.array([], dtype=type(self._x[0]))
        new_x = _numpy.append(new_x, xf)
        new_x = _numpy.append(new_x, self._x)

        yf = self._y[-1]
        new_y = _numpy.array([], dtype=type(self._y[0]))
        new_y = _numpy.append(new_y, yf)
        new_y = _numpy.append(new_y, self._y)

        return (new_x, new_y)

    def _get_data_with_copy_min_to_max(self):
        xi = self._x[0]
        new_x = _numpy.array([], dtype=type(self._x[0]))
        new_x = _numpy.append(new_x, self._x)
        new_x = _numpy.append(new_x, xi)

        yi = self._y[0]
        new_y = _numpy.array([], dtype=type(self._y[0]))
        new_y = _numpy.append(new_y, self._y)
        new_y = _numpy.append(new_y, yi)

        return (new_x, new_y)

    def _calculate_interpolation(self):
        xi = self._interval_min
        xf = self._interval_max
        x0 = self._x[0]
        xn = self._x[-1]
        y0 = self._y[0]
        yn = self._y[-1]
        result = yn + (y0-yn)*(xf-xn)/(xf-xn+x0-xi)
        return result
