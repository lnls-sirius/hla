from pydm.widgets.qtplugin_base import qtplugin_factory

from .label import SiriusLabel
from .log_label import PyDMLogLabel
from .led import PyDMLed, SiriusLedState, SiriusLedAlert, \
    PyDMLedMultiChannel, PyDMLedMultiConnection
from .QLed import QLed
from .QDoubleScrollBar import QDoubleScrollBar
from .scrollbar import PyDMScrollBar
from .spinbox import SiriusSpinbox
from .state_button import PyDMStateButton
from .line_edit import SiriusLineEdit
from .spectrogram_view import SiriusSpectrogramView
from .string_combo_box import SiriusStringComboBox
from .timeplot import SiriusTimePlot
from .enum_combo_box import SiriusEnumComboBox
from .windows import SiriusDialog, SiriusMainWindow

SIRIUS_CATEGORY = 'Sirius Widgets'

# windows
SiriusMainWindowPlugin = qtplugin_factory(
                    SiriusMainWindow, is_container=True, group=SIRIUS_CATEGORY)
SiriusDialogPlugin = qtplugin_factory(
                    SiriusDialog, is_container=True, group=SIRIUS_CATEGORY)

# Led plugin
QLedPlugin = qtplugin_factory(QLed, group=SIRIUS_CATEGORY)
PyDMLedPlugin = qtplugin_factory(PyDMLed, group=SIRIUS_CATEGORY)
PyDMLedMultiChannelPlugin = qtplugin_factory(
    PyDMLedMultiChannel, group=SIRIUS_CATEGORY)
PyDMLedMultiConnectionPlugin = qtplugin_factory(
    PyDMLedMultiConnection, group=SIRIUS_CATEGORY)
SiriusLedStatePlugin = qtplugin_factory(SiriusLedState, group=SIRIUS_CATEGORY)
SiriusLedAlertPlugin = qtplugin_factory(SiriusLedAlert, group=SIRIUS_CATEGORY)

# Log Label
PyDMLogLabelPlugin = qtplugin_factory(PyDMLogLabel, group=SIRIUS_CATEGORY)

# Label plugin
SiriusLabelPlugin = qtplugin_factory(SiriusLabel, group=SIRIUS_CATEGORY)

# LineEdit plugin
SiriusLineEditPlugin = qtplugin_factory(SiriusLineEdit, group=SIRIUS_CATEGORY)

# Scrollbar plugin
QDoubleScrollBarPlugin = qtplugin_factory(
                    QDoubleScrollBar, group=SIRIUS_CATEGORY)
PyDMScrollBarPlugin = qtplugin_factory(PyDMScrollBar, group=SIRIUS_CATEGORY)

# State Button
PyDMStateButtonPlugin = qtplugin_factory(
                    PyDMStateButton, group=SIRIUS_CATEGORY)

# Spinbox plugin
SiriusSpinboxPlugin = qtplugin_factory(SiriusSpinbox, group=SIRIUS_CATEGORY)

# String ComboBox plugin
SiriusStringComboBoxPlugin = qtplugin_factory(
    SiriusStringComboBox, group=SIRIUS_CATEGORY)

# Enum ComboBox plugin
SiriusEnumComboBoxPlugin = qtplugin_factory(
    SiriusEnumComboBox, group=SIRIUS_CATEGORY)

# Spectrogram plugin
SiriusSpectrogramViewPlugin = qtplugin_factory(
    SiriusSpectrogramView, group=SIRIUS_CATEGORY)

# TimePlot plugin
SiriusTimePlotPlugin = qtplugin_factory(
    SiriusTimePlot, group=SIRIUS_CATEGORY)
