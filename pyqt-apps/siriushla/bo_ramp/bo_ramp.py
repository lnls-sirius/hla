"""Booster Ramp Control HLA."""

import sys
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QGroupBox, QLabel, QWidget, QScrollArea, \
                            QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit, \
                            QPushButton, QTableWidget, QTableWidgetItem, \
                            QRadioButton, QFormLayout, QDoubleSpinBox, \
                            QComboBox, QSpinBox, QStyledItemDelegate, \
                            QSpacerItem, QSizePolicy as QSzPlcy
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas)
from matplotlib.figure import Figure
import numpy as np
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets.windows import SiriusMainWindow, SiriusDialog
from siriuspy.namesys import SiriusPVName as _PVName
from siriushla import util as _util
from siriuspy.ramp import ramp, exceptions
from siriuspy.csdevice.pwrsupply import MIN_WFMSIZE, MAX_WFMSIZE


class RampMain(SiriusMainWindow):
    """Main window of Booster Ramp Control HLA."""

    def __init__(self, parent=None, prefix=''):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self.ramp_config = None
        self._setupUi()
        self._connSignals()

    def _setupUi(self):
        # self.resize(2000, 2000)
        cw = QWidget(self)
        self.setCentralWidget(cw)
        self.my_layout = QGridLayout(cw)
        self.my_layout.setHorizontalSpacing(20)
        self.my_layout.setVerticalSpacing(20)
        lab = QLabel('<h1>Booster Energy Ramping</h1>', cw)
        self.my_layout.addWidget(lab, 0, 0, 1, 3)
        self.my_layout.setAlignment(lab, Qt.AlignCenter)

        self.ramp_settings = RampSettings(self, self.prefix, self.ramp_config)
        self.my_layout.addWidget(self.ramp_settings, 1, 0)

        self.commands = RampCommands(self, self.prefix, self.ramp_config)
        self.my_layout.addWidget(self.commands, 2, 0, 2, 1)

        self.ramp_parameters = RampParameters(self, self.prefix,
                                              self.ramp_config)
        self.my_layout.addWidget(self.ramp_parameters, 1, 1, 2, 1)

        self.optics_adjust = OpticsAdjust(self, self.prefix, self.ramp_config)
        self.my_layout.addWidget(self.optics_adjust, 3, 1)

        self.statistics = RampStatistics(self, self.prefix, self.ramp_config)
        self.my_layout.addWidget(self.statistics, 1, 2, 3, 1)

    def _connSignals(self):
        self.ramp_settings.configSignal.connect(self._receiveNewConfigName)

        self.ramp_settings.loadSignal.connect(
            self.ramp_parameters.dip_ramp.handleLoadRampConfig)
        self.ramp_settings.loadSignal.connect(
            self.ramp_parameters.mult_ramp.handleLoadRampConfig)

        self.ramp_parameters.dip_ramp.updateDipoleRampSignal.connect(
            self.ramp_settings.verifySync)
        self.ramp_parameters.dip_ramp.updateDipoleRampSignal.connect(
            self.ramp_parameters.mult_ramp.updateTable)
        self.ramp_parameters.dip_ramp.updateDipoleRampSignal.connect(
            self.ramp_parameters.mult_ramp.updateGraph)
        self.ramp_parameters.mult_ramp.updateMultipoleRampSignal.connect(
            self.ramp_settings.verifySync)

    @pyqtSlot(str)
    def _receiveNewConfigName(self, new_config_name):
        self.ramp_config = ramp.BoosterRamp(new_config_name)
        if self.ramp_config.configsrv_check():
            self.ramp_config.configsrv_load()
            self.ramp_config.configsrv_load_normalized_configs()
        self._setupUi()
        self._connSignals()
        self.ramp_settings.loadSignal.emit()
        self.ramp_settings.verifySync()


class RampSettings(QGroupBox):

    configSignal = pyqtSignal(str)
    loadSignal = pyqtSignal()

    def __init__(self, parent=None, prefix='', ramp_config=None):
        super().__init__('Ramp Settings', parent)
        self.prefix = _PVName(prefix)
        self.ramp_config = ramp_config
        self._setupUi()

    def _setupUi(self):
        if self.ramp_config is not None:
            le_text = self.ramp_config.name
        else:
            le_text = ''
        self.le_config = QLineEdit(le_text, self)
        self.bt_load = QPushButton('Load', self)
        self.bt_save = QPushButton('Save', self)
        self.le_config.editingFinished.connect(self._le_config_textChanged)
        self.bt_load.clicked.connect(self._load)
        self.bt_save.clicked.connect(self._save)
        lay = QVBoxLayout(self)
        lay.addWidget(self.le_config)
        lay.addWidget(self.bt_load)
        lay.addWidget(self.bt_save)

    def _le_config_textChanged(self):
        name = self.le_config.text()
        if ramp.BoosterRamp(name).configsrv_check():
            if ((self.ramp_config is None) or
                    (self.ramp_config is not None and
                     name != self.ramp_config.name)):
                self.bt_load.setStyleSheet("""background-color:#1F64FF;""")
        elif name != '':
            create_config = _MessageBox(
                self, 'Create a new configuration?',
                'There is no configuration with name \"{}\". \n'
                'Create a new one?'.format(name), 'Yes', 'Cancel')
            create_config.acceptedSignal.connect(self._emitConfigSignal)
            create_config.show()

    def _emitConfigSignal(self):
        self.configSignal.emit(self.le_config.text())

    def _load(self):
        name = self.le_config.text()
        if ramp.BoosterRamp(name).configsrv_check():
            if self.ramp_config is not None:
                if not self.ramp_config.configsrv_synchronized:
                    save_changes = _MessageBox(
                        self, 'Save changes?',
                        'There are unsaved changes. \n'
                        'Do you want to save?'.format(name),
                        'Yes', 'Cancel')
                    save_changes.acceptedSignal.connect(self._save)
                    save_changes.exec_()

                if name != self.ramp_config.name:
                    self.configSignal.emit(name)
                else:
                    self.ramp_config.configsrv_load()
                    self.ramp_config.configsrv_load_normalized_configs()
                    self.loadSignal.emit()
            else:
                self.configSignal.emit(name)
            self.verifySync()

    def _save(self):
        config_exists = self.ramp_config.configsrv_check()
        if config_exists:
            self.ramp_config.configsrv_update()
        else:
            self.ramp_config.configsrv_save()
        self.verifySync()

    def verifySync(self):
        if self.ramp_config is not None:
            if not self.ramp_config.configsrv_synchronized:
                self.bt_save.setStyleSheet("""background-color: #1F64FF;""")
            else:
                self.bt_save.setStyleSheet("")


class RampCommands(QGroupBox):

    def __init__(self, parent=None, prefix='', ramp_config=None):
        super().__init__('Commands', parent)
        self.prefix = _PVName(prefix)
        self.ramp_config = ramp_config
        self._setupUi()

    def _setupUi(self):
        self.bt_upload = QPushButton('Upload to PS', self)
        self.bt_cycle = QPushButton('Cycle', self)
        self.bt_start = QPushButton('Start', self)
        self.bt_stop = QPushButton('Stop', self)
        self.bt_abort = QPushButton('Abort', self)
        self.bt_abort.setStyleSheet('background-color: red;')

        self.bt_upload.clicked.connect(self._upload)
        self.bt_cycle.clicked.connect(self._cycle)
        self.bt_start.clicked.connect(self._start)
        self.bt_stop.clicked.connect(self._stop)
        self.bt_abort.clicked.connect(self._abort)

        lay = QVBoxLayout(self)
        lay.addWidget(self.bt_upload)
        lay.addWidget(self.bt_cycle)
        lay.addWidget(self.bt_start)
        lay.addWidget(self.bt_stop)
        lay.addWidget(self.bt_abort)

    def _calculate(self):
        print('Do stuff')

    def _upload(self):
        print('Do stuff')

    def _cycle(self):
        print('Do stuff')

    def _start(self):
        print('Do stuff')

    def _stop(self):
        print('Do stuff')

    def _abort(self):
        print('Do stuff')


class RampParameters(QGroupBox):

    def __init__(self, parent=None, prefix='', ramp_config=None):
        super().__init__('Ramping Parameters', parent)
        self.prefix = _PVName(prefix)
        self.ramp_config = ramp_config
        self._setupUi()

    def _setupUi(self):
        my_lay = QHBoxLayout(self)
        self.dip_ramp = DipoleRamp(self, self.prefix, self.ramp_config)
        self.mult_ramp = MultipolesRamp(self, self.prefix, self.ramp_config)
        self.rf_ramp = RFRamp(self, self.prefix, self.ramp_config)
        my_lay.addWidget(self.dip_ramp)
        my_lay.addWidget(self.mult_ramp)
        my_lay.addWidget(self.rf_ramp)


class DipoleRamp(QWidget):

    updateDipoleRampSignal = pyqtSignal()

    def __init__(self, parent=None, prefix='', ramp_config=None):
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self.ramp_config = ramp_config
        self._setupUi()
        self._loadedFlag = False

    def _setupUi(self):
        vlay = QVBoxLayout(self)
        self.graph = FigureCanvas(Figure())
        self.set_nrpoints = QHBoxLayout()
        self.table = QTableWidget(self)

        self._setupGraph()
        label_nrpoints = QLabel('# of points', self)
        label_nrpoints.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.sb_nrpoints = QSpinBox(self)
        self.set_nrpoints.addSpacerItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        self.set_nrpoints.addWidget(label_nrpoints)
        self.set_nrpoints.addWidget(self.sb_nrpoints)
        self.set_nrpoints.addSpacerItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        self._setupWfmNrPoints()
        self._setupTable()

        label = QLabel('<h4>Dipole Ramp</h4>', self)
        label.setAlignment(Qt.AlignCenter)
        label.setFixedHeight(48)
        vlay.addWidget(label)
        vlay.addWidget(self.graph)
        vlay.addLayout(self.set_nrpoints)
        vlay.addWidget(self.table)

    def _setupGraph(self):
        self.ax = self.graph.figure.subplots()
        self.ax.grid()
        self.ax.set_xlabel('t [ms]')
        self.ax.set_ylabel('E [GeV]')
        self.line, = self.ax.plot([0], [0], '-b')
        self.markers, = self.ax.plot([0], [0], '+r')
        self.m_inj, = self.ax.plot([0], [0], 'or')
        self.m_ej, = self.ax.plot([0], [0], 'or')

    def _setupWfmNrPoints(self):
        self.sb_nrpoints.setMinimum(MIN_WFMSIZE)
        self.sb_nrpoints.setMaximum(MAX_WFMSIZE)
        if self.ramp_config is not None:
            self.sb_nrpoints.setValue(
                self.ramp_config.ramp_dipole_wfm_nrpoints)
            self.sb_nrpoints.editingFinished.connect(self.updateWfmNrPoints)

    def _setupTable(self):
        self.table_map = {
            'rows': {'Start': 0,
                     'RampUp-Start': 1,
                     'Injection': 2,
                     'Ejection': 3,
                     'RampUp-Stop': 4,
                     'Plateau-Start': 5,
                     'RampDown-Start': 6,
                     'RampDown-Stop': 7,
                     'Stop': 8},
            'columns': {'': 0,
                        'T [ms]': 1,
                        'Index': 2,
                        'E [GeV]': 3,
                        'v [MeV/pt]': 4}}
        self.table.setStyleSheet(
            """
            QHeaderView::section {
                background-color: #1F64FF;
                }
            QTableWidget {
                background-color: #D3E1FF;
                gridline-color: #003065;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #1F64FF;
            }
            """)
        self.table.setFixedSize(852, self.table_map['rows']['Stop']*48+85)
        self.table.setRowCount(9)
        self.table.setColumnCount(5)
        self.table.setColumnWidth(0, 250)
        for i in range(1, len(self.table_map['columns'].keys())):
            self.table.setColumnWidth(i, 150)
        self.table.verticalHeader().hide()
        self.table.setHorizontalHeaderLabels(self.table_map['columns'].keys())

        for vlabel, row in self.table_map['rows'].items():
            label_item = QTableWidgetItem(vlabel)
            t_item = QTableWidgetItem('0')
            np_item = QTableWidgetItem('0')
            e_item = QTableWidgetItem('0')
            v_item = QTableWidgetItem('0')

            label_item.setFlags(Qt.ItemIsEnabled)
            np_item.setFlags(Qt.ItemIsEnabled)
            v_item.setFlags(Qt.ItemIsEnabled)
            if vlabel == 'Start':
                t_item.setFlags(Qt.ItemIsEnabled)
                e_item.setBackground(QBrush(QColor("white")))
            elif vlabel in ['Plateau-Start', 'Stop']:
                t_item.setFlags(Qt.ItemIsEnabled)
                e_item.setFlags(Qt.ItemIsEnabled)
            elif vlabel in ['Injection', 'Ejection']:
                t_item.setBackground(QBrush(QColor("white")))
                e_item.setFlags(Qt.ItemIsEnabled)
            else:
                t_item.setBackground(QBrush(QColor("white")))
                e_item.setBackground(QBrush(QColor("white")))

            self.table.setItem(row, 0, label_item)
            self.table.setItem(row, 1, t_item)
            self.table.setItem(row, 2, np_item)
            self.table.setItem(row, 3, e_item)
            self.table.setItem(row, 4, v_item)

            self.table.setRowHeight(row, 48)

        self.table.setItemDelegate(_SpinBoxDelegate())
        self.table.cellChanged.connect(self._handleCellChanged)

    @pyqtSlot(int, int)
    def _handleCellChanged(self, row, column):
        try:
            if row == self.table_map['rows']['Start']:
                energy = float(self.table.item(
                    row, self.table_map['columns']['E [GeV]']).data(
                        Qt.DisplayRole))
                self.ramp_config.ramp_start_value = energy

            elif row == self.table_map['rows']['RampUp-Start']:
                if column == self.table_map['columns']['T [ms]']:
                    time = float(self.table.item(row, column).data(
                        Qt.DisplayRole))
                    self.ramp_config.rampup_start_time = time
                elif column == self.table_map['columns']['E [GeV]']:
                    energy = float(self.table.item(row, column).data(
                        Qt.DisplayRole))
                    self.ramp_config.rampup_start_value = energy

            elif row == self.table_map['rows']['Injection']:
                if column == self.table_map['columns']['T [ms]']:
                    time = float(self.table.item(row, column).data(
                        Qt.DisplayRole))
                    self.ramp_config.injection_time = time
                # elif column == self.table_map['columns']['E [GeV]']:
                #     energy = float(self.table.item(row, column).data(
                #         Qt.DisplayRole))

            elif row == self.table_map['rows']['Ejection']:
                if column == self.table_map['columns']['T [ms]']:
                    time = float(self.table.item(row, column).data(
                        Qt.DisplayRole))
                    self.ramp_config.ejection_time = time
                # elif column == self.table_map['columns']['E [GeV]']:
                #     energy = float(self.table.item(row, column).data(
                #         Qt.DisplayRole))

            elif row == self.table_map['rows']['RampUp-Stop']:
                if column == self.table_map['columns']['T [ms]']:
                    time = float(self.table.item(row, column).data(
                        Qt.DisplayRole))
                    self.ramp_config.rampup_stop_time = time
                elif column == self.table_map['columns']['E [GeV]']:
                    energy = float(self.table.item(row, column).data(
                        Qt.DisplayRole))
                    self.ramp_config.rampup_stop_value = energy

            elif row == self.table_map['rows']['RampDown-Start']:
                if column == self.table_map['columns']['T [ms]']:
                    time = float(self.table.item(row, column).data(
                        Qt.DisplayRole))
                    self.ramp_config.rampdown_start_time = time
                elif column == self.table_map['columns']['E [GeV]']:
                    energy = float(self.table.item(row, column).data(
                        Qt.DisplayRole))
                    self.ramp_config.rampdown_start_value = energy

            elif row == self.table_map['rows']['RampDown-Stop']:
                if column == self.table_map['columns']['T [ms]']:
                    time = float(self.table.item(row, column).data(
                        Qt.DisplayRole))
                    self.ramp_config.rampdown_stop_time = time
                elif column == self.table_map['columns']['E [GeV]']:
                    energy = float(self.table.item(row, column).data(
                        Qt.DisplayRole))
                    self.ramp_config.rampdown_stop_value = energy
        except exceptions.RampInvalidDipoleWfmParms as e:
            err_msg = _MessageBox(self, 'Error', str(e), 'Ok')
            err_msg.show()
        finally:
            self.updateTable()
            self.updateGraph()
            self.updateDipoleRampSignal.emit()

    def updateGraph(self):
        if self.ramp_config is not None:
            xdata = self.ramp_config.waveform_get_times()
            ydata = self.ramp_config.waveform_get('BO-Fam:MA-B')
            self.line.set_xdata(xdata)
            self.line.set_ydata(ydata)
            self.ax.set_xlim(min(xdata)-0.2, max(xdata)+0.2)
            self.ax.set_ylim(min(ydata)-0.2, max(ydata)+0.2)

            self.markers.set_xdata(self.ramp_config.ramp_dipole_time)
            self.markers.set_ydata(self.ramp_config.ramp_dipole_energy)

            inj_marker_time = self.ramp_config.injection_time
            self.m_inj.set_xdata(inj_marker_time)
            self.m_inj.set_ydata(self.ramp_config.waveform_interp_energy(
                inj_marker_time))

            ej_marker_time = self.ramp_config.ejection_time
            self.m_ej.set_xdata(ej_marker_time)
            self.m_ej.set_ydata(self.ramp_config.waveform_interp_energy(
                ej_marker_time))

            self.graph.figure.canvas.draw()
            self.graph.figure.canvas.flush_events()

    @pyqtSlot()
    def updateWfmNrPoints(self):
        self.ramp_config.ramp_dipole_wfm_nrpoints = self.sb_nrpoints.value()
        self.updateDipoleRampSignal.emit()

    def updateTable(self):
        self.table.cellChanged.disconnect(self._handleCellChanged)
        for label, row in self.table_map['rows'].items():
            t_item = self.table.item(row, 1)
            e_item = self.table.item(row, 3)
            if label == 'Start':
                time = str(self.ramp_config.ramp_dipole_time[0])
                energy = str(self.ramp_config.ramp_start_value)
            elif label == 'RampUp-Start':
                time = str(self.ramp_config.rampup_start_time)
                energy = str(self.ramp_config.rampup_start_value)
            elif label == 'Injection':
                time = self.ramp_config.injection_time
                energy = str(self.ramp_config.waveform_interp_energy(time))
            elif label == 'Ejection':
                time = self.ramp_config.ejection_time
                energy = str(self.ramp_config.waveform_interp_energy(time))
            elif label == 'RampUp-Stop':
                time = str(self.ramp_config.rampup_stop_time)
                energy = str(self.ramp_config.rampup_stop_value)
            elif label == 'Plateau-Start':
                time = str(self.ramp_config.ramp_dipole_time[4])
                energy = str(self.ramp_config.ramp_plateau_value)
            elif label == 'RampDown-Start':
                time = str(self.ramp_config.rampdown_start_time)
                energy = str(self.ramp_config.rampdown_start_value)
            elif label == 'RampDown-Stop':
                time = str(self.ramp_config.rampdown_stop_time)
                energy = str(self.ramp_config.rampdown_stop_value)
            elif label == 'Stop':
                time = str(self.ramp_config.ramp_dipole_time[-1])
                energy = str(self.ramp_config.ramp_dipole_energy[-1])
            t_item.setData(Qt.DisplayRole, str(time))
            e_item.setData(Qt.DisplayRole, str(energy))

        for row in self.table_map['rows'].values():
            for label, column in self.table_map['columns'].items():
                if label == 'Index':
                    D = self.ramp_config.ramp_dipole_duration
                    N = self.ramp_config.ramp_dipole_wfm_nrpoints
                    T = float(self.table.item(
                        row, self.table_map['columns']['T [ms]']).data(
                            Qt.DisplayRole))
                    value = round(T*N/D)
                    item = self.table.item(row, column)
                    item.setData(Qt.DisplayRole, str(value))
                elif label == 'v [MeV/pt]':
                    if row == 0:
                        value = '-'
                    else:
                        T1 = float(self.table.item(
                            row, self.table_map['columns']['T [ms]']).data(
                                Qt.DisplayRole))
                        T2 = float(self.table.item(
                            row-1, self.table_map['columns']['T [ms]']).data(
                                Qt.DisplayRole))
                        dT = T1 - T2
                        E1 = float(self.table.item(
                            row, self.table_map['columns']['E [GeV]']).data(
                                Qt.DisplayRole))
                        E2 = float(self.table.item(
                            row-1, self.table_map['columns']['E [GeV]']).data(
                                Qt.DisplayRole))
                        dE = E1 - E2
                        value = dE*1000/dT
                    item = self.table.item(row, column)
                    item.setData(Qt.DisplayRole, str(value))
        self.table.cellChanged.connect(self._handleCellChanged)

    @pyqtSlot()
    def handleLoadRampConfig(self):
        self.updateTable()
        self.updateWfmNrPoints()
        self.updateGraph()


class MultipolesRamp(QWidget):

    updateMultipoleRampSignal = pyqtSignal()

    def __init__(self, parent=None, prefix='', ramp_config=None):
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self.ramp_config = ramp_config
        self._getNormalizedConfigs()
        self._setupUi()

    def _setupUi(self):
        glay = QGridLayout(self)
        self.graph = FigureCanvas(Figure())
        self.choose_plot = QHBoxLayout()
        self.table = QTableWidget(self)
        self.bt_insert = QPushButton('Insert Normalized Configuration', self)
        self.bt_delete = QPushButton('Delete Normalized Configuration', self)

        self._setupGraph()
        label_maname = QLabel('Plot magnet: ', self)
        label_maname.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.cb_maname = QComboBox(self)
        self.cb_maname.setStyleSheet(
            """
            QComboBox {
                combobox-popup: 0;
            }
            QComboBox QAbstractItemView {
                background-color: lightgray;
            }""")
        self.cb_maname.addItem('Quadrupoles')
        self.cb_maname.addItem('Sextupoles')
        for maname in ramp.BoosterNormalized().get_config_type_template():
            if maname != 'BO-Fam:MA-B':
                self.cb_maname.addItem(maname)
        self.cb_maname.currentTextChanged.connect(self.updateGraph)
        self.cb_maname.setMaximumWidth(250)
        self.choose_plot.addSpacerItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        self.choose_plot.addWidget(label_maname)
        self.choose_plot.addWidget(self.cb_maname)
        self.choose_plot.addSpacerItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        self._setupTable()
        self.bt_insert.clicked.connect(self._showInsertNormConfigPopup)
        self.bt_delete.clicked.connect(self._showDeleteNormConfigPopup)

        label = QLabel('<h4>Multipoles Ramp</h4>', self)
        label.setAlignment(Qt.AlignCenter)
        label.setFixedHeight(48)
        glay.addWidget(label, 0, 0, 1, 2)
        glay.addWidget(self.graph, 1, 0, 1, 2)
        glay.addLayout(self.choose_plot, 2, 0, 1, 2)
        glay.addWidget(self.table, 3, 0, 1, 2)
        glay.addWidget(self.bt_insert, 4, 0)
        glay.addWidget(self.bt_delete, 4, 1)

    def _setupGraph(self):
        self.ax = self.graph.figure.subplots()
        self.ax.grid()
        self.ax.set_xlabel('t [ms]')
        self.line1, = self.ax.plot([0], [0], '-b')
        self.line2, = self.ax.plot([0], [0], '-g')
        self.markers, = self.ax.plot([0], [0], '+r')
        self.m_inj, = self.ax.plot([0], [0], 'or')
        self.m_ej, = self.ax.plot([0], [0], 'or')

    def _setupTable(self):
        self.table_map = {
            'rows': {'Injection': 0,
                     'Ejection': self.normalized_configs_count+1},
            'columns': {'': 0,
                        'T [ms]': 1,
                        'Index': 2,
                        'E [GeV]': 3,
                        'ΔIndex': 4,
                        'v [MeV/pt]': 5}}
        idx = 1
        normalized_config_rows = list()
        for config in self.normalized_configs:
            self.table_map['rows'][config[1]] = idx
            normalized_config_rows.append(idx)
            idx += 1

        self.table.setStyleSheet(
            """
            QHeaderView::section {
                background-color: #FF7C52;
            }
            QTableWidget {
                background-color: #FFDDD2;
                gridline-color: #BD0000;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #FF7C52;
            }
            """)
        self.table.setMinimumSize(
            1050, (self.normalized_configs_count+1)*48+85)
        self.table.verticalHeader().setFixedSize(
            QSize(48, (self.normalized_configs_count+1)*48+85))
        self.table.setRowCount(2+self.normalized_configs_count)
        self.table.setColumnCount(6)
        self.table.setColumnWidth(0, 250)
        for i in range(1, len(self.table_map['columns'].keys())):
            self.table.setColumnWidth(i, 150)
        self.table.setHorizontalHeaderLabels(self.table_map['columns'].keys())

        for vlabel, row in self.table_map['rows'].items():
            label_item = QTableWidgetItem(vlabel)
            t_item = _CustomTableWidgetItem('0')
            np_item = QTableWidgetItem('0')
            e_item = QTableWidgetItem('0')
            deltanp_item = QTableWidgetItem('0')
            v_item = QTableWidgetItem('0')

            label_item.setFlags(Qt.ItemIsEnabled)
            np_item.setFlags(Qt.ItemIsEnabled)
            e_item.setFlags(Qt.ItemIsEnabled)
            deltanp_item.setFlags(Qt.ItemIsEnabled)
            v_item.setFlags(Qt.ItemIsEnabled)
            if row in normalized_config_rows:
                label_item.setBackground(QBrush(QColor("white")))
                t_item.setBackground(QBrush(QColor("white")))
            else:
                t_item.setFlags(Qt.ItemIsEnabled)

            self.table.setItem(row, 0, label_item)
            self.table.setItem(row, 1, t_item)
            self.table.setItem(row, 2, np_item)
            self.table.setItem(row, 3, e_item)
            self.table.setItem(row, 4, deltanp_item)
            self.table.setItem(row, 5, v_item)

            self.table.setRowHeight(row, 48)

        self.table.setItemDelegate(_SpinBoxDelegate())
        self.table.cellChanged.connect(self._handleCellChanged)

    def _getNormalizedConfigs(self):
        if self.ramp_config is not None:
            self.normalized_configs = self.ramp_config.normalized_configs
            self.normalized_configs_count = len(self.normalized_configs)
        else:
            self.normalized_configs = list()
            self.normalized_configs_count = 0

    def _sortTable(self):
        self.table.sortByColumn(1, Qt.AscendingOrder)
        for row in range(self.table.rowCount()):
            self.table_map['rows'][self.table.item(row, 0).text()] = row

    def _handleCellChanged(self, row, column):
        try:
            config_changed_name = self.table.item(row, 0).data(
                Qt.DisplayRole)
            self.ramp_config.normalized_configs_change_time(
                config_changed_name,
                float(self.table.item(row, column).data(Qt.DisplayRole)))
        except exceptions.RampInvalidNormConfig as e:
            err_msg = _MessageBox(self, 'Error', str(e), 'Ok')
            err_msg.show()
        finally:
            self.updateTable()
            self.updateGraph()
        self.updateMultipoleRampSignal.emit()

    def _showInsertNormConfigPopup(self):
        if self.ramp_config is not None:
            self._insertConfigPopup = _InsertNormalizedConfig(self)
            self._insertConfigPopup.insertConfig.connect(
                self._handleInsertNormConfig)
            self._insertConfigPopup.show()

    @pyqtSlot(list)
    def _handleInsertNormConfig(self, config):
        try:
            self.ramp_config.normalized_configs_insert(time=config[0],
                                                       name=config[1],
                                                       nconfig=config[2])
            if config[3] == 1:  # got an existing one
                self.ramp_config.configsrv_load_normalized_configs()
        except exceptions.RampInvalidNormConfig as e:
            err_msg = _MessageBox(self, 'Error', str(e), 'Ok')
            err_msg.show()
        self.handleLoadRampConfig()
        self.updateMultipoleRampSignal.emit()

    def _showDeleteNormConfigPopup(self):
        if self.ramp_config is not None:
            self._deleteConfigPopup = _DeleteNormalizedConfig(self,
                                                              self.table_map)
            self._deleteConfigPopup.deleteConfig.connect(
                self._handleDeleteNormConfig)
            self._deleteConfigPopup.show()

    @pyqtSlot(str)
    def _handleDeleteNormConfig(self, config):
        self.ramp_config.normalized_configs_delete(config)
        self.handleLoadRampConfig()
        self.updateMultipoleRampSignal.emit()

    def updateGraph(self):
        if self.ramp_config is not None:
            maname = [self.cb_maname.currentText()]
            xdata = self.ramp_config.waveform_get_times()
            if maname[0] == 'Quadrupoles':
                maname = ['BO-Fam:MA-QF', 'BO-Fam:MA-QD']
                self.line2.set_linewidth(2)
                y1 = self.ramp_config.waveform_get_strengths(maname[0])
                y2 = self.ramp_config.waveform_get_strengths(maname[1])
                self.line1.set_xdata(xdata)
                self.line2.set_xdata(xdata)
                self.line1.set_ydata(y1)
                self.line2.set_ydata(y2)
                ydata = np.array([y1, y2])
            elif maname[0] == 'Sextupoles':
                maname = ['BO-Fam:MA-SF', 'BO-Fam:MA-SD']
                self.line2.set_linewidth(2)
                y1 = self.ramp_config.waveform_get_strengths(maname[0])
                y2 = self.ramp_config.waveform_get_strengths(maname[1])
                self.line1.set_xdata(xdata)
                self.line2.set_xdata(xdata)
                self.line1.set_ydata(y1)
                self.line2.set_ydata(y2)
                ydata = np.array([y1, y2])
            else:
                self.line2.set_linewidth(0)
                ydata = self.ramp_config.waveform_get(maname[0])
                self.line1.set_xdata(xdata)
                self.line1.set_ydata(ydata)
                ydata = np.array(ydata)
            self.ax.set_xlim(min(xdata)-0.2, max(xdata)+0.2)
            self.ax.set_ylim(ydata.min()-0.2, ydata.max()+0.2)

            if 'MA-Q' in maname[0]:
                self.ax.set_ylabel('KL [1/m]')
            elif 'MA-S' in maname[0]:
                self.ax.set_ylabel('SL [1/m$^2$]')
            else:
                self.ax.set_ylabel('Kick [rad]')

            markers_time = self.ramp_config.ramp_dipole_time
            self.markers.set_xdata(markers_time)
            if len(maname) > 1:
                self.markers.set_xdata([markers_time, markers_time])
            inj_marker_time = self.ramp_config.injection_time
            self.m_inj.set_xdata(inj_marker_time)
            ej_marker_time = self.ramp_config.ejection_time
            self.m_ej.set_xdata(ej_marker_time)

            markers_value = list()
            inj_marker_value = list()
            ej_marker_value = list()
            for name in maname:
                markers_value.append(
                    self.ramp_config.waveform_interp_strengths(
                        name, markers_time))
                inj_marker_value.append(
                    self.ramp_config.waveform_interp_strengths(
                        name, inj_marker_time))
                ej_marker_value.append(
                    self.ramp_config.waveform_interp_strengths(
                        name, ej_marker_time))
            self.markers.set_ydata(markers_value)
            self.m_inj.set_ydata(inj_marker_value)
            self.m_ej.set_ydata(ej_marker_value)

            self.graph.figure.canvas.draw()
            self.graph.figure.canvas.flush_events()

    def updateTable(self):
        self.table.cellChanged.disconnect(self._handleCellChanged)
        for label, row in self.table_map['rows'].items():
            label_item = self.table.item(row, 0)
            t_item = self.table.item(row, 1)
            e_item = self.table.item(row, 3)

            config_labels = list()
            config_times = list()
            for config in self.ramp_config.normalized_configs:
                config_labels.append(config[1])
                config_times.append(config[0])

            if label == 'Injection':
                time = self.ramp_config.injection_time
                energy = str(self.ramp_config.waveform_interp_energy(time))
            elif label == 'Ejection':
                time = self.ramp_config.ejection_time
                energy = str(self.ramp_config.waveform_interp_energy(time))
            elif label in config_labels:
                idx = config_labels.index(label)
                label_item.setData(Qt.DisplayRole, str(label))
                time = str(config_times[idx])
                energy = str(
                    self.ramp_config.waveform_interp_energy(config_times[idx]))
            t_item.setData(Qt.DisplayRole, str(time))
            e_item.setData(Qt.DisplayRole, str(energy))

        for row in self.table_map['rows'].values():
            for label, column in self.table_map['columns'].items():
                if label == 'Index':
                    D = self.ramp_config.ramp_dipole_duration
                    N = self.ramp_config.ramp_dipole_wfm_nrpoints
                    T = float(self.table.item(
                        row, self.table_map['columns']['T [ms]']).data(
                            Qt.DisplayRole))
                    value = round(T*N/D)
                    item = self.table.item(row, column)
                    item.setData(Qt.DisplayRole, str(value))
                elif label == 'v [MeV/pt]':
                    if row == 0:
                        value = '-'
                    else:
                        T1 = float(self.table.item(
                            row, self.table_map['columns']['T [ms]']).data(
                                Qt.DisplayRole))
                        T2 = float(self.table.item(
                            row-1, self.table_map['columns']['T [ms]']).data(
                                Qt.DisplayRole))
                        dT = T1 - T2
                        E1 = float(self.table.item(
                            row, self.table_map['columns']['E [GeV]']).data(
                                Qt.DisplayRole))
                        E2 = float(self.table.item(
                            row-1, self.table_map['columns']['E [GeV]']).data(
                                Qt.DisplayRole))
                        dE = E1 - E2
                        value = dE*1000/dT
                    item = self.table.item(row, column)
                    item.setData(Qt.DisplayRole, str(value))
        for row in self.table_map['rows'].values():
            if row == 0:
                value = '-'
            else:
                idx1 = float(self.table.item(
                    row, self.table_map['columns']['Index']).data(
                        Qt.DisplayRole))
                idx2 = float(self.table.item(
                    row-1, self.table_map['columns']['Index']).data(
                        Qt.DisplayRole))
                value = int(idx1 - idx2)
            item = self.table.item(row, self.table_map['columns']['ΔIndex'])
            item.setData(Qt.DisplayRole, str(value))
        self._sortTable()
        self.table.cellChanged.connect(self._handleCellChanged)

    @pyqtSlot()
    def handleLoadRampConfig(self):
        self._getNormalizedConfigs()
        self.table.cellChanged.disconnect(self._handleCellChanged)
        self._setupTable()
        self.updateTable()
        self.updateGraph()


class RFRamp(QWidget):

    def __init__(self, parent=None, prefix='', ramp_config=None):
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self.ramp_config = ramp_config
        self._setupUi()

    def _setupUi(self):
        vlay = QVBoxLayout(self)
        self.graph = FigureCanvas(Figure())
        self.set_nrpoints = QHBoxLayout()
        self.table = QTableWidget(self)

        self._setupGraph()
        label_nrpoints = QLabel('# of points', self)
        label_nrpoints.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.sb_nrpoints = QSpinBox(self)
        self.set_nrpoints.addSpacerItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        self.set_nrpoints.addWidget(label_nrpoints)
        self.set_nrpoints.addWidget(self.sb_nrpoints)
        self.set_nrpoints.addSpacerItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        self._setupWfmNrPoints()
        self._setupTable()

        label = QLabel('<h4>RF Ramp</h4>', self)
        label.setFixedHeight(48)
        label.setAlignment(Qt.AlignCenter)
        vlay.addWidget(label)
        vlay.addWidget(self.graph)
        vlay.addLayout(self.set_nrpoints)
        vlay.addWidget(self.table)

    def _setupGraph(self):
        self.ax = self.graph.figure.subplots()
        self.ax.grid()
        self.ax.set_xlabel('t [ms]')
        self.line1, = self.ax.plot([0], [0], '-b')
        self.markers, = self.ax.plot([0], [0], '+r')

    def _setupWfmNrPoints(self):
        pass

    def _setupTable(self):
        self.table_map = {
            'rows': {'Start': 0,
                     'Start UP': 1,
                     'End UP': 2,
                     'Flat Top': 3,
                     'Start DWN': 4,
                     'End DWN': 5,
                     'End': 6},
            'columns': {'': 0,
                        'T [ms]': 1,
                        'Index': 2,
                        'E [GeV]': 3,
                        'Vgap [kV]': 4,
                        'v [MeV/pt]': 5}}
        self.table.setStyleSheet(
            """
            QHeaderView::section {
                background-color: #4A5E28;
            }
            QTableWidget {
                background-color: #EAFFC0;
                gridline-color: #1D3000;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #4A5E28;
            }
            """)
        self.table.setFixedSize(1002, self.table_map['rows']['End']*48+85)
        self.table.setRowCount(7)
        self.table.setColumnCount(6)
        self.table.setColumnWidth(0, 250)
        for i in range(1, len(self.table_map['columns'].keys())):
            self.table.setColumnWidth(i, 150)
        self.table.verticalHeader().hide()
        self.table.setHorizontalHeaderLabels(self.table_map['columns'].keys())

        for vlabel, row in self.table_map['rows'].items():
            label_item = QTableWidgetItem(vlabel)
            t_item = QTableWidgetItem('0')
            np_item = QTableWidgetItem('0')
            e_item = QTableWidgetItem('0')
            Vgap_item = QTableWidgetItem('0')
            v_item = QTableWidgetItem('0')

            label_item.setFlags(Qt.ItemIsEnabled)
            np_item.setFlags(Qt.ItemIsEnabled)
            e_item.setFlags(Qt.ItemIsEnabled)
            v_item.setFlags(Qt.ItemIsEnabled)
            if vlabel in ['Start', 'End']:
                t_item.setFlags(Qt.ItemIsEnabled)
                Vgap_item.setFlags(Qt.ItemIsEnabled)
            elif vlabel in ['Start UP', 'End UP']:
                t_item.setBackground(QBrush(QColor("white")))
                Vgap_item.setBackground(QBrush(QColor("white")))
            else:
                t_item.setBackground(QBrush(QColor("white")))
                Vgap_item.setFlags(Qt.ItemIsEnabled)

            self.table.setItem(row, 0, label_item)
            self.table.setItem(row, 1, t_item)
            self.table.setItem(row, 2, np_item)
            self.table.setItem(row, 3, e_item)
            self.table.setItem(row, 4, Vgap_item)
            self.table.setItem(row, 5, v_item)

            self.table.setRowHeight(row, 48)

        self.table.setItemDelegate(_SpinBoxDelegate())
        self.table.cellChanged.connect(self._handleCellChanged)

    @pyqtSlot(int, int)
    def _handleCellChanged(self, row, column):
        pass

    def updateGraph(self):
        pass

    def updateWfmNrPoints(self):
        pass

    def updateTable(self):
        pass

    @pyqtSlot()
    def handleLoadRampConfig(self):
        self.table.cellChanged.disconnect(self._handleCellChanged)
        self._setupTable()
        self.updateTable()
        self.updateWfmNrPoints()
        self.updateGraph()


class OpticsAdjust(QGroupBox):

    def __init__(self, parent=None, prefix='', ramp_config=None):
        super().__init__('Optics Configuration Adjustment', parent)
        self.prefix = _PVName(prefix)
        self.ramp_config = ramp_config
        self._setupUi()

    def _setupUi(self):
        glay = QGridLayout(self)
        self.bt_load = QPushButton('Load', self)
        self.bt_save = QPushButton('Save', self)
        self.bt_load.clicked.connect(self._load)
        self.bt_save.clicked.connect(self._save)
        glay.addWidget(self.bt_load, 0, 0)
        glay.addWidget(self.bt_save, 0, 1)

    def _load(self):
        print('Do stuff')

    def _save(self):
        print('Do stuff')


class RampStatistics(QGroupBox):

    def __init__(self, parent=None, prefix='', ramp_config=None):
        super().__init__('Statistics', parent)
        self.prefix = _PVName(prefix)
        self.ramp_config = ramp_config
        self._setupUi()

    def _setupUi(self):
        pass


class _InsertNormalizedConfig(SiriusMainWindow):

    insertConfig = pyqtSignal(list)

    def __init__(self, parent):
        """Initialize object."""
        super().__init__(parent)
        self.normalized_config = ramp.BoosterNormalized()
        self.setWindowTitle('Insert Normalized Configuration')
        self._setupUi()

    def _setupUi(self):
        vlay = QVBoxLayout()
        vlay.addWidget(
            QLabel('<h4>Insert a Normalized Configuration</h4>', self),
            alignment=Qt.AlignCenter)

        self.rb_interp = QRadioButton('By interpolation')
        self.rb_confsrv = QRadioButton(
            'By taking an existing one from Config Server')
        self.rb_create = QRadioButton('By creating a new configuration')
        self.config_data = QWidget()
        self._setupConfigDataWidget()

        self.rb_interp.toggled.connect(self.interp_settings.setVisible)
        self.rb_interp.setChecked(True)
        self.rb_confsrv.toggled.connect(self.confsrv_settings.setVisible)
        self.rb_create.toggled.connect(self.create_settings.setVisible)

        vlay.addSpacerItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        vlay.addWidget(self.rb_interp)
        vlay.addWidget(self.rb_confsrv)
        vlay.addWidget(self.rb_create)
        vlay.addSpacerItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        vlay.addWidget(self.config_data)

        self.cw = QWidget()
        self.cw.setLayout(vlay)
        self.setCentralWidget(self.cw)

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
        self.interp_settings.setFixedSize(600, 750)
        self.confsrv_settings.setFixedSize(600, 750)
        self.create_settings.setFixedSize(600, 750)

        flay_interp = QFormLayout()
        flay_interp.setLabelAlignment(Qt.AlignRight)
        self.le_interp_name = QLineEdit(self)
        self.sb_interp_time = QDoubleSpinBox(self)
        self.sb_interp_time.setMaximum(490)
        self.bt_interp = QPushButton('Insert', self)
        self.bt_interp.clicked.connect(self._emitInsertConfigData)
        flay_interp.addRow(QLabel('Name: ', self), self.le_interp_name)
        flay_interp.addRow(QLabel('Time: ', self), self.sb_interp_time)
        flay_interp.addRow(self.bt_interp)

        flay_confsrv = QFormLayout()
        flay_confsrv.setLabelAlignment(Qt.AlignRight)
        self.cb_confsrv_name = QComboBox(self)
        self.cb_confsrv_name.setStyleSheet(
            """ QComboBox::item {
                    height: 30px;}
            """)
        metadata = self.normalized_config.configsrv_find()
        for data in metadata:
            self.cb_confsrv_name.addItem(data['name'])
        self.sb_confsrv_time = QDoubleSpinBox(self)
        self.sb_confsrv_time.setMaximum(490)
        self.bt_confsrv = QPushButton('Insert', self)
        self.bt_confsrv.clicked.connect(self._emitInsertConfigData)
        flay_confsrv.addRow(QLabel('Name: ', self), self.cb_confsrv_name)
        flay_confsrv.addRow(QLabel('Time: ', self), self.sb_confsrv_time)
        flay_confsrv.addRow(self.bt_confsrv)

        flay_create = QFormLayout()
        self.le_create_name = QLineEdit(self)
        scrollarea = QScrollArea()
        scrollarea.setMinimumWidth(590)
        self.data = QWidget()
        flay_configdata = QFormLayout()
        flay_configdata.setLabelAlignment(Qt.AlignRight)
        config_template = self.normalized_config.get_config_type_template()
        for ma in config_template.keys():
            ma_value = QDoubleSpinBox(self.data)
            ma_value.setObjectName(ma)
            flay_configdata.addRow(QLabel(ma + ': ', self), ma_value)
        self.data.setLayout(flay_configdata)
        scrollarea.setWidget(self.data)
        self.sb_create_time = QDoubleSpinBox(self)
        self.sb_create_time.setMaximum(490)
        self.bt_create = QPushButton('Insert', self)
        self.bt_create.clicked.connect(self._emitInsertConfigData)
        flay_create.addRow(QLabel('Name: ', self), self.le_create_name)
        flay_create.addRow(scrollarea)
        flay_create.addRow(QLabel('Time: ', self), self.sb_create_time)
        flay_create.addRow(self.bt_create)

        self.interp_settings.setLayout(flay_interp)
        self.confsrv_settings.setLayout(flay_confsrv)
        self.create_settings.setLayout(flay_create)

    def _emitInsertConfigData(self):
        sender = self.sender()
        data = list()
        if sender is self.bt_interp:
            time = self.sb_interp_time.value()
            name = self.le_interp_name.text()
            nconfig = None
            option = 0
        elif sender is self.bt_confsrv:
            time = self.sb_confsrv_time.value()
            name = self.cb_confsrv_name.currentText()
            nconfig = None
            option = 1
        elif sender is self.bt_create:
            time = self.sb_create_time.value()
            name = self.le_create_name.text()
            config_template = self.normalized_config.get_config_type_template()
            nconfig = dict()
            for ma in config_template.keys():
                w = self.data.findChild(QDoubleSpinBox, name=ma)
                nconfig[ma] = w.value()
            option = 2
        data = [time, name, nconfig, option]
        self.insertConfig.emit(data)
        self.close()


class _DeleteNormalizedConfig(SiriusMainWindow):

    deleteConfig = pyqtSignal(str)

    def __init__(self, parent, table_map):
        """Initialize object."""
        super().__init__(parent)
        self.normalized_config = ramp.BoosterNormalized()
        self.setWindowTitle('Delete Normalized Configuration')
        self.table_map = table_map
        self._setupUi()

    def _setupUi(self):
        glay = QGridLayout()
        label = QLabel('<h4>Delete a Normalized Configuration</h4>', self)
        label.setAlignment(Qt.AlignCenter)
        glay.addWidget(label, 0, 0, 1, 2)

        self.sb_confignumber = QSpinBox(self)
        self.sb_confignumber.setMinimum(1)
        self.sb_confignumber.setMaximum(max(self.table_map['rows'].values())+1)
        self.sb_confignumber.setMaximumWidth(150)
        self.sb_confignumber.valueChanged.connect(self._searchConfigByIndex)
        self.bt_delete = QPushButton('Delete', self)
        self.bt_delete.clicked.connect(self._emitDeleteConfigData)
        for key, value in self.table_map['rows'].items():
            if value == 0:
                label = key
                self.l_configname = QLabel(label, self)
                self.l_configname.setSizePolicy(QSzPlcy.MinimumExpanding,
                                                QSzPlcy.Preferred)
                if label in ['Injection', 'Ejection']:
                    self.bt_delete.setEnabled(False)
                else:
                    self.bt_delete.setEnabled(True)
                break

        glay.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 1, 0)
        glay.addWidget(self.sb_confignumber, 2, 0)
        glay.addWidget(self.l_configname, 2, 1)
        glay.addItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum), 3, 0)
        glay.addWidget(self.bt_delete, 4, 0, 1, 2)

        self.cw = QWidget()
        self.cw.setLayout(glay)
        self.setCentralWidget(self.cw)

    @pyqtSlot(int)
    def _searchConfigByIndex(self, config_idx):
        for label, value in self.table_map['rows'].items():
            if config_idx == (value + 1):
                self.l_configname.setText(label)
                if label in ['Injection', 'Ejection']:
                    self.bt_delete.setEnabled(False)
                else:
                    self.bt_delete.setEnabled(True)
                break

    def _emitDeleteConfigData(self):
        self.deleteConfig.emit(self.l_configname.text())
        self.close()


class _SpinBoxDelegate(QStyledItemDelegate):

    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setMinimum(0)
        editor.setMaximum(500)
        editor.setDecimals(4)
        return editor

    def setEditorData(self, spinBox, index):
        value = index.model().data(index, Qt.EditRole)
        spinBox.setValue(float(value))

    def setModelData(self, spinBox, model, index):
        spinBox.interpretText()
        value = spinBox.value()
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, spinBox, option, index):
        spinBox.setGeometry(option.rect)


class _MessageBox(SiriusDialog):

    acceptedSignal = pyqtSignal()
    regectedSignal = pyqtSignal()

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
        self.regectedSignal.emit()
        self.close()


class _CustomTableWidgetItem(QTableWidgetItem):

    def __init__(self, value):
        super().__init__('{}'.format(value))

    def __lt__(self, other):
        if isinstance(other, _CustomTableWidgetItem):
            selfDataValue = float(self.data(Qt.EditRole))
            otherDataValue = float(other.data(Qt.EditRole))
            return selfDataValue < otherDataValue
        else:
            return QTableWidgetItem.__lt__(self, other)


if __name__ == '__main__':
    """Run Example."""
    app = SiriusApplication()
    _util.set_style(app)
    w = RampMain(
        prefix='ca://fernando-lnls452-linux-AS-Glob:TI-EVG:')
    w.show()
    sys.exit(app.exec_())
