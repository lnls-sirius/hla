#!/usr/bin/env python-sirius
"""Booster Optics Correction HLA Module."""

import epics as _epics
from pydm.PyQt.uic import loadUi
from pydm.PyQt import QtCore
from pydm.PyQt.QtGui import (QPushButton, QGridLayout, QLabel, QSizePolicy,
                             QFrame, QSpacerItem, QAbstractItemView, QGroupBox)
from pydm.widgets import (PyDMEnumComboBox, PyDMLabel, PyDMLineEdit,
                          PyDMWaveformTable)
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
            self.label_method = QLabel()
            self.label_method.setText("Method")
            self.label_method.setStyleSheet("font-weight:bold;")
            self.label_method.setAlignment(QtCore.Qt.AlignCenter)
            self.layout.addWidget(self.label_method, 1, 1, 1, nfam)

            self.combobox_method = PyDMEnumComboBox()
            self.combobox_method.setProperty(
                "channel",
                "ca://"+prefix+acc+"-Glob:AP-"+opticsparam+"Corr:CorrMeth-Sel")
            self.layout.addWidget(self.combobox_method, 2, nfam//2, 1, 1)

            self.pydmlabel_method = PyDMLabel()
            sizePolicy = QSizePolicy(
                QSizePolicy.Fixed, QSizePolicy.Preferred)
            self.pydmlabel_method.setSizePolicy(sizePolicy)
            self.pydmlabel_method.setMinimumSize(QtCore.QSize(180, 0))
            self.pydmlabel_method.setMaximumSize(QtCore.QSize(180, 16777215))
            self.pydmlabel_method.setFrameShape(QFrame.Box)
            self.pydmlabel_method.setFrameShadow(QFrame.Raised)
            self.pydmlabel_method.setProperty(
                "channel",
                "ca://"+prefix+acc+"-Glob:AP-"+opticsparam+"Corr:CorrMeth-Sts")
            self.layout.addWidget(self.pydmlabel_method, 2, nfam//2+1, 1, 1)

            spacer0 = QSpacerItem(
                20, 10,
                QSizePolicy.Minimum, QSizePolicy.Fixed)
            self.layout.addItem(spacer0, 3, 1, 1, 1)

            self.label_sync = QLabel()
            self.label_sync.setText("Syncronization")
            self.label_sync.setStyleSheet("font-weight:bold;")
            self.label_sync.setAlignment(QtCore.Qt.AlignCenter)
            self.layout.addWidget(self.label_sync, 4, 1, 1, nfam)

            self.button_sync = PyDMStateButton()
            self.button_sync.setMinimumSize(QtCore.QSize(0, 36))
            self.button_sync.setMaximumSize(QtCore.QSize(16777215, 36))
            self.button_sync.setProperty("shape", PyDMStateButton.Rounded)
            self.button_sync.setProperty(
                "channel",
                "ca://"+prefix+acc+"-Glob:AP-"+opticsparam+"Corr:SyncCorr-Sel")
            self.layout.addWidget(self.button_sync, 5, nfam//2, 1, 1)

            self.pydmlabel_sync = PyDMLabel()
            sizePolicy = QSizePolicy(
                QSizePolicy.Fixed, QSizePolicy.Preferred)
            self.pydmlabel_sync.setSizePolicy(sizePolicy)
            self.pydmlabel_sync.setMinimumSize(QtCore.QSize(180, 0))
            self.pydmlabel_sync.setMaximumSize(QtCore.QSize(180, 16777215))
            self.pydmlabel_sync.setFrameShape(QFrame.Box)
            self.pydmlabel_sync.setFrameShadow(QFrame.Raised)
            self.pydmlabel_sync.setAlignment(QtCore.Qt.AlignLeft)
            self.pydmlabel_sync.setProperty(
                "channel",
                "ca://"+prefix+acc+"-Glob:AP-"+opticsparam+"Corr:SyncCorr-Sts")
            self.layout.addWidget(self.pydmlabel_sync, 5, nfam//2+1, 1, 1)

            spacer1 = QSpacerItem(
                20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
            self.layout.addItem(spacer1, 6, 1, 1, 1)

        if opticsparam == 'Tune':
            self.label_corrfactor = QLabel()
            self.label_corrfactor.setText("Correction Factor (%)")
            self.label_corrfactor.setStyleSheet("font-weight:bold;")
            self.label_corrfactor.setAlignment(QtCore.Qt.AlignCenter)
            self.layout.addWidget(self.label_corrfactor, 7, 1, 1, nfam)

            self.pydmlinedit_corrfactor = PyDMLineEdit()
            sizePolicy = QSizePolicy(
                QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.pydmlinedit_corrfactor.setSizePolicy(sizePolicy)
            self.pydmlinedit_corrfactor.setAlignment(QtCore.Qt.AlignCenter)
            self.pydmlinedit_corrfactor.setMinimumSize(QtCore.QSize(200, 0))
            self.pydmlinedit_corrfactor.setProperty(
                "channel",
                "ca://" + prefix + acc + "-Glob:AP-" + opticsparam +
                "Corr:CorrFactor-SP")
            self.layout.addWidget(self.pydmlinedit_corrfactor,
                                  8, nfam//2, 1, 1)

            self.pydmlabel_corrfactor = PyDMLabel()
            sizePolicy = QSizePolicy(
                QSizePolicy.Fixed, QSizePolicy.Preferred)
            self.pydmlabel_corrfactor.setSizePolicy(sizePolicy)
            self.pydmlabel_corrfactor.setMinimumSize(QtCore.QSize(180, 0))
            self.pydmlabel_corrfactor.setMaximumSize(
                QtCore.QSize(180, 16777215))
            self.pydmlabel_corrfactor.setFrameShape(QFrame.Box)
            self.pydmlabel_corrfactor.setFrameShadow(QFrame.Raised)
            self.pydmlabel_corrfactor.setAlignment(QtCore.Qt.AlignLeft)
            self.pydmlabel_corrfactor.setProperty(
                "channel",
                "ca://" + prefix + acc + "-Glob:AP-" + opticsparam +
                "Corr:CorrFactor-RB")
            self.layout.addWidget(self.pydmlabel_corrfactor,
                                  8, nfam//2+1, 1, 1)

            spacer2 = QSpacerItem(
                20, 10,
                QSizePolicy.Minimum, QSizePolicy.Fixed)
            self.layout.addItem(spacer2, 9, 1, 1, 1)

        self.label_configname = QLabel()
        self.label_configname.setText("Configuration Name")
        self.label_configname.setStyleSheet("font-weight:bold;")
        self.label_configname.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.label_configname, 10, 1, 1, nfam)

        self.pydmlinedit_configname = PyDMLineEdit()
        sizePolicy = QSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.pydmlinedit_configname.setSizePolicy(sizePolicy)
        self.pydmlinedit_configname.setAlignment(QtCore.Qt.AlignCenter)
        self.pydmlinedit_configname.setMinimumSize(QtCore.QSize(200, 0))
        self.pydmlinedit_configname.setProperty(
            "channel",
            "ca://" + prefix + acc + "-Glob:AP-" + opticsparam +
            "Corr:ConfigName-SP")
        self.layout.addWidget(self.pydmlinedit_configname,
                              11, nfam//2, 1, 1)

        self.pydmlabel_configname = PyDMLabel()
        sizePolicy = QSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.pydmlabel_configname.setSizePolicy(sizePolicy)
        self.pydmlabel_configname.setMinimumSize(QtCore.QSize(180, 0))
        self.pydmlabel_configname.setMaximumSize(
            QtCore.QSize(180, 16777215))
        self.pydmlabel_configname.setFrameShape(QFrame.Box)
        self.pydmlabel_configname.setFrameShadow(QFrame.Raised)
        self.pydmlabel_configname.setAlignment(QtCore.Qt.AlignLeft)
        self.pydmlabel_configname.setProperty(
            "channel",
            "ca://" + prefix + acc + "-Glob:AP-" + opticsparam +
            "Corr:ConfigName-RB")
        self.layout.addWidget(self.pydmlabel_configname,
                              11, nfam//2+1, 1, 1)

        spacer2 = QSpacerItem(
            20, 10,
            QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout.addItem(spacer2, 12, 1, 1, 1)

        self.label_matrix = QLabel()
        self.label_matrix.setText("Matrix")
        self.label_matrix.setStyleSheet("font-weight:bold;")
        self.label_matrix.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.label_matrix, 13, 1, 1, nfam)

        self.table_matrix = PyDMWaveformTable()
        self.table_matrix.setEnabled(False)
        self.table_matrix.setMinimumSize(QtCore.QSize(0, 135))
        self.table_matrix.setMaximumSize(QtCore.QSize(16777215, 135))
        self.table_matrix.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.table_matrix.setEditTriggers(
            QAbstractItemView.NoEditTriggers)
        self.table_matrix.setSelectionMode(
            QAbstractItemView.ContiguousSelection)
        self.table_matrix.setRowCount(2)
        self.table_matrix.setColumnCount(nfam)
        self.table_matrix.setProperty("rowHeaderLabels", ['  X', '  Y'])
        self.table_matrix.setProperty("columnHeaderLabels", fams)
        self.table_matrix.horizontalHeader().setDefaultSectionSize(160)
        self.table_matrix.verticalHeader().setDefaultSectionSize(48)
        self.table_matrix.setProperty(
            "channel",
            "ca://"+prefix+acc+"-Glob:AP-"+opticsparam+"Corr:RespMat-Mon")
        self.layout.addWidget(self.table_matrix, 14, 1, 1, nfam)

        spacer3 = QSpacerItem(
            20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout.addItem(spacer3, 15, 1, 1, 1)

        self.label_nomintstrength = QLabel()
        self.label_nomintstrength.setText("Nominal "+intstrength+"s")
        self.label_nomintstrength.setStyleSheet("font-weight:bold;")
        self.label_nomintstrength.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.label_nomintstrength, 16, 1, 1, nfam)

        self.table_nomintstrength = PyDMWaveformTable()
        self.table_nomintstrength.setEnabled(False)
        self.table_nomintstrength.setMinimumSize(QtCore.QSize(0, 85))
        self.table_nomintstrength.setMaximumSize(QtCore.QSize(16777215, 85))
        self.table_nomintstrength.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.table_nomintstrength.setEditTriggers(
            QAbstractItemView.NoEditTriggers)
        self.table_nomintstrength.setSelectionMode(
            QAbstractItemView.ContiguousSelection)
        self.table_nomintstrength.setRowCount(1)
        self.table_nomintstrength.setColumnCount(nfam)
        self.table_nomintstrength.setProperty("rowHeaderLabels", [intstrength])
        self.table_nomintstrength.setProperty("columnHeaderLabels", fams)
        self.table_nomintstrength.horizontalHeader().setDefaultSectionSize(160)
        self.table_nomintstrength.verticalHeader().setDefaultSectionSize(48)
        self.table_nomintstrength.verticalHeader().setMinimumSectionSize(0)
        self.table_nomintstrength.setProperty(
            "channel",
            "ca://" + prefix + acc + "-Glob:AP-" + opticsparam +
            "Corr:Nominal" + intstrength + "-Mon")
        self.layout.addWidget(self.table_nomintstrength, 17, 1, 1, nfam)

        spacer4 = QSpacerItem(
            20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout.addItem(spacer4, 18, 1, 1, 1)

        if opticsparam == 'Chrom':
            self.label_nomchrom = QLabel()
            self.label_nomchrom.setText("Nominal Chrom")
            self.label_nomchrom.setStyleSheet("font-weight: bold;")
            self.label_nomchrom.setAlignment(QtCore.Qt.AlignCenter)
            self.layout.addWidget(self.label_nomchrom, 19, 1, 1, nfam)

            self.pydmlabel_nomchrom = PyDMLabel()
            self.pydmlabel_nomchrom.setMinimumSize(QtCore.QSize(0, 48))
            self.pydmlabel_nomchrom.setFrameShape(QFrame.Box)
            self.pydmlabel_nomchrom.setFrameShadow(QFrame.Raised)
            self.pydmlabel_nomchrom.setAlignment(QtCore.Qt.AlignCenter)
            self.pydmlabel_nomchrom.setProperty(
                "channel",
                "ca://" + prefix + acc + "-Glob:AP-" + opticsparam +
                "Corr:NominalChrom-Mon")
            self.layout.addWidget(self.pydmlabel_nomchrom, 20, 1, 1, nfam)

        self.centralwidget = QGroupBox()
        self.centralwidget.setTitle("Correction Parameters")
        self.centralwidget.setLayout(self.layout)
        self.resize(nfam*160+70, 700)
        self.setCentralWidget(self.centralwidget)
