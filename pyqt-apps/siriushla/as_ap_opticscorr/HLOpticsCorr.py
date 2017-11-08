#!/usr/bin/env python-sirius
"""Booster Optics Correction HLA Module."""

import epics as _epics
from pydm.PyQt.uic import loadUi
from pydm.PyQt.QtGui import QMainWindow, QFileDialog, QPushButton
from pydm.utilities.macro import substitute_in_file as _substitute_in_file
from siriuspy import util as _util
from siriushla import util as _hlautil
from siriushla.as_ma_control.MagnetDetailWindow import MagnetDetailWindow
from siriushla.as_ma_control.MagnetControlWindow import MagnetControlWindow


class OpticsCorrWindow(QMainWindow):
    """Class to include some intelligence in the .ui files."""

    def __init__(self, acc, opticsparam, parent=None, prefix=None):
        """Initialize some widgets."""
        super(OpticsCorrWindow, self).__init__(parent)

        UI_FILE = ('/home/fac_files/lnls-sirius/hla/pyqt-apps/siriushla/'
                   'as_ap_opticscorr/ui_'+acc+'_ap_'+opticsparam+'corr.ui')

        tmp_file = _substitute_in_file(UI_FILE, {'PREFIX': prefix})
        self.centralwidget = loadUi(tmp_file)
        self.setCentralWidget(self.centralwidget)

        if opticsparam == 'tune':
            self.corrMatrix_pv = _epics.PV(
                prefix+acc.upper()+'-Glob:AP-TuneCorr:CorrMat-SP')
            self.nomKL_pv = _epics.PV(
                prefix+acc.upper()+'-Glob:AP-TuneCorr:NominalKL-SP')
            self.statusLabel_pv = _epics.PV(
                prefix+acc.upper()+'-Glob:AP-TuneCorr:Status-Cte')
            self.statusLabel_pv.add_callback(self._setStatusLabels)

        elif opticsparam == 'chrom':
            self.corrMatrix_pv = _epics.PV(
                prefix+acc.upper()+'-Glob:AP-ChromCorr:CorrMat-SP')
            self.nomChrom_pv = _epics.PV(
                prefix+acc.upper()+'-Glob:AP-ChromCorr:NominalChrom-SP')
            self.nomSL_pv = _epics.PV(
                prefix+acc.upper()+'-Glob:AP-ChromCorr:NominalSL-SP')
            self.statusLabel_pv = _epics.PV(
                prefix+acc.upper()+'-Glob:AP-ChromCorr:Status-Cte')
            self.statusLabel_pv.add_callback(self._setStatusLabels)

        self.acc = acc
        self.opticsparam = opticsparam

        self.centralwidget.pushButton_getCorrParams.clicked.connect(
            self._getCorrParams)
        for button in self.centralwidget.findChildren(QPushButton):
            if 'MADetail' in button.objectName():
                ma = button.text()
                _hlautil.connect_window(button, MagnetDetailWindow, self,
                                        maname=ma)
            elif 'openMA' in button.objectName():
                acc = self.acc.upper()
                _hlautil.connect_window(button, MagnetControlWindow, self,
                                        section=acc, device="dipole")

    def _getCorrParams(self):
        fn, _ = QFileDialog.getOpenFileName(
            self, 'Choose Correction Parameters...', None,
            'Correction Parameters Files (*.' +
            self.acc + self.opticsparam + ')')

        if fn:
            f = open(fn, 'r')
            text = f.read()
            f.close()
            m, _ = _util.read_text_data(text)

            if self.opticsparam == 'chrom':
                if self.acc == 'bo':
                    fams = ['SF', 'SD']
                elif self.acc == 'si':
                    fams = ['SFA1', 'SFA2', 'SDA1', 'SDA2', 'SDA3',
                            'SFB1', 'SFB2', 'SDB1', 'SDB2', 'SDB3',
                            'SFP1', 'SFP2', 'SDP1', 'SDP2', 'SDP3']

                nomchrom = [0, 0]
                nomchrom[0] = float(m[0][0])
                nomchrom[1] = float(m[0][1])

                chrom_corrmat = 2*len(fams)*[0]
                index = 0
                for coordinate in [1, 2]:  # Read in C-like format
                    for fam in range(len(fams)):
                        chrom_corrmat[index] = float(m[coordinate][fam])
                        index += 1

                nomsl = len(fams)*[0]
                for fam in fams:
                    fam_index = fams.index(fam)
                    nomsl[fam_index] = float(m[3][fam_index])

                self.corrMatrix_pv.put(chrom_corrmat)
                self.nomChrom_pv.put(nomchrom)
                self.nomSL_pv.put(nomsl)

            else:  # self.opticsparam = 'tune':
                if self.acc == 'bo':
                    fams = ['QF', 'QD']
                elif self.acc == 'si':
                    fams = ['QFA', 'QDA',
                            'QFB', 'QDB1', 'QDB2',
                            'QFP', 'QDP1', 'QDP2']

                    nomkl = len(fams)*[0]
                    for fam in fams:
                        fam_index = fams.index(fam)
                        nomkl[fam_index] = float(m[2][fam_index])
                    self.nomKL_pv.put(nomkl)

                tune_corrmat = 2*len(fams)*[0]
                index = 0
                for coordinate in [0, 1]:  # Read in C-like format
                    for fam in range(len(fams)):
                        tune_corrmat[index] = float(m[coordinate][fam])
                        index += 1
                self.corrMatrix_pv.put(tune_corrmat)

    def _setStatusLabels(self, value, **kws):
        labels = value
        for i in range(5):
            exec('self.centralwidget.label_status{0}.setText'
                 '(labels[{0}])'.format(i))

    def closeEvent(self, event):
        """Reimplement closeEvent to close Epics PVs connections."""
        self.corrMatrix_pv.disconnect()
        self.corrMatrix_pv = None
        self.statusLabel_pv.disconnect()
        self.statusLabel_pv = None
        if self.opticsparam == 'chrom':
            self.nomSL_pv.disconnect()
            self.nomSL_pv = None
            self.nomChrom_pv.disconnect()
            self.nomChrom_pv = None
        elif self.opticsparam == 'tune':
            self.nomKL_pv.disconnect()
            self.nomKL_pv = None
        super().closeEvent(event)
