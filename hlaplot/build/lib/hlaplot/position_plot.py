
import matplotlib.ticker
from . import color_conversion as _color_conversion
from . import position_line as _position_line
from . import custom_plot as _custom_plot


DEFAULT_BACKGROUND_COLOR = _color_conversion.DEFAULT_BACKGROUND_COLOR
DEFAULT_AXIS_BACKGROUND_COLOR = _color_conversion.DEFAULT_AXIS_BACKGROUND_COLOR
DEFAULT_AXIS_ELEMENTS_COLOR = _color_conversion.DEFAULT_AXIS_ELEMENTS_COLOR


class IntervalBoundsError(Exception):
    pass


class LengthError(Exception):
    pass


class PositionPlot(_custom_plot.CustomPlot):

    """Embed a position plot in PyQt."""

    def __init__(self,
                 background_color=DEFAULT_BACKGROUND_COLOR,
                 axis_background_color=DEFAULT_AXIS_BACKGROUND_COLOR,
                 axis_elements_color=DEFAULT_AXIS_ELEMENTS_COLOR,
                 autoscale=True,
                 axis_extra_spacing=0,
                 interval_min=0,
                 interval_max=1):

        if not interval_min <= interval_max:
            raise IntervalBoundsError

        self.super = super(PositionPlot, self)
        self.super.__init__(background_color=background_color,
                            axis_background_color=axis_background_color,
                            axis_elements_color=axis_elements_color,
                            autoscale=autoscale,
                            axes_extra_spacing=axis_extra_spacing)

        self._interval_min = interval_min
        self._interval_max = interval_max

        self.x_axis = (self._interval_min, self._interval_max)

        self._ticks = {}
        self._selected_ticks = []

    @property
    def ticks(self):
        return self._ticks

    @property
    def selected_ticks(self):
        return self._selected_ticks

    def define_ticks(self, names, pos):
        if len(names) != len(pos):
            raise LengthError
        name_pos_pairs = zip(names, pos)
        self._ticks = dict(name_pos_pairs)

    def select_ticks(self, names):
        """
        Select ticks to be displayed.
        Raises KeyError if names are not valid keys.
        """
        self._check_tick_names_exist(names)
        pos = self._get_selected_ticks_pos_by_name(names)
        ticker = matplotlib.ticker.FixedLocator(locs=pos, nbins=len(pos))
        formatter = matplotlib.ticker.FixedFormatter(names)
        self._axes.xaxis.set_major_locator(ticker)
        self._axes.xaxis.set_major_formatter(formatter)
        self._selected_ticks = names

    def add_line(self, name, interpolate=False):
        """Add new line for presenting (position,y) data"""
        line, = self._axes.plot([])
        self._lines[name] = _position_line.PositionLine(line,
                                                      self._interval_min,
                                                      self._interval_max,
                                                      interpolate)

    def update_plot(self):
        for line in self._lines:
            self._lines[line].set_data_to_plot()
        self.super.update_plot()

    def _find_axis_min_and_max(self, axis):
        if axis == 'y':
            result = self.super._find_axis_min_and_max(axis)
        else:
            new_min = self._interval_min
            new_max = self._interval_max
            result = (new_min, new_max)
        return result

    def _check_tick_names_exist(self, names):
        for name in names:
            if not name in self._ticks:
                raise KeyError

    def _get_selected_ticks_pos_by_name(self, names):
        pos = []
        for name in names:
            pos.append(self._ticks[name])
        return pos
