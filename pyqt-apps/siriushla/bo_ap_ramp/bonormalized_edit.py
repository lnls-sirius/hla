"""Booster Ramp Control HLA: Optics Adjust Module."""

from copy import deepcopy as _dcopy
from functools import partial as _part

import numpy as _np

from qtpy.QtCore import Qt, Signal, Slot
from qtpy.QtGui import QKeySequence
from qtpy.QtWidgets import QWidget, QGroupBox, QPushButton, QLabel, \
    QGridLayout, QScrollArea, QFormLayout, QCheckBox, QMenuBar, \
    QUndoStack, QUndoCommand, QHBoxLayout, QMessageBox
import qtawesome as qta

from siriuspy.search import MASearch as _MASearch, PSSearch as _PSSearch
from siriuspy.ramp import ramp
from siriuspy.opticscorr.opticscorr import BOTuneCorr, BOChromCorr
from siriuspy.clientconfigdb import ConfigDBException as _ConfigDBException
from siriuspy.namesys import SiriusPVName

from siriushla.widgets import SiriusMainWindow, QDoubleSpinBoxPlus
from siriushla.as_ap_configdb import SaveConfigDialog as _SaveConfigDialog
from siriushla.bo_ap_ramp.auxiliary_dialogs import \
    ShowCorrectorKicks as _ShowCorrectorKicks


_flag_stack_next_command = True
_flag_stacking = False


class BONormEdit(SiriusMainWindow):
    """Widget to perform optics adjust in normalized configurations."""

    normConfigChanged = Signal(float, dict)

    def __init__(self, parent=None, prefix='', ramp_config=None,
                 norm_config=None, time=None, energy=None,
                 magnets=dict(), conn_sofb=None,
                 tunecorr_configname=None, chromcorr_configname=None):
        """Initialize object."""
        super().__init__(parent)
        self.setWindowTitle('Edit Normalized Configuration')
        self.setObjectName('BOApp')
        self.prefix = prefix
        self.ramp_config = ramp_config
        self.norm_config = _dcopy(norm_config)
        self.time = time
        self.energy = energy

        self._aux_magnets = magnets
        self._conn_sofb = conn_sofb
        self._tunecorr = BOTuneCorr(tunecorr_configname)
        self._chromcorr = BOChromCorr(chromcorr_configname)

        self._reference = _dcopy(norm_config)
        self._currChrom = self._estimateChrom(use_ref=True)
        self._deltas = {
            'kicks': dict(),
            'factorH': 0.0,
            'factorV': 0.0,
            'tuneX': 0.0,
            'tuneY': 0.0,
            'chromX': self._currChrom[0],
            'chromY': self._currChrom[1],
        }
        self._setupUi()
        self._setupMenu()
        self.verifySync()

    # ---------- setup/build layout ----------

    def _setupUi(self):
        self.label_description = QLabel(
            '<h2>'+self.norm_config['label']+'</h2>', self)
        self.label_description.setAlignment(Qt.AlignCenter)
        self.label_time = QLabel('<h2>T = '+str(self.time)+'ms</h2>', self)
        self.label_time.setAlignment(Qt.AlignCenter)

        self.strengths = self._setupStrengthWidget()
        self.orbit = self._setupOrbitWidget()
        self.tune = self._setupTuneWidget()
        self.chrom = self._setupChromWidget()

        self.bt_apply = QPushButton(qta.icon('fa5s.angle-right'), '', self)
        self.bt_apply.setToolTip('Apply Changes to Machine')
        self.bt_apply.setStyleSheet('icon-size: 30px 30px;')
        self.bt_apply.clicked.connect(self._updateRampConfig)

        cw = QWidget()
        lay = QGridLayout()
        lay.setVerticalSpacing(10)
        lay.setHorizontalSpacing(10)
        lay.addWidget(self.label_description, 0, 0, 1, 2)
        lay.addWidget(self.label_time, 1, 0, 1, 2)
        lay.addWidget(self.strengths, 2, 0, 4, 1)
        lay.addWidget(self.orbit, 2, 1)
        lay.addWidget(self.tune, 3, 1)
        lay.addWidget(self.chrom, 4, 1)
        lay.addWidget(self.bt_apply, 5, 1)
        lay.setColumnStretch(0, 2)
        lay.setColumnStretch(1, 2)
        lay.setRowStretch(0, 2)
        lay.setRowStretch(1, 2)
        lay.setRowStretch(2, 8)
        lay.setRowStretch(3, 8)
        lay.setRowStretch(4, 8)
        lay.setRowStretch(5, 1)
        cw.setLayout(lay)

        cw.setStyleSheet("""
            QGroupBox::title{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 2px 0 2px;}""")
        cw.setFocusPolicy(Qt.StrongFocus)
        self.setCentralWidget(cw)

    def _setupMenu(self):
        self.menubar = QMenuBar(self)
        self.layout().setMenuBar(self.menubar)
        self.menu = self.menubar.addMenu('Options')
        self.act_saveas = self.menu.addAction('Save as...')
        self.act_saveas.triggered.connect(self._showSaveAsPopup)

        self._undo_stack = QUndoStack(self)
        self.act_undo = self._undo_stack.createUndoAction(self, 'Undo')
        self.act_undo.setShortcut(QKeySequence.Undo)
        self.menu.addAction(self.act_undo)
        self.act_redo = self._undo_stack.createRedoAction(self, 'Redo')
        self.act_redo.setShortcut(QKeySequence.Redo)
        self.menu.addAction(self.act_redo)

    def _setupStrengthWidget(self):
        scrollarea = QScrollArea()
        self.nconfig_data = QWidget()
        flay_configdata = QFormLayout()
        psnames = self._get_PSNames()
        self._map_psnames2wigdets = dict()
        for ps in psnames:
            ps = SiriusPVName(ps)
            if ps in ramp.BoosterRamp.PSNAME_DIPOLES:
                ps_value = QLabel(str(self.norm_config[ps])+' GeV', self)
                flay_configdata.addRow(QLabel(ps + ': ', self), ps_value)
            else:
                ps_value = QDoubleSpinBoxPlus(self.nconfig_data)
                ps_value.setDecimals(6)
                ps_value.setMinimum(-10000)
                ps_value.setMaximum(10000)
                ps_value.setValue(self.norm_config[ps])
                ps_value.valueChanged.connect(self._handleStrenghtsSet)

                if ps.dev in {'QD', 'QF', 'QS'}:
                    unit_txt = '1/m'
                elif ps.dev in {'SD', 'SF'}:
                    unit_txt = '1/m²'
                else:
                    unit_txt = 'urad'
                label_unit = QLabel(unit_txt, self)
                label_unit.setStyleSheet("min-width:2.5em; max-width:2.5em;")
                hb = QHBoxLayout()
                hb.addWidget(ps_value)
                hb.addWidget(label_unit)

                flay_configdata.addRow(QLabel(ps + ': ', self), hb)

            ps_value.setObjectName(ps)
            ps_value.setStyleSheet("min-height:1.29em; max-height:1.29em;")
            self._map_psnames2wigdets[ps] = ps_value

        self.nconfig_data.setObjectName('data')
        self.nconfig_data.setStyleSheet("""
            #data{background-color: transparent;}""")
        self.nconfig_data.setLayout(flay_configdata)
        scrollarea.setWidget(self.nconfig_data)

        self.cb_checklims = QCheckBox('Set limits according to energy', self)
        self.cb_checklims.setChecked(False)
        self.cb_checklims.stateChanged.connect(self._handleStrengtsLimits)

        self.bt_graph = QPushButton(qta.icon('mdi.chart-line'), '', self)
        self.bt_graph.clicked.connect(self._show_kicks_graph)

        gbox = QGroupBox()
        gbox.setObjectName('strengths')
        gbox.setStyleSheet('#strengths{min-width:20em;}')
        glay = QGridLayout()
        glay.addWidget(scrollarea, 0, 0, 1, 2)
        glay.addWidget(self.cb_checklims, 1, 0, alignment=Qt.AlignLeft)
        glay.addWidget(self.bt_graph, 1, 1, alignment=Qt.AlignRight)
        gbox.setLayout(glay)
        return gbox

    def _setupOrbitWidget(self):
        self.bt_get_kicks = QPushButton('Get Kicks from TOCA', self)
        self.bt_get_kicks.clicked.connect(self._handleGetKicksFromTOCA)

        label_correctH = QLabel('Correct H', self,
                                alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.sb_correctH = QDoubleSpinBoxPlus(self)
        self.sb_correctH.setValue(self._deltas['factorH'])
        self.sb_correctH.setDecimals(1)
        self.sb_correctH.setMinimum(-10000)
        self.sb_correctH.setMaximum(10000)
        self.sb_correctH.setSingleStep(0.1)
        self.sb_correctH.setObjectName('factorH')
        self.sb_correctH.editingFinished.connect(self._handleCorrFactorsSet)
        labelH = QLabel('%', self)

        label_correctV = QLabel('Correct V', self,
                                alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.sb_correctV = QDoubleSpinBoxPlus(self)
        self.sb_correctV.setValue(self._deltas['factorV'])
        self.sb_correctV.setDecimals(1)
        self.sb_correctV.setMinimum(-10000)
        self.sb_correctV.setMaximum(10000)
        self.sb_correctV.setSingleStep(0.1)
        self.sb_correctV.setObjectName('factorV')
        self.sb_correctV.editingFinished.connect(self._handleCorrFactorsSet)
        labelV = QLabel('%', self)

        self.bt_update_ref_orbit = QPushButton('Update reference', self)
        self.bt_update_ref_orbit.clicked.connect(
            _part(self._updateReference, 'corrs'))

        gbox = QGroupBox('Orbit', self)
        lay = QGridLayout()
        lay.addWidget(self.bt_get_kicks, 0, 0, 1, 4)
        lay.addWidget(label_correctH, 1, 0)
        lay.addWidget(self.sb_correctH, 1, 2)
        lay.addWidget(labelH, 1, 3)
        lay.addWidget(label_correctV, 2, 0)
        lay.addWidget(self.sb_correctV, 2, 2)
        lay.addWidget(labelV, 2, 3)
        lay.addWidget(self.bt_update_ref_orbit, 3, 2, 1, 2)
        lay.setColumnStretch(0, 16)
        lay.setColumnStretch(1, 1)
        lay.setColumnStretch(2, 14)
        lay.setColumnStretch(3, 2)
        gbox.setLayout(lay)
        return gbox

    def _setupTuneWidget(self):
        for cord in ['X', 'Y']:
            setattr(self, 'label_deltaTune'+cord,
                    QLabel('Δν<sub>'+cord+'</sub>: '))
            lab = getattr(self, 'label_deltaTune'+cord)
            lab.setStyleSheet("min-width:1.55em; max-width:1.55em;")

            setattr(self, 'sb_deltaTune'+cord, QDoubleSpinBoxPlus(self))
            sb = getattr(self, 'sb_deltaTune'+cord)
            sb.setDecimals(6)
            sb.setMinimum(-5)
            sb.setMaximum(5)
            sb.setSingleStep(0.0001)
            sb.setObjectName('tune'+cord)
            sb.editingFinished.connect(self._handleDeltaTuneSet)

        label_KL = QLabel('<h4>ΔKL [1/m]</h4>', self)
        label_KL.setStyleSheet("""min-height:1.55em; max-height:1.55em;
                                  qproperty-alignment: AlignCenter;""")
        self.l_deltaKLQF = QLabel('', self)
        self.l_deltaKLQD = QLabel('', self)

        self.bt_update_ref_deltaKL = QPushButton('Update reference', self)
        self.bt_update_ref_deltaKL.clicked.connect(
            _part(self._updateReference, 'quads'))

        gbox = QGroupBox('Tune', self)
        lay = QGridLayout()
        lay.addWidget(self.label_deltaTuneX, 1, 0)
        lay.addWidget(self.sb_deltaTuneX, 1, 1)
        lay.addWidget(self.label_deltaTuneY, 1, 3)
        lay.addWidget(self.sb_deltaTuneY, 1, 4)
        lay.addWidget(label_KL, 3, 0, 1, 5)
        lay.addWidget(QLabel('QF: '), 4, 0)
        lay.addWidget(self.l_deltaKLQF, 4, 1)
        lay.addWidget(QLabel('QD: '), 4, 3)
        lay.addWidget(self.l_deltaKLQD, 4, 4)
        lay.addWidget(self.bt_update_ref_deltaKL, 6, 3, 1, 2)
        lay.setVerticalSpacing(6)
        lay.setColumnStretch(0, 2)
        lay.setColumnStretch(1, 4)
        lay.setColumnStretch(2, 1)
        lay.setColumnStretch(3, 2)
        lay.setColumnStretch(4, 4)
        lay.setRowStretch(0, 1)
        lay.setRowStretch(1, 2)
        lay.setRowStretch(2, 1)
        lay.setRowStretch(3, 2)
        lay.setRowStretch(4, 2)
        lay.setRowStretch(5, 1)
        lay.setRowStretch(6, 2)
        gbox.setLayout(lay)
        return gbox

    def _setupChromWidget(self):
        for cord in ['X', 'Y']:
            setattr(self, 'label_Chrom'+cord,
                    QLabel('ξ<sub>'+cord+'</sub>: '))
            lab = getattr(self, 'label_Chrom'+cord)
            lab.setStyleSheet("min-width:1.55em; max-width:1.55em;")

            setattr(self, 'sb_Chrom'+cord, QDoubleSpinBoxPlus(self))
            sb = getattr(self, 'sb_Chrom'+cord)
            sb.setDecimals(6)
            sb.setMinimum(-5)
            sb.setMaximum(5)
            sb.setSingleStep(0.0001)
            sb.setObjectName('chrom'+cord)
            sb.setValue(self._deltas['chrom'+cord])
            sb.editingFinished.connect(self._handleChromSet)

        label_SL = QLabel('<h4>ΔSL [1/m<sup>2</sup>]</h4>', self)
        label_SL.setStyleSheet("""min-height:1.55em; max-height:1.55em;
                                  qproperty-alignment: AlignCenter;""")
        self.l_deltaSLSF = QLabel('', self)
        self.l_deltaSLSD = QLabel('', self)

        self.bt_update_ref_deltaSL = QPushButton('Update reference', self)
        self.bt_update_ref_deltaSL.clicked.connect(
            _part(self._updateReference, 'sexts'))

        gbox = QGroupBox('Chromaticity', self)
        lay = QGridLayout()
        lay.addWidget(self.label_ChromX, 1, 0)
        lay.addWidget(self.sb_ChromX, 1, 1)
        lay.addWidget(self.label_ChromY, 1, 3)
        lay.addWidget(self.sb_ChromY, 1, 4)
        lay.addWidget(label_SL, 3, 0, 1, 5)
        lay.addWidget(QLabel('SF: '), 4, 0)
        lay.addWidget(self.l_deltaSLSF, 4, 1)
        lay.addWidget(QLabel('SD: '), 4, 3)
        lay.addWidget(self.l_deltaSLSD, 4, 4)
        lay.addWidget(self.bt_update_ref_deltaSL, 6, 3, 1, 2)
        lay.setVerticalSpacing(6)
        lay.setColumnStretch(0, 2)
        lay.setColumnStretch(1, 4)
        lay.setColumnStretch(2, 1)
        lay.setColumnStretch(3, 2)
        lay.setColumnStretch(4, 4)
        lay.setRowStretch(0, 1)
        lay.setRowStretch(1, 2)
        lay.setRowStretch(2, 1)
        lay.setRowStretch(3, 2)
        lay.setRowStretch(4, 2)
        lay.setRowStretch(5, 1)
        lay.setRowStretch(6, 2)
        gbox.setLayout(lay)
        return gbox

    # ---------- server communication ----------

    def _save(self, name):
        try:
            nconf = ramp.BoosterNormalized()
            nconf.value = self.norm_config
            nconf.save(new_name=name)
        except _ConfigDBException as err:
            QMessageBox.critical(self, 'Error', str(err), QMessageBox.Ok)

    def _showSaveAsPopup(self):
        self._saveAsPopup = _SaveConfigDialog('bo_normalized', self)
        self._saveAsPopup.configname.connect(self._save)
        self._saveAsPopup.open()

    def verifySync(self):
        if self.ramp_config is None:
            return
        if not self.ramp_config.verify_ps_normalized_synchronized(
                self.time, value=self.norm_config):
            self.label_time.setStyleSheet('color: red;')
            self.label_description.setStyleSheet('color: red;')
            self.setToolTip("There are unsaved changes")
        else:
            self.label_time.setStyleSheet('color: black;')
            self.label_description.setStyleSheet('color: black;')
            self.setToolTip("")

    # ---------- strengths ----------

    def _handleStrenghtsSet(self, new_value):
        psname = self.sender().objectName()
        self._stack_command(
            self.sender(), self.norm_config[psname], new_value,
            message='set '+psname+' strength to {}'.format(new_value))
        self.norm_config[psname] = new_value
        self.verifySync()

    def _handleStrengtsLimits(self, state):
        psnames = list(self.norm_config.keys())
        psnames.remove('BO-Fam:PS-B-1')
        psnames.remove('BO-Fam:PS-B-2')
        psnames.remove('label')
        if state:
            for ps in psnames:
                ps_value = self.nconfig_data.findChild(
                    QDoubleSpinBoxPlus, name=ps)
                ma = _MASearch.conv_psname_2_psmaname(ps)
                aux = self._aux_magnets[ma]
                currs = (aux.current_min, aux.current_max)
                lims = aux.conv_current_2_strength(
                    currents=currs, strengths_dipole=self.energy)
                ps_value.setMinimum(min(lims))
                ps_value.setMaximum(max(lims))
        else:
            for ps in psnames:
                ps_value = self.nconfig_data.findChild(
                    QDoubleSpinBoxPlus, name=ps)
                ps_value.setMinimum(-10000)
                ps_value.setMaximum(10000)

    def _updateStrenghtsWidget(self, pstype):
        psnames = self._get_PSNames(pstype)
        wid2change = psnames if psnames else list(self.norm_config.keys())
        for wid in wid2change:
            value = self.norm_config[wid]
            self._map_psnames2wigdets[wid].setValue(value)

    # ---------- orbit ----------

    def _updateCorrKicks(self):
        for psname, dkick in self._deltas['kicks'].items():
            corr_factor = self._deltas['factorV'] if 'CV' in psname \
                else self._deltas['factorH']
            corr_factor /= 100
            self.norm_config[psname] = self._reference[psname] + \
                dkick*corr_factor

    def _handleGetKicksFromTOCA(self):
        if not self._conn_sofb.connected:
            QMessageBox.warning(
                self, 'Not Connected',
                'There are not connected PVs!', QMessageBox.Ok)
            return
        dkicks = self._conn_sofb.get_deltakicks()

        if not dkicks:
            QMessageBox.warning(
                self, 'Could not get kicks',
                'Could not get kicks from TOCA!', QMessageBox.Ok)
            return

        self._deltas['kicks'] = dkicks
        self._updateCorrKicks()
        self._updateStrenghtsWidget('corrs')
        self.verifySync()

    def _handleCorrFactorsSet(self):
        widget = self.sender()
        factor = widget.objectName()
        dim = ' vertical ' if factor == 'factorV' else ' horizantal '
        new_value = widget.value()
        self._stack_command(
            widget, self._deltas[factor], new_value,
            message='set'+dim+'orbit correction factor to {}'.format(
                    new_value))
        self._deltas[factor] = new_value

        self._updateCorrKicks()
        self._updateStrenghtsWidget('corrs')
        self.verifySync()

    def _resetOrbitChanges(self):
        self._deltas['kicks'] = dict()
        self._deltas['factorH'] = 0.0
        self._deltas['factorV'] = 0.0
        self.sb_correctH.setValue(0.0)
        self.sb_correctV.setValue(0.0)

    # ---------- tune ----------

    def _handleDeltaTuneSet(self):
        widget = self.sender()
        tune = widget.objectName()
        dim = ' vertical ' if tune == 'tuneY' else ' horizantal '
        new_value = widget.value()
        self._stack_command(
            widget, self._deltas[tune], new_value,
            message='set'+dim+'delta tune to {}'.format(
                    new_value))
        self._deltas[tune] = new_value

        self._updateDeltaKL()

    def _updateDeltaKL(self):
        self._deltaKL = self._tunecorr.calculate_deltaKL(
            [self._deltas['tuneX'], self._deltas['tuneY']])
        self.l_deltaKLQF.setText('{: 4f}'.format(self._deltaKL[0]))
        self.l_deltaKLQD.setText('{: 4f}'.format(self._deltaKL[1]))

        self.norm_config['BO-Fam:PS-QF'] = \
            self._reference['BO-Fam:PS-QF'] + self._deltaKL[0]
        self.norm_config['BO-Fam:PS-QD'] = \
            self._reference['BO-Fam:PS-QD'] + self._deltaKL[1]

        self._updateStrenghtsWidget('quads')
        self.verifySync()

    def _resetTuneChanges(self):
        self.sb_deltaTuneX.setValue(0)
        self.sb_deltaTuneY.setValue(0)
        self._deltaKL = [0.0, 0.0]
        self.l_deltaKLQF.setText('{: 6f}'.format(self._deltaKL[0]))
        self.l_deltaKLQD.setText('{: 6f}'.format(self._deltaKL[1]))

    # ---------- chromaticity ----------

    def _estimateChrom(self, use_ref=False):
        nom_SL = self._chromcorr.nominal_intstrengths.flatten()
        if use_ref:
            curr_SL = _np.array([self._reference['BO-Fam:PS-SF'],
                                 self._reference['BO-Fam:PS-SD']])
        else:
            curr_SL = _np.array([self.norm_config['BO-Fam:PS-SF'],
                                 self.norm_config['BO-Fam:PS-SD']])
        delta_SL = curr_SL - nom_SL
        return self._chromcorr.calculate_Chrom(delta_SL)

    def _handleChromSet(self):
        widget = self.sender()
        chrom = widget.objectName()
        dim = ' vertical ' if chrom == 'chromY' else ' horizantal '
        new_value = widget.value()
        self._stack_command(
            widget, self._deltas[chrom], new_value,
            message='set'+dim+'chromaticity to {}'.format(
                    new_value))
        self._deltas[chrom] = new_value

        self._updateDeltaSL()

    def _updateDeltaSL(self):
        desired_Chrom = _np.array([self._deltas['chromX'],
                                   self._deltas['chromY']])
        deltas = desired_Chrom - self._currChrom
        self._deltaSL = self._chromcorr.calculate_deltaSL(
            [deltas[0], deltas[1]])
        self.l_deltaSLSF.setText('{: 4f}'.format(self._deltaSL[0]))
        self.l_deltaSLSD.setText('{: 4f}'.format(self._deltaSL[1]))

        self.norm_config['BO-Fam:PS-SF'] = \
            self._reference['BO-Fam:PS-SF'] + self._deltaSL[0]
        self.norm_config['BO-Fam:PS-SD'] = \
            self._reference['BO-Fam:PS-SD'] + self._deltaSL[1]

        self._updateStrenghtsWidget('sexts')
        self.verifySync()

    def _resetChromChanges(self):
        self._currChrom = self._estimateChrom(use_ref=True)
        self.sb_ChromX.setValue(self._currChrom[0])
        self.sb_ChromY.setValue(self._currChrom[1])
        self._deltaSL = [0.0, 0.0]
        self.l_deltaSLSF.setText('{: 6f}'.format(self._deltaSL[0]))
        self.l_deltaSLSD.setText('{: 6f}'.format(self._deltaSL[1]))

    # ---------- update methods ----------

    def _updateReference(self, pstype):
        psnames = self._get_PSNames(pstype)
        for ps in psnames:
            self._reference[ps] = self.norm_config[ps]

        if pstype == 'corrs':
            self._resetOrbitChanges()
        elif pstype == 'quads':
            self._resetTuneChanges()
        elif pstype == 'sexts':
            self._resetChromChanges()
        else:
            self._resetOrbitChanges()
            self._resetTuneChanges()
            self._resetChromChanges()

        self.verifySync()

    def _updateRampConfig(self):
        if self.norm_config is not None:
            self.normConfigChanged.emit(self.time, _dcopy(self.norm_config))

    def updateTime(self, time):
        """Update norm config time."""
        self.time = time
        self.label_time.setText('<h2>T = '+str(time)+'ms</h2>')
        self.energy = self.ramp_config.ps_waveform_interp_energy(time)
        self._handleStrengtsLimits(self.cb_checklims.checkState())
        self.verifySync()

    def updateLabel(self, label):
        """Update norm config label."""
        self.norm_config['label'] = label
        self.label_description.setText('<h2>'+label+'</h2>')
        self.verifySync()

    @Slot(str, str)
    def updateSettings(self, tunecorr_configname, chromcorr_configname):
        self._tunecorr = BOTuneCorr(tunecorr_configname)
        self._chromcorr = BOChromCorr(chromcorr_configname)
        self._updateDeltaKL()
        self._estimateChrom(use_ref=True)
        self._updateDeltaSL()

    # ---------- handle undo redo stack ----------

    def _stack_command(self, widget, old_value, new_value, message):
        global _flag_stack_next_command, _flag_stacking
        if _flag_stack_next_command and (old_value != new_value):
            _flag_stacking = True
            command = _UndoRedoSpinbox(widget, old_value, new_value, message)
            self._undo_stack.push(command)
        else:
            _flag_stack_next_command = True

    # ---------- helper methods ----------

    def _get_PSNames(self, pstype=None):
        psnames = list()
        if pstype == 'corrs':
            psnames = _PSSearch.get_psnames({'sec': 'BO', 'dev': 'C(V|H)'})
        elif pstype == 'quads':
            psnames = ['BO-Fam:PS-QF', 'BO-Fam:PS-QD']
        elif pstype == 'sexts':
            psnames = ['BO-Fam:PS-SF', 'BO-Fam:PS-SD']
        else:
            psnames = _PSSearch.get_psnames({'sec': 'BO', 'sub': 'Fam'})
            psnames.extend(_PSSearch.get_psnames({'sec': 'BO', 'dev': 'QS'}))
            psnames.extend(_PSSearch.get_psnames({'sec': 'BO', 'dev': 'CH'}))
            psnames.extend(_PSSearch.get_psnames({'sec': 'BO', 'dev': 'CV'}))
        return psnames

    def _show_kicks_graph(self):
        strenghts_dict = _dcopy(self.norm_config)
        strenghts_dict.pop('label')
        graph = _ShowCorrectorKicks(self, self.time, strenghts_dict)
        graph.show()


class _UndoRedoSpinbox(QUndoCommand):
    """Class to define command change ramp number of points."""

    def __init__(self, spinbox, old_data, new_data, description):
        super().__init__(description)
        self.spinbox = spinbox
        self.old_data = old_data
        self.new_data = new_data

    def undo(self):
        global _flag_stack_next_command
        _flag_stack_next_command = False
        self.spinbox.setValue(self.old_data)
        self.spinbox.editingFinished.emit()

    def redo(self):
        global _flag_stack_next_command, _flag_stacking
        if not _flag_stacking:
            _flag_stack_next_command = False
            self.spinbox.setValue(self.new_data)
            self.spinbox.editingFinished.emit()
        else:
            _flag_stacking = False
