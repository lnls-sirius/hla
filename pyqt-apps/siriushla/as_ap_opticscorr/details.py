"""OpticsCorr details module."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QPushButton, QGridLayout, QLabel, QSpacerItem, \
    QAbstractItemView, QGroupBox, QSizePolicy as QSzPlcy, QHeaderView
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.namesys import SiriusPVName as _PVName

from siriushla.widgets import SiriusMainWindow, SiriusLabel, \
    SiriusWaveformTable
from .custom_widgets import ConfigLineEdit as _ConfigLineEdit


class CorrParamsDetailWindow(SiriusMainWindow):
    """Correction parameters detail window."""

    def __init__(self, acc, opticsparam, fams, parent=None,
                 prefix=_VACA_PREFIX):
        """Class constructor."""
        super(CorrParamsDetailWindow, self).__init__(parent)
        self._prefix = prefix
        self._acc = acc
        self._opticsparam = opticsparam.title()
        self._fams = fams
        self._nfam = len(self._fams)
        self._intstrength = 'KL' if opticsparam == 'tune' else 'SL'
        self.setWindowTitle(acc+' '+self._opticsparam+' Correction Parameters')
        self.setObjectName(acc.upper() + 'App')
        self._setupUi()

    def _setupUi(self):
        ioc_prefix = _PVName(self._acc+'-Glob:AP-'+self._opticsparam+'Corr')
        ioc_prefix = ioc_prefix.substitute(prefix=self._prefix)

        lay = QGridLayout()

        label_configname = QLabel('<h4>Configuration Name</h4>', self,
                                  alignment=Qt.AlignCenter)
        self.pydmlinedit_configname = _ConfigLineEdit(
            self, ioc_prefix.substitute(propty='ConfigName-SP'))
        self.pydmlinedit_configname.setStyleSheet(
            """min-width:10em; max-width:10em;""")

        self.pydmlabel_configname = SiriusLabel(
            self, ioc_prefix.substitute(propty='ConfigName-RB'))

        lay.addWidget(label_configname, 10, 1, 1, self._nfam)
        lay.addWidget(self.pydmlinedit_configname, 11, self._nfam//2)
        lay.addWidget(self.pydmlabel_configname, 11, self._nfam//2+1)
        lay.addItem(
            QSpacerItem(20, 10, QSzPlcy.Minimum, QSzPlcy.Fixed), 12, 1)

        label_matrix = QLabel('<h4>Matrix</h4>', self,
                              alignment=Qt.AlignCenter)
        self.table_matrix = SiriusWaveformTable(
            self, ioc_prefix.substitute(propty='RespMat-Mon'))
        self.table_matrix.setObjectName('matrix')
        self.table_matrix.setEnabled(False)
        self.table_matrix.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table_matrix.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table_matrix.verticalHeader().setStyleSheet(
            """min-width:1.5em; max-width:1.5em;""")
        self.table_matrix.horizontalHeader().setStyleSheet(
            """min-height:1.5em; max-height:1.5em;""")
        self.table_matrix.setStyleSheet("""
            #matrix{
                min-width:valueem; min-height:5.84em; max-height:5.84em;
            }""".replace('value', str(1.5+8*self._nfam)))
        self.table_matrix.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_matrix.setRowCount(2)
        self.table_matrix.setColumnCount(self._nfam)
        self.table_matrix.rowHeaderLabels = ['  X', '  Y']
        self.table_matrix.columnHeaderLabels = self._fams
        self.table_matrix.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.table_matrix.verticalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.table_matrix.setSizePolicy(QSzPlcy.MinimumExpanding,
                                        QSzPlcy.Preferred)

        lay.addWidget(label_matrix, 13, 1, 1, self._nfam)
        lay.addWidget(self.table_matrix, 14, 1, 1, self._nfam)
        lay.addItem(QSpacerItem(20, 10, QSzPlcy.Minimum, QSzPlcy.Fixed), 15, 1)

        label_nomintstrength = QLabel(
            '<h4>Nominal '+self._intstrength+'s</h4>', self,
            alignment=Qt.AlignCenter)
        self.table_nomintstrength = SiriusWaveformTable(
            self, ioc_prefix.substitute(
                propty='Nominal'+self._intstrength+'-Mon'))
        self.table_nomintstrength.setObjectName('nom_strength')
        self.table_nomintstrength.setEnabled(False)
        self.table_nomintstrength.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.table_nomintstrength.verticalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.table_nomintstrength.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        self.table_nomintstrength.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        self.table_nomintstrength.verticalHeader().setStyleSheet(
            """min-width:1.5em; max-width:1.5em;""")
        self.table_nomintstrength.horizontalHeader().setStyleSheet(
            """min-height:1.5em; max-height:1.5em;""")
        self.table_nomintstrength.setStyleSheet("""
            #nom_strength{
                min-width:valueem; min-height:3.67em; max-height:3.67em;
            }""".replace('value', str(1.5+8*self._nfam)))
        self.table_nomintstrength.setEditTriggers(
            QAbstractItemView.NoEditTriggers)
        self.table_nomintstrength.setRowCount(1)
        self.table_nomintstrength.setColumnCount(self._nfam)
        self.table_nomintstrength.rowHeaderLabels = [self._intstrength]
        self.table_nomintstrength.columnHeaderLabels = self._fams
        self.table_nomintstrength.setSizePolicy(QSzPlcy.MinimumExpanding,
                                                QSzPlcy.Preferred)

        lay.addWidget(label_nomintstrength, 16, 1, 1, self._nfam)
        lay.addWidget(self.table_nomintstrength, 17, 1, 1, self._nfam)
        lay.addItem(QSpacerItem(20, 10, QSzPlcy.Minimum, QSzPlcy.Fixed), 18, 1)

        if self._opticsparam == 'Chrom':
            label_nomchrom = QLabel('<h4>Nominal Chrom</h4>', self,
                                    alignment=Qt.AlignCenter)
            self.pydmlabel_nomchrom = SiriusLabel(
                self, ioc_prefix.substitute(propty='NominalChrom-Mon'))
            self.pydmlabel_nomchrom.setAlignment(Qt.AlignCenter)

            lay.addWidget(label_nomchrom, 19, 1, 1, self._nfam)
            lay.addWidget(self.pydmlabel_nomchrom, 20, 1, 1, self._nfam)

        self.bt_apply = QPushButton('Ok', self)
        self.bt_apply.clicked.connect(self.close)
        lay.addWidget(self.bt_apply, 21, self._nfam)

        cwt = QGroupBox('Correction Parameters')
        cwt.setLayout(lay)
        self.setCentralWidget(cwt)
