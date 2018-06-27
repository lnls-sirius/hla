"""Booster Ramp Control HLA: Ramp Parameters Module."""

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QGroupBox, QLabel, QWidget, QSpacerItem, \
                            QVBoxLayout, QHBoxLayout, QGridLayout, \
                            QPushButton, QTableWidget, QTableWidgetItem, \
                            QComboBox, QSpinBox, QSizePolicy as QSzPlcy
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas)
from matplotlib.figure import Figure
import numpy as np
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.ramp import ramp, exceptions
from siriuspy.csdevice.pwrsupply import MAX_WFMSIZE
from auxiliar_classes import MessageBox as _MessageBox, \
    InsertNormalizedConfig as _InsertNormalizedConfig, \
    DeleteNormalizedConfig as _DeleteNormalizedConfig, \
    SpinBoxDelegate as _SpinBoxDelegate, \
    CustomTableWidgetItem as _CustomTableWidgetItem


class RampParameters(QGroupBox):
    """Widget to set and monitor ramp parametes."""

    def __init__(self, parent=None, prefix='', ramp_config=None):
        """Initialize object."""
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
    """Widget to set and monitor dipole ramp."""

    updateDipoleRampSignal = pyqtSignal()

    def __init__(self, parent=None, prefix='', ramp_config=None):
        """Initialize object."""
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
        self.sb_nrpoints.setMinimum(1)
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
                self.ramp_config.start_energy = energy

            elif row == self.table_map['rows']['RampUp-Start']:
                if column == self.table_map['columns']['T [ms]']:
                    time = float(self.table.item(row, column).data(
                        Qt.DisplayRole))
                    self.ramp_config.rampup_start_time = time
                elif column == self.table_map['columns']['E [GeV]']:
                    energy = float(self.table.item(row, column).data(
                        Qt.DisplayRole))
                    self.ramp_config.rampup_start_energy = energy

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
                    self.ramp_config.rampup_stop_energy = energy

            elif row == self.table_map['rows']['RampDown-Start']:
                if column == self.table_map['columns']['T [ms]']:
                    time = float(self.table.item(row, column).data(
                        Qt.DisplayRole))
                    self.ramp_config.rampdown_start_time = time
                elif column == self.table_map['columns']['E [GeV]']:
                    energy = float(self.table.item(row, column).data(
                        Qt.DisplayRole))
                    self.ramp_config.rampdown_start_energy = energy

            elif row == self.table_map['rows']['RampDown-Stop']:
                if column == self.table_map['columns']['T [ms]']:
                    time = float(self.table.item(row, column).data(
                        Qt.DisplayRole))
                    self.ramp_config.rampdown_stop_time = time
                elif column == self.table_map['columns']['E [GeV]']:
                    energy = float(self.table.item(row, column).data(
                        Qt.DisplayRole))
                    self.ramp_config.rampdown_stop_energy = energy
        except exceptions.RampInvalidDipoleWfmParms as e:
            err_msg = _MessageBox(self, 'Error', str(e), 'Ok')
            err_msg.show()
        finally:
            self.updateTable()
            self.updateGraph()
            self.updateDipoleRampSignal.emit()

    def updateGraph(self):
        """Update and redraw graph."""
        if self.ramp_config is not None:
            xdata = self.ramp_config.waveform_get_times()
            ydata = self.ramp_config.waveform_get('BO-Fam:MA-B')
            self.line.set_xdata(xdata)
            self.line.set_ydata(ydata)
            self.ax.set_xlim(min(xdata)-0.2, max(xdata)+0.2)
            self.ax.set_ylim(min(ydata)-0.2, max(ydata)+0.2)

            self.markers.set_xdata(self.ramp_config.ramp_dipole_times)
            self.markers.set_ydata(self.ramp_config.ramp_dipole_energies)

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
        """Update waveform number of points."""
        self.ramp_config.ramp_dipole_wfm_nrpoints = self.sb_nrpoints.value()
        self.updateDipoleRampSignal.emit()

    def updateTable(self):
        """Update and rebuild table."""
        self.table.cellChanged.disconnect(self._handleCellChanged)
        for label, row in self.table_map['rows'].items():
            t_item = self.table.item(row, 1)
            e_item = self.table.item(row, 3)
            if label == 'Start':
                time = str(0.0)
                energy = str(self.ramp_config.start_energy)
            elif label == 'RampUp-Start':
                time = str(self.ramp_config.rampup_start_time)
                energy = str(self.ramp_config.rampup_start_energy)
            elif label == 'Injection':
                time = self.ramp_config.injection_time
                energy = str(self.ramp_config.waveform_interp_energy(time))
            elif label == 'Ejection':
                time = self.ramp_config.ejection_time
                energy = str(self.ramp_config.waveform_interp_energy(time))
            elif label == 'RampUp-Stop':
                time = str(self.ramp_config.rampup_stop_time)
                energy = str(self.ramp_config.rampup_stop_energy)
            elif label == 'Plateau-Start':
                time = str(self.ramp_config.plateau_start_time)
                energy = str(self.ramp_config.plateau_energy)
            elif label == 'RampDown-Start':
                time = str(self.ramp_config.rampdown_start_time)
                energy = str(self.ramp_config.rampdown_start_energy)
            elif label == 'RampDown-Stop':
                time = str(self.ramp_config.rampdown_stop_time)
                energy = str(self.ramp_config.rampdown_stop_energy)
            elif label == 'Stop':
                time = str(self.ramp_config.ramp_dipole_duration)
                energy = str(self.ramp_config.start_energy)
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
        """Update all widgets in loading BoosterRamp config."""
        self.updateTable()
        self.updateWfmNrPoints()
        self.updateGraph()


class MultipolesRamp(QWidget):
    """Widget to set and monitor multipoles ramp."""

    updateMultipoleRampSignal = pyqtSignal()

    def __init__(self, parent=None, prefix='', ramp_config=None):
        """Initialize object."""
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
        """Update and redraw graph."""
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

            # markers_time = self.ramp_config.ramp_dipole_times
            markers_time = self.ramp_config.ramp_dipole_times
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
        """Update and rebuild table."""
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
        """Update all widgets in loading BoosterRamp config."""
        self._getNormalizedConfigs()
        self.table.cellChanged.disconnect(self._handleCellChanged)
        self._setupTable()
        self.updateTable()
        self.updateGraph()


class RFRamp(QWidget):
    """Widget to set and monitor RF ramp."""

    def __init__(self, parent=None, prefix='', ramp_config=None):
        """Initialize object."""
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
        """Update and redraw graph."""
        pass

    def updateWfmNrPoints(self):
        pass

    def updateTable(self):
        """Update and rebuild table."""
        pass

    @pyqtSlot()
    def handleLoadRampConfig(self):
        """Update all widgets in loading BoosterRamp config."""
        self.table.cellChanged.disconnect(self._handleCellChanged)
        self._setupTable()
        self.updateTable()
        self.updateWfmNrPoints()
        self.updateGraph()
