"""Booster Ramp Control HLA: Ramp Parameters Module."""

from qtpy.QtCore import Qt, Signal, Slot
from qtpy.QtGui import QBrush, QColor
from qtpy.QtWidgets import QGroupBox, QLabel, QWidget, QSpacerItem, \
                           QVBoxLayout, QHBoxLayout, QGridLayout, \
                           QPushButton, QTableWidget, QTableWidgetItem, \
                           QSpinBox, QSizePolicy as QSzPlcy, \
                           QAbstractItemView, QUndoCommand, QFormLayout
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import numpy as np
from siriuspy.ramp import ramp, exceptions
from siriuspy.csdevice.pwrsupply import MAX_WFMSIZE
from siriushla.bo_ap_ramp.auxiliar_classes import MessageBox as _MessageBox, \
    InsertNormalizedConfig as _InsertNormalizedConfig, \
    DeleteNormalizedConfig as _DeleteNormalizedConfig, \
    SpinBoxDelegate as _SpinBoxDelegate, \
    CustomTableWidgetItem as _CustomTableWidgetItem, \
    ChooseMagnetsToPlot as _ChooseMagnetsToPlot, \
    MyDoubleSpinBox as _MyDoubleSpinBox


_flag_stack_next_command = True
_flag_stacking = False


class ConfigParameters(QGroupBox):
    """Widget to set and monitor ramp parametes."""

    def __init__(self, parent=None, prefix='', ramp_config=None,
                 undo_stack=None):
        """Initialize object."""
        super().__init__('Ramping Parameters: ', parent)
        self.prefix = prefix
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

    @Slot(ramp.BoosterRamp)
    def handleLoadRampConfig(self, ramp_config):
        """Update all widgets when ramp_config is loaded."""
        self.ramp_config = ramp_config
        self.setTitle('Ramping Parameters: ' + self.ramp_config.name)


class DipoleRamp(QWidget):
    """Widget to set and monitor dipole ramp."""

    updateDipoleRampSignal = Signal()

    def __init__(self, parent=None, prefix='', ramp_config=None,
                 undo_stack=None):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = prefix
        self.ramp_config = ramp_config
        self._undo_stack = undo_stack
        self._setupUi()

    def _setupUi(self):
        glay = QGridLayout(self)
        self.graphview = QWidget()
        self.set_psdelay_and_nrpoints = QFormLayout()
        self.table = QTableWidget(self)

        self._setupGraph()
        self._setupPSDelayAndWfmNrPoints()
        self._setupTable()

        vlay_v = QVBoxLayout()
        self.l_rampupv = QLabel('RmpU 0 [GeV/s]', self,
                                alignment=Qt.AlignRight)
        self.l_rampupv.setFixedWidth(320)
        self.l_rampdownv = QLabel('RmpD 0 [GeV/s]', self,
                                  alignment=Qt.AlignRight)
        self.l_rampdownv.setFixedWidth(320)
        vlay_v.addWidget(self.l_rampupv)
        vlay_v.addWidget(self.l_rampdownv)

        hlay_caution = QHBoxLayout()
        self.label_caution = QLabel('', self)
        self.label_caution.setFixedSize(644, 40)
        self.pb_caution = QPushButton('?', self)
        self.pb_caution.setFixedWidth(48)
        self.pb_caution.setVisible(False)
        self.pb_caution.setStyleSheet('background-color: red;')
        self.pb_caution.clicked.connect(self._showAnomaliesPopup)
        hlay_caution.addWidget(self.label_caution)
        hlay_caution.addWidget(self.pb_caution)

        label = QLabel('<h4>Dipole Ramp</h4>', self, alignment=Qt.AlignCenter)
        label.setFixedHeight(48)
        glay.addWidget(label, 0, 0, 1, 2)
        glay.addWidget(self.graphview, 1, 0, 1, 2, alignment=Qt.AlignCenter)
        glay.addLayout(self.set_psdelay_and_nrpoints, 2, 0,
                       alignment=Qt.AlignLeft)
        glay.addLayout(vlay_v, 2, 1, alignment=Qt.AlignRight)
        glay.addWidget(self.table, 3, 0, 1, 2, alignment=Qt.AlignCenter)
        glay.addLayout(hlay_caution, 4, 0, 1, 2, alignment=Qt.AlignCenter)
        glay.addItem(
            QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding), 5, 1)

    def _setupGraph(self):
        self.graph = FigureCanvas(Figure())
        self.graph.setFixedSize(779, 500)
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

    def _setupPSDelayAndWfmNrPoints(self):
        label_psdelay = QLabel('PS Delay [ms]:', self,
                               alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.sb_psdelay = _MyDoubleSpinBox(self)
        self.sb_psdelay.setMinimum(0)
        self.sb_psdelay.setMaximum(490)
        self.sb_psdelay.setDecimals(6)
        self.sb_psdelay.setSingleStep(0.000008)
        self.sb_psdelay.setMaximumWidth(200)
        self.sb_psdelay.editingFinished.connect(self._handleChangePSDelay)

        label_nrpoints = QLabel('# of points:', self,
                                alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.sb_nrpoints = QSpinBox(self)
        self.sb_nrpoints.setMinimum(1)
        self.sb_nrpoints.setMaximum(MAX_WFMSIZE)
        self.sb_nrpoints.setMaximumWidth(200)
        self.sb_nrpoints.editingFinished.connect(self._handleChangeNrPoints)

        self.set_psdelay_and_nrpoints.addRow(label_psdelay, self.sb_psdelay)
        self.set_psdelay_and_nrpoints.addRow(label_nrpoints, self.sb_nrpoints)

    def _setupTable(self):
        self.table_map = {
            'rows': {0: 'Start',
                     1: 'RampUp-Start',
                     2: 'Injection',
                     3: 'Ejection',
                     4: 'RampUp-Stop',
                     5: 'Plateau-Start',
                     6: 'RampDown-Start',
                     7: 'RampDown-Stop',
                     8: 'Stop'},
            'columns': {0: '',
                        1: 'T [ms]',
                        2: 'Index',
                        3: 'E [GeV]'}}
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
        self.table.setFixedSize(
            717, (max(self.table_map['rows'].keys())+2)*48+2)
        self.table.setRowCount(9)
        self.table.setColumnCount(4)
        self.table.setColumnWidth(0, 250)
        for i in range(1, len(self.table_map['columns'].keys())):
            self.table.setColumnWidth(i, 155)
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().setFixedHeight(48)
        self.table.setHorizontalHeaderLabels(
            self.table_map['columns'].values())

        for row, vlabel in self.table_map['rows'].items():
            label_item = QTableWidgetItem(vlabel)
            t_item = QTableWidgetItem('0')
            np_item = QTableWidgetItem('0')
            e_item = QTableWidgetItem('0')

            label_item.setFlags(Qt.ItemIsEnabled)
            np_item.setFlags(Qt.ItemIsEnabled)
            if vlabel in ['Start', 'Plateau-Start']:
                t_item.setFlags(Qt.ItemIsEnabled)
                e_item.setBackground(QBrush(QColor("white")))
            elif vlabel in ['Injection', 'Ejection', 'Stop']:
                t_item.setBackground(QBrush(QColor("white")))
                e_item.setFlags(Qt.ItemIsEnabled)
            else:
                t_item.setBackground(QBrush(QColor("white")))
                e_item.setBackground(QBrush(QColor("white")))

            self.table.setItem(row, 0, label_item)
            self.table.setItem(row, 1, t_item)
            self.table.setItem(row, 2, np_item)
            self.table.setItem(row, 3, e_item)

            self.table.setRowHeight(row, 48)

        self.table.setItemDelegate(_SpinBoxDelegate())
        self.table.cellChanged.connect(self._handleCellChanged)

    @Slot(int, int)
    def _handleCellChanged(self, row, column):
        if self.ramp_config is None:
            return

        try:
            new_value = float(self.table.item(row, column).data(
                Qt.DisplayRole))
            if self.table_map['rows'][row] == 'Start':
                old_value = self.ramp_config.ps_ramp_start_energy
                self.ramp_config.ps_ramp_start_energy = new_value

            elif self.table_map['rows'][row] == 'RampUp-Start':
                if self.table_map['columns'][column] == 'T [ms]':
                    old_value = self.ramp_config.ps_ramp_rampup_start_time
                    self.ramp_config.ps_ramp_rampup_start_time = new_value
                elif self.table_map['columns'][column] == 'E [GeV]':
                    old_value = self.ramp_config.ps_ramp_rampup_start_energy
                    self.ramp_config.ps_ramp_rampup_start_energy = new_value

            elif self.table_map['rows'][row] == 'Injection':
                old_value = self.ramp_config.ti_params_injection_time
                self.ramp_config.ti_params_injection_time = new_value

            elif self.table_map['rows'][row] == 'Ejection':
                old_value = self.ramp_config.ti_params_ejection_time
                self.ramp_config.ti_params_ejection_time = new_value

            elif self.table_map['rows'][row] == 'RampUp-Stop':
                if self.table_map['columns'][column] == 'T [ms]':
                    old_value = self.ramp_config.ps_ramp_rampup_stop_time
                    self.ramp_config.ps_ramp_rampup_stop_time = new_value
                elif self.table_map['columns'][column] == 'E [GeV]':
                    old_value = self.ramp_config.ps_ramp_rampup_stop_energy
                    self.ramp_config.ps_ramp_rampup_stop_energy = new_value

            elif self.table_map['rows'][row] == 'Plateau-Start':
                old_value = self.ramp_config.ps_ramp_plateau_energy
                self.ramp_config.ps_ramp_plateau_energy = new_value

            elif self.table_map['rows'][row] == 'RampDown-Start':
                if self.table_map['columns'][column] == 'T [ms]':
                    old_value = self.ramp_config.ps_ramp_rampdown_start_time
                    self.ramp_config.ps_ramp_rampdown_start_time = new_value
                elif self.table_map['columns'][column] == 'E [GeV]':
                    old_value = self.ramp_config.ps_ramp_rampdown_start_energy
                    self.ramp_config.ps_ramp_rampdown_start_energy = new_value

            elif self.table_map['rows'][row] == 'RampDown-Stop':
                if self.table_map['columns'][column] == 'T [ms]':
                    old_value = self.ramp_config.ps_ramp_rampdown_stop_time
                    self.ramp_config.ps_ramp_rampdown_stop_time = new_value
                elif self.table_map['columns'][column] == 'E [GeV]':
                    old_value = self.ramp_config.ps_ramp_rampdown_stop_energy
                    self.ramp_config.ps_ramp_rampdown_stop_energy = new_value

            elif self.table_map['rows'][row] == 'Stop':
                old_value = self.ramp_config.ps_ramp_duration
                self.ramp_config.ps_ramp_duration = new_value

        except exceptions.RampInvalidDipoleWfmParms as e:
            err_msg = _MessageBox(self, 'Error', str(e), 'Ok')
            err_msg.open()
        else:
            self.updateGraph()
            self.updateDipoleRampSignal.emit()
            if len(self.ramp_config.ps_waveform_anomalies) > 0:
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

    @Slot()
    def _handleChangePSDelay(self):
        """Handle change ps delay."""
        if self.ramp_config is None:
            return

        old_value = self.ramp_config.ti_params_ps_ramp_delay
        new_value = self.sb_psdelay.value()
        try:
            self.ramp_config.ti_params_ps_ramp_delay = new_value
        except exceptions.RampInvalidDipoleWfmParms as e:
            self.updatePSDelay()
            err_msg = _MessageBox(self, 'Error', str(e), 'Ok')
            err_msg.open()
        else:
            self.updateGraph()
            self.updateDipoleRampSignal.emit()
            global _flag_stack_next_command, _flag_stacking
            if _flag_stack_next_command and (old_value != new_value):
                _flag_stacking = True
                command = _CommandChangeSpinbox(
                    self.sb_psdelay, old_value, new_value,
                    'set PS ramp delay to {}'.format(new_value))
                self._undo_stack.push(command)
            else:
                _flag_stack_next_command = True
        finally:
            self.updateTable()

    @Slot()
    def _handleChangeNrPoints(self):
        """Handle change waveform number of points."""
        if self.ramp_config is None:
            return

        old_value = self.ramp_config.ps_ramp_wfm_nrpoints
        new_value = self.sb_nrpoints.value()
        try:
            self.ramp_config.ps_ramp_wfm_nrpoints = new_value
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

    def _showAnomaliesPopup(self):
        text = 'Caution to the following anomalies: \n'
        for anom in self.ramp_config.ps_waveform_anomalies:
            text += anom + '\n'
        anomaliesPopup = _MessageBox(self, 'Caution', text, 'Ok')
        anomaliesPopup.open()

    def updateGraph(self):
        """Update and redraw graph when ramp_config is loaded."""
        if self.ramp_config is None:
            return

        xdata = self.ramp_config.ps_waveform_get_times()
        ydata = self.ramp_config.ps_waveform_get_strengths('BO-Fam:MA-B')
        self.line.set_xdata(xdata)
        self.line.set_ydata(ydata)
        self.ax.set_xlim(min(xdata)-0.2, max(xdata)+0.2)
        self.ax.set_ylim(min(ydata)-0.2, max(ydata)+0.2)

        self.markers.set_xdata(self.ramp_config.ps_ramp_times)
        self.markers.set_ydata(self.ramp_config.ps_ramp_energies)

        inj_marker_time = self.ramp_config.ti_params_injection_time
        self.m_inj.set_xdata(inj_marker_time)
        self.m_inj.set_ydata(self.ramp_config.ps_waveform_interp_energy(
            inj_marker_time))

        ej_marker_time = self.ramp_config.ti_params_ejection_time
        self.m_ej.set_xdata(ej_marker_time)
        self.m_ej.set_ydata(self.ramp_config.ps_waveform_interp_energy(
            ej_marker_time))

        self.graph.figure.canvas.draw()
        self.graph.figure.canvas.flush_events()

    def updatePSDelay(self):
        """Update PS delay when ramp_config is loaded."""
        self.sb_nrpoints.setValue(self.ramp_config.ti_params_ps_ramp_delay)

    def updateWfmNrPoints(self):
        """Update waveform number of points when ramp_config is loaded."""
        self.sb_nrpoints.setValue(self.ramp_config.ps_ramp_wfm_nrpoints)

    def updateTable(self):
        """Update and rebuild table when ramp_config is loaded."""
        self.table.cellChanged.disconnect(self._handleCellChanged)
        for row, label in self.table_map['rows'].items():
            t_item = self.table.item(row, 1)  # time column
            e_item = self.table.item(row, 3)  # energy column
            if label == 'Start':
                time = 0.0
                energy = self.ramp_config.ps_ramp_start_energy
            elif label == 'RampUp-Start':
                time = self.ramp_config.ps_ramp_rampup_start_time
                energy = self.ramp_config.ps_ramp_rampup_start_energy
            elif label == 'Injection':
                time = self.ramp_config.ti_params_injection_time
                energy = self.ramp_config.ps_waveform_interp_energy(time)
            elif label == 'Ejection':
                time = self.ramp_config.ti_params_ejection_time
                energy = self.ramp_config.ps_waveform_interp_energy(time)
            elif label == 'RampUp-Stop':
                time = self.ramp_config.ps_ramp_rampup_stop_time
                energy = self.ramp_config.ps_ramp_rampup_stop_energy
            elif label == 'Plateau-Start':
                time = self.ramp_config.ps_ramp_plateau_start_time
                energy = self.ramp_config.ps_ramp_plateau_energy
            elif label == 'RampDown-Start':
                time = self.ramp_config.ps_ramp_rampdown_start_time
                energy = self.ramp_config.ps_ramp_rampdown_start_energy
            elif label == 'RampDown-Stop':
                time = self.ramp_config.ps_ramp_rampdown_stop_time
                energy = self.ramp_config.ps_ramp_rampdown_stop_energy
            elif label == 'Stop':
                time = self.ramp_config.ps_ramp_duration
                energy = self.ramp_config.ps_ramp_start_energy
            t_item.setData(Qt.DisplayRole, str(time))
            e_item.setData(Qt.DisplayRole, str(energy))

        for row in self.table_map['rows'].keys():
            D = self.ramp_config.ps_ramp_duration
            N = self.ramp_config.ps_ramp_wfm_nrpoints
            T = float(self.table.item(row, 1).data(Qt.DisplayRole))
            value = round(T*N/D)
            item = self.table.item(row, 2)  # index column
            item.setData(Qt.DisplayRole, str(value))

        rampupv = ((self.ramp_config.ps_ramp_rampup_stop_energy -
                   self.ramp_config.ps_ramp_rampup_start_energy) /
                   (self.ramp_config.ps_ramp_rampup_stop_time -
                   self.ramp_config.ps_ramp_rampup_start_time))
        self.l_rampupv.setText('RmpU {: .3f} [GeV/s]'.format(1000*rampupv))

        rampdownv = ((self.ramp_config.ps_ramp_rampdown_stop_energy -
                      self.ramp_config.ps_ramp_rampdown_start_energy) /
                     (self.ramp_config.ps_ramp_rampdown_stop_time -
                     self.ramp_config.ps_ramp_rampdown_start_time))
        self.l_rampdownv.setText('RmpD {: .3f} [GeV/s]'.format(1000*rampdownv))

        self.table.cellChanged.connect(self._handleCellChanged)

    @Slot(ramp.BoosterRamp)
    def handleLoadRampConfig(self, ramp_config):
        """Update all widgets when ramp_config is loaded."""
        self.ramp_config = ramp_config
        self.updateGraph()
        self.updatePSDelay()
        self.updateWfmNrPoints()
        self.updateTable()
        if len(self.ramp_config.ps_waveform_anomalies) > 0:
            self.label_caution.setText('<h6>Caution: there are anomalies '
                                       'in the waveforms.</h6>')
            self.pb_caution.setVisible(True)
        else:
            self.label_caution.setText('')
            self.pb_caution.setVisible(False)


class MultipolesRamp(QWidget):
    """Widget to set and monitor multipoles ramp."""

    updateMultipoleRampSignal = Signal()
    configsIndexChangedSignal = Signal(dict)

    def __init__(self, parent=None, prefix='', ramp_config=None,
                 undo_stack=None):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = prefix
        self.ramp_config = ramp_config
        self._undo_stack = undo_stack
        self._getNormalizedConfigs()
        self._magnets_to_plot = []
        self._setupUi()

    def _setupUi(self):
        glay = QGridLayout(self)
        glay.setAlignment(Qt.AlignCenter)
        self.graphview = QWidget()
        self.table = QTableWidget(self)
        self.bt_insert = QPushButton('Insert Normalized Config', self)
        self.bt_delete = QPushButton('Delete Normalized Config', self)

        self._setupGraph()
        self._setupTable()
        self.bt_insert.clicked.connect(self._showInsertNormConfigPopup)
        self.bt_delete.clicked.connect(self._showDeleteNormConfigPopup)

        hlay_table = QHBoxLayout()
        hlay_table.addItem(
            QSpacerItem(1, 20, QSzPlcy.Minimum, QSzPlcy.Expanding))
        hlay_table.addWidget(self.table)
        hlay_table.addItem(
            QSpacerItem(1, 20, QSzPlcy.Minimum, QSzPlcy.Expanding))

        label = QLabel('<h4>Multipoles Ramp</h4>', self)
        label.setAlignment(Qt.AlignCenter)
        label.setFixedHeight(48)
        glay.addWidget(label, 0, 0, 1, 2)
        glay.addWidget(self.graphview, 1, 0, 1, 2)
        glay.addLayout(hlay_table, 2, 0, 1, 2)
        glay.addWidget(self.bt_insert, 3, 0)
        glay.addWidget(self.bt_delete, 3, 1)

    def _setupGraph(self):
        self.graph = FigureCanvas(Figure())
        self.graph.setFixedSize(779, 500)
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
            'rows': {0: 'Injection',
                     self.normalized_configs_count+1: 'Ejection'},
            'columns': {0: '',
                        1: 'T [ms]',
                        2: 'Index',
                        3: 'E [GeV]'}}
        idx = 1
        normalized_config_rows = list()
        for config in self.normalized_configs:
            self.table_map['rows'][idx] = config[1]
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
        self.table.setFixedWidth(779)
        self.table.setMinimumHeight(
            min((self.normalized_configs_count+3)*48+2, 482))
        self.table.verticalHeader().setFixedWidth(48)
        self.table.horizontalHeader().setFixedHeight(48)
        self.table.setRowCount(2+self.normalized_configs_count)
        self.table.setColumnCount(4)
        self.table.setColumnWidth(0, 250)
        for i in range(1, len(self.table_map['columns'].values())):
            self.table.setColumnWidth(i, 155)
        self.table.setHorizontalHeaderLabels(
            self.table_map['columns'].values())

        for row, vlabel in self.table_map['rows'].items():
            label_item = QTableWidgetItem(vlabel)
            t_item = _CustomTableWidgetItem('0')
            np_item = QTableWidgetItem('0')
            e_item = QTableWidgetItem('0')

            label_item.setFlags(Qt.ItemIsEnabled)
            np_item.setFlags(Qt.ItemIsEnabled)
            e_item.setFlags(Qt.ItemIsEnabled)
            if row in normalized_config_rows:
                label_item.setBackground(QBrush(QColor("white")))
                t_item.setBackground(QBrush(QColor("white")))
            else:
                t_item.setFlags(Qt.ItemIsEnabled)

            self.table.setItem(row, 0, label_item)
            self.table.setItem(row, 1, t_item)
            self.table.setItem(row, 2, np_item)
            self.table.setItem(row, 3, e_item)

            self.table.setRowHeight(row, 48)

        self.table.setItemDelegate(_SpinBoxDelegate())
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.table.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)
        self.table.cellChanged.connect(self._handleCellChanged)

    def _getNormalizedConfigs(self):
        if self.ramp_config is not None:
            self.normalized_configs = self.ramp_config.ps_normalized_configs
            self.normalized_configs_count = len(self.normalized_configs)
        else:
            self.normalized_configs = list()
            self.normalized_configs_count = 0

    def _sortTable(self):
        self.table.sortByColumn(1, Qt.AscendingOrder)
        for row in range(self.table.rowCount()):
            self.table_map['rows'][row] = self.table.item(row, 0).text()
        self.configsIndexChangedSignal.emit(self.table_map)

    def _handleCellChanged(self, row, column):
        try:
            config_changed_name = self.table.item(row, 0).data(
                Qt.DisplayRole)
            old_value = [t for t, n in self.normalized_configs
                         if n == config_changed_name]
            new_value = float(self.table.item(row, column).data(
                Qt.DisplayRole))
            self.ramp_config.ps_normalized_configs_change_time(
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
                    self.table, row, column, old_value[0], new_value,
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

    @Slot(list)
    def _handleInsertNormConfig(self, config):
        try:
            self.ramp_config.ps_normalized_configs_insert(time=config[0],
                                                          name=config[1],
                                                          nconfig=config[2])
        except exceptions.RampInvalidNormConfig as e:
            err_msg = _MessageBox(self, 'Error', str(e), 'Ok')
            err_msg.open()
        else:
            self.handleLoadRampConfig(self.ramp_config)
            self.updateMultipoleRampSignal.emit()

    def _showDeleteNormConfigPopup(self):
        if self.ramp_config is None:
            return
        selected_item = self.table.selectedItems()
        self._deleteConfigPopup = _DeleteNormalizedConfig(
            self, self.table_map, selected_item)
        self._deleteConfigPopup.deleteConfig.connect(
            self._handleDeleteNormConfig)
        self._deleteConfigPopup.open()

    @Slot(str)
    def _handleDeleteNormConfig(self, config):
        self.ramp_config.ps_normalized_configs_delete(config)
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

    @Slot(list)
    def _handleChooseMagnetToPlot(self, maname_list):
        self._magnets_to_plot = maname_list
        self.updateGraph()

    def updateGraph(self):
        """Update and redraw graph."""
        if self.ramp_config is not None:
            xdata = self.ramp_config.ps_waveform_get_times()
            for maname in self._magnets_to_plot:
                ydata = self.ramp_config.ps_waveform_get_strengths(maname)
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

            inj_marker_time = self.ramp_config.ti_params_injection_time
            self.m_inj.set_xdata(inj_marker_time)
            ej_marker_time = self.ramp_config.ti_params_ejection_time
            self.m_ej.set_xdata(ej_marker_time)

            markers_base_time = self.ramp_config.ps_ramp_times
            markers_time = list()
            markers_value = list()
            inj_marker_value = list()
            ej_marker_value = list()
            for maname in self._magnets_to_plot:
                markers_time.append(markers_base_time)
                markers_value.append(
                    self.ramp_config.ps_waveform_interp_strengths(
                        maname, markers_base_time))
                inj_marker_value.append(
                    self.ramp_config.ps_waveform_interp_strengths(
                        maname, inj_marker_time))
                ej_marker_value.append(
                    self.ramp_config.ps_waveform_interp_strengths(
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

        config_dict = dict()
        self._getNormalizedConfigs()
        for config in self.normalized_configs:
            config_dict[config[0]] = config[1]

        for row, label in self.table_map['rows'].items():
            label_item = self.table.item(row, 0)  # name column
            t_item = self.table.item(row, 1)  # time column
            e_item = self.table.item(row, 3)  # energy column

            if label == 'Injection':
                time = self.ramp_config.ti_params_injection_time
                energy = str(self.ramp_config.ps_waveform_interp_energy(time))
            elif label == 'Ejection':
                time = self.ramp_config.ti_params_ejection_time
                energy = str(self.ramp_config.ps_waveform_interp_energy(time))
            elif label in config_dict.values():
                label_item.setData(Qt.DisplayRole, str(label))
                time = [t for t, n in config_dict.items() if n == label]
                time = time[0]
                energy = self.ramp_config.ps_waveform_interp_energy(time)
                del config_dict[time]
            t_item.setData(Qt.DisplayRole, str(time))
            e_item.setData(Qt.DisplayRole, str(energy))

        for row in self.table_map['rows'].keys():
            D = self.ramp_config.ps_ramp_duration
            N = self.ramp_config.ps_ramp_wfm_nrpoints
            T = float(self.table.item(row, 1).data(Qt.DisplayRole))
            value = round(T*N/D)
            item = self.table.item(row, 2)  # index column
            item.setData(Qt.DisplayRole, str(value))
        self._sortTable()

        self.table.cellChanged.connect(self._handleCellChanged)

    @Slot(ramp.BoosterRamp)
    def handleLoadRampConfig(self, ramp_config):
        """Update all widgets in loading BoosterRamp config."""
        self.ramp_config = ramp_config
        self._getNormalizedConfigs()
        self.table.cellChanged.disconnect(self._handleCellChanged)
        self._setupTable()
        self.updateTable()
        self.updateGraph()

    @Slot(ramp.BoosterNormalized)
    def handleNormConfigsChanges(self, norm_config):
        """Reload normalized configs on change and update graph."""
        self.ramp_config[norm_config.name] = norm_config
        self.updateGraph()


class RFRamp(QWidget):
    """Widget to set and monitor RF ramp."""

    updateRFRampSignal = Signal()

    def __init__(self, parent=None, prefix='', ramp_config=None,
                 undo_stack=None):
        """Initialize object."""
        super().__init__(parent)
        self.prefix = prefix
        self.ramp_config = ramp_config
        self._undo_stack = undo_stack
        self._setupUi()

    def _setupUi(self):
        glay = QGridLayout(self)
        self.graphview = QWidget()
        self.set_rfdelay_and_rmpincintvl = QFormLayout()
        self.table = QTableWidget(self)

        self._setupGraph()
        self._setupRFDelayAndRmpIncIntvl()
        self._setupTable()

        vlay_v = QVBoxLayout()
        self.l_rampupv = QLabel('RmpU 0 [kV/s]', self,
                                alignment=Qt.AlignRight)
        self.l_rampupv.setFixedWidth(320)
        self.l_rampdownv = QLabel('RmpD 0 [kV/s]', self,
                                  alignment=Qt.AlignRight)
        self.l_rampdownv.setFixedWidth(320)
        vlay_v.addWidget(self.l_rampupv)
        vlay_v.addWidget(self.l_rampdownv)

        label = QLabel('<h4>RF Ramp</h4>', self)
        label.setFixedHeight(48)
        label.setAlignment(Qt.AlignCenter)
        glay.addWidget(label, 0, 0, 1, 2)
        glay.addWidget(self.graphview, 1, 0, 1, 2)
        glay.addLayout(self.set_rfdelay_and_rmpincintvl, 2, 0)
        glay.addLayout(vlay_v, 2, 1)
        glay.addWidget(self.table, 3, 0, 1, 2)
        glay.addItem(
            QSpacerItem(40, 20, QSzPlcy.Fixed, QSzPlcy.Expanding), 5, 1)

    def _setupGraph(self):
        self.graph = FigureCanvas(Figure())
        self.graph.setFixedHeight(500)
        self.ax = self.graph.figure.subplots()
        self.ax.grid()
        self.ax.set_xlabel('t [ms]')
        self.ax.set_ylabel('Vgap [kV]')
        self.line1, = self.ax.plot([0], [0], '-b')
        self.line2, = self.ax.plot([0], [0], '-g')
        self.markers, = self.ax.plot([0], [0], '+r')
        self.m_inj, = self.ax.plot([0], [0], 'or')
        self.m_ej, = self.ax.plot([0], [0], 'or')

        self.toolbar = NavigationToolbar(self.graph, self)

        lay = QVBoxLayout()
        lay.addWidget(self.graph)
        lay.addWidget(self.toolbar)
        self.graphview.setLayout(lay)

    def _setupRFDelayAndRmpIncIntvl(self):
        label_rfdelay = QLabel('RF delay [ms]:', self)
        label_rfdelay.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.sb_rfdelay = _MyDoubleSpinBox(self)
        self.sb_rfdelay.setMinimum(0)
        self.sb_rfdelay.setMaximum(410)
        self.sb_rfdelay.setDecimals(6)
        self.sb_rfdelay.setSingleStep(0.000008)
        self.sb_rfdelay.setMaximumWidth(200)
        self.sb_rfdelay.editingFinished.connect(
            self._handleChangeRFDelay)

        label_rmpincintvl = QLabel('Ramp Increase Duration [min]:', self)
        label_rmpincintvl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.sb_rmpincintvl = _MyDoubleSpinBox(self)
        self.sb_rmpincintvl.setMinimum(0)
        self.sb_rmpincintvl.setMaximum(28)
        self.sb_rmpincintvl.setDecimals(2)
        self.sb_rmpincintvl.setSingleStep(0.1)
        self.sb_rmpincintvl.setMaximumWidth(200)
        self.sb_rmpincintvl.editingFinished.connect(
            self._handleChangeRmpIncIntvl)

        self.set_rfdelay_and_rmpincintvl.addRow(label_rfdelay, self.sb_rfdelay)
        self.set_rfdelay_and_rmpincintvl.addRow(label_rmpincintvl,
                                                self.sb_rmpincintvl)

    def _setupTable(self):
        self.table_map = {
            'rows': {0: 'Start',
                     1: 'RampUp-Start',
                     2: 'RampUp-Stop',
                     3: 'RampDown-Start',
                     4: 'RampDown-Stop'},
            'columns': {0: '',
                        1: 'T [ms]',
                        2: '|Vgap| [kV]',
                        3: 'ㄥVgap [°]',
                        4: 'E [GeV]',
                        5: 'Φs [°]'}}
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
        self.table.setFixedSize(
            1027, (max(self.table_map['rows'].keys())+2)*48+2)
        self.table.setRowCount(5)
        self.table.setColumnCount(6)
        self.table.setColumnWidth(0, 250)
        for i in range(1, len(self.table_map['columns'].values())):
            self.table.setColumnWidth(i, 155)
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().setFixedHeight(48)
        self.table.setHorizontalHeaderLabels(
            self.table_map['columns'].values())

        for row, vlabel in self.table_map['rows'].items():
            label_item = QTableWidgetItem(vlabel)
            t_item = QTableWidgetItem('0')
            Ph_item = QTableWidgetItem('0')
            Vgap_item = QTableWidgetItem('0')
            e_item = QTableWidgetItem('0')
            phsinc_item = QTableWidgetItem('0')

            label_item.setFlags(Qt.ItemIsEnabled)
            e_item.setFlags(Qt.ItemIsEnabled)
            phsinc_item.setFlags(Qt.ItemIsEnabled)
            if vlabel == 'Start':
                t_item.setFlags(Qt.ItemIsEnabled)
                Ph_item.setBackground(QBrush(QColor("white")))
                Vgap_item.setBackground(QBrush(QColor("white")))
            elif vlabel == 'RampUp-Stop':
                t_item.setBackground(QBrush(QColor("white")))
                Ph_item.setBackground(QBrush(QColor("white")))
                Vgap_item.setBackground(QBrush(QColor("white")))
            else:
                t_item.setBackground(QBrush(QColor("white")))
                Vgap_item.setFlags(Qt.ItemIsEnabled)

            self.table.setItem(row, 0, label_item)
            self.table.setItem(row, 1, t_item)
            self.table.setItem(row, 2, Vgap_item)
            self.table.setItem(row, 3, Ph_item)
            self.table.setItem(row, 4, e_item)
            self.table.setItem(row, 5, phsinc_item)

            self.table.setRowHeight(row, 48)

        self.table.setItemDelegate(_SpinBoxDelegate())
        self.table.cellChanged.connect(self._handleCellChanged)

    @Slot(int, int)
    def _handleCellChanged(self, row, column):
        if self.ramp_config is None:
            return

        try:
            new_value = float(self.table.item(row, column).data(
                Qt.DisplayRole))
            if self.table_map['rows'][row] == 'Start':
                if self.table_map['columns'][column] == '|Vgap| [kV]':
                    old_value = self.ramp_config.rf_ramp_bottom_voltage
                    self.ramp_config.rf_ramp_bottom_voltage = new_value
                elif self.table_map['columns'][column] == 'ㄥVgap [°]':
                    old_value = self.ramp_config.rf_ramp_bottom_phase
                    self.ramp_config.rf_ramp_bottom_phase = new_value

            elif self.table_map['rows'][row] == 'RampUp-Start':
                old_value = self.ramp_config.rf_ramp_rampup_start_time
                self.ramp_config.rf_ramp_rampup_start_time = new_value

            elif self.table_map['rows'][row] == 'RampUp-Stop':
                if self.table_map['columns'][column] == 'T [ms]':
                    old_value = self.ramp_config.rf_ramp_rampup_stop_time
                    self.ramp_config.rf_ramp_rampup_stop_time = new_value
                elif self.table_map['columns'][column] == '|Vgap| [kV]':
                    old_value = self.ramp_config.rf_ramp_top_voltage
                    self.ramp_config.rf_ramp_top_voltage = new_value
                elif self.table_map['columns'][column] == 'ㄥVgap [°]':
                    old_value = self.ramp_config.rf_ramp_top_phase
                    self.ramp_config.rf_ramp_top_phase = new_value

            elif self.table_map['rows'][row] == 'RampDown-Start':
                old_value = self.ramp_config.rf_ramp_rampdown_start_time
                self.ramp_config.rf_ramp_rampdown_start_time = new_value

            elif self.table_map['rows'][row] == 'RampDown-Stop':
                old_value = self.ramp_config.rf_ramp_rampdown_stop_time
                self.ramp_config.rf_ramp_rampdown_stop_time = new_value

        except exceptions.RampInvalidRFParms as e:
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

    @Slot()
    def _handleChangeRFDelay(self):
        """Handle change rf delay."""
        if self.ramp_config is None:
            return

        old_value = self.ramp_config.ti_params_rf_ramp_delay
        new_value = self.sb_rfdelay.value()
        try:
            self.ramp_config.ti_params_ps_ramp_delay = new_value
        except exceptions.RampInvalidRFParms as e:
            self.updateRFDelay()
            err_msg = _MessageBox(self, 'Error', str(e), 'Ok')
            err_msg.open()
        else:
            self.updateGraph()
            self.updateRFRampSignal.emit()
            global _flag_stack_next_command, _flag_stacking
            if _flag_stack_next_command and (old_value != new_value):
                _flag_stacking = True
                command = _CommandChangeSpinbox(
                    self.sb_rfdelay, old_value, new_value,
                    'set RF ramp delay to {}'.format(new_value))
                self._undo_stack.push(command)
            else:
                _flag_stack_next_command = True
        finally:
            self.updateTable()

    @Slot()
    def _handleChangeRmpIncIntvl(self):
        """Handle change RF ramping increase duration."""
        if self.ramp_config is None:
            return

        old_value = self.ramp_config.rf_ramp_rampinc_duration
        new_value = self.sb_rmpincintvl.value()
        try:
            self.ramp_config.rf_ramp_rampinc_duration = new_value
        except exceptions.RampInvalidRFParms as e:
            err_msg = _MessageBox(self, 'Error', str(e), 'Ok')
            err_msg.open()
        else:
            self.updateGraph()
            self.updateRFRampSignal.emit()
            global _flag_stack_next_command, _flag_stacking
            if _flag_stack_next_command:
                _flag_stacking = True
                command = _CommandChangeSpinbox(
                    self.sb_rmpincintvl, old_value, new_value,
                    'set RF ramping increase duration to {0}'.format(
                     new_value))
                self._undo_stack.push(command)
            else:
                _flag_stack_next_command = True
        finally:
            self.updateTable()

    def updateGraph(self):
        """Update and redraw graph."""
        if self.ramp_config is None:
            return

        xdata = list()
        xdata.append(0)
        for i in self.ramp_config.rf_ramp_times:
            xdata.append(i)
        xdata.append(490)
        self.line1.set_xdata(xdata)
        self.ax.set_xlim(min(xdata)-0.2, max(xdata)+0.2)

        ydata = list()
        ydata.append(self.ramp_config.rf_ramp_voltages[0])
        for i in self.ramp_config.rf_ramp_voltages:
            ydata.append(i)
        ydata.append(self.ramp_config.rf_ramp_voltages[0])
        self.line1.set_ydata(ydata)
        self.ax.set_ylim(min(ydata)-10, max(ydata)+10)

        times = self.ramp_config.ps_ramp_times
        self.markers.set_xdata(times)
        self.markers.set_ydata(self.ramp_config.rf_ramp_interp_voltages(times))

        inj_marker_time = self.ramp_config.ti_params_injection_time
        self.m_inj.set_xdata(inj_marker_time)
        self.m_inj.set_ydata(self.ramp_config.rf_ramp_interp_voltages(
            inj_marker_time))

        ej_marker_time = self.ramp_config.ti_params_ejection_time
        self.m_ej.set_xdata(ej_marker_time)
        self.m_ej.set_ydata(self.ramp_config.rf_ramp_interp_voltages(
            ej_marker_time))

        self.graph.figure.canvas.draw()
        self.graph.figure.canvas.flush_events()

    def updateRFDelay(self):
        """Update rf delay when ramp_config is loaded."""
        self.sb_rfdelay.setValue(self.ramp_config.ti_params_rf_ramp_delay)

    def updateRmpIncIntvl(self):
        """Update RF ramping increase duration when ramp_config is loaded."""
        self.sb_rmpincintvl.setValue(self.ramp_config.rf_ramp_rampinc_duration)

    def updateTable(self):
        """Update and rebuild table."""
        self.table.cellChanged.disconnect(self._handleCellChanged)
        for row, label in self.table_map['rows'].items():
            t_item = self.table.item(row, 1)  # time column
            Vgap_item = self.table.item(row, 2)  # voltage amp column
            Ph_item = self.table.item(row, 3)  # voltage phase column
            if label == 'Start':
                time = self.ramp_config.ti_params_rf_ramp_delay
                vgap = self.ramp_config.rf_ramp_bottom_voltage
                ph = self.ramp_config.rf_ramp_bottom_phase
            elif label == 'RampUp-Start':
                time = self.ramp_config.rf_ramp_rampup_start_time
                vgap = self.ramp_config.rf_ramp_bottom_voltage
                ph = self.ramp_config.rf_ramp_bottom_phase
            elif label == 'RampUp-Stop':
                time = self.ramp_config.rf_ramp_rampup_stop_time
                vgap = self.ramp_config.rf_ramp_top_voltage
                ph = self.ramp_config.rf_ramp_top_phase
            elif label == 'RampDown-Start':
                time = self.ramp_config.rf_ramp_rampdown_start_time
                vgap = self.ramp_config.rf_ramp_top_voltage
                ph = self.ramp_config.rf_ramp_top_phase
            elif label == 'RampDown-Stop':
                time = self.ramp_config.rf_ramp_rampdown_stop_time
                vgap = self.ramp_config.rf_ramp_bottom_voltage
                ph = self.ramp_config.rf_ramp_bottom_phase
            t_item.setData(Qt.DisplayRole, str(time))
            Vgap_item.setData(Qt.DisplayRole, str(vgap))
            Ph_item.setData(Qt.DisplayRole, str(ph))

        for column, label in self.table_map['columns'].items():
            for row in self.table_map['rows'].keys():
                if label == 'E [GeV]':
                    t_item = self.table.item(row, 1)
                    time = float(t_item.data(Qt.DisplayRole))
                    energy = self.ramp_config.ps_waveform_interp_energy(time)
                    e_item = self.table.item(row, column)
                    e_item.setData(Qt.DisplayRole, str(energy))
                elif label == 'Φs [°]':
                    value = 0  # TODO
                    item = self.table.item(row, column)
                    item.setData(Qt.DisplayRole, str(value))

        rampupv = ((self.ramp_config.rf_ramp_top_voltage -
                   self.ramp_config.rf_ramp_bottom_voltage) /
                   self.ramp_config.rf_ramp_rampup_duration)
        self.l_rampupv.setText('RmpU {: .3f} [kV/s]'.format(1000*rampupv))

        rampdownv = ((self.ramp_config.rf_ramp_bottom_voltage -
                      self.ramp_config.rf_ramp_top_voltage) /
                     self.ramp_config.rf_ramp_rampdown_duration)
        self.l_rampdownv.setText('RmpD {: .3f} [kV/s]'.format(1000*rampdownv))

        self.table.cellChanged.connect(self._handleCellChanged)

    @Slot(ramp.BoosterRamp)
    def handleLoadRampConfig(self, ramp_config):
        """Update all widgets in loading BoosterRamp config."""
        self.ramp_config = ramp_config
        self.updateGraph()
        self.updateRFDelay()
        self.updateRmpIncIntvl()
        self.updateTable()


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
