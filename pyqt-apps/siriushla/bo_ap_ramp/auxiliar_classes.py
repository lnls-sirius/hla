"""Booster Ramp Control HLA: Auxiliar Classes Module."""

from qtpy.QtCore import Qt, Signal, Slot, QLocale
from qtpy.QtWidgets import QLabel, QWidget, QScrollArea, QAbstractItemView, \
                           QHBoxLayout, QVBoxLayout, QGridLayout, QLineEdit, \
                           QPushButton, QTableWidget, QTableWidgetItem, \
                           QRadioButton, QFormLayout, QDoubleSpinBox, \
                           QComboBox, QSpinBox, QStyledItemDelegate, \
                           QSpacerItem, QSizePolicy as QSzPlcy, QCheckBox, \
                           QTabWidget, QGroupBox
from pydm.widgets import PyDMLabel, PyDMSpinbox, PyDMEnumComboBox, \
                         PyDMPushButton
from siriushla.widgets.windows import SiriusDialog
from siriushla.widgets import PyDMStateButton, SiriusConnectionSignal, \
                              SiriusLedAlert, PyDMLedMultiChannel
from siriushla.as_ap_servconf import LoadConfiguration as _LoadConfiguration, \
                                     SaveConfiguration as _SaveConfiguration
from siriushla import util as _hlautil
from siriushla.as_ti_control.hl_trigger import HLTriggerDetailed
from siriuspy.servconf.srvconfig import ConnConfigService as _ConnConfigService
from siriuspy.servconf.util import \
    generate_config_name as _generate_config_name
from siriuspy.servconf import exceptions as _srvexceptions
from siriuspy.ramp import ramp


DCCT_MEASMODE_NORMAL = 1
DCCT_MEASMODE_FAST = 2


class LoadRampConfig(_LoadConfiguration):
    """Auxiliar window to get a ramp config name to load."""

    loadSignal = Signal()
    saveSignal = Signal()

    def __init__(self, ramp_config, parent=None):
        """Initialize object."""
        self.ramp_config = ramp_config
        super().__init__('bo_ramp', parent)
        self.setWindowTitle('Load ramp configuration from server')

    @Slot()
    def _load_configuration(self):
        name = self._get_config_name()
        if self.ramp_config is not None:
            if not self.ramp_config.configsrv_synchronized:
                save_changes = MessageBox(
                    self, 'Save changes?',
                    'There are unsaved changes in {}. \n'
                    'Do you want to save?'.format(name),
                    'Yes', 'Cancel')
                save_changes.acceptedSignal.connect(self._saveChanges)
                save_changes.exec_()

            if name != self.ramp_config.name:
                self.configname.emit(name)
            else:
                self.loadSignal.emit()
        else:
            self.configname.emit(name)
        self.accept()

    def _saveChanges(self):
        self.saveSignal.emit()


class NewRampConfigGetName(_SaveConfiguration):
    """Auxiliar window to get a configuration name to create a new one."""

    saveSignal = Signal()

    def __init__(self, config, config_type, parent=None,
                 new_from_template=True):
        """Initialize object."""
        super().__init__(config_type, parent)
        self.config = config
        self.config_type = config_type
        self._new_from_template = new_from_template
        if new_from_template:
            self.setWindowTitle('New config from template')
            self.save_button.setText('Create')
        else:
            self.setWindowTitle('Save current config as...')
            self.save_button.setText('Save as...')

    @Slot()
    def _load_configuration(self):
        name = self.search_lineedit.text()
        if (self._new_from_template and (self.config is not None)):
            if not self.config.configsrv_synchronized:
                save_changes = MessageBox(
                    self, 'Save changes?',
                    'There are unsaved changes in {}. \n'
                    'Do you want to save?'.format(name),
                    'Yes', 'Cancel')
                save_changes.acceptedSignal.connect(self._saveChanges)
                save_changes.exec_()
            else:
                self.configname.emit(name)
                self.accept()
        else:
            self.configname.emit(name)
            self.accept()

    def _saveChanges(self):
        self.saveSignal.emit()


class InsertNormalizedConfig(SiriusDialog):
    """Auxiliar window to insert a new normalized config."""

    insertConfig = Signal(list)

    def __init__(self, parent):
        """Initialize object."""
        super().__init__(parent)
        self.normalized_config = ramp.BoosterNormalized()
        self.setWindowTitle('Insert Normalized Configuration')
        self._setupUi()

    def _setupUi(self):
        self.rb_interp = QRadioButton('By interpolation')
        self.rb_confsrv = QRadioButton(
            'By taking an existing one from Config Server')
        self.rb_create = QRadioButton(
            'By creating a new nominal configuration')
        self.config_data = QWidget()
        self._setupConfigDataWidget()

        self.rb_interp.toggled.connect(self.interp_settings.setVisible)
        self.rb_interp.setChecked(True)
        self.rb_confsrv.toggled.connect(self.confsrv_settings.setVisible)
        self.rb_create.toggled.connect(self.create_settings.setVisible)

        vlay = QVBoxLayout()
        vlay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding))
        vlay.addWidget(
            QLabel('<h4>Insert a Normalized Configuration</h4>', self),
            alignment=Qt.AlignCenter)
        vlay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding))
        vlay.addWidget(self.rb_interp)
        vlay.addWidget(self.rb_confsrv)
        vlay.addWidget(self.rb_create)
        vlay.addItem(QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding))
        vlay.addWidget(self.config_data)

        self.setLayout(vlay)

    def _setupConfigDataWidget(self):
        vlay = QVBoxLayout()
        self.interp_settings = QWidget()
        self.confsrv_settings = QWidget()
        self.create_settings = QWidget()
        self.confsrv_settings.setVisible(False)
        self.create_settings.setVisible(False)
        vlay.addWidget(self.interp_settings)
        vlay.addWidget(self.confsrv_settings)
        vlay.addWidget(self.create_settings)
        self.config_data.setLayout(vlay)
        self.interp_settings.setFixedSize(600, 160)
        self.confsrv_settings.setFixedSize(600, 160)
        self.create_settings.setFixedSize(600, 160)

        # to insert interpolating existing norm configs
        flay_interp = QFormLayout()
        self.le_interp_name = QLineEdit(self)
        self.le_interp_name.setText(_generate_config_name())
        self.sb_interp_time = QDoubleSpinBox(self)
        self.sb_interp_time.setMaximum(490)
        self.sb_interp_time.setDecimals(6)
        self.bt_interp = QPushButton('Insert', self)
        self.bt_interp.setAutoDefault(False)
        self.bt_interp.setDefault(False)
        self.bt_interp.clicked.connect(self._emitInsertConfigData)
        flay_interp.addRow(QLabel('Name: ', self), self.le_interp_name)
        flay_interp.addRow(QLabel('Time: ', self), self.sb_interp_time)
        flay_interp.addRow(self.bt_interp)

        # to insert a new norm config from an existing one
        flay_confsrv = QFormLayout()
        self.le_confsrv_name = _ConfigLineEdit(self)
        self.sb_confsrv_time = QDoubleSpinBox(self)
        self.sb_confsrv_time.setMaximum(490)
        self.sb_confsrv_time.setDecimals(6)
        self.bt_confsrv = QPushButton('Insert', self)
        self.bt_confsrv.setAutoDefault(False)
        self.bt_confsrv.setDefault(False)
        self.bt_confsrv.clicked.connect(self._emitInsertConfigData)
        flay_confsrv.addRow(QLabel('Name: ', self), self.le_confsrv_name)
        flay_confsrv.addRow(QLabel('Time: ', self), self.sb_confsrv_time)
        flay_confsrv.addRow(self.bt_confsrv)

        # to insert a new norm config equal to template
        flay_create = QFormLayout()
        self.le_create_name = QLineEdit(self)
        self.le_create_name.setText(_generate_config_name())
        self.sb_create_time = QDoubleSpinBox(self)
        self.sb_create_time.setDecimals(6)
        self.sb_create_time.setMaximum(490)
        self.bt_create = QPushButton('Insert', self)
        self.bt_create.setAutoDefault(False)
        self.bt_create.setDefault(False)
        self.bt_create.clicked.connect(self._emitInsertConfigData)
        flay_create.addRow(QLabel('Name: ', self), self.le_create_name)
        flay_create.addRow(QLabel('Time: ', self), self.sb_create_time)
        flay_create.addRow(self.bt_create)

        self.interp_settings.setLayout(flay_interp)
        self.confsrv_settings.setLayout(flay_confsrv)
        self.create_settings.setLayout(flay_create)

    def _showLoadConfigPopup(self):
        popup = _LoadConfiguration('bo_normalized')
        popup.configname.connect(self.le_confsrv_name.setText)
        popup.exec_()

    def _emitInsertConfigData(self):
        sender = self.sender()
        data = list()
        if sender is self.bt_interp:
            time = self.sb_interp_time.value()
            name = self.le_interp_name.text()
            nconfig = None
        elif sender is self.bt_confsrv:
            time = self.sb_confsrv_time.value()
            name = self.le_confsrv_name.text()
            nconfig = None
            try:
                n = ramp.BoosterNormalized(name)
                n.configsrv_load()
                nconfig = n.configuration
            except _srvexceptions.SrvError as e:
                err_msg = MessageBox(self, 'Error', str(e), 'Ok')
                err_msg.open()
        elif sender is self.bt_create:
            time = self.sb_create_time.value()
            name = self.le_create_name.text()
            nconfig = self.normalized_config.get_config_type_template()
        data = [time, name, nconfig]
        self.insertConfig.emit(data)
        self.close()


class DeleteNormalizedConfig(SiriusDialog):
    """Auxiliar window to delete a normalized config."""

    deleteConfig = Signal(str)

    def __init__(self, parent, table_map, selected_item):
        """Initialize object."""
        super().__init__(parent)
        self.normalized_config = ramp.BoosterNormalized()
        self.setWindowTitle('Delete Normalized Configuration')
        self.table_map = table_map
        self.selected_item = selected_item
        self._setupUi()

    def _setupUi(self):
        glay = QGridLayout()
        label = QLabel('<h4>Delete a Normalized Configuration</h4>', self)
        label.setAlignment(Qt.AlignCenter)
        glay.addWidget(label, 0, 0, 1, 2)

        self.sb_confignumber = QSpinBox(self)
        self.sb_confignumber.setMinimum(1)
        self.sb_confignumber.setMaximum(max(self.table_map['rows'].keys())+1)
        self.sb_confignumber.setMaximumWidth(150)
        self.sb_confignumber.valueChanged.connect(self._searchConfigByIndex)
        self.bt_delete = QPushButton('Delete', self)
        self.bt_delete.setAutoDefault(False)
        self.bt_delete.setDefault(False)
        self.bt_delete.clicked.connect(self._emitDeleteConfigData)
        self.l_configname = QLabel('', self)
        self.l_configname.setSizePolicy(QSzPlcy.MinimumExpanding,
                                        QSzPlcy.Preferred)
        if self.selected_item:
            row = self.selected_item[0].row()
        else:
            row = 0
        self.sb_confignumber.setValue(row+1)
        self._searchConfigByIndex(row+1)

        glay.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 1, 0)
        glay.addWidget(self.sb_confignumber, 2, 0)
        glay.addWidget(self.l_configname, 2, 1)
        glay.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 3, 0)
        glay.addWidget(self.bt_delete, 4, 0, 1, 2)

        self.setLayout(glay)

    @Slot(int)
    def _searchConfigByIndex(self, config_idx):
        label = self.table_map['rows'][config_idx - 1]
        self.l_configname.setText(label)
        if label in ['Injection', 'Ejection']:
            self.bt_delete.setEnabled(False)
        else:
            self.bt_delete.setEnabled(True)

    def _emitDeleteConfigData(self):
        self.deleteConfig.emit(self.l_configname.text())
        self.close()


class EditNormalizedConfig(SiriusDialog):
    """Auxiliar window to edit an existing normalized config."""

    editConfig = Signal(dict)

    def __init__(self, parent, norm_config, energyGeV, aux_magnets):
        """Initialize object."""
        super().__init__(parent)
        self.norm_config = norm_config
        self.energy = energyGeV
        self._aux_magnets = aux_magnets
        self.setWindowTitle('Edit Normalized Configuration')
        self._setupUi()

    def _setupUi(self):
        glay = QGridLayout()
        label = QLabel(self.norm_config.name, self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""font-weight: bold;""")

        scrollarea = QScrollArea()
        scrollarea.setFixedWidth(500)
        self.data = QWidget()
        flay_configdata = QFormLayout()
        manames = self.norm_config.get_config_type_template().keys()
        for ma in manames:
            ma_value = MyDoubleSpinBox(self.data)
            ma_value.setDecimals(6)
            ma_value.setValue(self.norm_config[ma])
            ma_value.setObjectName(ma)
            ma_value.setFixedWidth(200)

            aux = self._aux_magnets[ma]
            currs = (aux.current_min, aux.current_max)
            lims = aux.conv_current_2_strength(
                currents=currs, strengths_dipole=self.energy)
            ma_value.setMinimum(min(lims))
            ma_value.setMaximum(max(lims))

            flay_configdata.addRow(QLabel(ma + ': ', self), ma_value)
        self.data.setLayout(flay_configdata)
        scrollarea.setWidget(self.data)

        self.cb_checklims = QCheckBox('Set limits according to energy', self)
        self.cb_checklims.setChecked(True)
        self.cb_checklims.stateChanged.connect(self._handleStrengtsLimits)
        self.bt_apply = QPushButton('Apply Changes', self)
        self.bt_apply.setAutoDefault(False)
        self.bt_apply.setDefault(False)
        self.bt_apply.clicked.connect(self._emitConfigChanges)
        self.bt_cancel = QPushButton('Cancel', self)
        self.bt_cancel.setAutoDefault(False)
        self.bt_cancel.setDefault(False)
        self.bt_cancel.clicked.connect(self.close)

        glay.addWidget(label, 0, 0, 1, 2)
        glay.addWidget(scrollarea, 1, 0, 1, 2)
        glay.addWidget(self.cb_checklims, 2, 0, 1, 2)
        glay.addWidget(self.bt_apply, 3, 0)
        glay.addWidget(self.bt_cancel, 3, 1)

        self.setLayout(glay)

    def _handleStrengtsLimits(self, state):
        manames = self.norm_config.get_config_type_template().keys()
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

    def _emitConfigChanges(self):
        config_template = self.norm_config.get_config_type_template()
        nconfig = dict()
        for ma in config_template.keys():
            w = self.data.findChild(QDoubleSpinBox, name=ma)
            nconfig[ma] = w.value()
        self.editConfig.emit(nconfig)
        self.close()


class OpticsAdjustSettings(SiriusDialog):
    """Auxiliar window to optics adjust settings."""

    updateSettings = Signal(list)

    def __init__(self, tuneconfig_currname, chromconfig_currname, parent=None):
        """Initialize object."""
        super().__init__(parent)
        self.setWindowTitle('Optics Adjust Settings')
        self.tuneconfig_currname = tuneconfig_currname
        self.chromconfig_currname = chromconfig_currname
        self.conn_tuneparams = _ConnConfigService('bo_tunecorr_params')
        self.conn_chromparams = _ConnConfigService('bo_chromcorr_params')
        self._setupUi()

        try:
            _, metadata = self.conn_tuneparams.config_find()
            for m in metadata:
                self.cb_tuneconfig.addItem(m['name'])

            _, metadata = self.conn_chromparams.config_find()
            for m in metadata:
                self.cb_chromconfig.addItem(m['name'])
        except _srvexceptions.SrvError as e:
            err_msg = MessageBox(self, 'Error', str(e), 'Ok')
            err_msg.open()
        finally:
            self.cb_tuneconfig.setCurrentText(self.tuneconfig_currname)
            self._showTuneConfigData()
            self.cb_chromconfig.setCurrentText(self.chromconfig_currname)
            self._showChromConfigData()

    def _setupUi(self):
        self.tune_settings = QWidget(self)
        self.tune_settings.setLayout(self._setupTuneSettings())
        self.chrom_settings = QWidget(self)
        self.chrom_settings.setLayout(self._setupChromSettings())
        self.bt_apply = QPushButton('Apply Settings', self)
        self.bt_apply.setFixedWidth(250)
        self.bt_apply.clicked.connect(self._emitSettings)
        hlay_apply = QHBoxLayout()
        hlay_apply.addItem(
            QSpacerItem(20, 60, QSzPlcy.Expanding, QSzPlcy.Fixed))
        hlay_apply.addWidget(self.bt_apply)

        tabs = QTabWidget(self)
        tabs.addTab(self.tune_settings, 'Tune')
        tabs.addTab(self.chrom_settings, 'Chromaticity')

        lay = QVBoxLayout()
        lay.addWidget(tabs)
        lay.addLayout(hlay_apply)

        self.setLayout(lay)

    def _setupTuneSettings(self):
        l_tuneconfig = QLabel('<h3>Tune Variation Config</h3>', self)
        l_tuneconfig.setAlignment(Qt.AlignCenter)
        self.cb_tuneconfig = QComboBox(self)
        self.cb_tuneconfig.setEditable(True)
        self.cb_tuneconfig.currentTextChanged.connect(self._showTuneConfigData)

        label_tunemat = QLabel('<h4>Matrix</h4>', self)
        label_tunemat.setAlignment(Qt.AlignCenter)
        self.table_tunemat = QTableWidget(self)
        self.table_tunemat.setFixedSize(686, 130)
        self.table_tunemat.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table_tunemat.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_tunemat.setRowCount(2)
        self.table_tunemat.setColumnCount(2)
        self.table_tunemat.setVerticalHeaderLabels(['  X', '  Y'])
        self.table_tunemat.setHorizontalHeaderLabels(['QF', 'QD'])
        self.table_tunemat.horizontalHeader().setDefaultSectionSize(320)
        self.table_tunemat.verticalHeader().setDefaultSectionSize(48)
        self.table_tunemat.setStyleSheet("background-color: #efebe7;")

        label_nomKL = QLabel('<h4>Nominal KL</h4>')
        label_nomKL.setAlignment(Qt.AlignCenter)
        self.table_nomKL = QTableWidget(self)
        self.table_nomKL.setFixedSize(685, 85)
        self.table_nomKL.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table_nomKL.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_nomKL.setRowCount(1)
        self.table_nomKL.setColumnCount(2)
        self.table_nomKL.setVerticalHeaderLabels(['KL'])
        self.table_nomKL.setHorizontalHeaderLabels(['QF', 'QD'])
        self.table_nomKL.horizontalHeader().setDefaultSectionSize(320)
        self.table_nomKL.verticalHeader().setDefaultSectionSize(48)
        self.table_nomKL.setStyleSheet("background-color: #efebe7;")

        lay = QVBoxLayout()
        lay.addWidget(l_tuneconfig)
        lay.addWidget(self.cb_tuneconfig)
        lay.addItem(QSpacerItem(20, 10, QSzPlcy.Fixed, QSzPlcy.Expanding))
        lay.addWidget(label_tunemat)
        lay.addWidget(self.table_tunemat)
        lay.addItem(QSpacerItem(20, 10, QSzPlcy.Fixed, QSzPlcy.Expanding))
        lay.addWidget(label_nomKL)
        lay.addWidget(self.table_nomKL)
        lay.addItem(
            QSpacerItem(20, 101, QSzPlcy.Fixed, QSzPlcy.MinimumExpanding))

        return lay

    def _setupChromSettings(self):
        l_chromconfig = QLabel('<h3>Chromaticity Variation Config</h3>', self)
        l_chromconfig.setAlignment(Qt.AlignCenter)
        self.cb_chromconfig = QComboBox(self)
        self.cb_chromconfig.setEditable(True)
        self.cb_chromconfig.currentTextChanged.connect(
            self._showChromConfigData)

        l_chrommat = QLabel('<h4>Matrix</h4>', self)
        l_chrommat.setAlignment(Qt.AlignCenter)
        self.table_chrommat = QTableWidget(self)
        self.table_chrommat.setFixedSize(686, 130)
        self.table_chrommat.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table_chrommat.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_chrommat.setRowCount(2)
        self.table_chrommat.setColumnCount(2)
        self.table_chrommat.setVerticalHeaderLabels(['  X', '  Y'])
        self.table_chrommat.setHorizontalHeaderLabels(['SF', 'SD'])
        self.table_chrommat.horizontalHeader().setDefaultSectionSize(320)
        self.table_chrommat.verticalHeader().setDefaultSectionSize(48)
        self.table_chrommat.setStyleSheet("background-color: #efebe7;")

        l_nomSL = QLabel('<h4>Nominal SL</h4>')
        l_nomSL.setAlignment(Qt.AlignCenter)
        self.table_nomSL = QTableWidget(self)
        self.table_nomSL.setFixedSize(683, 85)
        self.table_nomSL.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table_nomSL.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_nomSL.setRowCount(1)
        self.table_nomSL.setColumnCount(2)
        self.table_nomSL.setVerticalHeaderLabels(['SL'])
        self.table_nomSL.setHorizontalHeaderLabels(['SF', 'SD'])
        self.table_nomSL.horizontalHeader().setDefaultSectionSize(320)
        self.table_nomSL.verticalHeader().setDefaultSectionSize(48)
        self.table_nomSL.setStyleSheet("background-color: #efebe7;")

        l_nomchrom = QLabel('<h4>Nominal Chrom</h4>')
        l_nomchrom.setAlignment(Qt.AlignCenter)
        self.label_nomchrom = QLabel()
        self.label_nomchrom.setMinimumHeight(48)
        self.label_nomchrom.setAlignment(Qt.AlignCenter)

        lay = QVBoxLayout()
        lay.addWidget(l_chromconfig)
        lay.addWidget(self.cb_chromconfig)
        lay.addItem(QSpacerItem(20, 10, QSzPlcy.Fixed, QSzPlcy.Expanding))
        lay.addWidget(l_chrommat)
        lay.addWidget(self.table_chrommat)
        lay.addItem(QSpacerItem(20, 10, QSzPlcy.Fixed, QSzPlcy.Expanding))
        lay.addWidget(l_nomSL)
        lay.addWidget(self.table_nomSL)
        lay.addItem(QSpacerItem(20, 10, QSzPlcy.Fixed, QSzPlcy.Expanding))
        lay.addWidget(l_nomchrom)
        lay.addWidget(self.label_nomchrom)

        return lay

    @Slot(str)
    def _showTuneConfigData(self):
        try:
            config, _ = self.conn_tuneparams.config_get(
                name=self.tuneconfig_currname)
            mat = config['matrix']
            nomKL = config['nominal KLs']
        except _srvexceptions.SrvError as e:
            err_msg = MessageBox(self, 'Error', str(e), 'Ok')
            err_msg.open()
        else:
            self.table_tunemat.setItem(0, 0, QTableWidgetItem(str(mat[0][0])))
            self.table_tunemat.setItem(0, 1, QTableWidgetItem(str(mat[0][1])))
            self.table_tunemat.setItem(1, 0, QTableWidgetItem(str(mat[1][0])))
            self.table_tunemat.setItem(1, 1, QTableWidgetItem(str(mat[1][1])))
            self.table_tunemat.item(0, 0).setFlags(Qt.ItemIsEnabled)
            self.table_tunemat.item(0, 1).setFlags(Qt.ItemIsEnabled)
            self.table_tunemat.item(1, 0).setFlags(Qt.ItemIsEnabled)
            self.table_tunemat.item(1, 1).setFlags(Qt.ItemIsEnabled)
            self.table_nomKL.setItem(0, 0, QTableWidgetItem(str(nomKL[0])))
            self.table_nomKL.setItem(0, 1, QTableWidgetItem(str(nomKL[1])))
            self.table_nomKL.item(0, 0).setFlags(Qt.ItemIsEnabled)
            self.table_nomKL.item(0, 1).setFlags(Qt.ItemIsEnabled)

    @Slot(str)
    def _showChromConfigData(self):
        try:
            config, _ = self.conn_chromparams.config_get(
                name=self.chromconfig_currname)
            mat = config['matrix']
            nomSL = config['nominal SLs']
            nomChrom = config['nominal chrom']
        except _srvexceptions.SrvError as e:
            err_msg = MessageBox(self, 'Error', str(e), 'Ok')
            err_msg.open()
        else:
            self.table_chrommat.setItem(0, 0, QTableWidgetItem(str(mat[0][0])))
            self.table_chrommat.setItem(0, 1, QTableWidgetItem(str(mat[0][1])))
            self.table_chrommat.setItem(1, 0, QTableWidgetItem(str(mat[1][0])))
            self.table_chrommat.setItem(1, 1, QTableWidgetItem(str(mat[1][1])))
            self.table_chrommat.item(0, 0).setFlags(Qt.ItemIsEnabled)
            self.table_chrommat.item(0, 1).setFlags(Qt.ItemIsEnabled)
            self.table_chrommat.item(1, 0).setFlags(Qt.ItemIsEnabled)
            self.table_chrommat.item(1, 1).setFlags(Qt.ItemIsEnabled)
            self.table_nomSL.setItem(0, 0, QTableWidgetItem(str(nomSL[0])))
            self.table_nomSL.setItem(0, 1, QTableWidgetItem(str(nomSL[1])))
            self.table_nomSL.item(0, 0).setFlags(Qt.ItemIsEnabled)
            self.table_nomSL.item(0, 1).setFlags(Qt.ItemIsEnabled)
            self.label_nomchrom.setText(str(nomChrom))

    def _emitSettings(self):
        tuneconfig_name = self.cb_tuneconfig.currentText()
        chromconfig_name = self.cb_chromconfig.currentText()
        self.updateSettings.emit([tuneconfig_name, chromconfig_name])
        self.close()


class DiagnosisSettings(SiriusDialog):
    """Auxiliar window to diagnosis settings."""

    updateSettings = Signal(list)

    def __init__(self, parent, prefix, injcurr_idx, ejecurr_idx):
        """Initialize object."""
        super().__init__(parent)
        self.setWindowTitle('Diagnosis Settings')
        self.prefix = prefix
        self.injcurr_idx = injcurr_idx
        self.ejecurr_idx = ejecurr_idx
        self._setupUi()

    def _setupUi(self):
        self.dcct_prefix = 'ca://'+self.prefix+'BO-35D:DI-DCCT:'

        l_dcctacq = QLabel('<h3>Ramp Diagnosis Settings</h3>', self,
                           alignment=Qt.AlignCenter)

        self.gbox_reliablemeas = self._setupReliableMeasWidget()
        self.gbox_generalsettings = self._setupDCCTGeneralSettingsWidget()

        self.mode_channel = SiriusConnectionSignal(
            self.dcct_prefix+'MeasMode-Sts')
        self.mode_channel.new_value_signal.connect(self._showMeasModeSettings)
        self.gbox_normalmode = self._setupDCCTNormalMeasSettingsWidget()
        self.gbox_fastmode = self._setupDCCTFastMeasSettingsWidget()
        lay_mode = QGridLayout()
        lay_mode.addWidget(self.gbox_normalmode, 0, 0)
        lay_mode.addWidget(self.gbox_fastmode, 0, 0)

        self.gbox_effparams = self._setupRampEffIndicesWidget()

        self.bt_apply = QPushButton('Apply settings', self)
        self.bt_apply.clicked.connect(self._emitSettings)
        self.bt_apply.setAutoDefault(False)
        self.bt_apply.setDefault(False)
        hlay_apply = QHBoxLayout()
        hlay_apply.addItem(QSpacerItem(4, 2, QSzPlcy.Expanding, QSzPlcy.Fixed))
        hlay_apply.addWidget(self.bt_apply)

        lay = QVBoxLayout()
        lay.addWidget(l_dcctacq)
        lay.addWidget(self.gbox_reliablemeas)
        lay.addWidget(self.gbox_generalsettings)
        lay.addLayout(lay_mode)
        lay.addWidget(self.gbox_effparams)
        lay.addLayout(hlay_apply)
        lay.setSpacing(20)
        self.setLayout(lay)

    def _setupReliableMeasWidget(self):
        reliablemeas_channel = SiriusConnectionSignal(
            self.dcct_prefix+'ReliableMeasLabels-Mon')
        reliablemeas_channel.new_value_signal.connect(
            self._updateReliableMeasLabels)

        gbox_reliablemeas = _GroupBoxWithChannel(
            'DCCT Measure Reliability Status', self, [reliablemeas_channel])
        gbox_reliablemeas.setSizePolicy(QSzPlcy.Minimum, QSzPlcy.Fixed)

        self.label_reliablemeas0 = QLabel('', self)
        self.led_ReliableMeas0 = SiriusLedAlert(
            parent=self, init_channel=self.dcct_prefix+'ReliableMeas-Mon',
            bit=0)
        self.led_ReliableMeas0.setFixedWidth(48)
        self.label_reliablemeas1 = QLabel('', self)
        self.led_ReliableMeas1 = SiriusLedAlert(
            parent=self, init_channel=self.dcct_prefix+'ReliableMeas-Mon',
            bit=1)
        self.led_ReliableMeas1.setFixedWidth(48)
        self.label_reliablemeas2 = QLabel('', self)
        self.led_ReliableMeas2 = SiriusLedAlert(
            parent=self, init_channel=self.dcct_prefix+'ReliableMeas-Mon',
            bit=2)
        self.led_ReliableMeas2.setFixedWidth(48)
        lay_reliablemeas = QGridLayout()
        lay_reliablemeas.addWidget(self.led_ReliableMeas0, 0, 0)
        lay_reliablemeas.addWidget(self.label_reliablemeas0, 0, 1)
        lay_reliablemeas.addWidget(self.led_ReliableMeas1, 1, 0)
        lay_reliablemeas.addWidget(self.label_reliablemeas1, 1, 1)
        lay_reliablemeas.addWidget(self.led_ReliableMeas2, 2, 0)
        lay_reliablemeas.addWidget(self.label_reliablemeas2, 2, 1)
        gbox_reliablemeas.setLayout(lay_reliablemeas)
        return gbox_reliablemeas

    def _setupDCCTGeneralSettingsWidget(self):
        gbox_generalsettings = QGroupBox(
            'DCCT General Measurement Settings', self)

        l_measmode = QLabel('Measurement Mode: ', self)
        self.pydmenumcombobox_MeasMode = PyDMEnumComboBox(
            parent=self, init_channel=self.dcct_prefix+'MeasMode-Sel')
        self.pydmenumcombobox_MeasMode.setFixedSize(220, 40)
        self.pydmlabel_MeasMode = PyDMLabel(
            parent=self, init_channel=self.dcct_prefix+'MeasMode-Sts')
        hlay_measmode = QHBoxLayout()
        hlay_measmode.addWidget(self.pydmenumcombobox_MeasMode)
        hlay_measmode.addWidget(self.pydmlabel_MeasMode)

        l_currthold = QLabel('Current Threshold [mA]: ', self)
        self.pydmspinbox_CurrThold = PyDMSpinbox(
            parent=self, init_channel=self.dcct_prefix+'CurrThold-SP')
        self.pydmspinbox_CurrThold.setFixedSize(220, 40)
        self.pydmspinbox_CurrThold.setAlignment(Qt.AlignCenter)
        self.pydmspinbox_CurrThold.showStepExponent = False
        self.pydmlabel_CurrThold = PyDMLabel(
            parent=self, init_channel=self.dcct_prefix+'CurrThold-RB')
        hlay_currthold = QHBoxLayout()
        hlay_currthold.addWidget(self.pydmspinbox_CurrThold)
        hlay_currthold.addWidget(self.pydmlabel_CurrThold)

        l_hfreject = QLabel('High Frequency Rejection: ', self)
        self.pydmstatebutton_HFReject = PyDMStateButton(
            parent=self, init_channel=self.dcct_prefix+'HFReject-Sel')
        self.pydmstatebutton_HFReject.shape = 1
        self.pydmstatebutton_HFReject.setFixedSize(220, 40)
        self.pydmlabel_HFReject = PyDMLabel(
            parent=self, init_channel=self.dcct_prefix+'HFReject-Sts')
        hlay_hfreject = QHBoxLayout()
        hlay_hfreject.addWidget(self.pydmstatebutton_HFReject)
        hlay_hfreject.addWidget(self.pydmlabel_HFReject)

        l_meastrig = QLabel('Measurement Trigger Source: ', self)
        self.pydmenumcombobox_MeasTrg = PyDMEnumComboBox(
            parent=self, init_channel=self.dcct_prefix+'MeasTrg-Sel')
        self.pydmenumcombobox_MeasTrg.setFixedSize(220, 40)
        self.pydmlabel_MeasTrg = PyDMLabel(
            parent=self, init_channel=self.dcct_prefix+'MeasTrg-Sts')
        hlay_meastrig = QHBoxLayout()
        hlay_meastrig.addWidget(self.pydmenumcombobox_MeasTrg)
        hlay_meastrig.addWidget(self.pydmlabel_MeasTrg)

        l_TIstatus = QLabel('Timing Trigger Status: ', self)
        self.ledmulti_TIStatus = PyDMLedMultiChannel(
            parent=self,
            channels2values={
                'ca://'+self.prefix+'BO-35D:TI-DCCT:State-Sts': 1,
                'ca://'+self.prefix+'BO-35D:TI-DCCT:Status-Mon': 0})
        self.ledmulti_TIStatus.setFixedSize(220, 40)
        self.pb_trgdetails = QPushButton('Open details', self)
        _hlautil.connect_window(
            self.pb_trgdetails, HLTriggerDetailed, parent=self,
            prefix=self.prefix+'BO-35D:TI-DCCT:')
        hlay_TIstatus = QHBoxLayout()
        hlay_TIstatus.addWidget(self.ledmulti_TIStatus)
        hlay_TIstatus.addWidget(self.pb_trgdetails)

        l_TIdelay = QLabel('Timing Trigger Delay: ', self)
        self.pydmspinbox_TIDelay = PyDMSpinbox(
            parent=self,
            init_channel='ca://'+self.prefix+'BO-35D:TI-DCCT:Delay-SP')
        self.pydmspinbox_TIDelay.setFixedSize(220, 40)
        self.pydmspinbox_TIDelay.setAlignment(Qt.AlignCenter)
        self.pydmspinbox_TIDelay.showStepExponent = False
        self.pydmlabel_TIDelay = PyDMLabel(
            parent=self,
            init_channel='ca://'+self.prefix+'BO-35D:TI-DCCT:Delay-RB')
        hlay_TIdelay = QHBoxLayout()
        hlay_TIdelay.addWidget(self.pydmspinbox_TIDelay)
        hlay_TIdelay.addWidget(self.pydmlabel_TIDelay)

        l_trgdelay = QLabel('Measurement Delay After Trigger [s]: ', self)
        self.pydmspinbox_TrgDelay = PyDMSpinbox(
            parent=self, init_channel=self.dcct_prefix+'TrgDelay-SP')
        self.pydmspinbox_TrgDelay.setFixedSize(220, 40)
        self.pydmspinbox_TrgDelay.setAlignment(Qt.AlignCenter)
        self.pydmspinbox_TrgDelay.showStepExponent = False
        self.pydmlabel_TrgDelay = PyDMLabel(
            parent=self, init_channel=self.dcct_prefix+'TrgDelay-RB')
        hlay_trgdelay = QHBoxLayout()
        hlay_trgdelay.addWidget(self.pydmspinbox_TrgDelay)
        hlay_trgdelay.addWidget(self.pydmlabel_TrgDelay)

        flay_generalsettings = QFormLayout()
        flay_generalsettings.setFormAlignment(Qt.AlignCenter)
        flay_generalsettings.addRow(l_measmode, hlay_measmode)
        flay_generalsettings.addRow(l_currthold, hlay_currthold)
        flay_generalsettings.addRow(l_hfreject, hlay_hfreject)
        flay_generalsettings.addRow(l_meastrig, hlay_meastrig)
        flay_generalsettings.addRow(l_TIstatus, hlay_TIstatus)
        flay_generalsettings.addRow(l_TIdelay, hlay_TIdelay)
        flay_generalsettings.addRow(l_trgdelay, hlay_trgdelay)
        gbox_generalsettings.setLayout(flay_generalsettings)
        return gbox_generalsettings

    def _setupDCCTNormalMeasSettingsWidget(self):
        gbox_normalmode = _GroupBoxWithChannel(
            'DCCT Normal Measurement Mode Settings', self, [self.mode_channel])

        l_smpcnt = QLabel('Sample Count: ', self)
        self.pydmspinbox_SampleCnt = PyDMSpinbox(
            parent=self, init_channel=self.dcct_prefix+'SampleCnt-SP')
        self.pydmspinbox_SampleCnt.setFixedSize(220, 40)
        self.pydmspinbox_SampleCnt.setAlignment(Qt.AlignCenter)
        self.pydmspinbox_SampleCnt.showStepExponent = False
        self.pydmlabel_SampleCnt = PyDMLabel(
            parent=self, init_channel=self.dcct_prefix+'SampleCnt-RB')
        hlay_smpcnt = QHBoxLayout()
        hlay_smpcnt.addWidget(self.pydmspinbox_SampleCnt)
        hlay_smpcnt.addWidget(self.pydmlabel_SampleCnt)

        l_measperiod = QLabel('Measurement Period [s]: ', self)
        self.pydmspinbox_MeasPeriod = PyDMSpinbox(
            parent=self, init_channel=self.dcct_prefix+'MeasPeriod-SP')
        self.pydmspinbox_MeasPeriod.setFixedSize(220, 40)
        self.pydmspinbox_MeasPeriod.setAlignment(Qt.AlignCenter)
        self.pydmspinbox_MeasPeriod.showStepExponent = False
        self.pydmlabel_MeasPeriod = PyDMLabel(
            parent=self, init_channel=self.dcct_prefix+'MeasPeriod-RB')
        hlay_measperiod = QHBoxLayout()
        hlay_measperiod.addWidget(self.pydmspinbox_MeasPeriod)
        hlay_measperiod.addWidget(self.pydmlabel_MeasPeriod)

        l_offset = QLabel('Relative Offset Enable: ', self)
        self.pydmstatebutton_RelEnbl = PyDMStateButton(
            parent=self, init_channel=self.dcct_prefix+'RelEnbl-Sel')
        self.pydmstatebutton_RelEnbl.shape = 1
        self.pydmstatebutton_RelEnbl.setFixedSize(220, 40)
        self.pydmlabel_RelEnbl = PyDMLabel(
            parent=self, init_channel=self.dcct_prefix+'RelEnbl-Sts')
        self.pydmpushbutton_RelEnbl = PyDMPushButton(
            parent=self, label='Acquire Offset', pressValue=1,
            init_channel=self.dcct_prefix+'RelAcq-Cmd')
        self.pydmpushbutton_RelEnbl.setFixedSize(220, 40)
        hlay_offset = QHBoxLayout()
        hlay_offset.addWidget(self.pydmstatebutton_RelEnbl)
        hlay_offset.addWidget(self.pydmlabel_RelEnbl)
        hlay_offset.addWidget(self.pydmpushbutton_RelEnbl)

        l_rellvl = QLabel('Relative Offset Level [V]: ', self)
        self.pydmspinbox_RelLvl = PyDMSpinbox(
            parent=self, init_channel=self.dcct_prefix+'RelLvl-SP')
        self.pydmspinbox_RelLvl.setFixedSize(220, 40)
        self.pydmspinbox_RelLvl.setAlignment(Qt.AlignCenter)
        self.pydmspinbox_RelLvl.showStepExponent = False
        self.pydmlabel_RelLvl = PyDMLabel(
            parent=self, init_channel=self.dcct_prefix+'RelLvl-RB')
        hlay_rellvl = QHBoxLayout()
        hlay_rellvl.addWidget(self.pydmspinbox_RelLvl)
        hlay_rellvl.addWidget(self.pydmlabel_RelLvl)

        flay_normalmode = QFormLayout()
        flay_normalmode.setFormAlignment(Qt.AlignCenter)
        flay_normalmode.addRow(l_smpcnt, hlay_smpcnt)
        flay_normalmode.addRow(l_measperiod, hlay_measperiod)
        flay_normalmode.addRow(l_offset, hlay_offset)
        flay_normalmode.addRow(l_rellvl, hlay_rellvl)
        gbox_normalmode.setLayout(flay_normalmode)
        gbox_normalmode.setVisible(True)
        return gbox_normalmode

    def _setupDCCTFastMeasSettingsWidget(self):
        gbox_fastmode = _GroupBoxWithChannel(
            'DCCT Fast Measurement Mode Settings', self, [self.mode_channel])

        l_fastsmpcnt = QLabel('Sample Count: ', self)
        self.pydmspinbox_FastSampleCnt = PyDMSpinbox(
            parent=self, init_channel=self.dcct_prefix+'FastSampleCnt-SP')
        self.pydmspinbox_FastSampleCnt.setFixedSize(220, 40)
        self.pydmspinbox_FastSampleCnt.setAlignment(Qt.AlignCenter)
        self.pydmspinbox_FastSampleCnt.showStepExponent = False
        self.pydmlabel_FastSampleCnt = PyDMLabel(
            parent=self, init_channel=self.dcct_prefix+'FastSampleCnt-RB')
        hlay_fastsmpcnt = QHBoxLayout()
        hlay_fastsmpcnt.addWidget(self.pydmspinbox_FastSampleCnt)
        hlay_fastsmpcnt.addWidget(self.pydmlabel_FastSampleCnt)

        l_fastmeasperiod = QLabel('Measurement Period [s]: ', self)
        self.pydmspinbox_FastMeasPeriod = PyDMSpinbox(
            parent=self, init_channel=self.dcct_prefix+'FastMeasPeriod-SP')
        self.pydmspinbox_FastMeasPeriod.setFixedSize(220, 40)
        self.pydmspinbox_FastMeasPeriod.setAlignment(Qt.AlignCenter)
        self.pydmspinbox_FastMeasPeriod.showStepExponent = False
        self.pydmlabel_FastMeasPeriod = PyDMLabel(
            parent=self, init_channel=self.dcct_prefix+'FastMeasPeriod-RB')
        hlay_fastmeasperiod = QHBoxLayout()
        hlay_fastmeasperiod.addWidget(self.pydmspinbox_FastMeasPeriod)
        hlay_fastmeasperiod.addWidget(self.pydmlabel_FastMeasPeriod)

        l_fastoffset = QLabel('Relative Offset Enable: ', self)
        self.pydmstatebutton_FastRelEnbl = PyDMStateButton(
            parent=self, init_channel=self.dcct_prefix+'FastRelEnbl-Sel')
        self.pydmstatebutton_FastRelEnbl.shape = 1
        self.pydmstatebutton_FastRelEnbl.setFixedSize(220, 40)
        self.pydmlabel_FastRelEnbl = PyDMLabel(
            parent=self, init_channel=self.dcct_prefix+'FastRelEnbl-Sts')
        self.pydmpushbutton_FastRelEnbl = PyDMPushButton(
            parent=self, label='Acquire Offset', pressValue=1,
            init_channel=self.dcct_prefix+'FastRelAcq-Cmd')
        self.pydmpushbutton_FastRelEnbl.setFixedSize(220, 40)
        hlay_fastoffset = QHBoxLayout()
        hlay_fastoffset.addWidget(self.pydmstatebutton_FastRelEnbl)
        hlay_fastoffset.addWidget(self.pydmlabel_FastRelEnbl)
        hlay_fastoffset.addWidget(self.pydmpushbutton_FastRelEnbl)

        l_fastrellvl = QLabel('Relative Offset Level [V]: ', self)
        self.pydmspinbox_FastRelLvl = PyDMSpinbox(
            parent=self, init_channel=self.dcct_prefix+'FastRelLvl-SP')
        self.pydmspinbox_FastRelLvl.setFixedSize(220, 40)
        self.pydmspinbox_FastRelLvl.setAlignment(Qt.AlignCenter)
        self.pydmspinbox_FastRelLvl.showStepExponent = False
        self.pydmlabel_FastRelLvl = PyDMLabel(
            parent=self, init_channel=self.dcct_prefix+'FastRelLvl-RB')
        hlay_fastrellvl = QHBoxLayout()
        hlay_fastrellvl.addWidget(self.pydmspinbox_FastRelLvl)
        hlay_fastrellvl.addWidget(self.pydmlabel_FastRelLvl)

        flay_fastmode = QFormLayout()
        flay_fastmode.setFormAlignment(Qt.AlignCenter)
        flay_fastmode.addRow(l_fastsmpcnt, hlay_fastsmpcnt)
        flay_fastmode.addRow(l_fastmeasperiod, hlay_fastmeasperiod)
        flay_fastmode.addRow(l_fastoffset, hlay_fastoffset)
        flay_fastmode.addRow(l_fastrellvl, hlay_fastrellvl)
        gbox_fastmode.setLayout(flay_fastmode)
        gbox_fastmode.setVisible(False)
        return gbox_fastmode

    def _setupRampEffIndicesWidget(self):
        gbox_effparams = QGroupBox(
            'Ramp Efficiency Calculation Indices', self)

        l_injcurr = QLabel('Injected Current: ', self)
        self.sb_injcurr = QSpinBox(self)
        self.sb_injcurr.setValue(self.injcurr_idx)
        self.sb_injcurr.setMinimum(0)
        self.sb_injcurr.setFixedSize(220, 40)
        if self.pydmlabel_SampleCnt._connected:
            self.sb_injcurr.setMaximum(int(self.pydmlabel_SampleCnt.text())-1)
        else:
            self.sb_injcurr.setMaximum(1)

        l_ejecurr = QLabel('Ejected Current: ', self)
        self.sb_ejecurr = QSpinBox(self)
        self.sb_ejecurr.setValue(self.ejecurr_idx)
        self.sb_ejecurr.setMinimum(0)
        self.sb_ejecurr.setFixedSize(220, 40)
        if self.pydmlabel_SampleCnt._connected:
            self.sb_ejecurr.setMaximum(int(self.pydmlabel_SampleCnt.text())-1)
        else:
            self.sb_ejecurr.setMaximum(1)

        flay_effparams = QFormLayout()
        flay_effparams.setFormAlignment(Qt.AlignCenter)
        flay_effparams.addRow(l_injcurr, self.sb_injcurr)
        flay_effparams.addRow(l_ejecurr, self.sb_ejecurr)
        gbox_effparams.setLayout(flay_effparams)
        return gbox_effparams

    def _updateReliableMeasLabels(self, labels):
        if labels:
            self.label_reliablemeas0.setText(labels[0])
            self.label_reliablemeas1.setText(labels[1])
            self.label_reliablemeas2.setText(labels[2])

    def _showMeasModeSettings(self, value):
        if value == DCCT_MEASMODE_NORMAL:
            self.gbox_normalmode.setVisible(True)
            self.gbox_fastmode.setVisible(False)
        if value == DCCT_MEASMODE_FAST:
            self.gbox_normalmode.setVisible(False)
            self.gbox_fastmode.setVisible(True)

    def _emitSettings(self):
        self.updateSettings.emit([self.sb_injcurr.value(),
                                  self.sb_ejecurr.value()])
        self.close()


class _GroupBoxWithChannel(QGroupBox):

    def __init__(self, title='', parent=None, channels=None):
        self._channels = channels
        super().__init__(title, parent)

    def channels(self):
        """Return channels."""
        return self._channels


class ChooseMagnetsToPlot(SiriusDialog):
    """Auxiliar window to select which magnets will to be shown in plot."""

    choosePlotSignal = Signal(list)

    def __init__(self, parent, manames, current_plots):
        """Initialize object."""
        super().__init__(parent)
        self.setWindowTitle('Choose Magnets To Plot')
        self.manames = manames
        self.current_plots = current_plots
        self._setupUi()

    def _setupUi(self):
        self.quads = QWidget(self)
        vlay_quad = QVBoxLayout()
        vlay_quad.setAlignment(Qt.AlignTop)
        self.quads.setLayout(vlay_quad)

        self.sexts = QWidget(self)
        vlay_sext = QVBoxLayout()
        vlay_sext.setAlignment(Qt.AlignTop)
        self.sexts.setLayout(vlay_sext)

        self.chs = QWidget(self)
        vlay_ch = QVBoxLayout()
        vlay_ch.setAlignment(Qt.AlignTop)
        self.chs.setLayout(vlay_ch)

        self.cvs = QWidget(self)
        vlay_cv = QVBoxLayout()
        vlay_cv.setAlignment(Qt.AlignTop)
        self.cvs.setLayout(vlay_cv)

        self.all_quad_sel = QCheckBox('All quadrupoles', self.quads)
        self.all_quad_sel.clicked.connect(self._handleSelectGroups)
        vlay_quad.addWidget(self.all_quad_sel)
        self.all_sext_sel = QCheckBox('All sextupoles', self.sexts)
        self.all_sext_sel.clicked.connect(self._handleSelectGroups)
        vlay_sext.addWidget(self.all_sext_sel)
        self.all_ch_sel = QCheckBox('All CHs', self.chs)
        self.all_ch_sel.clicked.connect(self._handleSelectGroups)
        vlay_ch.addWidget(self.all_ch_sel)
        self.all_cv_sel = QCheckBox('All CVs', self.cvs)
        self.all_cv_sel.clicked.connect(self._handleSelectGroups)
        vlay_cv.addWidget(self.all_cv_sel)

        for maname in self.manames:
            if 'Q' in maname:
                cb_maname = QCheckBox(maname, self.quads)
                vlay_quad.addWidget(cb_maname)
            elif 'S' in maname:
                cb_maname = QCheckBox(maname, self.sexts)
                vlay_sext.addWidget(cb_maname)
            elif 'CH' in maname:
                cb_maname = QCheckBox(maname, self.chs)
                vlay_ch.addWidget(cb_maname)
            elif 'CV' in maname:
                cb_maname = QCheckBox(maname, self.cvs)
                vlay_cv.addWidget(cb_maname)
            if maname in self.current_plots:
                cb_maname.setChecked(True)
            cb_maname.setObjectName(maname)

        self.pb_choose = QPushButton('Choose', self)
        self.pb_choose.clicked.connect(self._emitChoosePlot)

        glay = QGridLayout()
        glay.addWidget(self.quads, 0, 0)
        glay.addWidget(self.sexts, 1, 0)
        glay.addWidget(self.chs, 0, 1, 2, 1)
        glay.addWidget(self.cvs, 0, 2, 2, 1)
        glay.addWidget(self.pb_choose, 2, 1)
        self.setLayout(glay)

    def _handleSelectGroups(self):
        sender = self.sender()
        sender_parent = sender.parent()
        for child in sender_parent.children():
            if isinstance(child, QCheckBox):
                child.setChecked(sender.isChecked())

    def _emitChoosePlot(self):
        maname_list = list()
        children = list()
        for w in [self.quads, self.sexts, self.chs, self.cvs]:
            for child in w.children():
                children.append(child)
        for child in children:
            if (isinstance(child, QCheckBox) and child.isChecked() and
                    'BO' in child.objectName()):
                maname_list.append(child.objectName())

        self.choosePlotSignal.emit(maname_list)
        self.close()


class SpinBoxDelegate(QStyledItemDelegate):
    """Auxiliar class to draw a SpinBox in table items on editing."""

    def createEditor(self, parent, option, index):
        """Create editor."""
        editor = QDoubleSpinBox(parent)
        editor.setMinimum(0)
        editor.setMaximum(500)
        editor.setDecimals(4)
        locale = QLocale(QLocale.English, country=QLocale.UnitedStates)
        locale.setNumberOptions(locale.RejectGroupSeparator)
        editor.setLocale(locale)
        return editor

    def setEditorData(self, spinBox, index):
        """Set editor data."""
        value = index.model().data(index, Qt.EditRole)
        spinBox.setValue(float(value))

    def setModelData(self, spinBox, model, index):
        """Set model data."""
        spinBox.interpretText()
        value = spinBox.value()
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, spinBox, option, index):
        """Update editor geometry."""
        spinBox.setGeometry(option.rect)


class MessageBox(SiriusDialog):
    """Auxiliar dialog to inform user about errors and pendencies."""

    acceptedSignal = Signal()
    rejectedSignal = Signal()

    def __init__(self, parent=None, title='', message='',
                 accept_button_text='', regect_button_text=''):
        """Initialize object."""
        super().__init__(parent)
        self.setWindowTitle(title)
        self.message = message
        self.accept_button_text = accept_button_text
        self.regect_button_text = regect_button_text
        self._setupUi()

    def _setupUi(self):
        glay = QGridLayout()

        self.label = QLabel(self.message, self)
        glay.addWidget(self.label, 0, 0, 1, 3)

        self.accept_button = QPushButton(self.accept_button_text, self)
        self.accept_button.clicked.connect(self._emitAccepted)
        glay.addWidget(self.accept_button, 1, 1)

        if self.regect_button_text != '':
            self.regect_button = QPushButton(self.regect_button_text, self)
            self.regect_button.clicked.connect(self._emitRegected)
            glay.addWidget(self.regect_button, 1, 2)

        self.setLayout(glay)

    def _emitAccepted(self):
        self.acceptedSignal.emit()
        self.close()

    def _emitRegected(self):
        self.rejectedSignal.emit()
        self.close()


class CustomTableWidgetItem(QTableWidgetItem):
    """Auxiliar class to make a table column sortable by numeric data."""

    def __init__(self, value):
        """Initialize object."""
        super().__init__('{}'.format(value))

    def __lt__(self, other):
        """Change default sort method to sort by numeric data."""
        if isinstance(other, CustomTableWidgetItem):
            selfDataValue = float(self.data(Qt.EditRole))
            otherDataValue = float(other.data(Qt.EditRole))
            return selfDataValue < otherDataValue
        else:
            return QTableWidgetItem.__lt__(self, other)


class MyDoubleSpinBox(QDoubleSpinBox):
    """Subclass QDoubleSpinBox to reimplement whellEvent."""

    def __init__(self, parent):
        """Initialize object."""
        super().__init__(parent)
        locale = QLocale(QLocale.English, country=QLocale.UnitedStates)
        locale.setNumberOptions(locale.RejectGroupSeparator)
        self.setLocale(locale)
        self.setFocusPolicy(Qt.StrongFocus)

    def wheelEvent(self, event):
        """Reimplement wheel event to ignore event when out of focus."""
        if not self.hasFocus():
            event.ignore()
        else:
            super().wheelEvent(event)


class _ConfigLineEdit(QLineEdit):

    def mouseReleaseEvent(self, ev):
        popup = _LoadConfiguration('bo_normalized')
        popup.configname.connect(self.setText)
        popup.exec_()
