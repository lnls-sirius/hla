"""S3PW Heaters Module."""

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


class S3PWHeaters(IDCommonDialog):
    """S3PW Heaters Details"""

    def __init__(self, parent=None, prefix='', device='', title=''):
        """Init."""
        super().__init__(
            parent, prefix, device, title)
        self.setMinimumWidth(1000)

    def _setupUi(self):
        lay = QHBoxLayout()
        self.setLayout(lay)

        gbox = QGroupBox('Heaters Status', self)
        glay = QGridLayout(gbox)

        ld_hist = QLabel('<h4>Histerese</h4>', self)
        ld_volt = QLabel('<h4>Voltage</h4>', self)
        ld_curr = QLabel('<h4>Current</h4>', self)
        ld_pwr = QLabel('<h4>Power</h4>', self)

        glay.addWidget(ld_hist, 1, 0)
        glay.addWidget(ld_volt, 2, 0)
        glay.addWidget(ld_curr, 3, 0)
        glay.addWidget(ld_pwr, 4, 0)

        details = [
            "<h4>Cold Bus</h4><h4>(Heater 1)</h4>",
            "<h4>Bottom Yoke</h4><h4>(Heater 2)</h4>",
            "<h4>Base Frame</h4><h4>(Heater 3)</h4>",
            "<h4>Chamber Support</h4><h4>(Heater 4)</h4>",
            "<h4>Shield 20K</h4><h4>(Heater 5)</h4>",
            "<h4>Shield 60K</h4><h4>(Heater 6)</h4>",
        ]

        heaters = [
            'ColdBus',
            'BottomYoke',
            'BaseFrame',
            'ChamberSup',
            '20KShield',
            '60KShield'
        ]

        for idx, title in enumerate(details):
            col = idx + 1
            title = QLabel(title, self)

            hist = self.dev_pref.substitute(propty=f'{heaters[idx]}Hist-Mon')
            hist_pv = SiriusLabel(self, init_channel=hist)
            volt = self.dev_pref.substitute(propty=f'Heat{col}_{heaters[idx]}Volt-Mon')
            volt_pv = SiriusLabel(self, init_channel=volt)
            curr = self.dev_pref.substitute(propty=f'Heat{col}_{heaters[idx]}Curr-Mon')
            curr_pv = SiriusLabel(self, init_channel=curr)
            pwr = self.dev_pref.substitute(propty=f'Heat{col}_{heaters[idx]}Pwr-Mon')
            pwr_pv = SiriusLabel(self, init_channel=pwr)

            glay.addWidget(title, 0, col)
            glay.addWidget(hist_pv, 1, col)
            glay.addWidget(volt_pv, 2, col)
            glay.addWidget(curr_pv, 3, col)
            glay.addWidget(pwr_pv, 4, col)

        gbox.setStyleSheet(
            'QLabel{qproperty-alignment: AlignCenter; max-width: 12em;}')
    
        lay.addWidget(gbox)