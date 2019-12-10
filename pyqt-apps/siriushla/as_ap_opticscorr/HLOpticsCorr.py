#!/usr/bin/env python-sirius
"""Booster Optics Correction HLA Module."""

import os as _os
from qtpy.uic import loadUi
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QPushButton, QGridLayout, QLabel, QSpacerItem, \
    QAbstractItemView, QGroupBox, QSizePolicy as QSzPlcy, QHeaderView
from pydm.widgets import PyDMEnumComboBox, PyDMLabel, PyDMLineEdit, \
    PyDMWaveformTable
from pydm.utilities.macro import substitute_in_file as _substitute_in_file
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy.csdevice.opticscorr import Const as _Const
from siriushla import util as _hlautil
from siriushla.widgets import PyDMStateButton
from siriushla.widgets.windows import SiriusMainWindow
from siriushla.as_ps_control import PSDetailWindow as _PSDetailWindow
from siriushla.as_ap_configdb import LoadConfigDialog as _LoadConfigDialog


class OpticsCorrWindow(SiriusMainWindow):
    """Class to include some intelligence in the .ui files."""

    def __init__(self, acc, opticsparam, parent=None, prefix=''):
        """Initialize some widgets."""
        super(OpticsCorrWindow, self).__init__(parent)
        self.opticsparam = opticsparam
        self._acc = acc.upper()
        if not prefix:
            prefix = _vaca_prefix

        UI_FILE = (_os.path.abspath(_os.path.dirname(__file__)) + '/ui_' +
                   acc + '_ap_' + opticsparam + 'corr.ui')
        tmp_file = _substitute_in_file(UI_FILE, {'PREFIX': prefix})
        self.centralwidget = loadUi(tmp_file)
        self.setObjectName(acc.upper()+'App')
        self.centralwidget.setObjectName(acc.upper()+'App')
        self.setCentralWidget(self.centralwidget)
        self.setWindowTitle(
            self._acc + ' Tune' if opticsparam == 'tune' else ' Chromaticity' +
            ' Correction')

        for button in self.centralwidget.findChildren(QPushButton):
            if 'PSDetail' in button.objectName():
                ma = button.text()
                _hlautil.connect_window(button, _PSDetailWindow, self,
                                        psname=ma)

        act_settings = self.menuBar().addAction('Settings')
        _hlautil.connect_window(act_settings, _CorrParamsDetailWindow,
                                parent=self, acc=self._acc,
                                opticsparam=opticsparam, prefix=prefix)

        self._setStatusLabels()

    def _setStatusLabels(self):
        status_bits = 5 if (self.opticsparam == 'tune' and
                            self._acc == 'SI') else 4
        for i in range(status_bits):
            exec('self.centralwidget.label_status{0}.setText'
                 '(_Const.STATUS_LABELS[{0}])'.format(i))


class _CorrParamsDetailWindow(SiriusMainWindow):
    """Correction parameters detail window."""

    def __init__(self, acc, opticsparam, parent=None, prefix=None):
        """Class constructor."""
        super(_CorrParamsDetailWindow, self).__init__(parent)
        self._acc = acc
        self._opticsparam = opticsparam.title()
        self.setWindowTitle(acc+' '+self._opticsparam+' Correction Parameters')
        self._prefix = prefix

        if opticsparam == 'tune':
            self._intstrength = 'KL'
            self._fams = list(_Const.SI_QFAMS_TUNECORR) if acc == 'SI' \
                else list(_Const.BO_QFAMS_TUNECORR)
        elif opticsparam == 'chrom':
            self._intstrength = 'SL'
            self._fams = list(_Const.SI_SFAMS_CHROMCORR) if acc == 'SI' \
                else list(_Const.BO_SFAMS_CHROMCORR)
        self._nfam = len(self._fams)

        self._setupUi()

    def _setupUi(self):
        ioc_prefix = self._prefix+self._acc+'-Glob:AP-' + \
                          self._opticsparam+'Corr:'
        lay = QGridLayout()

        if self._acc == 'SI':
            label_method = QLabel('<h4>Method</h4>', self,
                                  alignment=Qt.AlignCenter)
            self.combobox_method = PyDMEnumComboBox(
                parent=self, init_channel=ioc_prefix+'CorrMeth-Sel')
            self.combobox_method.setStyleSheet(
                """min-width:10em; max-width:10em;""")

            self.pydmlabel_method = PyDMLabel(
                parent=self, init_channel=ioc_prefix+'CorrMeth-Sts')

            lay.addWidget(label_method, 1, 1, 1, self._nfam)
            lay.addWidget(self.combobox_method, 2, self._nfam//2)
            lay.addWidget(self.pydmlabel_method, 2, self._nfam//2+1)
            lay.addItem(
                QSpacerItem(20, 10, QSzPlcy.Minimum, QSzPlcy.Fixed), 3, 1)

            if self._opticsparam == 'Tune':
                label_sync = QLabel('<h4>Syncronization</h4>',
                                    alignment=Qt.AlignCenter)
                self.button_sync = PyDMStateButton(
                    parent=self, init_channel=ioc_prefix+'SyncCorr-Sel')
                self.button_sync.shape = 1
                self.pydmlabel_sync = PyDMLabel(
                    parent=self, init_channel=ioc_prefix+'SyncCorr-Sts')

                lay.addWidget(label_sync, 4, 1, 1, self._nfam)
                lay.addWidget(self.button_sync, 5, self._nfam//2)
                lay.addWidget(self.pydmlabel_sync, 5, self._nfam//2+1)
                lay.addItem(
                    QSpacerItem(20, 10, QSzPlcy.Minimum, QSzPlcy.Fixed), 6, 1)

        label_configname = QLabel('<h4>Configuration Name</h4>', self,
                                  alignment=Qt.AlignCenter)
        self.pydmlinedit_configname = _ConfigLineEdit(
            parent=self, init_channel=ioc_prefix+'ConfigName-SP')
        self.pydmlinedit_configname.setStyleSheet(
            """min-width:10em; max-width:10em;""")

        self.pydmlabel_configname = PyDMLabel(
            parent=self, init_channel=ioc_prefix+'ConfigName-RB')

        lay.addWidget(label_configname, 10, 1, 1, self._nfam)
        lay.addWidget(self.pydmlinedit_configname, 11, self._nfam//2)
        lay.addWidget(self.pydmlabel_configname, 11, self._nfam//2+1)
        lay.addItem(
            QSpacerItem(20, 10, QSzPlcy.Minimum, QSzPlcy.Fixed), 12, 1)

        label_matrix = QLabel('<h4>Matrix</h4>', self,
                              alignment=Qt.AlignCenter)
        self.table_matrix = PyDMWaveformTable(
            parent=self, init_channel=ioc_prefix+'RespMat-Mon')
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
                min-width:valueem;
                min-height:5.84em;\nmax-height:5.84em;
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
        self.table_nomintstrength = PyDMWaveformTable(
            parent=self,
            init_channel=ioc_prefix+'Nominal'+self._intstrength+'-Mon')
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
                min-width:valueem;
                min-height:3.67em;\nmax-height:3.67em;
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
            self.pydmlabel_nomchrom = PyDMLabel(
                parent=self, init_channel=ioc_prefix+'NominalChrom-Mon')
            self.pydmlabel_nomchrom.setAlignment(Qt.AlignCenter)

            lay.addWidget(label_nomchrom, 19, 1, 1, self._nfam)
            lay.addWidget(self.pydmlabel_nomchrom, 20, 1, 1, self._nfam)

        self.bt_apply = QPushButton('Ok', self)
        self.bt_apply.clicked.connect(self.close)
        lay.addWidget(self.bt_apply, 21, self._nfam)

        self.centralwidget = QGroupBox('Correction Parameters')
        self.centralwidget.setLayout(lay)
        self.setCentralWidget(self.centralwidget)


class _ConfigLineEdit(PyDMLineEdit):

    def mouseReleaseEvent(self, ev):
        if 'SI' in self.channel and 'Tune' in self.channel:
            config_type = 'si_tunecorr_params'
        elif 'BO' in self.channel and 'Tune' in self.channel:
            config_type = 'bo_tunecorr_params'
        elif 'SI' in self.channel and 'Chrom' in self.channel:
            config_type = 'si_chromcorr_params'
        elif 'BO' in self.channel and 'Chrom' in self.channel:
            config_type = 'bo_chromcorr_params'
        popup = _LoadConfigDialog(config_type)
        popup.configname.connect(self._config_changed)
        popup.exec_()

    def _config_changed(self, configname):
        self.setText(configname)
        self.send_value()
        self.value_changed(configname)
