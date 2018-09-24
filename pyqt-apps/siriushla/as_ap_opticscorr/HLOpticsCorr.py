#!/usr/bin/env python-sirius
"""Booster Optics Correction HLA Module."""

import epics as _epics
from qtpy.uic import loadUi
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QPushButton, QGridLayout, QLabel, QFrame, \
                            QSpacerItem, QAbstractItemView, QGroupBox, \
                            QSizePolicy as QSzPlcy
from pydm.widgets import PyDMEnumComboBox, PyDMLabel, PyDMLineEdit, \
                            PyDMWaveformTable
from pydm.utilities.macro import substitute_in_file as _substitute_in_file
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriushla.widgets.state_button import PyDMStateButton
from siriushla import util as _hlautil
from siriushla.widgets.windows import SiriusMainWindow
from siriushla.as_ps_control.PSDetailWindow import PSDetailWindow


class OpticsCorrWindow(SiriusMainWindow):
    """Class to include some intelligence in the .ui files."""

    def __init__(self, acc, opticsparam, parent=None, prefix=''):
        """Initialize some widgets."""
        super(OpticsCorrWindow, self).__init__(parent)
        if prefix == '':
            prefix = _vaca_prefix
        self._acc = acc

        UI_FILE = ('/home/fac_files/lnls-sirius/hla/pyqt-apps/siriushla/'
                   'as_ap_opticscorr/ui_'+acc+'_ap_'+opticsparam+'corr.ui')

        tmp_file = _substitute_in_file(UI_FILE, {'PREFIX': prefix})
        self.centralwidget = loadUi(tmp_file)
        self.setCentralWidget(self.centralwidget)

        if opticsparam == 'tune':
            text = 'Tune'
            self.statusLabel_pv = _epics.PV(
                prefix+acc.upper()+'-Glob:AP-TuneCorr:StatusLabels-Cte')
            self.statusLabel_pv.add_callback(self._setStatusLabels)

        elif opticsparam == 'chrom':
            text = 'Chromaticity'
            self.statusLabel_pv = _epics.PV(
                prefix+acc.upper()+'-Glob:AP-ChromCorr:StatusLabels-Cte')
            self.statusLabel_pv.add_callback(self._setStatusLabels)

        self.opticsparam = opticsparam
        self.setWindowTitle(acc.upper() + ' ' + text + ' Correction')

        for button in self.centralwidget.findChildren(QPushButton):
            if 'MADetail' in button.objectName():
                ma = button.text()
                _hlautil.connect_window(button, PSDetailWindow, self,
                                        psname=ma)
            if 'CorrParams' in button.objectName():
                _hlautil.connect_window(button, CorrParamsDetailWindow,
                                        parent=self, acc=acc.upper(),
                                        opticsparam=opticsparam, prefix=prefix)

    def _setStatusLabels(self, value, **kws):
        if self._acc == 'si':
            status_bits = 5
        elif self._acc == 'bo':
            status_bits = 4
        for i in range(status_bits):
            exec('self.centralwidget.label_status{0}.setText'
                 '(value[{0}])'.format(i))


class CorrParamsDetailWindow(SiriusMainWindow):
    """Correction parameters detail window."""

    def __init__(self, acc, opticsparam, parent=None, prefix=None):
        """Class constructor."""
        super(CorrParamsDetailWindow, self).__init__(parent)

        if opticsparam == 'tune':
            intstrength = 'KL'
            opticsparam = 'Tune'
            if acc == 'SI':
                fams = ['QFA', 'QFB', 'QFP',
                        'QDA', 'QDB1', 'QDB2', 'QDP1', 'QDP2']
            else:
                fams = ['QF', 'QD']
        elif opticsparam == 'chrom':
            intstrength = 'SL'
            opticsparam = 'Chrom'
            if acc == 'SI':
                fams = ['SFA1', 'SFA2', 'SDA1', 'SDA2', 'SDA3',
                        'SFB1', 'SFB2', 'SDB1', 'SDB2', 'SDB3',
                        'SFP1', 'SFP2', 'SDP1', 'SDP2', 'SDP3']
            else:
                fams = ['SF', 'SD']
        nfam = len(fams)

        self.setStyleSheet("""
                           QGroupBox {
                                font-weight: bold;
                           }
                           * {
                                font-size:20pt;
                           }""")
        self.setWindowTitle(acc+' '+opticsparam+' Correction Parameters')
        self.layout = QGridLayout()

        if acc == 'SI':
            self.label_method = QLabel('<h4>Method</h4>', self,
                                       alignment=Qt.AlignCenter)
            self.layout.addWidget(self.label_method, 1, 1, 1, nfam)

            self.combobox_method = PyDMEnumComboBox(
                parent=self,
                init_channel='ca://'+prefix+acc+'-Glob:AP-'+opticsparam +
                             'Corr:CorrMeth-Sel')
            self.layout.addWidget(self.combobox_method, 2, nfam//2)

            self.pydmlabel_method = PyDMLabel(
                parent=self,
                init_channel='ca://'+prefix+acc+'-Glob:AP-'+opticsparam +
                             'Corr:CorrMeth-Sts')
            self.pydmlabel_method.setSizePolicy(
                QSzPlcy.Fixed, QSzPlcy.Preferred)
            self.pydmlabel_method.setFixedWidth(180)
            self.pydmlabel_method.setFrameShape(QFrame.Box)
            self.pydmlabel_method.setFrameShadow(QFrame.Raised)
            self.layout.addWidget(self.pydmlabel_method, 2, nfam//2+1)

            self.layout.addItem(
                QSpacerItem(20, 10, QSzPlcy.Minimum, QSzPlcy.Fixed), 3, 1)

            self.label_sync = QLabel('<h4>Syncronization</h4>',
                                     alignment=Qt.AlignCenter)
            self.layout.addWidget(self.label_sync, 4, 1, 1, nfam)

            self.button_sync = PyDMStateButton(
                parent=self,
                init_channel='ca://'+prefix+acc+'-Glob:AP-'+opticsparam +
                             'Corr:SyncCorr-Sel')
            self.button_sync.shape = 1
            self.button_sync.setFixedHeight(36)
            self.layout.addWidget(self.button_sync, 5, nfam//2)

            self.pydmlabel_sync = PyDMLabel(
                parent=self,
                init_channel='ca://'+prefix+acc+'-Glob:AP-'+opticsparam +
                             'Corr:SyncCorr-Sts')
            self.pydmlabel_sync.setSizePolicy(QSzPlcy.Fixed, QSzPlcy.Preferred)
            self.pydmlabel_sync.setFixedWidth(180)
            self.pydmlabel_sync.setFrameShape(QFrame.Box)
            self.pydmlabel_sync.setFrameShadow(QFrame.Raised)
            self.pydmlabel_sync.setAlignment(Qt.AlignLeft)
            self.layout.addWidget(self.pydmlabel_sync, 5, nfam//2+1)

            self.layout.addItem(QSpacerItem(
                20, 10, QSzPlcy.Minimum, QSzPlcy.Fixed), 6, 1)

        if opticsparam == 'Tune':
            self.label_corrfactor = QLabel('<h4>Correction Factor (%)</h4>',
                                           self, alignment=Qt.AlignCenter)
            self.layout.addWidget(self.label_corrfactor, 7, 1, 1, nfam)

            self.pydmlinedit_corrfactor = PyDMLineEdit(
                parent=self,
                init_channel='ca://'+prefix+acc+'-Glob:AP-'+opticsparam +
                             'Corr:CorrFactor-SP')
            self.pydmlinedit_corrfactor.setSizePolicy(
                QSzPlcy.Fixed, QSzPlcy.Fixed)
            self.pydmlinedit_corrfactor.setAlignment(Qt.AlignCenter)
            self.pydmlinedit_corrfactor.setMinimumSize(200, 0)
            self.layout.addWidget(self.pydmlinedit_corrfactor, 8, nfam//2)

            self.pydmlabel_corrfactor = PyDMLabel(
                parent=self,
                init_channel='ca://'+prefix+acc+'-Glob:AP-'+opticsparam +
                             'Corr:CorrFactor-RB')
            self.pydmlabel_corrfactor.setSizePolicy(
                QSzPlcy.Fixed, QSzPlcy.Preferred)
            self.pydmlabel_corrfactor.setFixedWidth(180)
            self.pydmlabel_corrfactor.setFrameShape(QFrame.Box)
            self.pydmlabel_corrfactor.setFrameShadow(QFrame.Raised)
            self.pydmlabel_corrfactor.setAlignment(Qt.AlignLeft)
            self.layout.addWidget(self.pydmlabel_corrfactor, 8, nfam//2+1)

            self.layout.addItem(
                QSpacerItem(20, 10, QSzPlcy.Minimum, QSzPlcy.Fixed), 9, 1)

        self.label_configname = QLabel('<h4>Configuration Name</h4>', self,
                                       alignment=Qt.AlignCenter)
        self.layout.addWidget(self.label_configname, 10, 1, 1, nfam)

        self.pydmlinedit_configname = PyDMLineEdit(
            parent=self,
            init_channel='ca://'+prefix+acc+'-Glob:AP-'+opticsparam +
                         'Corr:ConfigName-SP')
        self.pydmlinedit_configname.setSizePolicy(
            QSzPlcy.Fixed, QSzPlcy.Fixed)
        self.pydmlinedit_configname.setAlignment(Qt.AlignCenter)
        self.pydmlinedit_configname.setMinimumSize(200, 0)
        self.layout.addWidget(self.pydmlinedit_configname, 11, nfam//2)

        self.pydmlabel_configname = PyDMLabel(
            parent=self,
            init_channel='ca://'+prefix+acc+'-Glob:AP-'+opticsparam +
                         'Corr:ConfigName-RB')
        self.pydmlabel_configname.setSizePolicy(
            QSzPlcy.Fixed, QSzPlcy.Preferred)
        self.pydmlabel_configname.setFixedWidth(180)
        self.pydmlabel_configname.setFrameShape(QFrame.Box)
        self.pydmlabel_configname.setFrameShadow(QFrame.Raised)
        self.pydmlabel_configname.setAlignment(Qt.AlignLeft)
        self.layout.addWidget(self.pydmlabel_configname, 11, nfam//2+1)

        self.layout.addItem(
            QSpacerItem(20, 10, QSzPlcy.Minimum, QSzPlcy.Fixed), 12, 1)

        self.label_matrix = QLabel('<h4>Matrix</h4>', self,
                                   alignment=Qt.AlignCenter)
        self.layout.addWidget(self.label_matrix, 13, 1, 1, nfam)

        self.table_matrix = PyDMWaveformTable(
            parent=self,
            init_channel='ca://'+prefix+acc+'-Glob:AP-'+opticsparam +
                         'Corr:RespMat-Mon')
        self.table_matrix.setEnabled(False)
        self.table_matrix.setFixedHeight(135)
        self.table_matrix.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        self.table_matrix.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_matrix.setRowCount(2)
        self.table_matrix.setColumnCount(nfam)
        self.table_matrix.rowHeaderLabels = ['  X', '  Y']
        self.table_matrix.columnHeaderLabels = fams
        self.table_matrix.horizontalHeader().setDefaultSectionSize(160)
        self.table_matrix.verticalHeader().setDefaultSectionSize(48)
        self.layout.addWidget(self.table_matrix, 14, 1, 1, nfam)

        self.layout.addItem(
            QSpacerItem(20, 10, QSzPlcy.Minimum, QSzPlcy.Fixed), 15, 1)

        self.label_nomintstrength = QLabel('<h4>Nominal '+intstrength+'s</h4>',
                                           self, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.label_nomintstrength, 16, 1, 1, nfam)

        self.table_nomintstrength = PyDMWaveformTable(
            parent=self,
            init_channel='ca://'+prefix+acc+'-Glob:AP-'+opticsparam +
                         'Corr:Nominal'+intstrength+'-Mon')
        self.table_nomintstrength.setEnabled(False)
        self.table_nomintstrength.setFixedHeight(85)
        self.table_nomintstrength.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        self.table_nomintstrength.setEditTriggers(
            QAbstractItemView.NoEditTriggers)
        self.table_nomintstrength.setSelectionMode(
            QAbstractItemView.ContiguousSelection)
        self.table_nomintstrength.setRowCount(1)
        self.table_nomintstrength.setColumnCount(nfam)
        self.table_nomintstrength.rowHeaderLabels = [intstrength]
        self.table_nomintstrength.columnHeaderLabels = fams
        self.table_nomintstrength.horizontalHeader().setDefaultSectionSize(160)
        self.table_nomintstrength.verticalHeader().setDefaultSectionSize(48)
        self.layout.addWidget(self.table_nomintstrength, 17, 1, 1, nfam)

        self.layout.addItem(
            QSpacerItem(20, 10, QSzPlcy.Minimum, QSzPlcy.Fixed), 18, 1)

        if opticsparam == 'Chrom':
            self.label_nomchrom = QLabel('<h4>Nominal Chrom</h4>', self,
                                         alignment=Qt.AlignCenter)
            self.layout.addWidget(self.label_nomchrom, 19, 1, 1, nfam)

            self.pydmlabel_nomchrom = PyDMLabel(
                parent=self,
                init_channel='ca://'+prefix+acc+'-Glob:AP-'+opticsparam +
                             'Corr:NominalChrom-Mon')
            self.pydmlabel_nomchrom.setMinimumSize(0, 48)
            self.pydmlabel_nomchrom.setFrameShape(QFrame.Box)
            self.pydmlabel_nomchrom.setFrameShadow(QFrame.Raised)
            self.pydmlabel_nomchrom.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(self.pydmlabel_nomchrom, 20, 1, 1, nfam)

        self.centralwidget = QGroupBox('Correction Parameters')
        self.centralwidget.setLayout(self.layout)
        self.resize(nfam*160+70, 700)
        self.setCentralWidget(self.centralwidget)
