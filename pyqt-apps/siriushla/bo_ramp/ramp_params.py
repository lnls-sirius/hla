"""Booster Ramp Control HLA: Ramp Parameters Module."""

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QGroupBox, QLabel, QWidget, QSpacerItem, \
                            QVBoxLayout, QHBoxLayout, QGridLayout, \
                            QPushButton, QTableWidget, QTableWidgetItem, \
                            QSpinBox, QSizePolicy as QSzPlcy, \
                            QAbstractItemView, QUndoCommand
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import numpy as np
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.ramp import ramp, exceptions
from siriuspy.csdevice.pwrsupply import MAX_WFMSIZE
from siriushla.bo_ramp.auxiliar_classes import MessageBox as _MessageBox, \
    InsertNormalizedConfig as _InsertNormalizedConfig, \
    DeleteNormalizedConfig as _DeleteNormalizedConfig, \
    SpinBoxDelegate as _SpinBoxDelegate, \
    CustomTableWidgetItem as _CustomTableWidgetItem, \
    ChooseMagnetsToPlot as _ChooseMagnetsToPlot


_flag_stack_next_command = True
_flag_stacking = False


class RampParameters(QGroupBox):
    """Widget to set and monitor ramp parametes."""

    def __init__(self, parent=None, prefix='', ramp_config=None,
                 undo_stack=None):
        """Initialize object."""
        super().__init__('Ramping Parameters: ', parent)
        self.prefix = _PVName(prefix)
        self.ramp_config = ramp_config
        self._undo_stack = undo_stack
        self._setupUi()

    def _setupUi(self):
        my_lay = QHBoxLayout(self)
        self.dip_ramp = DipoleRamp(
            self, self.prefix, self.ramp_config, self._undo_stack)
        self.mult_ramp = MultipolesRamp(
            self, self.prefix, self.ramp_config, self._undo_stack)
        self.rf_ramp = RFRamp(
            self, self.prefix, self.ramp_config, self._undo_stack)
        my_lay.addWidget(self.dip_ramp)
        my_lay.addWidget(self.mult_ramp)
        my_lay.addWidget(self.rf_ramp)

    @pyqtSlot(ramp.BoosterRamp)
    def handleLoadRampConfig(self, ramp_config):
        """Update all widgets when ramp_config is loaded."""
        self.ramp_config = ramp_config
        self.setTitle('Ramping Parameters: ' + self.ramp_config.name)


class DipoleRamp(QWidget):
    """Widget to set and monitor dipole ramp."""

    updateDipoleRampSignal = pyqtSignal()

    def __init__(self, parent=None, prefix='', ramp_config=None,
                 undo_stack=None):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self.ramp_config = ramp_config
        self._undo_stack = undo_stack
        self._setupUi()

    def _setupUi(self):
        vlay = QVBoxLayout(self)
        self.graphview = QWidget()
        self.nrpoints_and_duration = QHBoxLayout()
        self.table = QTableWidget(self)

        self._setupGraph()
        self._setupWfmNrPointsAndDuration()
        self._setupTable()

        hlay_caution = QHBoxLayout()
        self.label_caution = QLabel('', self)
        self.label_caution.setFixedSize(794, 40)
        self.pb_caution = QPushButton('?', self)
        self.pb_caution.setFixedWidth(48)
        self.pb_caution.setVisible(False)
        self.pb_caution.setStyleSheet('background-color: red;')
        self.pb_caution.clicked.connect(self._showAnomaliesPopup)
        hlay_caution.addWidget(self.label_caution)
        hlay_caution.addWidget(self.pb_caution)

        label = QLabel('<h4>Dipole Ramp</h4>', self)
        label.setAlignment(Qt.AlignCenter)
        label.setFixedHeight(48)
        vlay.addWidget(label)
        vlay.addWidget(self.graphview)
        vlay.addLayout(self.nrpoints_and_duration)
        vlay.addWidget(self.table)
        vlay.addLayout(hlay_caution)
        vlay.addItem(QSpacerItem(40, 20, QSzPlcy.Minimum, QSzPlcy.Expanding))

    def _setupGraph(self):
        self.graph = FigureCanvas(Figure())
        self.graph.setFixedHeight(500)
        self.ax = self.graph.figure.subplots()
        self.ax.grid()
        self.ax.set_xlabel('t [ms]')
        self.ax.set_ylabel('E [GeV]')
        self.line, = self.ax.plot([0], [0], '-b')
        self.markers, = self.ax.plot([0], [0], '+r')
        self.m_inj, = self.ax.plot([0], [0], 'or')
        self.m_ej, = self.ax.plot([0], [0], 'or')

        self.toolbar = NavigationToolbar(self.graph, self)

        lay = QVBoxLayout()
        lay.addWidget(self.graph)
        lay.addWidget(self.toolbar)
        self.graphview.setLayout(lay)

    def _setupWfmNrPointsAndDuration(self):
        label_nrpoints = QLabel('# of points: ', self,
                                alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.sb_nrpoints = QSpinBox(self)
        self.sb_nrpoints.setMinimum(1)
        self.sb_nrpoints.setMaximum(MAX_WFMSIZE)
        self.sb_nrpoints.editingFinished.connect(self._handleChangeNrPoints)

        label_duration = QLabel('Duration (ms): ', self,
                                alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.sb_duration = QSpinBox(self)
        self.sb_duration.setMinimum(1)
        self.sb_duration.setMaximum(490)
        self.sb_duration.editingFinished.connect(self._handleChangeDuration)

        self.nrpoints_and_duration.addSpacerItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        self.nrpoints_and_duration.addWidget(label_nrpoints)
        self.nrpoints_and_duration.addWidget(self.sb_nrpoints)
        self.nrpoints_and_duration.addSpacerItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        self.nrpoints_and_duration.addWidget(label_duration)
        self.nrpoints_and_duration.addWidget(self.sb_duration)
        self.nrpoints_and_duration.addSpacerItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))

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
            new_value = float(self.table.item(row, column).data(
                Qt.DisplayRole))
            if row == self.table_map['rows']['Start']:
                old_value = self.ramp_config.start_energy
                self.ramp_config.start_energy = new_value

            elif row == self.table_map['rows']['RampUp-Start']:
                if column == self.table_map['columns']['T [ms]']:
                    old_value = self.ramp_config.rampup_start_time
                    self.ramp_config.rampup_start_time = new_value
                elif column == self.table_map['columns']['E [GeV]']:
                    old_value = self.ramp_config.rampup_start_energy
                    self.ramp_config.rampup_start_energy = new_value

            elif row == self.table_map['rows']['Injection']:
                if column == self.table_map['columns']['T [ms]']:
                    old_value = self.ramp_config.injection_time
                    self.ramp_config.injection_time = new_value

            elif row == self.table_map['rows']['Ejection']:
                if column == self.table_map['columns']['T [ms]']:
                    old_value = self.ramp_config.ejection_time
                    self.ramp_config.ejection_time = new_value

            elif row == self.table_map['rows']['RampUp-Stop']:
                if column == self.table_map['columns']['T [ms]']:
                    old_value = self.ramp_config.rampup_stop_time
                    self.ramp_config.rampup_stop_time = new_value
                elif column == self.table_map['columns']['E [GeV]']:
                    old_value = self.ramp_config.rampup_stop_energy
                    self.ramp_config.rampup_stop_energy = new_value

            elif row == self.table_map['rows']['RampDown-Start']:
                if column == self.table_map['columns']['T [ms]']:
                    old_value = self.ramp_config.rampdown_start_time
                    self.ramp_config.rampdown_start_time = new_value
                elif column == self.table_map['columns']['E [GeV]']:
                    old_value = self.ramp_config.rampdown_start_energy
                    self.ramp_config.rampdown_start_energy = new_value

            elif row == self.table_map['rows']['RampDown-Stop']:
                if column == self.table_map['columns']['T [ms]']:
                    old_value = self.ramp_config.rampdown_stop_time
                    self.ramp_config.rampdown_stop_time = new_value
                elif column == self.table_map['columns']['E [GeV]']:
                    old_value = self.ramp_config.rampdown_stop_energy
                    self.ramp_config.rampdown_stop_energy = new_value

        except exceptions.RampInvalidDipoleWfmParms as e:
            err_msg = _MessageBox(self, 'Error', str(e), 'Ok')
            err_msg.open()
        else:
            self.updateGraph()
            self.updateDipoleRampSignal.emit()
            if len(self.ramp_config.waveform_anomalies) > 0:
                self.label_caution.setText('<h6>Caution: there are anomalies '
                                           'in the waveforms.</h6>')
                self.pb_caution.setVisible(True)
            else:
                self.label_caution.setText('')
                self.pb_caution.setVisible(False)

            global _flag_stack_next_command, _flag_stacking
            if _flag_stack_next_command:
                _flag_stacking = True
                command = _CommandChangeTableCell(
                    self.table, row, column, old_value, new_value,
                    'set dipole table item at row {0}, column {1}'.format(
                        row, column))
                self._undo_stack.push(command)
            else:
                _flag_stack_next_command = True
        finally:
            self.updateTable()

    @pyqtSlot()
    def _handleChangeNrPoints(self):
        """Handle change waveform number of points."""
        old_value = self.ramp_config.ramp_dipole_wfm_nrpoints
        new_value = self.sb_nrpoints.value()

        try:
            self.ramp_config.ramp_dipole_wfm_nrpoints = new_value
        except exceptions.RampInvalidDipoleWfmParms as e:
            self.updateWfmNrPoints()
            err_msg = _MessageBox(self, 'Error', str(e), 'Ok')
            err_msg.open()
        else:
            self.updateGraph()
            self.updateDipoleRampSignal.emit()
            global _flag_stack_next_command, _flag_stacking
            if _flag_stack_next_command and (old_value != new_value):
                _flag_stacking = True
                command = _CommandChangeSpinbox(
                    self.sb_nrpoints, old_value, new_value,
                    'set dipole ramp number of points to {}'.format(new_value))
                self._undo_stack.push(command)
            else:
                _flag_stack_next_command = True
        finally:
            self.updateTable()

    @pyqtSlot()
    def _handleChangeDuration(self):
        """Handle change waveform duration."""
        old_value = self.ramp_config.ramp_dipole_duration
        new_value = self.sb_duration.value()

        try:
            self.ramp_config.ramp_dipole_duration = new_value
        except exceptions.RampInvalidDipoleWfmParms as e:
            self.updateDuration()
            err_msg = _MessageBox(self, 'Error', str(e), 'Ok')
            err_msg.open()
        else:
            self.updateGraph()
            self.updateDipoleRampSignal.emit()
            global _flag_stack_next_command, _flag_stacking
            if _flag_stack_next_command and (old_value != new_value):
                _flag_stacking = True
                command = _CommandChangeSpinbox(
                    self.sb_duration, old_value, new_value,
                    'set dipole ramp duration to {}'.format(new_value))
                self._undo_stack.push(command)
            else:
                _flag_stack_next_command = True
        finally:
            self.updateTable()

    def _showAnomaliesPopup(self):
        text = 'Caution to the following anomalies: \n'
        for anom in self.ramp_config.waveform_anomalies:
            text += anom + '\n'
        anomaliesPopup = _MessageBox(self, 'Caution', text, 'Ok')
        anomaliesPopup.open()

    def updateGraph(self):
        """Update and redraw graph when ramp_config is loaded."""
        if self.ramp_config is not None:
            xdata = self.ramp_config.waveform_get_times()
            ydata = self.ramp_config.waveform_get_strengths('BO-Fam:MA-B')
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

    def updateWfmNrPoints(self):
        """Update waveform number of points when ramp_config is loaded."""
        self.sb_nrpoints.setValue(self.ramp_config.ramp_dipole_wfm_nrpoints)

    def updateDuration(self):
        """Update waveform duration when ramp_config is loaded."""
        self.sb_duration.setValue(self.ramp_config.ramp_dipole_duration)

    def updateTable(self):
        """Update and rebuild table when ramp_config is loaded."""
        self.table.cellChanged.disconnect(self._handleCellChanged)
        for label, row in self.table_map['rows'].items():
            t_item = self.table.item(row, 1)
            e_item = self.table.item(row, 3)
            if label == 'Start':
                time = 0.0
                energy = self.ramp_config.start_energy
            elif label == 'RampUp-Start':
                time = self.ramp_config.rampup_start_time
                energy = self.ramp_config.rampup_start_energy
            elif label == 'Injection':
                time = self.ramp_config.injection_time
                energy = self.ramp_config.waveform_interp_energy(time)
            elif label == 'Ejection':
                time = self.ramp_config.ejection_time
                energy = self.ramp_config.waveform_interp_energy(time)
            elif label == 'RampUp-Stop':
                time = self.ramp_config.rampup_stop_time
                energy = self.ramp_config.rampup_stop_energy
            elif label == 'Plateau-Start':
                time = self.ramp_config.plateau_start_time
                energy = self.ramp_config.plateau_energy
            elif label == 'RampDown-Start':
                time = self.ramp_config.rampdown_start_time
                energy = self.ramp_config.rampdown_start_energy
            elif label == 'RampDown-Stop':
                time = self.ramp_config.rampdown_stop_time
                energy = self.ramp_config.rampdown_stop_energy
            elif label == 'Stop':
                time = self.ramp_config.ramp_dipole_duration
                energy = self.ramp_config.start_energy
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
                        idx1 = float(self.table.item(
                            row,
                            self.table_map['columns']['Index']).data(
                            Qt.DisplayRole))
                        idx2 = float(self.table.item(
                            row-1,
                            self.table_map['columns']['Index']).data(
                            Qt.DisplayRole))
                        dIdx = idx1 - idx2
                        E1 = float(self.table.item(
                            row,
                            self.table_map['columns']['E [GeV]']).data(
                            Qt.DisplayRole))
                        E2 = float(self.table.item(
                            row-1,
                            self.table_map['columns']['E [GeV]']).data(
                            Qt.DisplayRole))
                        dE = E1 - E2
                        if dIdx != 0:
                            value = dE*1000/dIdx
                        else:
                            value = '-'
                    item = self.table.item(row, column)
                    item.setData(Qt.DisplayRole, str(value))
        self.table.cellChanged.connect(self._handleCellChanged)

    @pyqtSlot(ramp.BoosterRamp)
    def handleLoadRampConfig(self, ramp_config):
        """Update all widgets when ramp_config is loaded."""
        self.ramp_config = ramp_config
        self.updateTable()
        self.updateWfmNrPoints()
        self.updateDuration()
        self.updateGraph()
        if len(self.ramp_config.waveform_anomalies) > 0:
            self.label_caution.setText('<h6>Caution: there are anomalies '
                                       'in the waveforms.</h6>')
            self.pb_caution.setVisible(True)
        else:
            self.label_caution.setText('')
            self.pb_caution.setVisible(False)


class MultipolesRamp(QWidget):
    """Widget to set and monitor multipoles ramp."""

    updateMultipoleRampSignal = pyqtSignal()
    configsIndexChangedSignal = pyqtSignal(dict)

    def __init__(self, parent=None, prefix='', ramp_config=None,
                 undo_stack=None):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self.ramp_config = ramp_config
        self._undo_stack = undo_stack
        self._getNormalizedConfigs()
        self._magnets_to_plot = []
        self._setupUi()

    def _setupUi(self):
        glay = QGridLayout(self)
        self.graphview = QWidget()
        self.table = QTableWidget(self)
        self.bt_insert = QPushButton('Insert Normalized Configuration', self)
        self.bt_delete = QPushButton('Delete Normalized Configuration', self)

        self._setupGraph()
        self._setupTable()
        self.bt_insert.clicked.connect(self._showInsertNormConfigPopup)
        self.bt_delete.clicked.connect(self._showDeleteNormConfigPopup)

        label = QLabel('<h4>Multipoles Ramp</h4>', self)
        label.setAlignment(Qt.AlignCenter)
        label.setFixedHeight(48)
        glay.addWidget(label, 0, 0, 1, 2)
        glay.addWidget(self.graphview, 1, 0, 1, 2)
        glay.addWidget(self.table, 2, 0, 1, 2)
        glay.addWidget(self.bt_insert, 3, 0)
        glay.addWidget(self.bt_delete, 3, 1)

    def _setupGraph(self):
        self.graph = FigureCanvas(Figure())
        self.graph.setFixedHeight(500)
        self.ax = self.graph.figure.subplots()
        self.ax.grid()
        self.ax.set_xlabel('t [ms]')
        self.lines = dict()
        for maname in ramp.BoosterNormalized().get_config_type_template():
            if maname != 'BO-Fam:MA-B':
                self.lines[maname], = self.ax.plot([0], [0], '-b')
        self.markers, = self.ax.plot([0], [0], '+r')
        self.m_inj, = self.ax.plot([0], [0], 'or')
        self.m_ej, = self.ax.plot([0], [0], 'or')

        self.toolbar = NavigationToolbar(self.graph, self)

        hlay_pb = QHBoxLayout()
        self.pb_maname = QPushButton('Choose magnets to plot... ', self)
        self.pb_maname.clicked.connect(self._showChooseMagnetToPlot)
        hlay_pb.addItem(QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Fixed))
        hlay_pb.addWidget(self.pb_maname)
        hlay_pb.addItem(QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Fixed))

        lay = QGridLayout()
        lay.addWidget(self.graph, 0, 0, 1, 2)
        lay.addWidget(self.toolbar, 1, 0)
        lay.addLayout(hlay_pb, 2, 0, 1, 2)
        self.graphview.setLayout(lay)

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
            1064, min((self.normalized_configs_count+1)*48+37, 426))
        self.table.verticalHeader().setFixedWidth(48)
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
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.table.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)
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
        self.configsIndexChangedSignal.emit(self.table_map)

    def _handleCellChanged(self, row, column):
        try:
            config_changed_name = self.table.item(row, 0).data(
                Qt.DisplayRole)
            for t, n in self.ramp_config.normalized_configs:
                if n == config_changed_name:
                    old_value = t
                    break
            new_value = float(self.table.item(row, column).data(
                Qt.DisplayRole))
            self.ramp_config.normalized_configs_change_time(
                config_changed_name, new_value)
        except exceptions.RampInvalidNormConfig as e:
            err_msg = _MessageBox(self, 'Error', str(e), 'Ok')
            err_msg.open()
        else:
            self.updateGraph()
            self.updateMultipoleRampSignal.emit()

            global _flag_stack_next_command, _flag_stacking
            if _flag_stack_next_command:
                _flag_stacking = True
                command = _CommandChangeTableCell(
                    self.table, row, column, old_value, new_value,
                    'set multipole table item at row {0}, column {1}'.format(
                        row, column))
                self._undo_stack.push(command)
            else:
                _flag_stack_next_command = True
        finally:
            self.updateTable()

    def _showInsertNormConfigPopup(self):
        if self.ramp_config is not None:
            self._insertConfigPopup = _InsertNormalizedConfig(self)
            self._insertConfigPopup.insertConfig.connect(
                self._handleInsertNormConfig)
            self._insertConfigPopup.open()

    @pyqtSlot(list)
    def _handleInsertNormConfig(self, config):
        try:
            self.ramp_config.normalized_configs_insert(time=config[0],
                                                       name=config[1],
                                                       nconfig=config[2])
        except exceptions.RampInvalidNormConfig as e:
            err_msg = _MessageBox(self, 'Error', str(e), 'Ok')
            err_msg.open()
        else:
            self.handleLoadRampConfig(self.ramp_config)
            self.updateMultipoleRampSignal.emit()

    def _showDeleteNormConfigPopup(self):
        if self.ramp_config is not None:
            self._deleteConfigPopup = _DeleteNormalizedConfig(self,
                                                              self.table_map)
            self._deleteConfigPopup.deleteConfig.connect(
                self._handleDeleteNormConfig)
            self._deleteConfigPopup.open()

    @pyqtSlot(str)
    def _handleDeleteNormConfig(self, config):
        self.ramp_config.normalized_configs_delete(config)
        self.handleLoadRampConfig(self.ramp_config)
        self.updateMultipoleRampSignal.emit()

    def _showChooseMagnetToPlot(self):
        manames = list(
            ramp.BoosterNormalized().get_config_type_template().keys())
        idx = manames.index('BO-Fam:MA-B')
        del manames[idx]
        self._chooseMagnetsPopup = _ChooseMagnetsToPlot(
            self, manames, self._magnets_to_plot)
        self._chooseMagnetsPopup.choosePlotSignal.connect(
            self._handleChooseMagnetToPlot)
        self._chooseMagnetsPopup.open()

    @pyqtSlot(list)
    def _handleChooseMagnetToPlot(self, maname_list):
        self._magnets_to_plot = maname_list
        self.updateGraph()

    def updateGraph(self):
        """Update and redraw graph."""
        if self.ramp_config is not None:
            xdata = self.ramp_config.waveform_get_times()
            for maname in self._magnets_to_plot:
                ydata = self.ramp_config.waveform_get_strengths(maname)
                self.lines[maname].set_xdata(xdata)
                self.lines[maname].set_ydata(ydata)

            ydata = list()
            template = ramp.BoosterNormalized().get_config_type_template()
            for maname in template:
                if maname in self._magnets_to_plot:
                    self.lines[maname].set_linewidth(1.5)
                    ydata.append(self.lines[maname].get_ydata())
                elif maname != 'BO-Fam:MA-B':
                    self.lines[maname].set_linewidth(0)

            self.ax.set_xlim(min(xdata)-0.2, max(xdata)+0.2)
            ydata = np.array(ydata)
            if len(ydata) > 0:
                self.ax.set_ylim(ydata.min()-0.2, ydata.max()+0.2)

            ylabel = None
            for maname in self._magnets_to_plot:
                if 'MA-Q' not in maname:
                    break
            else:
                ylabel = 'KL [1/m]'
            for maname in self._magnets_to_plot:
                if 'MA-S' not in maname:
                    break
            else:
                ylabel = 'SL [1/m$^2$]'
            for maname in self._magnets_to_plot:
                if 'MA-C' not in maname:
                    break
            else:
                ylabel = 'Kick [rad]'

            if ylabel:
                self.ax.set_ylabel(ylabel)
            else:
                self.ax.set_ylabel('Int. Strengths')

            inj_marker_time = self.ramp_config.injection_time
            self.m_inj.set_xdata(inj_marker_time)
            ej_marker_time = self.ramp_config.ejection_time
            self.m_ej.set_xdata(ej_marker_time)

            markers_base_time = self.ramp_config.ramp_dipole_times
            markers_time = list()
            markers_value = list()
            inj_marker_value = list()
            ej_marker_value = list()
            for maname in self._magnets_to_plot:
                markers_time.append(markers_base_time)
                markers_value.append(
                    self.ramp_config.waveform_interp_strengths(
                        maname, markers_base_time))
                inj_marker_value.append(
                    self.ramp_config.waveform_interp_strengths(
                        maname, inj_marker_time))
                ej_marker_value.append(
                    self.ramp_config.waveform_interp_strengths(
                        maname, ej_marker_time))
            self.markers.set_xdata(markers_time)
            self.markers.set_ydata(markers_value)
            self.m_inj.set_ydata(inj_marker_value)
            self.m_ej.set_ydata(ej_marker_value)

            self.graph.figure.canvas.draw()
            self.graph.figure.canvas.flush_events()

    def updateTable(self):
        """Update and rebuild table."""
        if self.ramp_config is None:
            return
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
            D = self.ramp_config.ramp_dipole_duration
            N = self.ramp_config.ramp_dipole_wfm_nrpoints
            T = float(self.table.item(
                row, self.table_map['columns']['T [ms]']).data(
                Qt.DisplayRole))
            value = round(T*N/D)
            item = self.table.item(row, self.table_map['columns']['Index'])
            item.setData(Qt.DisplayRole, str(value))
        self._sortTable()
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
        for row in self.table_map['rows'].values():
            if row == 0:
                value = '-'
            else:
                dIdx = float(self.table.item(
                    row, self.table_map['columns']['ΔIndex']).data(
                    Qt.DisplayRole))
                E1 = float(self.table.item(
                    row, self.table_map['columns']['E [GeV]']).data(
                    Qt.DisplayRole))
                E2 = float(self.table.item(
                    row-1, self.table_map['columns']['E [GeV]']).data(
                    Qt.DisplayRole))
                dE = E1 - E2
                if dIdx != 0:
                    value = dE*1000/dIdx
                else:
                    '-'
            item = self.table.item(row,
                                   self.table_map['columns']['v [MeV/pt]'])
            item.setData(Qt.DisplayRole, str(value))
        self.table.cellChanged.connect(self._handleCellChanged)

    @pyqtSlot(ramp.BoosterRamp)
    def handleLoadRampConfig(self, ramp_config):
        """Update all widgets in loading BoosterRamp config."""
        self.ramp_config = ramp_config
        self._getNormalizedConfigs()
        self.table.cellChanged.disconnect(self._handleCellChanged)
        self._setupTable()
        self.updateTable()
        self.updateGraph()

    @pyqtSlot(ramp.BoosterNormalized)
    def handleNormConfigsChanges(self, norm_config):
        """Reload normalized configs on change and update graph."""
        self.ramp_config[norm_config.name] = norm_config
        self.updateGraph()


class RFRamp(QWidget):
    """Widget to set and monitor RF ramp."""

    updateRFRampSignal = pyqtSignal()

    def __init__(self, parent=None, prefix='', ramp_config=None,
                 undo_stack=None):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = _PVName(prefix)
        self.ramp_config = ramp_config
        self._undo_stack = undo_stack
        self._setupUi()

    def _setupUi(self):
        vlay = QVBoxLayout(self)
        self.graphview = QWidget()
        self.set_nrpoints = QHBoxLayout()
        self.table = QTableWidget(self)

        self._setupGraph()
        self._setupWfmNrPoints()
        self._setupTable()

        label = QLabel('<h4>RF Ramp</h4>', self)
        label.setFixedHeight(48)
        label.setAlignment(Qt.AlignCenter)
        vlay.addWidget(label)
        vlay.addWidget(self.graphview)
        vlay.addLayout(self.set_nrpoints)
        vlay.addWidget(self.table)
        vlay.addSpacerItem(
            QSpacerItem(40, 20, QSzPlcy.Minimum, QSzPlcy.Expanding))

    def _setupGraph(self):
        self.graph = FigureCanvas(Figure())
        self.graph.setFixedHeight(500)
        self.ax = self.graph.figure.subplots()
        self.ax.grid()
        self.ax.set_xlabel('t [ms]')
        self.line1, = self.ax.plot([0], [0], '-b')
        self.markers, = self.ax.plot([0], [0], '+r')

        self.toolbar = NavigationToolbar(self.graph, self)

        lay = QVBoxLayout()
        lay.addWidget(self.graph)
        lay.addWidget(self.toolbar)
        self.graphview.setLayout(lay)

    def _setupWfmNrPoints(self):
        label_nrpoints = QLabel('# of points', self)
        label_nrpoints.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.sb_nrpoints = QSpinBox(self)
        self.set_nrpoints.addSpacerItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))
        self.set_nrpoints.addWidget(label_nrpoints)
        self.set_nrpoints.addWidget(self.sb_nrpoints)
        self.set_nrpoints.addSpacerItem(
            QSpacerItem(40, 20, QSzPlcy.Expanding, QSzPlcy.Minimum))

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
        try:
            # TODO
            old_value = 0
            new_value = float(self.table.item(row, column).data(
                Qt.DisplayRole))
        except exceptions.RampInvalidNormConfig as e:  # TODO
            err_msg = _MessageBox(self, 'Error', str(e), 'Ok')
            err_msg.open()
        else:
            self.updateGraph()
            self.updateRFRampSignal.emit()

            global _flag_stack_next_command, _flag_stacking
            if _flag_stack_next_command:
                _flag_stacking = True
                command = _CommandChangeTableCell(
                    self.table, row, column, old_value, new_value,
                    'set RF table item at row {0}, column {1}'.format(
                        row, column))
                self._undo_stack.push(command)
            else:
                _flag_stack_next_command = True
        finally:
            self.updateTable()

    @pyqtSlot()
    def _handleChangeNrPoints(self):
        """Handle change waveform number of points."""
        old_value = 0
        new_value = self.sb_nrpoints.value()

        try:
            # TODO: set new_value on ramp_config
            pass
        except exceptions.RampInvalidDipoleWfmParms as e:
            err_msg = _MessageBox(self, 'Error', str(e), 'Ok')
            err_msg.open()
        else:
            self.updateGraph()
            self.updateRFRampSignal.emit()
            global _flag_stack_next_command, _flag_stacking
            if _flag_stack_next_command:
                _flag_stacking = True
                command = _CommandChangeSpinbox(
                    self.sb_nrpoints, old_value, new_value,
                    'set number of RF ramp points to {0}'.format(new_value))
                self._undo_stack.push(command)
            else:
                _flag_stack_next_command = True
        finally:
            self.updateTable()

    def updateGraph(self):
        """Update and redraw graph."""
        pass

    def updateWfmNrPoints(self):
        """Update waveform number of points when ramp_config is loaded."""
        pass

    def updateTable(self):
        """Update and rebuild table."""
        if self.ramp_config is None:
            return
        self.table.cellChanged.disconnect(self._handleCellChanged)
        # TODO
        self.table.cellChanged.connect(self._handleCellChanged)

    @pyqtSlot(ramp.BoosterRamp)
    def handleLoadRampConfig(self, ramp_config):
        """Update all widgets in loading BoosterRamp config."""
        self.ramp_config = ramp_config
        self.updateTable()
        self.updateWfmNrPoints()
        self.updateGraph()


class _CommandChangeTableCell(QUndoCommand):
    """Class to define command change table cell."""

    def __init__(self, table, row, column, old_data, new_data, description):
        super().__init__(description)
        self.table = table
        self.row = row
        self.column = column
        self.old_data = old_data
        self.new_data = new_data

    def undo(self):
        global _flag_stack_next_command
        _flag_stack_next_command = False
        self.table.item(self.row, self.column).setData(
            Qt.DisplayRole, str(self.old_data))

    def redo(self):
        global _flag_stack_next_command, _flag_stacking
        if not _flag_stacking:
            _flag_stack_next_command = False
            self.table.item(self.row, self.column).setData(
                Qt.DisplayRole, str(self.new_data))
        else:
            _flag_stacking = False


class _CommandChangeSpinbox(QUndoCommand):
    """Class to define command change ramp number of points or duration."""

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
