"""Booster Ramp Control HLA: Optics Adjust Module."""

from copy import deepcopy as _dcopy
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QGroupBox, QPushButton, QSpinBox, QLabel, \
                            QHBoxLayout, QVBoxLayout, QGridLayout, \
                            QSizePolicy as QSzPlcy, QDoubleSpinBox, \
                            QSpacerItem, QInputDialog, QLineEdit
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.ramp import ramp
from siriuspy.ramp.magnet import Magnet as _Magnet
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy.optics.opticscorr import BOTuneCorr, BOChromCorr
from siriuspy.servconf.conf_service import ConfigService as _ConfigService
from pydm.widgets import PyDMLineEdit
from auxiliar_classes import EditNormalizedConfig as _EditNormalizedConfig, \
                             OpticsAdjustSettings as _OpticsAdjustSettings, \
                             MessageBox as _MessageBox


class OpticsAdjust(QGroupBox):
    """Widget to perform optics adjust in normalized configurations."""

    normConfigChanged = pyqtSignal(ramp.BoosterNormalized)

    def __init__(self, parent=None, prefix='', ramp_config=None):
        """Initialize object."""
        super().__init__('Normalized Configurations Optics Adjustments',
                         parent)
        self.prefix = _PVName(prefix)
        self.ramp_config = ramp_config
        self.norm_config = None
        self._table_map = dict()
        self._aux_magnets = dict()
        for ma in ramp.BoosterNormalized().manames:
            self._aux_magnets[ma] = _Magnet(ma)
        self._setupUi()
        self._tunecorr = BOTuneCorr('Default_1')
        self._chromcorr = BOChromCorr('Default')

    def _setupUi(self):
        hlay = QHBoxLayout()
        self.settings = QVBoxLayout()
        self.tune_variation = QGridLayout()
        self.chrom_variation = QGridLayout()
        self.orbit_correction = QGridLayout()

        self._setupChooseConfig()
        self._setupTuneVariation()
        self._setupChromVariation()
        self._setupOrbitCorrection()

        hlay.addSpacerItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Preferred))
        hlay.addLayout(self.settings)
        hlay.addSpacerItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Preferred))
        hlay.addLayout(self.tune_variation)
        hlay.addSpacerItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Preferred))
        hlay.addLayout(self.chrom_variation)
        hlay.addSpacerItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Preferred))
        hlay.addLayout(self.orbit_correction)
        hlay.addSpacerItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Preferred))
        self.setLayout(hlay)

    def _setupChooseConfig(self):
        hlay_config = QHBoxLayout()
        self.sb_config = QSpinBox(self)
        self.l_configname = QLabel('', self)
        hlay_config.addWidget(self.sb_config)
        hlay_config.addWidget(self.l_configname)
        self.bt_edit = QPushButton('Edit strengths', self)
        self.bt_update = QPushButton('Update in ramp config.')
        self.bt_settings = QPushButton('Settings', self)
        l_server = QLabel('<h4>Server</h4>')
        l_server.setAlignment(Qt.AlignCenter)
        self.bt_load = QPushButton('Load', self)
        self.bt_save = QPushButton('Save', self)
        self.bt_save_as = QPushButton('Save As...', self)

        self.sb_config.setMinimum(1)
        self.sb_config.setFixedWidth(80)
        self.sb_config.editingFinished.connect(self._handleConfigIndexChanged)
        self.l_configname.setFixedWidth(250)
        self.bt_edit.clicked.connect(self._showEditPopup)
        self.bt_update.clicked.connect(self._updateRampConfig)
        self.bt_settings.clicked.connect(self._showSettingsPopup)
        self.bt_load.clicked.connect(self._load)
        self.bt_save.clicked.connect(self._save)
        self.bt_save_as.clicked.connect(self._showSaveAsPopup)

        self.settings.addItem(
            QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding))
        self.settings.addLayout(hlay_config)
        self.settings.addItem(
            QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding))
        self.settings.addWidget(self.bt_edit)
        self.settings.addWidget(self.bt_update)
        self.settings.addWidget(self.bt_settings)
        self.settings.addItem(
            QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding))
        self.settings.addWidget(l_server)
        self.settings.addWidget(self.bt_load)
        self.settings.addWidget(self.bt_save)
        self.settings.addWidget(self.bt_save_as)
        self.settings.addItem(
            QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding))

    def _setupTuneVariation(self):
        label_tune = QLabel('<h4>Tune Variation</h4>', self)
        label_tune.setAlignment(Qt.AlignCenter)
        label_tune.setFixedHeight(48)

        label_deltaTuneX = QLabel('Δν<sub>x</sub>: ')
        label_deltaTuneX.setFixedWidth(48)
        self.sb_deltaTuneX = QDoubleSpinBox(self)
        self.sb_deltaTuneX.setDecimals(6)
        self.sb_deltaTuneX.setMinimum(-1)
        self.sb_deltaTuneX.setMaximum(1)
        self.sb_deltaTuneX.setSingleStep(0.0001)
        self.sb_deltaTuneX.setFixedWidth(200)
        self.sb_deltaTuneX.editingFinished.connect(self._calculate_deltaKL)

        label_deltaTuneY = QLabel('Δν<sub>y</sub>: ')
        label_deltaTuneY.setFixedWidth(48)
        self.sb_deltaTuneY = QDoubleSpinBox(self)
        self.sb_deltaTuneY.setDecimals(6)
        self.sb_deltaTuneY.setMinimum(-1)
        self.sb_deltaTuneY.setMaximum(1)
        self.sb_deltaTuneY.setSingleStep(0.0001)
        self.sb_deltaTuneY.setFixedWidth(200)
        self.sb_deltaTuneY.editingFinished.connect(self._calculate_deltaKL)

        label_KL = QLabel('<h4>ΔKL</h4>', self)
        label_KL.setAlignment(Qt.AlignCenter)
        label_KL.setFixedHeight(48)

        label_deltaKLQF = QLabel('QF: ', self)
        label_deltaKLQF.setFixedWidth(48)
        self.l_deltaKLQF = QLabel('', self)

        label_deltaKLQD = QLabel('QD: ', self)
        label_deltaKLQD.setFixedWidth(48)
        self.l_deltaKLQD = QLabel('', self)

        hlay_bt_apply = QHBoxLayout()
        self.bt_apply_deltaKL = QPushButton('Apply', self)
        self.bt_apply_deltaKL.clicked.connect(self._apply_deltaKL)
        self.bt_apply_deltaKL.setFixedWidth(150)
        hlay_bt_apply.addSpacerItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed))
        hlay_bt_apply.addWidget(self.bt_apply_deltaKL)
        hlay_bt_apply.addSpacerItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed))

        self.tune_variation.addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Expanding), 0, 2)
        self.tune_variation.addWidget(label_tune, 1, 0, 1, 5)
        self.tune_variation.addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 2, 2)
        self.tune_variation.addWidget(label_deltaTuneX, 3, 0)
        self.tune_variation.addWidget(self.sb_deltaTuneX, 3, 1)
        self.tune_variation.addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 3, 2)
        self.tune_variation.addWidget(label_deltaTuneY, 3, 3)
        self.tune_variation.addWidget(self.sb_deltaTuneY, 3, 4)
        self.tune_variation.addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Expanding), 4, 2)
        self.tune_variation.addWidget(label_KL, 5, 0, 1, 5)
        self.tune_variation.addWidget(label_deltaKLQF, 6, 0)
        self.tune_variation.addWidget(self.l_deltaKLQF, 6, 1)
        self.tune_variation.addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 6, 2)
        self.tune_variation.addWidget(label_deltaKLQD, 6, 3)
        self.tune_variation.addWidget(self.l_deltaKLQD, 6, 4)
        self.tune_variation.addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Expanding), 7, 2)
        self.tune_variation.addLayout(hlay_bt_apply, 8, 0, 1, 5)
        self.tune_variation.addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Expanding), 9, 2)

    def _setupChromVariation(self):
        label_chrom = QLabel('<h4>Chromaticity Variation</h4>', self)
        label_chrom.setAlignment(Qt.AlignCenter)
        label_chrom.setFixedHeight(48)

        label_deltaChromX = QLabel('Δξ<sub>x</sub>: ')
        label_deltaChromX.setFixedWidth(48)
        self.sb_deltaChromX = QDoubleSpinBox(self)
        self.sb_deltaChromX.setDecimals(6)
        self.sb_deltaChromX.setMinimum(-10)
        self.sb_deltaChromX.setMaximum(10)
        self.sb_deltaChromX.setSingleStep(0.0001)
        self.sb_deltaChromX.setFixedWidth(200)
        self.sb_deltaChromX.editingFinished.connect(self._calculate_deltaSL)

        label_deltaChromY = QLabel('Δξ<sub>y</sub>: ')
        label_deltaChromY.setFixedWidth(48)
        self.sb_deltaChromY = QDoubleSpinBox(self)
        self.sb_deltaChromY.setDecimals(6)
        self.sb_deltaChromY.setMinimum(-10)
        self.sb_deltaChromY.setMaximum(10)
        self.sb_deltaChromY.setSingleStep(0.0001)
        self.sb_deltaChromY.setFixedWidth(200)
        self.sb_deltaChromY.editingFinished.connect(self._calculate_deltaSL)

        label_SL = QLabel('<h4>ΔSL</h4>', self)
        label_SL.setAlignment(Qt.AlignCenter)
        label_SL.setFixedHeight(48)

        label_deltaSLSF = QLabel('SF: ', self)
        label_deltaSLSF.setFixedWidth(48)
        self.l_deltaSLSF = QLabel('', self)

        label_deltaSLSD = QLabel('SD: ', self)
        label_deltaSLSD.setFixedWidth(48)
        self.l_deltaSLSD = QLabel('', self)

        hlay_bt_apply = QHBoxLayout()
        self.bt_apply_deltaSL = QPushButton('Apply', self)
        self.bt_apply_deltaSL.clicked.connect(self._apply_deltaSL)
        self.bt_apply_deltaSL.setFixedWidth(150)
        hlay_bt_apply.addSpacerItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed))
        hlay_bt_apply.addWidget(self.bt_apply_deltaSL)
        hlay_bt_apply.addSpacerItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed))

        self.chrom_variation.addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Expanding), 0, 2)
        self.chrom_variation.addWidget(label_chrom, 1, 0, 1, 5)
        self.chrom_variation.addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 2, 2)
        self.chrom_variation.addWidget(label_deltaChromX, 3, 0)
        self.chrom_variation.addWidget(self.sb_deltaChromX, 3, 1)
        self.chrom_variation.addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 3, 2)
        self.chrom_variation.addWidget(label_deltaChromY, 3, 3)
        self.chrom_variation.addWidget(self.sb_deltaChromY, 3, 4)
        self.chrom_variation.addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Expanding), 4, 2)
        self.chrom_variation.addWidget(label_SL, 5, 0, 1, 5)
        self.chrom_variation.addWidget(label_deltaSLSF, 6, 0)
        self.chrom_variation.addWidget(self.l_deltaSLSF, 6, 1)
        self.chrom_variation.addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 6, 2)
        self.chrom_variation.addWidget(label_deltaSLSD, 6, 3)
        self.chrom_variation.addWidget(self.l_deltaSLSD, 6, 4)
        self.chrom_variation.addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Expanding), 7, 2)
        self.chrom_variation.addLayout(hlay_bt_apply, 8, 0, 1, 5)
        self.chrom_variation.addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Expanding), 9, 2)

    def _setupOrbitCorrection(self):
        label = QLabel('<h4>Orbit Correction</h4>', self)
        label.setAlignment(Qt.AlignCenter)
        label.setFixedHeight(48)

        self.bt_load_measured_orbit = QPushButton(
            'Load Measured Orbit', self)
        self.bt_load_measured_orbit.clicked.connect(self._load_measured_orbit)
        self.bt_correctH = QPushButton('Correct H', self)
        self.bt_correctH.clicked.connect(self._correctH)
        self.pydmledit_correctH = PyDMLineEdit(
            parent=self,
            init_channel='ca://'+_vaca_prefix)
        labelH = QLabel('%', self)
        labelH.setFixedWidth(24)
        self.bt_correctV = QPushButton('Correct V', self)
        self.bt_correctV.clicked.connect(self._correctV)
        self.pydmledit_correctV = PyDMLineEdit(
            parent=self,
            init_channel='ca://'+_vaca_prefix)
        labelV = QLabel('%', self)
        labelV.setFixedWidth(24)

        hlay_bt_apply = QHBoxLayout()
        self.bt_apply_orbitcorrection = QPushButton('Apply', self)
        self.bt_apply_orbitcorrection.clicked.connect(
            self._apply_orbitcorrection)
        self.bt_apply_orbitcorrection.setFixedWidth(150)
        hlay_bt_apply.addSpacerItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed))
        hlay_bt_apply.addWidget(self.bt_apply_orbitcorrection)
        hlay_bt_apply.addSpacerItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed))

        self.orbit_correction.addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 0, 0)
        self.orbit_correction.addWidget(label, 1, 0, 1, 3)
        self.orbit_correction.addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 2, 0)
        self.orbit_correction.addWidget(self.bt_load_measured_orbit,
                                        3, 0, 1, 3)
        self.orbit_correction.addWidget(self.bt_correctH, 4, 0)
        self.orbit_correction.addWidget(self.pydmledit_correctH, 4, 1)
        self.orbit_correction.addWidget(labelH, 4, 2)
        self.orbit_correction.addWidget(self.bt_correctV, 5, 0)
        self.orbit_correction.addWidget(self.pydmledit_correctV, 5, 1)
        self.orbit_correction.addWidget(labelV, 5, 2)
        self.orbit_correction.addLayout(hlay_bt_apply, 6, 0, 1, 3)
        self.orbit_correction.addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 7, 0)

    def _handleConfigIndexChanged(self):
        if not self._table_map:
            return
        config_idx = self.sb_config.value()
        for label, value in self._table_map['rows'].items():
            if config_idx == (value + 1):
                self.l_configname.setText(label)
                if label in ['Injection', 'Ejection']:
                    self.bt_edit.setEnabled(False)
                    self.bt_update.setEnabled(False)
                    self.bt_load.setEnabled(False)
                    self.bt_save.setEnabled(False)
                    self.bt_save_as.setEnabled(False)
                    self.norm_config = None
                else:
                    self.bt_edit.setEnabled(True)
                    self.bt_update.setEnabled(True)
                    self.bt_save.setEnabled(True)
                    self.bt_save_as.setEnabled(True)
                    self.norm_config = self.ramp_config[label]
                    if self.norm_config.configsrv_exist():
                        self.bt_load.setEnabled(True)
                    else:
                        self.bt_load.setEnabled(False)
                        self.verifySync()
                break
        self._resetTuneChanges()
        self._resetChromChanges()
        self._resetOrbitChanges()

    def _showEditPopup(self):
        if self.norm_config is not None:
            norm_list = self.ramp_config.normalized_configs
            for norm in norm_list:
                if norm[1] == self.norm_config.name:
                    time = norm[0]
                    break
            energy = self.ramp_config.waveform_interp_energy(time)
            self._editPopup = _EditNormalizedConfig(
                self, self.norm_config, energyGeV=energy,
                aux_magnets=self._aux_magnets)
            self._editPopup.editConfig.connect(self._handleEdit)
            self._editPopup.cb_checklims.setFocus()
            self._editPopup.open()

    @pyqtSlot(dict)
    def _handleEdit(self, nconfig):
        for maname, value in nconfig.items():
            self.norm_config[maname] = value
        self.verifySync()

    def _updateRampConfig(self):
        self.normConfigChanged.emit(self.norm_config)

    def _showSettingsPopup(self):
        if self.norm_config is not None:
            self._settingsPopup = _OpticsAdjustSettings(
                self, self._tunecorr.name, self._chromcorr.name)
            self._settingsPopup.updateSettings.connect(
                self._handleUpdateSettings)
            self._settingsPopup.open()

    @pyqtSlot(list)
    def _handleUpdateSettings(self, settings):
        self._tunecorr = BOTuneCorr(settings[0])
        self._chromcorr = BOChromCorr(settings[1])
        # TODO: handle orbir correction settings

    def _load(self):
        if self.norm_config is not None:
            self.norm_config.configsrv_load()
            self._resetTuneChanges()
            self._resetChromChanges()
            self._resetOrbitChanges()
            self.verifySync()

    def _save(self):
        if self.norm_config is not None:
            self.norm_config.configsrv_save()
            self.verifySync()

    def _showSaveAsPopup(self):
        if self.norm_config is not None:
            text, ok = QInputDialog.getText(self, 'Save As...',
                                            'Normalized config. name:',
                                            echo=QLineEdit.Normal, text='')
        if not ok:
            return
        self._name_to_saveas = text
        allconfigs = _ConfigService().find_configs(config_type='bo_ramp')
        for c in allconfigs['result']:
            if text == c['name']:
                save_changes = _MessageBox(
                    self, 'Overwrite configuration?',
                    'There is a configuration with name {}. \n'
                    'Do you want to replace it?'.format(text),
                    'Yes', 'Cancel')
                save_changes.acceptedSignal.connect(self._save_as)
                save_changes.exec_()
                break
        else:
            self._save_as()

    def _save_as(self):
        config_tosave = _dcopy(self.norm_config)
        config_tosave.name = self._name_to_saveas
        config_tosave.configsrv_save()

    def _calculate_deltaKL(self):
        if self.norm_config is None:
            return
        dtunex = self.sb_deltaTuneX.value()
        dtuney = self.sb_deltaTuneY.value()

        self._deltaKL = self._tunecorr.calculate_deltaKL([dtunex, dtuney])

        self.l_deltaKLQF.setText('{:6f}'.format(self._deltaKL[0]))
        self.l_deltaKLQD.setText('{:6f}'.format(self._deltaKL[1]))

    def _apply_deltaKL(self):
        self.norm_config['BO-Fam:MA-QF'] += self._deltaKL[0]
        self.norm_config['BO-Fam:MA-QD'] += self._deltaKL[1]
        self._resetTuneChanges()
        self.verifySync()

    def _calculate_deltaSL(self):
        if self.norm_config is None:
            return

        dchromx = self.sb_deltaChromX.value()
        dchromy = self.sb_deltaChromY.value()

        self._deltaSL = self._chromcorr.calculate_deltaSL([dchromx, dchromy])

        self.l_deltaSLSF.setText('{:6f}'.format(self._deltaSL[0]))
        self.l_deltaSLSD.setText('{:6f}'.format(self._deltaSL[1]))

    def _apply_deltaSL(self):
        self.norm_config['BO-Fam:MA-SF'] += self._deltaSL[0]
        self.norm_config['BO-Fam:MA-SD'] += self._deltaSL[1]
        self._resetChromChanges()
        self.verifySync()

    def _load_measured_orbit(self):
        # TODO: include orbit correction
        print('Load Measured Orbit')

    def _correctH(self):
        # TODO: include orbit correction
        print('Correct Horizontal Orbit')

    def _correctV(self):
        # TODO: include orbit correction
        print('Correct Vertical Orbit')

    def _apply_orbitcorrection(self):
        # TODO: include orbit correction
        self._resetOrbitChanges()
        self.verifySync()

    def _resetTuneChanges(self):
        self.sb_deltaTuneX.setValue(0)
        self.sb_deltaTuneY.setValue(0)
        self._deltaKL = [0.0, 0.0]
        self.l_deltaKLQF.setText('{:6f}'.format(self._deltaKL[0]))
        self.l_deltaKLQD.setText('{:6f}'.format(self._deltaKL[1]))

    def _resetChromChanges(self):
        self.sb_deltaChromX.setValue(0)
        self.sb_deltaChromY.setValue(0)
        self._deltaSL = [0.0, 0.0]
        self.l_deltaSLSF.setText('{:6f}'.format(self._deltaSL[0]))
        self.l_deltaSLSD.setText('{:6f}'.format(self._deltaSL[1]))

    def _resetOrbitChanges(self):
        pass
        # TODO: include orbit correction

    @pyqtSlot(dict)
    def getConfigIndices(self, table_map):
        """Update table_map and settings widget."""
        self._table_map = table_map
        self.sb_config.setMaximum(max(self._table_map['rows'].values())+1)
        normconfigname = self.l_configname.text()
        if normconfigname == '':
            return
        if normconfigname in self._table_map['rows'].keys():
            self.sb_config.setValue(self._table_map['rows'][normconfigname]+1)
        else:
            self.sb_config.setValue(self._table_map['rows']['Injection']+1)
            self.l_configname.setText('Injection')
        self._handleConfigIndexChanged()

    @pyqtSlot(ramp.BoosterRamp)
    def handleLoadRampConfig(self, ramp_config):
        """Update all widgets in loading BoosterRamp config."""
        self.ramp_config = ramp_config
        if (self.norm_config is not None and
                self.norm_config.name in ramp_config.normalized_configs_names):
            self.norm_config = self.ramp_config[self.norm_config.name]

    def verifySync(self):
        """Verify sync status related to ConfServer."""
        if self.norm_config is not None:
            if not self.norm_config.configsrv_synchronized:
                self.bt_save.setEnabled(True)
            else:
                self.bt_save.setEnabled(False)
