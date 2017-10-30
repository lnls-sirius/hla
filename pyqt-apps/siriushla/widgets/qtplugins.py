from pydm.widgets.qtplugin_base import qtplugin_factory, WidgetCategory

from .log_label import PyDMLogLabel
from .led import PyDMLed, SiriusLedState, SiriusLedAlert
from .QLed import QLed
from .QDoubleScrollBar import QDoubleScrollBar
from .scrollbar import PyDMScrollBar
from .state_button import PyDMStateButton

SIRIUS_CATEGORY = 'Sirius Widgets'

# Led plugin
PyDMLedPlugin = qtplugin_factory(PyDMLed, group=SIRIUS_CATEGORY)
SiriusLedStatePlugin = qtplugin_factory(SiriusLedState, group=SIRIUS_CATEGORY)
SiriusLedAlertPlugin = qtplugin_factory(SiriusLedAlert, group=SIRIUS_CATEGORY)

# Log Label
PyDMLogLabelPlugin = qtplugin_factory(PyDMLogLabel,
                                      group=SIRIUS_CATEGORY)

# Scrollbar plugin
PyDMScrollBarPlugin = qtplugin_factory(PyDMScrollBar,
                                       group=SIRIUS_CATEGORY)

# State Button
PyDMStateButtonPlugin = qtplugin_factory(PyDMStateButton,
                                         group=SIRIUS_CATEGORY)

# Scrollbar plugin
QDoubleScrollBarPlugin = qtplugin_factory(QDoubleScrollBar,
                                          group=SIRIUS_CATEGORY)

# Led plugin
QLedPlugin = qtplugin_factory(QLed, group=SIRIUS_CATEGORY)
