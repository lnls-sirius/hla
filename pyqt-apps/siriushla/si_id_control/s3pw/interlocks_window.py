"""S3PW Interlocks Module."""

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


class S3PWInterlocks(IDCommonDialog):

    QUENCH_STS = {
        'Quench Detector Monitor 1 (P)': 'QDSPTrigTs-Mon',
        'Quench Detector Monitor 2 (R)': 'QDSRTrigTs-Mon',
        'Power On QDS01 (P)': 'QDSPPwrEnbl-Mon',
        'Power On QDS02 (R)': 'QDSRPwrEnbl-Mon',
        'Connection Loss ADC QDS P': 'QDSPADC1ConnectionIntlk-Mon',
        'Connection Loss ADC QDS R': 'QDSRADC2ConnectionIntlk-Mon',
        'Connection Loss QDS 01 ETH P ': 'QDSPConnectionIntlk-Mon',
        'Connection Loss QDS 01 ETH R ': 'QDSRConnectionIntlk-Mon',
    }

    EXTRACT_STS = {
        'Extraction 1 Enabled': 'ExtrPEnbl-Mon',
        'Extraction 2 Enabled': 'ExtrREnbl-Mon',
        'Extraction Auxiliary Contact 01.A': 'ExtrPCoilAIntlk-Mon',
        'Extraction Auxiliary Contact 01.B': 'ExtrPCoilBIntlk-Mon',
        'Extraction Auxiliary Contact 02.A': 'ExtrRCoilAIntlk-Mon',
        'Extraction Auxiliary Contact 02.B': 'ExtrRCoilBIntlk-Mon',
        'Thermo 1': 'ExtrPTempIntlk-Mon',
        'Thermo 2': 'ExtrRTempIntlk-Mon',
    }

    PWR_SUPPLY_STS = {
        'Power Supply 1 Enabled': 'PSCenCoilPwrEnbl-Mon',
        'Rotameter 1': 'PSCenCoilRotEnbl-Mon',
        'Power Supply 2 Enabled': 'PSLatCoilPwrEnbl-Mon',
        'Rotameter 2': 'PSLatCoilRotEnbl-Mon',
    }

    VACUUM_STS = {
        'Relay CC 01': 'miss',
        'Pirani': 'miss',
    }

    SAFETY_STS = {
        'Emergency Button Local': 'RemoteEStopTs-Mon',
        'Emergency Button Remote': 'LocalEStopTs-Mon',
    }

    COMPRESSOR_STS = {
        'Compressor 1 Pressure': 'Comp1PressureIntlk-Mon',
        'Compressor 1 Temperature': 'Comp1TempIntlk-Mon',
        'Compressor 1 Rotameter': 'Comp1RotIntlk-Mon',
        'Compressor 2 Pressure': 'Comp2PressureIntlk-Mon',
        'Compressor 2 Temperature': 'Comp2TempIntlk-Mon',
        'Compressor 2 Rotameter': 'Comp2RotIntlk-Mon',
        'Compressor 3 Pressure': 'Comp3PressureIntlk-Mon',
        'Compressor 3 Temperature': 'Comp3TempIntlk-Mon',
        'Compressor 3 Rotameter': 'Comp3RotIntlk-Mon',
        'Compressor 4 Pressure': 'Comp4PressureIntlk-Mon',
        'Compressor 4 Temperature': 'Comp4TempIntlk-Mon',
        'Compressor 4 Rotameter': 'Comp4RotIntlk-Mon',
    }
    
    def __init__(self, parent=None, prefix='', device='', title=''):
        super().__init__(parent, prefix, device, title=title)

    def _setupUi(self):
        glay = QHBoxLayout()
        self.setLayout(glay)
        self.setFixedSize(600, 640)

        left_frame = QFrame()
        left_lay = QVBoxLayout(left_frame)

        right_frame = QFrame()
        right_lay = QVBoxLayout(right_frame)
        
        quench = self._createGBox('Quench', self.QUENCH_STS)
        extract = self._createGBox('Extractor Circuit', self.EXTRACT_STS)
        pwr_supply = self._createGBox('Power Supplies', self.PWR_SUPPLY_STS)
        vacuum = self._createGBox('Vacuum', self.VACUUM_STS)
        compr = self._createGBox('Compressors', self.COMPRESSOR_STS)
        safety = self._createGBox('Safety', self.SAFETY_STS)

        left_lay.addWidget(safety)
        left_lay.addWidget(quench)
        left_lay.addWidget(extract)
        right_lay.addWidget(pwr_supply)
        right_lay.addWidget(vacuum)
        right_lay.addWidget(compr)

        glay.addWidget(left_frame)
        glay.addWidget(right_frame)


    def _createGBox(self, title, labels):
        group = QGroupBox(title, self)
        lay = QGridLayout(group)
        lay.setContentsMargins(12,12,12,12)

        for idx, (lbl, pv) in enumerate(labels.items()):
            pvname = self.dev_pref.substitute(propty=pv)
            led = SiriusLedState(self, init_channel=pvname)
            led.setFixedSize(QSize(40,40))
            label = QLabel(lbl, self)
            lay.addWidget(led, idx, 0, alignment=Qt.AlignVCenter)
            lay.addWidget(label, idx, 1, alignment=Qt.AlignLeft | Qt.AlignVCenter)

        return group