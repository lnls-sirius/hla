"""Booster Ramp Control HLA: Optics Adjust Module."""

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QGroupBox, QPushButton, QSpinBox, QLabel, \
                            QHBoxLayout, QGridLayout, QSpacerItem, \
                            QSizePolicy as QSzPlcy, QDoubleSpinBox
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.ramp import ramp
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy.optics.opticscorr import BOTuneCorr, BOChromCorr
from pydm.widgets import PyDMLineEdit
from auxiliar_classes import EditNormalizedConfig


class OpticsAdjust(QGroupBox):
    """Widget to perform optics adjust in normalized configurations."""

    def __init__(self, parent=None, prefix=''):
        """Initialize object."""
        super().__init__('Optics Configuration Adjustment', parent)
        self.prefix = _PVName(prefix)
        self.norm_config = None
        self.table_map = dict()
        self._setupUi()
        self._tunecorr = BOTuneCorr('Default_1')
        self._chromcorr = BOChromCorr('Default')

    def _setupUi(self):
        hlay = QHBoxLayout()
        self.settings = QGridLayout()
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
        self.sb_config = QSpinBox(self)
        self.l_configname = QLabel('', self)
        self.bt_edit = QPushButton('Edit', self)
        self.bt_load = QPushButton('Load', self)
        self.bt_save = QPushButton('Save', self)

        self.sb_config.setMinimum(1)
        self.sb_config.editingFinished.connect(self._handleConfigIndexChanged)
        self.l_configname.setFixedWidth(250)
        self.bt_edit.clicked.connect(self._showEditPopup)
        self.bt_load.clicked.connect(self._load)
        self.bt_save.clicked.connect(self._save)

        self.settings.addWidget(self.sb_config, 0, 0)
        self.settings.addWidget(self.l_configname, 0, 1)
        self.settings.addWidget(self.bt_edit, 1, 0, 1, 2)
        self.settings.addWidget(self.bt_load, 2, 0, 1, 2)
        self.settings.addWidget(self.bt_save, 3, 0, 1, 2)

    def _setupTuneVariation(self):
        label_tune = QLabel('<h4>Tune Variation</h4>', self)
        label_tune.setAlignment(Qt.AlignCenter)
        label_tune.setFixedHeight(48)

        label_deltaTuneX = QLabel('Δν<sub>x</sub>: ')
        label_deltaTuneX.setFixedWidth(48)
        self.sb_deltaTuneX = QDoubleSpinBox(self)
        self.sb_deltaTuneX.setDecimals(6)
        self.sb_deltaTuneX.setSingleStep(0.0001)
        self.sb_deltaTuneX.setFixedWidth(200)
        self.sb_deltaTuneX.editingFinished.connect(self._calculate_deltaKL)

        label_deltaTuneY = QLabel('Δν<sub>y</sub>: ')
        label_deltaTuneY.setFixedWidth(48)
        self.sb_deltaTuneY = QDoubleSpinBox(self)
        self.sb_deltaTuneY.setDecimals(6)
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
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 0, 2)
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
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 4, 2)
        self.tune_variation.addWidget(label_KL, 5, 0, 1, 5)
        self.tune_variation.addWidget(label_deltaKLQF, 6, 0)
        self.tune_variation.addWidget(self.l_deltaKLQF, 6, 1)
        self.tune_variation.addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 6, 2)
        self.tune_variation.addWidget(label_deltaKLQD, 6, 3)
        self.tune_variation.addWidget(self.l_deltaKLQD, 6, 4)
        self.tune_variation.addLayout(hlay_bt_apply, 7, 0, 1, 5)
        self.tune_variation.addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 8, 2)

    def _setupChromVariation(self):
        label_chrom = QLabel('<h4>Chromaticity Variation</h4>', self)
        label_chrom.setAlignment(Qt.AlignCenter)
        label_chrom.setFixedHeight(48)

        label_deltaChromX = QLabel('Δξ<sub>x</sub>: ')
        label_deltaChromX.setFixedWidth(48)
        self.sb_deltaChromX = QDoubleSpinBox(self)
        self.sb_deltaChromX.setDecimals(6)
        self.sb_deltaChromX.setSingleStep(0.0001)
        self.sb_deltaChromX.setFixedWidth(200)
        self.sb_deltaChromX.editingFinished.connect(self._calculate_deltaSL)

        label_deltaChromY = QLabel('Δξ<sub>y</sub>: ')
        label_deltaChromY.setFixedWidth(48)
        self.sb_deltaChromY = QDoubleSpinBox(self)
        self.sb_deltaChromY.setDecimals(6)
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
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 0, 2)
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
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 4, 2)
        self.chrom_variation.addWidget(label_SL, 5, 0, 1, 5)
        self.chrom_variation.addWidget(label_deltaSLSF, 6, 0)
        self.chrom_variation.addWidget(self.l_deltaSLSF, 6, 1)
        self.chrom_variation.addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 6, 2)
        self.chrom_variation.addWidget(label_deltaSLSD, 6, 3)
        self.chrom_variation.addWidget(self.l_deltaSLSD, 6, 4)
        self.chrom_variation.addLayout(hlay_bt_apply, 7, 0, 1, 5)
        self.chrom_variation.addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 8, 2)

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
        if not self.table_map:
            return
        config_idx = self.sb_config.value()
        for label, value in self.table_map['rows'].items():
            if config_idx == (value + 1):
                self.l_configname.setText(label)
                if label in ['Injection', 'Ejection']:
                    self.bt_edit.setEnabled(False)
                    self.bt_load.setEnabled(False)
                    self.bt_save.setEnabled(False)
                    self.norm_config = None
                    self.bt_load.setStyleSheet("")
                else:
                    self.bt_edit.setEnabled(True)
                    self.bt_load.setEnabled(True)
                    self.bt_save.setEnabled(True)
                    self.norm_config = ramp.BoosterNormalized(label)
                    self.bt_load.setStyleSheet("""background-color:#1F64FF;""")
                break
        self.sb_deltaTuneX.setValue(0)
        self.sb_deltaTuneY.setValue(0)
        self.sb_deltaChromX.setValue(0)
        self.sb_deltaChromY.setValue(0)

    def _showEditPopup(self):
        if self.norm_config is not None:
            self.editPopup = EditNormalizedConfig(self, self.norm_config)
            self.editPopup.editConfig.connect(self._handleEdit)
            self.editPopup.show()

    @pyqtSlot(dict)
    def _handleEdit(self, nconfig):
        for maname, value in nconfig.items():
            self.norm_config[maname] = value
        self.verifySync()

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
        self.verifySync()

    def _apply_orbitcorrection(self):
        # TODO: include orbit correction
        self.verifySync()

    def _load(self):
        if self.norm_config is not None:
            self.norm_config.configsrv_load()
            self.bt_load.setStyleSheet("")

            # set to zero all modifications
            self.sb_deltaTuneX.setValue(0)
            self.sb_deltaTuneY.setValue(0)
            self._deltaKL = [0.0, 0.0]
            self.l_deltaKLQF.setText('{:6f}'.format(self._deltaKL[0]))
            self.l_deltaKLQD.setText('{:6f}'.format(self._deltaKL[1]))

            self.sb_deltaChromX.setValue(0)
            self.sb_deltaChromY.setValue(0)
            self._deltaSL = [0.0, 0.0]
            self.l_deltaSLSF.setText('{:6f}'.format(self._deltaSL[0]))
            self.l_deltaSLSD.setText('{:6f}'.format(self._deltaSL[1]))

            # TODO: include orbit correction

            self.verifySync()

    def _save(self):
        if self.norm_config is not None:
            self.norm_config.configsrv_save()
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

    @pyqtSlot(dict)
    def getConfigIndices(self, table_map):
        """Update table_map and settings widget."""
        self.table_map = table_map
        self.sb_config.setMaximum(max(self.table_map['rows'].values()))
        normconfigname = self.l_configname.text()
        if normconfigname == '':
            return
        if normconfigname in self.table_map['rows'].keys():
            self.sb_config.setValue(self.table_map['rows'][normconfigname]+1)
        else:
            self.sb_config.setValue(self.table_map['rows']['Injection'])
            self.l_configname.setText('Injection')

    def verifySync(self):
        """Verify sync status related to ConfServer."""
        if self.norm_config is not None:
            if not self.norm_config.configsrv_synchronized:
                self.bt_save.setStyleSheet("""background-color: #1F64FF;""")
            else:
                self.bt_save.setStyleSheet("")
