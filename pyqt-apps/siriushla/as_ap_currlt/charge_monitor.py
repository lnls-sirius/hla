from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QFormLayout, QSpacerItem, \
    QSizePolicy as QSzPlcy
from pydm.widgets import PyDMLabel
from siriuspy.envars import vaca_prefix
from siriushla.widgets import SiriusMainWindow


class BOMonitor(SiriusMainWindow):
    """BO charges monitor."""

    def __init__(self, parent=None, prefix=vaca_prefix):
        super().__init__(parent)
        self._prefix = prefix
        self.setWindowTitle('BO Charge Monitor')
        self._setupUi()

    def _setupUi(self):
        cw = QWidget(self)
        self.setCentralWidget(cw)

        label = QLabel('Booster Charge [A.h]')
        label.setStyleSheet('font-weight: bold;')

        ioc_prefix = 'BO-Glob:AP-CurrInfo'
        label150MeV = QLabel('150MeV: ')
        label150MeV.setStyleSheet('font-weight: bold;')
        self.label150MeV = PyDMLabel(
            parent=self,
            init_channel=self._prefix+ioc_prefix+':Charge150MeV-Mon')
        self.label150MeV.showUnits = True
        self.label150MeV.precisionFromPV = True
        self.label150MeV.displayFormat = PyDMLabel.Exponential

        label1GeV = QLabel('1GeV: ')
        label1GeV.setStyleSheet('font-weight: bold;')
        self.label1GeV = PyDMLabel(
            parent=self,
            init_channel=self._prefix+ioc_prefix+':Charge1GeV-Mon')
        self.label1GeV.displayFormat = PyDMLabel.Exponential

        label2GeV = QLabel('2GeV: ')
        label2GeV.setStyleSheet('font-weight: bold;')
        self.label2GeV = PyDMLabel(
            parent=self,
            init_channel=self._prefix+ioc_prefix+':Charge2GeV-Mon')
        self.label2GeV.displayFormat = PyDMLabel.Exponential

        label3GeV = QLabel('3GeV: ')
        label3GeV.setStyleSheet('font-weight: bold;')
        self.label3GeV = PyDMLabel(
            parent=self,
            init_channel=self._prefix+ioc_prefix+':Charge3GeV-Mon')
        self.label3GeV.displayFormat = PyDMLabel.Exponential

        lay = QFormLayout(cw)
        lay.setLabelAlignment(Qt.AlignRight)
        lay.addRow(label)
        lay.addItem(QSpacerItem(1, 1, QSzPlcy.Fixed, QSzPlcy.Fixed))
        lay.addRow(label150MeV, self.label150MeV)
        lay.addRow(label1GeV, self.label1GeV)
        lay.addRow(label2GeV, self.label2GeV)
        lay.addRow(label3GeV, self.label3GeV)

        self.setStyleSheet("""
            QLabel{
                qproperty-alignment: 'AlignHCenter';
            }
            """)
