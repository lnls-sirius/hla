import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QLabel, QWidget, QScrollArea
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QSizePolicy as QSzPol
from pydm.widgets.waveformplot import PyDMWaveformPlot
from pydm.widgets.label import PyDMLabel
from pydm.widgets.line_edit import PyDMLineEdit
from pydm.widgets.spinbox import PyDMSpinbox
from pydm.widgets.pushbutton import PyDMPushButton
from pydm.widgets.enum_combo_box import PyDMEnumComboBox as PyDMECB
from pydm.widgets.checkbox import PyDMCheckbox as PyDMCb
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets.led import PyDMLed, SiriusLedAlert
from siriushla.widgets.state_button import PyDMStateButton
from siriushla.widgets.windows import SiriusMainWindow
from siriuspy.namesys import SiriusPVName as _PVName
from siriushla import util as _util


class RampMain(SiriusMainWindow):
    """Template for control of High Level Triggers."""

    def __init__(self, parent=None, prefix=''):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self._setupUi()

    def _setupUi(self):
        # self.resize(2000, 2000)
        cw = QWidget(self)
        self.setCentralWidget(cw)
        self.my_layout = QGridLayout(cw)
        self.my_layout.setHorizontalSpacing(20)
        self.my_layout.setVerticalSpacing(20)
        lab = QLabel('<h1>Booster Energy Ramping</h1>', cw)
        self.my_layout.addWidget(lab, 0, 0, 1, 3)
        self.my_layout.setAlignment(lab, Qt.AlignCenter)

        self.ramp_settings = RampSettings(self, self.prefix)
        self.my_layout.addWidget(self.ramp_settings, 1, 0)

        self.commands = RampCommands(self, self.prefix)
        self.my_layout.addWidget(self.commands, 2, 0, 2, 1)

        self.ramp_parameters = RampParameters(self, self.prefix)
        self.my_layout.addWidget(self.ramp_parameters, 1, 1, 2, 1)

        self.optics_adjust = OpticsAdjust(self, self.prefix)
        self.my_layout.addWidget(self.optics_adjust, 3, 1)

        self.statistics = RampStatistics(self, self.prefix)
        self.my_layout.addWidget(self.statistics, 1, 2, 3, 1)


class RampSettings(QGroupBox):

    def __init__(self, parent=None, prefix=''):
        super().__init__('Ramp Settings', parent)
        self.prefix = _PVName(prefix)
        self._setupUi()

    def _setupUi(self):
        self.bt_load = QPushButton('Load', self)
        self.bt_save = QPushButton('Save', self)
        self.bt_load.clicked.connect(self._load)
        self.bt_save.clicked.connect(self._save)
        lay = QVBoxLayout(self)
        lay.addWidget(self.bt_load)
        lay.addWidget(self.bt_save)

    def _load(self):
        print('Do stuff')

    def _save(self):
        print('Do stuff')


class RampCommands(QGroupBox):

    def __init__(self, parent=None, prefix=''):
        super().__init__('Commands', parent)
        self.prefix = _PVName(prefix)
        self._setupUi()

    def _setupUi(self):
        self.bt_calculate = QPushButton('Calculate', self)
        self.bt_upload = QPushButton('Upload to PS', self)
        self.bt_cycle = QPushButton('Cycle', self)
        self.bt_start = QPushButton('Start', self)
        self.bt_stop = QPushButton('Stop', self)
        self.bt_abort = QPushButton('Abort', self)
        self.bt_abort.setStyleSheet('background-color: rgb(255, 0, 0);')

        self.bt_calculate.clicked.connect(self._calculate)
        self.bt_upload.clicked.connect(self._upload)
        self.bt_cycle.clicked.connect(self._cycle)
        self.bt_start.clicked.connect(self._start)
        self.bt_stop.clicked.connect(self._stop)
        self.bt_abort.clicked.connect(self._abort)

        lay = QVBoxLayout(self)
        lay.addWidget(self.bt_calculate)
        lay.addWidget(self.bt_upload)
        lay.addWidget(self.bt_cycle)
        lay.addWidget(self.bt_start)
        lay.addWidget(self.bt_stop)
        lay.addWidget(self.bt_abort)

    def _calculate(self):
        print('Do stuff')

    def _upload(self):
        print('Do stuff')

    def _cycle(self):
        print('Do stuff')

    def _start(self):
        print('Do stuff')

    def _stop(self):
        print('Do stuff')

    def _abort(self):
        print('Do stuff')


class RampParameters(QGroupBox):

    def __init__(self, parent=None, prefix=''):
        super().__init__('Ramping Parameters', parent)
        self.prefix = _PVName(prefix)
        self._setupUi()

    def _setupUi(self):
        my_lay = QHBoxLayout(self)
        self.dip_ramp = DipoleRamp(self, self.prefix)
        self.mult_ramp = MultipolesRamp(self, self.prefix)
        self.rf_ramp = RFRamp(self, self.prefix)
        my_lay.addWidget(self.dip_ramp)
        my_lay.addWidget(self.mult_ramp)
        my_lay.addWidget(self.rf_ramp)


class DipoleRamp(QWidget):

    def __init__(self, parent=None, prefix=''):
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self._setupUi()

    def _setupUi(self):
        vlay = QVBoxLayout(self)
        self.graph = PyDMWaveformPlot(self)
        self.table = QTableWidget(self)
        vlay.addWidget(
            QLabel('<h5>Dipole Ramp</h5>', self),
            alignment=Qt.AlignCenter)
        vlay.setAlignment(Qt.AlignCenter)
        vlay.addWidget(self.graph)
        vlay.addWidget(self.table)


class MultipolesRamp(QWidget):

    def __init__(self, parent=None, prefix=''):
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self._setupUi()

    def _setupUi(self):
        vlay = QVBoxLayout(self)
        self.graph = PyDMWaveformPlot(self)
        self.table = QTableWidget(self)
        vlay.addWidget(
            QLabel('<h5>Multipoles Ramp</h5>', self),
            alignment=Qt.AlignCenter)
        vlay.setAlignment(Qt.AlignCenter)
        vlay.addWidget(self.graph)
        vlay.addWidget(self.table)


class RFRamp(QWidget):

    def __init__(self, parent=None, prefix=''):
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self._setupUi()

    def _setupUi(self):
        vlay = QVBoxLayout(self)
        self.graph = PyDMWaveformPlot(self)
        self.table = QTableWidget(self)
        vlay.addWidget(
            QLabel('<h5>RF Ramp</h5>', self),
            alignment=Qt.AlignCenter)
        vlay.setAlignment(Qt.AlignCenter)
        vlay.addWidget(self.graph)
        vlay.addWidget(self.table)


class OpticsAdjust(QGroupBox):

    def __init__(self, parent=None, prefix=''):
        super().__init__('Optics Configuration Adjustment', parent)
        self.prefix = _PVName(prefix)
        self._setupUi()

    def _setupUi(self):
        self.bt_load = QPushButton('Load', self)
        self.bt_save = QPushButton('Save', self)
        self.bt_load.clicked.connect(self._load)
        self.bt_save.clicked.connect(self._save)

    def _load(self):
        print('Do stuff')

    def _save(self):
        print('Do stuff')


class RampStatistics(QGroupBox):

    def __init__(self, parent=None, prefix=''):
        super().__init__('Statistics', parent)
        self.prefix = _PVName(prefix)
        self._setupUi()

    def _setupUi(self):
        pass


if __name__ == '__main__':
    """Run Example."""
    app = SiriusApplication()
    _util.set_style(app)
    ramp = RampMain(
        prefix='ca://fernando-lnls452-linux-AS-Glob:TI-EVG:')
    ramp.show()
    sys.exit(app.exec_())
