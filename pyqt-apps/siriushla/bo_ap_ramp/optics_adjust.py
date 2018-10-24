"""Booster Ramp Control HLA: Optics Adjust Module."""

from qtpy.QtCore import Qt, Slot, Signal
from qtpy.QtWidgets import QGroupBox, QPushButton, QLabel, \
                           QHBoxLayout, QVBoxLayout, QGridLayout, \
                           QSizePolicy as QSzPlcy, QAction, \
                           QSpacerItem, QMenu
from siriuspy.ramp import ramp
from siriuspy.ramp.magnet import Magnet as _Magnet
from siriuspy.optics.opticscorr import BOTuneCorr, BOChromCorr
from siriuspy.servconf.util import \
    generate_config_name as _generate_config_name
from siriuspy.servconf import exceptions as _srvexceptions
from siriuspy.ramp.conn import ConnMagnets as _ConnMagnets, ConnRF as _ConnRF,\
                               ConnTiming as _ConnTiming, ConnSOFB as _ConnSOFB
from siriushla.bo_ap_ramp.auxiliar_classes import \
    EditNormalizedConfig as _EditNormalizedConfig, \
    NewRampConfigGetName as _NewRampConfigGetName, \
    MyDoubleSpinBox as _MyDoubleSpinBox, \
    MessageBox as _MessageBox


class OpticsAdjust(QGroupBox):
    """Widget to perform optics adjust in normalized configurations."""

    normConfigChanged = Signal(ramp.BoosterNormalized)

    def __init__(self, parent=None, prefix='', ramp_config=None):
        """Initialize object."""
        super().__init__('Normalized Configurations Optics Adjustments',
                         parent)
        self.prefix = prefix
        self.ramp_config = ramp_config
        self.norm_config = None
        self._table_map = dict()
        self._aux_magnets = dict()
        for ma in ramp.BoosterNormalized().manames:
            self._aux_magnets[ma] = _Magnet(ma)
        self._kicks = dict()
        self._corrfactorH = 100.0
        self._corrfactorV = 100.0
        self._setupUi()
        self._tunecorr = BOTuneCorr('Default_1')
        self._chromcorr = BOChromCorr('Default')
        self._conn_sofb = None

    def _setupUi(self):
        self.setMinimumHeight(500)
        self.settings = self._setupChooseConfig()
        self.tune_variation = self._setupTuneVariation()
        self.chrom_variation = self._setupChromVariation()
        self.orbit_correction = self._setupOrbitCorrection()

        lay = QHBoxLayout()
        lay.addItem(QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Preferred))
        lay.addLayout(self.settings)
        lay.addItem(QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Preferred))
        lay.addLayout(self.orbit_correction)
        lay.addItem(QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Preferred))
        lay.addLayout(self.tune_variation)
        lay.addItem(QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Preferred))
        lay.addLayout(self.chrom_variation)
        lay.addItem(QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Preferred))
        self.setLayout(lay)

    def _setupChooseConfig(self):
        l_confignr = QLabel('Config. number: ')
        self.sb_config = _MyDoubleSpinBox(self)
        self.sb_config.setMinimum(1)
        self.sb_config.setFixedWidth(80)
        self.sb_config.setSingleStep(1)
        self.sb_config.setDecimals(0)
        self.sb_config.editingFinished.connect(self._handleConfigIndexChanged)
        hlay_config = QHBoxLayout()
        hlay_config.addWidget(l_confignr)
        hlay_config.addWidget(self.sb_config)

        self.bt_edit = QPushButton('', self)
        self.bt_edit.setToolTip('Click to edit strengths')
        self.bt_edit.clicked.connect(self._showEditPopup)

        self.bt_update = QPushButton('Update in ramp config.')
        self.bt_update.clicked.connect(self._updateRampConfig)

        self.bt_server = QPushButton('Server', self)
        self.act_load = QAction('Load', self)
        self.act_load.triggered.connect(self._load)
        self.act_save = QAction('Save', self)
        self.act_save.triggered.connect(self._save)
        self.act_save_as = QAction('Save As...', self)
        self.act_save_as.triggered.connect(self._showSaveAsPopup)
        server_menu = QMenu(self)
        server_menu.addAction(self.act_load)
        server_menu.addAction(self.act_save)
        server_menu.addAction(self.act_save_as)
        self.bt_server.setMenu(server_menu)

        lay = QVBoxLayout()
        lay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding))
        lay.addLayout(hlay_config)
        lay.addWidget(self.bt_edit)
        lay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding))
        lay.addWidget(self.bt_update)
        lay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding))
        lay.addWidget(self.bt_server)
        lay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding))
        return lay

    def _setupTuneVariation(self):
        label_tune = QLabel('<h4>Tune Variation</h4>', self)
        label_tune.setAlignment(Qt.AlignCenter)
        label_tune.setFixedHeight(48)

        label_deltaTuneX = QLabel('Δν<sub>x</sub>: ')
        label_deltaTuneX.setFixedWidth(48)
        self.sb_deltaTuneX = _MyDoubleSpinBox(self)
        self.sb_deltaTuneX.setDecimals(6)
        self.sb_deltaTuneX.setMinimum(-1)
        self.sb_deltaTuneX.setMaximum(1)
        self.sb_deltaTuneX.setSingleStep(0.0001)
        self.sb_deltaTuneX.setFixedWidth(200)
        self.sb_deltaTuneX.editingFinished.connect(self._calculate_deltaKL)

        label_deltaTuneY = QLabel('Δν<sub>y</sub>: ')
        label_deltaTuneY.setFixedWidth(48)
        self.sb_deltaTuneY = _MyDoubleSpinBox(self)
        self.sb_deltaTuneY.setDecimals(6)
        self.sb_deltaTuneY.setMinimum(-1)
        self.sb_deltaTuneY.setMaximum(1)
        self.sb_deltaTuneY.setSingleStep(0.0001)
        self.sb_deltaTuneY.setFixedWidth(200)
        self.sb_deltaTuneY.editingFinished.connect(self._calculate_deltaKL)

        label_KL = QLabel('<h4>ΔKL [1/m]</h4>', self)
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

        lay = QGridLayout()
        lay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Expanding),
                    0, 2)
        lay.addWidget(label_tune, 1, 0, 1, 5)
        lay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 2, 2)
        lay.addWidget(label_deltaTuneX, 3, 0)
        lay.addWidget(self.sb_deltaTuneX, 3, 1)
        lay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 3, 2)
        lay.addWidget(label_deltaTuneY, 3, 3)
        lay.addWidget(self.sb_deltaTuneY, 3, 4)
        lay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Expanding),
                    4, 2)
        lay.addWidget(label_KL, 5, 0, 1, 5)
        lay.addWidget(label_deltaKLQF, 6, 0)
        lay.addWidget(self.l_deltaKLQF, 6, 1)
        lay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 6, 2)
        lay.addWidget(label_deltaKLQD, 6, 3)
        lay.addWidget(self.l_deltaKLQD, 6, 4)
        lay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Expanding),
                    7, 2)
        lay.addLayout(hlay_bt_apply, 8, 0, 1, 5)
        lay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Expanding),
                    9, 2)
        return lay

    def _setupChromVariation(self):
        label_chrom = QLabel('<h4>Chromaticity Variation</h4>', self)
        label_chrom.setAlignment(Qt.AlignCenter)
        label_chrom.setFixedHeight(48)

        label_deltaChromX = QLabel('Δξ<sub>x</sub>: ')
        label_deltaChromX.setFixedWidth(48)
        self.sb_deltaChromX = _MyDoubleSpinBox(self)
        self.sb_deltaChromX.setDecimals(6)
        self.sb_deltaChromX.setMinimum(-10)
        self.sb_deltaChromX.setMaximum(10)
        self.sb_deltaChromX.setSingleStep(0.0001)
        self.sb_deltaChromX.setFixedWidth(200)
        self.sb_deltaChromX.editingFinished.connect(self._calculate_deltaSL)

        label_deltaChromY = QLabel('Δξ<sub>y</sub>: ')
        label_deltaChromY.setFixedWidth(48)
        self.sb_deltaChromY = _MyDoubleSpinBox(self)
        self.sb_deltaChromY.setDecimals(6)
        self.sb_deltaChromY.setMinimum(-10)
        self.sb_deltaChromY.setMaximum(10)
        self.sb_deltaChromY.setSingleStep(0.0001)
        self.sb_deltaChromY.setFixedWidth(200)
        self.sb_deltaChromY.editingFinished.connect(self._calculate_deltaSL)

        label_SL = QLabel('<h4>ΔSL [1/m<sup>2</sup>]</h4>', self)
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

        lay = QGridLayout()
        lay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Expanding),
                    0, 2)
        lay.addWidget(label_chrom, 1, 0, 1, 5)
        lay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 2, 2)
        lay.addWidget(label_deltaChromX, 3, 0)
        lay.addWidget(self.sb_deltaChromX, 3, 1)
        lay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 3, 2)
        lay.addWidget(label_deltaChromY, 3, 3)
        lay.addWidget(self.sb_deltaChromY, 3, 4)
        lay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Expanding),
                    4, 2)
        lay.addWidget(label_SL, 5, 0, 1, 5)
        lay.addWidget(label_deltaSLSF, 6, 0)
        lay.addWidget(self.l_deltaSLSF, 6, 1)
        lay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 6, 2)
        lay.addWidget(label_deltaSLSD, 6, 3)
        lay.addWidget(self.l_deltaSLSD, 6, 4)
        lay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Expanding),
                    7, 2)
        lay.addLayout(hlay_bt_apply, 8, 0, 1, 5)
        lay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Expanding),
                    9, 2)
        return lay

    def _setupOrbitCorrection(self):
        label = QLabel('<h4>Orbit Correction</h4>', self)
        label.setAlignment(Qt.AlignCenter)
        label.setFixedHeight(48)

        self.bt_load_sofb_kicks = QPushButton('Load Kicks from SOFB', self)
        self.bt_load_sofb_kicks.clicked.connect(self._load_sofb_kicks)
        label_correctH = QLabel('Correct H', self)
        self.sb_correctH = _MyDoubleSpinBox(self)
        self.sb_correctH.setValue(self._corrfactorH)
        self.sb_correctH.setDecimals(1)
        self.sb_correctH.setMinimum(-10000)
        self.sb_correctH.setMaximum(10000)
        self.sb_correctH.setSingleStep(0.1)
        self.sb_correctH.setFixedWidth(200)
        labelH = QLabel('%', self)
        labelH.setFixedWidth(24)
        label_correctV = QLabel('Correct V', self)
        self.sb_correctV = _MyDoubleSpinBox(self)
        self.sb_correctV.setValue(self._corrfactorV)
        self.sb_correctV.setDecimals(1)
        self.sb_correctV.setMinimum(-10000)
        self.sb_correctV.setMaximum(10000)
        self.sb_correctV.setSingleStep(0.1)
        self.sb_correctV.setFixedWidth(200)
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

        lay = QGridLayout()
        lay.addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Expanding), 0, 0)
        lay.addWidget(label, 1, 0, 1, 3)
        lay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 2, 0)
        lay.addWidget(self.bt_load_sofb_kicks, 3, 0, 1, 3)
        lay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 4, 0)
        lay.addWidget(label_correctH, 5, 0)
        lay.addWidget(self.sb_correctH, 5, 1)
        lay.addWidget(labelH, 5, 2)
        lay.addItem(QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Fixed), 6, 0)
        lay.addWidget(label_correctV, 7, 0)
        lay.addWidget(self.sb_correctV, 7, 1)
        lay.addWidget(labelV, 7, 2)
        lay.addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Expanding), 8, 0)
        lay.addLayout(hlay_bt_apply, 9, 0, 1, 3)
        lay.addItem(
            QSpacerItem(20, 20, QSzPlcy.Fixed, QSzPlcy.Expanding), 10, 0)
        return lay

    def _handleConfigIndexChanged(self):
        if not self._table_map:
            return
        config_idx = int(self.sb_config.value())
        for value, label in self._table_map['rows'].items():
            if config_idx == (value + 1):
                self.bt_edit.setText(label)
                if label in ['Injection', 'Ejection']:
                    self.bt_edit.setEnabled(False)
                    self.bt_update.setEnabled(False)
                    self.act_load.setEnabled(False)
                    self.act_save.setEnabled(False)
                    self.act_save_as.setEnabled(False)
                    self.norm_config = None
                else:
                    self.bt_edit.setEnabled(True)
                    self.bt_update.setEnabled(True)
                    self.act_save.setEnabled(True)
                    self.act_save_as.setEnabled(True)
                    self.norm_config = self.ramp_config[label]
                    try:
                        if self.norm_config.configsrv_exist():
                            self.act_load.setEnabled(True)
                        else:
                            self.act_load.setEnabled(False)
                            self.verifySync()
                    except _srvexceptions.SrvError as e:
                        err_msg = _MessageBox(self, 'Error', str(e), 'Ok')
                        err_msg.open()
                break
        self._resetTuneChanges()
        self._resetChromChanges()
        self._resetOrbitChanges()

    def _showEditPopup(self):
        if self.norm_config is not None:
            norm_list = self.ramp_config.ps_normalized_configs
            for norm in norm_list:
                if norm[1] == self.norm_config.name:
                    time = norm[0]
                    break
            energy = self.ramp_config.ps_waveform_interp_energy(time)
            self._editPopup = _EditNormalizedConfig(
                self, self.norm_config, energyGeV=energy,
                aux_magnets=self._aux_magnets)
            self._editPopup.editConfig.connect(self._handleEdit)
            self._editPopup.cb_checklims.setFocus()
            self._editPopup.open()

    @Slot(dict)
    def _handleEdit(self, nconfig):
        for maname, value in nconfig.items():
            self.norm_config[maname] = value
        self.verifySync()

    def _updateRampConfig(self):
        if self.norm_config is not None:
            self.normConfigChanged.emit(self.norm_config)

    def _load(self):
        if self.norm_config is not None:
            try:
                self.norm_config.configsrv_load()
            except _srvexceptions.SrvError as e:
                err_msg = _MessageBox(self, 'Error', str(e), 'Ok')
                err_msg.open()
            else:
                self._resetTuneChanges()
                self._resetChromChanges()
                self._resetOrbitChanges()
                self.verifySync()

    def _save(self, new_name=None):
        if self.norm_config is None:
            return
        try:
            if self.norm_config.configsrv_exist():
                old_name = self.norm_config.name
                if not new_name:
                    new_name = _generate_config_name(old_name)
                self.norm_config.configsrv_save(new_name)
            else:
                self.norm_config.configsrv_save()
        except _srvexceptions.SrvError as e:
            err_msg = _MessageBox(self, 'Error', str(e), 'Ok')
            err_msg.open()
        finally:
            self.bt_edit.setText(self.norm_config.name)
            self.verifySync()

    def _showSaveAsPopup(self):
        if self.norm_config is None:
            return
        self._saveAsPopup = _NewRampConfigGetName(
            self.norm_config, 'bo_normalized', self, new_from_template=False)
        self._saveAsPopup.newConfigNameSignal.connect(self._save)
        self._saveAsPopup.open()

    def _calculate_deltaKL(self):
        if self.norm_config is None:
            return
        dtunex = self.sb_deltaTuneX.value()
        dtuney = self.sb_deltaTuneY.value()

        self._deltaKL = self._tunecorr.calculate_deltaKL([dtunex, dtuney])

        self.l_deltaKLQF.setText('{: 6f}'.format(self._deltaKL[0]))
        self.l_deltaKLQD.setText('{: 6f}'.format(self._deltaKL[1]))

    def _apply_deltaKL(self):
        if self.norm_config is None:
            return
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

        self.l_deltaSLSF.setText('{: 6f}'.format(self._deltaSL[0]))
        self.l_deltaSLSD.setText('{: 6f}'.format(self._deltaSL[1]))

    def _apply_deltaSL(self):
        if self.norm_config is None:
            return
        self.norm_config['BO-Fam:MA-SF'] += self._deltaSL[0]
        self.norm_config['BO-Fam:MA-SD'] += self._deltaSL[1]
        self._resetChromChanges()
        self.verifySync()

    def _load_sofb_kicks(self):
        if not self._conn_sofb:
            return
        if not self._conn_sofb.connected:
            warn_msg = _MessageBox(
                self, 'Not Connected',
                'There are not connected PVs!', 'Ok')
            warn_msg.exec_()
            return
        self._kicks = self._conn_sofb.get_kicks()

    def _apply_orbitcorrection(self):
        if not self._kicks or self.norm_config is None:
            return
        self._corrfactorH = self.sb_correctH.value()
        self._corrfactorV = self.sb_correctV.value()
        for maname, kick in self._kicks:
            corr_factor = self._corrfactorV if 'CV' in maname \
                          else self._corrfactorH
            self.norm_config[maname] = kick*corr_factor
        self._resetOrbitChanges()
        self.verifySync()

    def _resetTuneChanges(self):
        self.sb_deltaTuneX.setValue(0)
        self.sb_deltaTuneY.setValue(0)
        self._deltaKL = [0.0, 0.0]
        self.l_deltaKLQF.setText('{: 6f}'.format(self._deltaKL[0]))
        self.l_deltaKLQD.setText('{: 6f}'.format(self._deltaKL[1]))

    def _resetChromChanges(self):
        self.sb_deltaChromX.setValue(0)
        self.sb_deltaChromY.setValue(0)
        self._deltaSL = [0.0, 0.0]
        self.l_deltaSLSF.setText('{: 6f}'.format(self._deltaSL[0]))
        self.l_deltaSLSD.setText('{: 6f}'.format(self._deltaSL[1]))

    def _resetOrbitChanges(self):
        self._kicks = dict()
        self._corrfactorH = 100.0
        self._corrfactorV = 100.0
        self.sb_correctH.setValue(100.0)
        self.sb_correctV.setValue(100.0)

    @Slot(dict)
    def getConfigIndices(self, table_map):
        """Update table_map and settings widget."""
        self._table_map = table_map
        self.sb_config.setMaximum(max(self._table_map['rows'].keys())+1)
        normconfigname = self.bt_edit.text()
        if normconfigname == '':
            return
        if normconfigname in self._table_map['rows'].values():
            name = normconfigname
        else:
            name = 'Injection'
        value = [row for row, lb in self._table_map['rows'].items()
                 if lb == name]
        self.sb_config.setValue(value[0]+1)
        self.bt_edit.setText(name)
        self._handleConfigIndexChanged()

    @Slot(ramp.BoosterRamp)
    def handleLoadRampConfig(self, ramp_config):
        """Update all widgets in loading BoosterRamp config."""
        self.ramp_config = ramp_config
        if self.norm_config is not None and self.norm_config.name in \
                ramp_config.ps_normalized_configs_names:
            self.norm_config = self.ramp_config[self.norm_config.name]

    @Slot(list)
    def handleUpdateSettings(self, settings):
        """Update settings."""
        self._tunecorr = BOTuneCorr(settings[0])
        self._chromcorr = BOChromCorr(settings[1])

    @Slot(_ConnMagnets, _ConnTiming, _ConnRF, _ConnSOFB)
    def getConnectors(self, conn_magnet, conn_timing, conn_rf, conn_sofb):
        """Receive connectors."""
        self._conn_sofb = conn_sofb

    def verifySync(self):
        """Verify sync status related to ConfServer."""
        if self.norm_config is not None:
            if not self.norm_config.configsrv_synchronized:
                self.act_save.setEnabled(True)
            else:
                self.act_save.setEnabled(False)
