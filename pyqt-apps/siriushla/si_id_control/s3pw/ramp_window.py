"""S3PW Ramp Module."""

import qtawesome as qta

from qtpy.QtCore import Qt, QSize
from qtpy.QtWidgets import QFrame, QGroupBox, QLabel, QWidget, \
    QPushButton, QHBoxLayout, QGridLayout, QVBoxLayout

from pydm.widgets import PyDMPushButton

from siriuspy.namesys import SiriusPVName as _PVName

from siriushla.widgets import SiriusLedAlert, SiriusLabel, SiriusSpinbox, \
    SiriusLedState, SiriusLineEdit, SiriusEnumComboBox, \
    PyDMStateButton, SiriusTimePlot

from ..base import IDCommonControlWindow, IDCommonDialog, IDCommonSummaryBase, \
    IDCommonSummaryHeader, IDCommonSummaryWidget


class S3PWRamp(IDCommonDialog):
    def __init__(self, parent=None, prefix='', device='', title=''):
        super().__init__(parent, prefix, device, title)

    def _setupUi(self):
        gbox = QGroupBox('Ramp', self)
        glay = QGridLayout(gbox)
