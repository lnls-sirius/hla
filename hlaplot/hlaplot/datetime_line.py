"""
DateTimeLine
    Keep a matplotlib (date,y) line and related methods.

Afonso Haruo Carnielli Mukai (FAC - LNLS)

2013-11-27: v0.1
"""

import datetime as _datetime
import numpy as _numpy
from . import custom_line as _custom_line


class DateTimeLengthError(Exception):
    pass


class DateTimeLine(_custom_line.CustomLine):

    """
    Keep a matplotlib line for datetime data and the maximum array length.
    """

    def __init__(self, line, max_data_length=1000):
        """
        line -- matplotlib Line2D
        max_data_length -- the maximum array length (default 1000)
        """
        super(DateTimeLine, self).__init__(line)
        self._max_data_length = max_data_length
        self.line_style = '-'
        self.marker = 'None'

    @property
    def length(self):
        x = self._get_x()
        y = self._get_y()
        if not len(x) == len(y):
            raise DateTimeLengthError
        else:
            return len(x)

    @property
    def max_length(self):
        return self._max_data_length

    @property
    def x(self):
        return super(DateTimeLine, self)._get_x()

    @x.setter
    def x(self, array):
        self._check_array_length(array)
        super(DateTimeLine, self)._set_x(array)

    @property
    def y(self):
        return super(DateTimeLine, self)._get_y()

    @y.setter
    def y(self, array):
        self._check_array_length(array)
        super(DateTimeLine, self)._set_y(array)

    def clear(self):
        self.x = []
        self.y = []

    def add_y(self, y):
        x = _datetime.datetime.now()
        self.add_xy(x, y)

    def add_xy(self, x, y):
        current_x = self._get_x()
        current_y = self._get_y()
        length = self.length
        if length < self._max_data_length:
            new_x = self._append(current_x, x)
            new_y = self._append(current_y, y)
        else:
            new_x = self._remove_first_and_append(current_x, x)
            new_y = self._remove_first_and_append(current_y, y)
        self._set_x(new_x)
        self._set_y(new_y)

    def _append(self, array, element):
        return _numpy.append(array, element)

    def _remove_first_and_append(self, array, element):
        return _numpy.append(array[1:], element)

    def _check_array_length(self, array):
        if len(array) > self._max_data_length:
            raise DateTimeLengthError
