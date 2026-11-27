"""S3PW Vacuum Module."""

import qtawesome as qta

from qtpy.QtCore import Qt, QSize
from qtpy.QtWidgets import QFrame, QGroupBox, QLabel, QWidget, \
    QPushButton, QHBoxLayout, QGridLayout, QVBoxLayout

from pydm.widgets import PyDMPushButton

from siriuspy.namesys import SiriusPVName as _PVName

from siriushla.util import connect_newprocess, connect_window
from siriushla.widgets import SiriusLedAlert, SiriusLabel, SiriusSpinbox, \
    SiriusLedState, SiriusLineEdit, SiriusEnumComboBox, \
    PyDMStateButton, SiriusTimePlot
from siriushla.widgets.dialog import StatusDetailDialog

from ..base import IDCommonControlWindow, IDCommonDialog, IDCommonSummaryBase, \
    IDCommonSummaryHeader, IDCommonSummaryWidget


class S3PWVacuum(IDCommonDialog):
    def __init__(self, parent=None, prefix='', device='', title=''):
        super().__init__(parent, prefix, device, title)

    def _setupUi(self):
        gbox = QGroupBox('Heaters Status', self)
        glay = QGridLayout(gbox)