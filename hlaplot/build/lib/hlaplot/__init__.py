"""Plot utilities for PyQt GUIs"""

import os as _os
from . import color_conversion
from . import custom_line
from . import custom_plot
from . import custom_toolbar
from . import datetime_line
from . import datetime_plot
from . import position_line
from . import position_plot


__all__ = ['custom_plot', 'datetime_plot', 'position_plot']


with open(_os.path.join(__path__[0], 'VERSION'), 'r') as _f:
    __version__ = _f.read().strip()


# Legacy API
CustomPlot = custom_plot
DateTimePlot = datetime_plot
PositionPlot = position_plot
