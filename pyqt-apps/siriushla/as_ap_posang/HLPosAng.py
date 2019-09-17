#!/usr/bin/env python-sirius

"""HLA as_ap_posang module."""

import os as _os
from qtpy.uic import loadUi as _loadUi
from qtpy.QtWidgets import QGridLayout, QLabel, QGroupBox, QAbstractItemView, \
                           QSizePolicy as QSzPlcy, QSpacerItem, QPushButton, \
                           QHeaderView
from qtpy.QtCore import Qt

from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy.csdevice.posang import Const

from pydm.utilities.macro import substitute_in_file as _substitute_in_file
from pydm.widgets import PyDMWaveformTable, PyDMLabel, PyDMLineEdit

from siriushla import util as _hlautil
from siriushla.widgets import SiriusMainWindow, PyDMLedMultiChannel, \
    SiriusConnectionSignal
from siriushla.as_ps_control.PSDetailWindow import \
    PSDetailWindow as _PSDetailWindow
from siriushla.as_pu_control.PulsedMagnetDetailWindow import \
    PulsedMagnetDetailWindow as _PulsedMagnetDetailWindow
from siriushla.as_ap_configdb import LoadConfigDialog as _LoadConfigDialog


UI_FILE = (_os.path.abspath(_os.path.dirname(__file__))+'/ui_as_ap_posang.ui')


class PosAngCorr(SiriusMainWindow):
    """Main Class."""

    def __init__(self, parent=None, prefix='', tl=None, corrtype='ch-sept'):
        """Class construc."""
        super(PosAngCorr, self).__init__(parent)
        if not prefix:
            self._prefix = _vaca_prefix
        else:
            self._prefix = prefix
        self._tl = tl.upper()
        self.posang_prefix = self._prefix + self._tl + '-Glob:AP-PosAng'
        self._corrtype = corrtype

        self.setObjectName(tl.upper()+'App')
        tmp_file = _substitute_in_file(UI_FILE, {'TRANSPORTLINE': self._tl,
                                                 'PREFIX': self._prefix})
        self.centralwidget = _loadUi(tmp_file)
        self.setCentralWidget(self.centralwidget)
        self.setWindowTitle(self._tl + ' Position and Angle Correction Window')

        correctors = ['', '', '', '']
        if tl == 'ts':
            correctors[0] = Const.TS_CORRH_POSANG[0]
            correctors[1] = Const.TS_CORRH_POSANG[1]
            correctors[2] = Const.TS_CORRV_POSANG[0]
            correctors[3] = Const.TS_CORRV_POSANG[1]
        elif tl == 'tb':
            if corrtype == 'ch-sept':
                CORRCH = Const.TB_CORRH_POSANG_CHSEPT
            else:
                CORRCH = Const.TB_CORRH_POSANG_CHCH
            correctors[0] = CORRCH[0]
            correctors[1] = CORRCH[1]
            correctors[2] = Const.TB_CORRV_POSANG[0]
            correctors[3] = Const.TB_CORRV_POSANG[1]
        self._set_correctors_channels(correctors)

        act_settings = self.menuBar().addAction('Settings')
        _hlautil.connect_window(act_settings, CorrParamsDetailWindow,
                                parent=self, tl=self._tl, prefix=self._prefix)

        self._set_status_labels()

        self.corrtype_led = PyDMLedMultiChannel(
            parent=self,
            channels2values={self.posang_prefix+':CorrType-Cte': corrtype})
        self.centralwidget.hlay_corrtype.addWidget(self.corrtype_led)
        self.corrtype_ch = SiriusConnectionSignal(
            self.posang_prefix+':CorrType-Cte')
        self.corrtype_ch.new_value_signal[str].connect(
            self._set_corrtype_label)

        self.setStyleSheet("""
            PyDMSpinbox{
                min-width: 5em;
            }
            PyDMLabel{
                min-width: 5em;
            }
        """)

    def _set_correctors_channels(self, correctors):
        self.centralwidget.pushButton_CH1.setText(correctors[0])
        _hlautil.connect_window(self.centralwidget.pushButton_CH1,
                                _PSDetailWindow, self, psname=correctors[0])
        self.centralwidget.PyDMLabel_KickRBCH1.channel = (
            self._prefix + correctors[0] + ':Kick-RB')

        self.centralwidget.pushButton_CH2.setText(correctors[1])
        _hlautil.connect_window(self.centralwidget.pushButton_CH2,
                                _PulsedMagnetDetailWindow, self,
                                maname=correctors[1])
        self.centralwidget.PyDMLabel_KickRBCH2.channel = (
            self._prefix + correctors[1] + ':Kick-RB')

        self.centralwidget.pushButton_CV1.setText(correctors[2])
        _hlautil.connect_window(self.centralwidget.pushButton_CV1,
                                _PSDetailWindow, self, psname=correctors[2])
        self.centralwidget.PyDMLabel_KickRBCV1.channel = (
            self._prefix + correctors[2] + ':Kick-RB')

        self.centralwidget.pushButton_CV2.setText(correctors[3])
        _hlautil.connect_window(self.centralwidget.pushButton_CV2,
                                _PSDetailWindow, self, psname=correctors[3])
        self.centralwidget.PyDMLabel_KickRBCV2.channel = (
            self._prefix + correctors[3] + ':Kick-RB')

    def _set_status_labels(self):
        for i in range(4):
            exec('self.centralwidget.label_status{0}.setText('
                 'Const.STATUSLABELS[{0}])'.format(i))

    def _set_corrtype_label(self, corrtype):
        text = 'Controlling ' + self._corrtype
        self.centralwidget.label_corrtype.setText(text)


class CorrParamsDetailWindow(SiriusMainWindow):
    """Correction parameters detail window."""

    def __init__(self, tl, parent=None, prefix=None):
        """Class constructor."""
        super(CorrParamsDetailWindow, self).__init__(parent)
        self._tl = tl
        self._prefix = prefix
        self.setWindowTitle(self._tl +
                            ' Position and Angle Correction Parameters')
        self._setupUi()

    def _setupUi(self):
        label_configname = QLabel('<h4>Configuration Name</h4>', self,
                                  alignment=Qt.AlignCenter)
        self.pydmlinedit_configname = _ConfigLineEdit(
            parent=self,
            init_channel=self._prefix+self._tl+'-Glob:AP-PosAng:ConfigName-SP')
        self.pydmlabel_configname = PyDMLabel(
            parent=self,
            init_channel=self._prefix+self._tl+'-Glob:AP-PosAng:ConfigName-RB')

        label_matrix_X = QLabel('<h4>Matrix X</h4>', self,
                                alignment=Qt.AlignCenter)
        self.table_matrix_X = PyDMWaveformTable(
            parent=self,
            init_channel=self._prefix+self._tl+'-Glob:AP-PosAng:RespMatX-Mon')
        self.table_matrix_X.setObjectName('table_matrix_X')
        self.table_matrix_X.setStyleSheet("""
            #table_matrix_X{
                min-width:20.72em;
                min-height:4.65em; max-height:4.65em;}""")
        self.table_matrix_X.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_matrix_X.setRowCount(2)
        self.table_matrix_X.setColumnCount(2)
        self.table_matrix_X.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.table_matrix_X.horizontalHeader().setVisible(False)
        self.table_matrix_X.verticalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.table_matrix_X.verticalHeader().setVisible(False)
        self.table_matrix_X.setSizePolicy(QSzPlcy.MinimumExpanding,
                                          QSzPlcy.Preferred)

        label_matrix_Y = QLabel('<h4>Matrix Y</h4>', self,
                                alignment=Qt.AlignCenter)
        self.table_matrix_Y = PyDMWaveformTable(
            parent=self,
            init_channel=self._prefix+self._tl+'-Glob:AP-PosAng:RespMatY-Mon')
        self.table_matrix_Y.setObjectName('table_matrix_Y')
        self.table_matrix_Y.setStyleSheet("""
            #table_matrix_Y{
                min-width:20.72em;
                min-height:4.65em; max-height:4.65em;}""")
        self.table_matrix_Y.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_matrix_Y.setRowCount(2)
        self.table_matrix_Y.setColumnCount(2)
        self.table_matrix_Y.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.table_matrix_Y.horizontalHeader().setVisible(False)
        self.table_matrix_Y.verticalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.table_matrix_Y.verticalHeader().setVisible(False)
        self.table_matrix_Y.setSizePolicy(QSzPlcy.MinimumExpanding,
                                          QSzPlcy.Preferred)

        self.bt_apply = QPushButton('Ok', self)
        self.bt_apply.clicked.connect(self.close)

        lay = QGridLayout()
        lay.addItem(
            QSpacerItem(20, 10, QSzPlcy.Minimum, QSzPlcy.Expanding), 0, 1)
        lay.addWidget(label_configname, 1, 1, 1, 2)
        lay.addWidget(self.pydmlinedit_configname, 2, 1)
        lay.addWidget(self.pydmlabel_configname, 2, 2)
        lay.addItem(
            QSpacerItem(20, 10, QSzPlcy.Minimum, QSzPlcy.Expanding), 3, 1)
        lay.addWidget(label_matrix_X, 4, 1, 1, 2)
        lay.addWidget(self.table_matrix_X, 5, 1, 1, 2)
        lay.addItem(
            QSpacerItem(20, 10, QSzPlcy.Minimum, QSzPlcy.Expanding), 6, 1)
        lay.addWidget(label_matrix_Y, 7, 1, 1, 2)
        lay.addWidget(self.table_matrix_Y, 8, 1, 1, 2)
        lay.addItem(
            QSpacerItem(20, 10, QSzPlcy.Minimum, QSzPlcy.Expanding), 9, 1)
        lay.addWidget(self.bt_apply, 10, 2)
        self.centralwidget = QGroupBox('Correction Parameters')
        self.centralwidget.setLayout(lay)
        self.setCentralWidget(self.centralwidget)


class _ConfigLineEdit(PyDMLineEdit):

    def mouseReleaseEvent(self, ev):
        if 'TB' in self.channel:
            config_type = 'tb_posang_respm'
        elif 'TS' in self.channel:
            config_type = 'ts_posang_respm'
        popup = _LoadConfigDialog(config_type)
        popup.configname.connect(self._config_changed)
        popup.exec_()

    def _config_changed(self, configname):
        self.setText(configname)
        self.send_value()
        self.value_changed(configname)
