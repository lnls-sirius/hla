"""Booster Ramp Control HLA: Optics Adjust Module."""

from functools import partial as _part
from copy import deepcopy as _dcopy
import numpy as _np

from qtpy.QtCore import Qt, Signal, Slot
from qtpy.QtGui import QKeySequence
from qtpy.QtWidgets import QWidget, QGroupBox, QPushButton, QLabel, \
    QGridLayout, QScrollArea, QFormLayout, QCheckBox, QDoubleSpinBox, \
    QUndoStack, QUndoCommand, QHBoxLayout, QMessageBox

from siriuspy.search import MASearch as _MASearch
from siriuspy.ramp import ramp
from siriuspy.optics.opticscorr import BOTuneCorr, BOChromCorr
from siriuspy.clientconfigdb import ConfigDBException as _ConfigDBException

from siriushla.widgets.windows import SiriusMainWindow
from siriushla.bo_ap_ramp.auxiliar_classes import \
    NewRampConfigGetName as _NewRampConfigGetName, \
    MyDoubleSpinBox as _MyDoubleSpinBox


_flag_stack_next_command = True
_flag_stacking = False


class BONormEdit(SiriusMainWindow):
    """Widget to perform optics adjust in normalized configurations."""

    normConfigChanged = Signal(ramp.BoosterNormalized, str, float, bool)

    def __init__(self, parent=None, prefix='', norm_config=None,
                 time=None, energy=None, magnets=dict(), conn_sofb=None,
                 tunecorr_configname=None, chromcorr_configname=None):
        """Initialize object."""
        super().__init__(parent)
        self.setWindowTitle('Edit Normalized Configuration')
        self.prefix = prefix
        self.norm_config = norm_config
        self.time = time
        self.energy = energy

        self._aux_magnets = magnets
        self._tunecorr = BOTuneCorr(tunecorr_configname)
        self._chromcorr = BOChromCorr(chromcorr_configname)

        self._norm_config_oldname = ''
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
        self._conn_sofb = conn_sofb
        self._setupUi()

        self._undo_stack = QUndoStack(self)
        self.act_undo = self._undo_stack.createUndoAction(self, 'Undo')
        self.act_undo.setShortcut(QKeySequence.Undo)
        self.menu.addAction(self.act_undo)
        self.act_redo = self._undo_stack.createRedoAction(self, 'Redo')
        self.act_redo.setShortcut(QKeySequence.Redo)
        self.menu.addAction(self.act_redo)

    # ---------- setup/build layout ----------

    def _setupUi(self):
        self.menu = self.menuBar().addMenu('Options')
        self.act_load = self.menu.addAction('Load')
        self.act_load.triggered.connect(self._load)
        if not self.norm_config.exist():
            self.act_load.setEnabled(False)
        self.act_save = self.menu.addAction('Save')
        self.act_save.triggered.connect(self._save)
        self.act_saveas = self.menu.addAction('Save as...')
        self.act_saveas.triggered.connect(self._showSaveAsPopup)

        self.label_name = QLabel('<h2>'+self.norm_config.name+'</h2>', self)
        self.label_name.setAlignment(Qt.AlignCenter)

        self.strengths = self._setupStrengthWidget()
        self.orbit = self._setupOrbitWidget()
        self.tune = self._setupTuneWidget()
        self.chrom = self._setupChromWidget()

        self.bt_save2rampconfig = QPushButton('Save changes', self)
        self.bt_save2rampconfig.clicked.connect(self._updateRampConfig)
        self.bt_apply2machine = QPushButton('Apply changes to machine', self)
        self.bt_apply2machine.clicked.connect(
            _part(self._updateRampConfig, apply=True))

        cw = QWidget()
        lay = QGridLayout()
        lay.setVerticalSpacing(10)
        lay.setHorizontalSpacing(10)
        lay.addWidget(self.label_name, 0, 0, 1, 2)
        lay.addWidget(self.strengths, 1, 0, 5, 1)
        lay.addWidget(self.orbit, 1, 1)
        lay.addWidget(self.tune, 2, 1)
        lay.addWidget(self.chrom, 3, 1)
        lay.addWidget(self.bt_save2rampconfig, 4, 1)
        lay.addWidget(self.bt_apply2machine, 5, 1)
        lay.setColumnStretch(0, 2)
        lay.setColumnStretch(1, 2)
        lay.setRowStretch(0, 2)
        lay.setRowStretch(1, 8)
        lay.setRowStretch(2, 8)
        lay.setRowStretch(3, 8)
        lay.setRowStretch(4, 1)
        cw.setLayout(lay)

        cw.setStyleSheet("""
            QGroupBox::title{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 2px 0 2px;}""")
        cw.setFocusPolicy(Qt.StrongFocus)
        self.setCentralWidget(cw)

    def _setupStrengthWidget(self):
        scrollarea = QScrollArea()
        self.nconfig_data = QWidget()
        flay_configdata = QFormLayout()
        manames = self._getManames()
        self._map_manames2wigdets = dict()
        for ma in manames:
            if ma == ramp.BoosterRamp.MANAME_DIPOLE:
                ma_value = QLabel(str(self.norm_config[ma])+' GeV', self)
                flay_configdata.addRow(QLabel(ma + ': ', self), ma_value)
            else:
                ma_value = _MyDoubleSpinBox(self.nconfig_data)
                ma_value.setDecimals(6)
                ma_value.setValue(self.norm_config[ma])
                ma_value.editingFinished.connect(self._handleStrenghtsSet)

                aux = self._aux_magnets[ma]
                currs = (aux.current_min, aux.current_max)
                lims = aux.conv_current_2_strength(
                    currents=currs, strengths_dipole=self.energy)
                ma_value.setMinimum(min(lims))
                ma_value.setMaximum(max(lims))

                if 'Q' in ma:
                    unit_txt = '1/m'
                elif 'S' in ma:
                    unit_txt = '1/m²'
                else:
                    unit_txt = 'urad'
                label_unit = QLabel(unit_txt, self)
                label_unit.setStyleSheet("min-width:2.5em; max-width:2.5em;")
                hb = QHBoxLayout()
                hb.addWidget(ma_value)
                hb.addWidget(label_unit)

                flay_configdata.addRow(QLabel(ma + ': ', self), hb)

            ma_value.setObjectName(ma)
            ma_value.setStyleSheet("min-height:1.29em; max-height:1.29em;")
            self._map_manames2wigdets[ma] = ma_value

        self.nconfig_data.setLayout(flay_configdata)
        scrollarea.setWidget(self.nconfig_data)

        self.cb_checklims = QCheckBox('Set limits according to energy', self)
        self.cb_checklims.setChecked(True)
        self.cb_checklims.stateChanged.connect(self._handleStrengtsLimits)

        gbox = QGroupBox()
        gbox.setObjectName('strengths')
        gbox.setStyleSheet('#strengths{min-width:20em;}')
        glay = QGridLayout()
        glay.addWidget(scrollarea, 0, 0, 1, 2)
        glay.addWidget(self.cb_checklims, 1, 0, 1, 2)
        gbox.setLayout(glay)
        return gbox

    def _setupOrbitWidget(self):
        self.bt_get_kicks = QPushButton('Get Kicks from SOFB', self)
        self.bt_get_kicks.clicked.connect(self._handleGetKicksFromSOFB)

        label_correctH = QLabel('Correct H', self,
                                alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.sb_correctH = _MyDoubleSpinBox(self)
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
        self.sb_correctV = _MyDoubleSpinBox(self)
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

            setattr(self, 'sb_deltaTune'+cord, _MyDoubleSpinBox(self))
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

            setattr(self, 'sb_Chrom'+cord, _MyDoubleSpinBox(self))
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

    def _load(self):
        try:
            self.norm_config.load()
        except _ConfigDBException as err:
            QMessageBox.critical(self, 'Error', str(err), QMessageBox.Ok)
        else:
            self._resetTuneChanges()
            self._resetChromChanges()
            self._resetOrbitChanges()
            self.verifySync()

    def _save(self, new_name=None):
        try:
            if self.norm_config.exist():
                self._norm_config_oldname = self.norm_config.name
                if not new_name:
                    new_name = self.norm_config.generate_config_name(
                        self._norm_config_oldname)
                self.norm_config.save(new_name)
            else:
                self.norm_config.save()
                self.act_load.setEnabled(True)
        except _ConfigDBException as err:
            QMessageBox.critical(self, 'Error', str(err), QMessageBox.Ok)
        finally:
            self.label_name.setText('<h2>'+self.norm_config.name+'</h2>')
            self.verifySync()

    def _showSaveAsPopup(self):
        self._saveAsPopup = _NewRampConfigGetName(
            self.norm_config, 'bo_normalized', self, new_from_template=False)
        self._saveAsPopup.configname.connect(self._save)
        self._saveAsPopup.open()

    def verifySync(self):
        """Verify sync status related to ConfServer."""
        if not self.norm_config.synchronized:
            self.act_save.setEnabled(True)
            self.label_name.setStyleSheet("color:red;")
            self.setToolTip("There are unsaved changes")
        else:
            self.act_save.setEnabled(False)
            self.label_name.setStyleSheet("")
            self.setToolTip("")

    # ---------- strengths ----------

    def _handleStrenghtsSet(self):
        maname = self.sender().objectName()
        new_value = self.sender().value()
        self._stack_command(
            self.sender(), self.norm_config[maname], new_value,
            message='set '+maname+' strength to {}'.format(new_value))
        self.norm_config[maname] = new_value

    def _handleStrengtsLimits(self, state):
        manames = self.norm_config.manames
        if state:
            for ma in manames:
                ma_value = self.data.findChild(QDoubleSpinBox, name=ma)
                aux = self._aux_magnets[ma]
                currs = (aux.current_min, aux.current_max)
                lims = aux.conv_current_2_strength(
                    currents=currs, strengths_dipole=self.energy)
                ma_value.setMinimum(min(lims))
                ma_value.setMaximum(max(lims))
        else:
            for ma in manames:
                ma_value = self.data.findChild(QDoubleSpinBox, name=ma)
                ma_value.setMinimum(-100)
                ma_value.setMaximum(100)

    def _updateStrenghtsWidget(self, matype):
        manames = self._getManames(matype)
        wid2change = manames if manames else self.norm_config.manames
        for wid in wid2change:
            value = self.norm_config[wid]
            self._map_manames2wigdets[wid].setValue(value)

    # ---------- orbit ----------

    def _updateCorrKicks(self):
        for maname, dkick in self._deltas['kicks']:
            corr_factor = self._deltas['factorV'] if 'CV' in maname \
                else self._deltas['factorH']
            current_kick = self.norm_config[maname]
            self.norm_config[maname] = current_kick + dkick*corr_factor

    def _handleGetKicksFromSOFB(self):
        if not self._conn_sofb.connected:
            QMessageBox.warning(
                self, 'Not Connected',
                'There are not connected PVs!', QMessageBox.Ok)
            return
        dkicks = self._conn_sofb.get_deltakicks()

        if not dkicks:
            QMessageBox.warning(
                self, 'Could not get kicks',
                'Could not get kicks from SOFB!', QMessageBox.Ok)
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

        self.norm_config['BO-Fam:MA-QF'] = \
            self._reference['BO-Fam:MA-QF'] + self._deltaKL[0]
        self.norm_config['BO-Fam:MA-QD'] = \
            self._reference['BO-Fam:MA-QD'] + self._deltaKL[1]
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
            curr_SL = _np.array([self._reference['BO-Fam:MA-SF'],
                                 self._reference['BO-Fam:MA-SD']])
        else:
            curr_SL = _np.array([self.norm_config['BO-Fam:MA-SF'],
                                 self.norm_config['BO-Fam:MA-SD']])
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

        self.norm_config['BO-Fam:MA-SF'] = \
            self._reference['BO-Fam:MA-SF'] + self._deltaSL[0]
        self.norm_config['BO-Fam:MA-SD'] = \
            self._reference['BO-Fam:MA-SD'] + self._deltaSL[1]
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

    def _updateReference(self, matype):
        manames = self._getManames(matype)
        for ma in manames:
            self._reference[ma] = self.norm_config[ma]

        if matype == 'corrs':
            self._resetOrbitChanges()
        elif matype == 'quads':
            self._resetTuneChanges()
        elif matype == 'sexts':
            self._resetChromChanges()
        else:
            self._resetOrbitChanges()
            self._resetTuneChanges()
            self._resetChromChanges()

        self.verifySync()

    def _updateRampConfig(self, apply=False):
        if self.norm_config is not None:
            self.normConfigChanged.emit(
                self.norm_config, self._norm_config_oldname,
                self.time, apply)

    @Slot(str, str)
    def updateSettings(self, tunecorr_configname, chromcorr_configname):
        self._tunecorr = BOTuneCorr(tunecorr_configname)
        self._chromcorr = BOChromCorr(chromcorr_configname)
        self._updateDeltaKL()
        self._estimateChrom(use_ref=True)
        self._updateDeltaSL()

    # ---------- handle undo redo stask ----------

    def _stack_command(self, widget, old_value, new_value, message):
        global _flag_stack_next_command, _flag_stacking
        if _flag_stack_next_command and (old_value != new_value):
            _flag_stacking = True
            command = _UndoRedoSpinbox(widget, old_value, new_value, message)
            self._undo_stack.push(command)
        else:
            _flag_stack_next_command = True

    # ---------- helper methods ----------

    def _getManames(self, matype=None):
        manames = list()
        if matype == 'corrs':
            manames = _MASearch.get_manames(
                filters={'sec': 'BO', 'dev': 'C(V|H)'})
        elif matype == 'quads':
            manames = ['BO-Fam:MA-QF', 'BO-Fam:MA-QD']
        elif matype == 'sexts':
            manames = ['BO-Fam:MA-SF', 'BO-Fam:MA-SD']
        else:
            manames = _MASearch.get_manames(
                filters={'sec': 'BO', 'sub': 'Fam'})
            manames.extend(_MASearch.get_manames(
                filters={'sec': 'BO', 'dev': 'QS'}))
            manames.extend(sorted(_MASearch.get_manames(
                filters={'sec': 'BO', 'dev': 'CH'})))
            manames.extend(sorted(_MASearch.get_manames(
                filters={'sec': 'BO', 'dev': 'CV'})))
        return manames


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


if __name__ == '__main__':
    """Run Example."""
    import sys
    from siriuspy.envars import vaca_prefix
    from siriuspy.ramp import ramp
    from siriuspy.ramp.conn import ConnSOFB
    from siriuspy.ramp.magnet import Magnet
    from siriushla.sirius_application import SiriusApplication

    app = SiriusApplication()

    nconfig = ramp.BoosterNormalized('testing')
    aux_magnets = dict()
    for ma in ramp.BoosterNormalized().manames:
        aux_magnets[ma] = Magnet(ma)
    conn_sofb = ConnSOFB(prefix=vaca_prefix)

    w = BONormEdit(
        parent=None, prefix=vaca_prefix, norm_config=nconfig,
        time=100, energy=0.985, magnets=aux_magnets, conn_sofb=conn_sofb,
        tunecorr_configname='Default', chromcorr_configname='Default')
    w.show()
    sys.exit(app.exec_())
